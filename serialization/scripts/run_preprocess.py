"""Preprocessing pipeline: load HybridQA + WikiTables data and validate."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from serialization.src.data_loader.hybridqa_loader import (
    get_unique_table_ids,
    load_questions,
)
from serialization.src.data_loader.wikitables_loader import WikiTablesLoader


def setup_logging(log_file: Path | None = None) -> logging.Logger:
    """Setup logging to both console and file.

    :param log_file: Optional log file path.
    :return: Configured logger.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess HybridQA data")
    parser.add_argument("--config", default="configs/base.yaml", help="Base config path")
    parser.add_argument("--split", default="dev", choices=["train", "dev", "test"])
    parser.add_argument("--check", action="store_true", help="Only check dependencies")
    parser.add_argument("--no-log-file", action="store_true", help="Disable log file")
    parser.add_argument("--sample-tables", type=int, default=5, help="Num tables to sample")
    args = parser.parse_args()

    # Setup logging
    base_dir = Path(__file__).resolve().parent.parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = None if args.no_log_file else (
        base_dir / "outputs" / "logs" / f"preprocess_{args.split}_{timestamp}.log"
    )
    logger = setup_logging(log_file)

    if log_file:
        logger.info("Logging to: %s", log_file)

    config_path = base_dir / args.config
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    data_path = (base_dir / config["paths"]["hybridqa_data"]).resolve()
    wikitables_path = (base_dir / config["paths"]["wikitables"]).resolve()

    logger.info("=" * 80)
    logger.info("HybridQA Preprocessing Pipeline")
    logger.info("Split: %s", args.split)
    logger.info("=" * 80)

    # Check WikiTables dependency
    if not wikitables_path.exists():
        logger.error(
            "WikiTables-WithLinks not found at %s\n"
            "Install with: cd %s && git clone https://github.com/wenhuchen/WikiTables-WithLinks",
            wikitables_path,
            base_dir.parent,
        )
        if args.check:
            sys.exit(1)
        logger.warning("Continuing without WikiTables (limited functionality)")
    else:
        logger.info("✓ WikiTables-WithLinks found at %s", wikitables_path)

        # Check subdirectories
        tables_dir = wikitables_path / "tables_tok"
        request_dir = wikitables_path / "request_tok"
        if tables_dir.exists() and request_dir.exists():
            num_tables = len(list(tables_dir.glob("*.json")))
            num_passages = len(list(request_dir.glob("*.json")))
            logger.info("  - tables_tok: %d files", num_tables)
            logger.info("  - request_tok: %d files", num_passages)
        else:
            logger.warning("  - Missing tables_tok or request_tok directories")

    if args.check:
        logger.info("✓ Dependency check passed")
        return

    # Load questions with progress bar
    logger.info("\nLoading questions from %s...", data_path)
    start_time = time.time()
    questions = load_questions(data_path, args.split)
    load_time = time.time() - start_time

    table_ids = get_unique_table_ids(questions)
    logger.info(
        "✓ Loaded %d questions, %d unique tables (%.2fs)",
        len(questions),
        len(table_ids),
        load_time,
    )

    # Analyze questions
    with_answer = sum(1 for q in questions if q.answer_text)
    with_nodes = sum(1 for q in questions if q.answer_nodes)
    logger.info("  - Questions with answer_text: %d", with_answer)
    logger.info("  - Questions with answer_nodes: %d", with_nodes)

    # Load sample tables if WikiTables available
    if wikitables_path.exists() and table_ids:
        logger.info("\nLoading sample tables...")
        loader = WikiTablesLoader(wikitables_path)

        num_samples = min(args.sample_tables, len(table_ids))
        sample_stats = {"total_rows": 0, "total_cols": 0, "total_passages": 0}
        start_time = time.time()

        for table_id in tqdm(
            table_ids[:num_samples],
            desc="Loading tables",
            unit="table",
        ):
            table, passages = loader.load_table_and_passages(table_id)
            sample_stats["total_rows"] += table.num_rows
            sample_stats["total_cols"] += table.num_cols
            sample_stats["total_passages"] += len(passages)

        load_time = time.time() - start_time

        # Statistics
        avg_rows = sample_stats["total_rows"] / num_samples
        avg_cols = sample_stats["total_cols"] / num_samples
        avg_passages = sample_stats["total_passages"] / num_samples

        logger.info(
            "✓ Loaded %d sample tables (%.2fs, %.1fms/table)",
            num_samples,
            load_time,
            (load_time / num_samples) * 1000,
        )
        logger.info("  - Avg table size: %.1f rows x %.1f cols", avg_rows, avg_cols)
        logger.info("  - Avg passages per table: %.1f", avg_passages)

        # Cache statistics
        cache_info = loader.cache_info()
        logger.info("\nCache statistics:")
        logger.info("  - Table cache: %s", cache_info["table_cache"])
        logger.info("  - Passage cache: %s", cache_info["passage_cache"])

    logger.info("\n" + "=" * 80)
    logger.info("✓ Preprocessing complete")
    logger.info("=" * 80)
    if log_file:
        logger.info("Full log saved to: %s", log_file)


if __name__ == "__main__":
    main()
