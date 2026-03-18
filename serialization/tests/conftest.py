"""Shared fixtures for serialization tests."""

from __future__ import annotations

import pytest

from serialization.src.data_loader.schema import AnswerNode, Evidence, Question, Table


@pytest.fixture
def sample_header() -> list[tuple[str, list[str]]]:
    """Sample table header with 3 columns."""
    return [
        ("Rank", []),
        ("Player", ["/wiki/Walter_Payton", "/wiki/Emmitt_Smith"]),
        ("Yards", []),
    ]


@pytest.fixture
def sample_data() -> list[list[tuple[str, list[str]]]]:
    """Sample table data with 3 rows x 3 columns."""
    return [
        [
            ("1", []),
            ("Walter Payton", ["/wiki/Walter_Payton"]),
            ("16,726", []),
        ],
        [
            ("2", []),
            ("Emmitt Smith", ["/wiki/Emmitt_Smith"]),
            ("18,355", []),
        ],
        [
            ("3", []),
            ("Barry Sanders", ["/wiki/Barry_Sanders"]),
            ("15,269", []),
        ],
    ]


@pytest.fixture
def sample_table(sample_header, sample_data) -> Table:
    """Sample Table dataclass."""
    return Table(
        table_id="NFL_rushing_leaders_0",
        header=sample_header,
        data=sample_data,
        title="NFL Rushing Yards Leaders",
        section_title="All-time leaders",
    )


@pytest.fixture
def sample_passages() -> dict[str, str]:
    """Sample passages linked from the table."""
    return {
        "/wiki/Walter_Payton": (
            "Walter Jerry Payton was an American football running back "
            "who played for the Chicago Bears."
        ),
        "/wiki/Emmitt_Smith": (
            "Emmitt James Smith III is a former American football running back "
            "who played for the Dallas Cowboys."
        ),
        "/wiki/Barry_Sanders": (
            "Barry Sanders is a former American football running back "
            "who played for the Detroit Lions."
        ),
        "/wiki/Unrelated_Page": "This passage is not linked from the table.",
    }


@pytest.fixture
def sample_question() -> Question:
    """Sample Question dataclass."""
    return Question(
        question_id="test_q_001",
        question="Who has the most rushing yards in NFL history?",
        table_id="NFL_rushing_leaders_0",
        answer_text="Emmitt Smith",
        answer_nodes=[
            AnswerNode(
                text="Emmitt Smith",
                position=(1, 1),
                wiki_link="/wiki/Emmitt_Smith",
                source="table",
            )
        ],
    )


@pytest.fixture
def sample_evidence(sample_table, sample_passages, sample_question) -> Evidence:
    """Sample Evidence combining table, passages, and question."""
    return Evidence(
        table=sample_table,
        passages=sample_passages,
        question=sample_question,
    )
