"""Bitboard bounded-Wythoff: the same recurrence as ``wythoffs_game/bounded_wythoff.py``,
but each grid row is packed into ``uint64`` words so 64 cells are decided per instruction.

Two facts make this work:

* Every operation in the recurrence -- the three Hilbert-basis steps of the bounded-ratio
  wedge, the cumulative-loser sheet, the single-pile blocks -- is a shift of a whole row by
  1 or 2 cells followed by an OR. Nothing looks at a cell in isolation.
* Each row holds at most one loser. Walking a row, the first cell that no move reaches is
  the loser, and ``loser_in_row`` makes every later cell in that row a winner. So the
  per-row work is "OR the blocking sheets together, then find the first zero bit".

Rows are indexed ``[z]`` and bits within a row are ``y`` (bit ``y & 63`` of word ``y >> 6``),
matching the ``[z, y]`` convention of the rest of the codebase.

Output is sparse: ``loser_y[x, z]`` is the column of row ``z``'s loser on sheet ``x``, or -1
if that row has no loser inside the grid. That is the whole loser set (one per row, one per
column), which is all the plotting and analysis need -- ``depth * size`` ints instead of
``depth * size**2`` bytes.

Losers do not depend on the grid size: every move decreases a coordinate, so a cell's status
is fixed by cells below and left of it. A run at size S therefore contains the answer for
every size <= S, which is what makes the cache in ``store.py`` reusable.
"""

import numpy as np
from numba import njit

ONE = np.uint64(1)
ZERO = np.uint64(0)
FULL = np.uint64(0xFFFFFFFFFFFFFFFF)
S1 = np.uint64(1)
S2 = np.uint64(2)
S63 = np.uint64(63)
S62 = np.uint64(62)


@njit(cache=True, nogil=True)
def _first_zero(row, nwords, tail_mask, size):
    """Index of the lowest clear bit in a packed row, or -1 if the row is full."""
    for i in range(nwords):
        w = row[i]
        if i == nwords - 1:
            w |= ~tail_mask  # bits past the grid edge never count as free
        if w != FULL:
            for b in range(64):
                if (w >> np.uint64(b)) & ONE == ZERO:
                    y = i * 64 + b
                    if y < size:
                        return y
                    return -1
    return -1


