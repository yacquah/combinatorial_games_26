"""Generates and displays Instant-Winner and Loser sheets for 3-Heap Bounded Wythoff

(x,y,z) --> (x-s,y,z), (x,y-s,z), (x,y,z-s) which are the normal nim moves, 
(x-s,y-t,z) where 0<s<=x and ceiling(s/2)<=t<=min(2s,y), 
(x-s,y,z-t) where 0<s<=x and ceiling(s/2)<=t<=min(2s,z), 
(x,y-s,z-t) where 0<s<=y and ceiling(s/2)<=t<=min(2s,z)
"""

import numpy as np
from numba import njit
from utils.display import run_sheet_session

@njit(cache=True)
def parents(Wx, Lx, x_difference):
    """
    Finds the parents of losing position x sheets above it.
    """
    grid_size = Wx.shape[0]
    # minimum vertical displacement is ceiling(x_difference/2)
    min_displacement = (x_difference + 1) // 2 
    
    for y in range(grid_size):
        for z in range(grid_size):
            if Lx[z, y]:
                # nim move
                Wx[z, y] = True
                
                # maximum displacement is 2*x_difference or grid height
                max_displacement_z = min(2 * x_difference, grid_size - z - 1)
                max_displacement_y = min(2 * x_difference, grid_size - y - 1)
                
                # Shade the vertical and horizontal parents for this loser
                if min_displacement <= max_displacement_z:
                    Wx[z + min_displacement : z + max_displacement_z + 1, y] = True
                if min_displacement <= max_displacement_y:
                    Wx[z, y + min_displacement : y + max_displacement_y + 1] = True
            
                break
    return Wx
                
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
                # We everything above (y, z)
                Tx[z:, y] = True
                # We everything above (y, z)
                Tx[z, y:] = True
                
                for right_displacement in range(1, grid_size - y):
                    # minimum vertical displacement is ceiling(right_displacement/2)
                    min_vertical_displacement = (right_displacement + 1) // 2 
                    
                    # maximum vertical displacement is 2*right_displacement or grid height
                    max_vertical_displacement = min(2 * right_displacement, grid_size - z - 1)
                    
                    if min_vertical_displacement <= max_vertical_displacement:
                        # Shade the vertical slice for this column
                        Tx[z + min_vertical_displacement : z + max_vertical_displacement + 1, 
                           y + right_displacement] = True
                
                break
                
    return Lx

@njit(cache=True)
def compute_sheets(depth, grid_size):
    """
    Computes W sheets and L sheets for x-levels 0..depth-1 over a grid_size grid.

    Depth (number of x-levels) and grid size are decoupled: the returned cubes have
    shape ``(depth, grid_size, grid_size)`` indexed ``[x, z, y]``.
    """
    # Initialize Lx and Wx as all 0s
    L = np.zeros((depth, grid_size, grid_size), dtype=np.bool_)
    W = np.zeros((depth, grid_size, grid_size), dtype=np.bool_)

    for x in range(depth):
        for sheets_below in range(x):
            W[x] |= parents(W[x], L[sheets_below], x-sheets_below)

        L[x] = supermex(W[x])

    return W, L


def main():
    """Prompt for sheets and render them side-by-side."""
    run_sheet_session(compute_sheets, row_is_z=True)


if __name__ == "__main__":
    main()
