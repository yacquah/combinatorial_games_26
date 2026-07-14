# Bounded Wythoff's Game
## Game Rules
Ordinary 3-heap Nim, plus a two-pile move that removes $a$ from one pile and $b$ from another, as
long as the amounts stay within a $1\!:\!2$ to $2\!:\!1$ ratio.

### Moves

- **Single-pile (Nim):** $[x-t,y,z],\ [x,y-t,z],\ [x,y,z-t]$.
- **Two-pile, bounded ratio** (any pair), with $\tfrac12 \le a/b \le 2$ and $a,b \ge 1$:

$$[x-a,\ y-b,\ z], \qquad [x-a,\ y,\ z-b], \qquad [x,\ y-a,\ z-b].$$

E.g. taking $4$ from one pile lets you take $2$ through $8$ from another (or $0$, an ordinary nim move).

</details>

## Recursive operator
To write $W_x = P_x(L_0)+P_x(L_1)+P_x(L_2)+\dots+P_x(L_{x-1})$:

If we have a loser on level $k$ then the difference in levels is $x-k$.

The normal nim move is just if $L_k(y,z)$ is a loser, then $W_x(y,z)$ is a winner.

And also due to the $xy$ and $xz$ moves, $W_x$ is a winner if $L_k(y-t,z)$ or $L_k(y,z-t)$ are losers for $\lceil{\frac{x-k}{2}}\rceil \le t \le 2(x-k)$.

We can define an operator $\mathcal{S}_\mathcal{d}$ where $d$ is $x-k$ and 
$$\mathcal{S}_\mathcal{d}L_k(y,z) = \sum\limits_{t=\lceil{d/2}\rceil}^{2d}{L_k(y-t,z)+L_k(y,z-t)}$$

So in total: $\boxed{W_x=\sum\limits_{k=0}^{x-1}{L_k+S_{x-k}L_k}}$

$W_{x+1}$ cannot be written in terms of $W_x$ alone

$$W_{x+1} = \sum_{k=0}^{x} \big(L_k + S_{x+1-k}(L_k)\big) = \underbrace{\big(L_x + S_1(L_x)\big)}_{\text{new sheet } x} + \sum_{k=0}^{x-1} \big(L_k + S_{(x-k)+1}(L_k)\big)$$

The sum is now $W_x$ but every $S_d$ is now $S_{d+1}$.

Farther edge: $2d \to 2d+2$.\
Closer edge: $\lceil d/2 \rceil \to \lceil (d{+}1)/2 \rceil$ which stays the same when $d$ is odd, but increases by one if $d$ is even.

A position in $W_x$ doesn't remember which loser generated it so we don't know if it should grow and in which direction.

So we need auxiliary sheets:

$W_{x+1}=V^1_{x+1}+V^2_{x+1}+V^3_{x+1}$

$V^1_{x+1}=V^1_x+L_x$

$V^2_{x+1} = S_y(V^2_x + L_x) + S^2_y(V^2_x + L_x) + S_y(V^2_{x-1} + L_{x-1})$

$V^3_{x+1} = S_z(V^3_x + L_x) + S^2_z(V^3_x + L_x) + S_z(V^3_{x-1} + L_{x-1})$

## Where this game sits in the literature

The **two-pile** version of this game is **Fraenkel's $(s,t)$-Wythoff game** with $(s,t) = (2,1)$. Fraenkel's rule — take $k > 0$ from one pile and $\ell \ge k$ from the other, subject to $\ell - k < (s-1)k + t$ — becomes exactly $k \le \ell \le 2k$ at $(2,1)$: take at least as much, and at most twice as much, from the second pile. That is precisely our ratio cone. Fraenkel solved the 2-pile game for every $(s,t)$ in 1998 [F98], and in 2004 explicitly listed extending these games to more than two piles as an open problem [F04].

The base sheet ($x=0$) represents the pure 2-pile game. It is exactly solvable via a discrete recurrence, Fraenkel's [F98, Theorem 1], specialized to $(s,t) = (2,1)$; we found it independently.

$S$ is exactly the set of P-positions.

**1. Independence (No move connects two points in $S$):** Standard single-pile moves cannot connect points in $S$ because the mex sequence partitions the integers (no shared coordinates). For 2-pile cone moves, removing $(s, t)$ such that $s \le 2t \le 4s$ fails algebraically. For example, moving from $(a_m, S_m) \to (a_n, S_n)$ requires $t = S_m - S_n = 2s + (m-n) > 2s$, which is an illegal move ratio.

