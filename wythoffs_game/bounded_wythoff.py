"""
Generates and displays Instant-Winner and Loser sheets for 3-Heap Bounded Wythoff.

Normal 3-heap Nim (remove any number of chips from a single pile), plus a two-pile move: remove
``a`` chips from one pile and ``b`` from another (any of the three pairs), as long as the amounts
stay within a 1:2 .. 2:1 ratio -- that is, ``a <= 2b`` and ``b <= 2a`` (both >= 1). For example,
taking 4 from a pile lets you take 2..8 from another (or 0, which is just the single-pile Nim move).

Moves, with x as the sheet level:

    Inter-sheet (lower x):  (x-t, y,   z)                      single pile X
                            (x-a, y-b, z)   ratio(a,b)         two-pile X,Y
                            (x-a, y,   z-b) ratio(a,b)         two-pile X,Z
    Intra-sheet (fix x):    (x,   y-t, z)                      single pile Y
                            (x,   y,   z-t)                    single pile Z
                            (x,   y-a, z-b) ratio(a,b)         two-pile Y,Z

The bounded-ratio two-pile move spans a 2D wedge of valid offsets, but that wedge has a tiny
generating set, which is what makes this O(N^3). The offsets form the cone with extreme rays (2,1)
and (1,2); its determinant is 3 (non-unimodular), so those two rays alone do not hit every integer
point -- the interior vector (1,1) fills the gap. Hence the Hilbert basis of the cone is exactly

    {(1,1), (1,2), (2,1)},

and every valid offset is a non-negative integer combination of these three. So instead of scanning
the whole wedge behind each cell, we push each loser's "shadow" forward one basis step at a time with
a 2D boolean accumulator: a cell is threatened iff a loser (or an already-threatened cell) sits one
basis vector behind it. That makes each wedge test O(1).

Because the basis vectors only reach back x-1 and x-2 along the level axis, the inter-sheet
accumulators need just the two previous levels in memory (no 3D prefix arrays).

W_x (instant winners) records the moves that lower x; L_x the losers. Sheets are indexed [x, y, z]
(row y, column z); the game is symmetric in all three piles, so the orientation is immaterial.
"""

import numpy as np
from numba import njit
from utils.display import run_sheet_session


@njit(cache=True)
def compute_sheets(depth, size):
    """Compute the W and L sheets over x-levels ``0..depth-1`` on a ``size x size`` (y, z) grid.

    Returns only ``(W, L)`` -- two ``(depth, size, size)`` boolean cubes -- to keep memory down at
    large sizes (each cube is depth*size^2 bytes). Depth and grid size are decoupled, so requesting a
    low x-level on a big grid no longer allocates a full size^3 cube. The cumulative-loser (C) sheets
    are derived from L on demand by the display layer (OR of L_0..L_level), so no third cube is
    stored.

    Returns:
        W: instant-winner positions (some move lowers x onto a loser).
        L: Loser (P-)positions.
    """

    L = np.zeros((depth, size, size), dtype=np.bool_)
    W = np.zeros((depth, size, size), dtype=np.bool_)

    cumX = np.zeros((size, size), dtype=np.bool_)  # any loser at (y, z) on a strictly lower x-level

    # Wedge "shadow" accumulators for the two inter-sheet moves. A_xy_p1 / A_xy_p2 hold the
    # accumulator from the previous one / two x-levels (the only history the basis steps reach).
    A_xy_p1 = np.zeros((size, size), dtype=np.bool_)
    A_xy_p2 = np.zeros((size, size), dtype=np.bool_)
    A_xz_p1 = np.zeros((size, size), dtype=np.bool_)
    A_xz_p2 = np.zeros((size, size), dtype=np.bool_)

    for x in range(depth):
        colseen = np.zeros(size, dtype=np.bool_)        # any loser in column z at rows < y, this sheet
        A_xy_cur = np.zeros((size, size), dtype=np.bool_)  # this level's X,Y shadow (for next levels)
        A_xz_cur = np.zeros((size, size), dtype=np.bool_)  # this level's X,Z shadow
        A_yz = np.zeros((size, size), dtype=np.bool_)      # intra-sheet Y,Z shadow (this sheet only)

        for y in range(size):
            row_has = False                          # any loser in this row at a column < z

            for z in range(size):
                # ---------- two-pile wedge shadows via the three basis vectors ----------
                # X,Y move (offset in the x,y plane; z fixed): bases (1,1), (1,2), (2,1).
                xy = False
                if x >= 1 and y >= 1 and (L[x - 1, y - 1, z] or A_xy_p1[y - 1, z]):
                    xy = True
                elif x >= 1 and y >= 2 and (L[x - 1, y - 2, z] or A_xy_p1[y - 2, z]):
                    xy = True
                elif x >= 2 and y >= 1 and (L[x - 2, y - 1, z] or A_xy_p2[y - 1, z]):
                    xy = True
                A_xy_cur[y, z] = xy

                # X,Z move (offset in the x,z plane; y fixed).
                xz = False
                if x >= 1 and z >= 1 and (L[x - 1, y, z - 1] or A_xz_p1[y, z - 1]):
                    xz = True
                elif x >= 1 and z >= 2 and (L[x - 1, y, z - 2] or A_xz_p1[y, z - 2]):
                    xz = True
                elif x >= 2 and z >= 1 and (L[x - 2, y, z - 1] or A_xz_p2[y, z - 1]):
                    xz = True
                A_xz_cur[y, z] = xz

                # Y,Z move (offset in the y,z plane; x fixed -> current sheet).
                yz = False
                if y >= 1 and z >= 1 and (L[x, y - 1, z - 1] or A_yz[y - 1, z - 1]):
                    yz = True
                elif y >= 1 and z >= 2 and (L[x, y - 1, z - 2] or A_yz[y - 1, z - 2]):
                    yz = True
                elif y >= 2 and z >= 1 and (L[x, y - 2, z - 1] or A_yz[y - 2, z - 1]):
                    yz = True
                A_yz[y, z] = yz

                # ---------- decide winner / loser ----------
                # Inter-sheet moves (lower x) define the instant-winner sheet.
                inst = cumX[y, z] or xy or xz
                W[x, y, z] = inst

                # Intra-sheet moves: single pile Y (column), single pile Z (row), two-pile Y,Z.
                winner = inst or colseen[z] or row_has or yz

                if not winner:
                    L[x, y, z] = True
                    row_has = True
                    cumX[y, z] = True   # remember this loser for higher x-levels' single-X move

            # Row y complete: fold its losers into the per-column "seen above" flags.
            for z in range(size):
                if L[x, y, z]:
                    colseen[z] = True

        # Sheet x complete: roll the inter-sheet accumulators forward for the next levels.
        A_xy_p2[:] = A_xy_p1
        A_xy_p1[:] = A_xy_cur
        A_xz_p2[:] = A_xz_p1
        A_xz_p1[:] = A_xz_cur

    return W, L


def main():
    """Prompt for one or more Bounded Wythoff sheets and display them together."""
    # Sheets are indexed [x, y, z], so the (row, col) axes are (y, z): row_is_z=False.
    run_sheet_session(compute_sheets, row_is_z=False)


if __name__ == "__main__":
    main()
