# 22. A root run script gives npm style commands

Date: 2026-10-14
Status: accepted

## Context

The owner's other projects are JavaScript: one short command (`npm run dev`) starts the dev
server in the browser with errors visible, and `npm run build` produces the artifact. Here the
equivalent was four lines of environment setup pasted from the README. The owner asked for the
npm experience, typed without the `.\` prefix, and for platform builds (`run build windows`).

## Decision

One PowerShell script at the repository root, `run.ps1`, with a `run.cmd` shim, plus a `run`
function in the owner's PowerShell profile (`$PROFILE.CurrentUserAllHosts`) so plain
`run <task>` works in any shell without `.\`. The profile function falls back to `npm run` in
folders that have a `package.json` instead, so the same word drives the JavaScript projects.

- `run dev` serves the interface in the browser with `FLET_LOG_LEVEL=info`, so every traceback
  and the serving address land in the terminal.
- `run test` runs pytest.
- `run check` runs the whole gate: pytest, ruff check, ruff format --check, mypy.
- `run build` builds the wheel and sdist into `dist/` with `python -m build`.
- `run build windows` builds the Windows desktop app with `flet build windows` (installing
  `flet-cli` on demand; on first use Flet asks to install its pinned Flutter SDK).
- `run build linux` and `run build mac` refuse with the reason: Flet builds a platform's app
  only on that platform, and this machine is Windows.
- `run desktop` starts the built desktop executable and streams its Python log into the
  terminal until the window is closed. The packaged app writes stdout and stderr to a
  `console.log` under `%LOCALAPPDATA%\<company>\pool-heat-exchanger-designer\`; without this
  task an error in the packaged app is only visible inside the app window. The owner asked for
  the builds to be testable by hand, in their own control, and this is that handle.

On first use the script creates `.venv`, installs the project editable with both interface
extras, and installs the development tools. The manual commands in the README remain the
canonical, cross platform route; the script is Windows convenience on top.

`flet build` needs a flat entry file, so `src/main.py` (three lines, launches the desktop
interface) exists for the packager, pointed at by `[tool.flet.app] path = "src"`. It is not
part of the wheel or sdist. `[tool.flet] company = "Hami Bahadir Bilir"` replaces flet's
"Your Company" placeholder in the executable metadata and in the log folder path.

## Alternatives considered and rejected

- **A `Makefile`.** Rejected: `make` is not installed on Windows, and this project is developed
  on Windows.
- **`taskipy` or `poethepoet`.** Rejected: a runtime-adjacent dependency whose whole job is to
  run four commands that a fifty line script runs; the project just removed dependencies that
  were lighter than their justification.
- **A `package.json` with npm scripts.** Rejected: it would literally provide `npm run dev`,
  but a `package.json` in a pure Python repository misleads every reader and every tool that
  sees it.
- **Adding the repository root to `PATH` so `run` resolves.** Rejected: `run` is a generic name
  and the owner has forty repositories; a profile function that dispatches on the current
  folder does the same with no collisions.
- **Hot reload through `flet-cli`'s `flet run`.** Rejected for now: the interface restarts in
  about two seconds with `run dev`. Worth revisiting if interface work becomes the daily
  activity.
- **Documentation only, no script.** What existed; the owner asked for better.

## Consequences

Two small files at the root plus one profile function on this machine. The script duplicates
nothing from `pyproject.toml`: tool configuration stays there, the script only invokes the
tools. CI or another machine can keep using the README commands unchanged.

Verification status: `run dev`, `run test`, `run check` and `run build` were each run and work;
plain `run test` was verified in a fresh shell. `run build windows` first stopped at Flutter's
native toolchain; with the owner's approval the machine was set up on 2026-10-15 — Windows
Developer Mode enabled (registry `AllowDevelopmentWithoutDevLicense`), and the missing
`Microsoft.VisualStudio.Component.VC.CMake.Project` added to the existing VS Build Tools (the
MSVC compiler and Windows 11 SDK were already present; Flutter's doctor lists its whole
requirement set when any piece is missing).

The first completed build opened on an error: `require_the_client_package` demanded
`flet_desktop`, which a packaged app neither ships nor needs, because the Flutter host is the
desktop client. The guard now steps aside when `FLET_PLATFORM` is set, which is how Flet's own
`app.py` detects an embedding host, and
`test_a_packaged_desktop_app_starts_without_the_desktop_client_package` pins the behaviour.
After the fix, `build/windows/pool-heat-exchanger-designer.exe` was started and its window
title became "Pool Heat Exchanger Designer", which only `DesignerApplication.build` sets — the
real interface loads, not an error screen.
