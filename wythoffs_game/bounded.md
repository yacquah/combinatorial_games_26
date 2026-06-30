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
whole cone behind each cell, each move keeps an **auxiliary sheet** that advances **one basis step at
a time**: a cell is a winner via the move iff a loser, or a cell already marked in the auxiliary
sheet, sits exactly one basis vector behind it.

For the **X,Y move** (offset in the $x,y$ plane, $z$ fixed), reading $(\Delta x, \Delta y)$ from each
basis vector gives:

$$
V^{xy}_x(y,z) =
\underbrace{L_{x-1}(y-1,z)\cup V^{xy}_{x-1}(y-1,z)}_{(1,1)} \;\cup\;
\underbrace{L_{x-1}(y-2,z)\cup V^{xy}_{x-1}(y-2,z)}_{(1,2)} \;\cup\;
\underbrace{L_{x-2}(y-1,z)\cup V^{xy}_{x-2}(y-1,z)}_{(2,1)}.
$$

The deepest basis vector steps back only $2$ in $x$, so the recursion needs **just the two previous
levels** — no 3-D prefix arrays. The X,Z move gives $V^{xz}_x$ by the same logic on the $z$ axis,
and Nim X is the usual running union $V^1_x$. Then $W_x = V^1_x \cup V^{xy}_x \cup V^{xz}_x$.

**In code:** sheets are indexed `[z, y]`. `aux_xy_prev1`/`aux_xy_prev2` are
$V^{xy}_{x-1}$/$V^{xy}_{x-2}$ (likewise `aux_xz_*`); the three `if/elif` clauses building `xy` are the
three basis terms above (reading the loser cube `L[x-1]`, `L[x-2]` for the $L$ part and the auxiliary
sheets for the $V$ part). `cum_x` is $V^1$. After each sheet the auxiliary sheets roll forward
(`aux_xy_prev2 = aux_xy_prev1`, `aux_xy_prev1 = aux_xy_cur`).

### Supermex operator $\mathcal{M}$ (intra-sheet)

With $x$ fixed the in-sheet moves are Nim Y, Nim Z, and the bounded-ratio **Y,Z** move — the same
cone, now in the $(y,z)$ plane. So the same three basis vectors drive an intra-sheet auxiliary sheet
$V^{yz}$, built from losers already found on this sheet. A cell is a loser iff it is not in $W_x$,
has no loser earlier in its row (Nim Y, varying $y$) or column (Nim Z, varying $z$), and is not
marked in $V^{yz}$.

**In code:** the whole thing is one fused pass. `loser_in_row` / `loser_in_col[y]` carry the Nim Y /
Nim Z look-backs, `aux_yz` is the intra-sheet auxiliary sheet, and a cell becomes a loser only when
`instant`, `loser_in_col[y]`, `loser_in_row`, and `yz` are all false. Because each basis test reads
one cell, the sheet is $O(N^2)$ and the whole game $O(N^3)$.
