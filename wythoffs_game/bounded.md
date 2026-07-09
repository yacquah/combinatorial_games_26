# Bounded Wythoff's Game

Ordinary 3-heap Nim, plus a two-pile move that removes $a$ from one pile and $b$ from another, as
long as the amounts stay within a $1\!:\!2$ to $2\!:\!1$ ratio.

### Moves

- **Single-pile (Nim):** $[x-t,y,z],\ [x,y-t,z],\ [x,y,z-t]$.
- **Two-pile, bounded ratio** (any pair), with $\tfrac12 \le a/b \le 2$ and $a,b \ge 1$:

$$[x-a,\ y-b,\ z], \qquad [x-a,\ y,\ z-b], \qquad [x,\ y-a,\ z-b].$$

E.g. taking $4$ from one pile lets you take $2$ through $8$ from another (or $0$, an ordinary Nim move).

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

\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
Yes. There is no first-order recursion on the W-sheet alone (same situation as the paper's 3-D Wythoff example in §2.4 — the diagonal moves shift by an amount tied to the level difference), but there is a finite vector recursion on auxiliary sheets, and it's exactly what your existing bounded_wythoff.py implements. Here's the math, in the paper's operator notation.

The wedge is a cone with a 3-element Hilbert basis
Your shading rule says: a loser $k$ levels below shades offsets $t \in [\lceil k/2 \rceil,\ 2k]$ to the right (and up, for the other pairing). Check: $k=1 \to {1,2}$, $k=2 \to {1..4}$, $k=3 \to {2..6}$ — matches what you wrote. So the full set of (level-drop, shift) offsets is the integer cone

$$C = {(k,t) : k \ge 1,\ \lceil k/2\rceil \le t \le 2k},$$

bounded by the rays $(2,1)$ and $(1,2)$. That cone's Hilbert basis is ${(1,1), (1,2), (2,1)}$: every point of $C$ is a non-negative integer sum of those three vectors (the two extreme rays span a determinant-3 cone, and the interior vector $(1,1)$ fills the missing lattice points). Equivalently: from any point of $C$, subtracting one of the three basis vectors lands you back in $C$ or at the origin.

The recursion
Let $\mathcal{Y}^t$ be the shift-right-by-$t$ operator (paper's notation) and $+$ be logical OR. Define the auxiliary sheet for the X,Y two-pile move as the union of all wedge-shifted lower losers:

$$B^{xy}x = \sum{(k,t)\in C} \mathcal{Y}^t L_{x-k}.$$

Peeling off the last basis vector of each decomposition gives a recursion that never re-reads $L_0..L_{x-1}$:

$$\boxed{B^{xy}_{x+1} = \mathcal{Y}\big(B^{xy}x + L_x\big) ;+; \mathcal{Y}^2\big(B^{xy}x + L_x\big) ;+; \mathcal{Y}\big(B^{xy}{x-1} + L{x-1}\big)}$$

The three terms are the three basis steps $(1,1), (1,2), (2,1)$; the $(2,1)$ step is why the recursion reaches back two levels instead of one. (OR is idempotent, so points with multiple decompositions cause no trouble.) Identically for the X,Z move with the vertical shift $\mathcal{Z}$:

$$B^{xz}_{x+1} = \mathcal{Z}\big(B^{xz}x + L_x\big) + \mathcal{Z}^2\big(B^{xz}x + L_x\big) + \mathcal{Z}\big(B^{xz}{x-1} + L{x-1}\big)$$

and the ordinary straight Nim move keeps its usual accumulator $A_{x+1} = A_x + L_x$. Then

$$W_x = A_x + B^{xy}_x + B^{xz}_x, \qquad L_x = \mathcal{M}W_x,$$

where $\mathcal{M}$ is your wedge-blocking supermex (the intra-sheet Y,Z move). If you want it in the paper's strict first-order form $V_{x+1} = \mathcal{R}V_x$, just stack two levels into the state: $V_x = (A_x, B^{xy}x, B^{xy}{x-1}, B^{xz}x, B^{xz}{x-1}, L_x, L_{x-1})$.

What this means for manual_bounded.py
Two spots currently rescan history/ranges that the basis steps make O(1):

The for sheets_below in range(x) loop in compute_sheets (manual_bounded.py:90-91) — this is the $\sum_{x'} $ over all lower L-sheets you're asking to eliminate. Replace it with the two rolling auxiliary sheets above (kept for the previous two levels only), and the per-level cost drops from $O(x \cdot N^2)$ to $O(N^2)$, i.e. the whole computation from $O(N^4)$ to $O(N^3)$.
The for right_displacement in range(...) loop inside supermex (manual_bounded.py:61-71) — same wedge, intra-sheet. Since you process cells in increasing $(z, y)$, a cell is blocked by the Y,Z move iff a loser or already-blocked auxiliary cell sits one basis vector behind it: check $(z-1,y-1)$, $(z-1,y-2)$, $(z-2,y-1)$. That's the aux_yz sheet in bounded_wythoff.py.
One caveat on your parents shading: it only marks the two axis-aligned strips (up and right), which is correct for W since the two inter-sheet moves each fix one of $y, z$ — but note the strip lengths must be clipped by the pile bound ($t \le$ pile size), which your min(..., grid_size - z - 1) handles for the grid but the game rule min(2s, y) in your docstring is automatically satisfied since $t \le y$ is exactly "doesn't go below column 0" when shading from the loser upward. So the geometry you described is right; the recursion above generates the same strips level-by-level without the history scan.

Since bounded_wythoff.py (commit 29f1959) already implements all of this, the cheapest path is to diff your manual version's output against it at a few W/L levels to confirm they agree — happy to run that comparison if you want.


\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
The x = 0 sheet is exactly solvable
L₀ is the pure two-pile ratio-bounded game, and its losers follow a Wythoff-style mex recurrence with zero exceptions over 800+ pairs on a 3000-grid:

$$a_n = \operatorname{mex}{a_i, b_i : i < n}, \qquad \boxed{b_n = 2a_n + n}$$

with losers at $(a_n, b_n)$ and mirrors $(b_n, a_n)$, plus $(0,0)$. The sequences $a$ and $b$ partition the positive integers. Asymptotically $a_n \approx n\alpha$, $b_n \approx n\beta$ with

$$\alpha = \tfrac{1+\sqrt3}{2} \approx 1.366, \qquad \beta = 2\alpha+1 = 2+\sqrt3$$

(from $\beta = 2\alpha + 1$ and the Beatty condition $1/\alpha + 1/\beta = 1$, i.e. $2\alpha^2-2\alpha-1=0$). It's not an exact Beatty pair — $a_n - n\alpha$ wanders in about $[-1.45, 0.61]$ — but the deviation is bounded, so the recurrence is exact while the floor formula is only approximate. Line slopes: $1+\sqrt3 \approx 2.732$ (upper) and $\tfrac{1}{1+\sqrt3} = \tfrac{\sqrt3-1}{2} \approx 0.366$ (lower), at every x level (fits give 2.732–2.75 for all x ≤ 38).

The holes — your observation is exactly right
Every sheet is symmetric with exactly one loser per column and per row (empty columns in my counts are just grid truncation), so L_x is the graph of an involution pairing each y with a partner z. Columns split into two sets: those whose loser is on the upper line, and those whose loser is the mirror on the lower line. The holes in the upper line occur precisely at columns of the second kind — i.e. a column is skipped iff it already appears as a z-value of the lower line, which is your "mirrored across the diagonal" guess, confirmed.

The "up 3 over 1" vs "up 5 over 2" is forced by $b_n = 2a_n + n$: consecutive losers satisfy $\Delta b = 2\Delta a + 1$, so $\Delta a = 1 \Rightarrow \Delta b = 3$ and $\Delta a = 2$ (skipping a hole) $\Rightarrow \Delta b = 5$. The reason you can't see a period in when the skips happen: there isn't one. Hole density is exactly $1/\beta = 2-\sqrt3 \approx 0.268$ (measured 0.2685), and the gap sequence between holes is 3 5 3 5 3 3 3 5 … — a quasi-periodic Sturmian-type word driven by the irrational $\alpha$. It repeats approximately but never exactly, which matches your "for a while, then it changes" experience.

Higher x levels and the intercepts
The same law generalizes with a per-sheet offset. In the asymptotic tail (away from the chaotic region near the origin, whose size grows ~linearly with x), the n-th upper-line loser on sheet x satisfies exactly

$$b = 2a + n + k(x)$$

with a constant $k(x)$ per sheet: $k = 0, 3, 7, 11, 16, 20, 24, 29, 33, 37, 42, {\sim}46, 51, {\sim}56, {\sim}59, 64$ for $x = 0..15$ (the ~ entries had a couple of stray off-line losers shifting the index). So the intercept question reduces to $k(x)$: the upper line's z-intercept (and by symmetry the lower line's y-intercept) grows linearly-ish, ≈ 4.4·x (direct intercept fits gave $c(x)/x$ drifting 3.8 → 5.0 with growing scatter, so convergence is slow). The increments of $k$ are mostly the pattern 4,4,5 with occasional 3s — again quasi-periodic, not periodic. I didn't find a clean closed form for the constant; it doesn't match the obvious candidates ($2+\sqrt3$, $3+\sqrt3$, $2\sqrt3$). Pinning it down analytically is exactly the kind of thing the Friedman–Landsberg self-consistency equations are for: write the density/slope constraints for the forbidden regions of your W-sheets (whose inter-sheet wedges have rays 2 and 1/2) and solve for the intercept growth rate — that's the natural next step if you want the exact constant.

One practical note: the near-origin region where the lines break down grows with x, so when hunting patterns at level x, only trust columns $y \gtrsim 15x$ or so.

---

# July 8 session — mechanism, fixed point, and the $x=0$ theorem

*(Supersedes the "Higher x levels and the intercepts" notes above: the $k(x)$ table there is
window-dependent — see §3 below.)*

## 1. The gap logic is fully deterministic: the perching rule

Three rules, all verified against the engine:

1. **Perching.** Each upper-line loser sits **exactly one cell above the slope-2 top edge of the
   previous upper loser's move cone**: $\Delta b = 2\Delta a + 1$. The cell on the edge is a parent
   of the previous loser (offset ratio exactly $2$), hence blocked; the cell above it is the first
   candidate the supermex scan can accept. Gap $3 \iff \Delta a = 1$, gap $5 \iff \Delta a = 2$.
2. **Skipping.** $\Delta a = 2$ happens exactly when the skipped column already holds a mirror
   (lower-line) loser — the mex bookkeeping.
3. **Collisions.** On sheets $x \ge 1$ the perch cell is occasionally an instant-winner cell
   inherited from a lower sheet; the loser is then kicked up by exactly $1$. Verified: every tail
   defect found at $x = 10, 13, 14$ (5 of 5) has its expected perch cell in $W_x$. Defects occur
   arbitrarily deep (e.g. at $a \approx 108x$ on sheet $40$) at density $< 2$ per $1000$ columns.

So the gaps and intercepts have a **complete deterministic algorithm** — perch, skip, dodge — but
apparently no closed form: each collision depends on the point-by-point detail of all lower sheets,
and each one permanently shifts every subsequent perch. This is the Friedman–Landsberg "sensitivity
to initial conditions" (§3.2), and their open problem 11a conjectures exactly this situation: no
polynomial-time exact description, but exact *statistical* description.

## 2. Renormalization fixed point: slope and densities derived, not fitted

Let $m$ be the upper-line slope and $\lambda_U, \lambda_L$ the per-column densities of upper/lower
line losers. Two self-consistency conditions:

- **Cone-fill / perching:** over $Y$ columns the line rises $\sum \Delta b = 2Y + \#\text{points} =
  (2 + \lambda_U)Y$, so $m = 2 + \lambda_U$.
- **Complementarity + mirror symmetry:** every column holds exactly one loser, and the lower line is
  the mirror of the upper, so its column density is $\lambda_U/m$. Hence
  $\lambda_U + \lambda_U/m = 1$, i.e. $\lambda_U = \frac{m}{m+1}$.

Substituting: $m = 2 + \frac{m}{m+1} \;\Rightarrow\; m^2 - 2m - 2 = 0 \;\Rightarrow\;
\boxed{m = 1+\sqrt3}$, $\lambda_U = \sqrt3 - 1$, $\lambda_L = 2-\sqrt3$.

Measured (grid $12000^2$, all levels $x \le 60$): slope $2.7320 \pm 0.005$, $\lambda_U = 0.7320 \pm
0.001$, hole density $0.268$. All three match to four digits, **at every $x$ level** — the slopes
are universal in $x$.

## 3. Corrections: intercepts are an irregular walk, not a formula

- The per-sheet constant $k(x)$ in $b = 2a + n + k(x)$ is only **locally** constant: each defect
  shifts the rank $n$ by one, so the measured $k$ depends on the counting window. The earlier table
  ($0, 3, 7, 11, 16, \dots$) is unreliable past $x \approx 3$; do not pattern-hunt on it.
- The robust intercept is $c(x) = \operatorname{median}(z - (1+\sqrt3)\,y)$ over a clean tail
  window. Tracking fixed columns across levels (no fitting, no rank counting) gives the per-level
  increment $\delta(x) = c(x) - c(x-1)$:
  - $\delta(x) \ge 3$ always — forced, because the straight move and the $(1,1), (1,2)$ basis moves
    kill the 3 cells at offsets $0, +1, +2$ above the same column's previous-level loser.
  - $\delta(x)$ is often sharply concentrated (nearly every column jumps by exactly $4$ at $x=3$, by
    $7$ at $x=18$, by $10$ at $x=45$) but the sequence of increments fluctuates irregularly in
    $\approx [3.5, 7]$ with no periodicity found.
  - The running mean drifts $4.7 \to 5.35$ over $x \le 69$ without settling; consistent with
    $\approx 5.2$–$5.5$ asymptotically ($3\sqrt3 \approx 5.196$ and $2(1+\sqrt3) \approx 5.464$ both
    compatible, neither confirmed).

## 4. Scatter: how deviation from "the line" is measured (no best-fit needed)

- At $x=0$ the recurrence is exact (zero exceptions to $n \approx 3200$), so residuals against the
  law are identically zero. Against the ideal line $z = (1+\sqrt3)y + c$ the residual is a
  **deterministic bounded sawtooth** in $[-0.8, +0.8]$ — quasi-periodic wobble of the $\{3,5\}$ step
  word, not noise, and it never grows.
- For $x > 0$: fix the slope to $1+\sqrt3$ (universal), take $c$ = median residual. Total line width
  grows roughly linearly: $[-0.8,0.8]$ at $x{=}0$ → $[-1.8,1.9]$ at $x{=}10$ → $[-4.4,3.1]$ at
  $x{=}24$ → $[-7.0,3.9]$ at $x{=}40$ (fattens mostly on the underside). Linear-in-level width is
  the same scaling Friedman–Landsberg derive for Wythoff's Grundy values (Nivasch's $O(g)$ bound).

## 5. Gap statistics, every level

In clean windows the hole-gap alphabet is $\{3,5\}$ at **every** level, with the frequency of 5s
$\approx 0.36 \approx \alpha - 1$ (exact at $x=0$; occasional 6s appear only at defect sites). The
gap word is Sturmian-type, driven by the irrational $\alpha = \frac{1+\sqrt3}{2}$: same statistics
on every sheet, different actual word per sheet, periodic on none.

## 6. Literature notes (checked 2026-07-08)

- **Fraenkel's $m$-Wythoff** bounds the *difference* of the removals ($|s-t| < m$; P-positions
  $b_n = a_n + mn$, exact Beatty).
