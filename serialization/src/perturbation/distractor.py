"""Distractor insertion perturbations for Stage 3."""

from __future__ import annotations

import copy
import random

from serialization.src.data_loader.schema import Table


def insert_distractor_rows(
    table: Table,
    num_distractors: int = 3,
    seed: int = 42,
) -> Table:
    """Insert random distractor rows into the table.

    Generates rows by randomly shuffling cell values from existing rows.

    :param table: Original table.
    :param num_distractors: Number of distractor rows to insert.
    :param seed: Random seed for reproducibility.
    :return: New table with distractor rows inserted.
    """
    if not table.data:
        return copy.deepcopy(table)

    new_table = copy.deepcopy(table)
    rng = random.Random(seed)
    num_cols = len(table.header)

    for _ in range(num_distractors):
        distractor_row = []
        for col_idx in range(num_cols):
            # Pick a random cell from this column
            source_row = rng.choice(table.data)
            if col_idx < len(source_row):
                distractor_row.append(source_row[col_idx])
            else:
                distractor_row.append(("", []))

        # Insert at random position
        insert_pos = rng.randint(0, len(new_table.data))
        new_table.data.insert(insert_pos, distractor_row)

    return new_table


def insert_distractor_passages(
    passages: dict[str, str],
    distractor_passages: dict[str, str],
    num_distractors: int = 3,
    seed: int = 42,
) -> dict[str, str]:
    """Add distractor passages to the passage map.

    :param passages: Original passage map.
    :param distractor_passages: Pool of distractor passages to sample from.
    :param num_distractors: Number of distractors to add.
    :param seed: Random seed.
    :return: New passage map with distractors added.
    """
    result = dict(passages)
    rng = random.Random(seed)

    available = [
        (url, text)
        for url, text in distractor_passages.items()
        if url not in passages
    ]

    if available:
        selected = rng.sample(available, min(num_distractors, len(available)))
        for url, text in selected:
            result[url] = text

    return result
