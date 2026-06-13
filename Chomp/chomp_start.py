import numpy as np
import display

def generate_Wx(Wx, Lx, desired_level, compute_size):
    if(desired_level == 0): 
        return Wx
    
    # W1 is L0, a horizontal line from z=1, with an added spot at (0,0)
    Wx = np.copy(Lx)
    Wx[0,0] = True
    for i in range(2, desired_level+1):
        Wx = left_shift(Wx | diagonal(supermex(Wx,compute_size)))    # New Wx becomes L(I+DM)Wx
    return Wx

def left_shift(input_sheet):
    """
    Takes in input which is (I+DM)Wx (2d array of size compute_size by compute_size)
    Outputs Tx, which is every entry in input shifted to the left by 1 spot
    """
    Tx = np.zeros_like(input_sheet)  # Empty array with same dimensions and type as Wx
    Tx[:, :-1] = input_sheet[:, 1:]  # For all rows, copy index 1 to end of Wx
                            # and paste to index 0 to second-last column of Tx
    return Tx

def diagonal(MWx):
    Tx = np.copy(MWx)
    z_indices = np.where(MWx[:, 0])[0]     # Gives an array of all z-values where (0, z*) is loser
    if z_indices.size == 0: # No z* found within compute_size means it won't impact our output
        return Tx
    z_star = z_indices[0]

    t = np.arange(z_star+1) 
    Tx[z_star-t, t] = True
    
    return Tx

def supermex(Wx, compute_size):
    MWx = np.zeros((compute_size,compute_size), dtype=np.bool_)     # Our MWx is empty
    Tx = np.copy(Wx)    # Editable copy of Wx
    for y in range(compute_size): # Scan each column from z = 0 to z = compute_size
        z_indices = np.where(~Tx[:, y])[0]  # Gives an array of the z-values in 
                                            #the y column where (y,z) is 0 (first empty space)
        if z_indices.size == 0: # If we find no empty spots, move to the next column
            continue

        next_available_z = z_indices[0]

        MWx[next_available_z,y] = True

        if(next_available_z == 0):  # If we are at z=0 then we stop marking losers
            break

        # We don't need to mark all z greater than the first empty spot we found
        # because we will just move to next y column

        # Marking 45 degree diagonal as N
        steps = min(next_available_z, compute_size-1-y)
        t = np.arange(steps+1)
        Tx[next_available_z-t, y+t] = True
    
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

Wx = generate_Wx(Wx, Lx, desired_level, compute_size)

if(is_winner == True):
    # Desired Wx of size grid_size is rows 0 to grid_size and columns 0 to grid_size of Wx
    final_Wx = Wx[:grid_size, :grid_size]  
    # print(final_Wx.astype(int))
    display.output(final_Wx, grid_size, True, desired_level)
else:
    Lx = supermex(Wx, compute_size)
    final_Lx = Lx[:grid_size, :grid_size]
    # print(final_Lx.astype(int))
    display.output(final_Lx, grid_size, False, desired_level)
