# 7. Impossible geometry raises, but a standards violation is reported

Date: 2026-10-14
Status: accepted

## Context

Two different kinds of bad input get confused with each other. A tube whose inner diameter
exceeds its outer diameter does not exist. A shell whose diameter to length ratio sits outside
the TEMA window exists perfectly well and may even be what the engineer wants to look at.

The 2022 version treated both the same way, with a `messagebox.showwarning` that the user
dismissed before being shown numbers computed anyway. Worse, several warnings fired and then
execution continued with an undefined variable, so the real failure arrived later as a silent
dead button.

## Decision

- **Physically impossible or thermodynamically impossible input raises** a `DesignError`
  subclass from the constructor, in `__post_init__`. An invalid object never exists.
- **A standards or envelope violation is returned as a `ConstraintCheck`** with the actual
  value, the allowed range, the standard that sets it and whether it passes. The calculation
  still runs. The interface shows the check next to the number it concerns.
- **A correlation applied outside its validated range** is reported the same way, as a boolean
  on the side rating, not as an interruption.

The command line exposes this distinction: a `DesignError` exits 2 with a one line message and
no traceback, an unsatisfied constraint exits 3 only when `--fail-on-unsatisfied-constraint`
is passed.

## Alternatives considered and rejected

- **Raising on standards violations too.** Rejected: it would stop an engineer from exploring
  a design just outside TEMA, which is a legitimate thing to do deliberately.
- **Warnings through the `warnings` module.** Rejected: warnings are easy to miss, hard to
  render in an interface, and carry no structured data about which limit and by how much.
- **Returning a list of error strings.** Rejected: strings cannot be sorted, filtered or
  rendered in a table, and the interface would have to parse prose.

## Consequences

Every unsatisfied check must be renderable, so `ConstraintCheck` carries a unit and a formatted
allowed range rather than only a boolean.