- **Larsson, "A Generalized Diagonal Wythoff Nim"** (arXiv:1005.1555) adjoins a *single* ratio ray
  $(pt, qt)$; studies P-beam splitting.
- **Kay & Polanco, "Relaxed Wythoff has All Beatty Solutions"** (arXiv:2208.00041) studies
  constraint-function families with mex recurrences and characterizes exactly when they produce
  true Beatty pairs.
- Our game — the full ratio **cone** $\tfrac12 \le s/t \le 2$, solution $b_n = 2a_n + n$,
  **bounded-but-not-Beatty** deviations — was not found verbatim in any of them. Plausibly novel;
  at minimum a natural example in the non-Beatty regime that Kay–Polanco's criterion delimits.

---

# Theorem ($x=0$ sheet): exact solution of two-pile bounded-ratio Wythoff

**Game.** Two piles $(y, z)$. Moves: (i) remove any positive number of tokens from one pile;
(ii) remove $s \ge 1$ from one pile and $t \ge 1$ from the other with $s \le 2t$ and $t \le 2s$.
Last player to move wins.

**Definitions.** Let $a_0 = b_0 = 0$ and for $n \ge 1$:

$$a_n = \operatorname{mex}\{a_i, b_i : 1 \le i < n\}, \qquad b_n = 2a_n + n.$$

