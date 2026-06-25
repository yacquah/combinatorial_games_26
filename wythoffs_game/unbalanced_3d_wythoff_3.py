"""'Unbalanced 3D Wythoff' sheet generator.

Normal 3-heap Nim, plus an additional move: remove k chips from
one pile and 3k chips from another pile.
"""

import numpy as np
from numba import njit
from utils.display import output_sheets, parse_sheet_specs

@njit(cache=True)
def supermex(Wx, grid_size):
    """
    Intra-sheet supermex: computes L_x from W_x. 
    """
    Lx = np.zeros((grid_size, grid_size), dtype=np.bool_)
    blocked = np.copy(Wx)

    for y in range(grid_size):
        for z in range(grid_size):
            if not blocked[z, y]:
                Lx[z, y] = True

                # Normal Nim on y
                for t in range(1, grid_size):
                    if y + t < grid_size: blocked[z, y + t] = True
                    else: break

                # Normal Nim on z
                for t in range(1, grid_size):
                    if z + t < grid_size: blocked[z + t, y] = True
                    else: break

                # Unbalanced y:z = 1:3  (y+t, z+3t)
                for t in range(1, grid_size):
                    if y + t < grid_size and z + 3 * t < grid_size: blocked[z + 3 * t, y + t] = True
                    else: break

                # Unbalanced y:z = 3:1  (y+3t, z+t)
                for t in range(1, grid_size):
                    if y + 3 * t < grid_size and z + t < grid_size: blocked[z + t, y + 3 * t] = True
                    else: break
    return Lx

@njit(cache=True)
def compute_sheets(max_size):
    """
    Computes W_history and L_history up to max_size.
    Uses 2D Rolling Accumulators to drop time complexity from O(N^3.5) to O(N^3).
    """
    L_space = np.zeros((max_size, max_size, max_size), dtype=np.bool_)
    W_space = np.zeros((max_size, max_size, max_size), dtype=np.bool_)

    ever_lost = np.zeros((max_size, max_size), dtype=np.bool_) 
    
    # We now need 3 levels of history tracking because of the 3t moves!
    L_prev1 = np.zeros((max_size, max_size), dtype=np.bool_)
    L_prev2 = np.zeros((max_size, max_size), dtype=np.bool_)
    L_prev3 = np.zeros((max_size, max_size), dtype=np.bool_)

    Acc2_prev = np.zeros((max_size, max_size), dtype=np.bool_) # Move 2: (x-t, y-3t)
    
    Acc3_m1   = np.zeros((max_size, max_size), dtype=np.bool_) # Move 3: (x-3t, y-t)
    Acc3_m2   = np.zeros((max_size, max_size), dtype=np.bool_)
    Acc3_m3   = np.zeros((max_size, max_size), dtype=np.bool_) # New deeper history
    
    Acc4_prev = np.zeros((max_size, max_size), dtype=np.bool_) # Move 4: (x-t, z-3t)
    
    Acc5_m1   = np.zeros((max_size, max_size), dtype=np.bool_) # Move 5: (x-3t, z-t)
    Acc5_m2   = np.zeros((max_size, max_size), dtype=np.bool_)
    Acc5_m3   = np.zeros((max_size, max_size), dtype=np.bool_) # New deeper history

    for x in range(max_size):
        if x == 0:
            W_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            Acc2_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            Acc3_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            Acc4_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            Acc5_curr = np.zeros((max_size, max_size), dtype=np.bool_)
        else:
            W_curr = np.copy(ever_lost)

            # Move 2: (x-t, y-3t) -> Shift accumulator by 3 in y
            temp2 = L_prev1 | Acc2_prev
            Acc2_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            if max_size > 3: Acc2_curr[:, 3:] = temp2[:, :-3]  # Shift by 3
            W_curr |= Acc2_curr

            # Move 3: (x-3t, y-t) -> Shift by 1 in y, pulls from x-3!
            temp3 = L_prev3 | Acc3_m3  # Look back 3 levels
            Acc3_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            if max_size > 1: Acc3_curr[:, 1:] = temp3[:, :-1]
            W_curr |= Acc3_curr

            # Move 4: (x-t, z-3t) -> Shift accumulator by 3 in z
            temp4 = L_prev1 | Acc4_prev
            Acc4_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            if max_size > 3: Acc4_curr[3:, :] = temp4[:-3, :]  # Shift by 3
            W_curr |= Acc4_curr

            # Move 5: (x-3t, z-t) -> Shift by 1 in z, pulls from x-3!
            temp5 = L_prev3 | Acc5_m3  # Look back 3 levels
            Acc5_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            if max_size > 1: Acc5_curr[1:, :] = temp5[:-1, :]
            W_curr |= Acc5_curr

        L_curr = supermex(W_curr, max_size)

        W_space[x] = W_curr
        L_space[x] = L_curr

        # -------------------------------------------------------------
        # Shift the Sliding Windows for the next level
        # -------------------------------------------------------------
        if x > 0:
            # Shift the 3-level deep history first
            L_prev3 = L_prev2
            Acc3_m3 = Acc3_m2
            Acc5_m3 = Acc5_m2
            
            L_prev2 = L_prev1
            Acc3_m2 = Acc3_m1
            Acc5_m2 = Acc5_m1

            Acc2_prev = Acc2_curr
            Acc3_m1 = Acc3_curr
            Acc4_prev = Acc4_curr
            Acc5_m1 = Acc5_curr

        L_prev1 = L_curr
        ever_lost |= L_curr

    return W_space, L_space


def main():
    """Prompt for one or more sheet requests and display them together.

    Each requested sheet may have its own type, x-level, and size, e.g.
    ``W8x16, L4x20, W16x32``.
    """
    print("Enter sheets as <W|L><level>x<size>, separated by commas.")
    print("Example: W8x16, L4x20, W16x32")
    specs = parse_sheet_specs(input("Sheets:\n"))

    compute_size = max(max(size, level + 1) for _, level, size in specs)
    W_space, L_space = compute_sheets(compute_size)

    sheets = []
    for is_winner, level, size in specs:
        space = W_space if is_winner else L_space
        sheets.append((space[level, :size, :size], is_winner, level))
    output_sheets(sheets)


if __name__ == "__main__":
    main()
