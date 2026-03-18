"""Separator and field name perturbations for Stage 3."""

from __future__ import annotations


def swap_separators(text: str, original: str = " | ", replacement: str = " ; ") -> str:
    """Replace cell separators in serialized text.

    :param text: Serialized text.
    :param original: Original separator.
    :param replacement: New separator.
    :return: Text with swapped separators.
    """
    return text.replace(original, replacement)


def rename_field_labels(
    text: str,
    mapping: dict[str, str] | None = None,
) -> str:
    """Replace field labels (column names) in serialized text.

    :param text: Serialized text.
    :param mapping: Dict of original_label -> new_label. If None, uses generic labels.
    :return: Text with renamed field labels.
    """
    if mapping is None:
        return text
    for original, replacement in mapping.items():
        text = text.replace(original, replacement)
    return text


def strip_field_labels(text: str, labels: list[str]) -> str:
    """Remove field labels, keeping only values.

    :param text: Serialized text.
    :param labels: List of field labels to strip (e.g., column names).
    :return: Text with field labels removed.
    """
    for label in labels:
        text = text.replace(f"{label}: ", "")
    return text
