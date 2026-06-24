import numpy as np
from utils.display import output

def calculate_bus_game_sheets(level_x, dim_y=100, dim_z=100):
    """
    Calculates the Winning sheet (P-sheet) and Losing sheet (IN-sheet)
    for a given passenger count in Bus 1 (level_x).
    Bus 2 (dim_y) and Bus 3 (dim_z) are set to 100x100 dimensions.
    """
    # Initialize the matrices for all levels up to level_x
    W = np.zeros((level_x + 1, dim_y, dim_z), dtype=int)
    P = np.zeros((level_x + 1, dim_y, dim_z), dtype=int)
    
    for x in range(level_x + 1):
        if x > 0:
            # The IN-sheet is the logical OR of the previous IN-sheet and P-sheet
            W[x] = np.logical_or(W[x-1], P[x-1]).astype(int)
            
        # Supermex Operator to find the P-sheet for level x
        T_x = np.copy(W[x])
        M_W = np.zeros((dim_y, dim_z), dtype=int)
        
        for y in range(dim_y):
            # Find the smallest z (Bus 3 passengers) where T_x is 0
            zero_indices = np.where(T_x[y, :] == 0)[0]
            
            if len(zero_indices) > 0:
                z_s = zero_indices[0]
                # Step 3: Declare this a winning position
                M_W[y, z_s] = 1
                
                # Step 4: Forbid all future y values for this z_s
                # (since a player could just unload Bus 2 to get here)
                T_x[y:, z_s] = 1
                
        P[x] = M_W
        
    return P[level_x], W[level_x]

if __name__ == "__main__":
    try:
        user_level = int(input("Enter the target level (Bus 1 passenger count): "))
        
        # Outputting 100 by 100 sheets as requested
        p_sheet, in_sheet = calculate_bus_game_sheets(user_level, dim_y=100, dim_z=100)
        
        print(f"\n--- Winning Sheet (P-sheet) for level {user_level} (100x100) ---")
        print(p_sheet)
        output(p_sheet, False, user_level, 100)
        
        print(f"\n--- Losing/IN Sheet (W-sheet) for level {user_level} (100x100) ---")
        print(in_sheet)
        output(in_sheet, True, user_level, 100)

        
    except ValueError:
        print("Invalid input. Please enter a whole number.")