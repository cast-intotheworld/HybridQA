"""Compare the first sample across all 5 serialization formats.

Reads ONLY the first line of each JSONL file to avoid excessive I/O and token cost.
Output is printed to the terminal AND saved as a .txt file in outputs/view/.

Usage:
    python serialization/scripts/compare_formats.py
    python serialization/scripts/compare_formats.py --formats json markdown
    python serialization/scripts/compare_formats.py --split dev
    python serialization/scripts/compare_formats.py --truncate 500
    python serialization/scripts/compare_formats.py --summary-only
"""

import argparse
import json
import sys
from datetime import datetime
from io import StringIO
from pathlib import Path

SERIALIZED_DIR = Path(__file__).resolve().parent.parent / "outputs" / "serialized"
VIEW_DIR = Path(__file__).resolve().parent.parent / "outputs" / "view"

ALL_FORMATS = [
    "json",
    "yaml",
    "xml",
    "markdown",
    "html",
    "latex",
    "csv",
]


class TeeWriter:
    """Write to both stdout and a StringIO buffer simultaneously."""

    def __init__(self) -> None:
        self._buffer = StringIO()
        self._stdout = sys.stdout

    def write(self, text: str) -> None:
        self._stdout.write(text)
        self._buffer.write(text)

    def flush(self) -> None:
        self._stdout.flush()

    def get_content(self) -> str:
        return self._buffer.getvalue()


def read_first_line(filepath: Path) -> dict | None:
    """Read only the first line of a JSONL file and parse it as JSON.

    :param filepath: Path to the JSONL file.
    :return: Parsed dict from the first line, or None if file not found.
    """
    if not filepath.exists():
        print(f"  [SKIP] File not found: {filepath}")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        line = f.readline()
    if not line.strip():
        print(f"  [SKIP] Empty file: {filepath}")
        return None
    return json.loads(line)


def print_sample(data: dict, fmt_name: str, truncate: int = 0) -> None:
    """Print a single sample with optional text truncation.

    :param data: Parsed JSON dict from one JSONL line.
    :param fmt_name: Format name for display.
    :param truncate: Max characters to show for serialized_text. 0 = no limit.
    """
    text = data.get("serialized_text", "")
    token_count = data.get("token_count", "N/A")

    if truncate > 0 and len(text) > truncate:
        display_text = text[:truncate] + f"\n... [truncated, {len(text)} chars total]"
    else:
        display_text = text

    print(f"{'=' * 80}")
    print(f"FORMAT: {fmt_name}")
    print(f"  question_id : {data.get('question_id', 'N/A')}")
    print(f"  format      : {data.get('format', 'N/A')}")
    print(f"  token_count : {token_count}")
    print(f"  text length : {len(text)} chars")
    print(f"{'-' * 80}")
    print(display_text)
    print()


def print_summary(results: dict[str, dict]) -> None:
    """Print a compact summary table comparing token counts and text lengths.

    :param results: Dict mapping format name to parsed first-line data.
    """
    print(f"\n{'=' * 80}")
    print("SUMMARY: First sample comparison across formats")
    print(f"{'=' * 80}")
    print(f"{'Format':<22} {'Token Count':>12} {'Char Length':>12} {'Question ID'}")
    print(f"{'-' * 22} {'-' * 12} {'-' * 12} {'-' * 30}")
    for fmt_name, data in results.items():
        qid = data.get("question_id", "N/A")
        tokens = data.get("token_count", "N/A")
        chars = len(data.get("serialized_text", ""))
        print(f"{fmt_name:<22} {str(tokens):>12} {chars:>12} {qid}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare the first sample across serialization formats."
    )
    parser.add_argument(
        "--formats",
        nargs="*",
        default=ALL_FORMATS,
        choices=ALL_FORMATS,
        help="Formats to compare (default: all).",
    )
    parser.add_argument(
        "--split",
        default="dev",
        help="Data split to use (default: dev).",
    )
    parser.add_argument(
        "--truncate",
        type=int,
        default=0,
        help="Max chars to display for serialized_text. 0 = full text (default: 0).",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Show only the summary table without full text.",
    )
    args = parser.parse_args()

    # Tee: print to terminal + capture for file
    tee = TeeWriter()
    sys.stdout = tee

    print(f"Compare Formats — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Split: {args.split} | Truncate: {args.truncate or 'off'} | Summary only: {args.summary_only}")

    results: dict[str, dict] = {}

    for fmt_name in args.formats:
        filepath = SERIALIZED_DIR / fmt_name / args.split / "data.jsonl"
        data = read_first_line(filepath)
        if data is None:
            continue
        results[fmt_name] = data
        if not args.summary_only:
            print_sample(data, fmt_name, truncate=args.truncate)

    if results:
        print_summary(results)
    else:
        print("No data found. Check that serialized outputs exist.")

    # Restore stdout and save to file
    sys.stdout = tee._stdout

    VIEW_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_filename = f"compare_{args.split}_{timestamp}.txt"
    out_path = VIEW_DIR / out_filename
    out_path.write_text(tee.get_content(), encoding="utf-8")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
