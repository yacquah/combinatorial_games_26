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

