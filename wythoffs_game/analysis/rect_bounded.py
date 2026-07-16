"""Rectangular-grid bounded Wythoff: rows (z) and cols (y) sized independently.

Copy of analysis/fast_bounded.compute_loser_y with rows != cols. Correct for every
in-grid cell because every move decreases a coordinate; the upper line out to
y = cols is influenced only by lower-line losers with z <= cols/m, whose columns
(<= cols) are in-grid.

Because the upper branch sits at z ~ (1+sqrt(3))*y, a run only needs rows ~ (1+sqrt(3))*cols
to hold the whole upper branch out to y = cols -- and that trims the z-extent a square grid
would waste, so for a given amount of RAM a rectangle reaches almost twice as far out in y as a
square. y-reach is what convergence needs, so this is the shape to generate big.

Run it directly to generate and cache a grid (working RAM ~ 11*rows*ceil(cols/64)*8 bytes):

    python -m wythoffs_game.analysis.rect_bounded --cols 100000 --rows 273000 --depth 101

The result caches to data/rect_bounded_d<depth>_r<rows>_c<cols>.npz as sparse loser_y[x, z];
point analysis (e.g. intercept_scan.py) at that filename.
"""
import argparse
import time
from pathlib import Path

import numpy as np
from numba import njit

ONE = np.uint64(1)
ZERO = np.uint64(0)
FULL = np.uint64(0xFFFFFFFFFFFFFFFF)
S1 = np.uint64(1)
S2 = np.uint64(2)
S63 = np.uint64(63)
S62 = np.uint64(62)


@njit(cache=True, nogil=True)
def _first_zero(row, nwords, tail_mask, cols):
    for i in range(nwords):
        w = row[i]
        if i == nwords - 1:
            w |= ~tail_mask
        if w != FULL:
            for b in range(64):
                if (w >> np.uint64(b)) & ONE == ZERO:
                    y = i * 64 + b
                    if y < cols:
                        return y
                    return -1
    return -1


@njit(cache=True, nogil=True)
def compute_loser_y_rect(depth, rows, cols):
    nwords = (cols + 63) // 64
    rem = cols & 63
    tail_mask = FULL if rem == 0 else (ONE << np.uint64(rem)) - ONE

    loser_y = -np.ones((depth, rows), dtype=np.int32)

    cum_x = np.zeros((rows, nwords), dtype=np.uint64)
    xz_p1 = np.zeros((rows, nwords), dtype=np.uint64)
    xz_p2 = np.zeros((rows, nwords), dtype=np.uint64)
    xz_cur = np.zeros((rows, nwords), dtype=np.uint64)
    xy_p1 = np.zeros((rows, nwords), dtype=np.uint64)
    xy_p2 = np.zeros((rows, nwords), dtype=np.uint64)
    xy_cur = np.zeros((rows, nwords), dtype=np.uint64)
    L_p1 = np.zeros((rows, nwords), dtype=np.uint64)
    L_p2 = np.zeros((rows, nwords), dtype=np.uint64)
    L_cur = np.zeros((rows, nwords), dtype=np.uint64)
    C = np.zeros((rows, nwords), dtype=np.uint64)

    col = np.zeros(nwords, dtype=np.uint64)
    yz = np.zeros(nwords, dtype=np.uint64)
    win = np.zeros(nwords, dtype=np.uint64)

    for x in range(depth):
        for i in range(nwords):
            col[i] = ZERO
        for z in range(rows):
            for i in range(nwords):
                L_cur[z, i] = ZERO

            for i in range(nwords):
                b1 = L_p1[z, i] | xy_p1[z, i]
                b2 = L_p2[z, i] | xy_p2[z, i]
                b1_lo = ZERO if i == 0 else (L_p1[z, i - 1] | xy_p1[z, i - 1])
                b2_lo = ZERO if i == 0 else (L_p2[z, i - 1] | xy_p2[z, i - 1])

                xy = ((b1 << S1) | (b1_lo >> S63)) \
                    | ((b1 << S2) | (b1_lo >> S62)) \
                    | ((b2 << S1) | (b2_lo >> S63))
                xy_cur[z, i] = xy

                xzw = ZERO
                if z >= 1:
                    xzw |= L_p1[z - 1, i] | xz_p1[z - 1, i] | L_p2[z - 1, i] | xz_p2[z - 1, i]
                if z >= 2:
                    xzw |= L_p1[z - 2, i] | xz_p1[z - 2, i]
                xz_cur[z, i] = xzw

                yzw = ZERO
                if z >= 1:
                    c1 = C[z - 1, i]
                    c1_lo = ZERO if i == 0 else C[z - 1, i - 1]
                    yzw |= ((c1 << S1) | (c1_lo >> S63)) | ((c1 << S2) | (c1_lo >> S62))
                if z >= 2:
                    c2 = C[z - 2, i]
                    c2_lo = ZERO if i == 0 else C[z - 2, i - 1]
                    yzw |= (c2 << S1) | (c2_lo >> S63)
                yz[i] = yzw

                win[i] = cum_x[z, i] | xzw | xy | col[i] | yzw

            y0 = _first_zero(win, nwords, tail_mask, cols)
            if y0 >= 0:
                bit = ONE << np.uint64(y0 & 63)
                w = y0 >> 6
                L_cur[z, w] = bit
                col[w] |= bit
                cum_x[z, w] |= bit
                loser_y[x, z] = y0

            for i in range(nwords):
                C[z, i] = L_cur[z, i] | yz[i]

        for z in range(rows):
            for i in range(nwords):
                xz_p2[z, i] = xz_p1[z, i]
                xz_p1[z, i] = xz_cur[z, i]
                xy_p2[z, i] = xy_p1[z, i]
                xy_p1[z, i] = xy_cur[z, i]
                L_p2[z, i] = L_p1[z, i]
                L_p1[z, i] = L_cur[z, i]

    return loser_y


DATA = Path(__file__).parent / "data"


def main():
    p = argparse.ArgumentParser(description="Generate and cache a rectangular bounded-Wythoff grid.")
    p.add_argument("--cols", type=int, required=True, help="y-extent (how far out the branch reaches)")
    p.add_argument("--rows", type=int, help="z-extent; default ceil((1+sqrt(3))*cols) + 2000")
    p.add_argument("--depth", type=int, default=101, help="x-levels 0..depth-1 (default 101)")
    a = p.parse_args()

    rows = a.rows or int((1 + 3 ** 0.5) * a.cols) + 2000
    nwords = (a.cols + 63) // 64
    gib = 11 * rows * nwords * 8 / 2 ** 30
    DATA.mkdir(exist_ok=True)
    out = DATA / f"rect_bounded_d{a.depth}_r{rows}_c{a.cols}.npz"
    if out.exists():
        print(f"{out.name} already exists -- delete it to regenerate.")
        return

    print(f"depth {a.depth}, rows(z) {rows}, cols(y) {a.cols}  ->  working RAM ~{gib:.1f} GiB, "
          f"y-reach {a.cols:,}")
    t = time.time()
    loser_y = compute_loser_y_rect(a.depth, rows, a.cols)
    np.savez_compressed(out, loser_y=loser_y)
    print(f"{time.time() - t:.1f}s -> cached {out.name}  ({out.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
