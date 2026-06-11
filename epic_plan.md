# Epic Plan!!
### Inputs
- Size of square grid (integer such as 100x100 grid)
- Desired target: Winner/Loser sheet, x-level (for example maybe we want to find W<sub>20</sub>)
### Initialization
- Initialize W<sub>x</sub> as W<sub>0</sub> which is empty
- Initialize L<sub>x</sub> as L<sub>0</sub> which we should manually calculate
    - Nim: all spaces where $y=z$
    - Chomp: when there are 1 more rows of height 1 than rows of height 2: $(0,y,1)$