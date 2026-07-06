"""
Visualization for combinatorial games, rendering 2D boolean sheets using Matplotlib and NumPy
"""

import math
import re
import matplotlib.pyplot as plt
import numpy as np

def _nice_step(span):
    """Pick a 1/2/5-style step size giving roughly 8 ticks across ``span`` cells."""
    nice_multipliers = [1, 2, 5, 10]
    raw = max(1, span / 8)
    mag = 10 ** int(np.log10(raw)) if raw >= 1 else 1
    step = mag * min(nice_multipliers, key=lambda n: abs(n * mag - raw))
    return max(int(step), 1)


def _update_ticks(ax):
    """Recompute ticks and gridlines for the currently visible window of ``ax``.

    Runs once at creation and again on every zoom/pan (connected to the axes'
    ``xlim_changed``/``ylim_changed`` callbacks, which pass the axes as the sole
    argument). Tick spacing is chosen from the *visible* span, not the full grid,
    so zooming in refines the labels (500-steps become 50-steps become 1-steps),
    and per-cell minor gridlines appear whenever fewer than ~120 cells are visible.
    Every tick is clamped strictly inside the current limits: ``Axis.set_ticks``
    *expands* the view to show any out-of-range tick, which would re-fire this
    callback and walk the view outward forever. A re-entry guard backstops that.
    """
    if getattr(ax, '_updating_ticks', False):
        return
    ax._updating_ticks = True
    try:
        x0, x1 = sorted(ax.get_xlim())
        y0, y1 = sorted(ax.get_ylim())

        step_x = _nice_step(x1 - x0)
        step_y = _nice_step(y1 - y0)

        # Ticks at step multiples, only within the visible window (and never below 0).
        start_x = max(0, math.ceil(x0 / step_x)) * step_x
        start_y = max(0, math.ceil(y0 / step_y)) * step_y
        xt = np.arange(start_x, x1 + step_x, step_x)
        yt = np.arange(start_y, y1 + step_y, step_y)
        ax.set_xticks(xt[xt <= x1])
        ax.set_yticks(yt[yt <= y1])

        # Per-cell gridlines whenever the visible window is small enough to resolve them.
        if (x1 - x0) <= 120 and (y1 - y0) <= 120:
            mx = np.arange(math.floor(x0) - 0.5, x1 + 1, 1)
            my = np.arange(math.floor(y0) - 0.5, y1 + 1, 1)
            ax.set_xticks(mx[(mx >= x0) & (mx <= x1)], minor=True)
            ax.set_yticks(my[(my >= y0) & (my <= y1)], minor=True)
            ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)
            ax.tick_params(which='minor', bottom=False, left=False)
        else:
            ax.set_xticks([], minor=True)
            ax.set_yticks([], minor=True)
            ax.grid(False, which='minor')
    finally:
        ax._updating_ticks = False


def output_multiple(sheets, titles, sizes=None):
    """
    Renders and displays multiple 2D grid visualizations side-by-side.

    Args:
        sheets (list of np.ndarray): List of 2D boolean NumPy arrays representing game board sheets.
        titles (list of str): List of titles for each subplot.
        sizes (list of int or tuple, optional): List of sizes to crop each sheet.
    """
    num_sheets = len(sheets)

    # Grid layout math: max 3 columns per row to prevent cramping
    max_cols = 3
    cols = min(num_sheets, max_cols)
    rows = math.ceil(num_sheets / cols)

    # Crop every sheet up front so we know the real displayed dimensions before sizing
    # the figure (the dpi choice below depends on the largest cropped grid).
    cropped = []
    for i, sheet in enumerate(sheets):
        if sizes is not None and i < len(sizes) and sizes[i] is not None:
            size = sizes[i]
            if isinstance(size, int):
                sheet = sheet[:size, :size]
            else:
                sheet = sheet[:size[0], :size[1]]
        cropped.append(sheet)

    # Each subplot wants this many inches square, but the whole figure is capped to a
    # screen-sized budget so it never opens taller/wider than the display. Scaling both
    # dimensions by the same factor keeps the subplots square.
    per_subplot = 5
    fig_width = per_subplot * cols
    fig_height = per_subplot * rows
    max_width, max_height = 16, 9
    scale = min(1.0, max_width / fig_width, max_height / fig_height)

    # constrained_layout (unlike a one-shot tight_layout) recomputes spacing on every
    # resize, so shrinking the window reflows the panels instead of overlapping them.
    # dpi stays at 100: raising it scales fonts and window pixel size too, so it can't
    # fix cell rendering interactively. At full zoom-out a grid with more cells than the
    # axis has pixels cannot show every cell as a square -- zoom in (ticks refine
    # automatically, see _update_ticks) or use save_exact for a pixel-perfect PNG.
    fig, axes = plt.subplots(
        rows, cols,
        figsize=(fig_width * scale, fig_height * scale),
        dpi=100,
        constrained_layout=True,
    )

    # Flatten axes array so we can iterate linearly, handling single-sheet edge cases
    axes = np.atleast_1d(axes).flatten()

    for i, (ax, sheet, title) in enumerate(zip(axes[:num_sheets], cropped, titles)):
        
        ax.set_title(title)
        ax.set_xlabel("y")
        ax.set_ylabel("z")
        
        # Render the sheet, converting array's T/F values as 0/1, put (0,0) at the bottom left.
        # Sets minimum value as 0 (white), and maximum value as 1 (black)
        ax.imshow(sheet.astype(np.uint8), cmap="binary", origin="lower", vmin=0, vmax=1,
                  interpolation="nearest", aspect="equal")
        
        # Ticks and gridlines follow the visible window: set them for the initial
        # full view, then recompute on every zoom/pan so labels refine as you zoom.
        _update_ticks(ax)
        ax.callbacks.connect('xlim_changed', _update_ticks)
        ax.callbacks.connect('ylim_changed', _update_ticks)

    # Hide any unused subplots (e.g., if we have 5 sheets in a 2x3 grid)
    for ax in axes[num_sheets:]:
        ax.axis('off')

    plt.show()

