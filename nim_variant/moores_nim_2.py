"""Moore's Nim with 3 heaps and removing from up to two heaps sheet generator.

3 heaps and you can remove any number of chips from up to two piles
"""

import numpy as np
from numba import njit
from utils.display import output

@njit(cache=True)
def supermex(Wx):
    """
    Intra-sheet supermex: computes L_x from W_x. 
    """
    grid_size = Wx.shape[0]
    
    Lx = np.zeros((grid_size, grid_size), dtype=np.bool_)
    
    Tx = Wx.copy()

    for y in range(grid_size):
        for z in range(grid_size):
            if not Tx[z, y]:
                Lx[z, y] = True
                # We checked everything up and to the right of (y, z)
                Tx[z:, y:] = True
                
                break
                
    return Lx

@njit(cache=True)
def y_fill(input_sheet):
    """
    Acts on Lx and extends each loser into its row (y-axis)

    parameters:
    input_sheet : np.ndarray
        The current Lx grid layer.

    returns:
    Tx : np.ndarray
        The array with y-rows filled in with winners
    """
    grid_size = input_sheet.shape[0]
    # Empty array with same dimensions and type as input_sheet
    Tx = np.zeros((grid_size, grid_size), dtype=np.bool_)
    
    # Iterate through every row (z) and column (y)
    for z in range(grid_size):
        loser_found = False
        for y in range(grid_size):
            # If a previous cell in this row was a loser, mark current cell as True
            if loser_found:
                Tx[z, y] = True
                
            # If the current cell is a P-position, fill in all future cells in this row
            if input_sheet[z, y]:
                loser_found = True
                
    return Tx

@njit(cache=True)
def z_fill(input_sheet):
    """
    Acts on Lx and extends each loser into its column (z-axis).

    parameters:
    input_sheet : np.ndarray
        The current Lx grid layer.

    returns:
    Tx : np.ndarray
        The array with z-columns filled in with winners.
    """
    grid_size = input_sheet.shape[0]
    # Empty array with same dimensions and type as input_sheet
    Tx = np.zeros((grid_size, grid_size), dtype=np.bool_)
    
    # Iterate through every column (y) and row (z)
    for y in range(grid_size):
        loser_found = False
        for z in range(grid_size):
            # If a previous cell in this column was a loser, mark current cell as True
            if loser_found:
                Tx[z, y] = True
                
            # If the current cell is a P-position, fill in all future cells in this column
            if input_sheet[z, y]:
                loser_found = True
                
    return Tx

@njit(cache=True)
def compute_sheets(desired_level, grid_size):
    """
    Computes W sheets and L sheets up to desired x-level. 
    """
    # Initialize Lx and Wx as all 0s
    Lx = np.zeros((grid_size,grid_size),dtype=np.bool_)
    Wx = np.zeros((grid_size,grid_size),dtype=np.bool_)

    Lx = supermex(Wx)

    for _ in range(desired_level):
        Wx = Wx | Lx | y_fill(Lx) | z_fill(Lx)
        Lx = supermex(Wx)

    return Wx, Lx


def main():
    """Prompt for sheets"""
    
    grid_size = int(input("Size of the grid you want to see:\n"))
    is_winner = input("Winner or loser? (W/L)\n") == 'W'
    desired_level = int(input("x-level?\n"))

    Wx, Lx = compute_sheets(desired_level, grid_size)

    if is_winner:
        output(Wx, True, desired_level)
    else:
        output(Lx, False, desired_level)


if __name__ == "__main__":
    main()
