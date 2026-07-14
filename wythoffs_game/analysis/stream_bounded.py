"""Streaming bounded-Wythoff: same recurrence as wythoffs_game/bounded_wythoff.py but
keeps only the rolling 2D sheets, and records each sheet's losers as zvec[x, y] = z
(one loser per column; -1 if the column's loser is above the grid)."""

import numpy as np
from numba import njit


@njit(cache=True)
def compute_zvecs(depth, size):
    zvec = -np.ones((depth, size), dtype=np.int64)

    cum_x = np.zeros((size, size), dtype=np.bool_)
    aux_xz_prev1 = np.zeros((size, size), dtype=np.bool_)
    aux_xz_prev2 = np.zeros((size, size), dtype=np.bool_)
    aux_xy_prev1 = np.zeros((size, size), dtype=np.bool_)
    aux_xy_prev2 = np.zeros((size, size), dtype=np.bool_)
    L_prev1 = np.zeros((size, size), dtype=np.bool_)
    L_prev2 = np.zeros((size, size), dtype=np.bool_)

    for x in range(depth):
        loser_in_col = np.zeros(size, dtype=np.bool_)
        aux_xz_cur = np.zeros((size, size), dtype=np.bool_)
        aux_xy_cur = np.zeros((size, size), dtype=np.bool_)
        aux_yz = np.zeros((size, size), dtype=np.bool_)
        L_cur = np.zeros((size, size), dtype=np.bool_)

        for z in range(size):
            loser_in_row = False
            for y in range(size):
                xz = False
                if x >= 1 and z >= 1 and (L_prev1[z - 1, y] or aux_xz_prev1[z - 1, y]):
                    xz = True
                elif x >= 1 and z >= 2 and (L_prev1[z - 2, y] or aux_xz_prev1[z - 2, y]):
                    xz = True
                elif x >= 2 and z >= 1 and (L_prev2[z - 1, y] or aux_xz_prev2[z - 1, y]):
                    xz = True
                aux_xz_cur[z, y] = xz

                xy = False
                if x >= 1 and y >= 1 and (L_prev1[z, y - 1] or aux_xy_prev1[z, y - 1]):
                    xy = True
                elif x >= 1 and y >= 2 and (L_prev1[z, y - 2] or aux_xy_prev1[z, y - 2]):
                    xy = True
                elif x >= 2 and y >= 1 and (L_prev2[z, y - 1] or aux_xy_prev2[z, y - 1]):
                    xy = True
                aux_xy_cur[z, y] = xy

                yz = False
                if z >= 1 and y >= 1 and (L_cur[z - 1, y - 1] or aux_yz[z - 1, y - 1]):
                    yz = True
                elif z >= 1 and y >= 2 and (L_cur[z - 1, y - 2] or aux_yz[z - 1, y - 2]):
                    yz = True
                elif z >= 2 and y >= 1 and (L_cur[z - 2, y - 1] or aux_yz[z - 2, y - 1]):
                    yz = True
                aux_yz[z, y] = yz

                instant = cum_x[z, y] or xz or xy
                winner = instant or loser_in_col[y] or loser_in_row or yz

                if not winner:
                    L_cur[z, y] = True
                    loser_in_row = True
                    cum_x[z, y] = True
                    zvec[x, y] = z

            for y in range(size):
                if L_cur[z, y]:
                    loser_in_col[y] = True

        aux_xz_prev2[:] = aux_xz_prev1
        aux_xz_prev1[:] = aux_xz_cur
        aux_xy_prev2[:] = aux_xy_prev1
        aux_xy_prev1[:] = aux_xy_cur
        L_prev2[:] = L_prev1
        L_prev1[:] = L_cur

    return zvec
