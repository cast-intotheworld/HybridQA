"""Abstract base class for serializers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from serialization.src.data_loader.schema import Evidence


class BaseSerializer(ABC):
    """Base class for all serialization formats.

    Subclasses must implement `serialize()` and `format_name`.
    """

    def __init__(self, params: dict | None = None) -> None:
        """Initialize serializer with optional parameters.

        :param params: Format-specific parameters from formats.yaml.
        """
        self._params = params or {}

    @abstractmethod
    def serialize(self, evidence: Evidence) -> str:
        """Serialize table, passages, and question into a text representation.

        :param evidence: Evidence containing table, passages, and question.
        :return: Serialized string representation.
        """

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return the canonical name of this format."""

    def get_evidence_set(self, evidence: Evidence) -> set[str]:
        """Extract all evidence strings for verification.

        Used by evidence_checker to verify information preservation across formats.

        :param evidence: Evidence containing table, passages, and question.
        :return: Set of all evidence text strings.
        """
        texts: set[str] = set()

        # Header texts
        for cell_text, _ in evidence.table.header:
            if cell_text.strip():
                texts.add(cell_text.strip())

        # Data cell texts
        for row in evidence.table.data:
            for cell_text, _ in row:
                if cell_text.strip():
                    texts.add(cell_text.strip())

        # Passage texts (relevant ones linked from the table)
        table_links = evidence.table.get_all_links()
        for url, passage_text in evidence.passages.items():
            if url in table_links and passage_text.strip():
                texts.add(passage_text.strip())

        return texts
