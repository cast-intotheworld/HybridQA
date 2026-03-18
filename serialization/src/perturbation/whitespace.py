"""Whitespace and indentation perturbations for Stage 3."""

from __future__ import annotations

import re


def add_extra_whitespace(text: str, factor: int = 2) -> str:
    """Multiply whitespace between tokens.

    :param text: Input text.
    :param factor: Multiplication factor for spaces.
    :return: Text with expanded whitespace.
    """
    return re.sub(r" ", " " * factor, text)


def add_indentation(text: str, indent: str = "  ") -> str:
    """Add indentation to each line.

    :param text: Input text.
    :param indent: Indentation string to prepend.
    :return: Indented text.
    """
    lines = text.split("\n")
    return "\n".join(indent + line for line in lines)


def normalize_whitespace(text: str) -> str:
    """Collapse all whitespace to single spaces and strip lines.

    :param text: Input text.
    :return: Whitespace-normalized text.
    """
    lines = text.split("\n")
    normalized = [" ".join(line.split()) for line in lines]
    return "\n".join(line for line in normalized if line)


def remove_blank_lines(text: str) -> str:
    """Remove all blank lines from text.

    :param text: Input text.
    :return: Text without blank lines.
    """
    lines = text.split("\n")
    return "\n".join(line for line in lines if line.strip())
