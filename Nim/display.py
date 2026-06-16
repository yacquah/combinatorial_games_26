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
            the game board sheet. It is assumed to be a square grid.
        is_winner (bool): Flag indicating if the sheet represents Winning (True) 
            or Losing (False) positions. Used to format the plot title.
        desired_level (int): The x-level of the sheet that was calculated. 
            Used to format the plot title.

    Returns:
        No return value; displays a Matplotlib plot.
    """

    grid_size = sheet.shape[0]  # Dimensions of square array will be the size of the grid drawn

    _, ax = plt.subplots(figsize=(8, 8), dpi=100)   # Intitialize plot canvas, 100 pixels per inch

    # Set plot title based on W/L sheet and x-level, label axes as y and z
    if is_winner:
        ax.set_title("W" + str(desired_level) + " with size " + str(grid_size))
    else:
        ax.set_title("L" + str(desired_level) + " with size " + str(grid_size))
    ax.set_xlabel("y")
    ax.set_ylabel("z")

    # Render the sheet, converting array's T/F values as 0/1, put (0,0) at the bottom left.
    # Sets minimum value as 0 (white), and maximum value as 1 (black)
    ax.imshow(sheet.astype(np.uint8), cmap="binary", origin="lower", vmin=0, vmax=1)

    # Create step sizes for ~8 tick marks by finding raw step size, using its order of magnitude
    # to pick closest nice-looking step size to the raw step size
    raw_step = max(1, grid_size / 8)
    magnitude = 10 ** int(np.log10(raw_step)) if raw_step >= 1 else 1
    nice_multipliers = [1, 2, 5, 10]
    step = magnitude * min(nice_multipliers, key=lambda n: abs(n * magnitude - raw_step))
    step = max(int(step), 1)

    # Puts tick markers on axes
    major_ticks = np.arange(0, grid_size, step)
    ax.set_xticks(major_ticks)
    ax.set_yticks(major_ticks)

    # Show gridlines for smaller grids
    if grid_size <= 100:
        minor_ticks = np.arange(-0.5, grid_size, 1)
        ax.set_xticks(minor_ticks, minor=True)
        ax.set_yticks(minor_ticks, minor=True)
        ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)
        ax.tick_params(which='minor', bottom=False, left=False)

    plt.show()
