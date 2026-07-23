"""Desmos-3D-style viewer for bounded-Wythoff losers: rotatable WebGL scatter of the whole
(x, y, z) loser cloud, one toggleable trace per x-level.

Where ``plot_points`` slices the space at a fixed x and draws one flat sheet, this stacks the
sheets back into 3D so you can rotate the loser cloud and see the surface it lives on. Each
level's dots sit in the plane x = level; together they trace out the symmetric loser surface
(sorted p<q<r, r ~ m*q + alpha*p). Rotate to look down the x-axis and you get the familiar
2D sheet picture back; rotate side-on and the near-origin "core" bulges off the surface.

Points come from the same ``store.py`` cache as ``plot_points`` (a grid is generated at most
once), and colors/level handling are shared with it, so the two viewers stay consistent.

3D WebGL stays smooth to ~100-200k points; past that it drags, so ``--max-points`` (default
150k) thins each level by uniform random sampling. Thinning only drops dots, never moves them.

Reading it:
* Drag to rotate (turntable: z stays up, so it never tumbles out of view), scroll to zoom
  toward the cursor (custom -- Plotly's own 3D scroll only zooms the fixed centre), right-drag
  to pan. To dive on the origin, point at it and scroll.
* ORIENTATION PRESETS: the buttons at the top-left snap the camera straight down an axis, so the
  cloud flattens to a clean plane -- ``y–z`` (down x, the plot_points sheet view), ``x–z`` (down
  y), ``x–y`` (down z), and ``reset`` (back to the three-quarter iso view). They only move the
  camera, so they compose with rotation, zoom, and the slider.
* ``--slider``: show one x-level at a time under a slider (a 3D flip-book), starting looking down
  the x-axis onto the y–z face -- drag it to step through consecutive sheets in place. Same idea
  as ``plot_points --slider``, but you can still rotate the sheet or hit a preset.
* Up to ~150 levels get one toggleable trace each: click a level in the legend to toggle it,
  double-click to isolate one. Past that, the whole cloud collapses into a single trace colored
  by x (a colorbar replaces the legend) -- thousands of separate traces + a giant legend make
  the page crawl, so the many-level view trades per-level toggling for smooth rotation.
* The three axes are stretched to a box, NOT drawn to a common scale. x spans only 0..40 while
  y and z run into the thousands, so a true-to-data aspect would flatten the whole stack into a
  wafer (and rotating a wafer edge-on makes it vanish). Instead each axis fills its own edge of
  the box, so the x-levels stand well apart. The trade-off: a slope you read straight off this
  cloud is NOT the true y:z slope -- for true ratios use the 2D ``plot_points`` viewer, which
  keeps equal aspect. ``--stretch`` controls how much depth the x-axis gets (thicker = levels
  further apart).

Sessions (same idea as ``plot_points``): a session is a JSON file (in ``sessions_3d/``) holding
levels, size, stretch, max_points, and dark. It saves the *recipe*, not the HTML -- reopening
regenerates the graph from the cache, and command-line flags override what the session stores.
    --save NAME        write the current graph as a session (and name its HTML ``NAME.html``)
    --session NAME     reopen it (flags on the command line win over what the session holds)
    --list             list saved sessions
    --no-open          just write the HTML, don't open it in a browser

``--sorted`` draws only the sorted wedge ``y >= z >= x``: the loser set is symmetric under
permuting the three piles, so the full cloud is six overlapping copies of one surface, and this
keeps the single copy. That is what turns the several fans (one per choice of which pile is the
big one) into the one fan they are all images of. The sheet coordinate stays the *smallest* pile,
so each sheet keeps its whole far field.

Usage:
    python -m wythoffs_game.analysis.plot_3d --levels 0-40 --size 8000
    python -m wythoffs_game.analysis.plot_3d --levels 0-40 --size 8000 --sorted   # one wedge
    python -m wythoffs_game.analysis.plot_3d --levels 0,10,25,50 --size 20000 --dark
    python -m wythoffs_game.analysis.plot_3d --levels 0-100 --size 36000 --max-points 250000
    python -m wythoffs_game.analysis.plot_3d --levels 0-40 --size 8000 --stretch 2.5  # spread x
    python -m wythoffs_game.analysis.plot_3d --levels 0-40 --size 8000 --save wide3d  # keep it
    python -m wythoffs_game.analysis.plot_3d --session wide3d                         # reopen
"""

import argparse
import json
import webbrowser
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

