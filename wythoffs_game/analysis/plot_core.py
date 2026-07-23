"""One sheet at a time, zoomed to the three core regions, with the predicted shapes drawn on top.

This is the viewer for one question only: *what are the three clusters near the origin of a sheet,
and how do they move as x grows?* Everything else about a sheet -- the long slope-(1+sqrt3) lines
running out to y ~ 50x -- is deliberately off-screen. The other viewers show the whole sheet, which
is exactly why the core is an unreadable speck in them.

Two choices make the progression readable:

* **The window scales with the sheet.** Axes are pinned to ``0 .. window * x`` (default 5x), so the
  regions hold still on screen as you step x instead of marching off to the upper right. What you
  are watching is then the *shape* converging, not the numbers growing.
* **The predictions are drawn as lines, not left to your eye.** Each region gets a labelled guide,
  so a sheet either sits on it or does not:

  1. **Origin blob** -- the anti-diagonal ``y + z = (x+1)/3``. It exists only when ``x = 2 (mod 3)``
     (the sum has to be a whole number), so the guide is drawn solid on those sheets and ghosted on
     the other two out of three. Stepping x with the arrow keys is the fastest way to see that
     flicker: on, off, off, on, off, off. The guide is cut to the same ``[1/M, M]`` ratio window the
     branch uses, which is where the dots actually stop (251/251 sheets, ~88% of cells filled).
  2. **Mirror pair** -- the two-equal-pile family {n, n, c}. Drawn as *exact cells*, not as a ratio
     marker: Part 4's Theorem 2 gives one partner ``c(n)`` per ``n`` and one ``n`` per ``c``, so
     sheet x carries at most three region-2 dots -- ``(x, c(x))`` and ``(c(x), x)`` when x is a
     small pile, and ``(n, n)`` on the diagonal when x is some ``n``'s partner. Many carry none.
  3. **Core branch** -- the exact line ``z = 3(x+y) - 1`` and its mirror, region 1. Its lowest dot
     sits around ``z ~ 4.1x``, just above the mirror blob at ``3.23x``; the empty band between the
     two is the gap you can see on screen.

``--fold`` keeps only ``y >= z``, one of the six symmetric copies -- with the guides folded to
match. Worth knowing before you turn it on: folding merges the mirror pair into a *single* blob
(the two are each other's reflection), and it keeps the branch's mirror rather than the branch. The
three regions are three cuts of one symmetric surface, so any fold that removes the duplication also
removes part of the picture. Off by default for that reason.

Keys and mouse: left/right arrows step one sheet, drag to pan, scroll to zoom, double-click to reset
back to the scaled window.

Usage:
    python -m wythoffs_game.analysis.plot_core --levels 1-200
    python -m wythoffs_game.analysis.plot_core --levels 50-120 --window 12   # include the branch
    python -m wythoffs_game.analysis.plot_core --levels 1-200 --fold --dark
"""

import argparse
import math
import webbrowser
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

from .plot_points import SLIDER_KEYS_JS, THEME, parse_levels
from .store import load, sheet_points

PLOTS = Path(__file__).parent / "plots"

M = 1 + math.sqrt(3)          # main slope, and the branch's column window is [x/M, M*x]
B = 1.5 + math.sqrt(3)        # two-equal-pile ratio c/n
NONE = [None]                 # breaks a line trace into disjoint segments


def _dots(loser_y, x, window, fold):
    """Sheet ``x``'s losers inside the scaled window, optionally folded onto ``y >= z``."""
    y, z = sheet_points(loser_y, x)
    w = window * max(x, 1)
    keep = (y <= w) & (z <= w)
    y, z = y[keep], z[keep]
    if fold:
        lo = np.minimum(y, z)
        y, z = np.maximum(y, z), lo
    return y, z


def _partners(loser_y):
    """The two-equal-pile pairing ``n -> c`` and its inverse, read straight off the cache.

    ``{n, n, c}`` is a loser exactly when sheet ``n`` carries a dot at column ``n``. Part 4's
    Theorem 2 says there is at most one such ``c`` per ``n`` and at most one ``n`` per ``c``, so
    both directions are single-valued and the region-2 guide can be an exact cell rather than a
    ratio marker.
    """
    fwd = {}
    for n in range(1, loser_y.shape[0]):
        hits = np.nonzero(loser_y[n] == n)[0]
        if len(hits):
            fwd[n] = int(hits[0])
    return fwd, {c: n for n, c in fwd.items()}


