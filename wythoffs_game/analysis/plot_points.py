"""Desmos-style viewer for bounded-Wythoff losers: WebGL scatter, one toggleable trace per
x-level, overlaid lines, and saveable sessions.

Points come from the cache in ``store.py``, so a grid is generated at most once no matter how
many times you re-plot it. Rendering is Plotly's ``Scattergl`` (WebGL), which pans and zooms
smoothly at the point counts that make Desmos crawl.

Reading the plot:

* Click a level in the legend to toggle it; double-click one to isolate it. A level's dots and
  its fitted lines share a legend entry, so they toggle together.
* Each sheet's losers hug two lines -- an upper one of slope 1+sqrt(3) and its mirror across
  y=z -- but only outside a chaotic core roughly 25x wide. ``--fit`` draws those two lines with
  the slope fixed at 1+sqrt(3) and the intercept fitted past the core, so the line you see is
  the real asymptote rather than an eyeballed one.

A **session** is a JSON file holding the levels, grid size, lines and view -- the Desmos-account
part. Save one with ``--save <name>``, reopen it with ``--session <name>``, and edit the JSON by
hand to add lines.

Usage:
    python -m wythoffs_game.analysis.plot_points --levels 0,10,25,50 --size 8000 --fit
    python -m wythoffs_game.analysis.plot_points --levels 0-40 --size 20000 --save wide
    python -m wythoffs_game.analysis.plot_points --session wide
    python -m wythoffs_game.analysis.plot_points --list
"""

import argparse
import json
import math
import webbrowser
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

from .store import load, sheet_points

HERE = Path(__file__).parent
SESSIONS = HERE / "sessions"
PLOTS = HERE / "plots"

M = 1 + math.sqrt(3)  # asymptotic slope of the upper line, on every sheet

# Up to 8 levels get distinct hues, in this fixed order (chosen so that neighbouring hues stay
# apart under colorblindness) -- with a handful of levels on screen you are comparing them as
# identities, not reading a gradient. Past 8 hues that stops working, so a longer selection
# falls back to a single blue ramp light -> dark, which is the honest encoding for an ordered
# quantity anyway. Each ramp/palette is stepped for its own surface, never flipped.
CAT_LIGHT = ["#2a78d6", "#1baf7a", "#eda100", "#008300",
             "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"]
CAT_DARK = ["#3987e5", "#199e70", "#c98500", "#008300",
            "#9085e9", "#e66767", "#d55181", "#d95926"]
RAMP_LIGHT = ["#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6",
              "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
RAMP_DARK = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec",
             "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab"]
THEME = {
    False: dict(surface="#fcfcfb", ink="#0b0b0b", muted="#52514e", grid="#eceae6",
                axis="#3d3c39", ramp=RAMP_LIGHT, cat=CAT_LIGHT),
    True: dict(surface="#1a1a19", ink="#ffffff", muted="#c3c2b7", grid="#2f2f2d",
               axis="#8f8e86", ramp=RAMP_DARK, cat=CAT_DARK),
}


def level_color(i, n, t):
    """Color for the i-th of n selected levels: a distinct hue if few, else a step of the ramp."""
    if n <= len(t["cat"]):
        return t["cat"][i]
    ramp = t["ramp"]
    return ramp[round(i * (len(ramp) - 1) / (n - 1))]


def parse_levels(spec):
    """``"0,4,10-14"`` -> ``[0, 4, 10, 11, 12, 13, 14]``."""
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-")
            out.extend(range(int(lo), int(hi) + 1))
        elif part:
            out.append(int(part))
    return sorted(set(out))


def parse_number(v):
    """Numbers, or arithmetic like ``"1+sqrt(3)"`` -- so sessions can hold exact slopes."""
    if isinstance(v, (int, float)):
        return float(v)
    ns = {k: getattr(math, k) for k in ("sqrt", "pi", "e", "cos", "sin", "log")}
    return float(eval(v, {"__builtins__": {}}, ns))


