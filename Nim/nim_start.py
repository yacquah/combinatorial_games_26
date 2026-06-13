import numpy as np
import display

# There's an option to use for loops + njit instead of using np.arange/np.where
# for faster code

def generate_Wx(Wx, desired_level, grid_size):
    if(desired_level == 0): 
        return Wx
    for i in range(1, desired_level+1):
        Wx = Wx | supermex(Wx,grid_size)    # New Wx becomes Wx + MWx
    return Wx

def supermex(Wx, grid_size):
    MWx = np.zeros((grid_size,grid_size), dtype=np.bool_)     # Our MWx is empty
    Tx = np.copy(Wx)    # Editable copy of Wx
    for y in range(grid_size):
        z_indices = np.where(~Tx[:, y])[0]
        if z_indices.size == 0:
            continue
        next_available_z = z_indices[0]
        
        MWx[next_available_z,y] = True
        # We don't need to mark all z greater as N, only all y greater (horizontal)
        Tx[next_available_z,y:] = True
    return MWx

#---------------------------- Running Main Function ----------------------------

grid_size = int(input("Size of the grid you want to see:\n"))
is_winner = (input("Winner or loser? (W/L)\n") == 'W')
desired_level = int(input("x-level?\n"))

# Initialize Wx as all 0s. We don't need Lx because in Nim, W0 = MW0
Wx = np.zeros((grid_size,grid_size),dtype=np.bool_)

Wx = generate_Wx(Wx, desired_level, grid_size)

if(is_winner == True):
    # print(Wx.astype(int))
    display.output(Wx, grid_size, True, desired_level)
else:
    Lx = supermex(Wx, grid_size)
    # print(Lx.astype(int))
    display.output(Lx, grid_size, False, desired_level)
