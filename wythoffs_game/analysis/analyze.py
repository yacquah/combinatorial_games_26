"""Per-sheet analysis of bounded-Wythoff loser sheets from zvec[x, y] = z data.

For each x-level, in a clean tail window (past the near-origin region):
  - split columns into upper-line (z > y) and lower-line (z < y)
  - check the exact local law: consecutive upper points satisfy db - 2*da = 1
  - k(x): mode of  b - 2a - n  (n = rank among all upper points)
  - c(x): median of z - m*y  (rank-free intercept, m = 1+sqrt(3))
  - residual spread vs the ideal line z = m*y + c(x)
  - hole gaps (gaps between lower-line columns) and upper-column density
"""

import math
import numpy as np

M = 1 + math.sqrt(3)


def sheet_stats(zv_x, x, win_lo=None, win_hi=None):
    size = len(zv_x)
    ys = np.nonzero(zv_x >= 0)[0]
    zs = zv_x[ys]

    up_mask = zs > ys
    a_all = ys[up_mask]
    b_all = zs[up_mask]
    ranks = np.arange(1, len(a_all) + 1)          # rank among all upper points

    if win_lo is None:
        win_lo = 25 * x + 150
    if win_hi is None:
        win_hi = int(0.95 * (size / M))           # keep b safely on the grid

    w = (a_all >= win_lo) & (a_all <= win_hi)
    a, b, n = a_all[w], b_all[w], ranks[w]
    if len(a) < 60:
        return None

    # exact local law
    da, db = np.diff(a), np.diff(b)
    viol = np.nonzero(db - 2 * da != 1)[0]

    # k(x) = mode of b - 2a - n ; also record step structure
    d = b - 2 * a - n
    vals, counts = np.unique(d, return_counts=True)
    k_mode = int(vals[np.argmax(counts)])
    n_steps = int(np.sum(np.diff(d) != 0))

    # rank-free intercept and residual spread
    resid = b - M * a
    c = float(np.median(resid))
    r = resid - c

    # step sizes da distribution
    da_vals, da_counts = np.unique(da, return_counts=True)

    # holes: lower-line columns in the same window
    low_cols = ys[~up_mask & (zs < ys)]
    lw = low_cols[(low_cols >= win_lo) & (low_cols <= win_hi)]
    gaps = np.diff(lw)
    gap_vals, gap_counts = np.unique(gaps, return_counts=True)

    dens = len(a) / (win_hi - win_lo + 1)
    slope_secant = (b[-1] - b[0]) / (a[-1] - a[0])

    return dict(
        x=x, npts=len(a), k=k_mode, k_all=list(zip(vals.tolist(), counts.tolist())),
        n_steps=n_steps, viol=len(viol),
        c=c, r_min=float(r.min()), r_max=float(r.max()), r_std=float(r.std()),
        slope=slope_secant, dens=dens,
        da=dict(zip(da_vals.tolist(), da_counts.tolist())),
        gaps=dict(zip(gap_vals.tolist(), gap_counts.tolist())),
    )


def run(path, depth=None, every=1):
    zv = np.load(path)
    if depth is None:
        depth = zv.shape[0]
    out = []
    for x in range(0, depth, every):
        s = sheet_stats(zv[x], x)
        if s:
            out.append(s)
    return out
