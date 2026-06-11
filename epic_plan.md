# Epic Plan!!
### Inputs
- Size of square grid (integer such as 100x100 grid)
- Desired target: Winner/Loser sheet, x-level (for example maybe we want to find $W_x$)
### Initialization
- Initialize $W_x$ as $W_x$ which is empty
- Initialize $L_x$ as $L_0$ which we should manually calculate
    - Nim: all spaces where $y=z$
    - Chomp: when there are 1 more rows of height 1 than rows of height 2: $(0,y,1)$

### Functions
- Recursive operator $\mathcal{R}$ where $W_{x+1} = \mathcal{R}W_x$
    - Nim: $\mathcal{R} = \mathcal{M} + \mathcal{I}$
    - Chomp: $\mathcal{R} = \mathcal{L}(\mathcal{I+DM})$
- Supermex $\mathcal{M}$ where we have a common part "mex" that sets the smallest non-occupied space as 'L'
- Left-shift $\mathcal{L}$ where if we have matrix $A$, $\mathcal{L}A(y,z)=A(y+1,z)$
- Identity $\mathcal{I}$ where $\mathcal{I}A=A$
- Diagonal $\mathcal{D}$ where it marks all positions starting from $(0,z^*)$ to $(z^*,0)$: All points $(s,z^*-s): 0\le s\le z^*$

### Generating $W_x$ up to target level:
First we need to manually generate $W_1$ (for Chomp) because if we use $\mathcal{R}W_0$ then it won't do it correctly, since it will keep generating a blank sheet for $W_x$ because if $z=0$ then we stop marking more losing positions.

Instead we need to start finding $W_x$ in Chomp 