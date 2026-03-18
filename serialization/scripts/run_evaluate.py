"""Evaluation pipeline: compute EM/F1 metrics and comparison tables."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from serialization.src.data_loader.hybridqa_loader import load_reference
from serialization.src.evaluation.metrics import get_raw_scores

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate predictions")
    parser.add_argument("predictions", nargs="?", help="Predictions JSONL file")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--ref", default=None, help="Reference file path")
    parser.add_argument("--compare", action="store_true", help="Compare all results")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / args.config
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    data_path = (base_dir / config["paths"]["hybridqa_data"]).resolve()

    # Load reference
    if args.ref:
        with open(args.ref, "r") as f:
            reference = json.load(f)
    else:
        reference = load_reference(data_path, "dev")

    if args.compare:
        # Compare all results in outputs/results/
        results_dir = base_dir / config["paths"]["output_dir"] / "results"
        if not results_dir.exists():
            logger.error("No results directory found at %s", results_dir)
            sys.exit(1)

        print("\n| Format | Table EM | Table F1 | Pass EM | Pass F1 | Total EM | Total F1 |")
        print("|--------|----------|----------|---------|---------|----------|----------|")

        for metrics_file in sorted(results_dir.glob("*/metrics.json")):
            with open(metrics_file, "r") as f:
                metrics = json.load(f)
            name = metrics_file.parent.name
            print(
                f"| {name:<6} | {metrics.get('table exact', 0):8.1f} "
                f"| {metrics.get('table f1', 0):8.1f} "
                f"| {metrics.get('passage exact', 0):7.1f} "
                f"| {metrics.get('passage f1', 0):7.1f} "
                f"| {metrics.get('total exact', 0):8.1f} "
                f"| {metrics.get('total f1', 0):8.1f} |"
            )
        return

    if not args.predictions:
        parser.error("predictions file is required unless using --compare")

    # Load predictions
    predictions_path = Path(args.predictions)
    examples: list[dict] = []

    with open(predictions_path, "r") as f:
        if predictions_path.suffix == ".jsonl":
            for line in f:
                examples.append(json.loads(line.strip()))
        else:
            examples = json.load(f)

    # Compute metrics
    scores = get_raw_scores(examples, reference)

    print("\nResults:")
    for key, value in scores.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    # Save results
    if predictions_path.parent.name != ".":
        output_dir = base_dir / config["paths"]["output_dir"] / "results" / predictions_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "metrics.json", "w") as f:
            json.dump(dict(scores), f, indent=2)
        logger.info("Saved metrics to %s", output_dir / "metrics.json")


if __name__ == "__main__":
    main()
