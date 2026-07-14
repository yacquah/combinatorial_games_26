"""Print the losers of one x-level as (y, z) coordinates for Desmos, plus the
asymptotic upper line so you can overlay the RIGHT line instead of eyeballing.

The upper line has slope 1+sqrt(3) ~ 2.7321 on EVERY sheet, but on a high sheet
it only settles far out: the transient "core" near the origin is about 25*x
wide. To actually SEE the slope on sheet x you must plot out to at least
y ~ 30*x (ideally ~50*x). Inside the core the points look steeper than
1+sqrt(3) -- e.g. sheet x=50 reads slope ~3.2 near y=0 and doesn't reach 2.73
until about y=2500. That is the core, not a different slope.

The default grid size is chosen large enough for the sheet to settle; pass your
own size to override. Output is one comma-separated line of (y,z) points,
pasteable into a single Desmos expression. Use --table for one point per line.

Usage:
    python print_level.py <x> [size] [--table]
"""

import math
import sys

import numpy as np

from stream_bounded import compute_zvecs

M = 1 + math.sqrt(3)  # 1 + sqrt(3) ~ 2.7321, the asymptotic upper-line slope


def main():
    argv = sys.argv[1:]
    table = "--table" in argv
    args = [a for a in argv if a != "--table"]
    if not args:
        print(__doc__)
        return
    x = int(args[0])
    # default: tall enough that the upper line clears its ~25*x-wide core AND
    # runs far enough (~50*x) for the slope to converge to 1+sqrt(3).
    size = int(args[1]) if len(args) > 1 else max(2000, int(M * (25 * x + 500)), 155 * x)

    zvec = compute_zvecs(x + 1, size)
    zx = zvec[x]
    pts = [(int(y), int(z)) for y, z in enumerate(zx) if z >= 0]

    print(f"# level x={x}, grid size {size}: {len(pts)} losers")
    if table:
        for y, z in pts:
            print(f"({y},{z})")
    else:
        print(",".join(f"({y},{z})" for y, z in pts))

    # ---- asymptotic upper line: intercept + a size sanity check ----
    ys = np.array([y for y, _ in pts], dtype=float)
    zs = np.array([z for _, z in pts], dtype=float)
    up = zs > ys
    a, b = ys[up], zs[up]
    if a.size < 20:
        return
    max_y = a.max()
    clean_lo = 25 * x + 150
    tail_lo = max(clean_lo, 0.5 * max_y)      # judge slope on the settled far half
    tail = a >= tail_lo
    if tail.sum() < 20:                       # grid too short: use the far 40%
        tail_lo = 0.6 * max_y
        tail = a >= tail_lo
    at, bt = a[tail], b[tail]
    c_est = float(np.median(bt - M * at))     # robust intercept (slope fixed at M)
    emp_slope = float(np.polyfit(at, bt, 1)[0])  # free slope, as a settled-ness check

    print(f"# upper line ~  z = (1+sqrt(3))*y + {c_est:.1f}"
          f"   Desmos:  y=(1+\\sqrt{{3}})x+{c_est:.1f}")
    print(f"# mirror line ~ z = (y - {c_est:.1f})/(1+sqrt(3))"
          f"   Desmos:  y=(x-{c_est:.1f})/(1+\\sqrt{{3}})")
    print(f"# empirical slope over the clean tail (y>={int(tail_lo)}):"
          f" {emp_slope:.3f}   (target {M:.3f})")

    settled = max_y > clean_lo + 300 and abs(emp_slope - M) < 0.02
    if not settled:
        rec = max(size * 2, 160 * x)
        print(f"# WARNING: grid reaches only y={int(max_y)}, but sheet x={x}'s core is"
              f" ~{clean_lo} wide, so the slope here reads too steep.")
        print(f"#          Re-run bigger to see it settle:  python print_level.py {x} {rec}")


if __name__ == "__main__":
    main()
