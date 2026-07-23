# Bounded Wythoff Analysis (Pt. 3)

## Recursive Operator

### Goal: Find $W_{x+1}$ from $W_x$

We may start by expressing $W_x$ as the parents of all lower level losers: \
$W_x = P_x(L_0)+P_x(L_1)+P_x(L_2)+\dots+P_x(L_{x-1})$ where:

- $W_x$ is the sheet of instant winners on level x.
- $L_k$ is the sheet of losers on level k.
- The $P_x$ operator finds all the parents on level x.
- If we have a loser on level $k$ then the difference in levels is $x-k$.

#### Moves that change x-level

- Removing chips from only pile x:
$[x-t,y,z]$

- Removing chips from piles x and y:
$[x-s,y-t,z]$ with $\frac{1}{2} \le \frac{s}{t} \le 2$ and $s,t \ge 1$

- Removing chips from piles x and z:
$[x-s,y,z-t]$ with $\frac{1}{2} \le \frac{s}{t} \le 2$ and $s,t \ge 1$
\
\
Because the "normal nim x" move leaves $y$ and $z$ unchanged, if $L_k(y,z)$ is a loser,
 then $W_x(y,z)$ is an instant winner.

Moving down $x-k$ levels means removing $x-k$ from pile x, so piles y and z may have anywhere from
 $\lceil{\frac{x-k}{2}}\rceil$ to $2(x-k)$ chips removed.

Therefore, $W_x$ is a winner if $L_k(y-t,z)$ or $L_k(y,z-t)$ are losers for
$\lceil{\frac{x-k}{2}}\rceil \le t \le 2(x-k)$.

![Instant winners from losers 1 level below](images/possible_recursive_moves.png)\
*The red winner is from removing only from $x$, the blue is from removing from $x$ and $y$,
 and green is from removing from $x$ and $z$.*

For every level that we go up, we "extend" parents of losers horizontally ($+y$ direction) and
 vertically ($+z$ direction). If the difference in levels is $x-k$, then the extension will be from
 $\lceil{\frac{x-k}{2}}\rceil$ to $2(x-k)$ cells up or to the right from the loser.

### Attempt 1: No auxiliary sheets

To express the "extensions" of losers, we can define an operator $\mathcal{S}_\mathcal{d}$ where $d$
 is difference in levels $x-k$ and acts upon a loser sheet to make extensions horizontally and
 vertically for all losers.
$$\mathcal{S}_\mathcal{d}L_k(y,z) = \sum\limits_{t=\lceil{d/2}\rceil}^{2d}{L_k(y-t,z)+L_k(y,z-t)}$$

Recall that the parents of losers also includes the loser itself, but on the higher level due to the
 "normal nim x" move, which contributes $L_k$ to $W_x$.

Thus, $P_x(L_k)=L_k+\mathcal{S}_{x-k}L_k$.

So in total, the contributions from all lower loser sheets to a winner sheet $W_x$ is:
$$W_x=\sum\limits_{k=0}^{x-1}{L_k+\mathcal{S}_{x-k}L_k}$$

However, using this form, $W_{x+1}$ cannot be written in terms of $W_x$ alone.

$$W_{x+1} = \sum_{k=0}^{x} \big(L_k + \mathcal{S}_{x+1-k}L_k\big)$$
Taking out the last term of index $x$ gives us:
$$W_{x+1} = \underbrace{\big(L_x + \mathcal{S}_1(L_x)\big)}_{\text{new sheet } x} + \sum_{k=0}^{x-1}
 \big(L_k + \mathcal{S}_{x+1+k}L_k\big)$$

Notice that the sum portion is identical to $W_x$ but every $\mathcal{S}_d$ is now
 $\mathcal{S}_{d+1}$.

The problem with this is that for every step up, the farther edge of the extension moves from
 $2d \to 2d+2$, while the closer edge moves from $\lceil d/2 \rceil \to \lceil (d{+}1)/2 \rceil$
  which stays the same when $d$ is odd, but increases by one if $d$ is even.

