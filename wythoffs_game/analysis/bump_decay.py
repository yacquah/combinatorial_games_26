"""Are collisions transient or persistent along a sheet's line?

Counts perching-law violations (db - 2da != 1) among consecutive upper-line
losers, binned by column, per sheet and aggregated. If the per-column rate
decays with column, collisions are a transient boundary effect: each bump is a
permanent +1 shift of everything after it (an intercept effect), and a finite
number of bumps cannot change the asymptotic slope — so the slope of every
sheet is exactly 2 + lambda, pinned at 1 + sqrt(3) by the column-partition
equation lambda = m / (m + 1).

Usage:
    python bump_decay.py path/to/zvec.npy
(regenerate zvec with stream_bounded.compute_zvecs, e.g. depth 33, size 12000)

Measured on zvec 33x12000, sheets 10..27, bumps per column by column bin:
    [0,250): 0.1133   [250,500): 0.0091   [500,1000): 0.0022
    [1000,2000): 0.0007   [2000,4000): 0.0002
i.e. a ~500x decay — collisions cluster just past the chaotic core and die out
along the line.
"""

import sys
import numpy as np

BINS = [0, 250, 500, 1000, 2000, 4000]


def bump_columns(zv_x):
    """Columns (upper-line) where the perching law db = 2da + 1 is violated."""
    ys = np.nonzero(zv_x >= 0)[0]
    zs = zv_x[ys]
    up = zs > ys
    a, b = ys[up], zs[up]
    da, db = np.diff(a), np.diff(b)
    exc = db - 2 * da - 1
    return a[1:][exc != 0], exc[exc != 0]


def run(path, x_lo=10, x_hi=27):
    zv = np.load(path)
    x_hi = min(x_hi, zv.shape[0] - 1)
    labels = [f"[{BINS[i]},{BINS[i+1]})" for i in range(len(BINS) - 1)]
    agg = np.zeros(len(labels), dtype=int)

    print(f"{'x':>3} " + " ".join(f"{l:>12}" for l in labels))
    for x in range(x_lo, x_hi + 1):
        cols, _sizes = bump_columns(zv[x])
        row = [int(((cols >= BINS[i]) & (cols < BINS[i + 1])).sum())
               for i in range(len(labels))]
        agg += row
        print(f"{x:>3} " + " ".join(f"{n:>12}" for n in row))

    nsheets = x_hi - x_lo + 1
    width = np.diff(np.array(BINS))
    print(f"{'all':>3} " + " ".join(f"{n:>12}" for n in agg))
    print("bumps per column: " +
          "  ".join(f"{agg[i] / width[i] / nsheets:.6f}" for i in range(len(labels))))


if __name__ == "__main__":
    run(sys.argv[1])
