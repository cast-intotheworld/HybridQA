"""Format 2: Flattened row-wise text serialization."""

from __future__ import annotations

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.base import BaseSerializer
from serialization.src.serializers.registry import register


@register("row_wise")
class RowWiseSerializer(BaseSerializer):
    """Serialize evidence as flattened row-wise text."""

    @property
    def format_name(self) -> str:
        return "row_wise"

    def serialize(self, evidence: Evidence) -> str:
        """Serialize evidence into row-wise text.

        Each row is represented as "col1: val1 | col2: val2 | ...".

        :param evidence: Evidence containing table, passages, and question.
        :return: Row-wise text representation.
        """
        row_sep = self._params.get("row_separator", "\n")
        cell_sep = self._params.get("cell_separator", " | ")
        include_header = self._params.get("include_header", True)

        table = evidence.table
        header_names = [cell[0] for cell in table.header]

        lines: list[str] = []

        if include_header:
            lines.append(f"Table: {table.title}" if table.title else "Table:")

        for row_idx, row in enumerate(table.data):
            parts = []
            for col_idx, (cell_text, _) in enumerate(row):
                col_name = header_names[col_idx] if col_idx < len(header_names) else f"col_{col_idx}"
                parts.append(f"{col_name}: {cell_text}")
            lines.append(f"Row {row_idx + 1}: {cell_sep.join(parts)}")

        # Append linked passages
        table_links = table.get_all_links()
        passage_lines: list[str] = []
        for url, text in evidence.passages.items():
            if url in table_links and text.strip():
                entity_name = url.replace("/wiki/", "").replace("_", " ")
                passage_lines.append(f"{entity_name}: {text.strip()}")

        if passage_lines:
            lines.append("")
            lines.append("Passages:")
            lines.extend(passage_lines)

        return row_sep.join(lines)
