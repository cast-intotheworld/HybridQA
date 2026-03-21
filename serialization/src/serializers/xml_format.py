"""XML serialization.

Uses stdlib ``xml.etree.ElementTree`` to build a well-formed XML tree
and ``ET.indent()`` (Python 3.9+) for pretty-printing.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.base import BaseSerializer
from serialization.src.serializers.registry import register


@register("xml")
class XMLSerializer(BaseSerializer):
    """Serialize evidence as XML preserving original hierarchy."""

    @property
    def format_name(self) -> str:
        return "xml"

    def serialize(self, evidence: Evidence) -> str:
        """Serialize evidence into XML format.

        Builds an ElementTree, then serializes to a string.

        :param evidence: Evidence containing table, passages, and question.
        :return: XML string representation.
        """
        indent = self._params.get("indent", 2)
        include_metadata = self._params.get("include_metadata", True)

        table = evidence.table
        header_names = [cell[0] for cell in table.header]

        root = ET.Element("evidence")

        # Table section
        table_elem = ET.SubElement(root, "table")
        if include_metadata:
            title_elem = ET.SubElement(table_elem, "title")
            title_elem.text = table.title
            section_elem = ET.SubElement(table_elem, "section_title")
            section_elem.text = table.section_title

        # Columns
        columns_elem = ET.SubElement(table_elem, "columns")
        for name in header_names:
            col_elem = ET.SubElement(columns_elem, "column")
            col_elem.text = name

        # Rows
        rows_elem = ET.SubElement(table_elem, "rows")
        for row in table.data:
            row_elem = ET.SubElement(rows_elem, "row")
            for col_idx, (cell_text, cell_links) in enumerate(row):
                col_name = (
                    header_names[col_idx]
                    if col_idx < len(header_names)
                    else f"col_{col_idx}"
                )
                tag = _to_tag_name(col_name)
                cell_elem = ET.SubElement(row_elem, tag)
                cell_elem.text = cell_text
                for link in cell_links:
                    link_elem = ET.SubElement(row_elem, "link")
                    link_elem.set("column", tag)
                    link_elem.text = link

        # Passages section
        self._add_passages(root, evidence)

        # Pretty-print
        ET.indent(root, space=" " * indent)
        return ET.tostring(
            root, encoding="unicode", xml_declaration=True,
        )

    def _add_passages(self, root: ET.Element, evidence: Evidence) -> None:
        """Add linked passages as XML sub-elements.

        :param root: Root XML element to attach passages to.
        :param evidence: Evidence data.
        """
        table_links = evidence.table.get_all_links()
        entries: list[tuple[str, str]] = []

        for url, text in evidence.passages.items():
            if url in table_links and text.strip():
                entries.append((url, text.strip()))

        if entries:
            passages_elem = ET.SubElement(root, "passages")
            for url, text in entries:
                passage_elem = ET.SubElement(passages_elem, "passage")
                passage_elem.set("url", url)
                passage_elem.text = text


def _to_tag_name(name: str) -> str:
    """Convert a column name to a valid XML tag name.

    Replaces spaces and special characters with underscores,
    ensures the tag starts with a letter or underscore.

    :param name: Raw column name.
    :return: Valid XML tag name.
    """
    tag = name.replace(" ", "_")
    tag = "".join(c if c.isalnum() or c == "_" else "_" for c in tag)
    if tag and not (tag[0].isalpha() or tag[0] == "_"):
        tag = f"_{tag}"
    return tag or "_unknown"
