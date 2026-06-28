"""
Generates and displays Instant-Winner and Loser sheets for the full 3-heap Wythoff game: Normal
3-heap Nim, plus the moves to take away the same number of chips from any two piles or from all
three piles at once.
"""

import numpy as np
from numba import njit
from utils.display import output

def main():
    """Prompt for a Wythoff sheet request, compute it, and display the result."""

    grid_size = int(input("Size of the grid you want to see:\n"))
    is_winner = input("Winner or loser? (W/L)\n") == 'W'
    desired_level = int(input("x-level?\n"))

    # Initialize Ax, Bx, Cx, and Dx as all 0s.
    # Ax = x reduction, Bx = x,y reduction, Cx = x,z reduction, Dx = x,y,z reduction
    Ax = np.zeros((grid_size, grid_size), dtype=np.bool_)
    Bx = np.zeros((grid_size, grid_size), dtype=np.bool_)
    Cx = np.zeros((grid_size, grid_size), dtype=np.bool_)
    Dx = np.zeros((grid_size, grid_size), dtype=np.bool_)

    Wx = generate_Wx(Ax, Bx, Cx, Dx, desired_level)

    if is_winner:
        final_Wx = Wx[:grid_size, :grid_size]
        output(final_Wx, True, desired_level)
    else:
        Lx = supermex(Wx)
        final_Lx = Lx[:grid_size, :grid_size]
        output(final_Lx, False, desired_level)


@njit
def generate_Wx(Ax, Bx, Cx, Dx, desired_level):
    """Iteratively build the instant-winner sheet W_x up to ``desired_level``.

    Args:
        Ax: Auxiliary sheet for (x-k, y, z) moves.
        Bx: Auxiliary sheet for (x-k, y-k, z) moves.
        Cx: Auxiliary sheet for (x-k, y, z-k) moves.
        Dx: Auxiliary sheet for (x-k, y-k, z-k) moves.
        desired_level: Target x-level to compute.

    Returns:
        The updated boolean grid for W_desired_level.
    """

    if desired_level == 0:
        return Ax | Bx | Cx | Dx

    for _ in range(1, desired_level + 1):
        # Current instant winners pointing to a lower x-level
        current_sheet = Ax | Bx | Cx | Dx

        # Calculate the actual Loser sheet for the current level
        MWx = supermex(current_sheet)

        # Accumulate and shift for the next level
        Ax |= MWx
        Bx = shift_y(Bx | MWx)
        Cx = shift_z(Cx | MWx)
        Dx = shift_yz(Dx | MWx)

    return Ax | Bx | Cx | Dx


@njit
def supermex(Wx):
    """Compute the supermex sheet M(Wx) for the current x-level.

    For a fixed x, this resolves every move that keeps x constant: reducing z alone
    (column mex), reducing y alone (blocked rows), and reducing y and z by the same
    amount (blocked diagonals).

    Args:
        Wx: Boolean instant-winner sheet from lower x-levels.

    Returns:
        A boolean sheet containing the newly selected loser positions (Lx).
    """

    grid_size = Wx.shape[0]
    MWx = np.zeros((grid_size, grid_size), dtype=np.bool_)

    blocked_rows = np.zeros(grid_size, dtype=np.bool_)
    # We use 2*grid_size to safely store negative (z - y) diagonal indices.
    blocked_diags = np.zeros(grid_size * 2, dtype=np.bool_)

    for y in range(grid_size):  # Loop through each column (implicitly handles y-reduction)
        next_available_z = -1

        for z in range(grid_size):
            # Calculate the diagonal identifier. Adding grid_size prevents negative indexing.
            diag_index = (z - y) + grid_size

            # If cell is not an Instant Winner, row is not blocked, and diagonal is not blocked
            if not Wx[z, y] and not blocked_rows[z] and not blocked_diags[diag_index]:
                next_available_z = z
                break

        if next_available_z == -1:  # No z found means we go to next y column
            continue

        # Mark the Loser and cast out the "Implied Winners"
        MWx[next_available_z, y] = True
        blocked_rows[next_available_z] = True
        blocked_diags[(next_available_z - y) + grid_size] = True

    return MWx


@njit
def shift_y(input_sheet):
    """Shifts the sheet right (along the y-axis). Translates A(z, y) to A(z, y+1)."""
    grid_size = input_sheet.shape[0]
    Tx = np.zeros((grid_size, grid_size), dtype=np.bool_)
    # Drops the last column and pastes starting at column 1
    Tx[:, 1:] = input_sheet[:, :-1]
    return Tx


@njit
def shift_z(input_sheet):
    """Shifts the sheet down (along the z-axis). Translates A(z, y) to A(z+1, y)."""
    grid_size = input_sheet.shape[0]
    Tx = np.zeros((grid_size, grid_size), dtype=np.bool_)
    # Drops the last row and pastes starting at row 1
    Tx[1:, :] = input_sheet[:-1, :]
    return Tx


@njit
def shift_yz(input_sheet):
    """Shifts the sheet diagonally down-right. Translates A(z, y) to A(z+1, y+1)."""
    grid_size = input_sheet.shape[0]
    Tx = np.zeros((grid_size, grid_size), dtype=np.bool_)
    # Drops the last row and column, pastes starting at row 1, col 1
    Tx[1:, 1:] = input_sheet[:-1, :-1]
    return Tx

#---------------------------- Running Main Function ----------------------------
if __name__ == "__main__":
    main()