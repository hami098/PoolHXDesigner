# 10. One pitch layout control instead of two

Date: 2026-10-14
Status: accepted

## Context

The 2022 interface exposed the tube layout twice, through two independent controls. A radio
pair chose between "90° or 45°" and "30° or 60°", which set the tube layout constant `CL` used
in preliminary sizing. A separate dropdown chose between "Square Pitch" and "Triangular Pitch",
which selected the shell side equivalent diameter formula.

These are the same physical fact. A 90° or 45° arrangement *is* a square pitch; 30° or 60° *is*
triangular. Because the controls were independent, the interface permitted a design that used
the square equivalent diameter with the triangular layout constant, which is not a design at
all.

## Decision

One `PitchLayout` enumeration with two members, `SQUARE` and `TRIANGULAR`. Each member carries
both its tube layout constant and its tube angles, so the two uses cannot disagree. The
interface exposes one control.

## Alternatives considered and rejected

- **Keeping both controls and validating that they agree.** Rejected: a validation rule that
  forbids three of four combinations is a sign the two controls should be one.
- **Treating 45° as distinct from 90°, and 60° from 30°.** Rejected as unsupported by the
  implementation: the equivalent diameter formulas and the layout constants in the source
  distinguish only square from triangular, so inventing four options would promise a
  resolution the physics here does not have. The angles are kept on the enumeration as
  labels, so the interface can still show the familiar wording.

## Consequences

A 2022 design case that used an inconsistent pair cannot be expressed any more, which is the
intent. The regression suite only ever used consistent pairs.
