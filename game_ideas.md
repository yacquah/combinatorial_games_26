# Game Ideas
### Requirements
- Impartial
- Position representable by 3 nonnegative integers $(x,y,z)$
- Every move strictly decreases the position in lexicographic (dictionary) order.

### [2 Heap Fibonacci Nim](https://en.wikipedia.org/wiki/Fibonacci_nim)
Remove chips from a pile. The first move can remove up all chips except one. Every subsequent move can remove from 1 to double the number of chips the previous player took.

### 3 Heap Subtract a Square
Remove a square number of chips from a pile. If the 3 piles are independent, we can just use Sprague-Grundy theorem to find SG value. 

If we want to make it more interesting, we can make it so that it's like Wythoff's game, where we can remove the same number of chips from two piles (or 3?). Or the total number of chips removed could sum to a square.

### 3 Heap Nim with Merging Piles
Nim but you can merge piles together, leaving an empty pile behind. 

### 3 Heap Subtract a Prime
Similar to subtract a square, but you have to subtract prime numbers (so 0 and 1 chips are terminal positions). 

Also can make it where we can remove the same chips from multiple piles or other variants.

### 3 Heap Wythoff's Game but "Unbalanced"
Remove *k* chips from one pile and *2k* from another pile. 

### 3 Heap Impartial Euclid's Game
Three piles of size $x$, $y$, $z$, and you can remove some multiple of a pile's chips from one pile. When there is 1 pile remaining with chips, the game is over. 

Basically a move can remove $ky$ or $kz$ from $x$, $kx$ or $kz$ from $y$, or $kx$ or $ky$ from $z$, as long as the pile size is not negative. 

Or we can do a variation where we subtract $kx$ or $ky$ or $kz$ from the other two piles as another move. 