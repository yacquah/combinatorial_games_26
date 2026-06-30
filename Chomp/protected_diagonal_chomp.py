"""Generate sheets for three-row Chomp with protected diagonal moves.

Positions are represented by row lengths ``(x, y, z)`` with ``x >= y >= z >= 0``.
A move chooses an occupied square and removes every square weakly below and to
the right, as in Chomp.

The protected-diagonal restriction is:
    A player may not choose a square on the main diagonal unless no non-diagonal
    square is available.

The computation is a direct dynamic program over row-length positions. Sheets
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

    W = np.zeros((max_depth, grid_size, grid_size), dtype=np.bool_)
    L = np.zeros((max_depth, grid_size, grid_size), dtype=np.bool_)
    Lcum = np.zeros((max_depth, grid_size, grid_size), dtype=np.bool_)
    cumL = np.zeros((grid_size, grid_size), dtype=np.bool_)

    for x in range(max_depth):
        y_stop = x + 1
        if y_stop > grid_size:
            y_stop = grid_size

        for y in range(y_stop):
            for z in range(y + 1):
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

    non_diagonal_available = has_non_diagonal_square(x, y, z)

    # Bite row 1, column c:
    # (x, y, z) -> (c - 1, min(y, c - 1), min(z, c - 1))
    for c in range(1, x + 1):
        if non_diagonal_available and c == 1:
            continue
        if not non_diagonal_available and c != 1:
            continue

        nx = c - 1
        ny = y
        if ny > nx:
            ny = nx
        nz = z
        if nz > nx:
            nz = nx

        if L[nx, nz, ny]:
            return True

    # Bite row 2, column c:
    # (x, y, z) -> (x, c - 1, min(z, c - 1))
    for c in range(1, y + 1):
        if non_diagonal_available and c == 2:
            continue
        if not non_diagonal_available and c != 2:
            continue

        ny = c - 1
        nz = z
        if nz > ny:
            nz = ny

        if L[x, nz, ny]:
            return True

    # Bite row 3, column c:
    # (x, y, z) -> (x, y, c - 1)
    for c in range(1, z + 1):
        if non_diagonal_available and c == 3:
            continue
        if not non_diagonal_available and c != 3:
            continue

        nz = c - 1

        if L[x, nz, y]:
            return True

    return False


@njit
def has_non_diagonal_square(x, y, z):
    """Return True iff the position contains an occupied off-diagonal square."""

    # Row 1 has an off-diagonal square as soon as column 2 exists. Any occupied
    # square in row 2 or row 3 also forces an off-diagonal square to its left.
    return x >= 2 or y >= 1 or z >= 1


def main():
    """Prompt for one or more protected-diagonal Chomp sheets."""

    run_sheet_session(compute_sheets, row_is_z=True, triplet_default=lambda level: level + 1)


if __name__ == "__main__":
    main()