from .plot_points import SLIDER_KEYS_JS, THEME, level_color, parse_levels
from .store import load, sheet_points

HERE = Path(__file__).parent
PLOTS = HERE / "plots"
SESSIONS = HERE / "sessions_3d"

# Plotly 3D scenes dolly the scroll wheel toward the fixed scene centre -- so the origin, off in
# a corner of the box, is hard to get close to. This handler replaces that with Desmos-style
# zoom-about-the-cursor: on wheel it finds the point the cursor is aimed at on the view (focal)
# plane, then scales BOTH camera eye and centre toward that point. Scaling a camera rig about a
# fixed point is exactly "zoom in on that point", so whatever is under the cursor stays put.
# It runs in the capture phase and stops the event, so Plotly's own centre-zoom never fires.
# TANHALF only affects how tightly the cursor locks (it sets the assumed field of view); the
# zoom direction is correct regardless. `{plot_id}` is substituted by write_html.
CURSOR_ZOOM_JS = """
var gd = document.getElementById('{plot_id}');
if (gd) {
  var ZOOM = 0.97, TANHALF = 0.5;  // per-notch zoom step; closer to 1 = less sensitive
  var sub = function(a,b){ return {x:a.x-b.x, y:a.y-b.y, z:a.z-b.z}; };
  var add = function(a,b){ return {x:a.x+b.x, y:a.y+b.y, z:a.z+b.z}; };
  var scl = function(a,s){ return {x:a.x*s, y:a.y*s, z:a.z*s}; };
  var dot = function(a,b){ return a.x*b.x + a.y*b.y + a.z*b.z; };
  var crs = function(a,b){ return {x:a.y*b.z-a.z*b.y, y:a.z*b.x-a.x*b.z, z:a.x*b.y-a.y*b.x}; };
  var nrm = function(a){ var l=Math.sqrt(dot(a,a))||1; return scl(a,1/l); };
  var getCam = function(){
    try { return gd._fullLayout.scene._scene.getCamera(); }
    catch(e) { return gd._fullLayout.scene.camera; }
  };
  gd.addEventListener('wheel', function(e){
    // Over the legend, let Plotly's own scroll handle it -- don't hijack the wheel for zoom,
    // or a tall (many-level) legend can never be scrolled.
    if (e.target && e.target.closest && e.target.closest('.legend')) { return; }
    var cam = getCam();
    if (!cam || !cam.eye) { return; }
    e.preventDefault(); e.stopPropagation();
    var eye = cam.eye, center = cam.center, up = cam.up;
    var fwd = nrm(sub(center, eye));       // forward (into the screen)
    var right = nrm(crs(fwd, up));         // screen right
    var upv = crs(right, fwd);             // screen up (already unit)
    var dvec = sub(eye, center);
    var dist = Math.sqrt(dot(dvec, dvec));
    var rect = gd.getBoundingClientRect();
    var nx = 2*(e.clientX-rect.left)/rect.width - 1;   // -1..1 across the plot
    var ny = -(2*(e.clientY-rect.top)/rect.height - 1);
    var halfH = dist*TANHALF, halfW = halfH*(rect.width/rect.height);
    var target = add(center, add(scl(right, nx*halfW), scl(upv, ny*halfH)));
    var k = e.deltaY < 0 ? ZOOM : 1/ZOOM;  // wheel up = zoom in
    Plotly.relayout(gd, {'scene.camera': {
      up: up,
      center: add(target, scl(sub(center, target), k)),
      eye:    add(target, scl(sub(eye,    target), k))
    }});
  }, {passive:false, capture:true});
}
"""


# Past this many levels, one-trace-per-level stops paying off: the legend becomes an
# unusable thousand-row list and every rotate/zoom re-touches thousands of WebGL objects, so
# the view crawls even though the point count is small. Above the threshold we collapse the
# whole cloud into ONE trace colored by x via a colorbar (a single draw call, no legend).
MERGE_ABOVE = 150


