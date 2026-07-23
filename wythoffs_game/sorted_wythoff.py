"""Bounded Wythoff played on *sorted* positions only: every position is kept as x >= y >= z.

Same game as ``wythoffs_game/bounded_wythoff.py`` -- 3-heap Nim plus a two-pile move that takes
``a`` from one pile and ``b`` from another with ``a <= 2b`` and ``b <= 2a`` -- but the three piles
are treated as an unordered multiset: after every move the piles are re-sorted so the largest is
always x. That collapses the game's 6-way permutation symmetry, so each loser appears exactly once
instead of once per ordering, and a sheet is a triangle (z <= y <= x) instead of a square.

Why this is a legal way to play
-------------------------------
Every move lowers one or two piles and touches nothing else. Sorting is monotone under that: the
k-th largest of the new multiset is <= the k-th largest of the old one for each k. So the sorted
target is <= the sorted source *componentwise*, and strictly smaller in at least one coordinate --
i.e. every legal move strictly decreases the sorted triple in dictionary order. The whole game is
therefore solvable by one pass over sorted triples in lexicographic order, which is what this module
does (x ascending, then y, then z).

Moves, from a sorted position (x, y, z), written as the target *multiset*:

    single pile:  {t, y, z} t<x    {x, t, z} t<y    {x, y, t} t<z
    two piles:    {x-a, y-b, z}    {x-a, y, z-b}    {x, y-a, z-b}       with 1/2 <= a/b <= 2

Keeping it O(N^3)
-----------------
*Single-pile moves.* A single-pile move keeps two piles and shrinks the third, so it asks: is there
a loser whose multiset contains the pair {y, z} (resp. {x, z}, {x, y}) with a small enough third
pile? So the only thing worth remembering about the losers found so far is, for each unordered pair
``(q, r)``, the **smallest third pile** ``pair_min[q][r]`` seen alongside it. Each of the three
single-pile moves is then one comparison. (Every loser recorded so far is lexicographically smaller
than the current position, which is exactly what makes the three comparisons ``pair_min[y][z] < x``,
``pair_min[x][z] < y``, ``pair_min[x][y] < z`` both sound and complete.)

*Two-pile moves.* The legal offsets ``(a, b)`` form the cone with extreme rays (2,1) and (1,2),
whose Hilbert basis is ``{(1,1), (1,2), (2,1)}`` -- see ``bounded_wythoff`` for that argument. So
"some bounded-ratio move on this pair reaches a loser" satisfies a one-step recurrence: it holds iff
one basis step back is already a loser, or itself has such a move on *the same pair of piles*. Each
cell therefore carries three flags, one per pile pair:

    P = pair {largest, middle}      Q = pair {largest, smallest}      R = pair {middle, smallest}

After a basis step the two marked piles may land in different slots of the re-sorted triple (a pair
that was {largest, middle} can become {largest, smallest}), so the recurrence hops between P, Q and
R -- ``_reach`` does that bookkeeping. The basis steps drop the level (= largest pile) by at most 2,
so only three levels of flags are ever live and the flag store is O(N^2), not O(N^3).

Output is sparse. Two losers cannot share their two largest piles (the smallest-pile Nim move would
join them), so ``loser_z[x, y]`` -- the smallest pile of the unique loser with largest x and middle
y, or -1 -- is the entire loser set in ``N^2`` ints.

Don't read these sheets as the usual ones
-----------------------------------------
The recurrence has to run with x = the largest pile, so a "sheet" here collects the losers whose
largest pile is exactly x -- a triangle of width x holding only a few dozen dots, empty above
y = x/(1+sqrt3). None of the familiar loser lines are in it, and that is correct rather than a bug:
those lines run out to y ~ 50x, so their largest pile is the y or z coordinate, and each of their
dots is filed on the much higher sheet named by that pile. Nothing is lost, only re-filed.

For pictures, slice at a fixed *smallest* pile instead -- that keeps a sheet's whole far field --
and use the existing bitboard engine, which reaches grids this O(N^3/6) solver cannot:

    python -m wythoffs_game.analysis.plot_3d --levels 0-40 --size 8000 --sorted

What this module is for is the other question: everything with all three piles below one bound,
where sorting is a genuine 6x saving and the triples come out already de-duplicated.
"""

import numpy as np
from numba import njit

from utils.display import run_sheet_session


@njit(cache=True)
def _reach(alpha, beta, gamma, H, loser_z):
    """True if the position {alpha, beta, gamma} is a loser, or has a bounded-ratio move on the
    pair {alpha, beta} that reaches one.

    ``alpha`` and ``beta`` are the two piles the move acts on and ``gamma`` is the bystander; the
    three are an arbitrary (unsorted) multiset. Sorting them tells us which of the caller's three
    flags to read: the bystander's slot in the sorted triple decides whether the marked pair is
    {largest, middle} (P), {largest, smallest} (Q) or {middle, smallest} (R). Ties are harmless --
    when two piles are equal the two candidate flags hold the same value.
    """
    a, b, c = alpha, beta, gamma
    if a < b:
        a, b = b, a
    if b < c:
        b, c = c, b
    if a < b:
        a, b = b, a

    if loser_z[a, b] == c:
        return True

    if gamma == c:
        kind = 0      # bystander is the smallest -> marked pair is {largest, middle}
    elif gamma == b:
        kind = 1      # bystander is the middle   -> marked pair is {largest, smallest}
    else:
        kind = 2      # bystander is the largest  -> marked pair is {middle, smallest}
    return H[a % 3, kind, b, c]


