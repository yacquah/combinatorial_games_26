import numpy as np
from numba import njit
from utils.display import output, output_multiple

@njit
def supermex_euclid(Wx, x, max_size):
    """
    Applies the Supermex operator for 3-Heap Euclid's Game to find L_x.
    Evaluates only intra-sheet moves that stay on the current x-level.
    """
    # Arrays are indexed as [z, y] to match matplotlib axes
    Lx = np.zeros((max_size, max_size), dtype=np.bool_)
    blocked = np.copy(Wx)

    for y in range(max_size):
        for z in range(max_size):
            
            # If the state hasn't been blocked by a Wx win or a lower Lx ray, it's a Loser
            if not blocked[z, y]:
                Lx[z, y] = True
                # Rays involving x
                if x > 0:
                    # Subtracting kx from y (ray moves forward along y)
                    k = 1
                    while y + k * x < max_size:
                        blocked[z, y + k * x] = True
                        k += 1
                        
                    # Subtracting kx from z (ray moves forward along z)
                    k = 1
                    while z + k * x < max_size:
                        blocked[z + k * x, y] = True
                        k += 1
                        
                # Rays involving z
                if z > 0:
                    # Subtracting kz from y
                    k = 1
                    while y + k * z < max_size:
                        blocked[z, y + k * z] = True
                        k += 1
                        
                # Rays involving y
                if y > 0:
                    # Subtracting ky from z
                    k = 1
                    while z + k * y < max_size:
                        blocked[z + k * y, y] = True
                        k += 1

    return Lx

@njit
def compute_euclid_space(max_size):
    """
    Computes the W and L sheets iteratively
    """
    # 3D History arrays indexed as [x, z, y]
    L_history = np.zeros((max_size, max_size, max_size), dtype=np.bool_)
    W_history = np.zeros((max_size, max_size, max_size), dtype=np.bool_)

    for x in range(max_size):
        Wx = np.zeros((max_size, max_size), dtype=np.bool_)

        # Step 1: Inter-sheet moves (Looking back at smaller x)
        # If x == 0, W0 correctly remains completely blank
        if x > 0:
            for y in range(max_size):
                for z in range(max_size):
                    can_win = False
                    
                    # Inter-sheet Move 1: Reduce x by multiples of y
                    if y > 0:
                        k = 1
                        while x - k * y >= 0:
                            if L_history[x - k * y, z, y]:
                                can_win = True
                                break
                            k += 1
                    
                    # Inter-sheet Move 2: Reduce x by multiples of z
                    if not can_win and z > 0:
                        k = 1
                        while x - k * z >= 0:
                            if L_history[x - k * z, z, y]:
                                can_win = True
                                break
                            k += 1
                            
                    Wx[z, y] = can_win
                    
        W_history[x] = Wx
        
        # Step 2: Intra-sheet moves (Supermex computes Lx from Wx)
        L_history[x] = supermex_euclid(Wx, x, max_size)

    return W_history, L_history


def main():
    """Prompt for a Euclid's Game sheet request, compute it, and display the result."""
    
    grid_size = int(input("Size of the grid you want to see (y and z axes):\n"))
    is_winner = input("Winner or loser? (W/L)\n").strip().upper() == 'W'
    levels_input = input("x-level(s)? (Separate multiple with commas):\n")
    desired_levels = [int(x.strip()) for x in levels_input.split(',')]

    max_desired_level = max(desired_levels)
    compute_size = max(grid_size, max_desired_level + 1)

    Wx, Lx = compute_euclid_space(compute_size)

    if len(desired_levels) == 1:
        level = desired_levels[0]
        if is_winner:
            sheet = Wx[level, :grid_size, :grid_size]
            output(sheet, True, level)
        else:
            sheet = Lx[level, :grid_size, :grid_size]
            output(sheet, False, level)

    else:
        sheets_to_display = []
        titles = []
        
        for level in desired_levels:
            if is_winner:
                sheets_to_display.append(Wx[level, :grid_size, :grid_size])
                titles.append(f"W{level} with size {grid_size}")
            else:
                sheets_to_display.append(Lx[level, :grid_size, :grid_size])
                titles.append(f"L{level} with size {grid_size}")
                
        output_multiple(sheets_to_display, titles)

if __name__ == "__main__":
    main()
