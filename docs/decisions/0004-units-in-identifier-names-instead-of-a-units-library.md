# 4. Units in identifier names instead of a units library

Date: 2026-10-14
Status: accepted

## Context

With no comments available, a reader has no way to tell whether `tube_inner_diameter` is in
millimetres or metres. The 2022 version converted millimetres to metres inside four separate
button handlers, which is both duplication and an easy place for a unit to go missing.

## Decision

Every quantity that crosses a module boundary carries its unit in its name:
`tube_inner_diameter_meters`, `tube_side_inlet_temperature_celsius`,
`heat_transfer_coefficient_watts_per_square_meter_kelvin`. Everything inside the package is SI.
Conversion happens only at the edges, in the user interface and in the design case file.

Variables local to a single function do not carry unit suffixes, because the enclosing
function's name and its typed parameters already fix them. The rule is deliberately about
boundaries, not about every line.

## Alternatives considered and rejected

- **A units library: `pint`, or `astropy.units`.** Real unit safety, real dimensional checking.
  Rejected on three counts: it is a third runtime dependency against an explicit "as few as
  possible"; it makes every formula read as a wrapped quantity rather than as the textbook
  expression a mechanical engineer wants to recognise; and it imposes a performance and
  debugging cost out of proportion to a tool with roughly twenty inputs.
- **`typing.NewType` or `Annotated` aliases per unit.** Lighter than pint and catches some
  mix ups at type check time. Rejected as ceremony at this scale: it adds a vocabulary of
  types without making anything a reader sees clearer than the name already does.
- **Units in a separate table in the documentation.** Rejected: it puts the single most
  dangerous ambiguity in engineering code one file away from the code.
- **Storing engineer friendly units in the design case file, millimetres for diameters.**
  Tempting, since a human hand edits that file. Rejected to keep one single unit convention
  everywhere; the key names say `_meters`, so a hand editor is told what is expected.

## Consequences

Identifiers are long. `line-length` is set to 100 and some call sites wrap across several
lines. That is the accepted price; the alternative is ambiguity in a calculation nobody can
check.
