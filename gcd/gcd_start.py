"""Generate and display finite instant-winner and loser sheets for 3-heap GCD.

The 3-heap GCD game: positions are three piles (x, y, z). A move picks two of
the piles, computes their greatest common divisor g, and subtracts any positive
multiple of g from the remaining (third) pile.

Following the renormalization framework (Friedman & Landsberg), x is treated as
the sheet level and [y, z] as the in-sheet coordinates. Moves split into:
  * Inter-sheet moves: subtract k*gcd(y, z) from x  -> lands on a lower sheet x'.
  * Intra-sheet moves: subtract k*gcd(x, z) from y, or k*gcd(x, y) from z.

W_x (instant-winner sheet) marks positions with a move to a loser on a *lower*
sheet, so W_0 is necessarily blank. The supermex operator then turns W_x into
the loser sheet L_x by resolving the intra-sheet moves.
"""

import numpy as np
from numba import njit
from utils.display import output, output_multiple

@njit
def precompute_gcds(max_size):
    """Precompute all GCDs up to max_size into an O(1) lookup table."""
    gcd_table = np.zeros((max_size, max_size), dtype=np.int32)
    for i in range(max_size):
        for j in range(max_size):
            a, b = i, j
            while b:
                a, b = b, a % b
            gcd_table[i, j] = a
    return gcd_table

@njit
def supermex_gcd(Wx, x, max_size, gcd_table):
    """
    O(N^2) Supermex using Step-Parameterized Accumulators.
    Eliminates the 'k' loop by propagating the block from the previous step.
    """
    Lx = np.zeros((max_size, max_size), dtype=np.bool_)
    ray_Y = np.zeros((max_size, max_size), dtype=np.bool_)
    ray_Z = np.zeros((max_size, max_size), dtype=np.bool_)

    for y in range(max_size):
        gz = gcd_table[x, y]
        for z in range(max_size):
            gy = gcd_table[x, z]

            # Accumulate Y-axis blocks based on step size gy
            if gy > 0 and y - gy >= 0:
                ray_Y[z, y] = Lx[z, y - gy] or ray_Y[z, y - gy]
                
            # Accumulate Z-axis blocks based on step size gz
            if gz > 0 and z - gz >= 0:
                ray_Z[z, y] = Lx[z - gz, y] or ray_Z[z - gz, y]

            # If it survived inter-sheet wins and intra-sheet rays, it's a Loser
            if not Wx[z, y] and not ray_Y[z, y] and not ray_Z[z, y]:
                Lx[z, y] = True

    return Lx

@njit
def compute_gcd_space(max_size):
    """
    Computes W and L sheets iteratively in O(N^3) time.
    """
    L_history = np.zeros((max_size, max_size, max_size), dtype=np.bool_)
    W_history = np.zeros((max_size, max_size, max_size), dtype=np.bool_)
    
    gcd_table = precompute_gcds(max_size)

    for x in range(max_size):
        # We can write directly to the W_history slice to act as our accumulator
        if x > 0:
            for y in range(max_size):
                for z in range(max_size):
                    g = gcd_table[y, z]
                    
                    # Inherit the boolean state from the previous jump of size g
                    if g > 0 and x - g >= 0:
                        W_history[x, z, y] = L_history[x - g, z, y] or W_history[x - g, z, y]

        # Pass the accumulated Wx slice to the optimized supermex
        L_history[x] = supermex_gcd(W_history[x], x, max_size, gcd_table)

    return W_history, L_history


def main():
    """Prompt for a GCD-game sheet request, compute it, and display it."""

    grid_size = int(input("Size of the grid you want to see (y and z axes):\n"))
    is_winner = input("Winner or loser? (W/L)\n").strip().upper() == 'W'

    levels_input = input("x-level(s)? (Separate multiple with commas):\n")
    desired_levels = [int(x.strip()) for x in levels_input.split(',')]

    # Calculate up to the highest requested x-level
    max_desired_level = max(desired_levels)
    compute_size = max(grid_size, max_desired_level + 1)

    W_space, L_space = compute_gcd_space(compute_size)

    # If the user only asked for 1 level, use the normal output function
    if len(desired_levels) == 1:
        level = desired_levels[0]
        if is_winner:
            sheet = W_space[level, :grid_size, :grid_size]
            output(sheet, True, level)
        else:
            sheet = L_space[level, :grid_size, :grid_size]
            output(sheet, False, level)
            
    # If they asked for multiple, package them up for output_multiple
    else:
        sheets_to_display = []
        titles = []
        
        for level in desired_levels:
            if is_winner:
                sheets_to_display.append(W_space[level, :grid_size, :grid_size])
                titles.append(f"W{level} with size {grid_size}")
            else:
                sheets_to_display.append(L_space[level, :grid_size, :grid_size])
                titles.append(f"L{level} with size {grid_size}")
                
        output_multiple(sheets_to_display, titles)


if __name__ == "__main__":
    main()