def output(sheet, is_winner, desired_level, size=None):
    """
    Renders and displays a 2D grid visualization of the game state.

    Plots a 2D boolean array where True values are rendered as black squares and False values are 
    rendered as white squares. 
    Automatically scales the axis ticks based on the size of the grid and displays cell gridlines 
    only for smaller grids.

    Args:
        sheet (np.ndarray): A 2D boolean or integer NumPy array representing 
            the game board sheet.
        is_winner (bool): Flag indicating if the sheet represents Winning (True) 
            or Losing (False) positions. Used to format the plot title.
        desired_level (int): The x-level of the sheet that was calculated. 
            Used to format the plot title.
        size (int or tuple, optional): Specific size to crop the sheet before display.

    Returns:
        No return value; displays a Matplotlib plot.
    """
    sheet_type = "W" if is_winner else "L"
    
    if size is not None:
        disp_size = size if isinstance(size, int) else f"{size[1]} by {size[0]}"
    else:
        disp_size = str(sheet.shape[0])
        
    title = sheet_type + str(desired_level) + " with size " + str(disp_size)

    output_multiple([sheet], [title], sizes=[size] if size else None)


def parse_sheet_specs(raw):
    """Parse a request string into a list of (is_winner, level, size) tuples.

    Each spec has the form ``<W|L><level>x<size>`` and they are separated by commas,
    e.g. ``"W8x16, L4x20, W16x32"`` requests a 16x16 sheet of W8, a 20x20 sheet of L4,
    and a 32x32 sheet of W16.

    Args:
        raw (str): The user-entered request string.

    Returns:
        list[tuple[bool, int, int]]: (is_winner, x-level, grid size) for each sheet.

    Raises:
        ValueError: If any comma-separated token does not match the expected format.
    """
    specs = []
    for token in raw.split(','):
        token = token.strip()
        if not token:
            continue
        match = re.fullmatch(r'([WwLl])\s*(\d+)\s*[xX]\s*(\d+)', token)
        if not match:
            raise ValueError(
                f"Could not parse sheet spec '{token}' (expected e.g. W8x16)")
        type_char, level, size = match.group(1), int(match.group(2)), int(match.group(3))
        specs.append((type_char.upper() == 'W', level, size))
    return specs


def _loser_triplets(L_space, max_level, row_is_z):
    """Collect every losing position (x, y, z) for x-levels 0..max_level, sorted.

    ``row_is_z`` describes how each sheet ``L_space[x]`` is laid out: True means the
    axes are (z, y) (z is the row), False means (y, z). Either way the returned
    triplets are ordered (x, y, z).
    """
    triplets = []
    for x in range(max_level + 1):
        if row_is_z:
            zs, ys = np.where(L_space[x])
        else:
            ys, zs = np.where(L_space[x])
        for y, z in sorted(zip(ys.tolist(), zs.tolist())):
            triplets.append((x, y, z))
    return triplets


