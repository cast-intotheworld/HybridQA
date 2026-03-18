"""Tests for all serialization formats."""

from __future__ import annotations

import json

import pytest

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.registry import get_serializer, list_formats

# Import all serializers to trigger registration
import serialization.src.serializers.json_format  # noqa: F401
import serialization.src.serializers.row_wise  # noqa: F401
import serialization.src.serializers.col_wise  # noqa: F401
import serialization.src.serializers.markdown_html  # noqa: F401
import serialization.src.serializers.interleaved  # noqa: F401
import serialization.src.serializers.relation_explicit  # noqa: F401
import serialization.src.serializers.compressed  # noqa: F401


class TestRegistry:
    """Tests for the serializer registry."""

    def test_list_formats(self) -> None:
        """All 7 formats should be registered."""
        formats = list_formats()
        assert len(formats) == 7
        assert "json" in formats
        assert "row_wise" in formats
        assert "col_wise" in formats
        assert "markdown" in formats
        assert "interleaved" in formats
        assert "relation_explicit" in formats
        assert "compressed" in formats

    def test_get_serializer(self) -> None:
        """Get a serializer by name."""
        serializer = get_serializer("json")
        assert serializer.format_name == "json"

    def test_unknown_format(self) -> None:
        """KeyError for unknown format name."""
        with pytest.raises(KeyError, match="not found"):
            get_serializer("nonexistent")


class TestJSONSerializer:
    """Tests for Format 1: Structured JSON."""

    def test_serialize_produces_valid_json(self, sample_evidence: Evidence) -> None:
        """Output should be valid JSON."""
        serializer = get_serializer("json")
        result = serializer.serialize(sample_evidence)
        parsed = json.loads(result)
        assert "table" in parsed
        assert "passages" in parsed
        assert "columns" in parsed["table"]
        assert "rows" in parsed["table"]

    def test_all_cell_values_present(self, sample_evidence: Evidence) -> None:
        """All table cell values should appear in the output."""
        serializer = get_serializer("json")
        result = serializer.serialize(sample_evidence)
        assert "Walter Payton" in result
        assert "Emmitt Smith" in result
        assert "Barry Sanders" in result
        assert "16,726" in result

    def test_linked_passages_included(self, sample_evidence: Evidence) -> None:
        """Passages linked from the table should be included."""
        serializer = get_serializer("json")
        result = serializer.serialize(sample_evidence)
        assert "Chicago Bears" in result
        assert "Dallas Cowboys" in result
        # Unrelated passage should NOT be included
        assert "Unrelated_Page" not in result


class TestRowWiseSerializer:
    """Tests for Format 2: Row-wise text."""

    def test_row_format(self, sample_evidence: Evidence) -> None:
        """Each row should contain column labels and values."""
        serializer = get_serializer("row_wise")
        result = serializer.serialize(sample_evidence)
        assert "Row 1:" in result
        assert "Rank: 1" in result
        assert "Player: Walter Payton" in result

    def test_passages_section(self, sample_evidence: Evidence) -> None:
        """Passages section should be present."""
        serializer = get_serializer("row_wise")
        result = serializer.serialize(sample_evidence)
        assert "Passages:" in result


class TestColWiseSerializer:
    """Tests for Format 3: Column-wise text."""

    def test_column_format(self, sample_evidence: Evidence) -> None:
        """Each column should list all its values."""
        serializer = get_serializer("col_wise")
        result = serializer.serialize(sample_evidence)
        assert "Rank:" in result
        assert "Player:" in result
        # All values in one line
        assert "Walter Payton" in result
        assert "Emmitt Smith" in result


class TestMarkdownSerializer:
    """Tests for Format 4: Markdown/HTML."""

    def test_markdown_format(self, sample_evidence: Evidence) -> None:
        """Output should be a valid Markdown table."""
        serializer = get_serializer("markdown")
        result = serializer.serialize(sample_evidence)
        assert "| Rank |" in result
        assert "| --- |" in result or "| ---" in result
        assert "| 1 |" in result or "| 1 " in result

    def test_html_format(self, sample_evidence: Evidence) -> None:
        """Output should be valid HTML table when configured."""
        serializer = get_serializer("markdown", params={"table_format": "html"})
        result = serializer.serialize(sample_evidence)
        assert "<table>" in result
        assert "<th>Rank</th>" in result
        assert "<td>Walter Payton</td>" in result


class TestInterleavedSerializer:
    """Tests for Format 5: Interleaved."""

    def test_passages_after_rows(self, sample_evidence: Evidence) -> None:
        """Passages should appear after relevant rows."""
        serializer = get_serializer("interleaved")
        result = serializer.serialize(sample_evidence)
        lines = result.split("\n")
        # Find Walter Payton row, passage should be nearby
        payton_idx = next(i for i, l in enumerate(lines) if "Walter Payton" in l)
        # Check that passage appears within a few lines
        nearby = "\n".join(lines[payton_idx : payton_idx + 5])
        assert "Chicago Bears" in nearby


class TestRelationExplicitSerializer:
    """Tests for Format 6: Relation-explicit."""

    def test_triple_format(self, sample_evidence: Evidence) -> None:
        """Output should contain relation triples."""
        serializer = get_serializer("relation_explicit")
        result = serializer.serialize(sample_evidence)
        assert "Relations:" in result
        # Subject — Predicate — Object format
        assert "—" in result or "(" in result


class TestCompressedSerializer:
    """Tests for Format 7: Compressed."""

    def test_compressed_header(self, sample_evidence: Evidence) -> None:
        """Output should have abbreviated header."""
        serializer = get_serializer("compressed")
        result = serializer.serialize(sample_evidence)
        assert result.startswith("H:")

    def test_compact_rows(self, sample_evidence: Evidence) -> None:
        """Rows should use compact R0, R1, ... prefix."""
        serializer = get_serializer("compressed")
        result = serializer.serialize(sample_evidence)
        assert "R0:" in result
        assert "R1:" in result

    def test_all_data_preserved(self, sample_evidence: Evidence) -> None:
        """Even compressed format should preserve all cell values."""
        serializer = get_serializer("compressed")
        result = serializer.serialize(sample_evidence)
        assert "Walter Payton" in result
        assert "18,355" in result


class TestEvidencePreservation:
    """Cross-format evidence preservation tests."""

    @pytest.mark.parametrize("format_name", [
        "json", "row_wise", "col_wise", "markdown",
        "interleaved", "relation_explicit", "compressed",
    ])
    def test_all_cell_texts_preserved(
        self, sample_evidence: Evidence, format_name: str
    ) -> None:
        """Every format must contain all table cell text values."""
        serializer = get_serializer(format_name)
        result = serializer.serialize(sample_evidence)

        for row in sample_evidence.table.data:
            for cell_text, _ in row:
                if cell_text.strip():
                    assert cell_text in result, (
                        f"Cell '{cell_text}' missing in {format_name} output"
                    )

    @pytest.mark.parametrize("format_name", [
        "json", "row_wise", "col_wise", "markdown",
        "interleaved", "relation_explicit", "compressed",
    ])
    def test_linked_passages_preserved(
        self, sample_evidence: Evidence, format_name: str
    ) -> None:
        """Every format must contain text from linked passages."""
        serializer = get_serializer(format_name)
        result = serializer.serialize(sample_evidence)

        table_links = sample_evidence.table.get_all_links()
        for url, text in sample_evidence.passages.items():
            if url in table_links and text.strip():
                assert text.strip() in result, (
                    f"Passage for '{url}' missing in {format_name} output"
                )
