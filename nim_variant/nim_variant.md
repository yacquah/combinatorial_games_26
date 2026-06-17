# Nim variant 
We have 3 piles of chips. A move consists of removing any number of chips from one pile, or the same number of chips from all piles.

Coordinates as number of chips in each pile $(x,y,z)$

### Possible moves from $(x,y,z):$  
Remove some chips from one pile:  
$(x-t,y,z)$ where $t\leq x$  
$(x,y-t,z)$ where $t\leq y$  
$(x,y,z-t)$ where $t\leq z$  
Remove the same number of chips from all piles:  
$(x-t,y-t,z-t)$ where $t\leq \min(x,y,z)$

### Finding recursive operator $\mathcal{R}$
To reach a lower level losing position, we can go from $(x,y,z)$ to $(x-t,y,z)$ or $(x-t,y-t,z-t)$.

From the first move, $W_x(y,z) = L_{x-t}(y,z)$ so $W_x = \sum\limits_{t=1}^{x}{L_{x-t}}$

From the second move, $W_x(y,z)$ is filled in if $L_{x-t}(y-t,z-t)$ is filled in

We can define a shifting operator that moves a sheet diagonally up and right by 1 space:
$\mathcal{S}A(y,z) = A(y-1,z-1)$

So $W_x = \mathcal{S}^tL_{x-t}$ for moving down $t$ sheets.
$W_x=\sum\limits_{t=1}^{x}{\mathcal{S}^tL_{x-t}}$

Summing these up we get:
 $W_x = \sum\limits_{t=1}^{x}{L_{x-t}} + \sum\limits_{t=1}^{x}{\mathcal{S}^tL_{x-t}}$
 
$W_x = \sum\limits_{t=1}^{x}{L_{x-t} + \mathcal{S}^tL_{x-t}}$

$\boxed{W_x = \sum\limits_{t=1}^{x}{(I + \mathcal{S}^t)L_{x-t}}}$

$W_{x+1} = \sum\limits_{t=1}^{x+1}{(I + \mathcal{S}^t)L_{x+1-t}}$

$W_{x+1} = (I+S)L_{x+1-1}+\sum\limits_{t=2}^{x+1}{(I + \mathcal{S}^t)L_{x+1-t}}$

$W_{x+1} = (I+S)L_x+\sum\limits_{t=1}^{x}{(I + \mathcal{S}^{t+1})L_{x+1-(t+1)}}$

$W_{x+1} = (I+S)L_x+\sum\limits_{t=1}^{x}{(I + \mathcal{S}^{t+1})L_{x-t}}$

$W_{x+1} = (I+S)L_x+\sum\limits_{t=1}^{x}{L_{x-t}} + \sum\limits_{t=1}^{x}{\mathcal{S}^{t+1}L_{x-t}}$

$W_{x+1} = (I+S)L_x+\sum\limits_{t=1}^{x}{L_{x-t}} + \mathcal{S}\sum\limits_{t=1}^{x}{\mathcal{S}^{t}L_{x-t}}$

If the first term of $W_x$ is $A_x=\sum\limits_{t=1}^{x}{L_{x-t}}$ and second term is $B_x=\sum\limits_{t=1}^{x}{\mathcal{S}^tL_{x-t}}$
then:

$A_{x+1}=A_x+L_x$ and $B_{x+1}=\mathcal{S}(B_x+L_x)$ so $W_{x+1} = A_x+L_x+S(B_x+L_x)$

We will individually calculate the next $A_{x+1}$ and $B_{x+1}$, and add (bitwise OR operation) to get $W_{x+1}$.

### Supermex $\mathcal{M}$
Identical to normal Nim supermex, blocking off the rest of the row where the first empty space is found.

### Grid size and compute size
We will need to add a buffer of x-levels because the shifting will require an array of larger size. 