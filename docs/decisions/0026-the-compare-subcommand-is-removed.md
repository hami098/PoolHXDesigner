# 26. The compare subcommand is removed

Date: 2026-10-15
Status: accepted

## Context

`poolhx compare` diffed two JSON results with a relative tolerance. It existed to make run to
run comparison a first class feature (0006). The owner, trimming the project before
publication, asked for it to go: it was roughly 250 lines across the command line module, eight
catalogue messages in two languages, and three tests, for a job any diff tool performs on the
JSON that `evaluate --json-output-path` already writes.

## Decision

The subcommand, its helpers (`compare_result_dictionaries`, the recursive walker, the JSON
reader), exit code 4, the eight catalogue messages and the three tests are deleted. A new test,
`test_two_runs_of_the_same_design_case_write_identical_json`, keeps the reproducibility claim
honest: the same design case written twice produces byte-identical JSON.

## Alternatives considered and rejected

- **Keeping it.** Rejected by the owner: the tolerance-aware diff was the only thing a plain
  diff tool cannot do, and byte-identical output on the same machine makes a plain diff
  sufficient for the actual use.
- **Moving it to a separate script.** Rejected: a script nobody asked for is the same code in a
  worse place.

## Consequences

What 0006 says about `compare` is historical. The JSON output and its deliberate
English-in-any-language stability remain; they are the diffable record.
