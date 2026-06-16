import numpy as np
import display
from numba import njit
# import time

# Using loops + njit instead of using np.arange/np.where for faster code

@njit
def generate_Wx(Wx, desired_level):
    if(desired_level == 0): 
        return Wx
    for i in range(1, desired_level+1):
        Wx |= supermex(Wx)    # New Wx becomes Wx + MWx
    return Wx

@njit
def supermex(Wx):
    grid_size = Wx.shape[0]
    MWx = np.zeros((grid_size,grid_size), dtype=np.bool_)     # Our MWx is empty
    blocked_rows = np.zeros(grid_size, dtype=np.bool_)

    for y in range(grid_size):  # Loop through each column 
        next_available_z = -1
        for z in range(grid_size):
            if not Wx[z, y] and not blocked_rows[z]:    # If the position is 0 (loser) 
                                                        # and not in a row marked as N,
                                                        # then mark that z 
                next_available_z = z
                break

        if next_available_z == -1:  # No z found means we go to next y column
            continue

        MWx[next_available_z,y] = True
        blocked_rows[next_available_z] = True

    return MWx

#---------------------------- Running Main Function ----------------------------

grid_size = int(input("Size of the grid you want to see:\n"))
is_winner = (input("Winner or loser? (W/L)\n") == 'W')
desired_level = int(input("x-level?\n"))

# Initialize Wx as all 0s. We don't need Lx because in Nim, W0 = MW0
Wx = np.zeros((grid_size,grid_size),dtype=np.bool_)

# generate_Wx(Wx, desired_level)   # Warm up benchmark
# start = time.perf_counter()     # Benchmark time start

Wx = generate_Wx(Wx, desired_level)

# end = time.perf_counter()       # Benchmark time stop
# print(f"Execution time: {end - start:.6f} seconds")

if(is_winner == True):
    # print(Wx.astype(int))
    display.output(Wx, True, desired_level)
else:
    Lx = supermex(Wx)
    # print(Lx.astype(int))
    display.output(Lx, False, desired_level)

    
