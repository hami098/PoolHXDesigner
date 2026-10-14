# 24. The 2022 copy is removed, and git history is the archive

Date: 2026-10-14
Status: accepted

## Context

The repository carried the 2022 program as a browsable copy in
`docs/legacy-2022-implementation/` (`main.py`, `Water.csv`, `ReadMe.txt`, a screenshot). The
owner is about to push to GitHub and wants the repository clean: the old state is reachable
through git history anyway, at commit `067f66e`.

## Decision

The folder is deleted. What each part now relies on:

- **The 2022 source**: `git show 067f66e:main.py`, `git show 067f66e:Water.csv`.
- **The regression proof**: unchanged. The 36 regression tests read
  `tests/reference/original_implementation_behaviour.json`, which stays in the repository,
  together with the capture script that produced it. Re-running the capture requires restoring
  the two files from `067f66e` first; `validation.md` says so.
- **The README**: points at the commit instead of the folder.

Two other `docs/` files the owner explicitly keeps, although nothing references them:
`good-coding-principles.png` and `time-complexity.jpg`. They state the owner's engineering
philosophy.

## Alternatives considered and rejected

- **Keeping the browsable copy.** Rejected by the owner: a published repository should not
  carry its own predecessor as dead weight when version control already does that job.
- **Also deleting `tests/reference/`.** Rejected: that JSON is not a legacy copy, it is the
  data of the living regression suite. Deleting it deletes the proof that the physics matches
  the 2022 program, including the four documented corrections.
- **Moving the 2022 copy to a separate archive branch.** Rejected as ceremony: the commit
  already exists on this branch's history.

## Consequences

About 500 KB and four files leave the working tree. The byte for byte reproducibility claim
survives through the JSON; re-capturing it now takes one extra `git show` step.