Let $S = \{(0,0)\} \cup \{(a_n, b_n) : n \ge 1\} \cup \{(b_n, a_n) : n \ge 1\}$.

**Theorem.** $S$ is exactly the set of P-positions.

### Lemma 1 (sequence facts) — routine, to write up

1. $(a_n)$ and $(b_n)$ are strictly increasing. *(mex of a growing excluded set is nondecreasing
   and cannot repeat; $b_n = 2a_n + n$ inherits.)*
2. $\{a_n\} \cap \{b_m\} = \varnothing$ and $\{a_n\} \cup \{b_n\} = \mathbb{Z}^+$. *(Standard mex
   argument: $a_n$ avoids all earlier values by construction and $b_n > a_n$; every integer is
   eventually the mex.)*
3. Consequently **every positive integer is a coordinate of exactly one point of $S$** (each value
   appears in exactly one pair, on one side).
4. $\Delta a_n \in \{1, 2\}$ and $\Delta b_n = 2\Delta a_n + 1 \in \{3, 5\}$.

### Part A: no move connects two points of $S$ (independence) — complete

*Single-pile moves* fix one coordinate; by Lemma 1.3 no two points of $S$ share a coordinate, so no
single-pile move connects them.

*Two-pile moves.* Write the move as subtracting $(s, t)$, $s, t \ge 1$, $s \le 2t \le 4s$. Check
each pair type (using $b_k = 2a_k + k$ throughout), for $m > n$:

