"""EM and F1 metrics ported from evaluate_script.py.

The normalization and scoring logic is identical to the original HybridQA
evaluation script to ensure consistent comparison with published results.
"""

from __future__ import annotations

import collections
import re
import string


def normalize_answer(s: str) -> str:
    """Lower text and remove punctuation, articles and extra whitespace.

    :param s: Raw answer string.
    :return: Normalized answer string.
    """

    def remove_articles(text: str) -> str:
        regex = re.compile(r"\b(a|an|the)\b", re.UNICODE)
        return re.sub(regex, " ", text)

    def white_space_fix(text: str) -> str:
        return " ".join(text.split())

    def remove_punc(text: str) -> str:
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text: str) -> str:
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def get_tokens(s: str) -> list[str]:
    """Tokenize a normalized answer string.

    :param s: Answer string.
    :return: List of tokens.
    """
    if not s:
        return []
    return normalize_answer(s).split()


def compute_exact(a_gold: str, a_pred: str) -> int:
    """Compute exact match between gold and predicted answer.

    :param a_gold: Gold answer string.
    :param a_pred: Predicted answer string.
    :return: 1 if exact match, 0 otherwise.
    """
    return int(normalize_answer(a_gold) == normalize_answer(a_pred))


def compute_f1(a_gold: str, a_pred: str) -> float:
    """Compute token-level F1 score between gold and predicted answer.

    :param a_gold: Gold answer string.
    :param a_pred: Predicted answer string.
    :return: F1 score between 0 and 1.
    """
    gold_toks = get_tokens(a_gold)
    pred_toks = get_tokens(a_pred)
    common = collections.Counter(gold_toks) & collections.Counter(pred_toks)
    num_same = sum(common.values())
    if len(gold_toks) == 0 or len(pred_toks) == 0:
        # If either is no-answer, then F1 is 1 if they agree, 0 otherwise
        return int(gold_toks == pred_toks)
    if num_same == 0:
        return 0
    precision = 1.0 * num_same / len(pred_toks)
    recall = 1.0 * num_same / len(gold_toks)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


def get_raw_scores(
    examples: list[dict], reference: dict
) -> collections.OrderedDict:
    """Compute EM and F1 scores broken down by answer source.

    :param examples: List of dicts with 'question_id' and 'pred' keys.
    :param reference: Reference dict with 'reference', 'table', 'passage' keys.
    :return: OrderedDict with table/passage/total EM and F1 scores.
    """
    exact_scores: dict[str, int] = {}
    f1_scores: dict[str, float] = {}

    for example in examples:
        qas_id = example["question_id"]
        gold_answers = [reference["reference"][qas_id]]

        prediction = example["pred"]
        exact_scores[qas_id] = max(compute_exact(a, prediction) for a in gold_answers)
        f1_scores[qas_id] = max(compute_f1(a, prediction) for a in gold_answers)

    qid_list = reference["reference"].keys()
    total = len(qid_list)

    table_list = reference["table"]
    passage_list = reference["passage"]

    return collections.OrderedDict(
        [
            ("table exact", 100.0 * sum(exact_scores[k] for k in table_list) / len(table_list)),
            ("table f1", 100.0 * sum(f1_scores[k] for k in table_list) / len(table_list)),
            (
                "passage exact",
                100.0 * sum(exact_scores[k] for k in passage_list) / len(passage_list),
            ),
            ("passage f1", 100.0 * sum(f1_scores[k] for k in passage_list) / len(passage_list)),
            ("total exact", 100.0 * sum(exact_scores[k] for k in qid_list) / total),
            ("total f1", 100.0 * sum(f1_scores[k] for k in qid_list) / total),
            ("total", total),
        ]
    )
