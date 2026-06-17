"""Generate and display finite instant-winner and loser sheets for Nim.

This script computes two-dimensional slices of three-heap Nim using the
``supermex`` operator. The x-coordinate is treated as the sheet level, while the
rendered grid coordinates are y and z.
"""

import numpy as np
from numba import njit
from utils.display import output
# import time

@njit
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

@njit
def supermex(Wx):
    """Compute the supermex sheet M(Wx).

    For each y-column, this scans upward in z and selects the first cell that is
    not already an instant winner and whose row has not been blocked by an
    earlier selection.

    Args:
        Wx: Boolean instant-winner sheet.

    Returns:
        A boolean sheet containing the newly selected loser positions.
    """

    grid_size = Wx.shape[0]
    # MWx stores only the new positions selected by this supermex step.
    MWx = np.zeros((grid_size, grid_size), dtype=np.bool_)

    # Once supermex selects a z-row, later columns cannot select that row again.
    blocked_rows = np.zeros(grid_size, dtype=np.bool_)

    for y in range(grid_size):
        next_available_z = -1

        # Scan upward in this y-column and take the first unblocked loser spot.
        for z in range(grid_size):
            if not Wx[z, y] and not blocked_rows[z]:
                next_available_z = z
                break

        if next_available_z == -1:
            continue

        MWx[next_available_z, y] = True

        # Mark the selected row as unavailable for the remaining columns.
        blocked_rows[next_available_z] = True

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
