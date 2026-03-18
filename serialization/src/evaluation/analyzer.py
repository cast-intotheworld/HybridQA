"""Breakdown analysis for Stage 5 experiments."""

from __future__ import annotations

import collections
from dataclasses import dataclass

from serialization.src.data_loader.schema import Question
from serialization.src.evaluation.metrics import compute_exact, compute_f1


@dataclass
class BreakdownResult:
    """Metrics broken down by a specific condition.

    :param condition: Name of the condition (e.g., "table", "passage").
    :param count: Number of examples in this group.
    :param exact_match: Average EM score (0-100).
    :param f1: Average F1 score (0-100).
    """

    condition: str
    count: int
    exact_match: float
    f1: float


def analyze_by_source(
    predictions: dict[str, str],
    reference: dict,
) -> list[BreakdownResult]:
    """Analyze metrics broken down by answer source (table vs passage).

    :param predictions: Dict mapping question_id to predicted answer.
    :param reference: Reference dict with 'reference', 'table', 'passage' keys.
    :return: List of BreakdownResult for each source type.
    """
    results: list[BreakdownResult] = []

    for source in ["table", "passage"]:
        qids = reference.get(source, [])
        if not qids:
            continue

        em_scores = []
        f1_scores = []
        for qid in qids:
            if qid in predictions and qid in reference["reference"]:
                gold = reference["reference"][qid]
                pred = predictions[qid]
                em_scores.append(compute_exact(gold, pred))
                f1_scores.append(compute_f1(gold, pred))

        if em_scores:
            results.append(
                BreakdownResult(
                    condition=source,
                    count=len(em_scores),
                    exact_match=100.0 * sum(em_scores) / len(em_scores),
                    f1=100.0 * sum(f1_scores) / len(f1_scores),
                )
            )

    return results


def analyze_by_table_size(
    predictions: dict[str, str],
    questions: list[Question],
    reference: dict,
    size_bins: list[tuple[str, int, int]] | None = None,
) -> list[BreakdownResult]:
    """Analyze metrics broken down by table size (number of rows).

    :param predictions: Dict mapping question_id to predicted answer.
    :param questions: List of Question objects (to access table_id for grouping).
    :param reference: Reference dict.
    :param size_bins: List of (label, min_rows, max_rows) tuples. Default: small/medium/large.
    :return: List of BreakdownResult for each size bin.
    """
    if size_bins is None:
        size_bins = [
            ("small (1-5 rows)", 1, 5),
            ("medium (6-15 rows)", 6, 15),
            ("large (16+ rows)", 16, 999999),
        ]

    # Group questions by table_id to count rows per table
    # Note: actual row counts require loading tables, so this is a placeholder
    # that groups by question for now. Override with actual table sizes when available.
    results: list[BreakdownResult] = []

    qid_to_question = {q.question_id: q for q in questions}
    table_questions: dict[str, list[str]] = collections.defaultdict(list)
    for q in questions:
        table_questions[q.table_id].append(q.question_id)

    # Without actual table data, return empty results
    # This will be populated when table sizes are available
    return results
