# 1. src layout and a spelled out package name

Date: 2026-10-14
Status: accepted

## Context

The 2022 version was a single `main.py` at the repository root that read `Water.csv` from the
current working directory. Running it from any other directory failed.

## Decision

The importable code lives in `src/pool_heat_exchanger_designer/`. The property table ships
inside the package and is located with `importlib.resources`, not with a relative path.

## Alternatives considered and rejected

- **A flat package at the repository root.** Simpler, one less directory. Rejected because a
  root level package is importable from the repository directory whether or not it is
  installed, so tests can pass against the source tree and still fail for a user who installs
  the wheel. The src layout makes that failure impossible to miss.
- **Keeping the short name `poolhx` as the package name.** Rejected: the package name is read
  far more often than it is typed, and the author does not want abbreviations. `poolhx`
  survives only as a convenience alias for the console script, where a human types it.
- **Reading the property table with a path relative to `__file__`.** Works today, breaks
  inside a zip import or a frozen build. `importlib.resources` is the supported mechanism.

## Consequences

Tests need `src` on the path, which `pyproject.toml` sets through
`[tool.pytest.ini_options] pythonpath`. The data file needs an explicit `force-include` entry
in the wheel configuration.
