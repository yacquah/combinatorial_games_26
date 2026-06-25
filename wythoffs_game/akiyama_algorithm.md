# Finding recursive and supermex for Akiyama

### Big picture
If we know every loser on the lower sheets, we can build $W_x$. Then $L_x$ is from `supermex` on $W_x$.

**Shadows**: a known loser casts a shadow onto the higher
sheets, marking every position that can jump straight onto it in one move. $W_x$
is just all the shadows that reach sheet `x`. Each move type casts a different
shadow shape, and we keep a running tally of each shape in an accumulator/auxiliary sheet.

Two kinds of moves: those that **keep `x` fixed** stay inside a sheet (handled by
`supermex`), and those that **lower `x`** connect sheets (handled by the
accumulators).

### Possible moves
Remove any number of chips from 1 pile only:\
$(x,y,z) \rightarrow (x-t,y,z)$\
$(x,y,z) \rightarrow (x,y-t,z)$\
$(x,y,z) \rightarrow (x,y,z-t)$\
Remove any number of chips from two piles only (same or different number of chips):\
$(x,y,z) \rightarrow (x-s,y-t,z)$\
$(x,y,z) \rightarrow (x-s,y,z-t)$\
$(x,y,z) \rightarrow (x,y-s,z-t)$\
Remove the same number of chips from two piles, and remove any number of chips from the other pile:\
$(x,y,z) \rightarrow (x-s,y-s,z-t)$\
$(x,y,z) \rightarrow (x-s,y-t,z-s)$\
$(x,y,z) \rightarrow (x-t,y-s,z-s)$

### Some operators we need
- Shift matrix 1 step along +y (right): $\mathcal{S_y}A(y,z)=A(y-1,z)$
- Shift matrix 1 step along +z (up): $\mathcal{S_z}A(y,z)=A(y,z-1)$
- Shift matrix 1 step diagonally along +y and +z (up and right): $\mathcal{S_yz}A(y,z)=A(y-1,z-1)$
- Cumulative OR, along y, so $(y,z)$ becomes True if $(y,z)$ is True, or if $(y-1,z)$ is True, or if $(y-2,z)$ is True, and so on until $y=0$.
  - $\mathcal{C_y}A(y,z)=A(y,z)+A(y-1,z)+\dots+A(0,z)$
- Cumulative OR, along z, so $(y,z)$ becomes True if $(y,z)$ is True, or if $(y,z-1)$ is True, or if $(y,z-2)$ is True, and so on until $z=0$.
  - $\mathcal{C_z}A(y,z)=A(y,z)+A(y,z-1)+\dots+A(y,0)$
- Cumulative OR, along the diagonal, so $(y,z)$ becomes True if $(y,z)$ is True, or if $(y-1,z-1)$ is True, or if $(y-2,z-2)$ is True, and so on until $y=0$ or $z=0$.
  - $\mathcal{C_yz}A(y,z)=A(y,z)+A(y-1,z-1)+\dots$

**Strict vs inclusive cumulative.** The cumulative ORs above are *inclusive* because
they keep the cell's own value. Sometimes we want a *strict* version, "look only
to the left, not counting myself," which is just shift-then-cumulate
$(\mathcal{C_y}\mathcal{S_y}$):

```
input            :  F F T F F F
C_y  (inclusive) :  F F T T T T
C_y S_y (strict) :  F F F T T T   <- own cell dropped, spread starts one step over
```

We use **strict** when the move is forced to remove a **positive**
amount from that pile (you can't reach a loser you're already sitting on); use
**inclusive** when that pile may be left untouched (remove 0).

### Recursive operator
We need to look at every move that will change x-level, and read each move
**backwards**: given a known loser on a lower sheet, which current cells can
reach it? This set of current cells that can reach it is the loser's shadow.

The simplest accumulator is $V^1$ = `ever_lost` = OR of all lower-sheet losers, which will be a 2D array tracking every loser at $(y,z)$ that has happened on a lower level sheet.

**Remove any number of chips from 1 pile only:**\
<u>M1:</u> $(x,y,z) \rightarrow (x-t,y,z)$

$(x,y,z)$ is a winner iff $(y,z)$ was a loser on any lower sheet. So, a loser will mark any instant winners at a higher x-level (extend some "shadow" through sheets upwards).

Matrix $V^1_{x+1}=V^1_x+L_x$. Contribution to $W_x$ is $V^1_x$ itself.

