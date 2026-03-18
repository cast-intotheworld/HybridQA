"""Format 1: Structured JSON serialization."""

from __future__ import annotations

import json

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.base import BaseSerializer
from serialization.src.serializers.registry import register


@register("json")
class JSONSerializer(BaseSerializer):
    """Serialize evidence as structured JSON preserving original hierarchy."""

    @property
    def format_name(self) -> str:
        return "json"

    def serialize(self, evidence: Evidence) -> str:
        """Serialize evidence into structured JSON.

        :param evidence: Evidence containing table, passages, and question.
        :return: JSON string representation.
        """
        indent = self._params.get("indent", 2)
        include_metadata = self._params.get("include_metadata", True)

        table = evidence.table
        header_names = [cell[0] for cell in table.header]

        rows = []
        for row_idx, row in enumerate(table.data):
            row_dict: dict[str, object] = {}
            for col_idx, (cell_text, cell_links) in enumerate(row):
                col_name = header_names[col_idx] if col_idx < len(header_names) else f"col_{col_idx}"
                row_dict[col_name] = cell_text
                if cell_links:
                    row_dict[f"{col_name}_links"] = cell_links
            rows.append(row_dict)

        # Collect passages linked from the table
        table_links = table.get_all_links()
        linked_passages = {
            url: text
            for url, text in evidence.passages.items()
            if url in table_links
        }

        output: dict[str, object] = {
            "table": {
                "columns": header_names,
                "rows": rows,
            },
            "passages": linked_passages,
        }

        if include_metadata:
            output["table"]["title"] = table.title
            output["table"]["section_title"] = table.section_title

        return json.dumps(output, ensure_ascii=False, indent=indent)