- **upper → upper**, $(a_m, b_m) \to (a_n, b_n)$: $\;t = b_m - b_n = 2(a_m - a_n) + (m - n)
  = 2s + (m-n) > 2s$. Illegal.
- **upper → lower**, $(a_m, b_m) \to (b_n, a_n)$ (requires $a_m > b_n$): $\;t - 2s =
  (b_m - a_n) - 2(a_m - b_n) = m + 3a_n + 2n > 0$, so $t > 2s$. Illegal.
- **lower → upper**, $(b_m, a_m) \to (a_n, b_n)$ (requires $a_m > b_n$): symmetric computation
  gives $s - 2t = m + 3a_n + 2n > 0$, so $s > 2t$. Illegal.
- **lower → lower**: mirror image of upper → upper. Illegal.
- **anything → $(0,0)$** diagonally: from $(a_n, b_n)$, $t/s = b_n/a_n = 2 + n/a_n > 2$. Illegal
  (mirror for lower). Single-pile moves cannot empty both piles.

Verified exhaustively by machine over all $S$-pairs with coordinates $\le 3000$: zero violations.

### Part B: every position off $S$ has a move into $S$ (coverage) — complete

Let $(y, z) \notin S$, wlog $y \le z$ (the game is symmetric). Let $p(v)$ = the partner of value
$v$ (the other coordinate of the unique $S$-point having coordinate $v$; $p(0) = 0$). Play the
first applicable rule:

