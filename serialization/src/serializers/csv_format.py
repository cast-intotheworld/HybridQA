"""CSV table serialization."""

from __future__ import annotations

import csv
import io

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.base import BaseSerializer
from serialization.src.serializers.registry import register


@register("csv")
class CSVSerializer(BaseSerializer):
    """Serialize evidence as CSV (RFC 4180) with passages appended."""

    @property
    def format_name(self) -> str:
        return "csv"

    def serialize(self, evidence: Evidence) -> str:
        """Serialize evidence into CSV format.

        The entire output is valid CSV: table rows, then an empty separator row,
        then passages as single-cell rows (quoted, with remaining columns empty).

        :param evidence: Evidence containing table, passages, and question.
        :return: CSV string where all lines are proper CSV rows.
        """
        delimiter = self._params.get("delimiter", ",")
        include_title = self._params.get("include_title", True)

        table = evidence.table
        header_names = [cell[0] for cell in table.header]
        num_cols = len(header_names)

        output = io.StringIO()
        writer = csv.writer(output, delimiter=delimiter, quoting=csv.QUOTE_ALL)

        # Optional title as a CSV row (text in first cell, rest empty)
        if include_title and table.title:
            writer.writerow([table.title] + [""] * (num_cols - 1))

        # Header row
        writer.writerow(header_names)

        # Data rows
        for row in table.data:
            cells = [cell[0] for cell in row]
            while len(cells) < num_cols:
                cells.append("")
            writer.writerow(cells)

        # Passages as CSV rows (text in first cell, rest empty)
        self._write_passages(writer, evidence, num_cols)

        return output.getvalue().rstrip("\r\n")

    def _write_passages(
        self,
        writer: csv.writer,
        evidence: Evidence,
        num_cols: int,
    ) -> None:
        """Write linked passages as CSV rows via the writer.

        Each passage becomes a row with the text in the first cell
        and empty strings for the remaining columns.

        :param writer: CSV writer instance.
        :param evidence: Evidence data.
        :param num_cols: Number of columns to pad to.
        """
        table_links = evidence.table.get_all_links()
        passage_rows: list[str] = []

        for url, text in evidence.passages.items():
            if url in table_links and text.strip():
                entity_name = url.replace("/wiki/", "").replace("_", " ")
                passage_rows.append(f"{entity_name}: {text.strip()}")

        if passage_rows:
            # Empty separator row
            writer.writerow([""] * num_cols)
            # "Passages" label row
            writer.writerow(["Passages"] + [""] * (num_cols - 1))
            for entry in passage_rows:
                writer.writerow([entry] + [""] * (num_cols - 1))