def _points(loser_y, x, wedge=False):
    """Sheet ``x``'s losers as ``(y, z)``, optionally cut down to the sorted wedge.

    ``wedge=True`` keeps only the dots with ``y >= z >= x`` -- the losers whose piles are already
    in sorted order with the sheet coordinate as the *smallest* pile. The loser set is symmetric
    under permuting the three piles, so every loser has exactly one arrangement satisfying that,
    and the full cloud is six overlapping copies of this one wedge. Drawing the wedge alone
    replaces the six fans with the single surface they are copies of.

    Note which pile the sheet holds: slicing at a fixed *smallest* pile keeps each sheet's whole
    far field (the slope-(1+sqrt3) lines run out to y ~ 50x, far above x), whereas slicing at a
    fixed *largest* pile -- what ``wythoffs_game.sorted_wythoff`` does, because that is the order
    its recurrence must run in -- leaves only the handful of dots with both other piles below the
    sheet, a triangle of width x with none of the lines in it.
    """
    y, z = sheet_points(loser_y, x)
    if wedge:
        keep = (z >= x) & (y >= z)
        y, z = y[keep], z[keep]
    return y, z


def _ramp_colorscale(t):
    """Plotly [pos, color] colorscale from the theme's ramp, matching ``level_color``'s gradient."""
    ramp = t["ramp"]
    return [[i / (len(ramp) - 1), c] for i, c in enumerate(ramp)]


# The three-quarter starting eye; also what the "reset" preset returns to.
ISO_EYE = dict(x=1.7, y=1.7, z=0.9)


def _axis_view(stretch):
    """Camera eyes that look straight down each axis, so the cloud flattens to a clean plane.

    Looking down an axis puts the other two axes in the screen plane, so you get the 2D picture
    back with no perspective skew:
      * down x -> the y–z face (the ``plot_points`` sheet view: y across, z up);
      * down y -> the x–z face (levels across, z up);
      * down z -> the x–y face (levels across, y up).
    ``up`` is chosen perpendicular to the view direction. The down-x eye stands back by ``stretch``
    because the x edge is that much longer; distances only set the initial framing -- zoom adjusts.
    """
    return {
        "yz": dict(eye=dict(x=stretch + 1.4, y=0, z=0), up=dict(x=0, y=0, z=1)),
        "xz": dict(eye=dict(x=0, y=2.5, z=0), up=dict(x=0, y=0, z=1)),
        "xy": dict(eye=dict(x=0, y=0, z=2.5), up=dict(x=0, y=1, z=0)),
        "iso": dict(eye=ISO_EYE, up=dict(x=0, y=0, z=1)),
    }


def _orientation_buttons(t, stretch):
    """A row of preset buttons that snap the camera to each axis-aligned view (and back to iso).

    Each button is a ``relayout`` that just moves ``scene.camera`` -- the dots never move, so the
    presets compose with the slider and with manual rotation/zoom.
    """
    v = _axis_view(stretch)
    presets = [
        ("y–z  (down x)", v["yz"]),
        ("x–z  (down y)", v["xz"]),
        ("x–y  (down z)", v["xy"]),
        ("reset", v["iso"]),
    ]
    buttons = [dict(method="relayout", label=label, args=[{"scene.camera": cam}])
               for label, cam in presets]
    # Hung from the TOP of the plotting area (yanchor="top"), not above it: anchoring to the
    # bottom of y=1 put the row in the same margin strip as the title, which it then covered.
    # The 3D box's top-left corner is empty, so the buttons sit clear of both title and legend.
    return dict(type="buttons", direction="right", showactive=False,
                x=0.0, xanchor="left", y=1.0, yanchor="top",
                pad=dict(l=2, t=2, b=2), bgcolor=t["grid"],
                bordercolor=t["axis"], font=dict(color=t["ink"], size=11),
                buttons=buttons)


def _scene(t, stretch, camera, ranges=None, cube=False):
    """The shared 3D scene dict: boxed axes, manual aspect (x stretched), turntable drag.

    ``ranges`` optionally pins each axis to a fixed ``(lo, hi)`` (keys ``x``/``y``/``z``). The
    slider view uses this so the y and z axes hold still as you step levels -- otherwise Plotly
    auto-ranges to the single visible sheet and the picture rescales under you, hiding exactly the
    progression you want to watch.

    ``cube`` switches to a true common scale on all three axes (``aspectmode="data"``). This is the
    only mode in which the game's x/y/z symmetry is undistorted -- but it is only worth using on a
    cube-shaped window (x, y, z all covering the same range), i.e. ``--levels 0-L --size L``.
    """
    r = ranges or {}
    axis = dict(backgroundcolor=t["surface"], gridcolor=t["grid"], zerolinecolor=t["axis"],
                color=t["muted"], title_font=dict(color=t["ink"], size=13))
    scene = dict(
        xaxis=dict(title="x  (pile 1 / level)", range=r.get("x"), **axis),
        yaxis=dict(title="y  (pile 2)", range=r.get("y"), **axis),
        zaxis=dict(title="z  (pile 3)", range=r.get("z"), **axis),
        # Turntable keeps z pointing up, so dragging orbits the stack instead of tumbling it off.
        dragmode="turntable",
        camera=camera,
    )
    if cube:
        # Equal scale on every axis: the ONLY view in which the three-pile symmetry is true to
        # shape. Meant for a cube window (x, y, z same range); on a thin slab it makes a wafer.
        scene["aspectmode"] = "data"
    else:
        # NOT "data": x spans only the chosen levels while y,z reach the thousands, so a common
        # scale flattens the stack into a wafer. Give each axis its own edge; x gets a
        # `stretch`-long depth edge so the levels stand apart. Slopes here are therefore not
        # true y:z ratios -- use plot_points (2D, equal aspect) for those, or --cube.
        scene["aspectmode"] = "manual"
        scene["aspectratio"] = dict(x=stretch, y=1, z=1)
    return scene