@njit(cache=True, nogil=True)
def compute_loser_y(depth, size):
    """Losers of bounded Wythoff on x-levels ``0..depth-1`` over a ``size x size`` grid.

    Returns ``loser_y`` of shape ``(depth, size)``: ``loser_y[x, z]`` is the y of the loser in
    row z of sheet x, or -1 if the row has none inside the grid.
    """
    nwords = (size + 63) // 64
    rem = size & 63
    tail_mask = FULL if rem == 0 else (ONE << np.uint64(rem)) - ONE

    loser_y = -np.ones((depth, size), dtype=np.int32)

    # Every sheet below is packed [z, word]. cum_x is the only one that spans all lower
    # levels; the rest reach back at most two levels, per the Hilbert-basis argument.
    cum_x = np.zeros((size, nwords), dtype=np.uint64)      # losers at any strictly lower x
    xz_p1 = np.zeros((size, nwords), dtype=np.uint64)      # X,Z wedge sheet, level x-1
    xz_p2 = np.zeros((size, nwords), dtype=np.uint64)      # ... level x-2
    xz_cur = np.zeros((size, nwords), dtype=np.uint64)
    xy_p1 = np.zeros((size, nwords), dtype=np.uint64)      # X,Y wedge sheet, level x-1
    xy_p2 = np.zeros((size, nwords), dtype=np.uint64)      # ... level x-2
    xy_cur = np.zeros((size, nwords), dtype=np.uint64)
    L_p1 = np.zeros((size, nwords), dtype=np.uint64)       # losers, level x-1
    L_p2 = np.zeros((size, nwords), dtype=np.uint64)       # ... level x-2
    L_cur = np.zeros((size, nwords), dtype=np.uint64)
    # C[z] = L_cur[z] | yz[z]: everything the intra-sheet Y,Z wedge steps forward from.
    C = np.zeros((size, nwords), dtype=np.uint64)

    col = np.zeros(nwords, dtype=np.uint64)                # a loser sits above in this column
    yz = np.zeros(nwords, dtype=np.uint64)                 # Y,Z wedge, current row only
    win = np.zeros(nwords, dtype=np.uint64)

    for x in range(depth):
        for i in range(nwords):
            col[i] = ZERO
        for z in range(size):
            for i in range(nwords):
                L_cur[z, i] = ZERO

            for i in range(nwords):
                # Bits shifted in from the word below, for the +1 and +2 column steps.
                # (Packing is LSB-first, so a step toward larger y is a left shift.)
                b1 = L_p1[z, i] | xy_p1[z, i]
                b2 = L_p2[z, i] | xy_p2[z, i]
                b1_lo = ZERO if i == 0 else (L_p1[z, i - 1] | xy_p1[z, i - 1])
                b2_lo = ZERO if i == 0 else (L_p2[z, i - 1] | xy_p2[z, i - 1])

                # X,Y wedge: basis steps (x-1, y-1), (x-1, y-2), (x-2, y-1).
                xy = ((b1 << S1) | (b1_lo >> S63)) \
                    | ((b1 << S2) | (b1_lo >> S62)) \
                    | ((b2 << S1) | (b2_lo >> S63))
                xy_cur[z, i] = xy

                # X,Z wedge: basis steps (x-1, z-1), (x-1, z-2), (x-2, z-1). Row shifts only.
                xzw = ZERO
                if z >= 1:
                    xzw |= L_p1[z - 1, i] | xz_p1[z - 1, i] | L_p2[z - 1, i] | xz_p2[z - 1, i]
                if z >= 2:
                    xzw |= L_p1[z - 2, i] | xz_p1[z - 2, i]
                xz_cur[z, i] = xzw

                # Y,Z wedge: same three steps, but within this sheet, off rows z-1 and z-2.
                yzw = ZERO
                if z >= 1:
                    c1 = C[z - 1, i]
                    c1_lo = ZERO if i == 0 else C[z - 1, i - 1]
                    yzw |= ((c1 << S1) | (c1_lo >> S63)) | ((c1 << S2) | (c1_lo >> S62))
                if z >= 2:
                    c2 = C[z - 2, i]
                    c2_lo = ZERO if i == 0 else C[z - 2, i - 1]
                    yzw |= (c2 << S1) | (c2_lo >> S63)
                yz[i] = yzw

                # Inter-sheet moves are the instant-winner sheet; the intra-sheet ones (a
                # loser above in this column, the Y,Z wedge) finish the losing test. The
                # "loser earlier in this row" block is implicit: we take the first free bit.
                win[i] = cum_x[z, i] | xzw | xy | col[i] | yzw

            y0 = _first_zero(win, nwords, tail_mask, size)
            if y0 >= 0:
                bit = ONE << np.uint64(y0 & 63)
                w = y0 >> 6
                L_cur[z, w] = bit
                col[w] |= bit
                cum_x[z, w] |= bit
                loser_y[x, z] = y0

            for i in range(nwords):
                C[z, i] = L_cur[z, i] | yz[i]

        # Roll the two-level history forward.
        for z in range(size):
            for i in range(nwords):
                xz_p2[z, i] = xz_p1[z, i]
                xz_p1[z, i] = xz_cur[z, i]
                xy_p2[z, i] = xy_p1[z, i]
                xy_p1[z, i] = xy_cur[z, i]
                L_p2[z, i] = L_p1[z, i]
                L_p1[z, i] = L_cur[z, i]

    return loser_y


def points(loser_y, x, size=None):
    """The losers of sheet ``x`` as ``(y, z)`` arrays, optionally clipped to a smaller grid."""
    z = np.nonzero(loser_y[x] >= 0)[0]
    y = loser_y[x][z].astype(np.int64)
    if size is not None:
        keep = (y < size) & (z < size)
        y, z = y[keep], z[keep]
    return y, z.astype(np.int64)
