"""On-disk cache of bounded-Wythoff losers, so a grid is only ever generated once.

A run at grid size S and depth D answers every query with size <= S and level < D: losers
never move when the grid grows (every move decreases a coordinate, so a cell's status is
settled by cells below and left of it). So the cache keeps one file per (depth, size) and
serves a request from any file that covers it, generating only when nothing does.

Files live in ``analysis/data/`` as ``bounded_d<depth>_s<size>.npz``, holding the sparse
``loser_y[x, z]`` array from ``fast_bounded`` -- 4 bytes per row per level, so even
depth 100 x size 30000 is 12 MB on disk.
"""

import time
from pathlib import Path

import numpy as np

from .fast_bounded import compute_loser_y

DATA_DIR = Path(__file__).parent / "data"
PREFIX = "bounded_d"


def _covering(depth, size):
    """The smallest cached file that covers ``depth`` levels on a ``size`` grid, if any."""
    best = None
    for f in DATA_DIR.glob(f"{PREFIX}*.npz"):
        try:
            d, s = f.stem[len(PREFIX):].split("_s")
            d, s = int(d), int(s)
        except ValueError:
            continue
        if d >= depth and s >= size:
            if best is None or d * s < best[1] * best[2]:
                best = (f, d, s)
    return best


def load(depth, size, verbose=True):
    """``loser_y`` for levels ``0..depth-1`` on a ``size x size`` grid, from cache or fresh.

    Rows beyond the requested grid are dropped; loser columns that fall outside it are set
    to -1, so the result is exactly what a fresh run at this size would give.
    """
    DATA_DIR.mkdir(exist_ok=True)
    hit = _covering(depth, size)
    if hit:
        f, d, s = hit
        if verbose:
            print(f"cache hit: {f.name} (covers depth {depth}, size {size})")
        loser_y = np.load(f)["loser_y"]
    else:
        if verbose:
            print(f"generating depth {depth} x size {size} ...", end="", flush=True)
        t = time.time()
        loser_y = compute_loser_y(depth, size)
        f = DATA_DIR / f"{PREFIX}{depth}_s{size}.npz"
        np.savez_compressed(f, loser_y=loser_y)
        if verbose:
            print(f" {time.time() - t:.1f}s -> cached as {f.name}")

    out = loser_y[:depth, :size].copy()
    out[out >= size] = -1
    return out


def sheet_points(loser_y, x):
    """Losers of sheet ``x`` as ``(y, z)`` int arrays."""
    z = np.nonzero(loser_y[x] >= 0)[0]
    return loser_y[x][z].astype(np.int64), z.astype(np.int64)
