"""Serialization pipeline: convert evidence to all/specific formats."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import yaml
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from serialization.src.data_loader.hybridqa_loader import load_questions
from serialization.src.data_loader.schema import Evidence
from serialization.src.data_loader.wikitables_loader import WikiTablesLoader
from serialization.src.evaluation.token_counter import count_tokens
from serialization.src.serializers.registry import get_serializer, list_formats

# Import all serializer modules to trigger registration
import serialization.src.serializers.json_format  # noqa: F401
import serialization.src.serializers.row_wise  # noqa: F401
import serialization.src.serializers.col_wise  # noqa: F401
import serialization.src.serializers.markdown_html  # noqa: F401
import serialization.src.serializers.interleaved  # noqa: F401
import serialization.src.serializers.relation_explicit  # noqa: F401
import serialization.src.serializers.compressed  # noqa: F401

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serialize HybridQA evidence")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--format", default="all", help="Format name or 'all'")
    parser.add_argument("--split", default="dev", choices=["train", "dev", "test"])
    parser.add_argument("--sample", type=int, default=None, help="Number of samples")
    parser.add_argument("--dry-run", action="store_true", help="Print 1 sample, don't save")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / args.config
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    formats_path = base_dir / "configs" / "formats.yaml"
    with open(formats_path, "r") as f:
        formats_config = yaml.safe_load(f)

    data_path = (base_dir / config["paths"]["hybridqa_data"]).resolve()
    wikitables_path = (base_dir / config["paths"]["wikitables"]).resolve()
    output_dir = base_dir / config["paths"]["output_dir"] / "serialized"

    # Determine formats to run
    if args.format == "all":
        format_names = list_formats()
    else:
        format_names = [args.format]

    # Load data
    questions = load_questions(data_path, args.split)
    if args.sample:
        questions = questions[: args.sample]

    wt_loader = WikiTablesLoader(wikitables_path)

    for fmt_name in format_names:
        fmt_config = formats_config.get("formats", {}).get(fmt_name, {})
        params = fmt_config.get("params", {})
        serializer = get_serializer(fmt_name, params)

        logger.info("Serializing %d questions with format '%s'", len(questions), fmt_name)
        results: list[dict] = []
        token_counts: list[int] = []

        for q in tqdm(questions, desc=fmt_name):
            table, passages = wt_loader.load_table_and_passages(q.table_id)
            evidence = Evidence(table=table, passages=passages, question=q)
            serialized = serializer.serialize(evidence)
            tokens = count_tokens(serialized)
            token_counts.append(tokens)

            if args.dry_run:
                print(f"\n{'='*80}")
                print(f"Format: {fmt_name} | Question: {q.question_id}")
                print(f"Tokens: {tokens}")
                print(f"{'='*80}")
                print(serialized[:2000])
                break

            results.append(
                {
                    "question_id": q.question_id,
                    "format": fmt_name,
                    "serialized_text": serialized,
                    "token_count": tokens,
                }
            )

        if not args.dry_run and results:
            fmt_output = output_dir / fmt_name / args.split
            fmt_output.mkdir(parents=True, exist_ok=True)
            output_file = fmt_output / "data.jsonl"

            with open(output_file, "w", encoding="utf-8") as f:
                for r in results:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")

            avg_tokens = sum(token_counts) / len(token_counts)
            logger.info(
                "%s: %d items, avg %.1f tokens (min %d, max %d) -> %s",
                fmt_name,
                len(results),
                avg_tokens,
                min(token_counts),
                max(token_counts),
                output_file,
            )


if __name__ == "__main__":
    main()
