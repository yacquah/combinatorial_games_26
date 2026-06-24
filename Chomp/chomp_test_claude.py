"""Three-row Chomp, via the instant-winner / supermex sheet framework.

Rewritten after the first attempt (using the paper's compact operator
formula W_x = sum L^t D L_{x-t}) produced a verified bug: it dropped
contributions where the shift made the column index negative, when in
fact those very cases (a Loser at y=0) are exactly what M6 needs to
handle. Implementing the M4/M5/M6 moves directly, cell by cell, avoids
re-deriving the compact operator algebra and is much easier to verify.

Position [x,y,z] = number of columns of height 3, 2, 1 respectively.
Move rules (all moves are "chomp a token, remove it and everything
north/east"):
  M1: [x, y-t, z+t]      0 < t <= y      (intra-sheet)
  M2: [x, y-t, 0]        0 < t <= y      (intra-sheet)
  M3: [x, y, z-t]        0 < t <= z      (intra-sheet)
  M4: [x-t, y+t, z]      0 < t <= x      (inter-sheet)
  M5: [x-t, 0, z+y+t]    0 < t <= x      (inter-sheet)
  M6: [x-t, 0, 0]        0 < t <= x      (inter-sheet)

W_x(y,z) = 1 iff [x,y,z] can reach a P-position at a strictly lower
x-level via M4, M5, or M6.
L_x = supermex(W_x), accounting for the intra-sheet moves M1-M3.
"""

import numpy as np
from numba import njit


@njit
def supermex(Wx, grid_size):
    """Compute L_x from W_x using the intra-sheet moves M1-M3.

    CRITICAL FIX (found by cross-checking against Zeilberger's published
    P-positions and the standard 2-row Chomp formula): the original
    version of this function (and compute_chomp_space below) implicitly
    treated [0,0,0] -- the fully empty board -- as a valid P-position
    that any position could trivially reach via move M6 with t=x. This
    made nearly every position a trivial "instant winner," producing
    sheets that were almost entirely True. The actual terminal losing
    position in Chomp is "only the poison square remains" (Zeilberger
    coordinates [0,0,1], not [0,0,0]); the fully empty board [0,0,0] is
    not a real, reachable game position and must never be treated as a
    P-position by the M4/M5/M6 lookups. This function itself is
    unaffected (it only handles intra-sheet moves M1-M3, which never
    involve x=0 specifically), but compute_chomp_space below required a
    fix to special-case the [0,0,0] target.
    """
    Lx = np.zeros((grid_size, grid_size), dtype=np.bool_)
    blocked = np.copy(Wx)

    for y in range(grid_size):
        zsmall = -1
        for z in range(grid_size):
            if not blocked[z, y]:
                zsmall = z
                break
        if zsmall == -1:
            continue

        Lx[zsmall, y] = True

        # M3 parents: (y, z') for all z' > zsmall
        for zp in range(zsmall + 1, grid_size):
            blocked[zp, y] = True

        # M1/M2 parents: (y+k, zsmall-k) for k=1..zsmall
        k = 1
        while zsmall - k >= 0 and y + k < grid_size:
            blocked[zsmall - k, y + k] = True
            k += 1

        if zsmall == 0:
            break

    return Lx


