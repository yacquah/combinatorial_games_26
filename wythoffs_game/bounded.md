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


## 3. Structure of the Core

Section 2 describes each sheet far from the origin, where the dots settle onto slope $1+\sqrt3$.
Near the origin they do not: the first few thousand columns of a sheet look steeper and messier,
and this transient region — the **core** — is where the sheet's intercept is decided. The core
is not shapeless. It splits into three regions, and the largest of them has an exact formula.

### The core branch: an exact line of slope 3

Between roughly column $x$ and column $(1+\sqrt3)\,x$, every upper loser of sheet $x$ sits on
one exact line:

$$\boxed{z = 3(x+y) - 1}$$

Not approximately — exactly, with no scatter at all. On sheet $700$ this predicts $1173$
consecutive losers with zero misses; on sheet $200$, $320$ of them. It holds for **every sheet
$x \ge 29$** (and sporadically from $x = 17$); below that the core is too short for a clean run
and the constant falls $3$ to $6$ short. Verified independently on three grid sizes
($3{,}500$, $8{,}000$, $36{,}000$) — losers never move as the grid grows, so the agreement is a
real check and not a fitting artifact.

**Why slope 3.** Section 2 proved the stepping rule $\Delta b = 2\Delta a + 1$: each new upper
dot lands one cell above the previous dot's slope-2 threat edge. Section 2 then averaged this
over a long stretch, where some columns are skipped, to get slope $2 + \lambda$. But inside the
core *no columns are skipped*. A skip happens only when a column is already occupied by a mirror
dot, and the mirrors of these core dots land out at column $z \approx 3y$, far to the right —
they have not arrived yet. So the local density is $\lambda_{\text{local}} = 1$, every column
carries a dot, $\Delta a = 1$ throughout, and the stepping rule gives

$$\Delta b = 2(1) + 1 = 3$$

exactly, cell after cell. The core is the pure stepping regime, before mirrors start forcing
skips.

**Where it ends.** The branch stops at $y^{*} = 2.7277\,x$, measured across sheets $50$ to
$600$ — indistinguishable from $(1+\sqrt3)\,x$. Past that column skipped columns appear,
$\Delta a$ starts taking the value $2$, and the residual $z - 3y$ begins drifting down: the line
bending from slope $3$ onto its asymptotic $1+\sqrt3$. This measured $y^{*}(x)$ replaces the old
hand-fitted core width.

That $y^{*}$ should equal $(1+\sqrt3)x$ is presumably the arrival of the first mirrors — a dot
at height $h$ reflects into column $h$, so the branch survives exactly until the lowest dots of
the wall fan, which sit at heights of order $(1+\sqrt3)x$, start reflecting back into it. This
is a plausible mechanism, not yet a proof: the wall fan's heights spread over a wide range
(sheet $100$: $18$ to $593$, around $(1+\sqrt3)x = 273$), so which dot binds first still needs
to be pinned down.

**Where collisions fit.** Track the residual $r = z - 3y$ across a whole sheet and it tells the
story in three acts. Approaching the branch it *climbs* to $3x - 1$ in steps of $+1$, $+2$ and
$+3$ (sheet $50$: $137, 139, 140, 143, 145, 148, 149$; sheet $200$: $591 \dots 599$). Then, for
the whole length of the branch, it is **exactly constant** — sheet $200$ holds $r = 599$
unbroken from column $230$ to column $549$. Only past $y^{*}$ does it start decaying, as the
line bends onto slope $1+\sqrt3$.

The middle act is the surprising one: there are **no collisions on the branch at all**. That is
precisely why the formula is exact rather than approximate — the inherited winners from lower
sheets sit clear of it, so nothing perturbs the stepping rule over hundreds of consecutive
columns. Collisions live on either side of the branch, not within it. The measured core slope of
$\approx 3.22$ therefore averages the clean slope-$3$ branch together with the collision-ridden
approach and the bending tail; it is not the branch's own slope, which is exactly $3$.

Note the line does **not** pass through the edge dot: extrapolating to $y=0$ gives $3x-1$, while
the true $y=0$ loser is $\operatorname{partner}(x)$ (e.g. sheet $50$: $149$ versus $18$). The two
are unrelated quantities. The origin of the constant $-1$ is not yet explained.

