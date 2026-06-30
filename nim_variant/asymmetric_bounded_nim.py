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

Sheets are indexed [x, z, y] (z = row, y = column). Within a sheet both intra-sheet windows have
*constant* width: the Pile Y window (along the row) spans the last x columns (x is fixed for the
sheet) and the Pile Z window (down the column) spans the last y rows. Tracking the most-recent loser
per row / per column therefore resolves each cell in O(1).
"""

import numpy as np
from numba import njit
from utils.display import run_sheet_session


@njit
def compute_sheets(depth, size):
    """Compute the W and L sheets over x-levels ``0..depth-1`` on a ``size x size`` (z, y) grid.

    Sheets are indexed ``[x, z, y]`` (row = z, column = y). Depth (x-levels) and grid size are
    decoupled, so a low-level request on a big grid only allocates the levels it needs.

    Returns just ``(W, L)`` -- two ``(depth, size, size)`` cubes; the cumulative-loser (C) sheets are
    derived from L on demand by the display layer (OR of L_0..L_level), so no third cube is stored.

    Returns:
        W: 3D boolean array of instant-winner positions (Pile X move to a lower loser).
        L: 3D boolean array of loser positions.
    """

    L = np.zeros((depth, size, size), dtype=np.bool_)
    W = np.zeros((depth, size, size), dtype=np.bool_)

    # Running OR of every completed lower L-sheet at each (z, y). This is exactly the set of
    # instant winners for the next level, since the Pile X move is unrestricted in t.
    lower_losers = np.zeros((size, size), dtype=np.bool_)

    for x in range(depth):
        W[x, :, :] = lower_losers         # W_0 is blank; thereafter it is the lower-loser projection
        L[x, :, :] = supermex(W[x], x)
        lower_losers = lower_losers | L[x]   # now the OR of L_0..L_x

    return W, L


@njit
def supermex(Wx, x):
    """Resolve one sheet: mark losers given the instant-winner sheet ``Wx`` and level ``x``.

    Sheets are indexed [z, y] (z = row, y = column). A cell (y, z) is a loser unless it is an instant
    winner, or it can reach an in-sheet loser by
        Pile Y: some loser at (y', z) with y - x <= y' < y      (window width x, along the row), or
        Pile Z: some loser at (y, z') with z - y <= z' < z      (window width y, down the column).

    Each window has constant width, so we only need the most-recent loser seen: the closest loser
    behind the current cell decides whether *any* loser falls inside the window.

    Args:
        Wx: Boolean instant-winner sheet for this level, indexed [z, y].
        x: Current x-level, i.e. the Pile Y window width.

    Returns:
        Boolean sheet of the newly selected loser positions (L_x), indexed [z, y].
    """

    N = Wx.shape[0]
    L = np.zeros((N, N), dtype=np.bool_)

    # For each column y, the row index (z) of the most recent loser found above the current row.
    last_loser_z = np.full(N, -1, dtype=np.int64)

    for z in range(N):
        last_loser_y = -1                 # most recent loser column in this row (Pile Y look-back)
        for y in range(N):
            winner = False

            if Wx[z, y]:                  # Pile X move to a lower-level loser
                winner = True

            # Pile Y move: a loser within the last x columns of row z (t <= min(x, y)).
            if not winner and last_loser_y >= 0 and last_loser_y >= y - x:
                winner = True

            # Pile Z move: a loser within the last y rows of column y (t <= min(y, z)).
            if not winner and last_loser_z[y] >= 0 and last_loser_z[y] >= z - y:
                winner = True

            if not winner:
                L[z, y] = True
                last_loser_y = y
                last_loser_z[y] = z

    return L


def main():
    """Prompt for one or more Asymmetric Bounded Nim sheets and display them together."""
    # Sheets are indexed [x, z, y], so the (row, col) axes are (z, y): row_is_z=True.
    run_sheet_session(compute_sheets, row_is_z=True)


if __name__ == "__main__":
    main()