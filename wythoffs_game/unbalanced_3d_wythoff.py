"""'Unbalanced 3D Wythoff' sheet generator.

Normal 3-heap Nim, PLUS an unbalanced joint move: remove k chips from
one pile and 2k chips from another pile (any of the 3 ordered pile-pairs).
"""

import numpy as np
from numba import njit
from utils.display import output

@njit
def supermex(Wx, grid_size):
    """
    Intra-sheet supermex: computes L_x from W_x. 
    Because Losers are sparse, the ray-firing inside only executes O(N) times
    per sheet, making this function strictly O(N^2) overall per sheet.
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

                # Unbalanced y:z = 1:2  (y+t, z+2t)
                for t in range(1, grid_size):
                    if y + t < grid_size and z + 2 * t < grid_size: blocked[z + 2 * t, y + t] = True
                    else: break

                # Unbalanced y:z = 2:1  (y+2t, z+t)
                for t in range(1, grid_size):
                    if y + 2 * t < grid_size and z + t < grid_size: blocked[z + t, y + 2 * t] = True
                    else: break
    return Lx

@njit
def compute_variant_space(max_size):
    """
    Computes W_history and L_history up to max_size.
    Uses 2D Rolling Accumulators to drop time complexity from O(N^3.5) to O(N^3).
    """
    # Allocate the 3D space strictly to return it to the user.
    L_space = np.zeros((max_size, max_size, max_size), dtype=np.bool_)
    W_space = np.zeros((max_size, max_size, max_size), dtype=np.bool_)

    # -------------------------------------------------------------
    # Sliding Window 2D Accumulators
    # -------------------------------------------------------------
    ever_lost = np.zeros((max_size, max_size), dtype=np.bool_) # Move 1 (x-t)
    
    L_prev1 = np.zeros((max_size, max_size), dtype=np.bool_)
    L_prev2 = np.zeros((max_size, max_size), dtype=np.bool_)

    Acc2_prev = np.zeros((max_size, max_size), dtype=np.bool_) # Move 2: (x-t, y-2t)
    
    Acc3_m1   = np.zeros((max_size, max_size), dtype=np.bool_) # Move 3: (x-2t, y-t)
    Acc3_m2   = np.zeros((max_size, max_size), dtype=np.bool_)
    
    Acc4_prev = np.zeros((max_size, max_size), dtype=np.bool_) # Move 4: (x-t, z-2t)
    
    Acc5_m1   = np.zeros((max_size, max_size), dtype=np.bool_) # Move 5: (x-2t, z-t)
    Acc5_m2   = np.zeros((max_size, max_size), dtype=np.bool_)

    for x in range(max_size):
        if x == 0:
            W_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            Acc2_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            Acc3_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            Acc4_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            Acc5_curr = np.zeros((max_size, max_size), dtype=np.bool_)
        else:
            # Move 1: Normal Nim on x contributes all previously found Losers
            W_curr = np.copy(ever_lost)

            # Move 2: (x-t, y-2t) -> Shift accumulator by 2 in y
            temp2 = L_prev1 | Acc2_prev
            Acc2_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            if max_size > 2: Acc2_curr[:, 2:] = temp2[:, :-2]
            W_curr |= Acc2_curr

            # Move 3: (x-2t, y-t) -> Shift accumulator by 1 in y, pulls from x-2
            temp3 = L_prev2 | Acc3_m2
            Acc3_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            if max_size > 1: Acc3_curr[:, 1:] = temp3[:, :-1]
            W_curr |= Acc3_curr

            # Move 4: (x-t, z-2t) -> Shift accumulator by 2 in z
            temp4 = L_prev1 | Acc4_prev
            Acc4_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            if max_size > 2: Acc4_curr[2:, :] = temp4[:-2, :]
            W_curr |= Acc4_curr

            # Move 5: (x-2t, z-t) -> Shift accumulator by 1 in z, pulls from x-2
            temp5 = L_prev2 | Acc5_m2
            Acc5_curr = np.zeros((max_size, max_size), dtype=np.bool_)
            if max_size > 1: Acc5_curr[1:, :] = temp5[:-1, :]
            W_curr |= Acc5_curr

        # Compute Losers for this level
        L_curr = supermex(W_curr, max_size)

        # Write to the 3D array for the user's slice output
        W_space[x] = W_curr
        L_space[x] = L_curr

        # -------------------------------------------------------------
        # Shift the Sliding Windows for the next level
        # -------------------------------------------------------------
        if x > 0:
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
    """Prompt for a variant sheet request, compute it, and display the result."""

    grid_size = int(input("Size of the grid you want to see (y and z axes):\n"))
    is_winner = input("Winner or loser? (W/L)\n").strip().upper() == 'W'
    desired_level = int(input("x-level?\n"))

    compute_size = max(grid_size, desired_level + 1)

    print(f"Computing 3D space up to size {compute_size} using 2D Rolling Accumulators...")
    W_space, L_space = compute_variant_space(compute_size)

    if is_winner:
        sheet = W_space[desired_level, :grid_size, :grid_size]
        output(sheet, True, desired_level)
    else:
        sheet = L_space[desired_level, :grid_size, :grid_size]
        output(sheet, False, desired_level)


if __name__ == "__main__":
    main()