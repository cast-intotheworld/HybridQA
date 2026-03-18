"""Format 7: Compressed (token-minimized) serialization."""

from __future__ import annotations

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.base import BaseSerializer
from serialization.src.serializers.registry import register


@register("compressed")
class CompressedSerializer(BaseSerializer):
    """Serialize evidence in a compressed, token-minimized format."""

    @property
    def format_name(self) -> str:
        return "compressed"

    def serialize(self, evidence: Evidence) -> str:
        """Serialize evidence into compressed format.

        Minimizes token usage by abbreviating headers, omitting empty cells,
        and using compact separators.

        :param evidence: Evidence containing table, passages, and question.
        :return: Compressed text representation.
        """
        abbreviate = self._params.get("abbreviate_headers", True)
        omit_empty = self._params.get("omit_empty_cells", True)
        sep = self._params.get("separator", ";")

        table = evidence.table
        header_names = [cell[0] for cell in table.header]

        if abbreviate:
            header_abbrevs = [self._abbreviate(name) for name in header_names]
        else:
            header_abbrevs = header_names

        lines: list[str] = []

        # Compact header
        lines.append(f"H:{sep.join(header_abbrevs)}")

        # Compact rows
        for row_idx, row in enumerate(table.data):
            parts = []
            for col_idx, (cell_text, _) in enumerate(row):
                if omit_empty and not cell_text.strip():
                    continue
                abbrev = (
                    header_abbrevs[col_idx] if col_idx < len(header_abbrevs) else f"c{col_idx}"
                )
                parts.append(f"{abbrev}={cell_text}")
            if parts:
                lines.append(f"R{row_idx}:{sep.join(parts)}")

        # Compact passages
        table_links = table.get_all_links()
        for url, text in evidence.passages.items():
            if url in table_links and text.strip():
                entity = url.split("/wiki/")[-1] if "/wiki/" in url else url
                lines.append(f"P[{entity}]:{text.strip()}")

        return "\n".join(lines)

    @staticmethod
    def _abbreviate(name: str) -> str:
        """Create a short abbreviation from a column name.

        :param name: Full column header name.
        :return: Abbreviated version.
        """
        words = name.split()
        if len(words) == 1:
            return name[:4].lower() if len(name) > 4 else name.lower()
        return "".join(w[0].lower() for w in words)
