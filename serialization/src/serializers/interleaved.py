"""Format 5: Interleaved table-text serialization."""

from __future__ import annotations

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.base import BaseSerializer
from serialization.src.serializers.registry import register


@register("interleaved")
class InterleavedSerializer(BaseSerializer):
    """Serialize evidence by interleaving table rows with relevant passages."""

    @property
    def format_name(self) -> str:
        return "interleaved"

    def serialize(self, evidence: Evidence) -> str:
        """Serialize evidence with passages interleaved after relevant rows.

        :param evidence: Evidence containing table, passages, and question.
        :return: Interleaved text representation.
        """
        table = evidence.table
        header_names = [cell[0] for cell in table.header]
        passages = evidence.passages
        table_links = table.get_all_links()

        lines: list[str] = []
        if table.title:
            lines.append(f"Table: {table.title}")
            lines.append("")

        # Header
        lines.append("Columns: " + " | ".join(header_names))
        lines.append("")

        for row_idx, row in enumerate(table.data):
            # Row text
            parts = []
            for col_idx, (cell_text, _) in enumerate(row):
                col_name = (
                    header_names[col_idx] if col_idx < len(header_names) else f"col_{col_idx}"
                )
                parts.append(f"{col_name}: {cell_text}")
            lines.append(f"Row {row_idx + 1}: " + " | ".join(parts))

            # Collect links from this row and append passages
            row_links: set[str] = set()
            for _, cell_links in row:
                row_links.update(cell_links)

            for link in sorted(row_links):
                if link in passages and link in table_links:
                    text = passages[link].strip()
                    if text:
                        entity_name = link.replace("/wiki/", "").replace("_", " ")
                        lines.append(f"  [{entity_name}]: {text}")

            lines.append("")

        return "\n".join(lines).rstrip()