1. **Column.** If $p(y) < z$: single-pile move to $(y, p(y)) \in S$.
2. **Row.** If $p(z) < y$: single-pile move to $(p(z), z) \in S$.
3. **Origin.** If $z \le 2y$ (and $y \ge 1$): diagonal move $(s,t) = (y, z)$ to $(0,0)$ — legal
   since $y \le z \le 2y$ puts the ratio in bounds.
4. **Wedge.** Otherwise $2y < z$, and rules 1–2 failed, which forces $y = a_n$ for some $n$ with
   $z < b_n$ *(if $y$ were a $b$-value its partner would be below, rule 1; if $y = a_n$ with
   $b_n < z$, rule 1 again; $z = b_m$ would give $m < n$, partner $a_m < a_n = y$, rule 2)*. Set

   $$k = z - 2y.$$

   Then $1 \le k$ (since $z > 2y$) and $k < n$ (since $z < b_n = 2a_n + n = 2y + n$), so
   $a_k < a_n = y$ by Lemma 1.1. Move diagonally by $(s, t) = (y - a_k,\ 2(y - a_k))$ — ratio
   exactly $2$, legal — and land on

   $$\big(y - s,\ z - t\big) = \big(a_k,\ z - 2y + 2a_k\big) = \big(a_k,\ 2a_k + k\big)
   = (a_k, b_k) \in S. \qquad \blacksquare$$

   *(The identity in rule 4 is exact — no asymptotics or deviation bounds needed. Note the move
   removes $(s, 2s)$: the winning move rides the cone's slope-2 edge, the same edge the losers
   perch above. That is the whole geometry of the game in one line.)*

