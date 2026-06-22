"""Generate and display finite instant-winner and loser sheets for three-heap Subtract a Square.

This script computes two-dimensional slices using the
``supermex`` operator. The x-coordinate is treated as the sheet level, while the
rendered grid coordinates are y and z.
"""

import numpy as np
from numba import njit
from utils.display import output

@njit
def get_squares(max_val):
    """Precompute a 1D array of all perfect squares up to max_val."""
    squares = []
    i = 1
    while i * i <= max_val:
        squares.append(i * i)
        i += 1
    return np.array(squares)

@njit
def compute_subtract_a_square(max_size):
    """
    Computes the W and L sheets for 3-Heap Subtract a Square.
    
    Returns:
        W: 3D boolean array of Instant-N positions.
        L: 3D boolean array of Loser (P-positions).
    """
    # Precompute our squares array to avoid doing math in the tight loops
    squares = get_squares(max_size)

    L = np.zeros((max_size, max_size, max_size), dtype=np.bool_)
    W = np.zeros((max_size, max_size, max_size), dtype=np.bool_)

    # Iterate through the levels from bottom up
    for x in range(max_size):

        # A temporary 2D tracking grid for the current x-level.
        # True means the position is blocked from being a Loser.
        blocked = np.zeros((max_size, max_size), dtype=np.bool_)

        # ---------------------------------------------------------
        # STEP 1: The Look-back (Compute W_x)
        # ---------------------------------------------------------
        for y in range(max_size):
            for z in range(max_size):
                for sq in squares:
                    if sq > x:
                        break # Stop looking if the square is bigger than our heap

                    # If subtracting a square lands on a known lower L-sheet
                    if L[x - sq, y, z]:
                        blocked[y, z] = True  # It's a winner, block it from being an L
                        W[x, y, z] = True
                        break

        # ---------------------------------------------------------
        # STEP 2: The Forward Sieve (Supermex for L_x)
        # ---------------------------------------------------------
        for y in range(max_size):
            for z in range(max_size):

                # If this position survived the inter-sheet look-back AND 
                # all previous intra-sheet blocking rays, it is a Loser!
                if not blocked[y, z]:
                    L[x, y, z] = True

                    # Fire blocking rays FORWARD along the y-axis
                    for sq in squares:
                        if y + sq < max_size:
                            blocked[y + sq, z] = True
                        else:
                            break # Array of squares is sorted, so we can safely break

                    # Fire blocking rays FORWARD along the z-axis
                    for sq in squares:
                        if z + sq < max_size:
                            blocked[y, z + sq] = True
                        else:
                            break

    return W, L


def main():
    """Prompt for a Subtract a Square sheet request, compute it, and display the result."""

    grid_size = int(input("Size of the grid you want to see (y and z axes):\n"))
    is_winner = input("Winner or loser? (W/L)\n").strip().upper() == 'W'
    desired_level = int(input("x-level?\n"))

    # Decouple the display size from the computational bounds to prevent crashes.
    # We must calculate up to at least the desired x-level, plus whatever view size is requested.
    compute_size = max(grid_size, desired_level + 1)

    # Generate the full 3D game space up to our safe computational bounds
    print(f"Computing 3D space up to size {compute_size}... this might take a moment for large grids.")
    W_space, L_space = compute_subtract_a_square(compute_size)

    # Slice out the specific 2D sheet the user requested, trimmed to their viewing size
    if is_winner:
        sheet = W_space[desired_level, :grid_size, :grid_size]
        output(sheet, True, desired_level)
    else:
        sheet = L_space[desired_level, :grid_size, :grid_size]
        output(sheet, False, desired_level)

if __name__ == "__main__":
    main()
