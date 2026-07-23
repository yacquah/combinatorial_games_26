# Combinatorial Game Foundations & Renormalization Framework

## 1. Combinatorial Game Foundations

### Core Criteria
1. **Two Players**: Alternating turns until one player wins or loses (no draws allowed).
2. **Deterministic**: No chance moves (e.g., no rolling dice or dealing cards).
3. **Perfect Information**: All game information is fully visible to both players.
4. **Categorization**: Classified as either **impartial** or **partizan**.
5. **Termination**: Games end when no legal moves remain (categorized by **normal** or **misère** play rules).
6. **Finite State Space**: Played on a set (usually finite) of positions, ending in a finite number of moves.

---

## 2. Game States & Positions

* **Initial Position $\rightarrow$ Terminal Position**:
  * **Terminal Position**: A state where no legal moves are available.
  * **P-position**: Winning position for the *Previous* player (the player who just moved).
  * **N-position**: Winning position for the *Next* player (the player whose turn it is).

### Properties of P and N Positions
* Under **normal play**, terminal positions are **P-positions**. Under **misère play**, terminal positions are **N-positions**.
* From an **N-position**, there is *at least one* legal move to a **P-position**.
* From a **P-position**, *all* legal moves lead to **N-positions**.

---

## 3. The Game of Nim & Nim-Sum

### Rules & Setup
* **Setup**: 3 piles of chips $(x_1, x_2, x_3)$.
* **Move**: Choose a single pile and remove any positive number of chips.
* **Winning Condition**: Under normal play, the player to take the last chip wins.

### Nim-Sum Calculation ($\oplus$)
The Nim-sum is calculated by expressing each pile size in binary ($\text{base}_2$) and performing bitwise XOR (addition without carrying):

```python
# Example: Piles of size 13, 12, and 8
piles = [13, 12, 8]

# Binary representation:
# 13 = 1101_2
# 12 = 1100_2
#  8 = 1000_2
# --------------
# XOR = 1001_2 = 9

nim_sum = 13 ^ 12 ^ 8  # Evaluates to 9 (N-position)

```

* **P-position Criterion**: A position is a **P-position** if and only if $\bigoplus x_i = 0$.
* **N-position Criterion**: A position is an **N-position** if $\bigoplus x_i \neq 0$.

### Winning Strategy in Nim

* To make the Nim-sum equal $0$, all binary columns must contain an **even** number of $1\text{s}$.
* Modify the size of a single pile to change its binary representation and force the game into a **P-position**.
* **Misère Nim Strategy**: Play standard normal-play Nim until only **one pile** remains with a size $> 1$. Then, reduce that pile to size $0$ or $1$ to leave an **odd number of piles of size 1**.

---

## 4. Directed Graph Representation

A game can be modeled as a directed graph $G = (X, F)$:

* $X$: Set of all possible game positions.
* $F(x)$: Set of all followers (legal next moves) from position $x$.
* **Terminal Positions**: Positions where $F(x) = \emptyset$.
* **Start Position**: $x_0$.
* **Progressively Bounded**: Every path has a length less than or equal to some maximum integer $n$.
* **Cycles**: Paths that lead back to a previously visited vertex.

### Subtraction Game Model

For a game defined on $X = \{0, 1, 2, \dots, n\}$ with $x_0 = n$ and $F(0) = \emptyset$:

```python
def followers(x: int, valid_moves: list[int]) -> list[int]:
    """Returns the set of follower positions F(x) from state x."""
    return [x - m for m in valid_moves if x - m >= 0]

```

---

## 5. Sprague-Grundy Theorem & MEX

### Minimum Excludant (MEX)

The $\text{mex}$ function returns the smallest non-negative integer not present in a given set:

$$\text{mex}(S) = \min \{ n \ge 0 : n \notin S \}$$

*Example*: $\text{mex}(\{0, 1, 3\}) = 2$.

### Sprague-Grundy Value Calculation

For any position $x$, its Grundy value $g(x)$ is defined recursively:

$$g(x) = \text{mex}(\{ g(y) : y \in F(x) \})$$

### Analysis & Winning Conditions

