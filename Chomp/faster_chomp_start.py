import numpy as np
import display
# import time 
from numba import njit

@njit
def generate_Wx(Wx, Lx, desired_level):
    if(desired_level == 0): 
        return Wx
    
    # W1 is L0, a horizontal line from z=1, with an added spot at (0,0)
    Wx = Lx.copy()
    Wx[0,0] = True
    for i in range(2, desired_level+1):
        Wx = left_shift(Wx | diagonal(supermex(Wx)))    # New Wx becomes L(I+DM)Wx
    return Wx

@njit
def left_shift(input_sheet):
    """
    Takes in input which is (I+DM)Wx (2d array of size compute_size by compute_size)
    Outputs Tx, which is every entry in input shifted to the left by 1 spot
    """
    compute_size = input_sheet.shape[0]
    Tx = np.zeros((compute_size, compute_size), dtype=np.bool_)  # Empty array with same dimensions and type as Wx
    for z in range(compute_size):
        for y in range(compute_size - 1):
            Tx[z, y] = input_sheet[z, y + 1]
    return Tx

@njit
def diagonal(MWx):
    compute_size = MWx.shape[0]
    z_star = -1
    for z in range(compute_size):
        if MWx[z, 0]:   # If we found a "True" then we found a loser position (z*)
            z_star = z
            break
    if z_star == -1: # No z* found within compute_size means it won't impact our output
        return MWx

    for t in range(z_star+1):   # Add the diagonal
        MWx[z_star-t, t] = True
    
    return MWx

@njit
def supermex(Wx):
    compute_size = Wx.shape[0]

    MWx = np.zeros((compute_size,compute_size), dtype=np.bool_)     # Our MWx is empty
    blocked_diagonals = np.zeros(compute_size*2, dtype=np.bool_)  # We can skip past blocked diagonals, marked by if z+y is a constant
    for y in range(compute_size):   # Scan each column from z = 0 to z = compute_size 
        next_available_z = -1
        for z in range(compute_size):
            if not Wx[z,y] and not blocked_diagonals[z+y]:  # First empty spot is False and not blocked)
                next_available_z = z
                break
        if next_available_z == -1:
            continue
        MWx[next_available_z,y] = True

        if(next_available_z == 0):  # If we are at z=0 then we stop marking losers
            break

        # We don't need to mark all z greater than the first empty spot we found
        # because we will just move to next y column

        # Marking 45 degree diagonal as N
        blocked_diagonals[next_available_z + y] = True
    
    return MWx

#---------------------------- Running Main Function ----------------------------

grid_size = int(input("Size of the grid you want to see:\n"))
is_winner = (input("Winner or loser? (W/L)\n") == 'W')
desired_level = int(input("x-level?\n"))

compute_size = grid_size + desired_level

# Initialize Lx and Wx as all 0s
Lx = np.zeros((compute_size,compute_size),dtype=np.bool_)  
Wx = np.zeros((compute_size,compute_size),dtype=np.bool_)



# Generating L0 (All 1s/losers in row z=1)
Lx[1,:compute_size] = True

# generate_Wx(Wx, Lx, desired_level)   # Warm up benchmark
# start = time.perf_counter()     # Benchmark time start

Wx = generate_Wx(Wx, Lx, desired_level)

# end = time.perf_counter()       # Benchmark time stop
# print(f"Execution time: {end - start:.6f} seconds")



if(is_winner == True):
    # Desired Wx of size grid_size is rows 0 to grid_size and columns 0 to grid_size of Wx
    final_Wx = Wx[:grid_size, :grid_size]  
    # print(final_Wx.astype(int))
    display.output(final_Wx, True, desired_level)
else:
    Lx = supermex(Wx)
    final_Lx = Lx[:grid_size, :grid_size]
    # print(final_Lx.astype(int))
    display.output(final_Lx, False, desired_level)
