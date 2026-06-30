# Diet Chomp
Normal 3-row chomp but with the restriction of removing no more than 4 pieces in a move.

Coordinates for the position are $(x,y,z)$ where $x$ is the number of three-tall columns, $y$ is the number of two-tall columns, and $z$ is the number of one-tall columns.

### Possible Moves from $(x,y,z)$
- **(M1):** &ensp; $(x,y-t,z+t)$
removes $t$ pieces, 

    $0<t\leq y$ &ensp; and &ensp; $t\leq 4$
    
- **(M2):** &ensp; $(x,y-t,0)$
removes $2t+z$ pieces, 

    $0<t\leq y$ &ensp; and &ensp; $2t+z\leq 4$

- **(M3):** &ensp; $(x,y,z-t)$
removes $t$ pieces,

    $0<t\leq z$ &ensp; and &ensp; $t\leq 4$

- **(M4):** &ensp; $(x-t,y+t,z)$
removes $t$ pieces, 

    $0<t\leq x$ &ensp; and &ensp; $t\leq 4$

- **(M5):** &ensp; $(x-t,0,z+y+t)$
removes $2t+y$ pieces,

    $0<t\leq x$ &ensp; and &ensp; $2t+y\leq 4$

- **(M6):** &ensp; $(x-t,0,0)$
removes $3t+2y+z$ pieces,

    $0<t\leq x$ &ensp; and &ensp; $3t+2y+z\leq 4$

## Sheets and indexing

We fix $x$ (the **sheet level**) and render the remaining $(y,z)$ plane as a 2D
boolean grid, stored indexed $[z,y]$ ($z$ is the row, $y$ the column). $W_x$ is the
**instant-winner** sheet (positions with a winning move to a lower level) and $L_x$
is the **loser** sheet (P-positions, no winning move).

The moves split into two groups:

- **x-fixed** $(M1,M2,M3)$ stay on the same sheet — resolved by `supermex_diet`.
- **x-reducing** $(M4,M5,M6)$ drop the level by $t$ — handled by the recursion
  operator `generate_Wx_diet`.

Because every move removes at most 4 pieces, an x-reducing move lowers the level by
at most $t=4$ ($M4$; note $M5$ needs $2t\leq 4$ so $t\leq 2$, and $M6$ needs
$3t\leq 4$ so $t\leq 1$). So $W_x$ depends only on the previous **four** loser
sheets $L_{x-1},\dots,L_{x-4}$, which `main` keeps in a sliding history buffer. A
target can also sit up to $4$ columns further out per level, so the grid is padded
by $4\cdot(\text{desired level})$.

## Recursion operator ($W_x$)

$W_x$ marks every position with a winning **x-reducing** move. For each prior loser
sheet $L_{x-t}$ ($t=1..4$) we add the *pre-images* of $M4,M5,M6$ — every level-$x$
position that lands on a loser $(y,z)$ of $L_{x-t}$:

- $M4^{-1}$: &ensp; $(x,\,y-t,\,z) \to (x-t,\,y,\,z)$ &ensp; — mark $W_x[z,\,y-t]$ when $y-t\geq 0$.
- $M5^{-1}$: &ensp; the target has $y=0$; for a loser at $(0,z)$ the sources are
  $(x,\,y_{\text{win}},\,z-y_{\text{win}}-t)$ with $0\leq y_{\text{win}}\leq 4-2t$ (the $2t+y\leq 4$ cap).
- $M6^{-1}$: &ensp; the target is $(0,0)$; the sources are all $(x,\,y_{\text{win}},\,z_{\text{win}})$ with $3t+2y_{\text{win}}+z_{\text{win}}\leq 4$.

The x-fixed moves are **not** applied here; `supermex_diet` resolves them when it
recovers $L_x$ from this $W_x$.

## supermex ($L_x$)

`supermex_diet` recovers $L_x$ from $W_x$ by resolving the **x-fixed** moves. A
position not in $W_x$ is still a winner if some $M1/M2/M3$ move reaches a loser on
the same sheet; only positions with no such move are losers.

Sweep $(y,z)$ in column-major order ($y$ outer, $z$ inner). The first cell that is
neither an instant winner nor already *blocked* has no move to any loser, so it is a
P-position: mark it in $L_x$, then *block* every position that can reach it via
$M1/M2/M3$ (those now have a winning move and cannot be losers):

- $M1^{-1}$: &ensp; block $(y+t,\,z-t)$ for $t=1..4$.
- $M3^{-1}$: &ensp; block $(y,\,z+t)$ for $t=1..4$.
- $M2^{-1}$: &ensp; only when the loser has $z=0$; block $(y+t,\,z_{\text{win}})$ for $t=1..4$ and $0\leq z_{\text{win}}\leq 4-2t$ (the $2t+z\leq 4$ cap).

This is the diet-Chomp analogue of the generic `supermex`: the blocking geometry
encodes exactly the x-fixed moves $M1$, $M2$, $M3$.

    