"""Format 6: Relation-explicit serialization."""

from __future__ import annotations

from serialization.src.data_loader.schema import Evidence
from serialization.src.serializers.base import BaseSerializer
from serialization.src.serializers.registry import register


@register("relation_explicit")
class RelationExplicitSerializer(BaseSerializer):
    """Serialize evidence as explicit relation triples."""

    @property
    def format_name(self) -> str:
        return "relation_explicit"

    def serialize(self, evidence: Evidence) -> str:
        """Serialize evidence into explicit relation triples.

        Each cell becomes a (subject, predicate, object) triple.

        :param evidence: Evidence containing table, passages, and question.
        :return: Relation-explicit text representation.
        """
        triple_format = self._params.get("triple_format", "natural")
        include_passages = self._params.get("include_passage_relations", True)

        table = evidence.table
        header_names = [cell[0] for cell in table.header]

        lines: list[str] = []
        if table.title:
            lines.append(f"Table: {table.title}")
            lines.append("")

        lines.append("Relations:")

        # Determine the subject column (first column typically identifies the entity)
        for row in table.data:
            if not row:
                continue
            subject = row[0][0]

            for col_idx in range(1, len(row)):
                predicate = (
                    header_names[col_idx] if col_idx < len(header_names) else f"col_{col_idx}"
                )
                obj = row[col_idx][0]

                if not obj.strip():
                    continue

                if triple_format == "tuple":
                    lines.append(f"({subject}, {predicate}, {obj})")
                else:
                    lines.append(f"{subject} — {predicate} — {obj}")

        # Passage relations
        if include_passages:
            table_links = table.get_all_links()
            passage_lines: list[str] = []
            for url, text in evidence.passages.items():
                if url in table_links and text.strip():
                    entity_name = url.replace("/wiki/", "").replace("_", " ")
                    passage_lines.append(
                        f"{entity_name} — description — {text.strip()}"
                    )

            if passage_lines:
                lines.append("")
                lines.append("Passage Relations:")
                lines.extend(passage_lines)

        return "\n".join(lines)