* **Terminal Position**: $x$ is terminal $\implies g(x) = 0$ (P-position).
* **If $g(x) = 0$**: Every follower $y \in F(x)$ has $g(y) \neq 0$ ($x$ is P, all $y$ are N).
* **If $g(x) \neq 0$**: At least one follower $y \in F(x)$ has $g(y) = 0$ ($x$ is N, target $y$ is P).

### Graph Issues & Limitations

* **Progressively Infinite Graphs**: Path lengths have no maximum limit, which can cause Sprague-Grundy values to become infinite.
* **Graphs with Cycles**: A valid Sprague-Grundy function might not exist, allowing infinite play.

---

## 6. Disjunctive Sum of Games

When combining $n$ independent sub-games into $G = G_1 + G_2 + \dots + G_n$:

* A turn consists of choosing **one** sub-game and making a legal move within it.
* Game ends when **all** individual sub-games reach terminal positions.
* The position space $X$ is the Cartesian product: $X = X_1 \times X_2 \times \dots \times X_n$.
* A state is an ordered vector $x = (x_1, x_2, \dots, x_n)$.

### Followers in Sum of Games

```python
# A move in game i updates position x_i while keeping all other positions fixed:
# F(x) = (F1(x1) x {x2} x ... x {xn}) U ({x1} x F2(x2) x ... x {xn}) U ...

```

### Sprague-Grundy Theorem for Game Sums

The Grundy value of a combined game position is the Nim-sum of the individual Grundy values:

$$g(x_1, x_2, \dots, x_n) = g_1(x_1) \oplus g_2(x_2) \oplus \dots \oplus g_n(x_n)$$

#### Theoretical Properties (The Proof Principles)

1. **Reachability**: For any value $a < b$ (where $b$ is current total value), there exists a legal move in one sub-game to reduce the total value directly to $a$.
2. **Invariance**: No single legal move can preserve the total value $b$.
3. **Key Takeaway**: Every impartial game under normal play behaves identically to a single pile of Nim chips of size $g(x)$.

---

## 7. Sums of Subtraction Games

### Rules

Players may remove $1 \le k \le m$ chips from a single pile per turn, where $m$ is the maximum subtraction limit.
The Grundy value for a pile of size $x$ is given by:

$$g(x) = x \bmod (m + 1)$$

### Example: Combined Subtraction Game

Given a state $(9, 10, 14)$ across 3 different subtraction rules:

* **Game 1** ($m_1 = 3$, size $9$): $g_3(9) = 9 \bmod 4 = 1$
* **Game 2** ($m_2 = 5$, size $10$): $g_5(10) = 10 \bmod 6 = 4$
* **Game 3** ($m_3 = 7$, size $14$): $g_7(14) = 14 \bmod 8 = 6$

```python
# Combined Sprague-Grundy value:
total_sg_val = 1 ^ 4 ^ 6  # Evaluates to 3 (N-position)

```