def build_slider(levels, size, dark=False, max_points=150_000, stretch=1.6, cube=False,
                 title=None, wedge=False):
    """3D scatter with a slider that shows ONE x-level at a time (a flip-book across the stack).

    The camera starts looking straight down the x-axis, so each level lands on the same y–z face
    and sliding flips between consecutive sheets in place -- the ``plot_points --slider`` idea, but
    you can still grab the cloud and rotate, or hit an orientation preset, without losing the slider.
    A faint ghost of the WHOLE cloud stays drawn behind every step, so you can see where the active
    sheet sits inside the full stack; and the axes are pinned to the full data extent, so y and z
    hold still as you slide (Plotly would otherwise rescale them to the one visible sheet).

    Trace 0 is the ghost (always visible); traces 1..N are the per-level sheets, only the active one
    shown -- so even a thousand levels stay smooth (the ghost plus one small sheet at a time).
    """
    t = THEME[dark]
    loser_y = load(max(levels) + 1, size)
    rng = np.random.default_rng(0)
    fig = go.Figure()

    # Gather every level once: the full extent pins the axes, and a thinned copy is the ghost.
    gx, gy, gz = [], [], []
    for x in levels:
        y, z = _points(loser_y, x, wedge)
        gx.append(np.full(len(y), x)); gy.append(y); gz.append(z)
    gx, gy, gz = np.concatenate(gx), np.concatenate(gy), np.concatenate(gz)
    ranges = dict(
        x=[min(levels) - 0.5, max(levels) + 0.5],
        y=[0, int(gy.max()) + 1 if gy.size else size],
        z=[0, int(gz.max()) + 1 if gz.size else size],
    )

    # The ghost: a faint copy of the whole cloud behind every sheet, so you can see where the
    # active level sits in the stack. Kept LIGHT on purpose -- it has its own small budget (a
    # fraction of max_points), because a big semi-transparent Scatter3d is what makes 3D drag and
    # smear (WebGL has to depth-sort and alpha-blend every point). Colored by x via the ramp, not
    # gray, so the level gradient itself reads through it; a modest opacity keeps the dots crisp
    # instead of blurring into a haze the way near-zero opacity does.
    gtot = len(gx)
    ghost_cap = min(30_000, max_points)  # context only -- keep it small; big alpha clouds drag
    if gtot > ghost_cap:
        keep = rng.choice(gtot, ghost_cap, replace=False)
        gx, gy, gz = gx[keep], gy[keep], gz[keep]
    fig.add_trace(go.Scatter3d(
        x=gx, y=gy, z=gz, mode="markers", name=f"all levels (ghost, {gtot:,})",
        marker=dict(size=1.6, color=gx, colorscale=_ramp_colorscale(t), opacity=0.30,
                    line=dict(width=0)),
        hoverinfo="skip",
    ))

    # The active sheet is drawn in ink (black in light theme, white in dark) so it reads instantly
    # against the colored ghost -- only one sheet shows at a time, so a single high-contrast color
    # beats a per-level hue you'd have to look up.
    cap = max_points  # one sheet on screen at a time, so each may use the whole budget
    counts = []
    for i, x in enumerate(levels):
        y, z = _points(loser_y, x, wedge)
        n = len(y)
        if n > cap:
            keep = rng.choice(n, cap, replace=False)
            y, z = y[keep], z[keep]
        counts.append(n)
        fig.add_trace(go.Scatter3d(
            x=np.full(len(y), x), y=y, z=z, mode="markers", visible=(i == 0),
            name=f"x = {x}  ({n:,})",
            marker=dict(size=2, color=t["ink"], line=dict(width=0)),
            hovertemplate="(%{x}, %{y}, %{z})<extra>x = " + str(x) + "</extra>",
        ))

    steps = []
    for i, x in enumerate(levels):
        vis = [True] + [j == i for j in range(len(levels))]  # ghost (trace 0) always on
        steps.append(dict(method="update", label=str(x),
                          args=[{"visible": vis},
                                {"title.text": title or f"Bounded Wythoff losers — sheet x = {x}"
                                                        f"  ({counts[i]:,})"}]))

    fig.update_layout(
        title=dict(text=title or f"Bounded Wythoff losers — sheet x = {levels[0]}"
                                 f"  ({counts[0]:,})",
                   font=dict(color=t["ink"], size=16)),
        paper_bgcolor=t["surface"], font=dict(color=t["muted"], size=12),
        legend=dict(title=dict(text="x-level"), itemsizing="constant", bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=50, b=0),
        updatemenus=[_orientation_buttons(t, stretch)],
        sliders=[dict(active=0, currentvalue=dict(prefix="x-level = ", font=dict(color=t["ink"])),
                      pad=dict(t=40, b=10), steps=steps,
                      font=dict(color=t["muted"]), bgcolor=t["grid"],
                      activebgcolor=t["axis"], bordercolor=t["axis"])],
        # Start looking down the x-axis: the flip-book reads as a stack of y–z sheets. Pin the
        # axes to the full data extent so y and z hold still while stepping levels.
        scene=_scene(t, stretch, camera=_axis_view(stretch)["yz"], ranges=ranges, cube=cube),
    )
    return fig


