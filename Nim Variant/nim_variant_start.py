"""Generates and displays Instant-Winner and Loser sheets for a Nim Variant where an additional
move  is introduced: to take away the same number of chips from all piles."""

import numpy as np
import display
from numba import njit

def main():
    """Prompt for a Nim sheet request, compute it, and display the result."""

    grid_size = int(input("Size of the grid you want to see:\n"))
    is_winner = input("Winner or loser? (W/L)\n") == 'W'
    desired_level = int(input("x-level?\n"))

    # Initialize Ax and Bx as all 0s. Wx = Ax + Bx
    # Lx will be generated using supermex(Wx)
    Ax = np.zeros((grid_size,grid_size),dtype=np.bool_)
    Bx = np.zeros((grid_size,grid_size),dtype=np.bool_)

    Wx = generate_Wx(Ax, Bx, desired_level)

    if is_winner:
        final_Wx = Wx[:grid_size, :grid_size]
        display.output(final_Wx, True, desired_level)
    else:
        Lx = supermex(Wx)
        final_Lx = Lx[:grid_size, :grid_size]
        display.output(final_Lx, False, desired_level)

@njit
def generate_Wx(Ax, Bx, desired_level):
    """Iteratively build the instant-winner sheet W_x up to ``desired_level``.
    Args:
        Ax: Boolean grid representing the first term of Wx, the loser positions' parents from a 
        move (x,y,z) -> (x-t,y,z).
        Bx: Boolean grid representing the second term of Wx, the loser positions' parents from a 
        move (x,y,z) -> (x-t,y-t,z-t).
        desired_level: Target x-level to compute.

    Returns:
        The updated boolean grid for W_desired_level.
    """

    if desired_level == 0:
        return Ax|Bx

    for _ in range(1, desired_level+1):
        # W_x+1 = Ax + Lx + S(Bx + Lx) and Lx = MWx
        current_sheet = Ax | Bx
        MWx = supermex(current_sheet)

        Ax |= MWx
        shift_target = Bx|MWx
        Bx = shift(shift_target)

    return Ax|Bx

@njit
def supermex(Wx):
    """Compute the supermex sheet M(Wx).

    For each y-column, this scans upward in z and selects the first cell that is
    not already an instant winner and whose row has not been blocked by an
    earlier selection.

    Args:
        Wx: Boolean instant-winner sheet.

    Returns:
        A boolean sheet containing the newly selected loser positions.
    """

    grid_size = Wx.shape[0]
    MWx = np.zeros((grid_size,grid_size), dtype=np.bool_)     # Our MWx is empty
    blocked_rows = np.zeros(grid_size, dtype=np.bool_)

    for y in range(grid_size):  # Loop through each column
        next_available_z = -1
        for z in range(grid_size):
            if not Wx[z, y] and not blocked_rows[z]:    # If the position is 0 (loser)
                                                        # and not in a row marked as N,
                                                        # then mark that z
                next_available_z = z
                break

        if next_available_z == -1:  # No z found means we go to next y column
            continue

        MWx[next_available_z,y] = True
        blocked_rows[next_available_z] = True

    return MWx

@njit
def shift(input_sheet):
    """
    Shifts sheet diagonally such that SA(z,y) = A(z-1,y-1). 
    Every entry in input it shifted up/right by 1 spot.

    Parameters:
    input_sheet : np.ndarray (current Bx|MWx array)

    Returns:
    Tx : np.ndarray
        The spatially translated grid sheet.
    """

    grid_size = input_sheet.shape[0]
    Tx = np.zeros((grid_size, grid_size), dtype=np.bool_)
    # [:-1, :-1] drops the last row and column from the input.
    # [1:, 1:] pastes the remaining input data starting at row 1, col 1.
    Tx[1:, 1:] = input_sheet[:-1, :-1]
    return Tx

#---------------------------- Running Main Function ----------------------------
if __name__ == "__main__":
    main()
