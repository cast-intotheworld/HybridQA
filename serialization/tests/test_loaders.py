"""Tests for data loaders."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from serialization.src.data_loader.hybridqa_loader import (
    get_unique_table_ids,
    group_by_table,
    load_questions,
    load_reference,
)
from serialization.src.data_loader.schema import Question
from serialization.src.data_loader.wikitables_loader import WikiTablesLoader


class TestHybridQALoader:
    """Tests for hybridqa_loader.py."""

    def test_load_questions_from_json(self, tmp_path: Path) -> None:
        """Load questions from a sample JSON file."""
        data = [
            {
                "question_id": "q001",
                "question": "What is the capital?",
                "table_id": "table_0",
                "answer-text": "Paris",
            },
            {
                "question_id": "q002",
                "question": "Who scored most?",
                "table_id": "table_1",
                "answer-text": "Messi",
            },
        ]
        filepath = tmp_path / "dev.json"
        filepath.write_text(json.dumps(data))

        questions = load_questions(tmp_path, "dev", traced=False)
        assert len(questions) == 2
        assert questions[0].question_id == "q001"
        assert questions[0].answer_text == "Paris"
        assert questions[0].table_id == "table_0"

    def test_load_traced_questions(self, tmp_path: Path) -> None:
        """Load traced questions with answer-node annotations."""
        data = [
            {
                "question_id": "q001",
                "question": "Who is ranked first?",
                "table_id": "table_0",
                "answer-text": "Payton",
                "answer-node": [
                    ["Payton", [0, 1], "/wiki/Walter_Payton", "table"]
                ],
            }
        ]
        filepath = tmp_path / "dev.traced.json"
        filepath.write_text(json.dumps(data))

        questions = load_questions(tmp_path, "dev", traced=True)
        assert len(questions) == 1
        assert len(questions[0].answer_nodes) == 1
        assert questions[0].answer_nodes[0].text == "Payton"
        assert questions[0].answer_nodes[0].position == (0, 1)
        assert questions[0].answer_nodes[0].source == "table"

    def test_load_questions_file_not_found(self, tmp_path: Path) -> None:
        """Raise FileNotFoundError for missing data file."""
        with pytest.raises(FileNotFoundError):
            load_questions(tmp_path, "dev")

    def test_load_reference(self, tmp_path: Path) -> None:
        """Load reference answers for evaluation."""
        ref = {
            "reference": {"q001": "Paris", "q002": "Messi"},
            "table": ["q001"],
            "passage": ["q002"],
        }
        filepath = tmp_path / "dev_reference.json"
        filepath.write_text(json.dumps(ref))

        result = load_reference(tmp_path, "dev")
        assert result["reference"]["q001"] == "Paris"
        assert "q001" in result["table"]

    def test_get_unique_table_ids(self) -> None:
        """Extract unique table IDs from questions."""
        questions = [
            Question(question_id="q1", question="?", table_id="t1"),
            Question(question_id="q2", question="?", table_id="t2"),
            Question(question_id="q3", question="?", table_id="t1"),
        ]
        table_ids = get_unique_table_ids(questions)
        assert table_ids == ["t1", "t2"]

    def test_group_by_table(self) -> None:
        """Group questions by table_id."""
        questions = [
            Question(question_id="q1", question="?", table_id="t1"),
            Question(question_id="q2", question="?", table_id="t2"),
            Question(question_id="q3", question="?", table_id="t1"),
        ]
        groups = group_by_table(questions)
        assert len(groups) == 2
        assert len(groups["t1"]) == 2
        assert len(groups["t2"]) == 1


class TestWikiTablesLoader:
    """Tests for wikitables_loader.py."""

    def test_load_table(self, tmp_path: Path) -> None:
        """Load a table from a JSON file."""
        tables_dir = tmp_path / "tables_tok"
        tables_dir.mkdir()
        request_dir = tmp_path / "request_tok"
        request_dir.mkdir()

        table_data = {
            "header": [["Rank", []], ["Player", ["/wiki/Test"]]],
            "data": [[["1", []], ["Test Player", ["/wiki/Test"]]]],
            "title": "Test Table",
            "section_title": "Section",
            "uid": "test_table_0",
        }
        (tables_dir / "test_table_0.json").write_text(json.dumps(table_data))
        (request_dir / "test_table_0.json").write_text(
            json.dumps({"/wiki/Test": "Test passage text"})
        )

        loader = WikiTablesLoader(tmp_path)
        table = loader.load_table("test_table_0")
        assert table.table_id == "test_table_0"
        assert table.num_rows == 1
        assert table.num_cols == 2
        assert table.title == "Test Table"

    def test_load_passages(self, tmp_path: Path) -> None:
        """Load passages for a table."""
        tables_dir = tmp_path / "tables_tok"
        tables_dir.mkdir()
        request_dir = tmp_path / "request_tok"
        request_dir.mkdir()

        (tables_dir / "t0.json").write_text(
            json.dumps({"header": [], "data": [], "title": ""})
        )
        (request_dir / "t0.json").write_text(
            json.dumps({"/wiki/A": "Passage A", "/wiki/B": "Passage B"})
        )

        loader = WikiTablesLoader(tmp_path)
        passages = loader.load_passages("t0")
        assert len(passages) == 2
        assert passages["/wiki/A"] == "Passage A"

    def test_missing_wikitables_dir(self, tmp_path: Path) -> None:
        """Raise FileNotFoundError for missing WikiTables directory."""
        with pytest.raises(FileNotFoundError, match="WikiTables-WithLinks"):
            WikiTablesLoader(tmp_path / "nonexistent")

    def test_cache_info(self, tmp_path: Path) -> None:
        """Verify LRU cache is working."""
        tables_dir = tmp_path / "tables_tok"
        tables_dir.mkdir()
        request_dir = tmp_path / "request_tok"
        request_dir.mkdir()

        table_data = {"header": [], "data": [], "title": "T"}
        (tables_dir / "t0.json").write_text(json.dumps(table_data))
        (request_dir / "t0.json").write_text(json.dumps({}))

        loader = WikiTablesLoader(tmp_path)
        loader.load_table("t0")
        loader.load_table("t0")  # Should hit cache

        info = loader.cache_info()
        assert info["table_cache"].hits == 1  # type: ignore[union-attr]
