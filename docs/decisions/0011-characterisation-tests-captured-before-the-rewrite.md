# 11. Characterisation tests captured before the rewrite

Date: 2026-10-14
Status: accepted

## Context

Rewriting numerical code from scratch with no reference is how physics gets broken silently.
The 2022 program ran correctly for inputs below 100 °C, so its outputs were worth preserving
as evidence, bugs and all.

## Decision

Before any new code was written, the 2022 `main.py` was driven headlessly through its own
widgets across four design cases spanning both materials, both pass counts, both pitch layouts
and a range of flows, and every intermediate result was captured to
`tests/reference/original_implementation_behaviour.json`. The script that did the capturing is
kept next to it as `how_the_original_behaviour_was_captured.py`.

`tests/test_regression_against_original_implementation.py` then asserts, for every case, that
each quantity is either **identical to twelve significant figures** or **different for a reason
named in the test's own name and proven inside it**. The test that covers the swapped film
coefficients reproduces the 2022 numbers exactly by deliberately re-applying the swap, which
proves the swap is the whole of the difference and nothing else drifted.

## Alternatives considered and rejected

- **Trusting a careful reading of the old code.** Rejected: the swapped film coefficients were
  found by reading, but their effect on the suggested shell diameter was only provable by
  running both.
- **Golden values taken from the 2022 report's figures.** The report's worked example lives in
  slide images rather than text. Rejected as both harder to extract and less complete than
  driving the program.
- **Deleting the old results once the rewrite passed.** Rejected: the reference file is what
  makes the four deliberate changes auditable by someone who was not here.

## Consequences

The reference file and the capture script stay in the repository permanently. They document a
program that no longer exists, which is the point.
