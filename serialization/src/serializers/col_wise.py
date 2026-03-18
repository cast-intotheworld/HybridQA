"""Format 3: Flattened column-wise text serialization."""

from __future__ import annotations

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.base import BaseSerializer
from serialization.src.serializers.registry import register


@register("col_wise")
class ColWiseSerializer(BaseSerializer):
    """Serialize evidence as flattened column-wise text."""

    @property
    def format_name(self) -> str:
        return "col_wise"

    def serialize(self, evidence: Evidence) -> str:
        """Serialize evidence into column-wise text.

        Each column is listed with all its values.

        :param evidence: Evidence containing table, passages, and question.
        :return: Column-wise text representation.
        """
        col_sep = self._params.get("col_separator", "\n")
        value_sep = self._params.get("value_separator", ", ")
        include_header = self._params.get("include_header", True)

        table = evidence.table
        header_names = [cell[0] for cell in table.header]

        lines: list[str] = []

        if include_header and table.title:
            lines.append(f"Table: {table.title}")

        for col_idx, col_name in enumerate(header_names):
            values = []
            for row in table.data:
                if col_idx < len(row):
                    values.append(row[col_idx][0])
            lines.append(f"{col_name}: {value_sep.join(values)}")

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

        return col_sep.join(lines)
