# Bounded Wythoff's Game

Ordinary 3-heap Nim, plus a two-pile move that removes $a$ from one pile and $b$ from another, as
long as the amounts stay within a $1\!:\!2$ to $2\!:\!1$ ratio.

### Moves

- **Single-pile (Nim):** $[x-t,y,z],\ [x,y-t,z],\ [x,y,z-t]$.
- **Two-pile, bounded ratio** (any pair), with $\tfrac12 \le a/b \le 2$ and $a,b \ge 1$:

$$[x-a,\ y-b,\ z], \qquad [x-a,\ y,\ z-b], \qquad [x,\ y-a,\ z-b].$$

E.g. taking $4$ from one pile lets you take $2$ through $8$ from another (or $0$, an ordinary Nim
move).

### Deriving the recursion operator $\mathcal{R}$ (inter-sheet)

For a $1\!:\!1$-ratio move a single shift operator suffices (see Combined Wythoff). Here the legal
offsets $(a,b)$ are not a line but a **2-D cone**: all integer points between the rays $(2,1)$ and
$(1,2)$. We need a finite set of shifts whose non-negative combinations hit *every* point of that
cone — its **Hilbert basis**.

The two extreme rays $(2,1)$ and $(1,2)$ span a cone of determinant $3$ (non-unimodular), so they
alone miss interior points; the gap is filled by the interior vector $(1,1)$. Hence

$$\text{Hilbert basis} = \{(1,1),\ (1,2),\ (2,1)\},$$

and every legal offset is a non-negative integer combination of these three. So rather than scan the
whole cone behind each cell, we push each P-position's "shadow" forward **one basis step at a time**:
a cell is an IN-position iff a P-position, or an already-shadowed cell, sits exactly one basis vector
behind it.

For the **X,Y move** (offset in the $x,y$ plane, $z$ fixed), reading $(\Delta x, \Delta y)$ from each
basis vector gives:

$$
V^{xy}_x(y,z) =
\underbrace{P_{x-1}(y-1,z)\cup V^{xy}_{x-1}(y-1,z)}_{(1,1)} \;\cup\;
\underbrace{P_{x-1}(y-2,z)\cup V^{xy}_{x-1}(y-2,z)}_{(1,2)} \;\cup\;
\underbrace{P_{x-2}(y-1,z)\cup V^{xy}_{x-2}(y-1,z)}_{(2,1)}.
$$

The deepest basis vector steps back only $2$ in $x$, so the recursion needs **just the two previous
levels** — no 3-D prefix arrays. The X,Z move gives $V^{xz}_x$ by the same logic on the $z$ axis,
and Nim X is the usual running union $V^1_x$. Then $W_x = V^1_x \cup V^{xy}_x \cup V^{xz}_x$.

**In code:** `A_xy_p1`/`A_xy_p2` are $V^{xy}_{x-1}$/$V^{xy}_{x-2}$ (likewise `A_xz_*`); the three
`if/elif` clauses building `xy` are the three basis terms above (reading `L[x-1]`, `L[x-2]` for the
$P$ part and the accumulators for the $V$ part). `cumX` is $V^1$. After each sheet the accumulators
roll forward (`A_xy_p2 = A_xy_p1`, `A_xy_p1 = A_xy_cur`).

### Supermex operator $\mathcal{M}$ (intra-sheet)

With $x$ fixed the in-sheet moves are Nim Y, Nim Z, and the bounded-ratio **Y,Z** move — the same
cone, now in the $(y,z)$ plane. So the same three basis vectors drive an intra-sheet shadow
accumulator $V^{yz}$, built from losers already found on this sheet. A cell is a P-position iff it is
not in $W_x$, has no loser to its left (Nim Y) or above it (Nim Z), and is not shadowed in $V^{yz}$.

**In code:** the whole thing is one fused pass. `row_has` / `colseen[z]` carry the Nim Y / Nim Z
look-backs, `A_yz` is the intra-sheet basis accumulator, and a cell becomes a loser only when
`inst`, `colseen[z]`, `row_has`, and `yz` are all false. Because each basis test reads one cell, the
sheet is $O(N^2)$ and the whole game $O(N^3)$.
