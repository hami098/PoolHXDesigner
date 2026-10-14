# 27. The 2022 regression apparatus is removed

Date: 2026-10-15
Status: accepted, supersedes [0011](0011-characterisation-tests-captured-before-the-rewrite.md)

## Context

The rewrite carried a characterisation suite: four design cases captured from the 2022 program
(`tests/reference/original_implementation_behaviour.json`, with the capture script beside it)
and 36 regression tests pinning every quantity to twelve significant figures. It did its job —
it caught the four defects recorded in `validation.md` and guarded the physics through the
restructurings. With the repository about to be published, the owner asked for the tie to the
legacy program to be cut entirely.

## Decision

`tests/reference/` and `test_regression_against_original_implementation.py` are deleted, along
with the conftest fixtures that only they used. `tests/__init__.py` goes with them: it existed
only so the regression module could `from tests.conftest import ...` (0023), and nothing else
needs it. The mypy exclusion and ruff per-file-ignores for `tests/reference/` leave
`pyproject.toml`.

What remains of the 2022 story: the source at git commit `067f66e`, and the four corrections
written up in `validation.md`, now as history rather than as executable proof.

## Alternatives considered and rejected

- **Keeping the suite.** The earlier position (0011, and the resistance recorded in 0024), and
  not wrong: executable proof beats prose. Rejected by the owner: the proof was needed while
  the physics was being rewritten and restructured; both are done, the unit tests now carry the
  guarding, and a published repository should not keep driving a program it no longer contains.
- **Keeping only the JSON as data.** Rejected: data without the tests that read it is dead
  weight, and data without the script that made it is unexplainable.

## Consequences

The test count drops by the 36 regression tests plus the per-file standards tests of the
deleted files. A future numerical change loses its strongest safety net; `validation.md` and
the remaining unit tests are the guard now, so deliberate changes must be argued there rather
than proven against 2022.