### The wall fan: solved by reduction

For $y < x$ the dots hug the wall and fan upward. These are not new data. The three-pile
symmetry — $(x,y,z)$ is a loser exactly when $(y,x,z)$ is, verified over $14{,}400$ pairs with
zero mismatches — means sheet $x$'s dot in column $y$ *is* sheet $y$'s dot in column $x$. So the
wall fan of a high sheet is a slice through every lower sheet's tail, at height
$\approx (1+\sqrt3)x + c(y)$. It is solved in the sense that it reduces exactly to lower sheets,
and it is also the mechanism by which every lower intercept $c(y)$ is carried into sheet $x$'s
core.

### The three blobs: the same law seen from a different side

Plot a single sheet and three tight clusters of dots stand out against the empty middle: one
sitting on the origin, and a mirror pair far out at roughly $(x, 3x)$ and $(3x, x)$. The first
of these is completely explained by the branch law — it *is* the branch law, read with the
coordinates permuted.

The loser set is symmetric in all three piles, so the branch law is really a statement about
unordered triples: for a loser $(p, q, r)$ with $r$ the largest coordinate,

$$r = 3(p+q) - 1 .$$

Section 3's slope-3 branch is what you see when the sheet coordinate $x$ is one of the two
*small* piles: fixing $x$ and solving for $z$ gives $z = 3(x+y)-1$, a line of slope $3$. But the
same surface can be met with $x$ as the *largest* pile. Then it reads $x = 3(y+z) - 1$, which
fixes the sum:

$$y + z = \frac{x+1}{3}.$$

A constant sum is a line of slope $-1$ — the anti-diagonal blob at the origin. Sheet $50$ carries
the eight positions $(5,12), (6,11), \dots, (12,5)$ on $y+z = 17$, and indeed $3 \cdot 17 - 1 = 50$.

This also explains the blob's odd on-off behaviour. The sum $y+z$ must be a whole number, so the
family can only exist when $3$ divides $x+1$ — that is, when

$$x \equiv 2 \pmod 3 .$$

That is exactly what the data shows: an exact anti-diagonal on $55$ of the $61$ sheets with
$x \equiv 2 \bmod 3$ up to $200$ (sheet $200$ carries $22$ dots on $y+z=67$, and
$3 \cdot 67 - 1 = 200$), and essentially nothing on the others — sheets $120$ and $180$ have none
at all. Sheets just off the residue sometimes show a broken near-miss one unit away (sheet $100$
has six dots on $y+z=34$, which would need $x = 101$), the same way the branch itself falls a few
short at small $x$.

**The mirror pair is a limit shape, not an integer law.** The two far blobs sit at
$\min(y,z) \approx x$ and $\max(y,z) \approx 3x$ — and they are each other's reflections across
$y = z$ (checked exactly: on every sheet from $x = 100$ to $800$, all $9803$ blob dots $(y,z)$
have their mirror $(z,y)$ a loser as well, zero misses). That reflection is the key to reading
them: since swapping $y$ and $z$ carries one blob onto the other, both are the *same* family of
positions — the ones with **two equal piles**. A position $(n, n, c)$ shows up on sheet $n$ once
with the big pile as $z$ (the upper blob, $y = n$) and once with it as $y$ (the lower blob,
$z = n$).

For this family there is no exact arithmetic law — and there cannot be, because the family is
**scale-invariant**. Unlike the branch, whose residual $z - 3(x+y)$ is a fixed integer, the
two-equal-pile blob keeps a *fixed ratio*: the big pile grows in proportion to the small ones,

$$\frac{c}{n} \;\longrightarrow\; \frac{3}{2} + \sqrt3 \;=\; m + \tfrac12 \;\approx\; 3.2320,$$

where $m = 1+\sqrt3$ is the main slope. This is the same *kind* of result as the asymptotic
slope and density of Section 2 — a measured limiting constant, identified in closed form, not a
Diophantine identity. The evidence: the blob's upper edge, measured as the largest $z/y$ among
its dots, climbs monotonically toward $m + \tfrac12$ from below as $x$ grows — median
$3.2227 \to 3.2291 \to 3.2302 \to 3.2308 \to 3.2311$ across windows from $x\approx150$ to $800$,
the gap to $m+\tfrac12$ roughly halving each time — and never overshoots, which is what rules out
a nearby rational like $3.23$. The ratio $c/n$ at the exact diagonal $y=x$ tells the same story,
converging to $m+\tfrac12$ from below. Every number here reproduces identically on two independent
grids ($3500$ and $8000$ wide), so it is a property of the losers, not of a truncated window.