We cannot express $\mathcal{S}_{d+1}$ in terms of $\mathcal{S}_d$ cleanly. A position in $W_x$ does
 not remember which loser generated it so we don't know if it should grow and in which direction.
 The $\mathcal{S}_d$ operator will extend both up and to the right of any marked position, instead
 of just from losers or only up/right.

### Attempt 2: Separating "extension" operators
We can try separating the $\mathcal{S}_d$ operator into its horizontal and vertical components:
We introduce the $\mathcal{H}$ and $\mathcal{V}$ operators, for horizontal and vertical shifts.

The horizontal shifter $\mathcal{H}$ will move a sheet to the right by one spot, where
 $\mathcal{H}A(y,z)=A(y-1,z)$.

The vertical shifter $\mathcal{V}$ will move a sheet up by one spot, where
 $\mathcal{V}A(y,z)=A(y,z-1)$.

Writing it out and finding a general formula for $W_x$ using this method:
![Work trying to find recursive operator](images/non_auxiliary_recursive.jpeg)\
*The underlined blue parts are difference between $W_x$ and $W_{x+1}$.*

This encounters a similar issue where applying a horizontal or vertical shift to $W_x$ will lead to
 unintended parts being shifted (the vertical parts being shifted horizontally and vice versa).
 This would lead to parents being found through a "diagonal" move which is not allowed.
 Also, it would depend on the difference being even or odd.

### So we need auxiliary sheets:
We use auxiliary sheets to calculate the contributions of moves separately.

We find the change in sheets that only contain parents from a certain move while going up x-levels,
 and then to get $W_x$, we sum the contributions up:

$\boxed{W_{x+1}=V^1_{x+1}+V^2_{x+1}+V^3_{}x+1}$

We introduce three auxiliary sheets ($V^1,V^2,V^3$), one for each move.\
$V^1$ are the instant winners that can reach a loser by only removing from $x$, $V^2$ are the
 winners that can reach losers by only removing from $x$ and $y$, and $V^3$ are winers that can
 reach losers by only removing from $x$ and $z$.

- "Normal nim x" move:
  $\boxed{V^1_{x+1}=V^1_x+L_x}$
  <details>
  <summary><b>Click to view the image</b></summary>

  ![Instant winner of a loser 1 level above with V1](images/auxiliary_nim_v1_1.png)\
  ![Instant winner of two losers 1 level above with V1](images/auxiliary_nim_v1_2.png)\
  *To find a recursive operator that acts on $V^1$, it's just the standard nim recursive operator.
   Since we are moving straight down to loser sheets, the (y,z) coordinates won't change so we only
   need to add the current losers $L_x$ to every other lower loser, which is already accounted for
   from $V^1_x$. So, $V^1_{x+1} = V^1_x + L_x$.*
  </details>
<br>

- Removing from $x$ and $y$:
  $\boxed{V^2_{x+1} = \mathcal{S}_y(V^2_x + L_x) + S^2_y(V^2_x + L_x) +
   \mathcal{S}_y(V^2_{x-1} + L_{x-1})}$
  <details>
  <summary><b>Click to view the image</b></summary>

  ![Progression of auxiliary sheet V2](images/auxiliary_nim_v2.png)\
  *To find a recursive operator that acts on $V^2$, we need to find a way to expand that horizontal
   line that starts at a loser. Every time we go up a level, that horizontal line's left endpoint
   should increase by 1 every 2 levels, while the right endpoint should increase by 2 every level.*
  </details>
<br>

- Removing from $x$ and $z$:
  $\boxed{V^3_{x+1} = \mathcal{S}_z(V^3_x + L_x) + S^2_z(V^3_x + L_x) +
   \mathcal{S}_z(V^3_{x-1} + L_{x-1})}$

  This will be identical to $V^2$ but instead of horizontal, it is extending vertically.

## Supermex Operator
The supermex operator concerns how we can find the losers from the same-level instant winner sheet.

#### Moves that don't change x-level:

- Removing chips from only pile y:
$[x,y-t,z]$

- Removing chips from only pile z:
$[x,y,z-t]$

- Removing chips from piles y and z:
$[x,y-s,z-t]$ with $\frac{1}{2} \le \frac{s}{t} \le 2$ and $s,t \ge 1$

