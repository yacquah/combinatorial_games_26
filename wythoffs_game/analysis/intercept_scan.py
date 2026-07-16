"""Increments read in the farthest band only (y in [25600, 45500))."""
import numpy as np
from pathlib import Path

M = 1 + 3**0.5
CACHE = Path("/Users/jzhang/Documents/VSCode/combinatorial_games_26/wythoffs_game/analysis/data")
loser = np.load(CACHE / "rect_bounded_d101_r124000_c46500.npz")["loser_y"]

LO, HI = 25600, 45500
ks, cols, nb = {}, {}, {}
for x in range(1, 101):
    zz = np.nonzero(loser[x] >= 0)[0]
    yy = loser[x][zz].astype(np.int64)
    up = zz > yy
    yu, zu = yy[up], zz[up].astype(np.int64)
    o = np.argsort(yu)
    yu, zu = yu[o], zu[o]
    m_ = (yu >= LO) & (yu < HI)
    ks[x] = float(np.median(zu[m_] - M * yu[m_]))
    dy, dz = np.diff(yu[m_]), np.diff(zu[m_])
    nb[x] = int(np.sum(dz - 2 * dy != 1))
    cols[x] = dict(zip(yu[m_].tolist(), zu[m_].tolist()))

print(f"{'x':>4} {'k_far':>8} {'dk':>6} {'gapmean':>8} {'gapmin':>6} {'bumps':>5}")
for x in range(2, 101):
    g = [zz - cols[x - 1][yy] for yy, zz in cols[x].items() if yy in cols[x - 1]]
    gm = np.mean(g) if g else float("nan")
    gmin = min(g) if g else -1
    if x % 2 == 0 or x < 20:
        print(f"{x:>4} {ks[x]:8.1f} {ks[x] - ks[x - 1]:6.1f} {gm:8.2f} {gmin:>6} {nb[x]:>5}")

xs = np.array(sorted(ks), float)
kv = np.array([ks[int(i)] for i in xs])
print("\nlocal regression slopes of k_far(x):")
for a, b in ((10, 30), (30, 50), (50, 70), (70, 90), (30, 70), (40, 80)):
    s = (xs >= a) & (xs <= b)
    p = np.polyfit(xs[s], kv[s], 1)
    print(f"  x in [{a},{b}]: {p[0]:.4f}")
print(f"candidates: 2+2sqrt3={2 + 2 * 3**0.5:.4f}  6  m^2={(1 + 3**0.5)**2:.4f}")

# gap means pooled by x-decade (same band): direct increment estimate
print("\npooled gap mean by x-range (far band):")
for a, b in ((20, 40), (40, 60), (60, 80), (80, 100)):
    tot, n = 0, 0
    for x in range(a, b):
        g = [zz - cols[x - 1][yy] for yy, zz in cols[x].items() if yy in cols[x - 1]]
        tot += sum(g)
        n += len(g)
    print(f"  x in [{a},{b}): mean gap {tot / n:.3f}  (n={n})")
