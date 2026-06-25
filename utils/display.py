"""
Visualization for combinatorial games, rendering 2D boolean sheets using Matplotlib and NumPy
"""

import math
import re
import matplotlib.pyplot as plt
import numpy as np

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
    fig, axes = plt.subplots(
        rows, cols,
        figsize=(fig_width * scale, fig_height * scale),
        dpi=100,
        constrained_layout=True,
    )

    # Flatten axes array so we can iterate linearly, handling single-sheet edge cases
    axes = np.atleast_1d(axes).flatten()
        
    for i, (ax, sheet, title) in enumerate(zip(axes[:num_sheets], sheets, titles)):
        # Crop sheet if a specific size is requested
        if sizes is not None and i < len(sizes) and sizes[i] is not None:
            size = sizes[i]
            if isinstance(size, int):
                sheet = sheet[:size, :size]
            else:
                sheet = sheet[:size[0], :size[1]]

        grid_rows = sheet.shape[0]  
        grid_columns = sheet.shape[1] 
        
        ax.set_title(title)
        ax.set_xlabel("y")
        ax.set_ylabel("z")
        
        # Render the sheet, converting array's T/F values as 0/1, put (0,0) at the bottom left.
        # Sets minimum value as 0 (white), and maximum value as 1 (black)
        ax.imshow(sheet.astype(np.uint8), cmap="binary", origin="lower", vmin=0, vmax=1)
        
        # Create step sizes for ~8 tick marks by finding raw step size, using its order of magnitude
        # to pick closest nice-looking step size to the raw step size
        nice_multipliers = [1, 2, 5, 10]
        
        raw_step_x = max(1, grid_columns / 8)
        mag_x = 10 ** int(np.log10(raw_step_x)) if raw_step_x >= 1 else 1
        step_x = mag_x * min(nice_multipliers, key=lambda n: abs(n * mag_x - raw_step_x))
        step_x = max(int(step_x), 1)
        
        raw_step_y = max(1, grid_rows / 8)
        mag_y = 10 ** int(np.log10(raw_step_y)) if raw_step_y >= 1 else 1
        step_y = mag_y * min(nice_multipliers, key=lambda n: abs(n * mag_y - raw_step_y))
        step_y = max(int(step_y), 1)
        
        # Puts tick markers on axes
        ax.set_xticks(np.arange(0, grid_columns, step_x))
        ax.set_yticks(np.arange(0, grid_rows, step_y))
        
        # Show gridlines for smaller grids
        if grid_columns <= 100 or grid_rows <= 100:
            ax.set_xticks(np.arange(-0.5, grid_columns, 1), minor=True)
            ax.set_yticks(np.arange(-0.5, grid_rows, 1), minor=True)
            ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)
            ax.tick_params(which='minor', bottom=False, left=False)

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
