"""The slope-3 branch that runs through the core of every sheet.

Past the wall fan and before the asymptotic tail, a sheet's upper losers sit on an exact
line of slope 3. Writing the residual r3 = z - 3y, the branch shows up as long runs where
r3 is a *constant integer* -- a plateau -- with each collision bumping it by exactly +1.
The dominant plateau value appears to be 3x - 1, i.e.

    z = 3y + 3x - 1 = 3(x + y) - 1.

This module measures those plateaus so the law can be tested rather than eyeballed.

Convention: everything here takes ``loser_y`` from ``store.load`` -- ``loser_y[x, z]`` is
the y column of the loser in row z. (``analyze``/``bump_decay``/``print_level`` use the
transposed ``zvec`` convention and cannot be fed these arrays.)
"""

import numpy as np

from . import store


def upper_branch(loser_y, x):
    """Sheet ``x``'s upper losers (z > y) as ``(y, z)``, sorted by column."""
    y, z = store.sheet_points(loser_y, x)
    keep = z > y
    y, z = y[keep], z[keep]
    order = np.argsort(y)
    return y[order], z[order]


def plateaus(y, z, min_len=3):
    """Maximal runs of consecutive columns sharing one residual ``r3 = z - 3y``.

    Returns ``[(y_start, y_end, r3, length)]``. A run may skip columns -- what matters is
    that the residual is unchanged, since a skipped column means the loser is on the lower
    line, not that the branch broke.
    """
    if len(y) == 0:
        return []
    r3 = z - 3 * y
    out = []
    start = 0
    for i in range(1, len(r3) + 1):
        if i == len(r3) or r3[i] != r3[start]:
            if i - start >= min_len:
                out.append((int(y[start]), int(y[i - 1]), int(r3[start]), i - start))
            start = i
    return out


def dominant_plateau(loser_y, x, min_len=3):
    """The longest plateau on sheet ``x``, or ``None`` if the sheet has no clean branch."""
    y, z = upper_branch(loser_y, x)
    runs = plateaus(y, z, min_len)
    return max(runs, key=lambda r: r[3]) if runs else None


def predict(x, y):
    """The conjectured branch height at sheet ``x``, column ``y``."""
    return 3 * (x + y) - 1


def check_prediction(loser_y, x, y_lo, y_hi):
    """Compare the conjecture against every actual loser in columns ``[y_lo, y_hi]``.

    Returns ``(n_checked, n_hit, misses)`` where ``misses`` are ``(y, z_actual, z_pred)``.
    """
    y, z = upper_branch(loser_y, x)
    window = (y >= y_lo) & (y <= y_hi)
    y, z = y[window], z[window]
    pred = predict(x, y)
    bad = z != pred
    return len(y), int((~bad).sum()), list(zip(y[bad].tolist(), z[bad].tolist(), pred[bad].tolist()))
