"""Format 4: Markdown/HTML table serialization."""

from __future__ import annotations

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.base import BaseSerializer
from serialization.src.serializers.registry import register


@register("markdown")
class MarkdownHTMLSerializer(BaseSerializer):
    """Serialize evidence as a Markdown or HTML table with passages."""

    @property
    def format_name(self) -> str:
        return "markdown"

    def serialize(self, evidence: Evidence) -> str:
        """Serialize evidence into Markdown or HTML table format.

        :param evidence: Evidence containing table, passages, and question.
        :return: Markdown or HTML table string.
        """
        table_format = self._params.get("table_format", "markdown")

        if table_format == "html":
            return self._serialize_html(evidence)
        return self._serialize_markdown(evidence)

    def _serialize_markdown(self, evidence: Evidence) -> str:
        """Render as Markdown table.

        :param evidence: Evidence data.
        :return: Markdown string.
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

    def _serialize_html(self, evidence: Evidence) -> str:
        """Render as HTML table.

        :param evidence: Evidence data.
        :return: HTML string.
        """
        table = evidence.table
        header_names = [cell[0] for cell in table.header]

        lines: list[str] = []
        if table.title:
            lines.append(f"<h2>{table.title}</h2>")

        lines.append("<table>")
        lines.append("<thead><tr>")
        for name in header_names:
            lines.append(f"  <th>{name}</th>")
        lines.append("</tr></thead>")
        lines.append("<tbody>")

        for row in table.data:
            lines.append("<tr>")
            for cell_text, _ in row:
                lines.append(f"  <td>{cell_text}</td>")
            lines.append("</tr>")

        lines.append("</tbody>")
        lines.append("</table>")

        # Passages
        lines.extend(self._format_passages(evidence))

        return "\n".join(lines)

    def _format_passages(self, evidence: Evidence) -> list[str]:
        """Format linked passages.

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
