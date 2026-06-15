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