@njit
def compute_chomp_space(max_size):
    """Compute W_history and L_history for x = 0..max_size-1.

    FIX: [0,0,0] is the fully empty board and is NOT a valid P-position
    target -- the true terminal P-position is [0,0,1] (only the poison
    square remains). We must explicitly skip [0,0,0] as a target for
    the M4/M5/M6 inter-sheet move checks, even though the move formulas
    can syntactically point there (e.g. M6 with t=x always gives target
    x'=0,y'=0,z'=0). Without this fix, every position trivially becomes
    an instant winner via M6, producing degenerate all-True sheets --
    confirmed by comparing against a known-correct reference image of
    W5 and against Zeilberger's published P-positions.
    """
    L_history = np.zeros((max_size, max_size, max_size), dtype=np.bool_)
    W_history = np.zeros((max_size, max_size, max_size), dtype=np.bool_)

    for x in range(max_size):
        Wx = np.zeros((max_size, max_size), dtype=np.bool_)

        if x == 0:
            # [0,0,0] (the fully empty board) is not a real game
            # position and must never be selectable as a Loser by the
            # supermex search. We pass a SEPARATE internal sheet with
            # [0,0,0] pre-blocked into supermex (so the search correctly
            # finds [0,0,1] -- board: only the poison square remains --
            # as the true terminal P-position), but keep Wx itself (the
            # one we store in W_history and return to the user) free of
            # this artifact, since [0,0,0] is not a real instant-winner
            # position and should read as False, not True. (An earlier
            # version of this fix incorrectly let the seeding value leak
            # into W_history itself, which was caught by comparing W0
            # against an independent brute-force board simulation.)
            Wx_for_supermex = np.zeros((max_size, max_size), dtype=np.bool_)
            Wx_for_supermex[0, 0] = True
        else:
            Wx_for_supermex = Wx
            for y in range(max_size):
                for z in range(max_size):
                    found = False

                    # M4: [x-t, y+t, z]
                    for t in range(1, x + 1):
                        ny = y + t
                        if ny >= max_size:
                            break
                        nx = x - t
                        if nx == 0 and ny == 0 and z == 0:
                            continue  # [0,0,0] is not a real P-position
                        if L_history[nx, z, ny]:
                            found = True
                            break

                    # M5: [x-t, 0, z+y+t]
                    if not found:
                        for t in range(1, x + 1):
                            nz = z + y + t
                            if nz >= max_size:
                                break
                            nx = x - t
                            if nx == 0 and nz == 0:
                                continue  # [0,0,0] is not a real P-position
                            if L_history[nx, nz, 0]:
                                found = True
                                break

                    # M6: [x-t, 0, 0]
                    if not found:
                        for t in range(1, x + 1):
                            nx = x - t
                            if nx == 0:
                                continue  # [0,0,0] is not a real P-position
                            if L_history[nx, 0, 0]:
                                found = True
                                break

                    Wx[z, y] = found
                    Wx_for_supermex[z, y] = found

        W_history[x] = Wx
        L_history[x] = supermex(Wx_for_supermex, max_size)

    return W_history, L_history


def main():
    """Prompt for a Chomp sheet request, compute it, and display the result."""
    from utils.display import output

    grid_size = int(input("Size of the grid you want to see (y and z axes):\n"))
    is_winner = input("Winner or loser? (W/L)\n").strip().upper() == 'W'
    desired_level = int(input("x-level?\n"))

    # IMPORTANT FIX: the M4 move targets y'=y+t (t up to x), and M5
    # targets z'=z+y+t (t up to x). This means correctly computing
    # cells near the edge of the requested display grid requires
    # looking at cells WELL OUTSIDE that grid -- specifically, up to
    # roughly (grid_size + desired_level) for y, and up to roughly
    # (2*grid_size + desired_level) for z. Using too small an internal
    # computation grid silently drops valid winning moves that point
    # outside the window, corrupting the result (confirmed by comparing
    # against a known-correct reference image: a grid_size=10 sheet
    # computed with NO safety margin showed clearly wrong results that
    # only matched after computing with a much larger internal grid and
    # slicing down). We use a generous margin here; if you still see
    # discrepancies at very large grid_size or desired_level, increase
    # the multiplier further.
    compute_size = max(grid_size, desired_level + 1) + 2 * grid_size + desired_level + 10

    print(f"Computing 3D space up to internal size {compute_size} "
          f"(requested display grid: {grid_size}, x-level: {desired_level})...")
    W_space, L_space = compute_chomp_space(compute_size)

    if is_winner:
        sheet = W_space[desired_level, :grid_size, :grid_size]
        output(sheet, True, desired_level)
    else:
        sheet = L_space[desired_level, :grid_size, :grid_size]
        output(sheet, False, desired_level)


if __name__ == "__main__":
    main()