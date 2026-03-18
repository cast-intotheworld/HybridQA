"""Tests for evaluation metrics (ported from evaluate_script.py)."""

from __future__ import annotations

import pytest

from serialization.src.evaluation.metrics import (
    compute_exact,
    compute_f1,
    get_raw_scores,
    get_tokens,
    normalize_answer,
)


class TestNormalizeAnswer:
    """Tests for normalize_answer function."""

    def test_lowercase(self) -> None:
        assert normalize_answer("Hello World") == "hello world"

    def test_remove_articles(self) -> None:
        assert normalize_answer("the quick brown fox") == "quick brown fox"
        assert normalize_answer("a cat and an apple") == "cat and apple"

    def test_remove_punctuation(self) -> None:
        assert normalize_answer("hello, world!") == "hello world"
        assert normalize_answer("score: 100%") == "score 100"

    def test_whitespace_fix(self) -> None:
        assert normalize_answer("  hello   world  ") == "hello world"

    def test_combined(self) -> None:
        assert normalize_answer("The Answer is: 42!") == "answer is 42"


class TestGetTokens:
    """Tests for get_tokens function."""

    def test_normal_text(self) -> None:
        assert get_tokens("Hello World") == ["hello", "world"]

    def test_empty_string(self) -> None:
        assert get_tokens("") == []


class TestComputeExact:
    """Tests for compute_exact function."""

    def test_exact_match(self) -> None:
        assert compute_exact("Paris", "Paris") == 1

    def test_case_insensitive(self) -> None:
        assert compute_exact("Paris", "paris") == 1

    def test_no_match(self) -> None:
        assert compute_exact("Paris", "London") == 0

    def test_article_normalization(self) -> None:
        assert compute_exact("the Eiffel Tower", "Eiffel Tower") == 1


class TestComputeF1:
    """Tests for compute_f1 function."""

    def test_perfect_match(self) -> None:
        assert compute_f1("Emmitt Smith", "Emmitt Smith") == 1.0

    def test_partial_match(self) -> None:
        f1 = compute_f1("Emmitt James Smith", "Emmitt Smith")
        assert 0 < f1 < 1

    def test_no_overlap(self) -> None:
        assert compute_f1("Paris", "London") == 0

    def test_empty_gold(self) -> None:
        assert compute_f1("", "") == 1

    def test_empty_pred(self) -> None:
        assert compute_f1("Paris", "") == 0


class TestGetRawScores:
    """Tests for get_raw_scores function."""

    def test_basic_evaluation(self) -> None:
        """Compute scores for a small example."""
        examples = [
            {"question_id": "q1", "pred": "Paris"},
            {"question_id": "q2", "pred": "Wrong"},
        ]
        reference = {
            "reference": {"q1": "Paris", "q2": "London"},
            "table": ["q1"],
            "passage": ["q2"],
        }
        scores = get_raw_scores(examples, reference)
        assert scores["table exact"] == 100.0
        assert scores["table f1"] == 100.0
        assert scores["passage exact"] == 0.0
        assert scores["total exact"] == 50.0
        assert scores["total"] == 2

    def test_all_correct(self) -> None:
        """All predictions correct yields 100% on all metrics."""
        examples = [
            {"question_id": "q1", "pred": "Paris"},
            {"question_id": "q2", "pred": "London"},
        ]
        reference = {
            "reference": {"q1": "Paris", "q2": "London"},
            "table": ["q1"],
            "passage": ["q2"],
        }
        scores = get_raw_scores(examples, reference)
        assert scores["total exact"] == 100.0
        assert scores["total f1"] == 100.0
