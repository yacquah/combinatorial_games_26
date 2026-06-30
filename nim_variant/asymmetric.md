# Asymmetric Bounded Nim

Three ordered piles $(x, y, z)$. Pile X is unrestricted; pile Y may not give up more than the
current size of X; pile Z may not give up more than the current size of Y.

### Moves

Every move is a **single-pile** (Nim-style) move — only one coordinate changes. The catch is that
the Y- and Z-moves carry a speed limit set by the pile to their left.

$$
\begin{aligned}
\text{Pile X (free):}\quad & [x,y,z] \rightarrow [x-t,\ y,\ z], & 0 < t \le x \\
\text{Pile Y (capped by X):}\quad & [x,y,z] \rightarrow [x,\ y-t,\ z], & 0 < t \le \min(x, y) \\
\text{Pile Z (capped by Y):}\quad & [x,y,z] \rightarrow [x,\ y,\ z-t], & 0 < t \le \min(y, z)
\end{aligned}
$$

Only the Pile X move changes $x$, so it is the **only inter-sheet move**; Y and Z stay inside a
sheet.

### Deriving the recursion operator $\mathcal{R}$ (inter-sheet)

The Pile X move is unrestricted, so from $[x,y,z]$ you can reach $[x', y, z]$ for *every* $x' < x$
with $(y,z)$ untouched. A single loser at $(y,z)$ on any lower sheet therefore makes $(y,z)$ an
instant winner on every sheet above it — each lower loser projects straight up the $x$-axis with no
shift. The operator is just the running union of all lower loser sheets:

$$W_x = \bigcup_{x'=0}^{x-1} L_{x'} \;=\; W_{x-1} \cup L_{x-1}.$$

**In code:** `lower_losers` is this running union. Each level does `W[x] = lower_losers`, then folds
in the sheet's new losers with `lower_losers |= L[x]`.

### Supermex operator $\mathcal{M}$ (intra-sheet)

Inside a sheet $x$ is fixed, leaving the Pile Y and Pile Z moves. Arrays are indexed `[z, y]`
(z = row, y = column). Two things make this cheap:

- The **Pile Y** move ($t \le \min(x,y)$) varies $y$, so it reaches losers only in the last $x$
  columns of the current row — a fixed-width window, since $x$ is constant on the sheet.
- The **Pile Z** move ($t \le \min(y,z)$) varies $z$, so it reaches losers only in the last $y$
  rows of the current column.

Inside a fixed-width window, only the *nearest* loser matters: if the closest one is inside the
window, the cell is a winner; if not, none are. So $\mathcal{M}$ keeps just two trackers instead of
scanning:

- `last_loser_z[y]` — the largest $z$ (row) at which a loser has appeared in column $y$.
- `last_loser_y` — the most recent loser column in the current row.

A cell $(y,z)$ that is not already in $W_x$ is a winner iff

$$\texttt{last\_loser\_y} \ge y - x \qquad\text{or}\qquad \texttt{last\_loser\_z}[y] \ge z - y,$$

i.e. the nearest loser falls inside the Pile Y window (width $x$) or the Pile Z window (width $y$).
Otherwise the cell is a new loser; we set $L_x(y,z)=1$ and update both trackers. This resolves each
cell in $O(1)$, for $O(N^3)$ overall.
