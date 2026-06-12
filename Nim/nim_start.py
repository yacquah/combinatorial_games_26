import numpy as np
#import mex
import display
import mex

def generate_Wx(Wx, Lx, desired_level, grid_size):
    if(desired_level == 0): 
        return Wx
    for i in range(1, desired_level+1):
        Wx = Wx | supermex(Wx,grid_size)    # New Wx becomes Wx + MWx
    return Wx

def supermex(Wx, grid_size):
    MWx = np.zeros((grid_size,grid_size), dtype=int)     # Our MWx is empty
    Tx = np.copy(Wx)
    while not np.all(Tx == 1):
        next_available_z, next_available_y = mex.find_next_L(Tx,grid_size)
        MWx[next_available_z][next_available_y] = 1
        for t in range(next_available_z, grid_size):
            Tx[t][next_available_y] = 1
        for t in range(next_available_y, grid_size):
            Tx[next_available_z][t] = 1
    return MWx

#---------------------------- Running Main Function ----------------------------

grid_size = int(input("Size of the grid you want to see:\n"))
is_winner = (input("Winner or loser? (W/L)\n") == 'W')
desired_level = int(input("x-level?\n"))

Lx = np.zeros((grid_size,grid_size),dtype=int)  # Initialize Lx and Wx as all 0s
Wx = np.zeros((grid_size,grid_size),dtype=int)

for i in range(grid_size):   # Generating L0
    Lx[i][i] = 1

Wx = generate_Wx(Wx, Lx, desired_level, grid_size)

if(is_winner == True):
    print(Wx)
    display.output(Wx, grid_size, True, desired_level)
else:
    print(supermex(Wx,grid_size))
    display.output(supermex(Wx), grid_size, False, desired_level)
