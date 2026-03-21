"""HTML table serialization.

Uses stdlib ``html.escape()`` for proper escaping of special characters
(``<``, ``>``, ``&``, ``"``) in cell values and passage text.
"""

from __future__ import annotations

from html import escape

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.base import BaseSerializer
from serialization.src.serializers.registry import register


@register("html")
class HTMLSerializer(BaseSerializer):
    """Serialize evidence as an HTML table with passages."""

    @property
    def format_name(self) -> str:
        return "html"

    def serialize(self, evidence: Evidence) -> str:
        """Serialize evidence into HTML table format.

        :param evidence: Evidence containing table, passages, and question.
        :return: HTML table string.
        """
        table = evidence.table
        header_names = [cell[0] for cell in table.header]

        lines: list[str] = []
        if table.title:
            lines.append(f"<h2>{escape(table.title)}</h2>")

        lines.append("<table>")
        lines.append("<thead><tr>")
        for name in header_names:
            lines.append(f"  <th>{escape(name)}</th>")
        lines.append("</tr></thead>")
        lines.append("<tbody>")

        for row in table.data:
            lines.append("<tr>")
            for cell_text, _ in row:
                lines.append(f"  <td>{escape(cell_text)}</td>")
            lines.append("</tr>")

        lines.append("</tbody>")
        lines.append("</table>")

        # Passages
        lines.extend(self._format_passages(evidence))

        return "\n".join(lines)

    def _format_passages(self, evidence: Evidence) -> list[str]:
        """Format linked passages as HTML paragraphs.

        :param evidence: Evidence data.
        :return: List of HTML passage lines.
        """
        table_links = evidence.table.get_all_links()
        lines: list[str] = []
        passage_lines: list[str] = []

        for url, text in evidence.passages.items():
            if url in table_links and text.strip():
                entity_name = url.replace("/wiki/", "").replace("_", " ")
                passage_lines.append(
                    f"<p><strong>{escape(entity_name)}</strong>: {escape(text.strip())}</p>"
                )

        if passage_lines:
            lines.append("")
            lines.append("<h3>Passages</h3>")
            lines.extend(passage_lines)

        return lines
