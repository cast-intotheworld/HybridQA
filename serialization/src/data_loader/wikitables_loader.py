"""Loader for WikiTables-WithLinks table and passage data with LRU caching."""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path

from serialization.src.data_loader.schema import Table
from serialization.src.types import PassageMap, TableID

logger = logging.getLogger(__name__)


class WikiTablesLoader:
    """Loads tables and passages from WikiTables-WithLinks repository.

    Uses LRU caching since multiple questions reference the same table.

    :param wikitables_path: Path to the WikiTables-WithLinks directory.
    """

    def __init__(self, wikitables_path: str | Path) -> None:
        self._path = Path(wikitables_path)
        self._tables_dir = self._path / "tables_tok"
        self._passages_dir = self._path / "request_tok"
        self._validate_paths()

    def _validate_paths(self) -> None:
        """Validate that WikiTables-WithLinks directories exist."""
        if not self._path.exists():
            raise FileNotFoundError(
                f"WikiTables-WithLinks not found at {self._path}. "
                "Install with: git clone https://github.com/wenhuchen/WikiTables-WithLinks"
            )
        if not self._tables_dir.exists():
            raise FileNotFoundError(f"tables_tok directory not found at {self._tables_dir}")
        if not self._passages_dir.exists():
            raise FileNotFoundError(f"request_tok directory not found at {self._passages_dir}")

    @lru_cache(maxsize=2048)
    def load_table(self, table_id: TableID) -> Table:
        """Load a single table by its ID.

        :param table_id: Table identifier matching the JSON filename.
        :return: Table dataclass.
        """
        filepath = self._tables_dir / f"{table_id}.json"
        if not filepath.exists():
            raise FileNotFoundError(f"Table file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)

        header = [(cell[0], cell[1]) for cell in raw.get("header", [])]
        data = [
            [(cell[0], cell[1]) for cell in row]
            for row in raw.get("data", [])
        ]

        return Table(
            table_id=table_id,
            header=header,
            data=data,
            title=raw.get("title", ""),
            section_title=raw.get("section_title", ""),
        )

    @lru_cache(maxsize=2048)
    def load_passages(self, table_id: TableID) -> PassageMap:
        """Load passages linked from a table.

        :param table_id: Table identifier matching the JSON filename.
        :return: Dict mapping wiki_url to passage text.
        """
        filepath = self._passages_dir / f"{table_id}.json"
        if not filepath.exists():
            logger.warning("Passage file not found: %s", filepath)
            return {}

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_table_and_passages(
        self, table_id: TableID
    ) -> tuple[Table, PassageMap]:
        """Load both table and passages for a given table_id.

        :param table_id: Table identifier.
        :return: Tuple of (Table, PassageMap).
        """
        table = self.load_table(table_id)
        passages = self.load_passages(table_id)
        return table, passages

    @property
    def path(self) -> Path:
        """Return the WikiTables-WithLinks root path."""
        return self._path

    def clear_cache(self) -> None:
        """Clear the LRU caches."""
        self.load_table.cache_clear()
        self.load_passages.cache_clear()

    def cache_info(self) -> dict[str, object]:
        """Return cache statistics.

        :return: Dict with table and passage cache info.
        """
        return {
            "table_cache": self.load_table.cache_info(),
            "passage_cache": self.load_passages.cache_info(),
        }
