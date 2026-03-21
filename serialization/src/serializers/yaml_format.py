"""YAML serialization."""

from __future__ import annotations

import yaml

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.base import BaseSerializer
from serialization.src.serializers.registry import register


@register("yaml")
class YAMLSerializer(BaseSerializer):
    """Serialize evidence as YAML preserving original hierarchy."""

    @property
    def format_name(self) -> str:
        return "yaml"

    def serialize(self, evidence: Evidence) -> str:
        """Serialize evidence into YAML format.

        :param evidence: Evidence containing table, passages, and question.
        :return: YAML string representation.
        """
        default_flow_style = self._params.get("default_flow_style", False)
        include_metadata = self._params.get("include_metadata", True)

        table = evidence.table
        header_names = [cell[0] for cell in table.header]

        rows = []
        for row in table.data:
            row_dict: dict[str, object] = {}
            for col_idx, (cell_text, cell_links) in enumerate(row):
                col_name = (
                    header_names[col_idx]
                    if col_idx < len(header_names)
                    else f"col_{col_idx}"
                )
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

        return yaml.dump(
            output,
            allow_unicode=True,
            default_flow_style=default_flow_style,
            sort_keys=False,
            width=2147483647,
        ).rstrip("\n")
