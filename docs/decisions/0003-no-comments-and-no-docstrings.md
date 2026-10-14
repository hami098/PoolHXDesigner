# 3. No comments and no docstrings

Date: 2026-10-14
Status: accepted

## Context

The author's instruction was explicit: no comment lines. Intent must come from file names and
function names, with no abbreviations, so that a reader who knows nothing can say both "he did
this for this reason, and it is sensible" and "he did not do this, and that is also sensible".

Engineering code resists this in three specific places. A name cannot carry a unit, it cannot
carry a literature citation, and it cannot carry the reason something was *not* done.

## Decision

No `#` comments and no docstrings anywhere in `src/` or `tests/`. The three things names
cannot carry are moved to places built for them:

- **Units** go into the identifier itself, see record 0004.
- **Literature citations** go into `docs/validation.md`, keyed by function name, alongside the
  test that proves each formula is still in use. Module names carry the correlation names too:
  `tube_side_correlations`, `shell_side_correlations`.
- **Rejected decisions** go into these records.

Test names are full sentences and carry the specification, for example
`test_the_shell_side_pressure_drop_is_exactly_half_the_original_which_omitted_the_factor_two`.

## Alternatives considered and rejected

- **No comments but keep short docstrings.** The conventional reading of the instruction, and
  defensible: a docstring is a runtime object and part of the public API rather than a comment.
  Rejected because the instruction was unambiguous, and because moving citations into a single
  validation document produces something a docstring cannot: one page a reviewer can read next
  to the textbook. The cost is that `help()` is empty, which matters little for a tool nobody
  imports from a REPL.
- **A single header comment per module.** Rejected: it decays into the documentation nobody
  updates, which is the failure mode the instruction is aimed at.
- **Type hints only, no prose anywhere at all.** Rejected: types cannot express "this is Kern's
  correlation and it is only valid between Re 2e3 and 1e6". Dropping that would make the
  physics uncheckable.

## Consequences

`ruff` has the `D` rules disabled so the linter does not demand docstrings. `docs/validation.md`
is now load bearing: if a correlation changes and that file is not updated, the physics becomes
untraceable. The test that names each correlation is the backstop.
