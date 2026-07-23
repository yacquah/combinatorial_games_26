"""Every loser with two equal piles, plotted as one picture.

Piles are interchangeable, so write every position sorted: ``(x, y, z)`` with ``x <= y <= z``.
Then "two coordinates are equal" has only two possible shapes, ``(x, x, z)`` and ``(x, z, z)``,
and the data says the second one never happens -- **the repeated pile is always one of the two
smaller ones**. So the whole family is ``(x, x, z)`` with ``z >= x``, indexed by ``x``.

Part 4's Theorem 2 says the family is a *pairing*: at most one ``z`` per ``x``, and at most one
``x`` per ``z``. So it collapses to a single curve ``x -> z(x)``, which is what this plots.

Two panels, sharing the ``x`` axis:

1. **z against x.** The pairing itself. It is not a cloud -- it is two straight lines plus five
   strays, which is the answer to "is there a pattern".
2. **The ratio z/x against x.** The same data with the growth divided out, which is the view that
   shows the pattern is *not* drifting with x: two flat bands, an empty gap between them, and no
   periodicity inside either band.

The three families the colours separate:

* **lower line**, ``z ~ (3/2 + sqrt3) x ~ 3.232 x`` -- the mirror-pair blob near the origin of a
  sheet. Roughly 87% of all x. Approaches the line from below, so small x reads nearer 2.5.
* **upper line**, ``z = 6x - d`` with ``d`` in 1..5 -- these sit on (or one to five cells under)
  the core surface ``z = 3(x + y) - 1``, which at ``y = x`` reads exactly ``z = 6x - 1``.
  Roughly 13% of all x, scattered through the integers with no visible arithmetic rule.
* **all three equal**, ``z = x`` -- only x = 1, 2, 4, 5, 13, and nothing after that up to 800.

Reading it per sheet: on the sheet for pile ``x`` the two-equal losers are exactly the dots on the
three special lines ``y = x``, ``z = x`` and ``y = z``. A sheet carries at most three of them.

**Truncation guard.** The upper line needs ``z ~ 6x``, so a cache of width ``s`` only resolves the
family up to ``x ~ s/6``. Asking for more silently deletes the upper line rather than erroring, so
the script checks that every x in range has a partner and refuses to plot if any are missing.

Usage:
    python -m wythoffs_game.analysis.plot_equal_pairs
    python -m wythoffs_game.analysis.plot_equal_pairs --max-x 300 --dark
"""

import argparse
import math
import webbrowser
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .plot_points import THEME
from .store import load

PLOTS = Path(__file__).parent / "plots"

B = 1.5 + math.sqrt(3)        # the lower line's conjectured ratio z/x
SURFACE_RATIO = 6.0           # the upper line: z = 6x - 1 is z = 3(x+y) - 1 at y = x


def equal_pairs(loser_y, max_x):
    """``(x, z)`` for every loser ``(x, x, z)`` with ``x <= max_x``, as two int arrays.

    ``(x, x, z)`` is a loser exactly when sheet ``x`` has a dot in column ``x``, i.e. when some
    row z of ``loser_y[x]`` holds the value ``x``. Theorem 2 promises at most one such row; the
    caller checks that promise rather than this function assuming it.
    """
    xs, zs = [], []
    for x in range(1, max_x + 1):
        for z in np.nonzero(loser_y[x] == x)[0]:
            xs.append(x)
            zs.append(int(z))
    return np.array(xs), np.array(zs)


def families(xs, zs):
    """Split the pairing into (all-equal, lower line, upper line) boolean masks.

    The split is by ratio and it is unambiguous: measured ratios land in [1, 1] or [2, 4] or
    [5, 6], never in the gaps, so the 1.5 and 4.5 cuts are nowhere near any data point.
    """
    r = zs / xs
    return r == 1.0, (r > 1.5) & (r < 4.5), r > 4.5