def build(levels, size, dark=False, max_points=150_000, stretch=1.6, slider=False, cube=False,
          title=None, wedge=False):
    """Rotatable 3D scatter of losers.

    ``slider`` hands off to :func:`build_slider` (one x-level at a time, flip-book). Otherwise:
    few levels (<= ``MERGE_ABOVE``) get one toggleable trace per level, distinct color, in the
    legend; many levels collapse into a single trace colored by x with a colorbar -- one draw call
    stays smooth where thousands of traces + a giant legend would crawl.

    ``stretch`` is how long the x (level) edge of the box is relative to the square y-z base:
    the x data range is tiny (0..40) next to y and z (0..thousands), so drawing all three to a
    common scale would crush the stack flat. Giving x its own full edge spreads the levels out.
    """
    if slider:
        return build_slider(levels, size, dark=dark, max_points=max_points, stretch=stretch,
                            cube=cube, title=title, wedge=wedge)
    t = THEME[dark]
    loser_y = load(max(levels) + 1, size)
    rng = np.random.default_rng(0)
    fig = go.Figure()

    if len(levels) > MERGE_ABOVE:
        # One trace: gather every level's points, thin the whole cloud once to max_points, color
        # by x. No per-level legend -- a colorbar reads the x-gradient instead.
        xs, ys, zs = [], [], []
        for x in levels:
            y, z = _points(loser_y, x, wedge)
            xs.append(np.full(len(y), x)); ys.append(y); zs.append(z)
        xs = np.concatenate(xs); ys = np.concatenate(ys); zs = np.concatenate(zs)
        total = len(xs)
        if total > max_points:
            keep = rng.choice(total, max_points, replace=False)
            xs, ys, zs = xs[keep], ys[keep], zs[keep]
        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs, mode="markers",
            marker=dict(size=2, color=xs, colorscale=_ramp_colorscale(t), line=dict(width=0),
                        colorbar=dict(title="x-level", tickcolor=t["muted"],
                                      tickfont=dict(color=t["muted"]))),
            hovertemplate="(%{x}, %{y}, %{z})<extra></extra>",
        ))
        print(f"{len(levels)} levels merged into one colored trace ({total:,} points, "
              f"{len(xs):,} drawn) -- legend replaced by a colorbar to stay smooth.")
        total = len(xs)  # the warning below should judge the drawn count, not the pre-thin total
    else:
        # A per-level cap that keeps the whole cloud under max_points; thin bigger sheets to fit.
        cap = max(1, max_points // max(1, len(levels)))
        total = 0
        for i, x in enumerate(levels):
            y, z = _points(loser_y, x, wedge)
            n = len(y)
            if n > cap:
                keep = rng.choice(n, cap, replace=False)
                y, z = y[keep], z[keep]
            total += len(y)
            fig.add_trace(go.Scatter3d(
                x=np.full(len(y), x), y=y, z=z, mode="markers",
                name=f"x = {x}  ({n:,})",
                marker=dict(size=2, color=level_color(i, len(levels), t), line=dict(width=0)),
                hovertemplate="(%{x}, %{y}, %{z})<extra>x = " + str(x) + "</extra>",
            ))

    if total > 400_000:
        print(f"warning: {total:,} points after thinning -- rotation may stutter. Lower "
              f"--max-points, or fewer levels, will stay smooth.")

    fig.update_layout(
        title=dict(text=title or (f"Bounded Wythoff losers in 3D"
                                  f"{' — sorted wedge y ≥ z ≥ x' if wedge else ''}"
                                  f" — {total:,} points"),
                   font=dict(color=t["ink"], size=16)),
        paper_bgcolor=t["surface"], font=dict(color=t["muted"], size=12),
        legend=dict(title=dict(text="x-level"), itemsizing="constant", bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=50, b=0),
        updatemenus=[_orientation_buttons(t, stretch)],
        # A three-quarter eye shows the level separation from the first frame; the preset buttons
        # snap to the axis-aligned views.
        scene=_scene(t, stretch, camera=dict(eye=ISO_EYE, up=dict(x=0, y=0, z=1)), cube=cube),
    )
    return fig


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--levels", help="e.g. 0,10,25 or 0-40")
    p.add_argument("--size", type=int, help="grid size (y and z run 0..size-1)")
    p.add_argument("--max-points", type=int, default=None,
                   help="thin the whole cloud to near this many dots (default 150k)")
    p.add_argument("--stretch", type=float, default=None,
                   help="length of the x (level) edge relative to the y-z base; bigger spreads "
                        "the sheets further apart (default 1.6)")
    p.add_argument("--slider", action="store_true",
                   help="show one x-level at a time under a slider (a 3D flip-book), starting "
                        "looking down the x-axis onto the y–z face. Rotate or use the presets freely.")
    p.add_argument("--sorted", dest="wedge", action="store_true",
                   help="draw only the sorted wedge y >= z >= x (each loser once, with the sheet "
                        "coordinate as the smallest pile) instead of all six permuted copies -- "
                        "the several fans collapse into the one surface they are copies of.")
    p.add_argument("--cube", action="store_true",
                   help="equal scale on all three axes (aspectmode=data), the only view where the "
                        "x/y/z symmetry is undistorted. Use on a cube window: --levels 0-L --size L.")
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
            print(f"{f.stem:20s} levels={a_levels_repr(s['levels'])}  size={s['size']}  "
                  f"stretch={s.get('stretch', 1.6)}")
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
    stretch = a.stretch if a.stretch is not None else s.get("stretch", 1.6)
    max_points = a.max_points if a.max_points is not None else s.get("max_points", 150_000)
    slider = a.slider or s.get("slider", False)
    cube = a.cube or s.get("cube", False)
    dark = a.dark or s.get("dark", False)
    wedge = a.wedge or s.get("wedge", False)
    s = dict(s, levels=levels, size=size, stretch=stretch, max_points=max_points,
             slider=slider, cube=cube, dark=dark, wedge=wedge)

    fig = build(levels, size, dark=dark, max_points=max_points, stretch=stretch, slider=slider,
                cube=cube, wedge=wedge)

    name = a.save or a.session or "plot_3d"
    if a.save:
        (SESSIONS / f"{a.save}.json").write_text(json.dumps(s, indent=2))
        print(f"saved session {a.save!r}")

    out = PLOTS / f"{name}.html"
    fig.write_html(out, include_plotlyjs="cdn",
                   config=dict(scrollZoom=True, displaylogo=False,
                               toImageButtonOptions=dict(format="png", scale=2)),
                   post_script=CURSOR_ZOOM_JS + SLIDER_KEYS_JS)
    print(f"wrote {out}")
    if not a.no_open:
        webbrowser.open(out.resolve().as_uri())


def a_levels_repr(levels):
    """Compact ``--list`` display: ``0-40`` for a contiguous run, else a short list."""
    levels = sorted(levels)
    if len(levels) > 1 and levels == list(range(levels[0], levels[-1] + 1)):
        return f"{levels[0]}-{levels[-1]}"
    return ",".join(map(str, levels[:6])) + (f",... ({len(levels)})" if len(levels) > 6 else "")


if __name__ == "__main__":
    main()
