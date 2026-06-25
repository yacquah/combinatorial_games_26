"""Generate and display finite instant-winner and loser sheets for Nim.

This script computes two-dimensional slices of three-heap Nim using the
``supermex`` operator. The x-coordinate is treated as the sheet level, while the
rendered grid coordinates are y and z.
"""

import numpy as np
from numba import njit
from utils.display import output
# import time

@njit(cache=True)
def generate_Wx(Wx, desired_level):
    """Iteratively build the instant-winner sheet W_x up to ``desired_level``.

    Args:
        Wx: Boolean grid representing the current instant-winner sheet.
        desired_level: Target x-level to compute.

    Returns:
        The updated boolean grid for W_desired_level.
    """
    if desired_level == 0:
        return Wx

    for _ in range(1, desired_level+1):
        # Recurrence for Nim: the next instant-winner sheet adds M(Wx).
        Wx |= supermex(Wx)
    return Wx

@njit(cache=True)
def _find(next_free, r):
    """Union-find lookup: smallest row index >= r not yet claimed this pass.

    ``next_free`` is a disjoint-set forest over rows; a claimed row points one
    step past itself. Path compression keeps repeated lookups near O(1), so a
    column never re-scans a run of already-claimed rows.
    """
    while next_free[r] != r:
        next_free[r] = next_free[next_free[r]]
        r = next_free[r]
    return r

@njit(cache=True)
def supermex(Wx):
    """Compute the supermex sheet M(Wx).

    For each y-column, this selects the first cell that is not already an instant
    winner and whose row has not been blocked by an earlier selection -- the same
    greedy rule as the original, but rows claimed by earlier columns are skipped
    in ~O(1) via a union-find "next free row" structure instead of being
    re-scanned cell by cell.

    Args:
        Wx: Boolean instant-winner sheet.

    Returns:
        A boolean sheet containing the newly selected loser positions.
    """

    grid_size = Wx.shape[0]
    # MWx stores only the new positions selected by this supermex step.
    MWx = np.zeros((grid_size, grid_size), dtype=np.bool_)

    # next_free[r] points to the smallest unclaimed row >= r (r itself if free).
    # The sentinel slot at grid_size lets _find run off the end harmlessly.
    next_free = np.empty(grid_size + 1, dtype=np.int64)
    for r in range(grid_size + 1):
        next_free[r] = r

    for y in range(grid_size):
        # Smallest row that is unclaimed (via union-find) AND free in this column.
        z = _find(next_free, 0)
        while z < grid_size and Wx[z, y]:
            z = _find(next_free, z + 1)

        if z == grid_size:
            continue

        MWx[z, y] = True
        # Claim row z: future _find calls skip straight past it.
        next_free[z] = z + 1

    return MWx


def main():
    """Prompt for a Nim sheet request, compute it, and display the result."""

    grid_size = int(input("Size of the grid you want to see:\n"))
    is_winner = input("Winner or loser? (W/L)\n") == 'W'
    desired_level = int(input("x-level?\n"))

    # For Nim, W_0 starts empty and L_x can be recovered as M(W_x).
    Wx = np.zeros((grid_size, grid_size), dtype=np.bool_)

    # generate_Wx(Wx, desired_level)   # Warm up benchmark
    # start = time.perf_counter()      # Benchmark time start

    Wx = generate_Wx(Wx, desired_level)

    # end = time.perf_counter()        # Benchmark time stop
    # print(f"Execution time: {end - start:.6f} seconds")

    if is_winner:
        # print(Wx.astype(int))
        output(Wx, True, desired_level)
    else:
        Lx = supermex(Wx)
        # print(Lx.astype(int))
        output(Lx, False, desired_level)


if __name__ == "__main__":
    main()