**2. Coverage (Every position off $S$ can reach $S$):** For any $(y, z) \notin S$ (with $y \le z$), a winning strategy exists. If standard single-pile or diagonal-to-zero moves fail to reach $S$, the position lies in the wedge $2y < z$. This forces $y = a_n$ with $z < S_n$. By setting $k = z - 2y$, we get $1 \le k < n$, meaning $a_k < y$. The winning move is to remove $(s, t) = (y - a_k, 2(y - a_k))$, perfectly riding the $1:2$ edge of the threat cone to land exactly on $(a_k, S_k) \in S$.

**Asymptotics:** Fraenkel [F98, Theorem 2] proves that for every $s > 1$ **no floor formula** $a_n = \lfloor n\alpha + \gamma \rfloor$ can exist. Classical Wythoff's losers *do* have such a formula (the golden-ratio one), so the base sheet of our game is already provably one notch harder.

## Geometry of losers
### Edge Dots of Every Sheet

From any position with $y = 0$, every legal move keeps $y = 0$ (any move touching pile $y$ must remove at least one chip from it). The $y{=}0$ plane is therefore the 2-pile game played on piles $(x, z)$ so its losers match $L_0$. The $z=0$ plane is identical by symmetry.

These *edge dots* can be easily found, while the loser lines cross $y=0$ far higher ($c(x) \approx 5x$, Section 4).

### Why Every Sheet Has the Same Slope

For 3-heap play ($x > 0$) the P-positions of each sheet organize into two lines, and the slope is the same on every sheet even though the dot-by-dot pattern never repeats. The reason: two counting facts pin the slope, and neither fact depends on $x$. This section states the facts, derives the two equations, and solves them.

### What changes from sheet to sheet — and what doesn't

Sort the moves by whether they touch pile $x$. The moves that leave $x$ alone — Nim on $y$, Nim on $z$, and the $y \leftrightarrow z$ two-pile move — never mention $x$: they are identical on every sheet, and they are exactly the 2-pile game of Section 1. The moves that lower $x$ do only one thing to sheet $x$: they mark certain cells as automatic winners — the cells that can drop to a loser on some lower sheet. Call these **inherited winners**. So every sheet is the same 2-pile game played around a background of inherited winners, and that background is the only thing that varies with $x$.

Three facts hold exactly on every sheet, no matter what the background looks like:

1. **Exactly one loser per column (and per row).** Two losers cannot share a column — the Nim move on $z$ would let one reach the other. And every column has one: a two-pile move into column $y$ removes at most twice as much from the tall pile as from the short one, so threats from other columns reach only boundedly high; the lowest unthreatened cell in the column is a loser.
2. **Mirror symmetry.** Piles $y$ and $z$ are interchangeable, and the background of inherited winners is itself symmetric, so each sheet's loser set is symmetric across the diagonal: an upper dot at column $a$, height $b$ has a mirror dot at column $b$, height $a$.
3. **Threat edges climb with slope 2.** The steepest in-sheet two-pile move takes $k$ from one pile and $2k$ from the other, so the cells a loser turns into winners form a cone whose top edge has slope 2.

One definition. Most columns hold an upper-line dot; some are skipped (their loser sits on the lower line instead). The **density** $\lambda$ is the fraction of columns holding an upper dot.

### Equation 1: slope $= 2 + \lambda$

A new upper dot must sit above the slope-2 threat edges of all earlier dots on its sheet: clearing dot $j$ means $b > 2a + (b_j - 2a_j)$. Each new dot lands on the first free cell, exactly one above the highest edge (Section 3 checks cell-by-cell that nothing else is in the way), so the quantity $b_j - 2a_j$ grows by exactly 1 per dot, the newest edge is always the binding one, and consecutive dots satisfy

$$\Delta b = 2\,\Delta a + 1.$$

Sum this over a long stretch — $N$ dots covering $Y$ columns:

$$\text{total rise} = 2 \times (\text{total run}) + N = 2Y + N,$$

and dividing by the run $Y$, with $N/Y = \lambda$ (dots per column):

$$m = 2 + \lambda.$$

With no skipped columns the line would climb up-3-over-1 forever (slope 3); every skip trades a $3/1$ step for a $5/2$ step and drags the slope below 3. One equation, two unknowns — we need a second relation between $m$ and $\lambda$.

### Equation 2: $\lambda = \frac{m}{m+1}$

Count all the losers in the first $Y$ columns (imagine $Y = 1000$). By fact 1 there are exactly $Y$ of them, and by fact 2 each is either an upper dot or the mirror of one:

- *Upper dots:* $\lambda Y$, by the definition of density.
- *Mirror dots:* the mirror of an upper dot $(a, b)$ lands in column $b \approx m a$, which is inside the window only when $a \le Y/m \approx 366$. So there are about $\lambda Y/m$ of them — reflection spreads the upper dots over $m \approx 2.7\times$ as many columns, which is why the lower line is sparser.

The two counts must total $Y$:

