# Combinatorial Games 2026

This repository contains Python experiments for generating finite two-dimensional
winner and loser sheets for impartial combinatorial games. The current maintained
work centers on optimized sheet generators for Nim, Chomp, and a Nim variant,
plus a shared Matplotlib display helper.

## Main Code

- `Nim/faster_nim_start.py`: optimized three-heap Nim sheet generator using
  NumPy arrays and Numba-compiled `supermex` logic.
- `Chomp/faster_chomp_start.py`: optimized Chomp sheet generator using
  diagonal blocking, level padding, and Numba-compiled loops.
- `nim_variant/nim_variant_start.py`: Nim variant where a move can remove chips
  from one pile or remove the same number from all piles.
- `utils/display.py`: shared plotting helper for rendering boolean sheets as
  black-and-white grids.

The older `Nim/nim_start.py` and `Chomp/chomp_start.py` files are kept as
historical baseline implementations. For new work, use the `faster_*` versions
and the Nim variant module.

## Setup

Use Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

The project depends on:

- NumPy for boolean sheet storage and array operations.
- Numba for compiling the performance-critical loops.
- Matplotlib for displaying the generated sheets.

## Running The Generators

Each maintained generator is interactive. Run a module, then enter:

1. the grid size to display,
2. whether to show winners or losers with `W` or `L`,
3. the target `x` level.

```bash
python -m Nim.faster_nim_start
python -m Chomp.faster_chomp_start
python -m nim_variant.nim_variant_start
```

If the project is installed with `pip install -e .`, these console commands are
also available:

```bash
faster-nim
faster-chomp
nim-variant
```

## How The Sheets Work

The scripts compute a fixed `x`-level sheet and render the remaining two
coordinates as a square grid. A `True` cell is displayed as a black square.

- Nim uses a row-blocking `supermex`: each column selects the first available
  `z` value, then blocks that row for later columns.
- Chomp uses a diagonal-blocking `supermex`: selected positions block diagonals
  of constant `z + y`, then a diagonal boundary and left shift generate the next
  level.
- The Nim variant splits the recurrence into `A_x` and `B_x`, where `B_x`
  tracks the extra diagonal move that removes the same amount from all piles.

## Project Layout

```text
.
├── Chomp/
│   ├── chomp_start.py
│   └── faster_chomp_start.py
├── Nim/
│   ├── nim_start.py
│   └── faster_nim_start.py
├── docs/
│   ├── architecture.md
│   └── paper_notes.md
├── nim_variant/
│   ├── nim_variant.md
│   └── nim_variant_start.py
├── utils/
│   └── display.py
├── CONTRIBUTING.md
└── pyproject.toml
```

## Quick Check

Before opening a pull request, run:

```bash
python3 -m compileall Nim Chomp nim_variant utils
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the Git workflow used by the team.
