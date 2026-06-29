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
We therefore compute the full 3D space directly in increasing (x, y, z) order: a position is a Loser
(P-position) exactly when no move reaches another Loser.

To stay O(N^3) we avoid re-scanning each move's whole range with prefix-OR accumulators:
    cumX[y,z] : OR of L over all completed lower x-levels at (y, z)        -> covers play-pile-x
    preY[y,z] : OR of L[x-1, y'<=y, z] (prefix along y on the level below) -> covers play-pile-y
    preZ[y,z] : OR of L[x-1, y, z'<=z] (prefix along z on the level below) -> covers play-pile-z
For x >= 1 every move lands on a completed lower level, so these fully determine the level. The
x = 0 plane is self-contained (play-x is impossible there) and is resolved with small direct scans.
"""

import numpy as np
from numba import njit
from utils.display import run_sheet_session


@njit
def compute_sheets(N):
    """Compute the Winner, Loser, and cumulative-Loser sheets for Tax Nim over ``[0, N)^3``.

    Sheets are indexed ``[x, y, z]``. For a fixed x the rendered grid uses y as the row and z as the
    column. The game is symmetric in y and z, so the orientation is immaterial.

    Args:
        N: Number of cells to compute along each axis.

    Returns:
        W: 3D boolean array of Winner (N-)positions.
        L: 3D boolean array of Loser (P-)positions.
        Lcum: 3D boolean array where Lcum[x] is the OR of L_0..L_x (every loser so far).
    """

    L = np.zeros((N, N, N), dtype=np.bool_)
    Lcum_space = np.zeros((N, N, N), dtype=np.bool_)

    # Prefix-OR accumulators describing the already-completed levels (see module docstring).
    cumX = np.zeros((N, N), dtype=np.bool_)  # OR of L over all x' < current level
    preY = np.zeros((N, N), dtype=np.bool_)  # prefix along y of the previous (x-1) level
    preZ = np.zeros((N, N), dtype=np.bool_)  # prefix along z of the previous (x-1) level

    for x in range(N):
        for y in range(N):
            yp = y - 1 if y > 0 else 0          # max(0, y - 1): taxed y
            for z in range(N):
                zp = z - 1 if z > 0 else 0      # max(0, z - 1): taxed z

                winner = False

                # Play pile x: targets (x', yp, zp) for x' = 0 .. x-1 (all lower levels).
                if cumX[yp, zp]:
                    winner = True

                # Play pile y: targets (max(0,x-1), y', zp) for y' = 0 .. y-1.
                if not winner and y > 0:
                    if x > 0:
                        if preY[y - 1, zp]:     # prefix of level x-1 along y, at column zp
                            winner = True
                    else:
                        # x == 0: the targets live in this same plane; rows y' < y are done.
                        for yy in range(y):
                            if L[0, yy, zp]:
                                winner = True
                                break

                # Play pile z: targets (max(0,x-1), yp, z') for z' = 0 .. z-1.
                if not winner and z > 0:
                    if x > 0:
                        if preZ[yp, z - 1]:     # prefix of level x-1 along z, at row yp
                            winner = True
                    else:
                        # x == 0: row yp == y (since y == 0 here) and z' < z is already filled.
                        for zz in range(z):
                            if L[0, yp, zz]:
                                winner = True
                                break

                if not winner:
                    L[x, y, z] = True

        # Roll the accumulators forward to include the level we just finished.
        for y in range(N):
            for z in range(N):
                cumX[y, z] = cumX[y, z] or L[x, y, z]

        # cumX now equals the OR of L_0..L_x, i.e. the cumulative-loser sheet for level x.
        Lcum_space[x, :, :] = cumX

        for y in range(N):
            for z in range(N):
                prev = preY[y - 1, z] if y > 0 else False
                preY[y, z] = L[x, y, z] or prev

        for y in range(N):
            for z in range(N):
                prev = preZ[y, z - 1] if z > 0 else False
                preZ[y, z] = L[x, y, z] or prev

    # Every position is either a Winner or a Loser under normal play.
    W = ~L
    return W, L, Lcum_space


def main():
    """Prompt for one or more Tax Nim sheets and display them together."""
    # Sheets are indexed [x, y, z], so the (row, col) axes are (y, z): row_is_z=False.
    run_sheet_session(compute_sheets, row_is_z=False)


if __name__ == "__main__":
    main()