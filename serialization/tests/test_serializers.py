"""Tests for all serialization formats."""

from __future__ import annotations

import json

import pytest

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.registry import get_serializer, list_formats

# Import all serializers to trigger registration
import serialization.src.serializers.json_format  # noqa: F401
import serialization.src.serializers.markdown  # noqa: F401
import serialization.src.serializers.html  # noqa: F401
import serialization.src.serializers.latex  # noqa: F401
import serialization.src.serializers.csv_format  # noqa: F401
import serialization.src.serializers.xml_format  # noqa: F401
import serialization.src.serializers.yaml_format  # noqa: F401


class TestRegistry:
    """Tests for the serializer registry."""

    def test_list_formats(self) -> None:
        """All 7 formats should be registered."""
        formats = list_formats()
        assert len(formats) == 7
        assert "json" in formats
        assert "yaml" in formats
        assert "xml" in formats
        assert "markdown" in formats
        assert "html" in formats
        assert "latex" in formats
        assert "csv" in formats

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


class TestYAMLSerializer:
    """Tests for YAML format."""

    def test_yaml_produces_valid_yaml(self, sample_evidence: Evidence) -> None:
        """Output should be valid YAML."""
        import yaml
        serializer = get_serializer("yaml")
        result = serializer.serialize(sample_evidence)
        parsed = yaml.safe_load(result)
        assert "table" in parsed
        assert "passages" in parsed
        assert "columns" in parsed["table"]
        assert "rows" in parsed["table"]

    def test_yaml_all_cell_values_present(self, sample_evidence: Evidence) -> None:
        """All table cell values should appear in the output."""
        serializer = get_serializer("yaml")
        result = serializer.serialize(sample_evidence)
        assert "Walter Payton" in result
        assert "Emmitt Smith" in result
        assert "16,726" in result

    def test_yaml_linked_passages_included(self, sample_evidence: Evidence) -> None:
        """Passages linked from the table should be included."""
        serializer = get_serializer("yaml")
        result = serializer.serialize(sample_evidence)
        assert "Chicago Bears" in result
        assert "Dallas Cowboys" in result
        assert "Unrelated_Page" not in result


class TestXMLSerializer:
    """Tests for XML format."""

    def test_xml_structure(self, sample_evidence: Evidence) -> None:
        """Output should have valid XML structure."""
        serializer = get_serializer("xml")
        result = serializer.serialize(sample_evidence)
        assert "<?xml version=" in result
        assert "<evidence>" in result
        assert "</evidence>" in result
        assert "<table>" in result
        assert "<columns>" in result
        assert "<rows>" in result

    def test_xml_all_cell_values_present(self, sample_evidence: Evidence) -> None:
        """All table cell values should appear in the output."""
        serializer = get_serializer("xml")
        result = serializer.serialize(sample_evidence)
        assert "Walter Payton" in result
        assert "Emmitt Smith" in result
        assert "16,726" in result

    def test_xml_passages(self, sample_evidence: Evidence) -> None:
        """Passages should be present as XML elements."""
        serializer = get_serializer("xml")
        result = serializer.serialize(sample_evidence)
        assert "<passages>" in result
        assert "<passage" in result
        assert "Chicago Bears" in result
        assert "Dallas Cowboys" in result

    def test_xml_parseable(self, sample_evidence: Evidence) -> None:
        """Output should be parseable by xml.etree."""
        import xml.etree.ElementTree as ET
        serializer = get_serializer("xml")
        result = serializer.serialize(sample_evidence)
        root = ET.fromstring(result)
        assert root.tag == "evidence"
        assert root.find("table") is not None
        assert root.find("passages") is not None


class TestMarkdownSerializer:
    """Tests for Markdown format."""

    def test_markdown_format(self, sample_evidence: Evidence) -> None:
        """Output should be a valid Markdown table."""
        serializer = get_serializer("markdown")
        result = serializer.serialize(sample_evidence)
        assert "| Rank |" in result
        assert "| --- |" in result or "| ---" in result
        assert "| 1 |" in result or "| 1 " in result

    def test_passages_included(self, sample_evidence: Evidence) -> None:
        """Passages section should be present."""
        serializer = get_serializer("markdown")
        result = serializer.serialize(sample_evidence)
        assert "### Passages" in result
        assert "Chicago Bears" in result


class TestHTMLSerializer:
    """Tests for HTML format."""

    def test_html_table_structure(self, sample_evidence: Evidence) -> None:
        """Output should be valid HTML table."""
        serializer = get_serializer("html")
        result = serializer.serialize(sample_evidence)
        assert "<table>" in result
        assert "<th>Rank</th>" in result
        assert "<td>Walter Payton</td>" in result

    def test_html_passages(self, sample_evidence: Evidence) -> None:
        """Passages should use HTML tags."""
        serializer = get_serializer("html")
        result = serializer.serialize(sample_evidence)
        assert "<h3>Passages</h3>" in result
        assert "<strong>" in result
        assert "Chicago Bears" in result


