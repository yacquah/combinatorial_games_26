# Game Ideas
### Requirements
- Impartial
- Position representable by 3 nonnegative integers $(x,y,z)$
- Every move strictly decreases the position in lexicographic (dictionary) order.

### [2 Heap Fibonacci Nim](https://en.wikipedia.org/wiki/Fibonacci_nim)
Remove chips from a pile. The first move can remove up all chips except one. Every subsequent move can remove from 1 to double the number of chips the previous player took.

$(x,y,z)$ could be chips in the first pile, chips in the second pile, and the chips taken away in the previous move.

$(x,y,z) \rightarrow (x−t, y, t)$ &ensp; for &ensp;  $1\le t \le 2z$ &ensp; and &ensp; $x-t \ge 0$\
$(x,y,z) \rightarrow (x, y-t, t)$ &ensp; for &ensp; $1\le t \le 2z$ &ensp; and &ensp; $y-t \ge 0$

### 3 Heap Subtract a Square
Remove a square number of chips from a pile. If the 3 piles are independent, we can just use Sprague-Grundy theorem to find SG value. 

If we want to make it more interesting, we can make it so that it's like Wythoff's game, where we can remove the same number of chips from two piles (or 3?). Or the total number of chips removed could sum to a square.

$(x,y,z) \rightarrow (x-t, y, z)$ \
$(x,y,z) \rightarrow (x, y-t, z)$ \
$(x,y,z) \rightarrow (x, y, z-t)$ \
Where $t$ is a square.

Or if we want to add: \
$(x,y,z) \rightarrow (x-t, y-t, z)$ \
$(x,y,z) \rightarrow (x-t, y, z-t)$ \
$(x,y,z) \rightarrow (x, y-t, z-t)$ \
Where $t$ is a square.

Or if we want to add: \
$(x,y,z) \rightarrow (x-a, y-b, z)$ \
$(x,y,z) \rightarrow (x-a, y, z-b)$ \
$(x,y,z) \rightarrow (x, y-a, z-b)$ \
$(x,y,z) \rightarrow (x-a, y-b, z-c)$ \
Where $a+b$ is a square (or $a+b+c$ is a square)


### 3 Heap Nim with Merging Piles
Nim but you can merge piles together, leaving an empty pile behind. 

### Chomp with Protected Diagonal
Start with a three-row position represented by:

$(x,y,z)$

where $x \ge y \ge z$ if using row lengths, or use the column-height encoding from the paper.
A move is like Chomp: choose a square and remove all squares weakly below/right of it.

*Restriction:*
A player may not choose a square on the main diagonal, unless it is the only legal move remaining.


### 3 Heap Subtract a Prime
Similar to subtract a square, but you have to subtract prime numbers (so 0 and 1 chips are terminal positions). 

Also can make it where we can remove the same chips from multiple piles or other variants.

$(x,y,z) \rightarrow (x-t, y, z)$ \
$(x,y,z) \rightarrow (x, y-t, z)$ \
$(x,y,z) \rightarrow (x, y, z-t)$ \
Where $t$ is a prime $(t \in \mathbb{P})$.

Or if we want to add: \
$(x,y,z) \rightarrow (x-t, y-t, z)$ \
$(x,y,z) \rightarrow (x-t, y, z-t)$ \
$(x,y,z) \rightarrow (x, y-t, z-t)$ \
Where $t$ is a prime $(t \in \mathbb{P})$.

Or if we want to add: \
$(x,y,z) \rightarrow (x-a, y-b, z)$ \
$(x,y,z) \rightarrow (x-a, y, z-b)$ \
$(x,y,z) \rightarrow (x, y-a, z-b)$ \
$(x,y,z) \rightarrow (x-a, y-b, z-c)$ \
Where $a+b$ is a prime (or $a+b+c$ is a prime)

### 3 Heap Wythoff's Game but "Unbalanced"
Remove *k* chips from one pile and *2k* from another pile. 

$(x,y,z) \rightarrow (x-t, y-2t, z)$ \
$(x,y,z) \rightarrow (x-2t, y-t, z)$ \
$(x,y,z) \rightarrow (x-t, y, z-2t)$ \
$(x,y,z) \rightarrow (x-2t, y, z-t)$ \
$(x,y,z) \rightarrow (x, y-t, z-2t)$ \
$(x,y,z) \rightarrow (x, y-2t, z-t)$

### 3 Heap Impartial Euclid's Game
Three piles of size $x$, $y$, $z$, and you can remove some multiple of a pile's chips from one pile. When there is 1 pile remaining with chips, the game is over. 

Basically a move can remove $ky$ or $kz$ from $x$, $kx$ or $kz$ from $y$, or $kx$ or $ky$ from $z$, as long as the pile size is not negative. 

Or we can do a variation where we subtract $kx$ or $ky$ or $kz$ from the other two piles as another move. 

$(x,y,z) \rightarrow (x-ky, y, z)$ \
$(x,y,z) \rightarrow (x-kz, y, z)$ \
$(x,y,z) \rightarrow (x, y-kx, z)$ \
$(x,y,z) \rightarrow (x, y-kz, z)$ \
$(x,y,z) \rightarrow (x, y, z-kx)$ \
$(x,y,z) \rightarrow (x, y, z-ky)$

