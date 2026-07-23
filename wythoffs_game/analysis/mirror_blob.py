"""The mirror-pair blobs: losers whose three piles sit in ratio about 1:1:3.

On a sheet plot these show up as two tight clouds, reflections of each other across z = y,
at min(y,z) ~ x and max(y,z) ~ 3x. Unlike the core branch (see ``core_branch.py``) they obey
no exact integer law -- their spread grows in proportion to x, so the object to measure is a
*ratio* z/x rather than a residual z - 3x. Written as

    z ~ (3 + kappa) * x,

this module measures kappa.

Convention: ``loser_y`` from ``store.load`` -- ``loser_y[x, z]`` is the y column of the loser
in row z, matching ``core_branch``. (``analyze``/``bump_decay``/``print_level`` use the
transposed ``zvec`` convention and cannot be fed these arrays.)
"""

import numpy as np

from . import store


def diagonal_losers(loser_y, x, eps=0.25, z_cap=4.0):
    """Sheet ``x``'s blob dots: column within ``eps * x`` of y = x, and height below ``z_cap * x``.

    The height cap is what separates the blob from the sheet's own asymptote. That line runs
    z ~ m*y + c(x) with c(x) ~ 4.8x, so at y ~ x it is already up near 7.5x -- more than twice
    the blob's height. Without the cap the window is almost entirely main-line dots and the
    blob is invisible in the statistics.

    Returns ``(y, z)`` sorted by column. This is the blob above the diagonal; the mirror blob
    below it is its reflection (see ``reflection_misses``).
    """
    y, z = store.sheet_points(loser_y, x)
    keep = (z > y) & (np.abs(y - x) <= eps * x) & (z < z_cap * x)
    y, z = y[keep], z[keep]
    order = np.argsort(y)
    return y[order], z[order]


def ceiling_ratio(loser_y, x, **kw):
    """The blob's upper edge, as the largest ``z / y`` among its dots.

    This is the quantity that converges: it climbs monotonically toward ``3/2 + sqrt(3) = m + 1/2``
    (``m = 1 + sqrt(3)`` the main slope) from below as ``x`` grows. Returns ``None`` for a blank
    sheet.
    """
    y, z = diagonal_losers(loser_y, x, **kw)
    if len(z) == 0:
        return None
    return float(np.max(z / y))


def ratio_sweep(loser_y, x_lo, x_hi, **kw):
    """``(x, n_dots, ceiling z/y)`` for every sheet in ``[x_lo, x_hi]`` that has a blob."""
    out = []
    for x in range(x_lo, x_hi + 1):
        y, z = diagonal_losers(loser_y, x, **kw)
        if len(z):
            out.append((x, len(z), float(np.max(z / y))))
    return out


def max_z(loser_y, x):
    """Highest loser row present on sheet ``x`` -- the truncation guard.

    A sheet whose blob would sit above this is *cut off by the grid*, not a counterexample.
    """
    zrows = np.nonzero(loser_y[x] >= 0)[0]
    return int(zrows.max()) if len(zrows) else -1


def reflection_misses(loser_y, x, eps=0.25):
    """Blob dots ``(y, z)`` whose reflection ``(z, y)`` is not itself a loser on sheet ``x``.

    The p<->q symmetry of the loser surface predicts this list is empty.
    """
    y, z = diagonal_losers(loser_y, x, eps)
    size = loser_y.shape[1]
    bad = []
    for yy, zz in zip(y.tolist(), z.tolist()):
        if yy >= size or loser_y[x, yy] != zz:
            bad.append((yy, zz))
    return bad