Heuristically the extra $\tfrac12$ over the main slope is the diagonal two-pile move's
contribution: on $(n,n,c)$ the ratio-bounded move is available on the equal pair (ratio $1$) but
*forbidden* on either $(n,c)$ pair (ratio $\approx 1{:}3$ is outside $[\tfrac12, 2]$), so this
family sits exactly on the boundary where the move's availability changes — but a proof that the
boundary lands at $m + \tfrac12$ is still open.

Geometrically the blob marks the far end of the approach region, sitting just *below* where the
core branch begins: on sheet $200$ its top dot is at $z = 648 \approx 3.24x$ while the branch's
lowest dot is up at $z \approx 4.10x$, a gap of about $0.86x$ that holds across sheets — the
visible empty band between the two.

(This corrects an earlier note that dismissed the "near-diagonal family $(x,x,z)$" as noise. It
is noise only as an *absolute* residual $z - 3x$, which grows with $x$; as a *ratio* it is this
clean limit shape. The near-diagonal family and the mirror-pair blobs are the same object.)

### The remaining chaos

Past $y^{*} = (1+\sqrt3)x$ and before the tail settles (around $y \approx 50x$) the dots are
genuinely transitional, and the point-by-point placements there are driven by a deterministic
but computationally irreducible algorithm with three rules:

**1. Stepping:** $\Delta b = 2\Delta a + 1$. Each upper-line loser sits exactly one cell above the slope-2 top edge of the previous upper loser's threat cone.

**2. Skipping:** $\Delta a = 2$ occurs exactly when the skipped column already holds a mirror loser on the lower line. This restricts the gap sequence between holes exclusively to the alphabet $\{3, 5\}$.

**3. Collisions (The Source of Chaos):** On sheets $x \ge 1$, the expected landing cell is occasionally pre-occupied by an instant-winner ($W$) inherited from a lower sheet. When this collision occurs, the P-position is kicked up by exactly 1. Collisions bracket the core branch — dense on the approach, absent along the branch itself, resuming past $y^{*}$ — and then die out along the line (Section 2).

These defects permanently shift the sequence rank $n$. They rule out a closed form for the sheet as a whole, but not everywhere: on the core branch, where no collisions occur at all, the P-positions have the exact closed form $z = 3(x+y)-1$.

\
\
So the black lines make up loser sheet 104's own two main loser lines, the ones of slope $m_u$ and $m_\ell$ sitting inside the blue fans. Each blue fan is what you get when you stack every sheet's line: as $x$ grows, sheet $x$'s line shifts outward, and the lines sweeps out a wedge-shaped plane. There appear to be several fans because of the three-pile symmetry: there's a wedge for "z is the big pile" (pointing up), one for "y is the big pile" (pointing right), and one for "x is the big pile".

The small black clusters near the middle — those are the three core regions of sheet 104.

Tool 1: equation 4:

$$\Delta z = 2\Delta y + (\text{\# of losers passed})$$

The next loser must clear the previous loser's slope-2 cone, plus one cell for every loser row it passes. Averaged over a long stretch where a fraction $\lambda_u$ of columns carry a dot, this gave you $m_u = 2 + \lambda_u$.

Tool 2: the symmetry:

The three piles are interchangeable, so instead of talking about $(x,y,z)$, sort every loser: $p \le q \le r$. Prove one statement about sorted triples, and you get all its appearances on all sheets for free, by permuting the coordinates back.

Here is the punchline of the whole section, up front: the three regions are not three separate phenomena. They are two families of sorted triples, and each region is just one family being cut by your sheet at a different angle.

Region 1 — the slope-3 branch: your equation with $\lambda = 1$
Take your stepping equation and ask: what happens near the origin, before the sheet settles down?

Out in the far field, some columns get skipped — a column is unavailable when a mirror dot (the reflection of an upper-line dot across $y=z$) already occupies it, and skipping is what dilutes the density to $\lambda_u = \sqrt3 - 1$ and gives slope $2+\lambda_u = m$.

But near the origin, no mirrors have arrived yet. A dot at height $h$ reflects into column $h$ — and the core's own dots sit at height $\approx 3y$, so their reflections land way out at column $\approx 3y$, far to the right of where we are. With nothing occupying columns, every column carries a dot: the local density is

$$\lambda_{\text{local}} = 1.$$

Now just plug into your own equation:

$$\Delta z = 2,\Delta y + \lambda_{\text{local}},\Delta y = 2(1) + 1 = 3 \quad \text{per column.}$$

Slope exactly 3 between column $\sim x$ and column $\sim(1+\sqrt3)x$, every dot of sheet $x$ sits on

$$z = 3(x+y) - 1.$$

The asymptotic line and the core branch are the same equation, $m = 2 + \lambda$, evaluated in two regimes. Far field: $\lambda = \sqrt3-1$, slope $2.732$. Core: $\lambda = 1$, slope $3$. The density $\lambda$ falls from $1$ to $\sqrt3 - 1$ as mirror dots start arriving, and the branch ends at column $\approx (1+\sqrt3)x$, which is exactly where the first reflected dots land, because the lowest dots of the sheet sit at height $\approx (1+\sqrt3)x$ and a dot at height $h$ reflects into column $h$.

Two honest gaps: the $3x$ part of the intercept comes from the same stepping argument run in $x$ (by symmetry $x$ and $y$ are interchangeable small piles, so stepping $x \to x+1$ also forces $\Delta z = 3$), but the exact constant $-1$ is read off the data, not yet derived. And "which mirror dot kills the branch first" is a mechanism, not yet a proof.

Region 2 — the origin blob: the same law, cut from the other side
Now use Tool 2. The branch law, stated symmetrically about sorted triples $(p,q,r)$:

$$r = 3(p+q) - 1 \qquad (r = \text{largest pile}).$$

Your sheet fixes $x$ and plots $(y,z)$. There are two ways your sheet can meet this one surface:

$x$ is a small pile ($x = p$ or $q$): solve for $z$: $\;z = 3(x+y)-1$. A line of slope 3 → the branch.
$x$ is the large pile ($x = r$): then $x = 3(y+z)-1$, i.e.
$$y + z = \frac{x+1}{3}.$$

A constant sum is an anti-diagonal segment (slope $-1$) hugging the origin → the origin blob. Same surface, different cut.

And this immediately explains the blob's strange flickering across sheets, which no amount of staring at one sheet would: $y+z$ has to be a whole number, so the blob can only exist when $3 \mid x+1$, i.e. $x \equiv 2 \pmod 3$. Check: sheet 50 has eight dots on $y+z = 17$, and $3\cdot17 - 1 = 50$. Sheets 120 and 180 ($\not\equiv 2$) have none. (Your screenshot's sheet 101: $101 \equiv 2 \pmod 3$, so its origin blob is present.)

The wall fan ($y < x$) is the third cut of the same symmetry: sheet $x$'s dot in column $y$ is sheet $y$'s dot in column $x$, so the fan is just lower sheets' tails sliced sideways. Nothing new there either.

Region 3 — the mirror pair: the symmetry's fixed line
The last two blobs, out at $(\approx x, \approx 3.2x)$ and $(\approx 3.2x, \approx x)$. First observation: they are exact reflections of each other across $y = z$. So by the mirror symmetry they are one family seen twice: the losers with two equal piles, ${n, n, c}$. On sheet $n$ the big pile shows up once as $z$ (upper blob) and once as $y$ (lower blob).

Second observation, and this is the key difference from the other two regions: this family has no integer formula, and can't have one. The branch's residual $z - 3(x+y)$ is a fixed integer ($-1$); this family's spread grows in proportion to $x$. It is scale-invariant. So the right kind of answer is the same kind as your $m$ and $\lambda$ — a limiting ratio:

$$\frac{c}{n} \;\longrightarrow\; \frac{3}{2}+\sqrt3 \;=\; m + \tfrac12 \;\approx\; 3.2320.$$

The measured ceiling climbs $3.2227 \to 3.2291 \to 3.2302 \to 3.2308 \to 3.2311$ as $x$ runs $150 \to 800$, always from below, gap halving each window — identical on two independent grid sizes.

Why this family exists as its own region: $(n,n,c)$ with $c \approx 3.2n$ sits exactly where the two-pile move changes character. On the equal pair the ratio-bounded move is fully available (ratio $1$); on either $(n,c)$ pair, chasing the family would need removals in ratio $\approx 1{:}3.2$ — outside the allowed $[\frac12, 2]$ cone, just like the branch's slope $3 > 2$ puts consecutive branch dots outside each other's cones. That the boundary lands at exactly $m + \tfrac12$ is still a conjecture (strongly supported numerically) — say that honestly when presenting.

What you see on sheet $x$:\
Branch: slope-3 line, columns $x \to (1{+}\sqrt3)x$\
Sorted triple statement: $r = 3(p+q)-1$, sheet coord = small pile\
Your $\Delta z = 2\Delta y + \text{\# losers}$ with local density $\lambda = 1$: slope $= 2+1 = 3$

Origin blob: anti-diagonal $y{+}z = \frac{x+1}{3}$, only $x \equiv 2 \bmod 3$\
Same law, sheet coord = largest pile\
Same surface, cut from the other side; integrality of $\frac{x+1}{3}$ gives the mod-3 flicker

Mirror pair at $(x, 3.2x)$ & $(3.2x, x)$\
Two equal piles ${n,n,c}$, $;c/n \to m+\tfrac12$\
Fixed line of the $y\leftrightarrow z$ mirror; scale-invariant, so a ratio law, not an integer law

sort the piles and work in one wedge, run the supermex stepping equation in that wedge (the same one that gave $m = 2+\lambda$); notice it has a second regime, $\lambda = 1$, which produces the exact slope-3 law; permute coordinates to recover the origin blob and wall fan for free; and the leftover pair of blobs is the mirror's own fixed-line family, governed by a ratio instead of a formula.

### The derivation of $z = 3(x+y)-1$

Write $\varphi(x,y,z) = z - 3(x+y)$, so the law says: on the branch, $\varphi = -1$. The derivation has four steps: an invariant, two ratchets, and a seed.

Step 1 — The invariant: no two dots with the same $\varphi$ can ever attack each other.
Go through all six move types and ask what each one does to $\varphi$. The whole game is in this little table ($s, t \ge 1$, and pair moves obey the cone $\tfrac12 \le s/t \le 2$):

remove $t$ from $x$ alone (or $y$ alone): $+3t$ — increases

remove $s$ from $x$, $t$ from $y$: $+3(s+t)$ — increases

remove $s$ from $y$, $t$ from $z$: $3s - t$, and $t \le 2s$ forces $3s - t \ge s > 0$ — increases

remove $s$ from $x$, $t$ from $z$: same: $3s - t \ge s > 0$ — increases

remove $t$ from $z$ alone: $-t$ — decreases, but $x, y$ stay fixed

So every move strictly increases $\varphi$, except the $z$-alone move, which keeps $(x,y)$ fixed. Now take two positions with the same $\varphi$: no increasing move can connect them, and the $z$-alone move can't either (same $(x,y)$ plus same $\varphi$ would mean the same $z$ — the same position).

For any constant $c$, the surface $z = 3(x+y)+c$ is an antichain: no legal move connects any two of its points

This single computation explains, at once: why the branch can be exact with no collisions (its dots can't threaten each other — bounded.md's "no collisions on the branch" surprise is now a theorem, not an observation), why it's symmetric in $x$ and $y$, and why the coefficient is $3$ — look at the third row: $3$ is exactly the smallest integer slope that beats the cone's slope $2$. A slope-2 line can be chased by the pair move; a slope-3 line is forever out of reach. This is the mechanism behind your $\Delta z = 2\Delta y + 1$.

Step 2 — The ratchet in $y$: your $m = 2+\lambda$ equation with $\lambda = 1$
The antichain says dots may sit on the line; the mex says they must. Suppose column $y-1$ has its loser at height $z_0 - 3$ (on the line). What does that dot attack in column $y$?

$y$-alone move (from height $z_0-3$, same height): attacks $z_0 - 3$.
Cone move with $s=1$: $t \in {1, 2}$, attacks $z_0-2$ and $z_0-1$.
Height $z_0$ would need $t = 3 > 2s$: out of the cone. Unattacked.
Everything lower in the column is attacked by earlier dots and lower sheets (that's the "no mirrors have arrived yet" density-1 condition — the one genuinely core-only input). So the scan-up lands on the first free cell: exactly $z_0$. Three cells blocked, the fourth free — the loser climbs by exactly $3$ per column. This is literally your Part 3 equation $\Delta z = 2\Delta y + (#\text{losers passed})$ with every column carrying a dot.

Step 3 — The ratchet in $x$: the same argument, rotated
Here's the payoff of the professor's symmetry hint. Since $x$ and $y$ are both small piles here, the argument of Step 2 must also run in the $x$-direction — and it does, using the inter-level moves this time. Suppose sheet $x-1$ has its dot in column $y$ at height $z_0 - 3$. From a cell $(x, y, w)$ in the same column of the sheet above:

$x$-alone (down 1 level): attacks $w = z_0 - 3$.
$x&z$ move with $s = 1$: $t \in {1,2}$, attacks $w = z_0-2$ and $z_0-1$.
$w = z_0$ would need $t = 3 > 2s$: out of the cone. Unattacked.
Identical structure: each sheet's branch is the previous sheet's branch pushed up by exactly $3$, column by column. Step 2 gives the $3y$; Step 3 gives the $3x$; together, $z = 3(x+y) + c$ with the same constant $c$ propagating from sheet to sheet. Note nothing so far chose the value of $c$ — the antichain and both ratchets work for any $c$. The law is a self-propagating structure; the constant is a boundary condition.

Step 4 — The seed: where $-1$ comes from
So the constant must be inherited from the bottom of the induction, and the cache shows exactly that. On sheet $x=0$ — the pure two-pile game — the losers happen to include $(4,11)$ and $(5,14)$, and

$$11 = 3\cdot 4 - 1, \qquad 14 = 3 \cdot 5 - 1.$$

Those two dots sit on the $\varphi = -1$ surface by accident of the two-pile loser sequence. Then the Step-3 ratchet does the rest, visibly: sheet 1 carries $(4,14), (5,17)$ — the same columns, three higher — sheet 2 carries $(4,17),(5,20)$, and each sheet the run gets longer as the Step-2 ratchet extends it sideways. The propagation is patchy at first (holes at small $x$), but by $x \approx 15$–$17$ the window is clean, and from there $c = -1$ is locked in forever — I confirmed the modal constant is $-1$ on every sheet from $x=15$ up, hitting all dots in the window from $x=17$ on with only stray misses.

Honest status for the professor: Steps 1–3 are rigorous arguments (Step 2 needs the density-1/"no mirrors yet" condition stated as a hypothesis; that's the same caveat as your $m = 2+\lambda$). Step 4 is a finite, checkable base case — which is how many combinatorial-game proofs end. The one remaining "why" is why the two-pile game seeds $-1$ rather than some other constant; that's now a question about two dots, not about an infinite pattern.

Two corrections to bounded.md this derivation exposed
While verifying, the data forced two fixes to the current write-up:

The branch window is bigger and symmetric. Dots satisfying the law run over $y/x \in [1/m,, m]$ — starting at column $\approx 0.366x$, not at column $x$. The part below column $x$ is what bounded.md files separately as the "wall fan"; it is the same law (of course: the sorted statement $r = 3(p+q)-1$ doesn't care which small pile is which, so the window had to be symmetric under $y \leftrightarrow x^2/y$... i.e. $[x/m, mx]$).
The branch's missing columns are the blob's shadow. The law fails in exactly the mirror-blob columns ($y \approx x$): there a blob dot sits below the branch line in the same column, the $z$-alone move from the branch cell down to it would reach a loser, so the branch cell is a winner and the column's true loser is the blob dot. Verified on sheets 100, 200, 300 — hole columns = blob columns, with the immediate neighbors depressed by 1–3 cells. So the blob and the branch, which looked independent, interlock: the blob punches the only holes the branch has.
If you want, I can write this into bounded.md (replacing the current "why slope 3" paragraph and correcting the window/wall-fan and holes statements), or as a standalone DOCUMENTATION part in the same style as Part 3 for your presentation.