Or if we want to add:\
$(x,y,z) \rightarrow (x-kz, y-kz, z)$ \
$(x,y,z) \rightarrow (x-ky, y, z-ky)$ \
$(x,y,z) \rightarrow (x, y-kx, z-kx)$ 

### 3 Heap GCD Game
Three positive integers $x,y,z$ representing piles of chips. Pick out any two piles, find their greatest common divisor, and subtract any positive multiple of that from the other pile. 

$(x,y,z) \rightarrow (x-k\gcd(y,z), y, z)$ \
$(x,y,z) \rightarrow (x, y-k\gcd(x,z), z)$ \
$(x,y,z) \rightarrow (x, y, z-k\gcd(x,y))$

### 3 Heap LCM-bounded subtraction
Subtract 1 to least common multiple of two piles from the other pile. 

$(x,y,z) \rightarrow (x-t, y, z)$ \
where $1\leq t\leq \operatorname{lcm}(y,z)$\
$(x,y,z) \rightarrow (x, y-t, z)$ \
where $1\leq t\leq \operatorname{lcm}(x,z)$\
$(x,y,z) \rightarrow (x, y, z-t)$ \
where $1\leq t\leq \operatorname{lcm}(x,y)$

### Akiyama 3D Wythoff Positive Nim
3 piles of chips $(x,y,z)$ 

We can take away $a,b,c$ chips: $(x,y,z) \rightarrow (x-a,y-b,z-c)$

$\set{(x,y,z)\in \mathbb{N}_0^3 | xyz(x-y)(y-z)(z-x)=0, x+y+z > 0}$

Basically $x,y,z \geq 0$ and the possible moves are:

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

### 3 Heap Wythoff's Game but "3 times Unbalanced"
Remove *k* chips from one pile and *3k* from another pile. On top of normal Nim moves.

$(x,y,z) \rightarrow (x-t, y-3t, z)$ \
$(x,y,z) \rightarrow (x-3t, y-t, z)$ \
$(x,y,z) \rightarrow (x-t, y, z-3t)$ \
$(x,y,z) \rightarrow (x-3t, y, z-t)$ \
$(x,y,z) \rightarrow (x, y-t, z-3t)$ \
$(x,y,z) \rightarrow (x, y-3t, z-t)$

### 3 Heap Wythoff's Game Combined
Very similar to Ryuo Nim for, which is solved and is Nim but you can also subtract 1 chip from two piles and 1 chip from three piles. 
But here, you can subtract the same number of chips from two piles or same number of chips from three piles (instead of just one chip)

Remove any number of chips from 1 pile only:\
$(x,y,z) \rightarrow (x-t,y,z)$\
$(x,y,z) \rightarrow (x,y-t,z)$\
$(x,y,z) \rightarrow (x,y,z-t)$\
Remove the same number of chips from two piles:\
$(x,y,z) \rightarrow (x-t,y-t,z)$\
$(x,y,z) \rightarrow (x-t,y,z-t)$\
$(x,y,z) \rightarrow (x,y-t,z-t)$\
Remove the same number of chips from all three piles:\
$(x,y,z) \rightarrow (x-t,y-t,z-t)$

### 3 Heap Restricted Wythoff's Game
On top of Nim rules (remove any number of chips from 1 pile), you can also remove the same number of chips from two piles, as long as the number of chips removed is less than or equal to the size of the third untouched pile.

Remove any number of chips from 1 pile only:\
$(x,y,z) \rightarrow (x-t,y,z)$\
$(x,y,z) \rightarrow (x,y-t,z)$\
$(x,y,z) \rightarrow (x,y,z-t)$\
Remove the same number of chips from two piles:\
$(x,y,z) \rightarrow (x-t,y-t,z)$ where $t\leq z$\
$(x,y,z) \rightarrow (x-t,y,z-t)$ where $t\leq y$\
$(x,y,z) \rightarrow (x,y-t,z-t)$ where $t\leq x$

### 3 Heap "Tax" Nim
 Normal nim rules (remove any number of chips from 1 pile), but the other two non-empty untouched piles lose 1 chip each.  
$$
(x,y,z) \rightarrow
\begin{cases}
(x-t, \max(0, y-1), \max(0, z-1)) & \text{if } 0 < t \leq x \\
(\max(0, x-1), y-t, \max(0, z-1)) & \text{if } 0 < t \leq y \\
(\max(0, x-1), \max(0, y-1), z-t) & \text{if } 0 < t \leq z
\end{cases}
$$

### 3 Heap Asymmetric Bounded Nim
Three piles are ordered:

You can remove any amount from Pile X.\
$(x,y,z) \rightarrow (x-t,y,z)$

You can remove chips from Pile Y, but the amount you remove cannot exceed the current size of Pile X.\
$(x,y,z) \rightarrow (x,y-t,z)$ where $t\le x$

You can remove chips from Pile Z, but the amount you remove cannot exceed the current size of Pile Y.\
$(x,y,z) \rightarrow (x,y,z-t)$ where $t\le y$

### 3-Heap Bounded Wythoff's Game
Normal Nim but you can remove any number of chips from two piles, as long as the ratio of the chips is between 1:2 and 2:1.\
For example if you take 4 chips from Pile X, you can take 2, 3, 4, 5, 6, 7, or 8 chips from Pile Y (or 0 which would be a standard Nim move)
