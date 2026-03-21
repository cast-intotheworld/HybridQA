"""LaTeX table serialization."""

from __future__ import annotations

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.base import BaseSerializer
from serialization.src.serializers.registry import register


@register("latex")
class LaTeXSerializer(BaseSerializer):
    """Serialize evidence as a LaTeX tabular environment with passages."""

    @property
    def format_name(self) -> str:
        return "latex"

    def serialize(self, evidence: Evidence) -> str:
        """Serialize evidence into LaTeX tabular format.

        :param evidence: Evidence containing table, passages, and question.
        :return: LaTeX string representation.
        """
        table = evidence.table
        header_names = [cell[0] for cell in table.header]
        num_cols = len(header_names)

        col_spec = self._params.get("col_spec", "")
        if not col_spec:
            col_spec = "l" * num_cols

        lines: list[str] = []
        if table.title:
            lines.append(f"\\title{{{self._escape_latex(table.title)}}}")
            lines.append("")

        lines.append("\\begin{table}")
        lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
        lines.append("\\hline")

        # Header row
        escaped_headers = [self._escape_latex(h) for h in header_names]
        lines.append(" & ".join(escaped_headers) + " \\\\")
        lines.append("\\hline")

        # Data rows
        for row in table.data:
            cells = [self._escape_latex(cell[0]) for cell in row]
            # Pad if fewer cells than headers
            while len(cells) < num_cols:
                cells.append("")
            lines.append(" & ".join(cells) + " \\\\")

        lines.append("\\hline")
        lines.append("\\end{tabular}")
        lines.append("\\end{table}")

        # Passages
        lines.extend(self._format_passages(evidence))

        return "\n".join(lines)

    def _format_passages(self, evidence: Evidence) -> list[str]:
        """Format linked passages as LaTeX paragraphs.

        :param evidence: Evidence data.
        :return: List of LaTeX passage lines.
        """
        table_links = evidence.table.get_all_links()
        lines: list[str] = []
        passage_lines: list[str] = []

        for url, text in evidence.passages.items():
            if url in table_links and text.strip():
                entity_name = url.replace("/wiki/", "").replace("_", " ")
                escaped_name = self._escape_latex(entity_name)
                escaped_text = self._escape_latex(text.strip())
                passage_lines.append(
                    f"\\textbf{{{escaped_name}}}: {escaped_text}"
                )

        if passage_lines:
            lines.append("")
            lines.append("\\paragraph{Passages}")
            lines.extend(passage_lines)

        return lines

    @staticmethod
    def _escape_latex(text: str) -> str:
        """Escape LaTeX special characters.

        :param text: Raw text string.
        :return: Text with LaTeX special characters escaped.
        """
        replacements = [
            ("\\", "\\textbackslash{}"),
            ("&", "\\&"),
            ("%", "\\%"),
            ("$", "\\$"),
            ("#", "\\#"),
            ("_", "\\_"),
            ("{", "\\{"),
            ("}", "\\}"),
            ("~", "\\textasciitilde{}"),
            ("^", "\\textasciicircum{}"),
        ]
        for old, new in replacements:
            text = text.replace(old, new)
        return text