$$\lambda Y + \frac{\lambda Y}{m} = Y \implies \lambda\left(1 + \frac{1}{m}\right) = 1 \implies \lambda = \frac{m}{m+1}.$$

### Solving the pair

Substitute Equation 2 into Equation 1 and multiply through by $(m+1)$:

$$m = 2 + \frac{m}{m+1} \implies m^2 + m = 2m + 2 + m \implies m^2 - 2m - 2 = 0 \implies \mathbf{m = 1+\sqrt{3}} \approx 2.7321,$$

and then $\lambda = m - 2 = \sqrt{3} - 1 \approx 0.7321$. The lower line's slope is $1/m = \frac{\sqrt{3}-1}{2} \approx 0.366$ and its column density is $2-\sqrt{3} \approx 0.268$. 

### Collisions move the intercept, not the slope

The stepping rule $\Delta b = 2\Delta a + 1$ has one exception. Occasionally the cell where the next dot should land — one above the newest threat edge — is already an inherited winner. This is a **collision** (Section 3), and the dot lands one cell higher: $\Delta b = 2\Delta a + 2$. The bookkeeping over any stretch of line is exact:

$$\text{total rise} = 2\,(\text{run}) + (\#\text{dots}) + (\#\text{collisions}), \qquad \text{i.e.} \qquad m_{\text{window}} = 2 + \lambda + \rho,$$

where $\rho$ is collisions per column. (Verified to the last digit in the scan data: total rise $225{,}425 = 2\cdot\text{run} + \text{dots} + \text{collisions}$.) So why don't collisions push the slope above $1+\sqrt{3}$? One geometric reason and one measured fact.

*Geometry: inherited winners sit below the line.* Consecutive sheets' lines are parallel with vertical spacing $\approx 5$ per level (Section 4). A loser $d$ levels down throws inherited winners into sheet $x$ at heights $\lceil d/2 \rceil$ through $2d$ above itself — which is roughly $3d$ to $4.5d$ **below** sheet $x$'s line, and the sideways-shifted ones land lower still. The background hugs the underside of the line; only the nearest level or two ever gets close, and a collision requires the line's local scatter to dip into it.


## 3. Microscopic Chaos: The Gap and Defect Logic

While the macroscopic geometry is a perfect fixed point, the exact point-by-point placements on sheets $x \ge 1$ are driven by a deterministic, computationally irreducible algorithm characterized by three rules:

**1. Stepping:** $\Delta b = 2\Delta a + 1$. Each upper-line loser sits exactly one cell above the slope-2 top edge of the previous upper loser's threat cone.

**2. Skipping:** $\Delta a = 2$ occurs exactly when the skipped column already holds a mirror loser on the lower line. This restricts the gap sequence between holes exclusively to the alphabet $\{3, 5\}$.

**3. Collisions (The Source of Chaos):** On sheets $x \ge 1$, the expected landing cell is occasionally pre-occupied by an instant-winner ($W$) inherited from a lower sheet. When this collision occurs, the P-position is kicked up by exactly 1. Collisions cluster just past the chaotic core and die out along the line (Section 2).

These defects permanently shift the sequence rank $n$, breaking any hope of a closed-form formula for the P-positions.

## 4. Scatter and Geometric Intercepts

Because the collisions depend on the highly complex geometric history of all lower sheets, the game exhibits severe sensitivity to initial conditions.

**Line Width:** As predicted by general Wythoff renormalization limits, the thickness of the scatter band grows linearly as $O(x)$. (e.g., from $[-1.8, 1.9]$ at $x=10$ to $[-7.0, 3.9]$ at $x=40$).

**Intercept Drift:** The geometric $z$-intercept of the upper line, $c(x) = \operatorname{median}(z - (1+\sqrt{3})y)$, shifts outward via an irregular, chaotic walk. The per-level increment $\delta(x)$ fluctuates pseudo-randomly between $\approx 3.5$ and $7$. While the running mean drifts upward toward an asymptote in the low 5s, the precise path of the intercept is mathematically chaotic.

## References

- **[F98]** A. S. Fraenkel, *Heap games, numeration systems and sequences*, Annals of Combinatorics **2** (1998), 197–210. Solves the 2-pile $(s,t)$ family; our base game is $(s,t) = (2,1)$. His Theorem 1 is our Section 1 recurrence; his Theorem 2 rules out any Beatty/floor formula for $s > 1$; his §§4–6 give the number system behind the $O(\log x)$ $\operatorname{partner}$ formula.
- **[F04]** A. S. Fraenkel, *New games related to old and new sequences*, INTEGERS **4** (2004), #G6. The same family recast via constraint functions; item 2 of "Further studies" poses the extension to more than two piles — this project — as an open problem.