def run_sheet_session(compute_sheets, row_is_z=True, triplet_default=None):
    """Interactive multi-sheet session shared by the 3D sheet generators.

    Prompts for a comma-separated request and renders every requested sheet together,
    each with its own type, x-level, and size, e.g. ``W8x16, L4x20, C16x32``. Types:
    W (instant winners), L (losers on that single sheet), C (cumulative losers: every
    loser up through that level). A ``T<level>`` (or ``T<level>x<size>``) token instead
    prints all loser triplets (x, y, z) up to that level.

    Args:
        compute_sheets: Callable ``(depth, size) -> (W_space, L_space[, Lcum_space])``
            returning 3D boolean arrays of shape ``(depth, size, size)`` indexed
            ``[x, a, b]`` -- x-levels ``0..depth-1`` over the ``size x size`` (a, b) grid.
            Depth (number of x-levels) and grid size are decoupled, so a low-level
            request on a big grid only allocates the levels it needs. Returning just
            ``(W, L)`` lets the C (cumulative-loser) sheets be derived from L on demand.
        row_is_z: Layout of each sheet's (a, b) axes -- True for (z, y), False for (y, z).
            Only affects how T triplets are reported (the rendered orientation is left
            untouched so it matches each generator's existing display).
        triplet_default: Callable ``max_level -> default grid size`` used for T requests
            that omit an explicit size. Defaults to ``3 * max_level + 4``.
    """
    if triplet_default is None:
        triplet_default = lambda m: 3 * m + 4

    print("Enter sheets as <W|L|C><level>x<size>, separated by commas.")
    print("  W = instant winners, L = losers on that sheet, "
          "C = cumulative losers (all losers up to that level).")
    print("  T<level> (or T<level>x<size>) prints all loser triplets (x,y,z) up to that level.")

    specs = []         # (type_char, level, size) for sheets to plot
    triplet_reqs = []  # (level, size_or_None) for triplet printouts
    for token in input("Sheets:\n").split(','):
        token = token.strip()
        if not token:
            continue
        tmatch = re.fullmatch(r'[Tt]\s*(\d+)(?:\s*[xX]\s*(\d+))?', token)
        if tmatch:
            size = int(tmatch.group(2)) if tmatch.group(2) else None
            triplet_reqs.append((int(tmatch.group(1)), size))
            continue
        match = re.fullmatch(r'([WwLlCc])\s*(\d+)\s*[xX]\s*(\d+)', token)
        if not match:
            raise ValueError(
                f"Could not parse sheet spec '{token}' (expected e.g. W8x16, C16x32, T50)")
        specs.append((match.group(1).upper(), int(match.group(2)), int(match.group(3))))

    # Print any requested triplet lists first.
    for level, size in triplet_reqs:
        grid = max(size or 0, triplet_default(level))
        L_space = compute_sheets(level + 1, grid)[1]
        triplets = _loser_triplets(L_space, level, row_is_z)
        for x, y, z in triplets:
            print(f"({x}, {y}, {z})")
        print(f"\n{len(triplets)} losers for x = 0..{level}")

    if not specs:
        return

    # Size the space to cover every request. Depth (number of x-levels) and grid size are sized
    # independently, so a low-level request on a big grid no longer allocates a full cube. A
    # generator may return just (W_space, L_space) to save memory; the cumulative-loser (C) sheets
    # are then derived from L on demand (OR of L_0..L_level), so no full Lcum cube is materialized.
    depth = max(level + 1 for _, level, _ in specs)
    grid = max(size for _, _, size in specs)
    result = compute_sheets(depth, grid)
    W_space, L_space = result[0], result[1]
    Lcum_space = result[2] if len(result) > 2 else None

    arrays, titles = [], []
    for type_char, level, size in specs:
        if type_char == 'W':
            arr = W_space[level, :size, :size]
        elif type_char == 'L':
            arr = L_space[level, :size, :size]
        elif Lcum_space is not None:
            arr = Lcum_space[level, :size, :size]
        else:
            arr = L_space[:level + 1, :size, :size].any(axis=0)
        arrays.append(arr)
        label = "cumulative L0-" if type_char == 'C' else type_char
        titles.append(f"{label}{level} with size {size}")
    output_multiple(arrays, titles)


def save_exact(sheet, path, cell_px=1, size=None):
    """Write a sheet to a PNG with exactly ``cell_px`` device pixels per cell.

    The interactive figures can't guarantee square cells once the grid has more cells
    than the axis has pixels (e.g. a 4000 grid on a laptop screen): the overview is
    downsampled, so isolated cells alias into uneven rectangles. This bypasses all axis
    and margin resampling -- the raw boolean array is written straight to pixels, one
    cell -> ``cell_px`` x ``cell_px`` square block -- so cells are perfectly square at
    any grid size. There are no axes or ticks; open the PNG and zoom to inspect.
    Black = True, and (0, 0) is the bottom-left corner (matching ``output``).

    Args:
        sheet (np.ndarray): 2D boolean/integer sheet.
        path (str): Output PNG path.
        cell_px (int): Device pixels per cell (1 gives a grid-sized image).
        size (int or tuple, optional): Crop the sheet before writing.
    """
    if size is not None:
        if isinstance(size, int):
            sheet = sheet[:size, :size]
        else:
            sheet = sheet[:size[0], :size[1]]

    img = sheet.astype(bool)
    if cell_px > 1:
        img = np.repeat(np.repeat(img, cell_px, axis=0), cell_px, axis=1)

    # imsave puts row 0 at the top; flip so (0, 0) lands at the bottom-left.
    plt.imsave(path, img[::-1], cmap="binary", vmin=0, vmax=1)


def output_sheets(sheets):
    """Render a heterogeneous batch of sheets side-by-side, each with its own size.

    Unlike ``output_multiple``, this derives every title from the sheet's own type,
    level, and (already-cropped) shape, so each entry can be a different W/L, x-level,
    and size.

    Args:
        sheets (list[tuple[np.ndarray, bool, int]]): A list of
            (sheet, is_winner, level) tuples. Each ``sheet`` should already be cropped
            to the size you want displayed.
    """
    arrays, titles = [], []
    for sheet, is_winner, level in sheets:
        arrays.append(sheet)
        titles.append(f"{'W' if is_winner else 'L'}{level} with size {sheet.shape[0]}")
    output_multiple(arrays, titles)
