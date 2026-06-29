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
apply. Instead we compute the full 3D space directly, looking back at stored lower L-sheets for the
x-reducing moves and running a (restricted) supermex for the moves that keep x fixed.
"""

import numpy as np
from numba import njit
from utils.display import run_sheet_session


@njit
def compute_sheets(max_size):
    """Compute the W, L, and cumulative-L sheets for Restricted 3-heap Wythoff up to ``max_size``.

    Sheets are indexed ``[x, z, y]`` so that a fixed x yields a 2D grid with z as the row and y as
    the column, matching the rest of the codebase.

    Args:
        max_size: Number of levels/cells to compute along each axis.

    Returns:
        W: 3D boolean array of Instant-Winner positions.
        L: 3D boolean array of Loser (P-)positions.
        Lcum: 3D boolean array where Lcum[x] is the OR of L_0..L_x (every loser so far).
    """

    L = np.zeros((max_size, max_size, max_size), dtype=np.bool_)
    W = np.zeros((max_size, max_size, max_size), dtype=np.bool_)
    Lcum = np.zeros((max_size, max_size, max_size), dtype=np.bool_)

    # Running OR of every L-sheet strictly below the current level. Handles the unrestricted
    # single-pile move (x-t, y, z): any lower x-level loser at the same (y, z) makes us a winner.
    cumL = np.zeros((max_size, max_size), dtype=np.bool_)

    for x in range(max_size):
        Wx = W[x]

        # -----------------------------------------------------------------
        # STEP 1: Look-back for the x-reducing moves (build W_x)
        # -----------------------------------------------------------------
        for z in range(max_size):
            for y in range(max_size):
                # Single-pile move on x: any lower L at the same (y, z).
                if cumL[z, y]:
                    Wx[z, y] = True
                    continue

                # The two-pile moves that touch x are both bounded by t <= min(x, y, z):
                #   - t <= x and t <= y for non-negativity of the two reduced piles
                #   - t <= (third, untouched pile) for the game restriction
                t_max = x
                if y < t_max:
                    t_max = y
                if z < t_max:
                    t_max = z

                found = False
                for t in range(1, t_max + 1):
                    # (x-t, y-t, z): remove t from x and y, untouched pile z (restriction t <= z)
                    if L[x - t, z, y - t]:
                        found = True
                        break
                    # (x-t, y, z-t): remove t from x and z, untouched pile y (restriction t <= y)
                    if L[x - t, z - t, y]:
                        found = True
                        break

                if found:
                    Wx[z, y] = True

        # -----------------------------------------------------------------
        # STEP 2: Supermex for the moves that keep x fixed (build L_x)
        # -----------------------------------------------------------------
        L[x] = supermex(Wx, x)
        cumL = cumL | L[x]            # now the OR of L_0..L_x
        Lcum[x] = cumL

    return W, L, Lcum


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