All valid moves must decrease the **lexicographic order:**

&emsp; $(x,y,z) \rightarrow (x',y',z')$ where one of the following are true:
- $x'<x$
- $x'=x$ and $y'<y$
- $x'=x$ and $y'=y$ and $z'<z$

### Finding parents on the graph
This means that we find the first available loser by scanning column by column (least to greatest
 $y$ coordinates), and within each column scanning upwards (least to greatest $z$ coordinates) until
 we find the first non-winner position.

Then from that loser, we mark all positions with a higher $z$ only, a higher $y$ only, and positions
 that we can reach by adding chips in a $1\!:\!2$ to $2\!:\!1$ ratio. This turns out to be a cone
 with upper slope $2$ and bottom slope $\frac{1}{2}$.
<details>
  <summary><b>Click to view the image</b></summary>

  ![Supermex L0 with first loser](images/supermex_1.png)

</details>
<br>

We continue to find the next loser, which must be in the next column and scan upwards to fill
another cone.
<details>
  <summary><b>Click to view the image</b></summary>

  ![Supermex L0 with first two losers](images/supermex_2.png)

</details>
<br>

And repeat until we fill the whole grid.
<details>
  <summary><b>Click to view the image</b></summary>

  ![Filled up supermex L0](images/supermex_3.png)

</details>
<br>

Since losers block off the entire column and row that they are in, there is exactly one loser in
 each row/column.

## Geometry
![L0, L1, L2, W1, W2, W3 with size 50](images/0123LW.png)\
![W/L 32, 64, 128 with sizes 300, 600, 1200](images/32_64_128LW.png)

### First observations
We can notice that the game is completely symmetrical across all three axes, since there is no
 difference between the $x,y,z$ piles.

This means that the graphs are symmetrical across the $45 \degree y/z$ diagonal (as well as $x/y$
 and $x/z$ which is less visible in 2D sheets).

Additionally, we spot two loser lines, which we will call the "upper loser line" and "lower loser
 line", with their slopes being inverses of each other. These loser lines lie on the outer boundary
 of the instant winner sheet geometries. There is also a region near the origin with three regions
 of losers. As we move up in x-values, the shape of the sheets stays roughly the same, while the
 size just increases.

Because the game is symmetrical, we can figure out the coordinates of the losers at $y=0$ or $z=0$.
 When $y=0$, it is basically the two-pile game with piles $x$ and $z$. When $z=0$, it is the
 two-pile game with $x$ and $y$. These losers will be the same as the losers at $x=0$, which is the
 two-pile game with piles $y$ and $z$.

For example, from the $L_0$ sheet we can see that there are losers with $x=0$ at
 $(1,3),(2,6),(3,1),(4,11)\ldots$\
This means that on $L_1$, there are losers at $(3,0)$ and $(0,3)$. On $L_2$, there are losers at
 $(6,0)$ and $(0,6)$. On $L_3$, there are losers at $(1,0)$ and $(0,1)$, and so on.

## Renormalization

We would like to find values that characterize the geometry of losers. From before, we see that
 there are two loser lines. We can assign each line a slope and density. The upper line has slope
 $m_u$ and density $\lambda_u$, while the lower line has slope $m_\ell$ and density $\lambda_\ell$.
 Since they are mirrored across the diagonal, we can assign one y-intercept/z-intercept value that
 scales with x-level, $\alpha$.
![Graph for desired variables](images/variables.png)

### Equations

First we look at four variables, $\lambda_u,\lambda_\ell,m_u,m_\ell$, and find four equations
 relating them to solve.

We know that there is exactly one loser in any column or row, and we define density as the number of
 dots on a line (upper or lower) per number of columns. Therefore, the two densities must sum to 1:
$$\boxed{\lambda_u+\lambda_\ell=1}$$

Since the game is symmetric across the $45\degree$ diagonal, the two lines are reflections of each
 other and their slopes are inverses:
$$\boxed{m_\ell = \frac{1}{m_u}}$$

#### Relating the densities to the slopes

Counting the losers along the two lines gives a relation between the densities and the slope.
 A horizontal stretch $d$ measured along the lower line contains $\lambda_\ell\mkern1mu d$ losers,
 and if we mirror this region to the upper line, the matching horizontal stretch $c$ along the upper
 line contains $\lambda_u\mkern1mu c$ losers. So, we have the same number of losers in
 $\lambda_u\mkern1mu d$ as in $\lambda_u\mkern1mu c$.

![Mirroring number of dots per distance across 45 degrees line](images/equation3.png)

$$\lambda_u\mkern1mu c = \lambda_\ell\mkern1mu d \qquad\Longrightarrow\qquad
\frac{\lambda_u}{\lambda_\ell} = \frac{d}{c} = m_u.$$
$$\boxed{\frac{\lambda_u}{m_u}=\lambda_\ell}$$

Our fourth equation comes from looking at supermex. It comes from asking how far apart consecutive
 losers on the upper line have to be. We are trying to figure out how we can generalize getting from
 one loser to another loser on the same line (we will focus on the upper line for convenience).

When we move from a loser $(y,z)$ to an implied winner, we know that the implied winner with highest
 possible $z$ (that is a parent of this specific loser) is of the form $(y+\Delta y,z+2\Delta y)$.
 This is because if we removed $\Delta y$ chips from $y$ from a winning position, then we can remove
 a maximum of $2\Delta y$ from $z$. Recall the two-pile move lands anywhere in a "cone" opening to
 the right, bounded by slope $\tfrac{1}{2}$ below and slope $2$ above (removing chips in a $1\!:\!2$
 to $2\!:\!1$ ratio).

<!The implied winners with highest z in a given column>
<img src="images/highestwinner.png" style="height: 500px; max-height: 100%;">\

To find the next consecutive loser on the upper line, it has to be above that cone, so at
 $(y+\Delta y, z + 2\Delta y+1)$. So over a run of $\Delta y$ columns, the rise in $z$ is
 $2\Delta y$ to reach the top loser in the column, plus one extra cell for each loser we passed
 along the way. *This is assuming that we do not have lower level losers that will force the next
 loser to increase in $z$ by 1.  If we go across $\Delta y$, then the number of upper-line losers
 passed would just be $\lambda_u(\Delta y)$, so:
$$\Delta z = 2\Delta y + (\text{\# of losers passed})$$
$$\Delta z = 2\Delta y + (\lambda_u \mkern1mu \Delta y)$$
$$\Delta z = \Delta y(2+\lambda_u)$$
$$\frac{\Delta z}{\Delta y} = 2+ \lambda_u$$
$$\boxed{m_u = 2+\lambda_u}$$

### Solving the equations

To recap, we have four equations:
$$\begin{equation}
    \lambda_u+\lambda_\ell=1
\end{equation}$$
$$\begin{equation}
    m_\ell = \frac{1}{m_u}
\end{equation}$$
$$\begin{equation}
    \frac{\lambda_u}{m_u}=\lambda_\ell
\end{equation}$$
$$\begin{equation}
    m_u = 2+\lambda_u
\end{equation}$$

We can substitute $(3)$ into $(1)$:
$$\lambda_u + \frac{\lambda_u}{m_u}=1$$
$$\lambda_u\left(1+\frac{1}{m_u}\right)=1$$
$$\lambda_u=\frac{1}{1+\frac{1}{m_u}}$$
$$\begin{equation}
\lambda_u=\frac{m_u}{m_u+1}
\end{equation}$$

Then we can use this equation $(5)$ and substitute it into $(4)$:
$$\lambda_u = \frac{m_u}{m_u + 1} \qquad\text{and}\qquad m_u = 2 + \lambda_u$$
$$\lambda_u=\frac{2+\lambda_u}{3+\lambda_u}$$
$$\lambda_u(3 + \lambda_u) = 2 + \lambda_u$$
$$\lambda_u^2 + 2\lambda_u - 2 = 0$$

The quadratic formula gives $\lambda_u = \dfrac{-2 \pm \sqrt{4 + 8}}{2} = -1 \pm \sqrt{3}$, and
 we take the positive root because density is positive:
$$\boxed{\lambda_u = \sqrt{3} - 1} \approx 0.732$$
Now that we have one unknown solved, we can find the rest easily:
$$m_u = 2 + \lambda_u$$
$$\boxed{m_u = 1 + \sqrt{3}} \approx 2.732$$
$$m_\ell = \frac{1}{m_u}$$
$$m_\ell = \frac{1}{1 + \sqrt{3}} $$
$$\boxed{m_\ell = \frac{\sqrt{3} - 1}{2}} \approx 0.366$$
$$\lambda_u+\lambda_\ell = 1$$
$$\lambda_\ell = 1 - \lambda_u$$
$$\lambda_\ell = 1 - \sqrt{3} - 1$$
$$\boxed{\lambda_\ell = 2 - \sqrt{3}} \approx 0.268$$

### Actual geometry

These four values are found under the assumption that there is no "bumping up" from loser level
 loser sheets. That is when there is a loser position already occupied by a lower level loser. The
 lower level loser would be reachable through a "normal nim x" move, since simply removing chips
 from the $x$ pile would reach the loser. Since losers may not reach losers, the position on $L_x$
 must be some sort of winner and the actual loser would have its $z$ increased by one. from the $x$
 pile would reach the loser.

When we look at the actual geometry of the sheets higher than $x=0$, we find that the lines form an
asymptote.

#### Asymptotic lines

The actual line starts out steeper, starts from under the asymptotic line, and approaches
 a slope of $1+\sqrt{3}$.

![L100 asymptotic line](images/L100_asymptotic.png)\
*$L_{100}$ top line losers start under the asymptotic line and approach it.*

![Slopes settling to asymptotic slope](images/slopes_settling.png)\
*The higher the x-level, the longer it takes for the slope to reach the $1+\sqrt{3}$*

However, the points are not always below the asymptotic line. Rather, it acts as a best fit line as
 $y$ and $z$ increase much greater than the x-level.

<!Residuals - distance from line>
<img src="images/residuals.png" style="height: 500px; max-height: 100%;">\
*Distance from line gradually decreases yet can vary above and below.*

![Intercepts of asymptotic lines and edge dots for x=0 to 100](images/intercepts.png)\
*Intercepts of asymptotic lines and edge dots for x=0 to 100. The top blue line represents the
 individual intercepts of the best fit lines for losers. The orange is the edge dots with z=0,
 and many of these lie on the line with slope $m_u$, while others lie on the line with slope
 $m_\ell$.*

The asymptotic lines' intercepts are still unclear, but if they scale linearly with x-level,
this would be the $\alpha$ we are looking for.

![Alpha and beta intercepts](images/general_intercepts.png)\
*The actual intercepts/edge dots (loser at $y=0$) labeled as $\beta x$ lie at $(1+\sqrt{3})x$.*

The actual intercepts are at $(1+\sqrt{3})x$ because it reduces to a two-pile game, which have
 losers with slope of $1+\sqrt{3}$.
 However, the asymptotic lines have a larger intercept $\alpha x$.

### Structure near the origin
#### Slope near the origin
The upper line slope asymptotes to $1+\sqrt{3}$ because of some columns being "blocked" by the lower
 line losers. This prevents a loser from being on the upper line, and the slope from one loser to
 the next becomes $5/2$ instead of $3$.

However, near the origin, the lower loser line has not appeared yet. The first loser at $y=0$ has a
 height of $z=(1+\sqrt{3})\,x$. This loser is on the upper line. When this gets mirrored across the $y=z$ diagonal, this means the first loser on the lower line is in column $y=(1+\sqrt{3})\,x$.

Therefore, up until column $y=(1+\sqrt{3})\,x$, the upper line has no interruptions from the lower
 line (as there is no lower line). So, no columns are skipped and the slope from one loser to the
 next on the top line is 3.

We can figure this out by using $(4)$, where $m_u = 2+\lambda_u$. The density of the upper line is
 simply $1$, because $\lambda_u+\lambda_\ell=1$ and $\lambda_\ell=0$. Thus, $m_u=2+1=3$.

<!Region with slope of 3>
<img src="images/three_slope.png" style="max-height: 400px;">\
*The highlighted region has $m_u=3$ exactly, even across the gaps (at least for $x=40$).

#### Three other regions near the origin

<!Three regions near the origin image>
<img src="images/origin_three_regions.png" style="max-height: 400px;">\
This part of the origin may be split up into three regions: a downwards diagonal area labeled
 "Region 1," and two symmetrical parts a bit further out labeled "Region 2" and "Region 3."

<!Three Dimensional view of three regions>
<img src="images/3d_core_regions.png" style="max-height: 400px;">\
*This is the 3D view of three regions. The $x,y,z$ axes are all symmetrical, and region 1 corresponds to the cut view of the large sheet and "small cone" in the x-direction, while regions 2 and 3 correspond to a differently-cut view of the y and z-direction "small cones."*

#### Region 1
To find region 1, we can analyze the supermex operator again. This time, we make use of symmetry in the game, since the three piles are interchangable.

The game is symmetrical in 6 ways: If we have a loser $(x,y,z)$, then the following are also losers:
- $(x,z,y)$
- $(y,x,z)$
- $(y,z,x)$
- $(z,x,y)$
- $(z,y,x)$

We can generalize the positions into the sorted triple $(a,b,c)$ where $a \le b \le c$.

<!Losers in region 1 line>
<img src="images/region1_losers.png" style="max-height: 300px">
<!Regions corresponding to largest pile>
<img src="images/largest_piles.png" style="max-height: 300px;">

*The losers in region 1 are the cross-section where the sheet coordinate $x$ is the largest pile, $c=x$. The two more prominent parts graphed, regions 2, 3, and the loser lines, are cross-sections of the shapes when $y$ and $z$ are the largest piles.*

When $x$ is the largest pile $c$, then $y$ and $z$ are then the two smaller piles $a,b$, so the losers are near the origin.

So to find the losers in region 1, we need to find which pairs $(a,b)$ with $a,b\le x$ is $(a,b,x)$ a loser since $x$ is the larger pile.

Just like how there is only one loser in a row or column in a sheet, each pair $(a,b)$ has at most one corresponding $c$ . If $(a,b,c)$ and $(a,b,c')$ were both losers with $c<c'$, then $(a,b,c')$ can reach $(a,b,c)$ by removing chips off the largest pile, but we cannot reach a loser from a loser so there cannot be two $c$ values for one pair $(a,b)$.

**Finding the slope**\
If $(a,b,c)$ is a loser and we increase one small pile up by one, the loser in the pair $(a,b+1)$ can only be at $c+3$. Using the same supermex "cone" from only looking at a sheet with $y$ and $z$, heights $c,c+1,c+2,c+3$ would be blocked off for $(a,b+1)$, since those would be implied winners.

This is the same if we were to change $a$ or $b$, so if we take 1 chip from $a$ or $b$ the next loser lands at $c+3$:

Define
$F(a,b)=\text{the largest pile }c\text{ that makes }(a,b,c)\text{ a loser.}$
$${F(a,b+1)=F(a,b)+3}$$
And $a,b$ are both small piles playing identical roles, so the same holds stepping in $a$:
$$F(a+1,b)=F(a,b)+3.$$

This is basically $\text{Equation} (4): \quad\Delta z = 2\Delta y + \lambda_u \quad$ but with $\Delta y=1$ with one loser, and the variables swapped because we are considering the general case.

So, $F$ increases by $3$ whether we change $a$ or $b$, so it depends only on the sum $a+b$:
$$\boxed{F(a,b)=3(a+b)+K}$$
for some constant $K$ consistent across sheets. In region 1, $x$ is the largest pile so we set $c=x$, and $y$ and $z$ to be $a$ and $b$:
$$x=3(y+z)+K$$
$$y+z=\frac{x-K}{3}$$
$$z=-y+\frac{x-K}{3}$$

Now we have the slope of $-1$, but we don't know the intercept, which $K$ determines.

------- Claude -------

**Is it $K=0$?** It is the natural guess — the empty position $(0,0,0)$ is a loser, so marching up in threes from the origin would give $F(a,b)=3(a+b)$, i.e. $y+z=x/3$. It fails, for a reason you can check by hand. $K=0$ puts a loser wherever the big pile is three times the sum of the two small piles; at the piles $(1,1)$ that demands a loser at $(1,1,6)$. But $(1,1,1)$ is already a loser — from it, every move lands on a winner;

**How much lower — read it off, in the right place.** The tempting place is the bottom edge, where one pile is empty and the game is just two piles. Its losers are
$$(1,3),\ (2,6),\ (4,11),\ (5,14),\ (7,19),\ (8,22),\dots$$
and comparing each big pile to three times its small pile gives
$$z-3y \;=\; 0,\ 0,\ -1,\ -1,\ -2,\ -2,\ -2,\ -2,\ -3,\dots$$
which is **not constant** — it slides down. The reason is concrete: this two-pile game uses each whole number at most once (a number that is the big pile of one loser cannot be the small pile of another), so some columns hold no loser at all — column $3$ is empty because $3$ is already the big pile of $(1,3)$, column $6$ because of $(2,6)$, and so on — and **each skipped column drops the value by exactly one**. The edge is riddled with these gaps and never holds still, so it is the wrong place to read $K$.

Step **one pile in**, to the losers whose smallest pile is $1$, and take the run of consecutive columns
$$(1,4,14),\ (1,5,17),\ (1,6,20),\ (1,7,23),\ (1,8,26)$$
— no gaps, so the $+3$ spacing holds cleanly. The big pile minus three times the sum of the two small piles is now $-1,\ -1,\ -1,\ -1,\ -1$: a flat run, sitting exactly one cell below the clean $x/3$ line — precisely the one-step drop the blocked corner forced. That settled value is the offset:
$$\boxed{K=-1}\qquad\Longrightarrow\qquad y+z=\frac{x+1}{3}.$$

---

From $y+z=\frac{x+1}{3}$ we find that $y+z$ must be an integer. We cannot have fractional piles so this slope $-1$ line only exists when $\frac{x+1}{3}$ is divisible by 3: $x\equiv 2\pmod 3$

The line $y+z=\frac{x+1}{3}$ is straight, so the predicted intercept would be $z=\frac{x+1}{3}$, but the dots actually curve upward and the actual intercept is higher.

We can find this intercept by looking at the positions where $y=0$, which is the same as playing with only the $x$ and $z$ piles. Its loser is a two-pile loser pair, and those pairs have their big pile equal to $1+\sqrt3$ times their small pile. Here $x$ is the big pile, so the small pile $z$ is
$$\boxed{z=\frac{x}{1+\sqrt3}=\frac{\sqrt3-1}{2}\,x}$$

<!Intercepts per x-level matched with m_u and m_l>
<img src="images/two_intercepts.png" style="max-height: 300px;">

*These are the actual intercepts of losers at $y=0$ for various x-levels. The top line is of slope $m_u=1+\sqrt{3}$ and the bottom line is of slope $m_\ell=\frac{\sqrt{3}-1}{2}.$*

<!Intercepts per x-level matched with m_u and m_l>
<img src="images/x121_loserlower.png" style="max-height: 300px;">
<!Intercepts per x-level matched with m_u and m_l>
<img src="images/x0_121loserupper.png" style="max-height: 300px;">

<!Intercepts per x-level matched with m_u and m_l>
<img src="images/region_1_intercept.png" style="max-height: 300px;">
<!Intercepts per x-level matched with m_u and m_l>
<img src="images/region_1_upperslope.png" style="max-height: 300px;">

*The intercepts line up with the losers on the $L_0$ sheet roughly. If we were to find the point on the projected line, then it would match up better but this is the closest point.*

So in summary, region 1 consists of:
- A line segment denoted by $y+z=\dfrac{x+1}{3}$, with slope $-1$ and predicted intercept of $\dfrac{x+1}{3}$.
- The actual intercept of $z=\dfrac{x}{1+\sqrt3}=\dfrac{\sqrt3-1}{2}\,x$.
