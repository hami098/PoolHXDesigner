# 25. pyproject.toml is the single source of the version

Date: 2026-10-15
Status: accepted

## Context

The owner asked for versioning to be handled with care. The cautionary example is close by: in
the owner's okey project the version lives in both `package.json` and `desktop.config.json` and
is synchronised by hand. This project's version appears in four places — the wheel, the exe
metadata, `poolhx --version` and the file people read — and they must never drift.

## Decision

The version is written once, as `version = "2.0.0"` in `[project]` in `pyproject.toml`.
Everything else derives from it:

- the wheel and sdist take it through hatchling;
- the Windows executable takes it through `flet build`, which reads `project.version` and
  passes it to Flutter as `--build-name`, so the exe's ProductVersion and FileVersion match
  (verified on the built exe);
- `poolhx --version` prints it through `program_version()`, which reads the adjacent
  `pyproject.toml` when running from a source checkout (so an editable install that was not
  reinstalled after a bump still reports the truth) and falls back to the installed
  distribution's metadata otherwise;
- `test_the_version_flag_prints_the_version_declared_in_pyproject` fails if the flag and the
  file disagree.

Releasing a new version therefore means editing one line, and tagging the commit (`v2.0.0`)
once the owner starts pushing.

## Alternatives considered and rejected

- **A `__version__` constant in the package.** Rejected: it is a second place to bump, and
  `flet build` reads `project.version`, so the constant and the exe would drift exactly the way
  okey's two files do.
- **A hatchling dynamic version read from the code.** Rejected: `flet build`'s
  `get_pyproject("project.version")` reads the TOML text, sees a dynamic field as absent, and
  the exe would silently lose its version.
- **Deriving the version from git tags (setuptools-scm style).** Rejected for now: the
  repository has no tags and no commits from the rewrite yet, the owner commits by hand, and it
  would add a build dependency to answer a question one static line answers.

## Consequences

The packaged desktop app has no `--version` flag, because its entry point opens the window
directly; its version lives in the exe file properties instead. Everything else answers
consistently from one line.