def fit_intercept(y, z, x):
    """Fit sheet ``x``'s upper asymptote: ``(intercept, measured_slope, core)`` or None.

    The slope is *fixed* at 1+sqrt(3); only the intercept is fitted, as the median of
    ``z - M*y`` over the settled tail (past the ~25x-wide core, where the dots have stopped
    being bumped). Returns None if the grid is too small for the sheet to have settled --
    better no line than a wrong one.
    """
    up = z > y
    a, b = y[up].astype(float), z[up].astype(float)
    if a.size < 20:
        return None
    core = 25 * x + 150
    lo = max(core, 0.5 * a.max())
    tail = a >= lo
    if tail.sum() < 20:
        return None
    at, bt = a[tail], b[tail]
    return (float(np.median(bt - M * at)), float(np.polyfit(at, bt, 1)[0]), core)


def fit_alpha(fits):
    """The single constant ``alpha`` in the model ``c(x) = alpha * x``.

    Least squares *through the origin* over the fitted per-sheet intercepts, so the x=0 line
    passes through (0, 0) by construction. Measures ~5.04 over levels 0..40.
    """
    xs = np.array([x for x, _ in fits], dtype=float)
    cs = np.array([c for _, c in fits], dtype=float)
    if not xs.any():
        return 0.0
    return float((xs * cs).sum() / (xs * xs).sum())


def sheet_lines(x, c, size, note):
    """Sheet ``x``'s upper asymptote and its mirror, as ``(slope, intercept, note)`` pairs.

    Both are drawn across the whole grid, core included. Inside the core the dots visibly
    leave the line -- that divergence *is* the phenomenon, so the line has to be there to
    measure it against.
    """
    return [
        (M, c, note),
        (1 / M, -c / M, "mirror of the above, across y = z"),  # reflect z = M*y + c in y = z
    ]


def build_residual(levels, size, pts, fits, alpha, t, view, title):
    """Plot each sheet's *residual* r = z - (M*y + c) against y, instead of z against y.

    Once the dots have settled they merge into a band that lies on the line, and at that zoom
    no styling can show both -- they occupy the same pixels. This view solves that by
    subtracting the line off: a perfect fit is a flat run at r = 0, so the vertical axis is
    "how far off the line is this dot", readable at any zoom.

    It also makes the mechanism visible. Every bump is a single cell, so a collision shows up
    as a +1 step in r. Near the origin the steps come thick and fast (the core); further out
    they stop and r goes flat -- that is the sheet escaping its lower neighbours' blocking
    strips for good. Only the upper branch is plotted; the loser set is symmetric in y and z,
    so the lower branch is the same points reflected and carries no new information.
    """
    fig = go.Figure()
    for i, x in enumerate(levels):
        if x not in fits:
            continue
        color = level_color(i, len(levels), t)
        y, z = pts[x]
        up = z > y
        a, b = y[up].astype(float), z[up].astype(float)
        c = alpha * x if alpha is not None else fits[x][0]
        fig.add_trace(go.Scattergl(
            x=a, y=b - M * a - c, mode="markers", name=f"x = {x}",
            marker=dict(size=4, color=color, line=dict(width=0)),
            hovertemplate="y = %{x}<br>off the line by %{y:.2f}<extra>x = " + str(x) + "</extra>",
        ))

    model = f"c(x) = {alpha:.3f}·x" if alpha is not None else "each sheet's own fitted c"
    fig.update_layout(
        title=dict(text=title or f"Distance from the line:  r = z − (1+√3)·y − c(x)"
                                 f"     [{model}]",
                   font=dict(color=t["ink"], size=15)),
        paper_bgcolor=t["surface"], plot_bgcolor=t["surface"],
        font=dict(color=t["muted"], size=12),
        legend=dict(title=dict(text="x-level"), itemsizing="constant", bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=70, r=20, t=60, b=60), hovermode="closest", dragmode="pan",
    )
    axis = dict(title_font=dict(color=t["ink"], size=15), tickfont=dict(color=t["muted"]),
                gridcolor=t["grid"], zeroline=True, zerolinecolor=t["axis"], zerolinewidth=2,
                linecolor=t["axis"], linewidth=2, mirror=True,
                ticks="outside", tickcolor=t["axis"], ticklen=6, showspikes=False)
    rng = view or {}
    # The zero line IS the fitted asymptote. Flat run on it = the dots are exactly on the line.
    fig.update_xaxes(title_text="y  (along the upper branch)", range=rng.get("x", [0, size]), **axis)
    fig.update_yaxes(title_text="r  =  cells above the line", range=rng.get("y"), **axis)
    return fig