**Remove any number of chips from two piles only (same or different number of chips):**\
<u>M2a:</u> $(x,y,z) \rightarrow (x-s,y-t,z)$

$(x,y,z)$ is a winner iff some lower level has a loser at $(y',z)$ with $y'<y$, meaning anywhere to the left. The shadow is a horizontal ray pointing right.

Contribution to $W_x$ is $V^2_x=\mathcal{C_y}\mathcal{S_y}V^1_x$ (strict cumulative in y — strict because we have to remove a positive amount of chips from $y$).

<u>M2b:</u> $(x,y,z) \rightarrow (x-s,y,z-t)$

Mirror of M2a with $y$ and $z$ swapped: a winner iff a lower loser sits at $(y,z')$ with $z'<z$, meaning anywhere below in the same column. The shadow is a vertical ray pointing up.

Contribution to $W_x$ is $V^3_x=\mathcal{C_z}\mathcal{S_z}V^1$ (strict cumulative in z).

**Remove the same number of chips from two piles, and remove any number of chips from the other pile:**\
<u>M3a:</u> $(x,y,z) \rightarrow (x-s,y-s,z-t)$ &nbsp; ($s\ge 1$, $t\ge 0$)

`x` and `y` both decrease by the same $s$, and `z` may decrease by any amount including 0, so it is inclusive. A winner iff some lower
loser sits at $(x-s,\,y-s,\,z')$ for some $s\ge 1$, $z'\le z$.

Accumulator $A$ (`Acc3a` in code), updated after level `x`:
$$A_{x+1}=\mathcal{S_y}\big(A_x+\mathcal{C_z}L_x\big)$$
Contribution to $W_x$ is $A_x$ itself.

<u>M3b:</u> $(x,y,z) \rightarrow (x-s,y-t,z-s)$ &nbsp; ($s\ge 1$, $t\ge 0$)

Same as M3a with `y` and `z` swapped:

Accumulator $B$ (`Acc3b`):
$$B_{x+1}=\mathcal{S_z}\big(B_x+\mathcal{C_y}L_x\big)$$
Contribution to $W_x$ is $B_x$ itself.

<u>M3c:</u> $(x,y,z) \rightarrow (x-t,y-s,z-s)$ &nbsp; ($s\ge 1$, $t\ge 1$)

Now the tied pair is `y` and `z`, so the diagonal lives **inside the sheet** (the
`y=z` direction). The free pile is `x` itself, which only has to drop to *some*
lower sheet — it doesn't matter which. So a winner iff **any** lower loser sits
diagonally down-left at $(y-s,\,z-s)$ for some $s\ge 1$.

Accumulator $D$ (`Dcum`): collect every lower loser and smear it up-right along
the diagonal (no per-level slide, since `x` is free):
$$D_{x+1}=D_x+\mathcal{C_{yz}}L_x$$
Contribution to $W_x$ is $\mathcal{S_{yz}}D$. It is one step diagonally to force $s\ge 1$; the $s=0$ case (only `x` changed) is just M1, already
covered by $V^1_x$.

### Adding it together
When building sheet `x`, we just "add" (OR) all six contributions:
$$W_x=V^1_x+\mathcal{C_y}\mathcal{S_y}V^1_x+\mathcal{C_z}\mathcal{S_z}V^1_x+A+B+\mathcal{S_{yz}}D$$
Then find losers $L_x$ with `supermex` ($\mathcal{M}$), and use that to calculate the next x-level for each accumulator sheet.
$$V^1_{x+1}=V^1_x+L_x,\quad A_{x+1}=\mathcal{S_y}(A_x+\mathcal{C_z}L_x),\quad B_{x+1}=\mathcal{S_z}(B_x+\mathcal{C_y}L_x),\quad D_{x+1}=D_x+\mathcal{C_{yz}}L_x$$
We only need $V^1, A, B, D$ to be stored and the M2a/M2b terms are recalculated from $V^1$ each step.

### Supermex $\mathcal{M}$ (finding $L_x$ from $W_x$)
Moves that keep `x` fixed: remove from `y` only, from `z` only, or any amount from both,
or the same amount from both:\
$(x,y,z) \rightarrow (x,y-t,z)$\
$(x,y,z) \rightarrow (x,y,z-t)$\
$(x,y,z) \rightarrow (x,y-s,z-t)$\
So using these moves we can reach a loser from a winner on the same sheet. 
