import matplotlib.pyplot as plt
import numpy as np

def output(sheet, grid_size, is_winner, desired_level):

    fig, ax = plt.subplots(figsize=(8, 8))

    if(is_winner == True):
        ax.set_title("W" + str(desired_level) + " with size " + str(grid_size))
    else:
        ax.set_title("L" + str(desired_level) + " with size " + str(grid_size))
    ax.set_xlabel("y")
    ax.set_ylabel("z")

    ax.imshow(sheet, cmap="binary", origin="lower", vmin=0, vmax=1)
    major_ticks = np.arange(0, grid_size, 10) #puts a major tick 
    ax.set_xticks(major_ticks)
    ax.set_yticks(major_ticks)
    minor_ticks = np.arange(-0.5, grid_size, 1)
    ax.set_xticks(minor_ticks, minor=True)
    ax.set_yticks(minor_ticks, minor=True)

    # Turn on the grid lines for the minor ticks only
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)

    # Hide the little tick marks for the minor ticks so it looks clean
    ax.tick_params(which='minor', bottom=False, left=False)

    plt.show()