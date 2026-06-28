"""Generates and displays Instant-Winner and Loser sheets for a Nim Variant where an additional
move  is introduced: to take away the same number of chips from all piles."""

import numpy as np
from numba import njit
from utils.display import output

def main():
    """Prompt for a Nim sheet request, compute it, and display the result."""

    grid_size = int(input("Size of the grid you want to see:\n"))
    sheet_type = input(
        "Winner, loser, cumulative losers, or sponge? (W/L/C/S)\n").strip().upper()

    if sheet_type == 'S':
        # 3D scatter of every loser triplet (x, y, z) -- the loser set of this game
        # is the 3-pile Nim P-set {x^y^z == 0}, i.e. a Sierpinski tetrahedron. Use a
        # power-of-two grid (and span the whole cube) to see the fractal cleanly.
        max_level = int(input("highest x-level (blank = grid_size - 1)?\n") or grid_size - 1)
        plot_losers_3d(grid_size, max_level)
        return

    desired_level = int(input("x-level?\n"))

    # Initialize Ax and Bx as all 0s. Wx = Ax + Bx
    # Lx will be generated using supermex(Wx)
    Ax = np.zeros((grid_size,grid_size),dtype=np.bool_)
    Bx = np.zeros((grid_size,grid_size),dtype=np.bool_)

    if sheet_type == 'C':
        # Union of every loser sheet L_0..L_desired_level, so the P-positions
        # accumulate into their lines instead of showing a single sheet's losers.
        Lcum = generate_cumulative_Lx(Ax, Bx, desired_level)
        output(Lcum[:grid_size, :grid_size], False, desired_level)
        return

    Wx = generate_Wx(Ax, Bx, desired_level)

    if sheet_type == 'W':
        final_Wx = Wx[:grid_size, :grid_size]
        output(final_Wx, True, desired_level)
    else:
        Lx = supermex(Wx)
        final_Lx = Lx[:grid_size, :grid_size]
        output(final_Lx, False, desired_level)

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

def plot_losers_3d(grid_size, max_level):
    """3D scatter of every loser position (x, y, z) for x-levels 0..max_level.

    Stacks the per-sheet loser sets recovered along the recurrence and scatters
    them in (x, y, z) space. For this game the losers are exactly the 3-pile Nim
    P-positions {x ^ y ^ z == 0}, whose 3D structure is a Sierpinski tetrahedron,
    so a power-of-two ``grid_size`` spanning the whole cube shows it most cleanly.
    """
    import matplotlib.pyplot as plt  # local import; registers the 3D projection

    xs, ys, zs = [], [], []
    Ax = np.zeros((grid_size, grid_size), dtype=np.bool_)
    Bx = np.zeros((grid_size, grid_size), dtype=np.bool_)
    for x in range(max_level + 1):
        Lx = supermex(Ax | Bx)          # L_x, indexed [z, y]
        z_idx, y_idx = np.where(Lx)
        xs.extend([x] * len(y_idx))
        ys.extend(y_idx.tolist())
        zs.extend(z_idx.tolist())
        Ax |= Lx
        Bx = shift(Bx | Lx)

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(projection="3d")
    ax.scatter(xs, ys, zs, s=3, c="black", depthshade=False)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title(f"Loser positions (x^y^z=0) for x=0..{max_level}")
    plt.show()


@njit
def generate_cumulative_Lx(Ax, Bx, desired_level):
    """Build the union (logical OR) of every loser sheet L_0..L_desired_level.

    Runs the same recurrence as ``generate_Wx``, but instead of returning only the
    final instant-winner sheet it ORs together the loser sheet recovered at each
    x-level along the way (L_k = supermex(W_k)). Showing all P-positions up through
    a level reveals their lines rather than a single sheet's losers.

    Args:
        Ax: Boolean grid, first term of Wx (zeros on entry); mutated in place.
        Bx: Boolean grid, second term of Wx (zeros on entry); mutated in place.
        desired_level: Highest x-level to include.

    Returns:
        A boolean grid marking every loser position for x = 0..desired_level.
    """

    grid_size = Ax.shape[0]
    Lcum = np.zeros((grid_size, grid_size), dtype=np.bool_)

    # W_x+1 = Ax + Lx + S(Bx + Lx) and Lx = MWx, exactly as in generate_Wx, but we
    # need desired_level+1 iterations so L_desired_level itself is folded in.
    for _ in range(desired_level + 1):
        current_sheet = Ax | Bx
        MWx = supermex(current_sheet)

        Lcum |= MWx
        Ax |= MWx
        Bx = shift(Bx | MWx)

    return Lcum

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
