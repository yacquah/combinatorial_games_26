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

The bounded-ratio two-pile move spans a 2D wedge of targets, so the usual shift-accumulator
recurrence does not apply. We compute the full 3D space directly: a position is a Loser exactly when
no move reaches another Loser. The wedge tests reduce to "is there a loser in this contiguous strip
of a row/column", answered in O(1) with prefix-loser-counts over completed rows, columns, and
sheets -- giving O(N^4) overall rather than the O(N^5) of a naive double scan.

W_x (instant winners) records the moves that lower x; L_x the losers. Sheets are indexed [x, y, z]
(row y, column z); the game is symmetric in all three piles, so the orientation is immaterial.
"""

import numpy as np
from numba import njit
from utils.display import run_sheet_session


@njit
def compute_sheets(N):
    """Compute the W, L, and cumulative-L sheets over the cube ``[0, N)^3``.

    Returns:
        W: instant-winner positions (some move lowers x onto a loser).
        L: Loser (P-)positions.
        Lcum: Lcum[x] is the OR of L_0..L_x (every loser seen up through level x).
    """

    L = np.zeros((N, N, N), dtype=np.bool_)
    W = np.zeros((N, N, N), dtype=np.bool_)
    Lcum = np.zeros((N, N, N), dtype=np.bool_)

    # Prefix loser-counts over completed sheets, used to test the two-pile wedges in O(1):
    #   colpre[x, y, z] = # losers in sheet x, column z, rows 0..y   (column-cumulative)
    #   rowpre[x, y, z] = # losers in sheet x, row y, columns 0..z   (row-cumulative)
    colpre = np.zeros((N, N, N), dtype=np.int32)
    rowpre = np.zeros((N, N, N), dtype=np.int32)

    cumX = np.zeros((N, N), dtype=np.bool_)  # any loser at (y, z) on a strictly lower x-level

    for x in range(N):
        colseen = np.zeros(N, dtype=np.bool_)  # any loser so far in column z (rows < y), this sheet

        for y in range(N):
            row_has = False                    # any loser in this row at a column < current z

            for z in range(N):
                # ---------- inter-sheet moves: these define the instant-winner sheet ----------
                inst = False

                # Single pile X: any loser at the same (y, z) on a lower level.
                if cumX[y, z]:
                    inst = True

                # Two-pile X,Y: remove a from X (1..x), b from Y with b in [ceil(a/2), 2a].
                if not inst:
                    a_max = x if x < 2 * y else 2 * y
                    for a in range(1, a_max + 1):
                        xs = x - a
                        b_lo = (a + 1) // 2
                        b_hi = 2 * a if 2 * a < y else y
                        if b_lo > b_hi:
                            continue
                        r1 = y - b_hi          # smallest target row
                        r2 = y - b_lo          # largest target row
                        cnt = colpre[xs, r2, z]
                        if r1 > 0:
                            cnt -= colpre[xs, r1 - 1, z]
                        if cnt > 0:
                            inst = True
                            break

                # Two-pile X,Z: remove a from X (1..x), b from Z with b in [ceil(a/2), 2a].
                if not inst:
                    a_max = x if x < 2 * z else 2 * z
                    for a in range(1, a_max + 1):
                        xs = x - a
                        b_lo = (a + 1) // 2
                        b_hi = 2 * a if 2 * a < z else z
                        if b_lo > b_hi:
                            continue
                        c1 = z - b_hi
                        c2 = z - b_lo
                        cnt = rowpre[xs, y, c2]
                        if c1 > 0:
                            cnt -= rowpre[xs, y, c1 - 1]
                        if cnt > 0:
                            inst = True
                            break

                W[x, y, z] = inst
                winner = inst

                # ---------- intra-sheet moves ----------
                # Single pile Y: any loser above in this column.
                if not winner and colseen[z]:
                    winner = True
                # Single pile Z: any loser to the left in this row.
                if not winner and row_has:
                    winner = True
                # Two-pile Y,Z: remove a from Y (1..y), b from Z with b in [ceil(a/2), 2a].
                if not winner:
                    a_max = y if y < 2 * z else 2 * z
                    for a in range(1, a_max + 1):
                        ys = y - a
                        b_lo = (a + 1) // 2
                        b_hi = 2 * a if 2 * a < z else z
                        if b_lo > b_hi:
                            continue
                        c1 = z - b_hi
                        c2 = z - b_lo
                        cnt = rowpre[x, ys, c2]    # completed row ys (< y) of this sheet
                        if c1 > 0:
                            cnt -= rowpre[x, ys, c1 - 1]
                        if cnt > 0:
                            winner = True
                            break

                if not winner:
                    L[x, y, z] = True
                    row_has = True

                # Extend this row's running prefix to include column z.
                rowpre[x, y, z] = (rowpre[x, y, z - 1] if z > 0 else 0) + (1 if L[x, y, z] else 0)

            # Row y is complete: fold its losers into the per-column "seen above" flags.
            for z in range(N):
                if L[x, y, z]:
                    colseen[z] = True

        # Sheet x is complete: build its column-cumulative prefix and roll the lower-x union.
        for z in range(N):
            run = 0
            for y in range(N):
                if L[x, y, z]:
                    run += 1
                colpre[x, y, z] = run
        for y in range(N):
            for z in range(N):
                if L[x, y, z]:
                    cumX[y, z] = True
                Lcum[x, y, z] = cumX[y, z]

    return W, L, Lcum


def main():
    """Prompt for one or more Bounded Wythoff sheets and display them together."""
    # Sheets are indexed [x, y, z], so the (row, col) axes are (y, z): row_is_z=False.
    run_sheet_session(compute_sheets, row_is_z=False)


if __name__ == "__main__":
    main()
