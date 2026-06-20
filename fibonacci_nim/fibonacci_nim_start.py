"""Generate and display finite instant-winner and loser sheets for 2 Heap Fibonacci Nim.

This script computes two-dimensional slices of two-heap Fibonacci Nim using the
``supermex`` operator and the ``recursive`` operator. The x-coordinate is treated as the sheet level
while the rendered grid coordinates are y and z.
"""

import numpy as np
from numba import njit
import rectangle_display

@njit
def supermex(Wx, y_size, z_size):
    """Compute the loser sheet L_x from the instant-winner sheet W_x.
 
    A position (z, y) [z=last move, y=pile2 size, at the current x level]
    is a Loser (P-position) iff:
      1. It is NOT an instant winner (Wx[z,y] is False), AND
      2. Every legal intra-sheet move (x,y,z) -> (x,y-t,t), 1<=t<=min(y,2z),
         lands on a position that is itself NOT a Loser (i.e. there is no
         move to a P-position).
 
    Args:
        Wx: boolean [z_size, y_size] instant-winner grid for this x-level.
        y_size: number of y values represented (columns).
        z_size: number of z values represented (rows).
 
    Returns:
        boolean [z_size, y_size] loser grid for this x-level.
    """
    Lx = np.zeros((z_size, y_size), dtype=np.bool_)

    # y must be the outer loop: a move (x,y,z)->(x,y-t,t) always strictly
    # decreases y (since t>=1), so Lx[t, y-t] is already finalized by the
    # time we need to read it, for any y in the outer loop.
    for y in range(y_size):
        for z in range(1, z_size):
            if Wx[z, y]:
                # Already an instant winner via a lower x-level; can't be a loser.
                continue

            can_reach_loser = False
            max_t = min(y, 2 * z)
            for t in range(1, max_t + 1):
                new_y = y - t
                new_z = t
                if new_z >= z_size:
                    # Target z falls outside our representable range.
                    # We cannot determine its status; skip (see caveats below).
                    continue
                if Lx[new_z, new_y]:
                    can_reach_loser = True
                    break

            if not can_reach_loser:
                Lx[z, y] = True

    return Lx


@njit
def _compute_Wx_from_history(L_history, x_level, y_size, z_size):
    """Compute the W sheet at x_level from already-computed L sheets at all
    lower x levels (0..x_level-1), stored in L_history[x][z][y].
 
    Move used: (x,y,z) -> (x-t, y, t), for 1 <= t <= min(x_level, 2*z).
    (x,y,z) is an instant winner iff some such move lands on a Loser.
    """
    Wx = np.zeros((z_size, y_size), dtype=np.bool_)
    for y in range(y_size):
        for z in range(1, z_size):
            max_t = min(x_level, 2 * z)
            for t in range(1, max_t + 1):
                target_x = x_level - t
                target_z = t
                if target_z >= z_size:
                    continue
                if L_history[target_x, target_z, y]:
                    Wx[z, y] = True
                    break
    return Wx


def generate_all_sheets_up_to(desired_level, y_size, z_size):
    """Build L_history[0..desired_level] and W_history[0..desired_level].
 
    IMPORTANT: z_size must be strictly greater than max(desired_level, y_size)
    for results to be exact. This is because a move can set the new z equal
    to t, where t can be as large as the pile size being reduced (up to
    desired_level for the x-pile move, or up to y_size for the y-pile move).
    If z_size is too small, moves landing at z >= z_size are silently
    skipped, which can misclassify positions as Losers when a real winning
    move was simply out of view. (Verified empirically: this causes wrong
    answers when z_size <= max(x_size, y_size); safe once z_size comfortably
    exceeds both.)
 
    Returns:
        L_history: np.bool_ array [desired_level+1, z_size, y_size]
        W_history: np.bool_ array [desired_level+1, z_size, y_size]
    """
    assert z_size > desired_level and z_size > y_size, (
        "z_size must exceed both desired_level and y_size to avoid silent "
        "truncation errors -- see docstring."
    )
    L_history = np.zeros((desired_level + 1, z_size, y_size), dtype=np.bool_)
    W_history = np.zeros((desired_level + 1, z_size, y_size), dtype=np.bool_)

    # x = 0 base case: W_0 is all False (no lower sheet to jump to).
    W_history[0] = np.zeros((z_size, y_size), dtype=np.bool_)
    L_history[0] = supermex(W_history[0], y_size, z_size)

    for x in range(1, desired_level + 1):
        Wx = _compute_Wx_from_history(L_history, x, y_size, z_size)
        Lx = supermex(Wx, y_size, z_size)
        W_history[x] = Wx
        L_history[x] = Lx

    return L_history, W_history


def get_sheet(desired_level, is_winner, y_size, z_size):
    """Convenience wrapper: get a single W or L sheet at desired_level."""
    L_history, W_history = generate_all_sheets_up_to(desired_level, y_size, z_size)
    if is_winner:
        return W_history[desired_level]
    else:
        return L_history[desired_level]


def main():
    """Prompt for a winner or loser sheet request, compute it, and display the result."""

    y_size = int(input("Size of the y-grid (pile 2 size) you want to see:\n"))
    z_size = int(input("Size of the z-grid (last-move size) you want to see:\n"))
    is_winner = input("Winner or loser? (W/L)\n").strip().upper() == 'W'
    desired_level = int(input("x-level?\n"))

    sheet = get_sheet(desired_level, is_winner, y_size, z_size)

    if is_winner:
        rectangle_display.output(sheet, True, desired_level)
    else:
        rectangle_display.output(sheet, False, desired_level)


if __name__ == "__main__":
    main()
