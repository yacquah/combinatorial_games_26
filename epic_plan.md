# Epic Plan!!
### Inputs
- Size of square grid (integer such as 100x100 grid)
- Desired target: Winner/Loser sheet, x-level (for example maybe we want to find $W_x$)

### Initialization
- Initialize $W_x$ as $W_x$ which is empty
- Initialize $L_x$ as $L_0$ which we should manually calculate
    - Nim: all spaces where $y=z$
    - Chomp: when there are 1 more rows of height 1 than rows of height 2: $(0,y,1)$

### Main
Call "Generate $W_x$ function" with inputs of our initialized $W_x$, desired x-level, $L_x$, and grid size. 

If the target is loser then call "Generate $L_x$ function" with input of $W_x$ after calling the $W_x$ function, and grid size.

### Functions
- Recursive operator $\mathcal{R}$ where $W_{x+1} = \mathcal{R}W_x$
    - Nim: $\mathcal{R} = \mathcal{M} + \mathcal{I}$
    - Chomp: $\mathcal{R} = \mathcal{L}(\mathcal{I+DM})$
- Supermex $\mathcal{M}$ where we have a common part "mex" that sets the smallest non-occupied space as 'L'
- Left-shift $\mathcal{L}$ where if we have matrix $A$, $\mathcal{L}A(y,z)=A(y+1,z)$
- Identity $\mathcal{I}$ where $\mathcal{I}A=A$
- Diagonal $\mathcal{D}$ where it marks all positions starting from $(0,z^*)$ to $(z^*,0)$: All points $(s,z^*-s): 0\le s\le z^*$

### Function for generating $W_x$ up to target level:
First, we need to manually generate $W_1$ (for Chomp) because if we use $\mathcal{R}W_0$ then it won't do it correctly, since it will keep generating a blank sheet for $W_x$ because if $z=0$ then we stop marking more losing positions.

Instead, we need to start finding $W_x$ in Chomp by using $W_1 = \mathcal{LD}L_0$ and then we can start generating starting with $W_1$. For Nim, we have the choice of finding $W_1$ separately, just like with Chomp, or we can change the next step to instead recursively generate starting from $W_0$.

1. If desired level is 0, output directly output the corresponding $L_0$ or $W_0$ sheets. 
2. Otherwise loop from $x=2$ to $x\le [\text{desired level}]$ and recursively generate $W_x$ using $W_{x+1} = \mathcal{R}W_x$
3. Now our $W_x$ should equal $W_{\text{desired level}}$ because if $[\text{desired level}]=0$, then we already outputted it. If $[\text{desired level}]=1$, then we know it already and we should not have looped to the next higher sheets.

### Function for generating $L_x$:
Use supermex operator $\mathcal{M}$ on $W_x$.

## Drawing the result:
We can have a function separate from the games that plots a grid, mapping out either the $W$ or $L$ sheets depending on what is inputted to it. 