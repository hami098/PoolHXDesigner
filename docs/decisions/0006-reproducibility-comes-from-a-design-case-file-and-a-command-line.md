# 6. Reproducibility comes from a design case file and a command line

Date: 2026-10-14
Status: accepted

## Context

The author requires that the tool run easily on another machine, that results be reproducible,
and that two runs be comparable. A graphical interface delivers none of those on its own: what
a user typed into sixteen fields is not recorded anywhere, and two screenshots cannot be
diffed.

## Decision

A design case is a TOML file that fully specifies one run, including the assumed coefficients
and the LMTD correction factor. The command line reads it and writes a JSON result with a
stable schema:

    poolhx evaluate examples/olympic_pool_fifty_meter.toml --json-output-path result.json
    poolhx compare first.json second.json

`compare` walks both documents and reports every numeric difference above a tolerance, exiting
non zero when they differ, so it works in a script and in CI. The graphical interface is an
editor for the TOML and a viewer for the JSON, not the system of record.

## Alternatives considered and rejected

- **Saving inputs from the interface in a private format.** Rejected: a format only the
  interface can read cannot be reviewed, version controlled or hand edited.
- **JSON or YAML for the input file.** JSON has no comments and is unpleasant to hand edit;
  YAML needs a dependency and has well known type surprises. TOML reads cleanly and
  `tomllib` is in the standard library.
- **`tomli-w` to write TOML.** Rejected: the schema is fixed and known, so the writer is about
  thirty lines of string formatting. A dependency to format thirty lines fails the dependency
  budget. The round trip is tested rather than assumed.
- **Claiming bit for bit reproducibility across machines.** Not claimed. The arithmetic here is
  plain double precision with no BLAS reductions, so results should agree to the last few bits
  across platforms, but that is not promised in the README, because floating point results from
  numpy can legitimately differ across builds and the author should not assert what cannot be
  guaranteed.

## Consequences

Every input must be expressible in the file, which is why the LMTD correction factor became an
explicit field instead of a constant buried in the code.
