"""Desmos-style viewer for bounded-Wythoff losers: WebGL scatter, one toggleable trace per
x-level, overlaid lines, and saveable sessions.

Points come from the cache in ``store.py``, so a grid is generated at most once no matter how
many times you re-plot it. Rendering is Plotly's ``Scattergl`` (WebGL), which pans and zooms
smoothly at the point counts that make Desmos crawl. The result is written to ``plots/<name>.html``
and opened in your browser (pass ``--no-open`` to just write it).

------------------------------------------------------------------------------------------------
QUICK START
------------------------------------------------------------------------------------------------
Pick which x-levels to show and how big a grid, and go:

    python -m wythoffs_game.analysis.plot_points --levels 0,10,25,50 --size 8000

``--levels`` takes a comma list and/or ranges: ``0,10,25`` or ``0-40`` or ``0,5,10-14``.
``--size`` is the grid width; y and z both run 0..size-1. Losers never move as the grid grows,
so a bigger --size just reveals more of the same picture (and reuses the same cache file).

RULE OF THUMB FOR --size: sheet x doesn't settle onto its asymptote until about y = 50*x, and
the transient "core" near the origin is about 25*x wide. So to actually SEE sheet 50's slope you
need --size ~ 8000+, not 400. Too small a window and a sheet looks steeper than it is -- that is
a window artifact, not a real slope. When in doubt, go bigger; the cache makes re-plots cheap.

------------------------------------------------------------------------------------------------
THE VIEWS
------------------------------------------------------------------------------------------------
1. RAW (default): z vs y, one colored trace of dots per level, equal aspect (so a slope of 2.73
   looks like 2.73). Add ``--fit`` to overlay each sheet's asymptote + its mirror.

2. RESIDUAL (``--residual``, implies --fit): plots r = z - (1+sqrt(3))*y - c instead of z vs y,
   i.e. "how far each dot sits above/below the fitted line." A perfect fit is a flat run at r=0.
   This is the view for judging the fit once the dots have merged into the line at zoom-out, and
   for watching collisions: each collision is a +1 step in r; steps come thick near the origin
   (the core) then stop and r goes flat (the sheet has escaped its lower neighbours for good).

3. INTERCEPTS (``--intercepts``, implies --fit): plots each sheet's line-intercept c(x) against x
   -- one point per level. The DOTS are c(x) measured per sheet (what you get without --alpha);
   the LINE is the single-constant model c(x)=alpha*x (what --alpha imposes). Dots hugging the
   line = one alpha fits every sheet; dots drifting off it = the single-alpha story is incomplete.
   (``--edge`` optionally overlays the y=0 edge dot, a separate quantity -- see below.)

4. SLOPE (``--slope``): plots each sheet's *local* slope against y, so you can watch it settle
   onto 1+sqrt(3). A sheet reads steeper than 1+sqrt(3) near the origin only because that window
   is still in the core; move out and the curve drops onto the dashed 1+sqrt(3) reference.

5. SLIDER (``--slider``): the raw z-vs-y plot, but with a slider under the plot that shows ONE
   sheet at a time instead of stacking every level at once. Drag it to flip between consecutive
   x in place -- the axes stay fixed, so it reads like a flip-book and what moves vs. stays put
   between neighbouring sheets is obvious. Respects ``--fit`` (each sheet's asymptote + mirror
   ride along) and ``--dark``. This is the view for hunting a pattern across many levels: build
   ``--levels 0-1000`` once and slide, rather than plotting a thousand overlapping traces.

Any view honours ``--dark`` (dark theme) and ``--no-open`` (just write the HTML, don't open it).

------------------------------------------------------------------------------------------------
TWO PILES THE SAME SIZE  (``--equal``)
------------------------------------------------------------------------------------------------
``--equal`` re-colors the losers whose triple has two equal piles. A dot at (y, z) on sheet x is
the triple {x, y, z}, so those are exactly the dots on the sheet's three special lines:

    y = x  or  z = x     x is the repeated pile      -- the triple is (x, x, other)
    y = z                x is the odd pile out       -- the triple is (x, other, other)

A sheet carries at most three of them, which is why they are invisible without a highlight. They
come out as big diamonds drawn on top of every level's dots, with one legend entry for the whole
family (toggle it to show/hide them all). Bare ``--equal`` uses high-contrast ink (black on the
light theme, white on dark); ``--equal magenta`` or ``--equal "#e34948"`` sets your own color.
Works on the raw view and on ``--slider``, and is saved with a ``--save``d session.

    python -m wythoffs_game.analysis.plot_points --levels 0-40 --size 8000 --equal
    python -m wythoffs_game.analysis.plot_points --levels 0-400 --size 3300 --slider --equal red

------------------------------------------------------------------------------------------------
HOW THE FITTED LINE IS CHOSEN  (this is automatic; nothing is eyeballed)
------------------------------------------------------------------------------------------------
The SLOPE is not fitted -- it is pinned to the theoretical value M = 1+sqrt(3) ~ 2.732. (The code
also *measures* the slope by least squares past the core and shows it in the hover text, purely so
you can see how close the data is; that measured number is never used to draw the line.)

The INTERCEPT is fitted as the median of z - M*y over the "settled tail" of the sheet: upper-branch
dots (z>y) with y past the core (y >= max(25*x+150, half the widest y present)). Median, not mean,
so a few late collisions don't drag the line. If the grid is too short for the tail to have
settled (fewer than ~20 tail dots), no line is drawn for that sheet -- better none than a wrong one.

------------------------------------------------------------------------------------------------
--alpha vs no --alpha  (this is the one to keep straight)
------------------------------------------------------------------------------------------------
Both are about the SAME object: c(x), the intercept of sheet x's line (where its far line, run
back, crosses y=0). There is one c(x) per sheet. The flag only changes how it is set:

* NO --alpha: measure c(x) on each sheet independently, from that sheet's own tail. Every sheet
  is separate, so the intercepts come out wiggly (roughly 4.8x, 5.1x, 5.3x ...). Use this to SEE
  how the intercept actually behaves sheet by sheet.
* --alpha: don't measure each one -- assume they all obey a single law c(x) = alpha*x and use
  that one number for every sheet. This forces the intercepts onto one straight line through the
  origin. Use this to summarise all the intercepts by one constant.
      --alpha      fit that one alpha by least squares THROUGH THE ORIGIN over the sheets shown
                   (~5.04 on 0..40); the x=0 line then passes exactly through (0,0).
      --alpha 5    pin alpha to a value you choose.

So alpha is NOT a different intercept -- it is the single slope of the c-vs-x trend, the
intercept's analog of the slope 1+sqrt(3). "alpha ~ 5 while c(0) ~ 0" is not a contradiction:
alpha is the growth rate of the intercept, c(0) is where the x=0 sheet itself crosses the axis.
The professor's "which intercept?" is really this fork: the per-sheet function c(x) (no --alpha)
or the one constant alpha (--alpha).

The EDGE DOT is a separate thing -- the real loser sitting in column y=0 -- and is NOT the line's
intercept (the near-origin dots peel off the extrapolated line, so the two disagree). It is shown
only with --edge, purely for contrast.

------------------------------------------------------------------------------------------------
YOUR OWN LINES
------------------------------------------------------------------------------------------------
Drop a line straight onto the raw plot without editing any file:

    --line "SLOPE,INTERCEPT"            e.g.  --line "1+sqrt(3),40"
    --line "SLOPE,INTERCEPT,LABEL"      e.g.  --line "2.732,0,through origin"

Repeat --line for several. Slope/intercept accept arithmetic like ``1+sqrt(3)``. Lines from
--line are added on top of any a --session already carries.

On the --intercepts view the same --line is drawn on the intercept axes, i.e. as
``c = SLOPE*x + INTERCEPT`` (x = sheet level, c = intercept), so ``--line "1+sqrt(3),0"`` overlays
``c = (1+sqrt(3))*x`` to compare the measured per-sheet intercepts against that trend.

------------------------------------------------------------------------------------------------
SESSIONS  (the "Desmos account" part)
------------------------------------------------------------------------------------------------
A session is a JSON file (in ``sessions/``) holding levels, size, alpha, view, and your lines.

    --save NAME        write the current graph as a session
    --session NAME     reopen it (command-line flags override what the session stores)
    --list             list saved sessions
You can also edit a session's JSON by hand to curate its ``lines`` list.

------------------------------------------------------------------------------------------------
READING THE RAW PLOT
------------------------------------------------------------------------------------------------
* Click a level in the legend to toggle it; double-click one to isolate it. A level's dots and
  its fitted lines share a legend entry, so they toggle together.
* Each sheet's losers hug two lines -- an upper one of slope 1+sqrt(3) and its mirror across y=z
  -- but only outside the core. The faint diagonal is y=z, the mirror axis; the two branches of
  every sheet are reflections across it (the loser set is symmetric in y and z).

------------------------------------------------------------------------------------------------
EXAMPLES
------------------------------------------------------------------------------------------------
    python -m wythoffs_game.analysis.plot_points --levels 0,10,25,50 --size 8000 --fit
    python -m wythoffs_game.analysis.plot_points --levels 0-40 --size 20000 --residual --alpha
    python -m wythoffs_game.analysis.plot_points --levels 0-100 --size 36000 --intercepts          # dots = per-sheet c(x)
    python -m wythoffs_game.analysis.plot_points --levels 0-100 --size 36000 --intercepts --alpha  # + the one-alpha line
    python -m wythoffs_game.analysis.plot_points --levels 2,10,50 --size 8000 --slope
    python -m wythoffs_game.analysis.plot_points --levels 0-1000 --size 3300 --slider        # flip-book
    python -m wythoffs_game.analysis.plot_points --levels 2,10,50 --size 8000 --line "1+sqrt(3),0"
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

# Left/right arrow keys step the slider, so you can walk through sheets one x at a time without
# hunting for a 3-pixel handle with the mouse (holding the key repeats). Plotly gives sliders no
# keyboard handling of its own, and moving `sliders[0].active` does NOT re-run that step's update,
# so this applies the step's own args and then syncs the handle. Passed to write_html as
# post_script by every viewer that builds a slider; a no-op on figures that have none.
SLIDER_KEYS_JS = """
var gd = document.getElementById('{plot_id}');
if (gd) {
  document.addEventListener('keydown', function(e){
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') { return; }
    var sl = (gd.layout.sliders || [])[0];
    if (!sl || !sl.steps || !sl.steps.length) { return; }
    var i = (sl.active || 0) + (e.key === 'ArrowRight' ? 1 : -1);
    if (i < 0 || i > sl.steps.length - 1) { return; }
    e.preventDefault();
    var st = sl.steps[i];
    Plotly.update(gd, st.args[0] || {}, st.args[1] || {}).then(function(){
      Plotly.relayout(gd, {'sliders[0].active': i});
    });
  });
}
"""


def equal_mask(x, y, z):
    """Which dots on sheet ``x`` are losers whose triple has two piles the same size.

    The dot at ``(y, z)`` is the triple ``{x, y, z}``, so "two piles equal" is just "the dot
    sits on one of the sheet's three special lines": ``y = x`` or ``z = x`` (x is the repeated
    pile, the triple is ``(x, x, other)``) or ``y = z`` (x is the odd pile out, the triple is
    ``(x, other, other)``). A sheet carries at most three such dots, which is why they need
    their own color to be findable at all.
    """
    return (y == z) | (y == x) | (z == x)


def level_color(i, n, t):
    """Color for the i-th of n selected levels: a distinct hue if few, else a step of the ramp."""
    if n <= len(t["cat"]):
        return t["cat"][i]
    ramp = t["ramp"]
    return ramp[round(i * (len(ramp) - 1) / (n - 1))]


def equal_color(equal, t):
    """Resolve ``--equal``'s value to a color: ``"auto"`` -> the theme's ink, else as given.

    Ink rather than another hue on purpose. The level colors already span the categorical
    palette (and past 8 levels the whole blue ramp), so any hue picked here would collide with
    *some* selection; black-on-light / white-on-dark collides with none of them. Pass a color to
    --equal to override it.
    """
    return t["ink"] if equal == "auto" else equal


def equal_trace(sheet, y, z, color, t, **kw):
    """The "two piles equal" highlight: big ringed diamonds, drawn on top of every level's dots.

    ``sheet`` is the x each dot came from, carried as customdata so the hover can name the whole
    triple. The diamond symbol and the size bump mean the family is still identifiable if the
    color is changed to something near a level's hue -- identity never rests on hue alone.
    """
    return go.Scattergl(
        x=y, y=z, mode="markers", name=f"two piles equal  ({len(y):,})",
        marker=dict(size=10, color=color, symbol="diamond",
                    line=dict(width=1.5, color=t["surface"])),
        customdata=sheet,
        hovertemplate="(%{customdata}, %{x}, %{y})<extra>two piles equal</extra>",
        **kw,
    )


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


def parse_line(spec):
    """``"1+sqrt(3),40"`` or ``"2.732,0,through origin"`` -> a lines-list dict.

    Slope and intercept go through ``parse_number`` (so arithmetic like ``1+sqrt(3)`` works); an
    optional third field is the legend label.
    """
    parts = [p.strip() for p in spec.split(",")]
    if len(parts) < 2:
        raise SystemExit(f"--line needs 'slope,intercept[,label]', got {spec!r}")
    out = {"slope": parts[0], "intercept": parts[1]}
    if len(parts) >= 3 and parts[2]:
        out["label"] = parts[2]
    return out


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


def build_intercepts(levels, size, pts, fits, alpha, t, view, title, show_edge=False, lines=()):
    """Plot each sheet's line-intercept against x -- the "intercept graph".

    This view is about ONE object, c(x) = the intercept of sheet x's asymptote line (where the
    settled far line, slope 1+sqrt(3), run back, crosses y=0), and the two ways of setting it:

    * DOTS = c(x) measured on each sheet independently, from that sheet's own tail. This is what
      you get WITHOUT --alpha: every sheet keeps its own fitted intercept, so the dots come out
      wiggly (~4.8x, 5.1x, 5.3x ...).
    * LINE = the single-constant model c(x) = alpha*x, a straight line through the origin. This
      is what --alpha imposes: all the intercepts collapsed onto one slope alpha (fitted, ~5, or
      pinned with --alpha 5).

    So the dots are "no --alpha" and the line is "--alpha", side by side: if the dots hug the
    line, one alpha summarises every sheet (alpha exists); if they drift or step off it, the
    single-alpha story is incomplete. That drift IS the open question.

    ``show_edge`` optionally overlays the edge dot (the real loser in column y=0, the Fraenkel
    partner). It is a DIFFERENT quantity from c(x) -- not the line's intercept -- shown only for
    contrast, off by default.
    """
    fig = go.Figure()
    xs = np.array(sorted(fits), dtype=float)
    cs = np.array([fits[int(x)][0] for x in xs])

    xmax = xs.max() if xs.size else max(levels)
    if alpha is not None:
        xline = np.array([0.0, xmax])
        fig.add_trace(go.Scattergl(
            x=xline, y=alpha * xline, mode="lines",
            name=f"--alpha model:  c = {alpha:.3f}·x  (one constant)",
            line=dict(color=t["muted"], width=2, dash="dash"), opacity=0.9,
            hovertemplate="c = %{y:.1f} at x = %{x}<extra>alpha model</extra>",
        ))
    fig.add_trace(go.Scattergl(
        x=xs, y=cs, mode="markers+lines",
        name="no --alpha:  c(x) measured per sheet",
        marker=dict(size=7, color=t["cat"][0], line=dict(width=0)),
        line=dict(color=t["cat"][0], width=1),
        hovertemplate="x = %{x}<br>c(x) = %{y:.2f}<extra>per-sheet intercept</extra>",
    ))
    if show_edge:
        ex, ez = [], []
        for x in levels:
            y, z = pts[x]
            e = z[y == 0]
            if e.size:
                ex.append(x)
                ez.append(int(e.min()))
        if ex:
            fig.add_trace(go.Scattergl(
                x=ex, y=ez, mode="markers",
                name="edge dot (separate: real y=0 loser, NOT the line's intercept)",
                marker=dict(size=7, color=t["cat"][5], symbol="diamond-open", line=dict(width=1.5)),
                hovertemplate="x = %{x}<br>edge z = %{y}<extra>column y=0 loser</extra>",
            ))

    # Your own comparison lines, over the x-axis (sheet level). A line "SLOPE,INTERCEPT" is drawn
    # as c = SLOPE*x + INTERCEPT, so e.g. --line "1+sqrt(3),0" overlays c = (1+√3)·x to compare
    # the measured intercepts against that trend.
    for spec in lines:
        m = parse_number(spec.get("slope", 0))
        b = parse_number(spec.get("intercept", 0))
        label = spec.get("label") or f"c = {m:.4f}·x + {b:.1f}"
        xline = np.array([0.0, xmax])
        fig.add_trace(go.Scattergl(
            x=xline, y=m * xline + b, mode="lines", name=label,
            line=dict(color=spec.get("color", t["cat"][2]), width=2), opacity=0.8,
            hovertemplate=f"c = {m:.4f}·x + {b:.1f}<extra>{label}</extra>",
        ))

    fig.update_layout(
        title=dict(text=title or "Intercept vs x:  each sheet's line-intercept c(x)  "
                                 "(dots = per sheet, line = one α)",
                   font=dict(color=t["ink"], size=15)),
        paper_bgcolor=t["surface"], plot_bgcolor=t["surface"],
        font=dict(color=t["muted"], size=12),
        legend=dict(itemsizing="constant", bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=70, r=20, t=60, b=60), hovermode="closest", dragmode="pan",
    )
    axis = dict(title_font=dict(color=t["ink"], size=15), tickfont=dict(color=t["muted"]),
                gridcolor=t["grid"], zeroline=True, zerolinecolor=t["axis"], zerolinewidth=2,
                linecolor=t["axis"], linewidth=2, mirror=True,
                ticks="outside", tickcolor=t["axis"], ticklen=6, showspikes=False)
    rng = view or {}
    fig.update_xaxes(title_text="x  (sheet / pile 1)", range=rng.get("x"), **axis)
    fig.update_yaxes(title_text="intercept  (z where the line meets y = 0)",
                     range=rng.get("y"), **axis)
    return fig


def build_slope(levels, size, pts, t, view, title):
    """Plot each sheet's *local* slope against y -- how the slope settles onto 1+sqrt(3).

    For a fixed sheet, the upper-branch dots are sorted by y and a straight line is fitted in a
    sliding window; the window's fitted slope is plotted at its centre y. Near the origin the
    slope reads high (a sheet-50 window at y<200 measures ~3.2); moving out it drops and flattens
    onto the dashed 1+sqrt(3) reference. This is the picture that shows a too-small window is why
    a sheet ever *looks* steeper than 1+sqrt(3) -- it is the core, not a real slope difference.
    """
    fig = go.Figure()
    fig.add_hline(y=M, line=dict(color=t["axis"], width=2, dash="dash"),
                  annotation_text=f"1+√3 = {M:.4f}", annotation_position="top right",
                  annotation_font_color=t["ink"])
    for i, x in enumerate(levels):
        y, z = pts[x]
        up = z > y
        a, b = y[up].astype(float), z[up].astype(float)
        o = np.argsort(a)
        a, b = a[o], b[o]
        n = a.size
        if n < 60:
            continue
        # A window of ~n/40 points (>=40), stepped by half its width: enough dots for a stable
        # slope, fine enough to trace the settling. Windows are in point-count, so they auto-widen
        # in y where dots thin out.
        w = max(40, n // 40)
        step = max(1, w // 2)
        yy, ss = [], []
        for j in range(0, n - w, step):
            aw, bw = a[j:j + w], b[j:j + w]
            yy.append(float(aw[w // 2]))
            ss.append(float(np.polyfit(aw, bw, 1)[0]))
        fig.add_trace(go.Scattergl(
            x=yy, y=ss, mode="lines", name=f"x = {x}",
            line=dict(color=level_color(i, len(levels), t), width=2),
            hovertemplate="y ≈ %{x:.0f}<br>local slope = %{y:.3f}<extra>x = " + str(x) + "</extra>",
        ))

    fig.update_layout(
        title=dict(text=title or "Local slope vs y:  each sheet settling onto 1+√3",
                   font=dict(color=t["ink"], size=15)),
        paper_bgcolor=t["surface"], plot_bgcolor=t["surface"],
        font=dict(color=t["muted"], size=12),
        legend=dict(title=dict(text="x-level"), itemsizing="constant", bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=70, r=20, t=60, b=60), hovermode="closest", dragmode="pan",
    )
    axis = dict(title_font=dict(color=t["ink"], size=15), tickfont=dict(color=t["muted"]),
                gridcolor=t["grid"], zeroline=False,
                linecolor=t["axis"], linewidth=2, mirror=True,
                ticks="outside", tickcolor=t["axis"], ticklen=6, showspikes=False)
    rng = view or {}
    fig.update_xaxes(title_text="y  (distance out along the branch)", range=rng.get("x"), **axis)
    # Clamp the default y-window around 1+√3 so the settling is readable; the steep near-origin
    # windows can run off the top, which is fine -- pan up to see them.
    fig.update_yaxes(title_text="local slope", range=rng.get("y", [2.4, 3.4]), **axis)
    return fig


def build_slider(levels, size, pts, fits, alpha, t, view, title, equal=None):
    """Raw z-vs-y plot with a slider that steps through one sheet at a time.

    Same dots and fitted lines as the raw view, but instead of stacking every selected level on
    screen at once, each slider position shows a single sheet (its dots plus its asymptote +
    mirror if --fit). Slide to flip between consecutive sheets in place -- the fixed axes make it
    a flip-book, so what stays put vs. what shifts between neighbouring x is read straight off.

    The y=z mirror axis stays visible at every step; only the per-sheet traces toggle.
    """
    fig = go.Figure()

    # Trace 0: the mirror axis, always visible.
    fig.add_trace(go.Scattergl(
        x=[0, size], y=[0, size], mode="lines", name="y = z (mirror axis)",
        line=dict(color=t["muted"], width=1), opacity=0.5, hoverinfo="skip",
    ))

    # For each level, remember which trace indices belong to it, so a slider step can show just
    # those. Dots first, then its two fitted lines.
    owned = []
    hi = equal_color(equal, t) if equal else None
    for i, x in enumerate(levels):
        idx = []
        color = level_color(i, len(levels), t)
        y, z = pts[x]
        idx.append(len(fig.data))
        fig.add_trace(go.Scattergl(
            x=y, y=z, mode="markers", name=f"x = {x}  ({len(y):,})", visible=(i == 0),
            marker=dict(size=5, color=color, line=dict(width=0)),
            hovertemplate="(%{x}, %{y})<extra>x = " + str(x) + "</extra>",
        ))
        if hi:
            m = equal_mask(x, y, z)
            idx.append(len(fig.data))
            fig.add_trace(equal_trace(np.full(int(m.sum()), x), y[m], z[m], hi, t,
                                      visible=(i == 0)))
        if x in fits:
            c_fit, emp, _core = fits[x]
            c = c_fit if alpha is None else alpha * x
            note = f"slope past core: {emp:.3f}   (1+√3 = {M:.3f})"
            for m, cc, extra in sheet_lines(x, c, size, note):
                idx.append(len(fig.data))
                fig.add_trace(go.Scattergl(
                    x=[0, size], y=[cc, m * size + cc], mode="lines", visible=(i == 0),
                    showlegend=False, line=dict(color=t["ink"], width=1), opacity=0.75,
                    hovertemplate=f"z = {m:.4f} y + {cc:.1f}<br>{extra}<extra>x = {x}</extra>",
                ))
        owned.append(idx)

    n_traces = len(fig.data)
    steps = []
    for i, x in enumerate(levels):
        vis = [False] * n_traces
        vis[0] = True                       # mirror axis always on
        for k in owned[i]:
            vis[k] = True
        steps.append(dict(method="update", label=str(x),
                          args=[{"visible": vis},
                                {"title.text": title or f"Bounded Wythoff losers — sheet x = {x}"}]))

    fig.update_layout(
        sliders=[dict(active=0, currentvalue=dict(prefix="x-level = ", font=dict(color=t["ink"])),
                      pad=dict(t=40), steps=steps,
                      font=dict(color=t["muted"]), bgcolor=t["grid"],
                      activebgcolor=t["axis"], bordercolor=t["axis"])],
        title=dict(text=title or f"Bounded Wythoff losers — sheet x = {levels[0]}",
                   font=dict(color=t["ink"], size=16)),
        paper_bgcolor=t["surface"], plot_bgcolor=t["surface"],
        font=dict(color=t["muted"], size=12),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=70, r=20, t=50, b=60), hovermode="closest", dragmode="pan",
    )
    axis = dict(title_font=dict(color=t["ink"], size=15), tickfont=dict(color=t["muted"]),
                gridcolor=t["grid"], zeroline=True, zerolinecolor=t["axis"], zerolinewidth=2,
                linecolor=t["axis"], linewidth=2, mirror=True,
                ticks="outside", tickcolor=t["axis"], ticklen=6, showspikes=False,
                constrain="domain")
    rng = view or dict(x=[0, size], y=[0, size])
    fig.update_xaxes(title_text="y  (pile 2)", range=rng["x"], **axis)
    fig.update_yaxes(title_text="z  (pile 3)", range=rng["y"],
                     scaleanchor="x", scaleratio=1, **axis)
    return fig


def build(levels, size, dark=False, fit=False, alpha=None, residual=False, intercepts=False,
          slope=False, edge=False, slider=False, lines=(), view=None, title=None, equal=None):
    """``fit`` draws each sheet's asymptote + mirror. ``alpha`` picks how the intercept is set:
    None = each sheet's own fitted intercept; a float = the model c(x) = alpha*x; "auto" =
    that model with alpha fitted through the origin across the selected sheets. ``residual``
    plots distance-from-the-line instead of the raw dots; ``intercepts`` plots the per-sheet
    intercept against x. ``equal`` re-colors the two-piles-equal losers (see ``equal_mask``):
    "auto" for the theme's ink, or any CSS color."""
    t = THEME[dark]
    loser_y = load(max(levels) + 1, size)
    total = 0

    pts = {x: sheet_points(loser_y, x) for x in levels}

    if slope:
        return build_slope(levels, size, pts, t, view, title)

    fits = {}       # x -> (fitted intercept, measured slope, core width)
    if fit:
        for x in levels:
            f = fit_intercept(*pts[x], x)
            if f:
                fits[x] = f
        if alpha == "auto":
            pairs = [(x, f[0]) for x, f in fits.items()]
            alpha = fit_alpha(pairs)
            # alpha is fitted over exactly these sheets, so it shifts with --levels and --size.
            # Print it so the value in use is never a mystery.
            print(f"alpha fitted through the origin over {len(pairs)} sheets "
                  f"(x up to {max(fits) if fits else 0}) = {alpha:.4f}")

    if slider:
        return build_slider(levels, size, pts, fits, alpha, t, view, title, equal=equal)
    if residual:
        return build_residual(levels, size, pts, fits, alpha, t, view, title)
    if intercepts:
        return build_intercepts(levels, size, pts, fits, alpha, t, view, title, show_edge=edge,
                                lines=lines)

    # Traces render in the order they are added. Dots go in first and lines last, so a line
    # stays visible where its dots merge into a solid band. The two-piles-equal highlights sit
    # between them -- above every level's dots (a highlight is never buried by a later sheet)
    # but under the fitted lines.
    under, dots, highs, over = [], [], [], []
    hi = equal_color(equal, t) if equal else None
    hi_x, hi_y, hi_z = [], [], []

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
        if hi:
            m = equal_mask(x, y, z)
            hi_x.append(np.full(int(m.sum()), x))
            hi_y.append(y[m])
            hi_z.append(z[m])
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

    # One trace for the whole family, not one per level: these are a handful of dots per sheet
    # and they read as a single population, so they get a single legend entry that toggles them
    # all at once.
    if hi and hi_y:
        highs.append(equal_trace(np.concatenate(hi_x), np.concatenate(hi_y),
                                 np.concatenate(hi_z), hi, t, legendrank=2))

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

    fig = go.Figure(under + dots + highs + over)

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
    p.add_argument("--intercepts", action="store_true",
                   help="plot each sheet's line-intercept c(x) against x: dots = measured per "
                        "sheet (no --alpha), line = the single-constant model (--alpha). Implies "
                        "--fit.")
    p.add_argument("--slope", action="store_true",
                   help="plot each sheet's local slope against y, to watch it settle onto 1+√3.")
    p.add_argument("--slider", action="store_true",
                   help="raw z-vs-y plot with a slider that steps through one sheet at a time "
                        "(a flip-book for comparing consecutive x). Respects --fit.")
    p.add_argument("--equal", nargs="?", const="auto", default=None, metavar="COLOR",
                   help="give the losers with two piles the same size their own color: the dots "
                        "on y=x, z=x (triple (x,x,other)) and y=z (triple (x,other,other)). Bare "
                        "--equal uses high-contrast ink; --equal \"#e34948\" or --equal magenta "
                        "picks your own. Works on the raw and --slider views.")
    p.add_argument("--edge", action="store_true",
                   help="on --intercepts, also overlay the y=0 edge dot (a separate quantity, "
                        "not the line's intercept).")
    p.add_argument("--line", action="append", default=[], metavar="SLOPE,INTERCEPT[,LABEL]",
                   help="drop a line on the raw plot, e.g. --line \"1+sqrt(3),40\". Repeatable; "
                        "slope/intercept accept arithmetic like 1+sqrt(3).")
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
    intercepts = a.intercepts or s.get("intercepts", False)
    slope = a.slope or s.get("slope", False)
    slider = a.slider or s.get("slider", False)
    edge = a.edge or s.get("edge", False)
    equal = a.equal if a.equal is not None else s.get("equal")
    # Lines from --line stack on top of whatever the session already carries.
    lines = list(s.get("lines", [])) + [parse_line(spec) for spec in a.line]
    s = dict(s, levels=levels, size=size, alpha=alpha, residual=resid, intercepts=intercepts,
             slope=slope, slider=slider, edge=edge, equal=equal, lines=lines,
             # --alpha is about the fitted lines' intercepts, so it needs the fit turned on.
             fit=a.fit or resid or intercepts or (alpha is not None) or s.get("fit", False),
             dark=a.dark or s.get("dark", False))

    fig = build(levels, size, dark=s["dark"], fit=s["fit"], alpha=alpha, residual=resid,
                intercepts=intercepts, slope=slope, slider=slider, edge=edge, equal=equal,
                lines=lines, view=s.get("view"), title=s.get("title"))

    name = a.save or a.session or "plot"
    if a.save:
        (SESSIONS / f"{a.save}.json").write_text(json.dumps(s, indent=2))
        print(f"saved session {a.save!r}")

    out = PLOTS / f"{name}.html"
    fig.write_html(out, include_plotlyjs="cdn",
                   config=dict(scrollZoom=True, displaylogo=False,
                               modeBarButtonsToAdd=["drawline", "eraseshape"],
                               toImageButtonOptions=dict(format="png", scale=2)),
                   post_script=SLIDER_KEYS_JS)
    print(f"wrote {out}")
    if not a.no_open:
        webbrowser.open(out.resolve().as_uri())


if __name__ == "__main__":
    main()
