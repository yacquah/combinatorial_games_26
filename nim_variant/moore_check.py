"""Check Moore's Nim_2 losers with formula 
A position is a loser iff the binary representation of heap sizes added together 
without carrying is 0 mod(k+1). In this case k=2.
"""

import numpy as np
from numba import njit
from utils.display import output

@njit(cache=True)
def check_columns_mod3(x, y, z):
    """
    Checks if the sum of bits at every binary column position mod 3 == 0.
    """
    while x > 0 or y > 0 or z > 0:
        # Sum the least significant bits of x, y, and z
        col_sum = (x & 1) + (y & 1) + (z & 1)
        
        # If any column sum is not divisible by 3, return False
        if col_sum % 3 != 0:
            return False
            
        # Shift all numbers right by 1 bit to process the next column
        x >>= 1
        y >>= 1
        z >>= 1
        
    return True

@njit(cache=True)
def calculate_grid(grid_size, desired_level):
    """Mark each position in Lx as loser if the column sum is 0 mod 3"""
    Lx = np.zeros((grid_size, grid_size), dtype=np.bool_)
    
    for y in range(grid_size):
        for z in range(grid_size):
            Lx[z, y] = check_columns_mod3(desired_level, y, z)
            
    return Lx

def main():
    """Prompt for sheets and calculate losers"""
    grid_size = int(input("Size of the grid you want to see:\n"))
    desired_level = int(input("x-level?\n"))

    Lx = calculate_grid(grid_size, desired_level)
    output(Lx, False, desired_level)


if __name__ == "__main__":
    main()
