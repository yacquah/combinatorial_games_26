# Paper Notes

The project is motivated by studying finite slices of impartial combinatorial
games through sheets rather than by simulating only individual play lines.

## Shared Ideas

- A position is classified as winning or losing relative to the game rules.
- A fixed `x` level can be represented as a two-dimensional sheet over the
  remaining coordinates.
- Winner sheets are generated recursively from earlier loser information.
- Loser sheets are recovered with a `supermex` operator that finds the first
  available position in each column while marking future positions as blocked.

## Current Translations

### Nim

For standard three-heap Nim, `supermex` blocks rows. Once a column selects a
`z` value, later columns cannot reuse that same row. Repeatedly OR-ing the
current winner sheet with `supermex(W_x)` produces the next instant-winner
sheet.

### Chomp

Chomp changes the geometry of blocking. Instead of blocking rows, the optimized
implementation blocks diagonals where `z + y` is constant. The recurrence then
adds a boundary diagonal and shifts the resulting sheet left to advance the
level.

### Nim Variant

The Nim variant adds a move that removes the same number of chips from all
piles. The implementation separates the winner sheet into two terms:

- `A_x`, for ordinary one-pile moves.
- `B_x`, for the diagonal all-piles move.

The update rule computes the current loser sheet with `supermex(A_x | B_x)`,
adds it into `A_x`, and shifts the diagonal contribution into the next `B_x`.

## Future Work

The current code focuses on exact finite sheet generation and visualization.
Future paper-facing work can build on these scripts by adding:

- tests that compare known small sheets across games,
- saved image or data exports for reproducible figures,
- shared operator modules once the repeated patterns stabilize,
- higher-level experiments around perturbations and asymptotic sheet geometry.
