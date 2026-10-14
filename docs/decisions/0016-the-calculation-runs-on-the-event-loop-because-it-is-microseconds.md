# 16. The calculation runs on the event loop, because it takes microseconds

Date: 2026-10-14
Status: accepted

## Context

Flet 1.0 changed its threading model. In 0.28 each synchronous event handler ran on its own
thread, so blocking code did not freeze the interface. In 1.0 handlers run on the application's
event loop, and `page.run_thread` exists precisely so that blocking work can be moved off it.

The obvious conclusion is that the Calculate button should use `page.run_thread`.

## Decision

It does not. `evaluate_design_case` is a few hundred floating point operations and two
`numpy.interp` calls on a thirty three row table. It completes in well under a millisecond;
the entire test suite, which evaluates design cases many times over, runs in about half a
second. Moving that onto a worker thread would add a thread hop, a state synchronisation
problem between the worker and the controls, and a reader's question of what exactly is slow —
all to avoid a delay no one can perceive.

## Alternatives considered and rejected

- **`page.run_thread` for the Calculate action anyway, as defensive practice.** Rejected as
  cargo cult. The guidance is sound for a genuinely blocking operation; applying it here would
  be following advice instead of measuring. This record exists so the omission reads as a
  decision rather than an oversight.
- **A progress indicator while calculating.** Rejected for the same reason: it would flash for
  less than a frame.

## When this should be revisited

If the automatic convergence solver that record 0008 defers is ever added, the loop could run
long enough to matter, and the Calculate action should move to `page.run_thread` at that point.
The file picker operations already run through `page.run_task`, because those genuinely wait on
the user.
