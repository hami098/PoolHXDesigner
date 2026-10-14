# 20. A consistent design needs agreeing coefficients and the suggested geometry

Date: 2026-10-14
Status: accepted

## Context

The owner tested the iteration by pressing "Apply computed values" and Calculate. The program
reported the design as converged after one click. The exported history showed why:

| iteration | assumed tube / shell | computed tube / shell | entered shell, tubes | suggested shell, tubes |
|---|---|---|---|---|
| 1 | 3000 / 3000 | 1399 / 3202 | 0.900 m, 700 | 0.317 m, 150 |
| 2 | 1399 / 3202 | 1399 / 3202 | **0.900 m, 700** | **0.389 m, 226** |

The computed coefficients depend only on the entered geometry and the flows. The assumed
coefficients only drive the preliminary sizing. Copying the computed values into the
assumptions therefore always closes the coefficient gap in one step, while the geometry that was
rated stays unrelated to the geometry the sizing asks for. "Converged" was true of the
coefficients and false of the design, and the screen said the second.

Calculating an unchanged design also appended a duplicate row to the history.

## Decision

- The core gains `GeometryAgreement`: the suggested and the entered shell inner diameter, tube
  count and baffle spacing, and their largest relative difference. The suggested tube count is
  compared as a whole number of tubes, rounded up.
- `DesignEvaluation.is_consistent()` is true only when the coefficients agree **and** the entered
  geometry is the suggested geometry, both within the existing one per cent tolerance.
- The results page leads with that verdict and two separate check lines, one per condition,
  each with its own button: "Use computed coefficients" and "Use suggested geometry". The same
  two buttons sit on the inputs page beside the grey computed and suggested columns.
- The command line report and the JSON record state both conditions.
- `IterationHistory.record` ignores an evaluation of the design case it recorded last.

## Alternatives considered and rejected

- **Redefining `has_converged` to include the geometry.** Rejected: it would change the meaning
  of a column in every exported history without changing its name. `has_converged` still means
  the coefficients agree; consistency has its own name.
- **One button that copies both the coefficients and the geometry.** Rejected. Pressed
  repeatedly it is a fixed point solver, which record 0008 decided against. And it does not
  settle: copying both on every step, starting from the example case, gives tube counts of 150,
  226, 75, 96, 53, 60 and 46 over successive iterations while the computed tube side coefficient
  climbs past 16 000 W/m²K. Nothing in the design stops the exchanger shrinking.
- **A separate, looser tolerance for the geometry.** Rejected as an unexplained second number.
  The suggested geometry can be entered exactly with one click, so one per cent is reachable.

## Consequences

The verdict is now truthful, and it will often say "not consistent yet" where the old screen
said "converged". That is the honest state of the method.

The loop has an open engineering question, recorded for the owner rather than answered here:
what stops the design from shrinking. A tube side velocity limit or an allowable pressure drop
far below the present 6 bar envelope would; which one, and at what value, is a design decision
for a mechanical engineer, not a software default.
