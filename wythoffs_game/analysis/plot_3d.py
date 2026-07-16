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

Usage:
    python -m wythoffs_game.analysis.plot_3d --levels 0-40 --size 8000
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

from .plot_points import THEME, level_color, parse_levels
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


def _ramp_colorscale(t):
    """Plotly [pos, color] colorscale from the theme's ramp, matching ``level_color``'s gradient."""
    ramp = t["ramp"]
    return [[i / (len(ramp) - 1), c] for i, c in enumerate(ramp)]


def build(levels, size, dark=False, max_points=150_000, stretch=1.6, title=None):
    """Rotatable 3D scatter of losers.

    Few levels (<= ``MERGE_ABOVE``): one toggleable trace per level, distinct color, in the
    legend. Many levels: a single trace colored by x with a colorbar -- one draw call stays
    smooth where thousands of traces + a giant legend would crawl.

    ``stretch`` is how long the x (level) edge of the box is relative to the square y-z base:
    the x data range is tiny (0..40) next to y and z (0..thousands), so drawing all three to a
    common scale would crush the stack flat. Giving x its own full edge spreads the levels out.
    """
    t = THEME[dark]
    loser_y = load(max(levels) + 1, size)
    rng = np.random.default_rng(0)
    fig = go.Figure()

    if len(levels) > MERGE_ABOVE:
        # One trace: gather every level's points, thin the whole cloud once to max_points, color
        # by x. No per-level legend -- a colorbar reads the x-gradient instead.
        xs, ys, zs = [], [], []
        for x in levels:
            y, z = sheet_points(loser_y, x)
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
            y, z = sheet_points(loser_y, x)
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

    axis = dict(backgroundcolor=t["surface"], gridcolor=t["grid"], zerolinecolor=t["axis"],
                color=t["muted"], title_font=dict(color=t["ink"], size=13))
    fig.update_layout(
        title=dict(text=title or f"Bounded Wythoff losers in 3D — {total:,} points",
                   font=dict(color=t["ink"], size=16)),
        paper_bgcolor=t["surface"], font=dict(color=t["muted"], size=12),
        legend=dict(title=dict(text="x-level"), itemsizing="constant", bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=50, b=0),
        scene=dict(
            xaxis=dict(title="x  (level / pile 1)", **axis),
            yaxis=dict(title="y  (pile 2)", **axis),
            zaxis=dict(title="z  (pile 3)", **axis),
            # NOT aspectmode="data": x spans 0..40 while y,z reach the thousands, so a common
            # scale flattens the stack into a wafer. Give each axis its own edge; x gets a
            # `stretch`-long depth edge so the levels stand apart. Slopes here are therefore not
            # true y:z ratios -- use plot_points (2D, equal aspect) for those.
            aspectmode="manual",
            aspectratio=dict(x=stretch, y=1, z=1),
            # Turntable keeps z pointing up, so dragging orbits the stack instead of tumbling it
            # off screen. A three-quarter eye shows the level separation from the first frame.
            dragmode="turntable",
            camera=dict(eye=dict(x=1.7, y=1.7, z=0.9)),
        ),
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
    dark = a.dark or s.get("dark", False)
    s = dict(s, levels=levels, size=size, stretch=stretch, max_points=max_points, dark=dark)

    fig = build(levels, size, dark=dark, max_points=max_points, stretch=stretch)

    name = a.save or a.session or "plot_3d"
    if a.save:
        (SESSIONS / f"{a.save}.json").write_text(json.dumps(s, indent=2))
        print(f"saved session {a.save!r}")

    out = PLOTS / f"{name}.html"
    fig.write_html(out, include_plotlyjs="cdn",
                   config=dict(scrollZoom=True, displaylogo=False,
                               toImageButtonOptions=dict(format="png", scale=2)),
                   post_script=CURSOR_ZOOM_JS)
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
