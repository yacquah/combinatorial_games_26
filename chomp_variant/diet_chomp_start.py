import numpy as np
from numba import njit
from utils.display import output

def main():
    grid_size = int(input("Size of the grid you want to see:\n"))
    is_winner = input("Winner or loser? (W/L)\n") == 'W'
    desired_level = int(input("x-level?\n"))
    
    # DYNAMIC PADDING: Diet Chomp back-projects up to 4 spaces per x-level (via M4/M5/M6).
    # We must pad the grid by 4 * desired_level to prevent boundary truncation.
    compute_size = grid_size + (desired_level * 4)

    if desired_level == 0:
        if not is_winner:
            L0 = generate_L0(compute_size)
            output(L0[:grid_size, :grid_size], False, 0)
        else:
            W0 = np.zeros((grid_size, grid_size), dtype=np.bool_)
            output(W0, True, 0)
        return

    # Initialize sliding history buffer
    L_history = np.zeros((4, compute_size, compute_size), dtype=np.bool_)
    L_history[0] = generate_L0(compute_size)
    
    Wx = np.zeros((compute_size, compute_size), dtype=np.bool_)
    Lx = np.zeros((compute_size, compute_size), dtype=np.bool_)

    for current_x in range(1, desired_level + 1):
        Wx = generate_Wx_diet(L_history)
        Lx = supermex_diet(Wx)
        
        # Slide history window forward
        L_history[3] = L_history[2]
        L_history[2] = L_history[1]
        L_history[1] = L_history[0]
        L_history[0] = Lx
    
    # Slice the padded matrix down to the requested size
    if is_winner:
        final_Wx = Wx[:grid_size, :grid_size]
        output(final_Wx, True, desired_level)
    else:
        final_Lx = Lx[:grid_size, :grid_size]
        output(final_Lx, False, desired_level)
    
@njit
def generate_Wx_diet(L_history):
    compute_size = L_history.shape[1]
    Wx = np.zeros((compute_size, compute_size), dtype=np.bool_)
    
    for t_idx in range(4):
        t = t_idx + 1
        Lx_prev = L_history[t_idx]
        
        for y in range(compute_size):
            for z in range(compute_size):
                if not Lx_prev[z, y]:
                    continue  
                    
                y_win_m4 = y - t
                if y_win_m4 >= 0:
                    Wx[z, y_win_m4] = True
                    
                if y == 0:
                    max_y_win = 4 - 2 * t
                    for y_win in range(max_y_win + 1):
                        z_win = z - y_win - t
                        if 0 <= z_win < compute_size:
                            Wx[z_win, y_win] = True
                            
                if y == 0 and z == 0:
                    for y_win in range(compute_size):
                        if 3 * t + 2 * y_win > 4:
                            break  
                        for z_win in range(compute_size):
                            if 3 * t + 2 * y_win + z_win <= 4:
                                Wx[z_win, y_win] = True
                                
    return Wx

@njit
def supermex_diet(Wx):
    compute_size = Wx.shape[0]
    Lx = np.zeros((compute_size, compute_size), dtype=np.bool_)
    blocked = np.zeros((compute_size, compute_size), dtype=np.bool_)
    
    for y in range(compute_size):
        for z in range(compute_size):
            if Wx[z, y] or blocked[z, y]:
                continue
                
            Lx[z, y] = True
            
            for t in range(1, 5):
                y_win = y + t
                z_win = z - t
                if y_win < compute_size and z_win >= 0:
                    blocked[z_win, y_win] = True
                    
            if z == 0:
                for t in range(1, 5):
                    y_win = y + t
                    if y_win < compute_size:
                        max_z_win = 4 - 2 * t
                        for z_win in range(max_z_win + 1):
                            if z_win < compute_size:
                                blocked[z_win, y_win] = True
                                
            for t in range(1, 5):
                z_win = z + t
                if z_win < compute_size:
                    blocked[z_win, y] = True
                    
    return Lx    

@njit
def generate_L0(compute_size):
    L0 = np.zeros((compute_size, compute_size), dtype=np.bool_)
    
    # Restored to original logic: [0,0,0] is an illegal destination. 
    # The loop evaluates [0,0,1] first, which correctly becomes the true terminal P-position.

    max_pieces = 2 * compute_size + compute_size
    for pieces in range(1, max_pieces): 
        for y in range(compute_size):
            z = pieces - 2 * y
            if z < 0 or z >= compute_size:
                continue
                
            can_reach_loser = False
            
            # M1: Bite row 2. (y-t, z+t)
            for t in range(1, 5):
                if t <= y and (z + t) < compute_size:
                    # RESTORED GUARD: Prevents transitioning to the empty board
                    if (y - t) == 0 and (z + t) == 0:
                        continue
                    if L0[z + t, y - t]:
                        can_reach_loser = True
                        break
                        
            # M2: Bite row 1 under a height-2 column. (y-t, 0)
            if not can_reach_loser:
                for t in range(1, y + 1):
                    if (2 * t + z) <= 4:
                        # RESTORED GUARD: Prevents transitioning to the empty board
                        if (y - t) == 0:
                            continue
                        if L0[0, y - t]:
                            can_reach_loser = True
                            break
                            
            # M3: Bite row 1. (y, z-t)
            if not can_reach_loser:
                for t in range(1, 5):
                    if t <= z:
                        # RESTORED GUARD: Prevents transitioning to the empty board
                        if y == 0 and (z - t) == 0: 
                            continue
                        if L0[z - t, y]:
                            can_reach_loser = True
                            break
                            
            if not can_reach_loser:
                L0[z, y] = True
                
    return L0

if __name__ == "__main__":
    main()