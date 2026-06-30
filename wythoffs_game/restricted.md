# Restricted Wythoff's Game

Ordinary 3-heap Nim, plus a two-pile Wythoff move whose size is bounded by the third, untouched
pile.

### Moves

- **Single-pile (Nim):** $[x-t,y,z],\ [x,y-t,z],\ [x,y,z-t]$.
- **Two-pile (Wythoff), bounded by the third pile:**

$$
\begin{aligned}
{}[x,y,z] &\rightarrow [x-t,\ y-t,\ z] && t \le z \\
{}[x,y,z] &\rightarrow [x-t,\ y,\ z-t] && t \le y \\
{}[x,y,z] &\rightarrow [x,\ y-t,\ z-t] && t \le x
\end{aligned}
$$

The two-pile move is the usual Wythoff diagonal, but the amount you may remove is capped by the
pile you *don't* touch.

### Deriving the recursion operator $\mathcal{R}$ (inter-sheet)

The $x$-lowering moves are Nim X, the X,Y move (bounded by $z$), and the X,Z move (bounded by $y$).

**Why a plain shift fails.** In Combined Wythoff the X,Y move was $\mathcal{Y}(V_{x-1} \cup
L_{x-1})$ because the move length was unbounded — every shift was legal. Here the move length is
capped by $z$ (a *third* coordinate), so the legal move length changes cell by cell. A single
invariant shift can't express that bound, so we track positions instead of shifting them.

**X,Y move** $[x-t, y-t, z]$. It drops $x$ and $y$ together, so it keeps $x-y$ constant: the source
loser lies on the same $(x-y)$ diagonal, on a lower sheet $x' = x-t$. The bound $t \le z$ means
$x' \ge x - z$. So a cell is a winner iff *some* loser on its $(x-y)$ diagonal sits no more than $z$
sheets below it. We only need the **closest** such loser, i.e. the largest $x'$ seen on that
diagonal:

$$\mathrm{MaxX}^{xy}(x-y,\ z) \ge x - z.$$

**X,Z move** $[x-t, y, z-t]$. Symmetric: it keeps $x-z$ constant and is bounded by $y$, so the
condition is

$$\mathrm{MaxX}^{xz}(x-z,\ y) \ge x - y.$$

**Nim X** contributes the usual running union $\bigcup_{x'<x} L_{x'}$.

A cell is in $W_x$ if Nim X fires, or either diagonal condition above holds.

**In code:** `cumL` is the Nim-X running union. `last_xy[(x-y)+size, z]` and `last_xz[(x-z)+size, y]`
store $\mathrm{MaxX}^{xy}$ and $\mathrm{MaxX}^{xz}$ — the most recent sheet that put a loser on that
diagonal. Building $W_x$ is three $O(1)$ tests per cell (`cumL`, `last_xy >= x - z`,
`last_xz >= x - y`); after `supermex` produces $L_x$, each new loser updates `cumL`, `last_xy`, and
`last_xz`. This keeps the whole computation $O(N^3)$ with no 3-D loser history.

### Supermex operator $\mathcal{M}$ (intra-sheet)

With $x$ fixed the in-sheet moves are Nim Y, Nim Z, and the Y,Z move bounded by $x$ (so $t \le x$).
The first two block a full row and column as in plain Wythoff. The bounded Y,Z move differs from
standard Wythoff in one way: instead of blocking an *infinite* diagonal, each new loser blocks a
diagonal segment of length exactly $x$ — positions $[y+t, z+t]$ for $t = 1 \dots x$ — because the
move can remove at most $x$.

**In code:** `supermex` scans each column for the first free $z$, marks the loser, blocks that row
(`blocked_rows`), and writes the length-$x$ diagonal into `diag_blocked` (the `for t in range(1,
x+1)` loop). Because the diagonal is finite, a per-diagonal boolean won't do — the specific blocked
cells are recorded individually.
