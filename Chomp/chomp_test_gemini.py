import numpy as np
from utils.display import output # Uncomment if using your local display util

def generate_sheets(target_x, dim_y=15, dim_z=15):
    """
    Generates the P-sheets (Winning) and W-sheets (Instant-N / Losing) 
    using the exact renormalization operators (L, D, M).
    
    Coordinates: array[z, y]
    z: number of columns of height 1 (row index / y-axis visually)
    y: number of columns of height 2 (col index / x-axis visually)
    x: number of columns of height 3 (sheet index)
    """
    P_sheets = []
    W_sheets = []
    
    for x in range(target_x + 1):
        if x == 0:
            # Base case W_0: All zeros except [0, 0] = 1
            W_x = np.zeros((dim_z, dim_y), dtype=int)
            W_x[0, 0] = 1
        else:
            P_prev = P_sheets[x - 1]
            W_prev = W_sheets[x - 1]
            
            # --- 1. Diagonal Operator (D) ---
            D_P = np.copy(P_prev)
            
            z_star_indices = np.where(P_prev[:, 0] == 1)[0]
            if len(z_star_indices) > 0:
                z_star = z_star_indices[0]
                for t in range(z_star + 1):
                    y_idx = z_star - t
                    z_idx = t
                    if z_idx < dim_z and y_idx < dim_y:
                        D_P[z_idx, y_idx] = 1
                        
            # Combine W_prev with D_P (Logical OR)
            Combined = np.logical_or(W_prev, D_P).astype(int)
            
            # --- 2. Left Shift Operator (L) ---
            W_x = np.zeros((dim_z, dim_y), dtype=int)
            W_x[:, :-1] = Combined[:, 1:]
            
            # FIX: Maintain the boundary condition for lines extending to infinity.
            # Without this, numpy pads with 0s, which corrupts the flat lines from right to left.
            W_x[:, -1] = Combined[:, -1]
            
        # --- 3. Supermex Operator (M) ---
        P_x = np.zeros((dim_z, dim_y), dtype=int)
        T_x = np.copy(W_x)
        
        for y in range(dim_y):
            zero_indices = np.where(T_x[:, y] == 0)[0]
            
            if len(zero_indices) == 0:
                continue  # Reached array boundary
                
            z_s = zero_indices[0]
            P_x[z_s, y] = 1  
            
            for t in range(z_s + 1):
                y_idx = y + t
                z_idx = z_s - t
                if z_idx < dim_z and y_idx < dim_y:
                    T_x[z_idx, y_idx] = 1
                    
            if z_s == 0:
                break
                
        P_sheets.append(P_x)
        W_sheets.append(W_x)
        
    return P_sheets, W_sheets

if __name__ == "__main__":
    X_LEVEL = 20
    DIM_Y = 40
    DIM_Z = 40
    
    P, W = generate_sheets(X_LEVEL, dim_y=DIM_Y, dim_z=DIM_Z)
    
    print(f"--- W-Sheet (Losing IN-positions) for x={X_LEVEL} ---")
    print(W[X_LEVEL])
    output(W[X_LEVEL], True, X_LEVEL, 100)

    print(f"\n--- P-Sheet (Winning positions) for x={X_LEVEL} ---")
    print(P[X_LEVEL])
    output(P[X_LEVEL], True, X_LEVEL, 100)