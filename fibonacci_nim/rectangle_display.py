"""
Visualization for combinatorial games, rendering 2D boolean sheets using Matplotlib and NumPy
"""

import matplotlib.pyplot as plt
import numpy as np

def output(sheet, is_winner, desired_level):
    """
    Renders and displays a 2D grid visualization of the game state.

    Plots a 2D boolean array where True values are rendered as black squares and False values are 
    rendered as white squares. 
    Automatically scales the axis ticks based on the size of the grid and displays cell gridlines 
    only for smaller grids.

    Args:
        sheet (np.ndarray): A 2D boolean or integer NumPy array representing 
            the game board sheet. Not assumed to be square -- rows (z) and
            columns (y) may have different sizes.
        is_winner (bool): Flag indicating if the sheet represents Winning (True) 
            or Losing (False) positions. Used to format the plot title.
        desired_level (int): The x-level of the sheet that was calculated. 
            Used to format the plot title.

    Returns:
        No return value; displays a Matplotlib plot.
    """

    grid_rows = sheet.shape[0]  # z-axis extent
    grid_columns = sheet.shape[1]  # y-axis extent

    _, ax = plt.subplots(figsize=(8, 8), dpi=100)   # Intitialize plot canvas, 100 pixels per inch

    # Set plot title based on W/L sheet and x-level, label axes as y and z
    if is_winner:
        ax.set_title(f"W {desired_level} with size {grid_columns} by {grid_rows}")
    else:
        ax.set_title(f"L {desired_level} with size {grid_columns} by {grid_rows}")
    ax.set_xlabel("y")
    ax.set_ylabel("z")

    # Render the sheet, converting array's T/F values as 0/1, put (0,0) at the bottom left.
    # Sets minimum value as 0 (white), and maximum value as 1 (black)
    ax.imshow(sheet.astype(np.uint8), cmap="binary", origin="lower", vmin=0, vmax=1)

    # Create step sizes for ~8 tick marks by finding raw step size, using its order of magnitude
    # to pick closest nice-looking step size to the raw step size
    raw_step_x_axis = max(1, grid_columns / 8)
    magnitude = 10 ** int(np.log10(raw_step_x_axis)) if raw_step_x_axis >= 1 else 1
    nice_multipliers = [1, 2, 5, 10]
    step_x_axis = magnitude * min(nice_multipliers, key=lambda n:
        abs(n * magnitude - raw_step_x_axis))
    step_x_axis = max(int(step_x_axis), 1)

    raw_step_y_axis = max(1, grid_rows / 8)
    magnitude = 10 ** int(np.log10(raw_step_y_axis)) if raw_step_y_axis >= 1 else 1
    nice_multipliers = [1, 2, 5, 10]
    step_y_axis = magnitude * min(nice_multipliers, key=lambda n:
        abs(n * magnitude - raw_step_y_axis))
    step_y_axis = max(int(step_y_axis), 1)

    # Puts tick markers on axes
    major_ticks_x_axis = np.arange(0, grid_columns, step_x_axis)
    ax.set_xticks(major_ticks_x_axis)

    # FIX: was np.arange(0, grid_columns, step_y_axis) -- used the wrong
    # dimension (columns instead of rows), which misplaces y-axis (z) ticks
    # whenever the sheet isn't square.
    major_ticks_y_axis = np.arange(0, grid_rows, step_y_axis)
    ax.set_yticks(major_ticks_y_axis)

    # Show gridlines for smaller grids
    # FIX: 'grid_size' was never defined (leftover from an earlier version
    # where rows/columns shared one size). Now checks both dimensions
    # independently, since sheets can be non-square (e.g. y_size != z_size).
    if grid_columns <= 100:
        minor_ticks_x = np.arange(-0.5, grid_columns, 1)
        ax.set_xticks(minor_ticks_x, minor=True)
        ax.tick_params(axis='x', which='minor', bottom=False)

    if grid_rows <= 100:
        minor_ticks_y = np.arange(-0.5, grid_rows, 1)
        ax.set_yticks(minor_ticks_y, minor=True)
        ax.tick_params(axis='y', which='minor', left=False)

    if grid_columns <= 100 or grid_rows <= 100:
        ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)

    plt.show()
