"""Evidence preservation checker across serialization formats."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.base import BaseSerializer

logger = logging.getLogger(__name__)


@dataclass
class CheckResult:
    """Result of a single evidence preservation check.

    :param question_id: ID of the checked question.
    :param format_name: Name of the serialization format.
    :param passed: Whether all evidence was preserved.
    :param missing_cells: Cell texts not found in serialized output.
    :param missing_passages: Passage texts not found in serialized output.
    """

    question_id: str
    format_name: str
    passed: bool
    missing_cells: list[str] = field(default_factory=list)
    missing_passages: list[str] = field(default_factory=list)


def check_evidence_preservation(
    evidence: Evidence, serializer: BaseSerializer, serialized_text: str
) -> CheckResult:
    """Check whether all evidence is preserved in serialized output.

    :param evidence: Original evidence data.
    :param serializer: The serializer that produced the output.
    :param serialized_text: The serialized text to check.
    :return: CheckResult indicating pass/fail and any missing items.
    """
    missing_cells: list[str] = []
    missing_passages: list[str] = []

    # Check all cell texts from header and data
    for cell_text, _ in evidence.table.header:
        if cell_text.strip() and cell_text.strip() not in serialized_text:
            missing_cells.append(cell_text.strip())

    for row in evidence.table.data:
        for cell_text, _ in row:
            if cell_text.strip() and cell_text.strip() not in serialized_text:
                missing_cells.append(cell_text.strip())

    # Check passage texts (only those linked from the table)
    table_links = evidence.table.get_all_links()
    for url, passage_text in evidence.passages.items():
        if url in table_links and passage_text.strip():
            if passage_text.strip() not in serialized_text:
                missing_passages.append(f"{url}: {passage_text[:80]}...")

    passed = len(missing_cells) == 0 and len(missing_passages) == 0

    return CheckResult(
        question_id=evidence.question.question_id,
        format_name=serializer.format_name,
        passed=passed,
        missing_cells=missing_cells,
        missing_passages=missing_passages,
    )


def cross_format_check(
    evidence: Evidence,
    serializers: list[BaseSerializer],
) -> list[tuple[str, str, bool, set[str]]]:
    """Verify that all formats contain the same evidence set.

    :param evidence: Original evidence data.
    :param serializers: List of serializers to compare.
    :return: List of (format_a, format_b, match, difference) tuples.
    """
    evidence_sets: dict[str, set[str]] = {}

    for serializer in serializers:
        evidence_sets[serializer.format_name] = serializer.get_evidence_set(evidence)

    results: list[tuple[str, str, bool, set[str]]] = []
    format_names = list(evidence_sets.keys())

    for i in range(len(format_names)):
        for j in range(i + 1, len(format_names)):
            name_a = format_names[i]
            name_b = format_names[j]
            set_a = evidence_sets[name_a]
            set_b = evidence_sets[name_b]
            diff = set_a.symmetric_difference(set_b)
            results.append((name_a, name_b, len(diff) == 0, diff))

    return results
