# 8. The manual coefficient iteration is kept

Date: 2026-10-14
Status: accepted

## Context

The tool's central method is that the user assumes tube side and shell side heat transfer
coefficients, reads what the rating step computes from the real geometry, and adjusts the
assumption until the two agree. The 2022 report describes this as "manually iterating the
overall design", and it is the reason the tool exists rather than a limitation of it.

Automating it with a solver would be straightforward.

## Decision

The iteration stays manual. The core evaluates one design case and reports the gap between
assumed and computed coefficients; it does not loop. What is removed is the clerical labour,
not the method: the gap is shown as a percentage, a single action copies the computed value
into the assumption, and `IterationHistory` records the sequence so the convergence is visible
and exportable.

## Alternatives considered and rejected

- **A fixed point or Newton solver that converges the coefficients automatically.** Faster and
  less error prone. Rejected for now on two grounds. It changes what the tool is: the visible
  iteration is the pedagogy, and a converged answer with no visible path hides the sensitivity
  the author explicitly wants a user to feel. And it is a feature nobody asked for, which the
  rule of three says to wait on. The core is shaped so it can be added later without changing
  anything else, because `evaluate_design_case` is a pure function of a design case.
- **Fifty hard coded dropdown values from 2000 to 6900 in steps of 100, as in 2022.** Rejected:
  it is a number, so it gets a number field with validation.
- **A convergence tolerance fixed in code.** `DEFAULT_CONVERGENCE_RELATIVE_TOLERANCE` is one
  per cent, but `has_converged` takes the tolerance as an argument, because what counts as
  converged is a judgement the engineer makes.

## Consequences

Nothing stops a user accepting a design that has not converged. The report says plainly whether
it has.

Agreeing coefficients are not by themselves a finished design: the geometry that was rated must
also be the geometry the sizing suggests. Record
[0020](0020-a-consistent-design-needs-agreeing-coefficients-and-the-suggested-geometry.md) adds
that second condition and explains why the loop is still not automated.
