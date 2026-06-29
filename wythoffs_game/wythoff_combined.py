"""
Generates and displays Instant-Winner and Loser sheets for the full 3-heap Wythoff game: Normal
3-heap Nim, plus the moves to take away the same number of chips from any two piles or from all
three piles at once.
"""

import numpy as np
from numba import njit
from utils.display import run_sheet_session


@njit
def compute_sheets(depth, size):
    """Build the W and L sheets for x-levels ``0..depth-1`` on a ``size x size`` (z, y) grid.

    Sheets are indexed ``[x, z, y]`` (z is the row, y is the column). The instant-winner
    sheet W_x is the union of four accumulators that fold in every lower loser sheet:
        Ax (x-k, y, z), Bx (x-k, y-k, z), Cx (x-k, y, z-k), Dx (x-k, y-k, z-k),
    shifted along y, z, and the y=z diagonal respectively. L_x = supermex(W_x).

    Depth (x-levels) and grid size are decoupled, so a low-level request on a big grid only allocates
    the levels it needs. Returns just ``(W_space, L_space)`` -- two ``(depth, size, size)`` cubes; the
    cumulative-loser (C) sheets are derived from L on demand by the display layer, so no third cube is
    materialized.

    Returns:
        W_space, L_space.
    """

    W_space = np.zeros((depth, size, size), dtype=np.bool_)
    L_space = np.zeros((depth, size, size), dtype=np.bool_)

    # Ax = x reduction, Bx = x,y reduction, Cx = x,z reduction, Dx = x,y,z reduction.
    Ax = np.zeros((size, size), dtype=np.bool_)
    Bx = np.zeros((size, size), dtype=np.bool_)
    Cx = np.zeros((size, size), dtype=np.bool_)
    Dx = np.zeros((size, size), dtype=np.bool_)

    for x in range(depth):
        # Instant winners pointing to a lower x-level (W_0 is blank).
        Wx = Ax | Bx | Cx | Dx
        Lx = supermex(Wx)

        W_space[x, :, :] = Wx
        L_space[x, :, :] = Lx

        # Accumulate and shift for the next level.
        Ax = Ax | Lx
        Bx = shift_y(Bx | Lx)
        Cx = shift_z(Cx | Lx)
        Dx = shift_yz(Dx | Lx)

    return W_space, L_space


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


def main():
    """Prompt for one or more Wythoff Combined sheets and display them together."""
    # Sheets are indexed [x, z, y], so the (row, col) axes are (z, y): row_is_z=True.
    run_sheet_session(compute_sheets, row_is_z=True)


#---------------------------- Running Main Function ----------------------------
if __name__ == "__main__":
    main()