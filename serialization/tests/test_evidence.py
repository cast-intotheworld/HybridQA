"""Tests for evidence preservation checking."""

from __future__ import annotations

from serialization.src.data_loader.schema import Evidence
from serialization.src.evaluation.evidence_checker import (
    CheckResult,
    check_evidence_preservation,
    cross_format_check,
)
from serialization.src.serializers.registry import get_serializer

# Import all serializers
import serialization.src.serializers.json_format  # noqa: F401
import serialization.src.serializers.markdown  # noqa: F401
import serialization.src.serializers.html  # noqa: F401
import serialization.src.serializers.latex  # noqa: F401
import serialization.src.serializers.csv_format  # noqa: F401
import serialization.src.serializers.xml_format  # noqa: F401
import serialization.src.serializers.yaml_format  # noqa: F401


class TestEvidenceChecker:
    """Tests for evidence_checker.py."""

    def test_check_passes_for_json(self, sample_evidence: Evidence) -> None:
        """JSON format should pass evidence preservation check."""
        serializer = get_serializer("json")
        text = serializer.serialize(sample_evidence)
        result = check_evidence_preservation(sample_evidence, serializer, text)
        assert result.passed
        assert result.missing_cells == []
        assert result.missing_passages == []

    def test_check_fails_for_incomplete_text(self, sample_evidence: Evidence) -> None:
        """Check should fail when evidence is missing."""
        serializer = get_serializer("json")
        # Deliberately incomplete text
        result = check_evidence_preservation(sample_evidence, serializer, "incomplete text")
        assert not result.passed
        assert len(result.missing_cells) > 0

    def test_cross_format_check(self, sample_evidence: Evidence) -> None:
        """All formats should have the same evidence set."""
        serializers = [
            get_serializer("json"),
            get_serializer("html"),
            get_serializer("markdown"),
        ]
        results = cross_format_check(sample_evidence, serializers)
        for name_a, name_b, match, diff in results:
            assert match, f"Evidence mismatch between {name_a} and {name_b}: {diff}"
