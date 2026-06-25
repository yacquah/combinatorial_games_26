"""'Akiyama 3D Positive Wythoff Nim' sheet generator.

Three piles (x, y, z). A move subtracts (a, b, c) where at least one of a, b, c
is zero OR at least two of them are equal (and the total removed is positive).
Equivalently, the allowed moves are:

  * Remove any number from one pile.
  * Remove any (possibly different) numbers from two piles.
  * Remove the same number from two piles and any number from the third.

As elsewhere in this repo, x is fixed per sheet and the (y, z) plane is rendered
as a [z, y] boolean grid. W_x marks instant winners (a move drops to a loser on
a *lower* x-level); L_x marks losers, recovered from W_x via ``supermex``.

The moves that keep x fixed let a player reach *any* dominated cell (y', z') with
y' <= y, z' <= z in the same sheet, so the losers of a sheet form a strictly
decreasing staircase --- this is what ``supermex`` traces out. The six families
of moves that lower x are accumulated into auxiliary sheets:

  * M1   (x-t, y,   z)    -> ever_lost
  * M2a  (x-s, y-t, z)    -> horizontal prefix-OR of ever_lost
  * M2b  (x-s, y,   z-t)  -> vertical prefix-OR of ever_lost
  * M3a  (x-s, y-s, z-t)  -> Acc3a (x,y diagonal; z free)
  * M3b  (x-s, y-t, z-s)  -> Acc3b (x,z diagonal; y free)
  * M3c  (x-t, y-s, z-s)  -> Dcum  (y,z diagonal; x free)
"""

import numpy as np
from numba import njit
from utils.display import output_sheets, parse_sheet_specs


@njit(cache=True)
def supermex(Wx, grid_size):
    """Recover the loser sheet L_x from the instant-winner sheet W_x.

    Within a sheet a player may move to any dominated cell, so a non-winner is a
    loser only if no dominated cell is already a loser. The losers therefore form
    a strictly decreasing staircase: scanning columns y left to right, the loser's
    z keeps dropping, so we only ever look below the lowest loser found so far.
    """
    Lx = np.zeros((grid_size, grid_size), dtype=np.bool_)
    min_loser_z = grid_size  # No loser found yet; whole column is available.

    for y in range(grid_size):
        for z in range(min_loser_z):
            if not Wx[z, y]:
                Lx[z, y] = True
                min_loser_z = z  # Strictly decreasing for each new loser.
                break
    return Lx


@njit(cache=True)
def compute_sheets(max_size):
    """Compute W_space and L_space for x-levels 0..max_size-1.

    Sheets are indexed [x, z, y]. The per-level work is fused into single in-place
    sweeps over reused scratch buffers (rather than allocating a fresh sheet for each
    shift / cumulative-OR), so the whole space is built in O(max_size^3) with a small
    constant factor and no per-level allocation churn.
    """
    n = max_size
    W_space = np.zeros((n, n, n), dtype=np.bool_)
    L_space = np.zeros((n, n, n), dtype=np.bool_)

    # Rolling auxiliary sheets, each accumulating one family of x-lowering moves.
    ever_lost = np.zeros((n, n), dtype=np.bool_)  # M1: any lower x, same (y, z)
    Acc3a = np.zeros((n, n), dtype=np.bool_)       # M3a: (x-s, y-s, z-t)
    Acc3b = np.zeros((n, n), dtype=np.bool_)       # M3b: (x-s, y-t, z-s)
    Dcum = np.zeros((n, n), dtype=np.bool_)        # M3c: (x-t, y-s, z-s)

    Wx = np.zeros((n, n), dtype=np.bool_)          # reused instant-winner buffer
    tmp = np.zeros((n, n), dtype=np.bool_)         # reused scratch for accumulator updates

    for x in range(n):
        # ---------- Build the instant-winner sheet Wx ----------
        if x == 0:
            Wx[:, :] = False
        else:
            # M1 (ever_lost) together with M2a (OR over y' < y of ever_lost) in one
            # left-to-right sweep per row z.
            for z in range(n):
                hrun = False
                for y in range(n):
                    e = ever_lost[z, y]
                    Wx[z, y] = e or hrun
                    hrun = hrun or e
            # M2b: OR over z' < z of ever_lost, one top-to-bottom sweep per column y.
            for y in range(n):
                vrun = False
                for z in range(n):
                    if vrun:
                        Wx[z, y] = True
                    if ever_lost[z, y]:
                        vrun = True
            # M3a, M3b, and M3c (= Dcum shifted one step down the main diagonal).
            for z in range(n):
                for y in range(n):
                    if Acc3a[z, y] or Acc3b[z, y]:
                        Wx[z, y] = True
                    elif z > 0 and y > 0 and Dcum[z - 1, y - 1]:
                        Wx[z, y] = True

        # ---------- Recover the loser sheet Lx ----------
        Lx = supermex(Wx, n)

        W_space[x] = Wx
        L_space[x] = Lx

        # ---------- Fold Lx into the rolling accumulators for x+1 ----------
        # ever_lost |= Lx
        for z in range(n):
            for y in range(n):
                if Lx[z, y]:
                    ever_lost[z, y] = True

        # Acc3a = shift_y(Acc3a | colcum_z(Lx)): OR the column-cumulative of Lx into
        # Acc3a, then translate one step along +y.
        for y in range(n):
            crun = False
            for z in range(n):
                if Lx[z, y]:
                    crun = True
                tmp[z, y] = Acc3a[z, y] or crun
        for z in range(n):
            Acc3a[z, 0] = False
            for y in range(n - 1, 0, -1):
                Acc3a[z, y] = tmp[z, y - 1]

        # Acc3b = shift_z(Acc3b | rowcum_y(Lx)): mirror of the above along z.
        for z in range(n):
            rrun = False
            for y in range(n):
                if Lx[z, y]:
                    rrun = True
                tmp[z, y] = Acc3b[z, y] or rrun
        for y in range(n):
            Acc3b[0, y] = False
        for z in range(n - 1, 0, -1):
            for y in range(n):
                Acc3b[z, y] = tmp[z - 1, y]

        # Dcum |= diagcum_incl(Lx). Dcum is closed under +diagonal translation, so a
        # single top-left-to-bottom-right sweep that pulls from Dcum[z-1, y-1]
        # propagates each new Lx bit forward along its diagonal.
        for z in range(n):
            for y in range(n):
                if Lx[z, y]:
                    Dcum[z, y] = True
                elif z > 0 and y > 0 and Dcum[z - 1, y - 1]:
                    Dcum[z, y] = True

    return W_space, L_space


def main():
    """Prompt for one or more sheet requests and display them together.

    Each requested sheet may have its own type, x-level, and size, e.g.
    ``W8x16, L4x20, W16x32``.
    """
    print("Enter sheets as <W|L><level>x<size>, separated by commas.")
    # print("Example: W8x16, L4x20, W16x32")
    specs = parse_sheet_specs(input("Sheets:\n"))

    # Compute one space big enough to cover every requested level and size.
    compute_size = max(max(size, level + 1) for _, level, size in specs)
    W_space, L_space = compute_sheets(compute_size)

    sheets = []
    for is_winner, level, size in specs:
        space = W_space if is_winner else L_space
        sheets.append((space[level, :size, :size], is_winner, level))
    output_sheets(sheets)


if __name__ == "__main__":
    main()
