"""
Generates and displays Instant-Winner and Loser sheets for 3-Heap Asymmetric Bounded Nim.

The three ordered piles (x, y, z) have cascading move restrictions:

    Pile X: remove any amount.                          (x,y,z) -> (x-t, y,   z)   0 < t <= x
    Pile Y: remove at most the size of Pile X.          (x,y,z) -> (x,   y-t, z)   0 < t <= min(x, y)
    Pile Z: remove at most the size of Pile Y.          (x,y,z) -> (x,   y,   z-t) 0 < t <= min(y, z)

(The "cannot exceed" reading: t <= x for the Y-move and t <= y for the Z-move.)

x is the sheet level: the Pile X move is the only inter-sheet move (it lowers x at fixed y, z),
while the Pile Y and Pile Z moves stay within a sheet. So:

    W_x (instant-winner sheet) = positions that can play Pile X down to a loser on a lower x-level
                               = OR of all lower L-sheets at the same (y, z).
    L_x = supermex(W_x): cells that are neither an instant winner nor able to reach an in-sheet
          loser via a Pile Y or Pile Z move.

Within a sheet both intra-sheet windows have *constant* width: the Pile Y look-back spans the last
x rows (x is fixed for the sheet) and the Pile Z look-back spans the last y columns (constant along
a row). Tracking the most-recent loser per column / per row therefore resolves each cell in O(1).
"""

import numpy as np
from numba import njit
from utils.display import run_sheet_session


@njit
def compute_sheets(N):
    """Compute the W, L, and cumulative-L sheets over the cube ``[0, N)^3``.

    Sheets are indexed ``[x, y, z]`` (row = y, column = z).

    Returns:
        W: 3D boolean array of instant-winner positions (Pile X move to a lower loser).
        L: 3D boolean array of Loser (P-)positions.
        Lcum: 3D boolean array where Lcum[x] is the OR of L_0..L_x (every loser so far).
    """

    L = np.zeros((N, N, N), dtype=np.bool_)
    W = np.zeros((N, N, N), dtype=np.bool_)
    Lcum = np.zeros((N, N, N), dtype=np.bool_)

    # Running OR of every completed lower L-sheet at each (y, z). This is exactly the set of
    # instant winners for the next level, since the Pile X move is unrestricted in t.
    cumX = np.zeros((N, N), dtype=np.bool_)

    for x in range(N):
        W[x, :, :] = cumX                 # W_0 is blank; thereafter it is the lower-loser projection
        L[x, :, :] = supermex(W[x], x)
        cumX = cumX | L[x]                # now the OR of L_0..L_x
        Lcum[x, :, :] = cumX

    return W, L, Lcum


@njit
def supermex(Wx, x):
    """Resolve one sheet: mark losers given the instant-winner sheet ``Wx`` and level ``x``.

    A cell (y, z) is a loser unless it is an instant winner, or it can reach an in-sheet loser by
        Pile Y: some loser at (y', z) with y - x <= y' < y      (window width x), or
        Pile Z: some loser at (y, z') with z - y <= z' < z      (window width y).

    Each window has constant width, so we only need the most-recent loser seen: the closest loser
    below the current cell decides whether *any* loser falls inside the window.

    Args:
        Wx: Boolean instant-winner sheet for this level.
        x: Current x-level, i.e. the Pile Y window width.

    Returns:
        Boolean sheet of the newly selected loser positions (L_x).
    """

    N = Wx.shape[0]
    L = np.zeros((N, N), dtype=np.bool_)

    # For each column z, the row index of the most recent loser found above the current row.
    last_loser_y = np.full(N, -1, dtype=np.int64)

    for y in range(N):
        last_loser_z = -1                 # most recent loser column in this row (Pile Z look-back)
        for z in range(N):
            winner = False

            if Wx[y, z]:                  # Pile X move to a lower-level loser
                winner = True

            # Pile Y move: a loser within the last x rows of column z (t <= min(x, y)).
            if not winner and last_loser_y[z] >= 0 and last_loser_y[z] >= y - x:
                winner = True

            # Pile Z move: a loser within the last y columns of row y (t <= min(y, z)).
            if not winner and last_loser_z >= 0 and last_loser_z >= z - y:
                winner = True

            if not winner:
                L[y, z] = True
                last_loser_z = z
                last_loser_y[z] = y

    return L


def main():
    """Prompt for one or more Asymmetric Bounded Nim sheets and display them together."""
    # Sheets are indexed [x, y, z], so the (row, col) axes are (y, z): row_is_z=False.
    run_sheet_session(compute_sheets, row_is_z=False)


if __name__ == "__main__":
    main()