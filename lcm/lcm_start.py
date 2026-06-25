"""Generate and display instant-winner (W) and loser (L) sheets for 3-heap LCM.

3-heap LCM game: a move picks two piles, computes their LCM L, then subtracts
any integer in [1, L] from the third pile.

Sheet framework (Friedman & Landsberg), x = level, [y, z] = sheet coords:
  - Inter-sheet:  subtract k ∈ [1, lcm(y,z)] from x  →  lower sheet x-k.
  - Intra-sheet:  subtract k ∈ [1, lcm(x,z)] from y,
                  subtract k ∈ [1, lcm(x,y)] from z.

W_0 is blank (x=0 has no lower sheet). Supermex derives L_x from W_x.

O(N^3) algorithm — "most-recent loser" trick:
  LCM moves cover a consecutive range [p+1, p+lcm], so a cell at position p is
  blocked iff the nearest loser before it is within lcm distance. Tracking just
  the most-recent loser index per row/column gives an O(1) blocked check,
  eliminating the inner k-loop that would make this O(N^4) or worse.
"""

import numpy as np
from numba import njit
from utils.display import output


@njit
def _build_lcm_table(max_size):
    """Precompute lcm(i, j) for i, j < max_size, capped at max_size.

    lcm(0, k) = 0 (encoded as no-move). Values exceeding max_size are capped
    because a window larger than the grid is equivalent to 'any prior level'.
    """
    table = np.zeros((max_size, max_size), dtype=np.int64)
    for i in range(1, max_size):
        for j in range(1, max_size):
            a, b = i, j
            while b:
                a, b = b, a % b
            g = a
            v = (i // g) * j  # divide first to delay overflow
            table[i, j] = v if v < max_size else max_size
    return table


@njit
def compute_lcm_space(max_size):
    """Compute W and L sheets for all levels 0..max_size-1.

    Returns (W_history, L_history) both indexed [level, z, y].
    """
    L_history = np.zeros((max_size, max_size, max_size), dtype=np.bool_)
    W_history = np.zeros((max_size, max_size, max_size), dtype=np.bool_)
    lcm = _build_lcm_table(max_size)

    # Most-recent loser x-level for each (z, y) position; -1 = none yet.
    last_x = np.full((max_size, max_size), -1, dtype=np.int64)

    for x in range(max_size):

        # ── W_x: inter-sheet instant winners ─────────────────────────────────
        # W_x[z,y] = True iff the nearest lower loser at this (z,y) column
        # is within lcm(y,z) steps of x.
        if x > 0:
            for z in range(max_size):
                for y in range(max_size):
                    w = lcm[y, z]
                    if w > 0 and last_x[z, y] >= 0 and x - last_x[z, y] <= w:
                        W_history[x, z, y] = True

        # ── L_x: supermex via intra-sheet moves ───────────────────────────────
        # Scan y (outer) then z (inner). For each row z track the most-recent
        # loser y-index; for each column y track the most-recent loser z-index.
        last_y = np.full(max_size, -1, dtype=np.int64)  # indexed by z (row)
        last_z = np.full(max_size, -1, dtype=np.int64)  # indexed by y (col)

        for y in range(max_size):
            for z in range(max_size):

                # y-ray: (z, y0) loser blocks (z, y) if y - y0 ≤ lcm(x, z)
                w_y = lcm[x, z]
                blocked_y = (w_y > 0 and last_y[z] >= 0
                             and y - last_y[z] <= w_y)

                # z-ray: (z0, y) loser blocks (z, y) if z - z0 ≤ lcm(x, y)
                w_z = lcm[x, y]
                blocked_z = (w_z > 0 and last_z[y] >= 0
                             and z - last_z[y] <= w_z)

                if not W_history[x, z, y] and not blocked_y and not blocked_z:
                    L_history[x, z, y] = True
                    last_y[z] = y          # update row tracker
                    last_z[y] = z          # update column tracker
                    last_x[z, y] = x       # update level tracker for future W

    return W_history, L_history


def main():
    """Prompt for an LCM-game sheet request, compute it, and display it."""

    grid_size = int(input("Size of the grid you want to see (y and z axes):\n"))
    is_winner = input("Winner or loser? (W/L)\n").strip().upper() == 'W'
    desired_level = int(input("x-level?\n"))

    compute_size = max(grid_size, desired_level + 1)

    W_space, L_space = compute_lcm_space(compute_size)

    if is_winner:
        sheet = W_space[desired_level, :grid_size, :grid_size]
        output(sheet, True, desired_level)
    else:
        sheet = L_space[desired_level, :grid_size, :grid_size]
        output(sheet, False, desired_level)


if __name__ == "__main__":
    main()
