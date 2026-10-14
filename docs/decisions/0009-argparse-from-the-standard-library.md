# 9. argparse from the standard library

Date: 2026-10-14
Status: accepted

## Context

The command line has three subcommands and roughly eight options.

## Decision

`argparse`, from the standard library.

## Alternatives considered and rejected

- **`typer`.** Nicer to write, type hint driven, good help output, shell completion. Rejected:
  it is a dependency, and it brings `click` with it, for a surface this small. The dependency
  budget is a stated requirement and this is the easiest place to honour it.
- **`click`.** Same reasoning.
- **Hand rolled `sys.argv` parsing.** Rejected: argparse is already in the standard library,
  so hand rolling would be more code and worse help text for no benefit.

## Consequences

Option parsing is more verbose than `typer` would be, and there is no shell completion. Neither
costs a user anything here.
