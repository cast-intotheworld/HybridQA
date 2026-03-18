"""Core dataclasses for HybridQA data representation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AnswerNode:
    """A single answer node from traced HybridQA data.

    :param text: Answer text content.
    :param position: (row_idx, col_idx) position in the table.
    :param wiki_link: Wikipedia URL if the answer comes from a linked passage.
    :param source: "table" or "passage" indicating where the answer was found.
    """

    text: str
    position: tuple[int, int]
    wiki_link: str | None = None
    source: str = "table"


@dataclass
class Question:
    """A single HybridQA question.

    :param question_id: Unique identifier for the question.
    :param question: The question text.
    :param table_id: ID of the associated table.
    :param answer_text: Gold answer text (None for test split).
    :param answer_nodes: List of answer nodes from traced data.
    """

    question_id: str
    question: str
    table_id: str
    answer_text: str | None = None
    answer_nodes: list[AnswerNode] = field(default_factory=list)


@dataclass
class Table:
    """A WikiTable with linked entities.

    :param table_id: Unique identifier matching WikiTables-WithLinks filename.
    :param header: List of (cell_text, [wiki_urls]) tuples for header row.
    :param data: 2D list of (cell_text, [wiki_urls]) tuples for data rows.
    :param title: Table title from Wikipedia page.
    :param section_title: Section title within the Wikipedia page.
    """

    table_id: str
    header: list[tuple[str, list[str]]]
    data: list[list[tuple[str, list[str]]]]
    title: str = ""
    section_title: str = ""

    @property
    def num_rows(self) -> int:
        """Return the number of data rows."""
        return len(self.data)

    @property
    def num_cols(self) -> int:
        """Return the number of columns."""
        return len(self.header) if self.header else 0

    def get_cell_text(self, row: int, col: int) -> str:
        """Get text content of a specific cell.

        :param row: Row index (0-based).
        :param col: Column index (0-based).
        :return: Cell text content.
        """
        return self.data[row][col][0]

    def get_cell_links(self, row: int, col: int) -> list[str]:
        """Get wiki links of a specific cell.

        :param row: Row index (0-based).
        :param col: Column index (0-based).
        :return: List of wiki URLs.
        """
        return self.data[row][col][1]

    def get_all_cell_texts(self) -> list[str]:
        """Get all cell text values (header + data).

        :return: List of all cell text strings.
        """
        texts = [cell[0] for cell in self.header]
        for row in self.data:
            texts.extend(cell[0] for cell in row)
        return texts

    def get_all_links(self) -> set[str]:
        """Get all unique wiki links from the table.

        :return: Set of wiki URLs.
        """
        links: set[str] = set()
        for cell in self.header:
            links.update(cell[1])
        for row in self.data:
            for cell in row:
                links.update(cell[1])
        return links


@dataclass
class Evidence:
    """Combined evidence for a single QA instance.

    :param table: The associated table.
    :param passages: Mapping from wiki_url to passage text.
    :param question: The question with answer annotations.
    """

    table: Table
    passages: dict[str, str]
    question: Question
