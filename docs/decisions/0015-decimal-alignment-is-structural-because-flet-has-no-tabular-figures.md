# 15. Decimal alignment is structural, because Flet has no tabular figures

Date: 2026-10-14
Status: superseded by [0019](0019-an-industrial-input-dialog-with-a-separate-results-page.md)

Kept as written. Once rendered, the split number showed a visible gap between its integer and
its fraction, and the owner rejected the layout it belonged to. Record 0019 explains what
replaced it and which of the arguments below still hold.

## Context

The author's requirement is a sterile, strictly aligned numeric panel. Engineers read a column
of numbers by scanning the decimal point, so the decimal points have to line up.

The normal answer is the OpenType `tnum` feature, which makes every digit the same width.
Flet 1.0.4 cannot do this: `TextStyle` has exactly eighteen fields and none of them is
`font_features` or `font_variations`. This was confirmed by listing the dataclass fields of the
installed package.

A second constraint compounds it: Flet's web mode renders with CanvasKit, where system fonts do
not resolve. A monospace font would have to be shipped as a static `.ttf` asset.

## Decision

Alignment is structural rather than typographic. Each number is formatted to a fixed number of
decimals and then split at the decimal point. The integer part goes into a fixed width container
aligned right; the fractional part, with its leading point, goes into a fixed width container
aligned left. The decimal point therefore sits exactly on the boundary between two containers,
in every row, in any font.

Explicit `width` is the only Flet layout primitive that gives a tight constraint, so every cell
in the form and the result panels carries one.

## Alternatives considered and rejected

- **Bundling a monospace static `.ttf` in an assets directory.** Would also work. Rejected
  because it adds a binary asset and a font licence to a project whose stated goal is as few
  moving parts as possible, and because the structural approach is font independent, so it
  cannot be broken by a future theme change.
- **Relying on the default font happening to have equal width digits.** Roboto mostly does.
  Rejected as an accident rather than a decision: it would break silently the first time anyone
  sets `font_family`.
- **`expand=N` for the column widths.** Rejected after reading Flet's Dart layer: `expand`
  compiles to Flutter's `Expanded(flex:)`, which divides only the space left over after fixed
  siblings, so two rows with differently sized neighbours get different column widths. It
  drifts, which is exactly the failure the requirement forbids.
- **`DataTable` for the input grid and the result panel.** Rejected: its columns are
  content measured per table, so a table aligns with itself but never with a second table or
  with the form. It is used for the iteration history, where self alignment is all that is
  needed, and nowhere else.
- **`ResponsiveRow`.** Rejected: it allocates a fraction of a twelve column virtual grid keyed
  to the parent width, so column boundaries move with the window. Wrong for a fixed numeric
  form.

## Consequences

Every displayed number costs two controls instead of one, and the column widths are constants in
`sterile_theme`. Changing a column width is a one line change in one file, which is the point of
keeping them there.
