# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Requires Python 3.11+, NumPy, Numba, and Matplotlib.

## Running a Generator

Each game module is interactive — run it and enter grid size, W/L, and x-level when prompted:

```bash
python -m nim.faster_nim_start
python -m chomp.faster_chomp_start
python -m nim_variant.nim_variant_start
python -m subtract_a_square.subtract_a_square_start
python -m gcd.gcd_start
python -m lcm.lcm_start
python -m euclids_game.euclids_game_start
python -m fibonacci_nim.fibonacci_nim_start
python -m wythoffs_game._3d_wythoff
```

After `pip install -e .`, the three registered console scripts also work:
```bash
faster-nim
faster-chomp
nim-variant
```

## Pre-PR Check

```bash
python3 -m compileall nim chomp nim_variant utils subtract_a_square gcd lcm euclids_game fibonacci_nim wythoffs_game
```

## Architecture

### Core concept: x-level sheets

Every game represents positions as three non-negative integers (x, y, z). The codebase fixes one coordinate (`x`) and renders the remaining two as a 2D boolean grid — the **sheet**. Black = True = the displayed position type (winner or loser).

- **W_x** (instant-winner sheet): positions where a player can move to a loser on a *lower* x-level. W_0 is always blank.
- **L_x** (loser sheet): positions with no winning move. Recovered from W_x via `supermex`.

Sheets are built iteratively: W_x+1 = R(W_x) for a game-specific recursive operator R.

### The supermex operator

`supermex` scans each y-column for the first available z-position (not already a winner, not blocked), marks it as a loser, then blocks future columns from reusing that position. The blocking geometry differs by game:

- **Nim / Nim variant**: blocks the entire z-row.
- **Chomp**: blocks the 45° diagonal where `z + y` is constant.
- **GCD / Euclid / Subtract-a-Square / LCM**: fires blocking *rays* forward along y and z axes at game-specific step sizes.

### Per-module notes

**`nim/faster_nim_start.py`** — canonical Nim. `generate_Wx` ORs `supermex(Wx)` onto Wx once per level. `@njit` compiles both functions.

**`chomp/faster_chomp_start.py`** — Chomp recurrence is `W_x = L(I + DM)W_{x-1}`: apply supermex (M), add boundary diagonal (D), OR with identity (I), then left-shift (L). The internal compute array is padded by `desired_level` columns to absorb the left-shifts without data loss; results are sliced back to `grid_size` before display.

**`nim_variant/nim_variant_start.py`** — splits W_x into two terms: `A_x` (ordinary one-pile moves) and `B_x` (diagonal all-piles move). Update rule: `A_{x+1} = A_x | L_x`, `B_{x+1} = shift(B_x | L_x)`. `shift` moves every entry diagonally up-right by 1 (SA(z,y) = A(z-1, y-1)).

**`subtract_a_square/subtract_a_square_start.py`** — computes the full 3D space `[x, y, z]` in one pass. For each x, looks back at lower L sheets to find W_x, then fires forward blocking rays along y and z at all square offsets to find L_x. Requires `compute_size = max(grid_size, desired_level + 1)`.

**`gcd/gcd_start.py`** — GCD game. Inter-sheet moves subtract multiples of `gcd(y,z)` from x. Intra-sheet supermex propagates blocking rays at variable step sizes `gcd(x, z)` along y and `gcd(x, y)` along z, using step-parameterized accumulators to achieve O(N^3) overall. Precomputes a full GCD lookup table.

**`euclids_game/euclids_game_start.py`** — same structure as GCD but steps are multiples of the pile values themselves (subtract `ky` or `kz` from x, etc.). Supermex fires forward rays at steps of x, y, and z.

**`utils/display.py`** — sole shared module. `output(sheet, is_winner, desired_level)` renders a 2D boolean NumPy array with Matplotlib. Shows per-cell gridlines for grids ≤ 100; auto-scales tick spacing for larger grids.

### Adding a new game

Follow the pattern of any existing `*_start.py`:
1. Implement a `compute_*_space` or `generate_Wx` function (usually `@njit`) that produces W and L sheets.
2. Define a `supermex` variant matching the game's blocking geometry.
3. Write a `main()` that prompts for grid size, W/L, and x-level, computes the appropriate slice, and calls `utils.display.output`.
4. Register the entry point in `pyproject.toml` if needed.

### Historical baselines

`nim/nim_start.py` and `chomp/chomp_start.py` are pure-Python reference implementations kept for comparison. Do not update them for new features.
