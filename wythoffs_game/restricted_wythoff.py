"""
Generates and displays Instant-Winner and Loser sheets for Restricted 3-heap Wythoff.

On top of Nim rules (remove any number of chips from one pile), a player may remove the same
number of chips ``t`` from two piles, but only if ``t`` does not exceed the size of the third,
untouched pile:

    Single pile:   (x,y,z) -> (x-t, y,   z),   (x, y-t, z),   (x, y, z-t)
    Two piles:     (x,y,z) -> (x-t, y-t, z) with t <= z
                   (x,y,z) -> (x-t, y,   z-t) with t <= y
                   (x,y,z) -> (x,   y-t, z-t) with t <= x

Because the two-pile bound couples all three heaps, the usual shift-accumulator recurrence does not
apply, so we compute the sheets directly. The two x-reducing moves slide along a diagonal (both
``(x-t, y-t, z)`` and ``(x-t, y, z-t)`` keep one coordinate fixed while two drop together), bounded
by the untouched pile. Rather than scanning that whole diagonal per cell -- which made the original
O(N^4) -- we track the most-recent loser on each diagonal and test "is it within the bound?" in
O(1), giving O(N^3) and needing no full 3D loser history.

Returns only ``(W, L)``; the cumulative-loser (C) sheets are derived from L on demand by the display
layer, so no third cube is materialized.
"""

import numpy as np
from numba import njit
from utils.display import run_sheet_session


@njit
def compute_sheets(depth, size):
    """Compute the W and L sheets for Restricted 3-heap Wythoff.

    Covers x-levels ``0..depth-1`` over a ``size x size`` (z, y) grid. Sheets are indexed
    ``[x, z, y]`` so that a fixed x yields a 2D grid with z as the row and y as the column, matching
    the rest of the codebase. Depth and grid size are decoupled, so a low-level request on a big grid
    only allocates the levels it needs.

    Args:
        depth: Number of x-levels to compute (cube depth).
        size: Number of cells along each of the y and z axes (grid size).

    Returns:
        W: 3D boolean array of Instant-Winner positions, shape ``(depth, size, size)``.
        L: 3D boolean array of Loser (P-)positions, shape ``(depth, size, size)``.
    """

    L = np.zeros((depth, size, size), dtype=np.bool_)
    W = np.zeros((depth, size, size), dtype=np.bool_)

    # Running OR of every L-sheet strictly below the current level. Handles the unrestricted
    # single-pile move (x-t, y, z): any lower x-level loser at the same (y, z) makes us a winner.
    cumL = np.zeros((size, size), dtype=np.bool_)

    # Most-recent sheet x' that holds a loser on each diagonal (-1 = none yet):
    #   last_xy[(x-y)+size, z] -- for the (x-t, y-t, z) move (x and y drop together; row z fixed)
    #   last_xz[(x-z)+size, y] -- for the (x-t, y, z-t) move (x and z drop together; col y fixed)
    # The diagonal index encodes x-y (resp. x-z); offset by ``size`` keeps it non-negative (x-y can
    # be as low as -(size-1)) and at most depth+size-1, so depth+size rows suffice. The loser's own
    # row/col indexes the second axis.
    last_xy = np.full((depth + size, size), -1, dtype=np.int64)
    last_xz = np.full((depth + size, size), -1, dtype=np.int64)

    for x in range(depth):
        Wx = W[x]

        # -----------------------------------------------------------------
        # STEP 1: Look-back for the x-reducing moves (build W_x)
        # -----------------------------------------------------------------
        for z in range(size):
            for y in range(size):
                # Single-pile move on x: any lower L at the same (y, z).
                if cumL[z, y]:
                    Wx[z, y] = True
                    continue

                # (x-t, y-t, z), bounded by the untouched pile z (t <= z), i.e. the loser must sit
                # within z steps back on this (x,y)-diagonal: x' = x - t >= x - z. The other bounds
                # (t <= x, t <= y) hold automatically -- a stored loser has x' >= 0 and y' >= 0.
                lxy = last_xy[(x - y) + size, z]
                if lxy >= 0 and lxy >= x - z:
                    Wx[z, y] = True
                    continue

                # (x-t, y, z-t), bounded by the untouched pile y (t <= y): x' >= x - y.
                lxz = last_xz[(x - z) + size, y]
                if lxz >= 0 and lxz >= x - y:
                    Wx[z, y] = True

        # -----------------------------------------------------------------
        # STEP 2: Supermex for the moves that keep x fixed (build L_x)
        # -----------------------------------------------------------------
        L[x] = supermex(Wx, x)

        # Fold sheet x's losers into the rolling structures for the higher x-levels.
        for z in range(size):
            for y in range(size):
                if L[x, z, y]:
                    cumL[z, y] = True
                    last_xy[(x - y) + size, z] = x
                    last_xz[(x - z) + size, y] = x

    return W, L


@njit
def supermex(Wx, x):
    """Compute the loser sheet M(W_x) for a fixed x-level.

    Resolves every move that keeps x constant:
        - reduce z alone  -> column mex (first free z in each y-column)
        - reduce y alone  -> blocked rows (unrestricted)
        - reduce y and z by the same t <= x -> blocked diagonal, but only for the next x cells,
          since the third (untouched) pile here is x.

    Args:
        Wx: Boolean instant-winner sheet for this x-level.
        x: The current x-level, i.e. the bound on the two-pile (y, z) move.

    Returns:
        A boolean sheet of the newly selected loser positions (L_x).
    """

    grid_size = Wx.shape[0]
    MWx = np.zeros((grid_size, grid_size), dtype=np.bool_)

    blocked_rows = np.zeros(grid_size, dtype=np.bool_)
    # The diagonal move is range-limited (t <= x), so a single boolean per diagonal will not do;
    # we mark the specific cells made into winners by each loser.
    diag_blocked = np.zeros((grid_size, grid_size), dtype=np.bool_)

    for y in range(grid_size):  # Each column; implicitly handles the y-reduction move
        next_available_z = -1
        for z in range(grid_size):
            if not Wx[z, y] and not blocked_rows[z] and not diag_blocked[z, y]:
                next_available_z = z
                break

        if next_available_z == -1:  # No free z in this column
            continue

        MWx[next_available_z, y] = True
        blocked_rows[next_available_z] = True

        # Cast out the implied winners along the diagonal: positions (z+t, y+t) can reach this
        # loser by removing t from both y and z, but only for t <= x.
        for t in range(1, x + 1):
            zz = next_available_z + t
            yy = y + t
            if zz < grid_size and yy < grid_size:
                diag_blocked[zz, yy] = True
            else:
                break

    return MWx


def main():
    """Prompt for one or more Restricted Wythoff sheets and display them together."""
    # Sheets are indexed [x, z, y], so the (row, col) axes are (z, y): row_is_z=True.
    run_sheet_session(compute_sheets, row_is_z=True)


if __name__ == "__main__":
    main()
