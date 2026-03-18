"""Token counting using tiktoken for serialized text."""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    import tiktoken

    _TIKTOKEN_AVAILABLE = True
except ImportError:
    _TIKTOKEN_AVAILABLE = False
    logger.warning("tiktoken not installed. Token counting will use whitespace splitting.")


@dataclass
class TokenStats:
    """Token count statistics for a set of serialized texts.

    :param total_tokens: Total number of tokens across all texts.
    :param mean_tokens: Mean tokens per text.
    :param min_tokens: Minimum tokens in a single text.
    :param max_tokens: Maximum tokens in a single text.
    :param count: Number of texts counted.
    """

    total_tokens: int
    mean_tokens: float
    min_tokens: int
    max_tokens: int
    count: int


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count the number of tokens in a text string.

    :param text: Input text.
    :param model: Model name for tokenizer selection.
    :return: Number of tokens.
    """
    if _TIKTOKEN_AVAILABLE:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    else:
        return len(text.split())


def compute_token_stats(texts: list[str], model: str = "gpt-4o") -> TokenStats:
    """Compute token statistics for a list of texts.

    :param texts: List of serialized text strings.
    :param model: Model name for tokenizer selection.
    :return: TokenStats with aggregate statistics.
    """
    if not texts:
        return TokenStats(total_tokens=0, mean_tokens=0.0, min_tokens=0, max_tokens=0, count=0)

    counts = [count_tokens(t, model) for t in texts]
    return TokenStats(
        total_tokens=sum(counts),
        mean_tokens=sum(counts) / len(counts),
        min_tokens=min(counts),
        max_tokens=max(counts),
        count=len(counts),
    )