def build(levels, size, dark=False, fit=False, alpha=None, residual=False,
          lines=(), view=None, title=None):
    """``fit`` draws each sheet's asymptote + mirror. ``alpha`` picks how the intercept is set:
    None = each sheet's own fitted intercept; a float = the model c(x) = alpha*x; "auto" =
    that model with alpha fitted through the origin across the selected sheets. ``residual``
    plots distance-from-the-line instead of the raw dots."""
    t = THEME[dark]
    loser_y = load(max(levels) + 1, size)
    total = 0

    pts = {x: sheet_points(loser_y, x) for x in levels}
    fits = {}       # x -> (fitted intercept, measured slope, core width)
    if fit:
        for x in levels:
            f = fit_intercept(*pts[x], x)
            if f:
                fits[x] = f
        if alpha == "auto":
            alpha = fit_alpha([(x, f[0]) for x, f in fits.items()])

    if residual:
        return build_residual(levels, size, pts, fits, alpha, t, view, title)

    # Traces render in the order they are added. Dots go in first and lines last, so a line
    # stays visible where its dots merge into a solid band.
    under, dots, over = [], [], []

    # The mirror axis, to orient by: each sheet's two branches are reflections across it.
    under.append(go.Scattergl(
        x=[0, size], y=[0, size], mode="lines", name="y = z (mirror axis)",
        legendrank=1, line=dict(color=t["muted"], width=1),
        opacity=0.5, hoverinfo="skip",
    ))

    for i, x in enumerate(levels):
        color = level_color(i, len(levels), t)
        y, z = pts[x]
        total += len(y)
        group = f"x{x}"
        dots.append(go.Scattergl(
            x=y, y=z, mode="markers", name=f"x = {x}  ({len(y):,})",
            legendgroup=group, legendrank=100 + i,
            marker=dict(size=5, color=color, line=dict(width=0)),
            hovertemplate="(%{x}, %{y})<extra>x = " + str(x) + "</extra>",
        ))
        if x not in fits:
            continue

        c_fit, emp, core = fits[x]
        if alpha is None:
            c, note = c_fit, f"intercept fitted on this sheet (past its core, y>={core})"
        else:
            c = alpha * x
            note = (f"intercept from the model c(x) = {alpha:.3f}·x "
                    f"(this sheet measures {c_fit:.1f}, so the model is off by {c - c_fit:+.1f})")
        note += f"<br>slope measured past the core: {emp:.3f}   (1+√3 = {M:.3f})"

        for m, cc, extra in sheet_lines(x, c, size, note):
            over.append(go.Scattergl(
                x=[0, size], y=[cc, m * size + cc], mode="lines",
                legendgroup=group, showlegend=False,
                # A 1px hairline in ink, on top of the dots -- not the level's own color, which
                # would vanish into its own dot band the moment you zoom out far enough for the
                # dots to merge. Solid, never dashed: a dash pattern crawls as you pan.
                line=dict(color=t["ink"], width=1), opacity=0.75,
                hovertemplate=f"z = {m:.4f} y + {cc:.1f}<br>{extra}<br>{note}<extra>x = {x}</extra>",
            ))

    for j, spec in enumerate(lines):
        m = parse_number(spec.get("slope", 0))
        c = parse_number(spec.get("intercept", 0))
        label = spec.get("label") or f"z = {m:.4f} y + {c:.1f}"
        under.append(go.Scattergl(
            x=[0, size], y=[c, m * size + c], mode="lines", name=label,
            legendrank=10 + j,
            line=dict(color=spec.get("color", t["muted"]), width=2), opacity=0.6,
            hovertemplate=f"z = {m:.4f} y + {c:.1f}<extra>{label}</extra>",
        ))

    fig = go.Figure(under + dots + over)

    if total > 600_000:
        print(f"warning: {total:,} points -- pans may stutter. Fewer levels, or a smaller "
              f"--size, will stay smooth.")

    rng = view or dict(x=[0, size], y=[0, size])
    fig.update_layout(
        title=dict(text=title or f"Bounded Wythoff losers — {total:,} points",
                   font=dict(color=t["ink"], size=16)),
        paper_bgcolor=t["surface"], plot_bgcolor=t["surface"],
        font=dict(color=t["muted"], size=12),
        legend=dict(title=dict(text="x-level"), itemsizing="constant",
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=70, r=20, t=50, b=60),
        hovermode="closest", dragmode="pan",
    )
    # A boxed frame with heavy zero lines. No hover spikes: crosshairs tracking the cursor are
    # more distracting than useful here.
    axis = dict(
        title_font=dict(color=t["ink"], size=15),
        tickfont=dict(color=t["muted"]),
        gridcolor=t["grid"], griddash="solid",
        zeroline=True, zerolinecolor=t["axis"], zerolinewidth=2,
        linecolor=t["axis"], linewidth=2, mirror=True,
        ticks="outside", tickcolor=t["axis"], ticklen=6,
        showspikes=False,
        constrain="domain",
    )
    fig.update_xaxes(title_text="y  (pile 2)", range=rng["x"], **axis)
    # Equal aspect: a slope of 2.73 only looks like 2.73 if one unit of y is one unit of z.
    fig.update_yaxes(title_text="z  (pile 3)", range=rng["y"],
                     scaleanchor="x", scaleratio=1, **axis)
    return fig


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--levels", help="e.g. 0,10,25 or 0-40")
    p.add_argument("--size", type=int, help="grid size (y and z run 0..size-1)")
    p.add_argument("--fit", action="store_true", help="draw each level's asymptote + mirror")
    p.add_argument("--alpha", nargs="?", const="auto", default=None, metavar="A",
                   help="use the model c(x) = alpha*x for the intercepts instead of each "
                        "sheet's own fit, so the x=0 line passes exactly through (0,0). "
                        "Bare --alpha fits alpha through the origin (~5.04); --alpha 5 pins it.")
    p.add_argument("--residual", action="store_true",
                   help="plot distance from the fitted line instead of the raw dots -- the way "
                        "to judge the fit once the dots merge into the line. Implies --fit.")
    p.add_argument("--dark", action="store_true")
    p.add_argument("--session", help="load a saved session by name")
    p.add_argument("--save", help="save this graph as a session")
    p.add_argument("--list", action="store_true", help="list saved sessions")
    p.add_argument("--no-open", action="store_true")
    a = p.parse_args()

    SESSIONS.mkdir(exist_ok=True)
    PLOTS.mkdir(exist_ok=True)

    if a.list:
        for f in sorted(SESSIONS.glob("*.json")):
            s = json.loads(f.read_text())
            print(f"{f.stem:20s} levels={s['levels']}  size={s['size']}  "
                  f"lines={len(s.get('lines', []))}")
        return

    s = {}
    if a.session:
        f = SESSIONS / f"{a.session}.json"
        if not f.exists():
            raise SystemExit(f"no session {a.session!r} (try --list)")
        s = json.loads(f.read_text())

    # Command-line flags override whatever the session holds.
    levels = parse_levels(a.levels) if a.levels else s.get("levels")
    size = a.size or s.get("size")
    if not levels or not size:
        raise SystemExit("need --levels and --size (or a --session that has them)")
    alpha = a.alpha if a.alpha is not None else s.get("alpha")
    if alpha is not None and alpha != "auto":
        alpha = float(alpha)
    resid = a.residual or s.get("residual", False)
    s = dict(s, levels=levels, size=size, alpha=alpha, residual=resid,
             fit=a.fit or resid or s.get("fit", False),
             dark=a.dark or s.get("dark", False))

    fig = build(levels, size, dark=s["dark"], fit=s["fit"], alpha=alpha, residual=resid,
                lines=s.get("lines", []), view=s.get("view"), title=s.get("title"))

    name = a.save or a.session or "plot"
    if a.save:
        (SESSIONS / f"{a.save}.json").write_text(json.dumps(s, indent=2))
        print(f"saved session {a.save!r}")

    out = PLOTS / f"{name}.html"
    fig.write_html(out, include_plotlyjs="cdn",
                   config=dict(scrollZoom=True, displaylogo=False,
                               modeBarButtonsToAdd=["drawline", "eraseshape"],
                               toImageButtonOptions=dict(format="png", scale=2)))
    print(f"wrote {out}")
    if not a.no_open:
        webbrowser.open(out.resolve().as_uri())


if __name__ == "__main__":
    main()
