# Diet Chomp
Normal 3-row chomp but with the restriction of removing no more than 4 pieces in a move.

Coordinates for the position are $(x,y,z)$ where $x$ is the number of three-tall columns, $y$ is the number of two-tall columns, and $z$ is the number of one-tall columns.

### Possible Moves from $(x,y,z)$
- **(M1):** &ensp; $(x,y-t,z+t)$
removes $t$ pieces, 

    $0<t\leq y$ &ensp; and &ensp; $t\leq 4$
    
- **(M2):** &ensp; $(x,y-t,0)$
removes $2t+z$ pieces, 

    $0<t\leq y$ &ensp; and &ensp; $2t+z\leq 4$

- **(M3):** &ensp; $(x,y,z-t)$
removes $t$ pieces,

    $0<t\leq z$ &ensp; and &ensp; $t\leq 4$

- **(M4):** &ensp; $(x-t,y+t,z)$
removes $t$ pieces, 

    $0<t\leq x$ &ensp; and &ensp; $t\leq 4$

- **(M5):** &ensp; $(x-t,0,z+y+t)$
removes $2t+y$ pieces,

    $0<t\leq x$ &ensp; and &ensp; $2t+y\leq 4$

- **(M6):** &ensp; $(x-t,0,0)$
removes $3t+2y+z$ pieces,

    $0<t\leq x$ &ensp; and &ensp; $3t+2y+z\leq 4$

    