import matplotlib.pyplot as plt
import numpy as np

def output(sheet, is_winner, desired_level):

    grid_size = sheet.shape[0]

    _, ax = plt.subplots(figsize=(8, 8), dpi=100)

    if is_winner:
        ax.set_title("W" + str(desired_level) + " with size " + str(grid_size))
    else:
        ax.set_title("L" + str(desired_level) + " with size " + str(grid_size))
    ax.set_xlabel("y")
    ax.set_ylabel("z")

    ax.imshow(sheet.astype(np.uint8), cmap="binary", origin="lower", vmin=0, vmax=1)

    raw_step = max(1, grid_size / 8)
    magnitude = 10 ** int(np.log10(raw_step)) if raw_step >= 1 else 1
    nice_multipliers = [1, 2, 5, 10]
    step = magnitude * min(nice_multipliers,
                           key=lambda n: abs(n * magnitude - raw_step))
    step = max(int(step), 1)

    major_ticks = np.arange(0, grid_size, step) #puts a major tick 
    ax.set_xticks(major_ticks)
    ax.set_yticks(major_ticks)

    if grid_size <= 100:    # Only show gridlines if we don't want so many positions
        minor_ticks = np.arange(-0.5, grid_size, 1)
        ax.set_xticks(minor_ticks, minor=True)
        ax.set_yticks(minor_ticks, minor=True)
        ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)
        ax.tick_params(which='minor', bottom=False, left=False)

    #plt.tight_layout()
    plt.show()
