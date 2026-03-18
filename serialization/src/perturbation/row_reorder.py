"""Row and column reordering perturbations for Stage 3."""

from __future__ import annotations

import copy
import random

from serialization.src.data_loader.schema import Table


def shuffle_rows(table: Table, seed: int = 42) -> Table:
    """Shuffle data rows of a table randomly.

    :param table: Original table.
    :param seed: Random seed for reproducibility.
    :return: New table with shuffled rows.
    """
    new_table = copy.deepcopy(table)
    rng = random.Random(seed)
    rng.shuffle(new_table.data)
    return new_table


def reverse_rows(table: Table) -> Table:
    """Reverse the order of data rows.

    :param table: Original table.
    :return: New table with reversed rows.
    """
    new_table = copy.deepcopy(table)
    new_table.data = list(reversed(new_table.data))
    return new_table


def shuffle_columns(table: Table, seed: int = 42) -> Table:
    """Shuffle columns of a table randomly.

    Reorders both header and data columns consistently.

    :param table: Original table.
    :param seed: Random seed for reproducibility.
    :return: New table with shuffled columns.
    """
    new_table = copy.deepcopy(table)
    num_cols = len(new_table.header)

    rng = random.Random(seed)
    col_indices = list(range(num_cols))
    rng.shuffle(col_indices)

    new_table.header = [new_table.header[i] for i in col_indices]
    new_table.data = [
        [row[i] for i in col_indices if i < len(row)] for row in new_table.data
    ]
    return new_table
