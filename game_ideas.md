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

$(x,y,z) \rightarrow (x-k\operatorname{lcm}(y,z), y, z)$ \
$(x,y,z) \rightarrow (x, y-k\operatorname{lcm}(x,z), z)$ \
$(x,y,z) \rightarrow (x, y, z-k\operatorname{lcm}(x,y))$