# Combined 3-Dimensional Wythoff's Game

The full 3-D generalization of Wythoff: ordinary 3-heap Nim, plus removing the same number of chips
from any two piles, plus removing the same number from all three piles.

### Moves

- **Single-pile (Nim):** change one coordinate.
- **Two-pile (Wythoff) X,Y / X,Z / Y,Z:** drop two coordinates by the same $t$. Because both drop
  together, the move walks down the 45° **diagonal** of that pair's plane.
- **Three-pile:** drop all three by the same $t$ (the main space diagonal).

$$
\begin{aligned}
\text{1 pile:}\quad & [x-t,y,z],\ [x,y-t,z],\ [x,y,z-t] \\
\text{2 piles:}\quad & [x-t,y-t,z],\ [x-t,y,z-t],\ [x,y-t,z-t] \\
\text{3 piles:}\quad & [x-t,y-t,z-t]
\end{aligned}
$$

Every coupling is at a clean $1\!:\!1$ ratio, so the recursion operator is built from plain
invariant shift operators — no dynamic bounds.

### Deriving the recursion operator $\mathcal{R}$ (inter-sheet)

**General rule.** An inter-sheet move that lowers $x$ by $t$ and another coordinate by the same $t$
keeps the *difference* of those two coordinates constant. As you move up one sheet ($x \to x+1$),
one extra unit of $t$ becomes available, so the shadow of every lower P-position shifts by exactly
$1$ along the partner axis. Such a move therefore becomes a single shift applied to "everything seen
so far on this move", refreshed with the newest P-sheet:

$$V_x \;=\; \mathcal{S}\big(V_{x-1} \cup P_{x-1}\big),$$

where $\mathcal{S}$ is the shift along the partner axis. Instantiating $\mathcal{S}$ for each
$x$-lowering move:

| Move | Partner axis | Shift $\mathcal{S}$ | Operator |
|------|--------------|---------------------|----------|
| $[x-t,y,z]$ (Nim X) | none | identity | $V^1_x = V^1_{x-1} \cup P_{x-1}$ |
| $[x-t,y-t,z]$ (X,Y) | $y$ | $\mathcal{Y}$ | $V^2_x = \mathcal{Y}(V^2_{x-1} \cup P_{x-1})$ |
| $[x-t,y,z-t]$ (X,Z) | $z$ | $\mathcal{Z}$ | $V^3_x = \mathcal{Z}(V^3_{x-1} \cup P_{x-1})$ |
| $[x-t,y-t,z-t]$ (3-pile) | $y$ and $z$ | $\mathcal{D}$ (diagonal) | $V^4_x = \mathcal{D}(V^4_{x-1} \cup P_{x-1})$ |

$$W_x = V^1_x \cup V^2_x \cup V^3_x \cup V^4_x.$$

**In code:** the four accumulators are `Ax, Bx, Cx, Dx`. Each level computes
`Wx = Ax | Bx | Cx | Dx`, then refreshes them with the new losers `Lx`:
`Ax |= Lx`, `Bx = shift_y(Bx | Lx)`, `Cx = shift_z(Cx | Lx)`, `Dx = shift_yz(Dx | Lx)` —
exactly the table above. `shift_y`/`shift_z`/`shift_yz` are $\mathcal{Y}/\mathcal{Z}/\mathcal{D}$.

### Supermex operator $\mathcal{M}$ (intra-sheet)

With $x$ fixed the remaining moves are Nim Y, Nim Z, and the Wythoff Y,Z move — which is precisely
ordinary **2-heap Wythoff** played on the $(y,z)$ plane. So $\mathcal{M}$ is the standard Wythoff
mex: scan for the first cell not already an IN-position, mark it as a P-position, and block its row,
its column, and its main diagonal $[y+t, z+t]$.

**In code:** `supermex` walks each column $y$, finds the first $z$ that is not in `Wx`, not in
`blocked_rows`, and not in `blocked_diags` (the diagonal keyed by $z-y$), marks it as a loser, and
sets those three blocks.
