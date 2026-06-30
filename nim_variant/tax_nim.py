"""
Generates and displays Winner and Loser sheets for Tax Nim, a three-heap game.

Normal Nim rules apply (remove any number of chips from a single pile), but each of the other two
untouched piles is "taxed" one chip whenever it is non-empty:

    (x,y,z) -> (x-t,            max(0,y-1),       max(0,z-1))   if 0 < t <= x   (play pile x)
    (x,y,z) -> (max(0,x-1),     y-t,              max(0,z-1))   if 0 < t <= y   (play pile y)
    (x,y,z) -> (max(0,x-1),     max(0,y-1),       z-t)          if 0 < t <= z   (play pile z)

Unlike the other games here, playing one pile shifts the other coordinates, so the clean
sheet/supermex shift recurrence does not apply. However every move strictly lowers the chip total
and never raises any coordinate, so a position only depends on coordinate-wise-smaller positions.
We therefore compute the full 3D space directly in increasing (x, z, y) order: a position is a loser
exactly when no move reaches another loser.

Arrays are indexed [x, z, y] (z = row, y = column). To stay O(N^3) we avoid re-scanning each move's
whole range with auxiliary prefix sheets:
    lower_losers[z,y] : OR of L over all completed lower x-levels at (z, y)  -> covers play-pile-x
    prefix_z[z,y]     : OR of L[x-1, z'<=z, y] (prefix down the column)      -> covers play-pile-z
    prefix_y[z,y]     : OR of L[x-1, z, y'<=y] (prefix along the row)        -> covers play-pile-y
For x >= 1 every move lands on a completed lower level, so these fully determine the level. The
x = 0 plane is self-contained (play-x is impossible there) and is resolved with small direct scans.
"""

import numpy as np
from numba import njit
from utils.display import run_sheet_session


@njit
def compute_sheets(depth, size):
    """Compute the Winner and Loser sheets for Tax Nim over x-levels ``0..depth-1``.

    Sheets are indexed ``[x, z, y]`` over a ``size x size`` (z, y) grid: z is the row, y is the
    column. The game is symmetric in y and z, so the orientation is a convention. Depth (x-levels)
    and grid size are decoupled, so a low-level request on a big grid only allocates the levels it
    needs.

    Returns just ``(W, L)`` -- two ``(depth, size, size)`` cubes; the cumulative-loser (C) sheets are
    derived from L on demand by the display layer (OR of L_0..L_level), so no third cube is stored.

    Args:
        depth: Number of x-levels to compute (cube depth).
        size: Number of cells along each of the y and z axes (grid size).

    Returns:
        W: 3D boolean array of winner positions.
        L: 3D boolean array of loser positions.
    """

    L = np.zeros((depth, size, size), dtype=np.bool_)

    # Auxiliary prefix sheets describing the already-completed levels (see module docstring).
    lower_losers = np.zeros((size, size), dtype=np.bool_)  # OR of L over all x' < current level
    prefix_z = np.zeros((size, size), dtype=np.bool_)  # prefix down column (along z) of level x-1
    prefix_y = np.zeros((size, size), dtype=np.bool_)  # prefix along row (along y) of level x-1

    for x in range(depth):
        for z in range(size):                   # row
            zp = z - 1 if z > 0 else 0          # max(0, z - 1): taxed z
            for y in range(size):               # column
                yp = y - 1 if y > 0 else 0      # max(0, y - 1): taxed y

                winner = False

                # Play pile x: targets (x', y=yp, z=zp) for x' = 0 .. x-1 (all lower levels).
                if lower_losers[zp, yp]:
                    winner = True

                # Play pile z: targets (max(0,x-1), y=yp, z') for z' = 0 .. z-1.
                if not winner and z > 0:
                    if x > 0:
                        if prefix_z[z - 1, yp]:  # prefix of level x-1 down the column, at column yp
                            winner = True
                    else:
                        # x == 0: the targets live in this same plane; rows z' < z are done.
                        for zz in range(z):
                            if L[0, zz, yp]:
                                winner = True
                                break

                # Play pile y: targets (max(0,x-1), y', z=zp) for y' = 0 .. y-1.
                if not winner and y > 0:
                    if x > 0:
                        if prefix_y[zp, y - 1]:  # prefix of level x-1 along the row, at row zp
                            winner = True
                    else:
                        # x == 0: row zp == z (since z == 0 here) and y' < y is already filled.
                        for yy in range(y):
                            if L[0, zp, yy]:
                                winner = True
                                break

                if not winner:
                    L[x, z, y] = True

        # Roll the prefix sheets forward to include the level we just finished.
        for z in range(size):
            for y in range(size):
                lower_losers[z, y] = lower_losers[z, y] or L[x, z, y]

        for z in range(size):
            for y in range(size):
                prev = prefix_z[z - 1, y] if z > 0 else False
                prefix_z[z, y] = L[x, z, y] or prev

        for z in range(size):
            for y in range(size):
                prev = prefix_y[z, y - 1] if y > 0 else False
                prefix_y[z, y] = L[x, z, y] or prev

    # Every position is either a Winner or a Loser under normal play.
    W = ~L
    return W, L


def main():
    """Prompt for one or more Tax Nim sheets and display them together."""
    # Sheets are indexed [x, z, y], so the (row, col) axes are (z, y): row_is_z=True.
    run_sheet_session(compute_sheets, row_is_z=True)


if __name__ == "__main__":
    main()