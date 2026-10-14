# 19. An industrial input dialog with a separate results page

Date: 2026-10-14
Status: accepted, superseding [0015](0015-decimal-alignment-is-structural-because-flet-has-no-tabular-figures.md)

## Context

The first Flet interface put a narrow form on the left and filled a panel on the right after
Calculate. The owner, a mechanical engineer, opened it for the first time and judged it against
the tools engineers actually use, with a screenshot of a classic "Shell and Tube Exchanger
Properties" dialog as the reference. What they saw, in their words, was unaligned, unclear about
what was what, and confusing in colour; results appearing in a side panel felt like a failure.
Looking at the rendered window confirmed each point:

- input boxes started at three different horizontal positions, and the dropdowns used a third
  style outside the grid
- labels wrapped onto two lines while half of the window stayed empty
- the structural decimal alignment of record 0015 rendered with a visible gap inside every
  number, `53 .400`, because the integer and the fraction were separate controls
- the suggested value was painted red, so the reference value looked like the error
- nothing said which water flows through the tubes and which through the shell
- the theme followed the operating system, so the same program was dark on one machine and
  light on the next

## Decision

The interface is laid out like an engineering input dialog.

- **Two steps, one at a time.** A tab bar reads `1 Inputs` and `2 Results`. Calculate opens the
  results page; `Back to inputs` returns. A fixed bar at the bottom holds the status message, the
  back button and Calculate, so the next action is always in the same place.
- **A schematic first.** A drawn shell and tube exchanger names the pool water stream on the
  tube side and the hot water stream on the shell side, with the entered inlet and outlet
  temperatures, and switches to a split head and a return head for two tube passes.
- **Boxed groups with one grid.** Pool water, hot water, tubes, shell and baffles, and design
  assumptions are each a bordered group with a title. Every row is label, value, unit, and,
  where it applies, a grey reference column: the suggested geometry next to the entered one, the
  computed coefficients next to the assumed ones. The value and unit columns have fixed widths,
  so they line up across every row of every group in the same column.
- **Choices are segmented buttons, not menus.** Every choice in this program has two options,
  so both are shown and one is highlighted. Nothing is hidden behind a click.
- **A light, fixed industrial palette.** Grey page, white panels, one steel blue accent for
  actions. Green, amber and red mean only satisfied, attention and failure. Blue and orange
  appear only where they name the two water streams. The theme no longer follows the operating
  system.
- **Numbers are right aligned with a fixed number of decimals per quantity.** One decimal for
  kilowatts, two for temperatures and pressure drops, none for heat transfer coefficients and
  Reynolds numbers, three for ratios. The suggested tube count is a whole tube.
- **Every displayed text starts with a capital letter**, in both languages.
- **Groups reflow, columns do not.** `ResponsiveRow` places the groups two abreast on a wide
  window and stacks them below 768 pixels. Inside a group the column widths stay fixed.

## Alternatives considered and rejected

- **Keeping the structural decimal alignment of record 0015.** Rejected after seeing it
  rendered: the gap between the two halves of a number is a defect a user notices at once.
  Right alignment with fixed decimals is how engineering data sheets present numbers.
- **Keeping the side by side form and results.** Rejected by the owner, and the rendering
  agreed: the form was squeezed into a fixed column while the results fought it for space, and
  a narrow window cut both.
- **Dropdowns for the two option choices.** Rejected: Flet 1.0's `Dropdown` is a Material 3
  menu with a minimum height of about 48 pixels, which broke the row rhythm, truncated
  "Triangular, 30° or 60°", and hid the alternative behind a click.
- **A dark theme, or following the operating system.** Rejected: the owner asked for an
  industrial look, and a program whose appearance depends on the machine it runs on cannot be
  described in one screenshot.
- **`DataTable` for the results.** Still rejected for the reasons in record 0015: its columns
  are measured per table, so two tables never line up with each other or with the groups.
- **A bundled monospace font for the numbers.** Still rejected: right alignment does not need
  one.

## Consequences

Right alignment lines decimal points up within one quantity, where every row has the same number
of decimals, but not across quantities with different precision. That is the data sheet
convention and was accepted deliberately. Decimal points line up only because the default
fonts, Roboto in the browser and Segoe UI on Windows, draw every digit at the same width. Setting
a proportional `font_family` would break that, which is the risk record 0015 named. It is
accepted here because it fails visibly and is a one line revert.

The layout was checked by rendering it, not by reading the code. A small harness starts the web
interface, drives it in headless Microsoft Edge over the Chrome DevTools protocol, clicks
Calculate and captures screenshots at 1600, 1440 and 760 pixels wide, in English and in
Turkish. Two of those captures are in [docs/images](../images/). The harness is not part of the
repository; it is the method that found the clipped schematic at 760 pixels and the nine pixel
offset of a computed value, both now fixed.
