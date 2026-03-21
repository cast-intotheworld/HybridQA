"""Markdown table serialization."""

from __future__ import annotations

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.base import BaseSerializer
from serialization.src.serializers.registry import register


@register("markdown")
class MarkdownSerializer(BaseSerializer):
    """Serialize evidence as a Markdown table with passages."""

    @property
    def format_name(self) -> str:
        return "markdown"

    def serialize(self, evidence: Evidence) -> str:
        """Serialize evidence into Markdown table format.

        :param evidence: Evidence containing table, passages, and question.
        :return: Markdown table string.
        """
        table = evidence.table
        header_names = [cell[0] for cell in table.header]

        lines: list[str] = []
        if table.title:
            lines.append(f"## {table.title}")
            lines.append("")

        # Header row
        lines.append("| " + " | ".join(header_names) + " |")
        lines.append("| " + " | ".join("---" for _ in header_names) + " |")

        # Data rows
        for row in table.data:
            cells = [cell[0] for cell in row]
            # Pad if fewer cells than headers
            while len(cells) < len(header_names):
                cells.append("")
            lines.append("| " + " | ".join(cells) + " |")

        # Passages
        lines.extend(self._format_passages(evidence))

        return "\n".join(lines)

    def _format_passages(self, evidence: Evidence) -> list[str]:
        """Format linked passages as Markdown bold text.

        :param evidence: Evidence data.
        :return: List of passage text lines.
        """
        table_links = evidence.table.get_all_links()
        lines: list[str] = []
        passage_lines: list[str] = []

        for url, text in evidence.passages.items():
            if url in table_links and text.strip():
                entity_name = url.replace("/wiki/", "").replace("_", " ")
                passage_lines.append(f"**{entity_name}**: {text.strip()}")

        if passage_lines:
            lines.append("")
            lines.append("### Passages")
            lines.append("")
            lines.extend(passage_lines)

        return lines