Since $g(x) \neq 0$, the position is an **N-position**. The current player can force a win by moving to a position where $g(x') = 0$.

---

## 8. Take-and-Break Games (Lasker's Nim)

### Rules

Players choose a single pile on their turn and perform one of two operations:

1. **Take**: Remove any number of chips from the pile (standard Nim move).
2. **Break**: Split a pile ($\ge 2$ chips) into two smaller, non-empty piles ($a + b = x$). No chips are removed.

### Grundy Value Evaluation

* **Take moves**: Computed using standard MEX over follower positions.
* **Break moves**: The Grundy value of the split state is the Nim-sum of the component piles:

$$g(a, b) = g(a) \oplus g(b)$$

$$g(x) = \text{mex}\left( \{ g(x - k) \}_{k \ge 1} \cup \{ g(a) \oplus g(b) \}_{a + b = x} \right)$$

---

## 9. Landsberg's Renormalization Framework

Renormalization handles complex, non-decomposable games where classical Sprague-Grundy theory fails, utilizing operators on **IN-sheets** (Instant-N sheets) and **P-sheets**.

### Key Mathematical Operators

* **Recursion Operator ($R$)**:
Generates higher-level IN-sheets $W_x$ from preceding levels $W_{x-1}$:

$$W_x = R * W_{x-1}$$



*If direct recursion fails, auxiliary vector sheets $V_x = [V_x^1, V_x^2, \dots]$ are used: $V_x = R * V_{x-1}$.*
* **Supermex Operator ($M$)**:
Maps an IN-sheet $W_x$ directly to a P-sheet $P_x$ (represented as a binary matrix of $0\text{s}$ and $1\text{s}$ marking P-positions):

$$P_x = M * W_x$$



Generalizes the 1D $\text{mex}$ operator to higher-dimensional geometric structures.

---

## 10. Analyzed Games Under Renormalization

### A. Three-Row Chomp ($M = 3$)

Impartial, non-decomposable game played on an $M \times N$ grid with a poison token at $(0, 0)$.

1. **Coordinates** (Zeilberger System): $p = [x, y, z]$
* $x$: Number of columns of height 3 (sheet index).
* $y$: Number of columns of height 2.
* $z$: Number of columns of height 1.
* Starting Position: $[x, 0, 0]$


2. **First-Player Strategy**: David Gale's strategy-stealing argument guarantees $[x, 0, 0]$ is an **N-position** (Player 1 win), though non-constructive.
3. **Operators**:
* Identity ($I$): $I * A(y, z) = A(y, z)$
* Left Shift ($L$): $L * A(y, z) = A(y + 1, z)$
* Diagonal Boundary Operator ($D$)
* Combined Recursion: $R = L * (I + D * M)$ where $W_{x-1} = R * W_x$


4. **Solved Fixed Point Parameters** (for large $x$):
* $\alpha = \frac{1}{\sqrt{2}} \approx 0.707$
* $\lambda_L = 1 - \frac{1}{\sqrt{2}} \approx 0.293$
* $\lambda_U = \frac{1}{\sqrt{2}} \approx 0.707$
* $m_L = -1 - \frac{1}{\sqrt{2}} \approx -1.707$
* $m_U = -1 + \frac{1}{\sqrt{2}} \approx -0.293$
* $\gamma = \sqrt{2} - 1 \approx 0.414$


5. **Optimal Opening Move Probabilities**:
* Target $r$-position $[x - r, r, 0]$: $\sqrt{2} - 1 \approx 41.4\%$
* Target $s$-position $[x - s, 0, s]$: $2 - \sqrt{2} \approx 58.6\%$



---

### B. Three-Heap Nim

1. **Coordinates**: $[x, y, z]$ represents heap sizes, indexed by sheet $x$.
2. **IN-Sheet Construction**:

$$W_x = \sum_{x'=0}^{x-1} P_{x'} \quad (\text{Logical OR sum})$$


3. **Supermex Operator Algorithm**:
* Set $M * W_x = 0$, $T_x = W_x$, $y = 0$.
* Find smallest $z_s$ such that $T_x(y, z_s) = 0$.
* Set $(M * W_x)(y, z_s) = 1$ and update $T_x(y + t, z_s) = 1$ for $t \ge 0$.
* Increment $y \rightarrow y + 1$ and iterate.


4. **Recursion & Scaling**:

$$W_{x+1} = R * W_x \quad \text{where } R = I + M$$



Exhibits self-similar, fractal geometric patterns scaling linearly with $x$.

---

### C. 3D Wythoff's Game

1. **Moves**: Single-heap reduction (Nim move) OR equal reduction across all 3 heaps (Wythoff move: $[x-k, y-k, z-k]$).
2. **Auxiliary Sheets**:
* $V_x^1$: Instant-N positions from Nim moves $\left( V_x^1 = \sum_{x'=0}^{x-1} P_{x'} \right)$.
* $V_x^2$: Instant-N positions from Wythoff moves $\left( V_x^2(y, z) = P_{x-t}(y-t, z-t) \text{ where } t = \min(y, z) \right)$.
* Total IN-Sheet: $W_x = V_x^1 + V_x^2$.


3. **Vector Recursion Relation**:

$$V_{x+1} = R * V_x \quad \text{where } R = \begin{bmatrix} (I + M_1) & M_2 \\ L_1 & L_2 \end{bmatrix}$$


4. **Geometry**: Displays $V$-shaped rays emanating from the origin in position space, scaling linearly with $x$.
