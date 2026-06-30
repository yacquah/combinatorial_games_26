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
the whole wedge behind each cell, each move keeps an **auxiliary sheet** that advances one basis step
per level: a cell is a winner via the move iff a loser (or a cell already marked in the auxiliary
sheet) sits one basis vector behind it. That makes each wedge test O(1).

Because the basis vectors only reach back x-1 and x-2 along the level axis, the inter-sheet auxiliary
sheets need just the two previous levels in memory (no 3D loser history).

W_x (instant winners) records the moves that lower x; L_x the losers. Sheets are indexed [x, z, y]
(row z, column y); the game is symmetric in all three piles, so the orientation is a convention.
"""

import numpy as np
from numba import njit
from utils.display import run_sheet_session


@njit(cache=True)
def compute_sheets(depth, size):
    """Compute the W and L sheets over x-levels ``0..depth-1`` on a ``size x size`` (z, y) grid.

    Sheets are indexed ``[x, z, y]`` (row = z, column = y). The game is symmetric in all three piles,
    so this orientation is a convention, not a constraint.

    Returns only ``(W, L)`` -- two ``(depth, size, size)`` boolean cubes -- to keep memory down at
    large sizes (each cube is depth*size^2 bytes). Depth and grid size are decoupled, so requesting a
    low x-level on a big grid no longer allocates a full size^3 cube. The cumulative-loser (C) sheets
    are derived from L on demand by the display layer (OR of L_0..L_level), so no third cube is
    stored.

    Returns:
        W: instant-winner positions (some move lowers x onto a loser).
        L: loser positions.
    """

    L = np.zeros((depth, size, size), dtype=np.bool_)
    W = np.zeros((depth, size, size), dtype=np.bool_)

    cum_x = np.zeros((size, size), dtype=np.bool_)  # any loser at (z, y) on a strictly lower x-level

    # Auxiliary sheets for the two inter-sheet two-pile moves, holding the winners each move
    # generates. ``_prev1`` / ``_prev2`` are the auxiliary sheets from the previous one / two
    # x-levels (the only history the Hilbert-basis steps reach back to).
    aux_xz_prev1 = np.zeros((size, size), dtype=np.bool_)
    aux_xz_prev2 = np.zeros((size, size), dtype=np.bool_)
    aux_xy_prev1 = np.zeros((size, size), dtype=np.bool_)
    aux_xy_prev2 = np.zeros((size, size), dtype=np.bool_)

    for x in range(depth):
        loser_in_col = np.zeros(size, dtype=np.bool_)     # a loser in column y at rows < z, this sheet
        aux_xz_cur = np.zeros((size, size), dtype=np.bool_)  # this level's X,Z auxiliary sheet
        aux_xy_cur = np.zeros((size, size), dtype=np.bool_)  # this level's X,Y auxiliary sheet
        aux_yz = np.zeros((size, size), dtype=np.bool_)      # intra-sheet Y,Z auxiliary (this sheet)

        for z in range(size):
            loser_in_row = False                          # a loser in this row at a column < y

            for y in range(size):
                # ---------- two-pile moves, advanced one Hilbert-basis step at a time ----------
                # X,Z move (offset in the x,z plane; y fixed): bases (1,1), (1,2), (2,1) on (x,z).
                xz = False
                if x >= 1 and z >= 1 and (L[x - 1, z - 1, y] or aux_xz_prev1[z - 1, y]):
                    xz = True
                elif x >= 1 and z >= 2 and (L[x - 1, z - 2, y] or aux_xz_prev1[z - 2, y]):
                    xz = True
                elif x >= 2 and z >= 1 and (L[x - 2, z - 1, y] or aux_xz_prev2[z - 1, y]):
                    xz = True
                aux_xz_cur[z, y] = xz

                # X,Y move (offset in the x,y plane; z fixed).
                xy = False
                if x >= 1 and y >= 1 and (L[x - 1, z, y - 1] or aux_xy_prev1[z, y - 1]):
                    xy = True
                elif x >= 1 and y >= 2 and (L[x - 1, z, y - 2] or aux_xy_prev1[z, y - 2]):
                    xy = True
                elif x >= 2 and y >= 1 and (L[x - 2, z, y - 1] or aux_xy_prev2[z, y - 1]):
                    xy = True
                aux_xy_cur[z, y] = xy

                # Y,Z move (offset in the y,z plane; x fixed -> current sheet).
                yz = False
                if z >= 1 and y >= 1 and (L[x, z - 1, y - 1] or aux_yz[z - 1, y - 1]):
                    yz = True
                elif z >= 1 and y >= 2 and (L[x, z - 1, y - 2] or aux_yz[z - 1, y - 2]):
                    yz = True
                elif z >= 2 and y >= 1 and (L[x, z - 2, y - 1] or aux_yz[z - 2, y - 1]):
                    yz = True
                aux_yz[z, y] = yz

                # ---------- decide winner / loser ----------
                # Inter-sheet moves (lower x) define the instant-winner sheet.
                instant = cum_x[z, y] or xz or xy
                W[x, z, y] = instant

                # Intra-sheet moves: single pile Z (down the column), single pile Y (along the row),
                # two-pile Y,Z.
                winner = instant or loser_in_col[y] or loser_in_row or yz

                if not winner:
                    L[x, z, y] = True
                    loser_in_row = True
                    cum_x[z, y] = True   # remember this loser for higher x-levels' single-X move

            # Row z complete: fold its losers into the per-column "seen above" flags.
            for y in range(size):
                if L[x, z, y]:
                    loser_in_col[y] = True

        # Sheet x complete: roll the inter-sheet auxiliary sheets forward for the next levels.
        aux_xz_prev2[:] = aux_xz_prev1
        aux_xz_prev1[:] = aux_xz_cur
        aux_xy_prev2[:] = aux_xy_prev1
        aux_xy_prev1[:] = aux_xy_cur

    return W, L


def main():
    """Prompt for one or more Bounded Wythoff sheets and display them together."""
    # Sheets are indexed [x, z, y], so the (row, col) axes are (z, y): row_is_z=True.
    run_sheet_session(compute_sheets, row_is_z=True)


if __name__ == "__main__":
    main()
