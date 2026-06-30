"""Generate sheets for three-row Chomp with protected diagonal moves.

Positions use the column-height encoding from the original Chomp scripts:
``(x, y, z)`` means ``x`` columns of height 3, then ``y`` columns of height 2,
then ``z`` columns of height 1.

A move chooses a non-poison occupied square and removes every square weakly
above and to the right, as in Chomp with the poisoned square at the lower-left
corner. The poisoned square is row 1, column 1; choosing it loses immediately,
so it is not counted as a legal move to another normal-play position.

The protected-diagonal restriction is:
    A player may choose a non-poison square on the main diagonal only when that
    Chomp move removes exactly that diagonal square and no other square.

The computation is a direct dynamic program over column-count positions. Sheets
are indexed ``[x, z, y]`` so a fixed x-level displays z as rows and y as columns.
"""

import numpy as np
from numba import njit
from utils.display import run_sheet_session


def compute_sheets(max_depth, grid_size=None):
    """Compute W, L, and cumulative-L sheets.

    Args:
        max_depth: Number of x-levels to compute.
        grid_size: Number of cells to compute along the displayed y and z axes.
            Defaults to ``max_depth`` for compatibility with one-argument callers.

    Returns:
        W: 3D boolean array of winning positions.
        L: 3D boolean array of losing positions.
        Lcum: 3D boolean array where Lcum[x] is the OR of L_0..L_x.
    """

    if grid_size is None:
        grid_size = max_depth
    return _compute_sheets(max_depth, grid_size)


@njit
def _compute_sheets(max_depth, grid_size):
    """Numba-compiled implementation for ``compute_sheets``."""

    # A move from a displayed position can convert taller columns into many
    # height-1 or height-2 columns. This internal padding keeps those reachable
    # target positions inside the computed space.
    row_bound = max_depth + 2 * grid_size
    internal_grid = row_bound + 1

    W = np.zeros((max_depth, internal_grid, internal_grid), dtype=np.bool_)
    L = np.zeros((max_depth, internal_grid, internal_grid), dtype=np.bool_)
    Lcum = np.zeros((max_depth, internal_grid, internal_grid), dtype=np.bool_)
    cumL = np.zeros((internal_grid, internal_grid), dtype=np.bool_)

    for x in range(max_depth):
        for y in range(internal_grid):
            for z in range(internal_grid):
                if x + y + z > row_bound:
                    continue

                if has_move_to_loser(x, y, z, L):
                    W[x, z, y] = True
                else:
                    L[x, z, y] = True

        cumL = cumL | L[x]
        Lcum[x] = cumL

    return W, L, Lcum


@njit
def has_move_to_loser(x, y, z, L):
    """Return True iff ``(x, y, z)`` has a legal move to a known loser."""

    # Bite a height-3 square: columns c..x drop from height 3 to height 2.
    for c in range(1, x + 1):
        if not move_allowed(x, y, z, 3, c):
            continue

        nx = c - 1
        ny = y + x - c + 1
        nz = z

        if L[nx, nz, ny]:
            return True

    # Bite a height-2 square. If it is in a height-3 column, all affected
    # height-3 and height-2 columns become height 1. If it is in a height-2
    # column, the later height-2 columns become height 1.
    for c in range(1, x + y + 1):
        if not move_allowed(x, y, z, 2, c):
            continue

        if c <= x:
            nx = c - 1
            ny = 0
            nz = z + y + x - c + 1
        else:
            nx = x
            ny = c - x - 1
            nz = z + x + y - c + 1

        if L[nx, nz, ny]:
            return True

    # Bite a height-1 square. Column 1 is the poisoned square; choosing it is an
    # immediate loss, so it is never a winning move to another position.
    for c in range(2, x + y + z + 1):
        if not move_allowed(x, y, z, 1, c):
            continue

        if c <= x:
            nx = c - 1
            ny = 0
            nz = 0
        elif c <= x + y:
            nx = x
            ny = c - x - 1
            nz = 0
        else:
            nx = x
            ny = y
            nz = c - x - y - 1

        if L[nx, nz, ny]:
            return True

    return False


@njit
def move_allowed(x, y, z, row, column):
    """Return True iff the selected square is allowed by the diagonal rule."""

    if row != column:
        return True

    return chomp_removes_one_cell(x, y, z, row, column)


@njit
def chomp_removes_one_cell(x, y, z, row, column):
    """Return True iff biting ``(row, column)`` removes exactly one square."""

    removed = 0
    total = x + y + z
    for c in range(column, total + 1):
        height = column_height(x, y, c)
        if height >= row:
            removed += height - row + 1
            if removed > 1:
                return False

    return removed == 1


@njit
def column_height(x, y, column):
    """Return the height of ``column`` in old Chomp column-count encoding."""

    if column <= x:
        return 3
    if column <= x + y:
        return 2
    return 1


def main():
    """Prompt for one or more protected-diagonal Chomp sheets."""

    run_sheet_session(compute_sheets, row_is_z=True)


if __name__ == "__main__":
    main()
