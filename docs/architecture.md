# Architecture

The current codebase is organized around direct, script-level generators for
specific impartial games. Each maintained generator follows the same broad
shape:

1. Prompt for a display grid size, winner/loser output, and target `x` level.
2. Allocate one or more NumPy boolean sheets.
3. Build the requested level with a game-specific recurrence.
4. Recover the loser sheet with `supermex` when needed.
5. Pass the final bounded sheet to `utils.display.output`.

## Maintained Modules

### `Nim/faster_nim_start.py`

This is the maintained Nim implementation. It models a fixed `x` level of
three-heap Nim as a two-dimensional `y,z` sheet.

- `generate_Wx` iteratively applies the Nim recurrence.
- `supermex` scans each column for the first open `z` value and blocks that row.
- Numba compiles the loop-heavy functions with `@njit`.

### `Chomp/faster_chomp_start.py`

This is the maintained Chomp implementation. It uses a larger internal compute
grid because the recurrence shifts sheet data while advancing levels.

- `generate_Wx` builds the requested Chomp winner sheet.
- `supermex` scans by column and blocks diagonals of constant `z + y`.
- `diagonal` adds the Chomp boundary diagonal from the first loser on the left
  edge.
- `left_shift` shifts the generated structure left by one column.

### `nim_variant/nim_variant_start.py`

This generator handles the Nim variant where a move may remove chips from one
pile or remove the same amount from all piles.

- `A_x` tracks winners produced by ordinary one-pile moves.
- `B_x` tracks winners produced by the all-piles diagonal move.
- `shift` moves the diagonal contribution up and right between levels.
- `supermex` is the same row-blocking operator used by standard Nim.

### `utils/display.py`

This shared helper renders a square boolean sheet with Matplotlib. It gives
small sheets per-cell gridlines and chooses readable tick spacing for larger
sheets.

## Design Notes

- The optimized scripts are the source of truth for current development.
- The non-optimized `nim_start.py` and `chomp_start.py` files are useful as
  historical baselines, but new changes should target the faster modules.
- Game rules currently live directly in each game module. Shared behavior is
  limited to display code.
- If the project later grows into a reusable package, `supermex`, shifting, and
  display concerns are the likely first pieces to extract carefully.