@njit(cache=True)
def _cone_hits(u, v, w, H, loser_z):
    """True if some bounded-ratio move on the pile pair (u, v), bystander w, reaches a loser.

    One Hilbert-basis step -- (1,1), (1,2) or (2,1) -- covers the whole cone, because ``_reach``
    folds the rest of the cone back in through the flag of the position one step behind.
    """
    if u >= 1 and v >= 1 and _reach(u - 1, v - 1, w, H, loser_z):
        return True
    if u >= 1 and v >= 2 and _reach(u - 1, v - 2, w, H, loser_z):
        return True
    if u >= 2 and v >= 1 and _reach(u - 2, v - 1, w, H, loser_z):
        return True
    return False


@njit(cache=True)
def _solve(size, cube_depth, cube_size, W, L):
    """Solve every sorted position with largest pile < ``size``, in lexicographic order.

    Fills ``loser_z[x, y]`` (the smallest pile of the loser with largest x and middle y, else -1)
    and returns it. If ``cube_depth > 0`` it additionally writes the dense sheets ``W`` and ``L``,
    indexed ``[x, z, y]`` (row z, column y) to match the rest of the codebase; cells outside the
    wedge z <= y <= x stay False, so a sheet is the lower-right triangle of the square.
    """
    loser_z = -np.ones((size, size), dtype=np.int32)

    # pair_min[q][r] (q >= r): smallest third pile over every loser found so far whose multiset
    # contains the pair {q, r}. ``size`` acts as +infinity (no pile is that big).
    pair_min = np.full((size, size), size, dtype=np.int32)

    # Two-pile flags, [level % 3, kind, y, z] with kind 0/1/2 = P/Q/R. A basis step lowers the
    # largest pile by at most 2, so three levels of history are enough.
    H = np.zeros((3, 3, size, size), dtype=np.bool_)

    for x in range(size):
        slot = x % 3
        for k in range(3):
            for y in range(x + 1):
                for z in range(y + 1):
                    H[slot, k, y, z] = False    # drop level x-3, which is now out of reach

        for y in range(x + 1):
            for z in range(y + 1):
                # Two-pile moves, one per pile pair.
                p = _cone_hits(x, y, z, H, loser_z)   # {largest, middle}
                q = _cone_hits(x, z, y, H, loser_z)   # {largest, smallest}
                r = _cone_hits(y, z, x, H, loser_z)   # {middle, smallest}
                H[slot, 0, y, z] = p
                H[slot, 1, y, z] = q
                H[slot, 2, y, z] = r

                # Single-pile moves: keep two piles, shrink the third below its current value.
                takes_max = p or q or pair_min[y, z] < x
                winner = (takes_max or r
                          or pair_min[x, z] < y      # shrink the middle pile
                          or pair_min[x, y] < z)     # shrink the smallest pile

                in_cube = x < cube_depth and y < cube_size and z < cube_size
                if in_cube:
                    W[x, z, y] = takes_max

                if not winner:
                    loser_z[x, y] = z
                    if pair_min[x, y] > z:
                        pair_min[x, y] = z
                    if pair_min[x, z] > y:
                        pair_min[x, z] = y
                    if pair_min[y, z] > x:
                        pair_min[y, z] = x
                    if in_cube:
                        L[x, z, y] = True

    return loser_z


_NO_CUBE = np.zeros((0, 0, 0), dtype=np.bool_)


def compute_loser_z(size):
    """Every sorted loser with largest pile < ``size``, sparsely.

    Returns ``loser_z`` of shape ``(size, size)``: ``loser_z[x, y]`` is the smallest pile of the
    unique loser whose largest pile is x and middle pile is y, or -1 if there is none. Only the
    lower triangle ``y <= x`` is meaningful.
    """
    return _solve(size, 0, 0, _NO_CUBE, _NO_CUBE)


def sorted_triples(loser_z):
    """The losers of ``compute_loser_z`` as an ``(n, 3)`` array of sorted triples (x, y, z)."""
    x, y = np.nonzero(loser_z >= 0)
    return np.column_stack((x, y, loser_z[x, y].astype(np.int64)))


def compute_sheets(depth, size):
    """Dense W and L sheets for x-levels ``0..depth-1``, for ``utils.display.run_sheet_session``.

    Sheets are indexed ``[x, z, y]`` and only the wedge ``z <= y <= x`` is ever set, so sheet x is a
    triangle: the sorted game states each position once instead of six times. Note ``size`` only
    crops the display -- on a sorted sheet no pile exceeds x, so the levels themselves fix how much
    there is to draw.

    These are the sheets the module docstring warns about: sliced at a fixed *largest* pile, so they
    look cut off and hold none of the loser lines (those dots are filed on the sheets named by their
    own largest pile). Useful for reading the origin blob -- sheet x carries the anti-diagonal
    ``y + z = (x+1)/3`` whenever ``x = 2 mod 3`` -- and not much else. For the familiar picture use
    ``analysis/plot_3d.py --sorted``.

    W is the sorted analogue of the instant-winner sheet: positions with a move that shrinks the
    *largest* pile onto a loser. Off the diagonal y = x, that is exactly "reaches a loser on a lower
    sheet", the same background of inherited winners that ``bounded_wythoff``'s W sheet shows.
    """
    W = np.zeros((depth, size, size), dtype=np.bool_)
    L = np.zeros((depth, size, size), dtype=np.bool_)
    _solve(depth, depth, size, W, L)
    return W, L


def main():
    """Prompt for one or more sorted Bounded Wythoff sheets and display them together."""
    # Sheets are indexed [x, z, y], and a level-m sheet is only m+1 wide, so T requests need no
    # margin beyond the level itself.
    run_sheet_session(compute_sheets, row_is_z=True, triplet_default=lambda m: m + 1)


if __name__ == "__main__":
    main()