Verified exhaustively by machine for all $(y,z) \in [0,1000]^2$: rule 4's first candidate succeeds
every time; usage split col/row/origin/wedge $\approx 268\text{k}/62\text{k}/135\text{k}/36\text{k}$.

### Corollaries

1. Slopes: $b_n/a_n \to 1+\sqrt3$, mirror $\tfrac{\sqrt3-1}{2}$; densities $\lambda_U = \sqrt3-1$,
   $\lambda_L = 2-\sqrt3$ (from Lemma 1 + $\beta = 2\alpha+1$, $1/\alpha + 1/\beta = 1$).
2. Gap alphabet $\{3,5\}$ with 5-frequency $\alpha - 1$ (Lemma 1.4 + densities).
3. The winning strategy is the explicit four-rule recipe of Part B — implementable in $O(1)$ per
   move given the sequences.

### Remaining write-up work (not gaps in the argument)

- Prove Lemma 1.1–1.2 carefully (half a page, standard).
- State and prove the bounded-deviation estimate $|a_n - n\alpha| \le C$ (observed $C < 1.5$);
  candidate approach: the potential $\varphi_n = a_n - \alpha n$ changes by $1-\alpha$ or $2-\alpha$
  per step according to the skip word, and skips are governed by the density identity in §2.
- Optional: formalize the perching/collision description of sheets $x \ge 1$ as a corollary of the
  same cone algebra plus the $W$-recursion (the defect mechanism verified in §1).