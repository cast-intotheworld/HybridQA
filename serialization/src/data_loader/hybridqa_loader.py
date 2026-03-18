"""Loader for HybridQA released data JSON files."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from serialization.src.data_loader.schema import AnswerNode, Question

logger = logging.getLogger(__name__)


def load_questions(data_path: str | Path, split: str, traced: bool = True) -> list[Question]:
    """Load HybridQA questions from a JSON file.

    :param data_path: Path to the released_data directory.
    :param split: Data split name ("train", "dev", or "test").
    :param traced: Whether to load traced version with answer-node annotations.
    :return: List of Question dataclasses.
    """
    data_path = Path(data_path)

    if traced and split != "test":
        filename = f"{split}.traced.json"
    else:
        filename = f"{split}.json"

    filepath = data_path / filename
    if not filepath.exists():
        raise FileNotFoundError(f"HybridQA data file not found: {filepath}")

    logger.info("Loading %s from %s", split, filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    questions = []
    for item in raw_data:
        answer_nodes = []
        if "answer-node" in item:
            for node in item["answer-node"]:
                answer_nodes.append(
                    AnswerNode(
                        text=node[0],
                        position=tuple(node[1]),
                        wiki_link=node[2] if node[2] else None,
                        source=node[3] if len(node) > 3 else "table",
                    )
                )

        questions.append(
            Question(
                question_id=item["question_id"],
                question=item["question"],
                table_id=item["table_id"],
                answer_text=item.get("answer-text"),
                answer_nodes=answer_nodes,
            )
        )

    logger.info("Loaded %d questions for %s split", len(questions), split)
    return questions


def load_reference(data_path: str | Path, split: str = "dev") -> dict:
    """Load reference answers for evaluation.

    :param data_path: Path to the released_data directory.
    :param split: Data split name (default: "dev").
    :return: Reference dict with 'reference', 'table', and 'passage' keys.
    """
    data_path = Path(data_path)
    filepath = data_path / f"{split}_reference.json"

    if not filepath.exists():
        raise FileNotFoundError(f"Reference file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_unique_table_ids(questions: list[Question]) -> list[str]:
    """Extract unique table IDs from a list of questions.

    :param questions: List of Question dataclasses.
    :return: Sorted list of unique table IDs.
    """
    return sorted({q.table_id for q in questions})


def group_by_table(questions: list[Question]) -> dict[str, list[Question]]:
    """Group questions by their table_id.

    :param questions: List of Question dataclasses.
    :return: Dict mapping table_id to list of questions.
    """
    groups: dict[str, list[Question]] = {}
    for q in questions:
        groups.setdefault(q.table_id, []).append(q)
    return groups
