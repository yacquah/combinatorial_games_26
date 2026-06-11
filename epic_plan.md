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