def _guides(x, fold, fwd, inv):
    """The three predicted shapes for sheet ``x`` as ``(xs, ys)`` pairs, in trace order.

    Returns ``(anti_diagonal, blob_markers, branch)``. Folding onto ``y >= z`` cannot just reflect
    endpoints -- the anti-diagonal straddles the mirror line -- so each shape is built directly in
    the half it belongs to.

    Both the anti-diagonal and the branch are drawn only across the window ``[1/M, M]`` in the
    ratio of the two plotted piles: the branch over columns ``[x/M, Mx]``, the anti-diagonal over
    the part of ``y + z = s`` where ``1/M <= z/y <= M``. That is one window law, measured to hold
    on 251 of 251 anti-diagonal sheets, not two coincidences.
    """
    s = (x + 1) / 3                     # the origin blob's constant sum
    a_lo, a_hi = s / (1 + M), s * M / (1 + M)   # the anti-diagonal's own [1/M, M] ratio window
    lo, hi = x / M, M * x               # the branch's column window
    branch_lo, branch_hi = 3 * (x + lo) - 1, 3 * (x + hi) - 1

    # Region 2 is two separate cells, both exact. With x as the *small* pile the partner c(x) puts
    # dots at (x, c) and (c, x); with x as the *large* pile the partner-inverse puts one dot on the
    # diagonal at (n, n). A sheet may carry either, both, or neither.
    hi_dots, lo_dots = [], []
    if x in fwd:
        hi_dots, lo_dots = [x, fwd[x]], [fwd[x], x]
    if x in inv:
        hi_dots, lo_dots = hi_dots + [inv[x]], lo_dots + [inv[x]]

    if fold:
        anti = ([s / 2, a_hi], [s / 2, s - a_hi])
        blob = ([max(p, q) for p, q in zip(hi_dots, lo_dots)],
                [min(p, q) for p, q in zip(hi_dots, lo_dots)])
        branch = ([branch_lo, branch_hi], [lo, hi])          # the mirror y = 3(x+z)-1
    else:
        anti = ([a_lo, a_hi], [s - a_lo, s - a_hi])
        blob = (hi_dots, lo_dots)
        branch = ([lo, hi] + NONE + [branch_lo, branch_hi],
                  [branch_lo, branch_hi] + NONE + [lo, hi])
    return anti, blob, branch


