"""
chomp:
Calculates the winning (Wx) and losing (Lx) states for the game of Chomp 
up to a user-specified x-level using combinatorial game theory.

mathematical process:
1. Chomp states can be represented on a 2D grid where moves block states diagonally.
2. We transition between levels recursively using a custom recursive operator:
   Wx = left_shift( Wx | diagonal( supermex(Wx) ) )
3. Level 0 (L0) is initialized structurally as a baseline of losers in row z=1.

optimization process:
- Pure Python loops are too slow for large game grids (e.g., 500x500).
- We implemented Numba's `@njit` decorator to compile our nested loops into native 
  machine code, accelerating our calculation speeds by orders of magnitude.
- We utilize NumPy boolean arrays for memory-efficient state tracking.
"""

import numpy as np
import display
from numba import njit
# import time

def main():
    """Collect custom execution parameters from user terminal inputs"""

    grid_size = int(input("Size of the grid you want to see:\n"))
    is_winner = input("Winner or loser? (W/L)\n") == 'W'
    desired_level = int(input("x-level?\n"))

    # critical step: Compute Size Padding
    # Because bit-shifting moves array data leftward, we scale our workspace
    # up by adding the desired level to our grid size. This provides an internal safety
    # padding so values do not get dropped or cut off out-of-bounds mid-calculation
    compute_size = grid_size + desired_level

    # Initialize Lx and Wx as all 0s
    Lx = np.zeros((compute_size,compute_size),dtype=np.bool_)
    Wx = np.zeros((compute_size,compute_size),dtype=np.bool_)

    # Generating L0 (All 1s/losers in row z=1)
    Lx[1,:compute_size] = True

    # If asked for L0, directly display it
    if not is_winner and desired_level==0:
        final_Lx = Lx[:grid_size, :grid_size]
        display.output(final_Lx, False, desired_level)

    else:
        # generate_Wx(Wx, Lx, desired_level)   # Warm up benchmark
        # start = time.perf_counter()     # Benchmark time start

        # Run our optimized logic tree functions to evaluate the boards
        Wx = generate_Wx(Wx, Lx, desired_level)

        # end = time.perf_counter()       # Benchmark time stop
        # print(f"Execution time: {end - start:.6f} seconds")

        # Output Routing: Clean and display the data
        if is_winner:
            # Slice the padded matrix down to the requested size to drop the computational padding
            final_Wx = Wx[:grid_size, :grid_size]
            display.output(final_Wx, True, desired_level)
        else:
            # Evaluate final losing states via our extraction algorithm
            Lx = supermex(Wx)
            # Slice matrix to clean size bounds
            final_Lx = Lx[:grid_size, :grid_size]
            display.output(final_Lx, False, desired_level)

@njit
def generate_Wx(Wx, Lx, desired_level):
    """Iteratively build the instant-winner sheet W_x up to ``desired_level``.
    Args:
        Wx: Boolean grid representing the current instant-winner sheet.
        Lx: Boolean grid representing the current loser sheet
        desired_level: Target x-level to compute.

    Returns:
        The updated boolean grid for W_desired_level.
    """
    if desired_level == 0:
        return Wx

    # W1 is L0, a horizontal line from z=1, with an added spot at (0,0)
    Wx = Lx.copy()
    Wx[0,0] = True
    for _ in range(2, desired_level+1):
        Wx = left_shift(Wx | diagonal(supermex(Wx)))    # New Wx becomes L(I+DM)Wx
    return Wx

@njit
def left_shift(input_sheet):
    """
    takes in input which is (I+DM)Wx (2d array of size compute_size by compute_size)
    outputs Tx, which is every entry in input shifted to the left by 1 spot

    shifts every entry in the 2D grid exactly 1 space to the left along the y-axis.

    why this is part of our process:
    - The Chomp game operator dictates a structural shift in coordinates 
      as game complexity scales up per layer level.

    parameters:
    input_sheet : np.ndarray
        The current (I + DM)Wx grid layer of size (compute_size x compute_size).

    returns:
    Tx : np.ndarray
        The spatially translated grid sheet.
    """
    compute_size = input_sheet.shape[0]
    # Empty array with same dimensions and type as Wx
    Tx = np.zeros((compute_size, compute_size), dtype=np.bool_)
    for z in range(compute_size):
    # we stop at column index 'compute_size - 1' to avoid lookahead index crashes
        for y in range(compute_size - 1):
            # take the state from the right neighbor (y + 1) and pull it left (y)
            Tx[z, y] = input_sheet[z, y + 1]
    return Tx

@njit
def diagonal(MWx):

    """
    Locates the first losing position along the left boundary axis and projects 
    a 45-degree diagonal line of true game entries across the grid workspace.

    parameters:
    MWx : np.ndarray
        The move extraction grid populated by the supermex routine.

    returns:
    np.ndarray
        The grid updated with the structural diagonal boundary wall.
    """

    compute_size = MWx.shape[0]
    z_star = -1 # Initialize our pointer variable to an invalid state
    # process step 1: Search column 0 vertically to identify our critical state (z*)
    for z in range(compute_size):
        if MWx[z, 0]:   # If we found a "True" then we found a loser position (z*)
            z_star = z
            break # Immediately break loop to save computation time
    if z_star == -1: # No z* found within compute_size means it won't impact our output
        return MWx

# process step 2: Plot the downward diagonal lines branching from our z* coordinate
    for t in range(z_star+1):   # Add the diagonal
    # traces a 45-degree diagonal down-right by subtracting row indices
    # while adding column indices
        MWx[z_star-t, t] = True

    return MWx

@njit
def supermex(Wx):
    """
    Core move for Chomp.
    
    Why this is unique to Chomp:
    - Unlike Nim, which blocks flat rows, Chomp geometry requires blocking game states 
      diagonally. Positions on the same 45-degree diagonal share a unique signature (z + y).

    parameters:
    Wx : np.ndarray
        The compiled winning game-state sheet.

    returns:
    MWx : np.ndarray
        A fresh grid containing newly uncovered move transitions.
    """
    compute_size = Wx.shape[0]

    MWx = np.zeros((compute_size,compute_size), dtype=np.bool_)     # Our MWx is empty
    # We can skip past blocked diagonals, marked by if z+y is a constant
    blocked_diagonals = np.zeros(compute_size*2, dtype=np.bool_)
    for y in range(compute_size):   # Scan each column from z = 0 to z = compute_size
        next_available_z = -1
        # Scan through the rows in this current column
        for z in range(compute_size):
            # First empty spot is False and not blocked)
            if not Wx[z,y] and not blocked_diagonals[z+y]:
                next_available_z = z
                break

        # If the entire column yields no valid open index, skip to the next column
        if next_available_z == -1:
            continue
        # Log this valid location on our tracking sheet
        MWx[next_available_z,y] = True

        if next_available_z == 0: # If we are at z=0 then we stop marking losers
            break

        # We don't need to mark all z greater than the first empty spot we found
        # because we will just move to next y column

        # Marking 45 degree diagonal as N
        # Lock this 45-degree diagonal path (z + y) so subsequent loops cannot reuse it
        blocked_diagonals[next_available_z + y] = True

    return MWx

#---------------------------- Running Main Function ----------------------------
if __name__ == "__main__":
    main()
