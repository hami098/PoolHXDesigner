# 17. Live validation, but an explicit Calculate action

Date: 2026-10-14
Status: accepted

## Context

The 2022 interface had twenty three "Send" buttons, one per input. Each read its field, parsed
it, range checked it, and wrote a module level global. That was not a design choice: the buttons
existed because the architecture had nowhere else to put the value. Replacing the global data
bus with an explicit design case object removes the reason for all twenty three.

That leaves the opposite question: with nothing to press, should the results simply recompute as
the user types?

## Decision

Two different things happen at two different times.

- **Validation is live.** Every keystroke reparses and range checks that one field and sets
  Flet's built-in inline `error` slot. A readiness line names every field still to fix, so a
  user never hunts for what is blocking them.
- **Calculation is explicit.** One Calculate button, and Enter in any field does the same thing.

The reason is that a run is a thing in this tool, not a side effect. It is recorded in the
iteration history, it is what gets exported, and it is what `poolhx compare` compares. Numbers
flickering mid-keystroke would make the results feel like a readout rather than a result, and
would record meaningless intermediate iterations.

## Alternatives considered and rejected

- **Recompute on every change, debounced.** Rejected for the reasons above, and because a
  partially typed field is a different thing from a changed design.
- **Recompute on blur rather than on a button.** Rejected: it makes the moment of calculation
  depend on where the user clicks next, which is exactly the kind of invisible rule the 2022
  README had to apologise for.
- **Disabling sections until their inputs are complete.** Rejected: greying out a section tells
  a user they cannot proceed without telling them why. The readiness line names the missing
  field instead.
- **Modal dialogs for errors, as in 2022.** Rejected. A dialog interrupts, carries no structured
  data, and in the 2022 program was routinely dismissed before the wrong number was displayed
  anyway. An impossible design is reported on the readiness line; a correlation used outside its
  validated range is reported as a badge beside the number it concerns.

## Consequences

A user can press Calculate on a design that has not converged, and on one that violates TEMA.
Both are legitimate things to want to look at, and both are stated plainly on screen.