def build(levels, window=5.0, fold=False, dark=False):
    """Flip-book of core windows, one trace per role and the data swapped in per slider step.

    Five traces total, no matter how many levels: dots, mirror axis, anti-diagonal, blob markers,
    branch. Each slider step is an ``update`` that rewrites their x/y arrays and re-ranges the axes,
    which keeps a 500-sheet flip-book as light as a single plot (one trace per level would mean
    thousands of WebGL objects and a legend to match).
    """
    t = THEME[dark]
    size = int(window * max(levels)) + 2
    loser_y = load(max(levels) + 1, size)
    fwd, inv = _partners(loser_y)

    first = levels[0]
    y0, z0 = _dots(loser_y, first, window, fold)
    anti0, blob0, branch0 = _guides(first, fold, fwd, inv)
    w0 = window * max(first, 1)

    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=y0, y=z0, mode="markers", name="losers",
        marker=dict(size=6, color=t["ink"], line=dict(width=0)),
        hovertemplate="(%{x}, %{y})<extra></extra>",
    ))
    fig.add_trace(go.Scattergl(
        x=[0, size], y=[0, size], mode="lines", name="y = z (mirror axis)",
        line=dict(color=t["muted"], width=1, dash="dot"), opacity=0.6, hoverinfo="skip",
    ))
    fig.add_trace(go.Scattergl(
        x=anti0[0], y=anti0[1], mode="lines", name="1. origin blob",
        line=dict(color=t["cat"][0], width=2), hoverinfo="skip",
    ))
    fig.add_trace(go.Scattergl(
        x=blob0[0], y=blob0[1], mode="markers", name="2. mirror pair (two equal piles)",
        marker=dict(size=16, color="rgba(0,0,0,0)", symbol="diamond-open",
                    line=dict(color=t["cat"][5], width=2)),
        hovertemplate="predicted (%{x:.0f}, %{y:.0f})<extra>c/n → 3/2+√3</extra>",
    ))
    fig.add_trace(go.Scattergl(
        x=branch0[0], y=branch0[1], mode="lines", name="3. core branch",
        line=dict(color=t["cat"][1], width=2), hoverinfo="skip",
    ))

    steps = []
    for x in levels:
        y, z = _dots(loser_y, x, window, fold)
        anti, blob, branch = _guides(x, fold, fwd, inv)
        w = window * max(x, 1)
        present = x % 3 == 2
        # The anti-diagonal is ghosted, not hidden, on the sheets that cannot carry it -- seeing the
        # line sit on an empty diagonal is what makes the mod-3 rule click.
        names = ["losers", "y = z (mirror axis)",
                 (f"1. origin blob:  y+z = {(x+1)//3}" if present
                  else f"1. origin blob:  absent (x mod 3 = {x % 3})"),
                 "2. mirror pair (two equal piles)", "3. core branch:  z = 3(x+y) − 1"]
        steps.append(dict(method="update", label=str(x), args=[
            {"x": [y, [0, size], anti[0], blob[0], branch[0]],
             "y": [z, [0, size], anti[1], blob[1], branch[1]],
             "name": names,
             "opacity": [1.0, 0.6, 1.0 if present else 0.2, 1.0, 0.9]},
            {"xaxis.range": [0, w], "yaxis.range": [0, w],
             "title.text": (f"Bounded Wythoff — core of sheet x = {x}"
                            f"   ({len(y):,} losers within {window:g}x"
                            f"{', folded to y ≥ z' if fold else ''})")},
        ]))

    fig.update_layout(
        sliders=[dict(active=0, currentvalue=dict(prefix="x-level = ", font=dict(color=t["ink"])),
                      pad=dict(t=40), steps=steps, font=dict(color=t["muted"]),
                      bgcolor=t["grid"], activebgcolor=t["axis"], bordercolor=t["axis"])],
        title=dict(text=steps[0]["args"][1]["title.text"],
                   font=dict(color=t["ink"], size=16)),
        paper_bgcolor=t["surface"], plot_bgcolor=t["surface"],
        font=dict(color=t["muted"], size=12),
        legend=dict(bgcolor="rgba(0,0,0,0)", yanchor="top", y=0.99, xanchor="right", x=0.99),
        margin=dict(l=70, r=20, t=50, b=60), hovermode="closest", dragmode="pan",
        annotations=[dict(text="← / → step one sheet", showarrow=False, xref="paper", yref="paper",
                          x=0.0, y=1.02, xanchor="left", yanchor="bottom",
                          font=dict(color=t["muted"], size=11))],
    )
    axis = dict(title_font=dict(color=t["ink"], size=15), tickfont=dict(color=t["muted"]),
                gridcolor=t["grid"], zeroline=True, zerolinecolor=t["axis"], zerolinewidth=2,
                linecolor=t["axis"], linewidth=2, mirror=True,
                ticks="outside", tickcolor=t["axis"], ticklen=6, showspikes=False,
                constrain="domain")
    fig.update_xaxes(title_text="y  (pile 2)", range=[0, w0], **axis)
    fig.update_yaxes(title_text="z  (pile 3)", range=[0, w0], scaleanchor="x", scaleratio=1, **axis)
    return fig


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--levels", default="1-200", help="e.g. 1-200 or 0,10,25 (default 1-200)")
    p.add_argument("--window", type=float, default=5.0,
                   help="how many multiples of x the axes span (default 5; the mirror blob sits at "
                        "3.23x, the branch starts near 4.1x, so 5 frames all three regions)")
    p.add_argument("--fold", action="store_true",
                   help="keep only y >= z -- one of the six symmetric copies. Note this merges the "
                        "mirror pair into a single blob and keeps the branch's mirror.")
    p.add_argument("--dark", action="store_true")
    p.add_argument("--out", default="core", help="HTML name under plots/ (default core)")
    p.add_argument("--no-open", action="store_true")
    a = p.parse_args()

    levels = parse_levels(a.levels)
    if not levels:
        raise SystemExit("need at least one level, e.g. --levels 1-200")

    PLOTS.mkdir(exist_ok=True)
    fig = build(levels, window=a.window, fold=a.fold, dark=a.dark)
    out = PLOTS / f"{a.out}.html"
    fig.write_html(out, include_plotlyjs="cdn",
                   config=dict(scrollZoom=True, displaylogo=False,
                               toImageButtonOptions=dict(format="png", scale=2)),
                   post_script=SLIDER_KEYS_JS)
    print(f"wrote {out}")
    if not a.no_open:
        webbrowser.open(out.resolve().as_uri())


if __name__ == "__main__":
    main()