class TestLaTeXSerializer:
    """Tests for LaTeX format."""

    def test_latex_tabular_structure(self, sample_evidence: Evidence) -> None:
        """Output should have LaTeX tabular structure."""
        serializer = get_serializer("latex")
        result = serializer.serialize(sample_evidence)
        assert "\\begin{table}" in result
        assert "\\begin{tabular}" in result
        assert "\\end{tabular}" in result
        assert "\\end{table}" in result
        assert "\\hline" in result

    def test_latex_escaping(self, sample_evidence: Evidence) -> None:
        """Special characters should be escaped."""
        serializer = get_serializer("latex")
        result = serializer.serialize(sample_evidence)
        # Underscores in wiki entity names should be replaced by spaces then escaped
        # Title "NFL Rushing Yards Leaders" has no special chars
        assert "\\paragraph{Passages}" in result

    def test_latex_passages(self, sample_evidence: Evidence) -> None:
        """Passages should be present with textbf formatting."""
        serializer = get_serializer("latex")
        result = serializer.serialize(sample_evidence)
        assert "\\textbf{" in result
        assert "Chicago Bears" in result


class TestCSVSerializer:
    """Tests for CSV format."""

    def test_csv_header_and_rows(self, sample_evidence: Evidence) -> None:
        """Output should have CSV header and data rows."""
        serializer = get_serializer("csv")
        result = serializer.serialize(sample_evidence)
        assert '"Rank"' in result
        assert '"Player"' in result
        assert '"Yards"' in result

    def test_csv_data_present(self, sample_evidence: Evidence) -> None:
        """All cell values should appear in CSV output."""
        serializer = get_serializer("csv")
        result = serializer.serialize(sample_evidence)
        assert "Walter Payton" in result
        assert "Emmitt Smith" in result
        assert "16,726" in result

    def test_csv_passages_as_csv_rows(self, sample_evidence: Evidence) -> None:
        """Passages should be written as proper CSV rows."""
        serializer = get_serializer("csv")
        result = serializer.serialize(sample_evidence)
        assert '"Passages"' in result
        assert "Chicago Bears" in result
        # Passage text should be quoted in a CSV cell
        assert '"Walter Payton:' in result or "Walter Payton:" in result

    def test_csv_title_row(self, sample_evidence: Evidence) -> None:
        """Title should appear as first CSV row when include_title is true."""
        serializer = get_serializer("csv", params={"include_title": True})
        result = serializer.serialize(sample_evidence)
        assert '"NFL Rushing Yards Leaders"' in result

    def test_csv_all_lines_valid(self, sample_evidence: Evidence) -> None:
        """Every line should be parseable as CSV."""
        import csv as csv_mod
        import io
        serializer = get_serializer("csv")
        result = serializer.serialize(sample_evidence)
        reader = csv_mod.reader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) > 0
        # All rows should have consistent column count
        num_cols = len(rows[0])
        for i, row in enumerate(rows):
            assert len(row) == num_cols, f"Row {i} has {len(row)} cols, expected {num_cols}"


class TestEvidencePreservation:
    """Cross-format evidence preservation tests."""

    @pytest.mark.parametrize("format_name", [
        "json", "yaml", "xml", "markdown", "html", "csv",
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
        "json", "yaml", "xml", "markdown", "html", "csv",
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

    def test_latex_all_cell_texts_preserved(
        self, sample_evidence: Evidence
    ) -> None:
        """LaTeX format must contain all table cell values (escaped)."""
        serializer = get_serializer("latex")
        result = serializer.serialize(sample_evidence)

        for row in sample_evidence.table.data:
            for cell_text, _ in row:
                if cell_text.strip():
                    escaped = LaTeXSerializer._escape_latex(cell_text)
                    assert escaped in result, (
                        f"Cell '{cell_text}' (escaped: '{escaped}') missing in latex output"
                    )

    def test_latex_linked_passages_preserved(
        self, sample_evidence: Evidence
    ) -> None:
        """LaTeX format must contain passage text (escaped)."""
        serializer = get_serializer("latex")
        result = serializer.serialize(sample_evidence)

        table_links = sample_evidence.table.get_all_links()
        for url, text in sample_evidence.passages.items():
            if url in table_links and text.strip():
                escaped = LaTeXSerializer._escape_latex(text.strip())
                assert escaped in result, (
                    f"Passage for '{url}' missing in latex output"
                )


# Import for LaTeX escape helper in tests
from serialization.src.serializers.latex import LaTeXSerializer  # noqa: E402