def build(loser_y, max_x, dark=False):
    """The two-panel figure, plus the text summary that goes with it."""
    t = THEME[dark]
    xs, zs = equal_pairs(loser_y, max_x)
    missing = sorted(set(range(1, max_x + 1)) - set(xs.tolist()))
    dupes = len(xs) - len(set(xs.tolist()))
    eq, lo, hi = families(xs, zs)
    r = zs / xs

    # Blue / green / red at ~7 deltaE under deuteranopia, so identity never rests on hue alone:
    # each family also gets its own marker symbol, its own band of the plot, and a legend entry.
    cat = [t["cat"][0], t["cat"][1], t["cat"][5]]
    spec = [
        (lo, "lower line   z ≈ 3.232 x", cat[0], "circle"),
        (hi, "upper line   z = 6x − d", cat[2], "triangle-up"),
        (eq, "all three equal   z = x", cat[1], "square"),
    ]

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.64, 0.36],
        subplot_titles=("the odd pile z that goes with each repeated pile x",
                        "the same data as a ratio — z/x against x"),
    )

    # Guides first, so the dots sit on top of them. Panel 1 gets the rays z = B*x and z = 6x;
    # panel 2 gets the same two constants as horizontals, which is what dividing by x does to a ray.
    span = np.array([0, max_x])
    for row in (1, 2):
        for val in (B, SURFACE_RATIO):
            fig.add_trace(go.Scatter(
                x=span, y=(val * span if row == 1 else [val, val]),
                mode="lines", showlegend=False, hoverinfo="skip",
                line=dict(color=t["muted"], width=1, dash="dash"), opacity=0.7,
            ), row=row, col=1)

    for row, yy in enumerate([zs, r], start=1):
        for mask, name, color, symbol in spec:
            fig.add_trace(go.Scattergl(
                x=xs[mask], y=yy[mask], mode="markers", name=name, legendgroup=name,
                showlegend=(row == 1),
                marker=dict(size=7, color=color, symbol=symbol,
                            line=dict(width=1, color=t["surface"])),
                customdata=np.stack([zs[mask], r[mask]], axis=-1),
                hovertemplate=("(%{x}, %{x}, %{customdata[0]})"
                               "<br>z/x = %{customdata[1]:.4f}<extra></extra>"),
            ), row=row, col=1)

    fig.update_layout(
        title=dict(text=(f"Bounded Wythoff — the {len(xs):,} losers (x, x, z) "
                         f"with two equal piles (x ≤ {max_x:,})"),
                   font=dict(color=t["ink"], size=17)),
        paper_bgcolor=t["surface"], plot_bgcolor=t["surface"],
        font=dict(color=t["muted"], size=12),
        legend=dict(bgcolor="rgba(0,0,0,0)", yanchor="top", y=0.99, xanchor="left", x=0.01,
                    font=dict(color=t["ink"])),
        margin=dict(l=80, r=30, t=70, b=60), hovermode="closest", dragmode="pan",
    )
    for note in fig.layout.annotations:
        note.font = dict(color=t["ink"], size=13)

    axis = dict(title_font=dict(color=t["ink"], size=14), tickfont=dict(color=t["muted"]),
                gridcolor=t["grid"], zeroline=False, linecolor=t["axis"], linewidth=2,
                ticks="outside", tickcolor=t["axis"], ticklen=6)
    fig.update_xaxes(range=[0, max_x * 1.02], **axis)
    fig.update_xaxes(title_text="x  (the repeated pile)", row=2, col=1)
    fig.update_yaxes(title_text="z  (the odd pile out)", row=1, col=1,
                     range=[0, SURFACE_RATIO * max_x * 1.03], **axis)
    fig.update_yaxes(title_text="z / x", row=2, col=1, range=[0, 7], **axis)

    # Direct labels on the two guides, so the reference values are readable without the legend.
    labels = [(B, "z = (3/2 + √3) x ≈ 3.232 x"),
              (SURFACE_RATIO, "z = 6x − 1   (the core surface z = 3(x+y) − 1 at y = x)")]
    for val, lab in labels:
        fig.add_annotation(x=max_x, y=val * max_x, text=lab, row=1, col=1, showarrow=False,
                           xanchor="right", yanchor="bottom", font=dict(color=t["muted"], size=11))

    summary = [
        f"x = 1..{max_x}: {len(xs):,} losers (x, x, z), {len(set(zs.tolist())):,} distinct z",
        f"  x with no z          : {len(missing)}   (any at all means the cache is too narrow)",
        f"  x with two z         : {dupes}   (Theorem 2 says 0)",
        f"  lower line z ≈ 3.232x: {int(lo.sum()):4d}  ({lo.mean():.1%})",
        f"  upper line z = 6x − d: {int(hi.sum()):4d}  ({hi.mean():.1%})   d ∈ "
        f"{sorted(set((6 * xs[hi] - zs[hi]).tolist()))}",
        f"  all three equal      : {int(eq.sum()):4d}   x = {xs[eq].tolist()}",
        f"  ratios seen in [1.0, 1.5) ∪ (4.0, 5.0): "
        f"{int(((r > 1.0) & (r < 1.5) | (r > 4.0) & (r < 5.0)).sum())}   (the gaps are empty)",
    ]
    return fig, "\n".join(summary), missing


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--max-x", type=int, default=800, help="largest repeated pile (default 800)")
    p.add_argument("--dark", action="store_true")
    p.add_argument("--out", default="equal_pairs", help="HTML name under plots/")
    p.add_argument("--no-open", action="store_true")
    a = p.parse_args()

    # Width has to clear the upper line at 6x, with headroom -- see the truncation guard above.
    loser_y = load(a.max_x + 1, int(6.5 * a.max_x) + 50)
    fig, summary, missing = build(loser_y, a.max_x, dark=a.dark)
    print(summary)
    if missing:
        raise SystemExit(f"\n{len(missing)} of {a.max_x} x have no partner in this cache "
                         f"(first: {missing[:5]}) — the grid is too narrow, widen it and re-run.")

    PLOTS.mkdir(exist_ok=True)
    out = PLOTS / f"{a.out}.html"
    fig.write_html(out, include_plotlyjs="cdn",
                   config=dict(scrollZoom=True, displaylogo=False,
                               toImageButtonOptions=dict(format="png", scale=2)))
    print(f"\nwrote {out}")
    if not a.no_open:
        webbrowser.open(out.resolve().as_uri())


if __name__ == "__main__":
    main()
