# 23. Two packages: calculation and user_interface

Date: 2026-10-14
Status: accepted, supersedes [0013](0013-a-flat-module-layout-rather-than-a-deep-package-tree.md)

## Context

This is the third layout. The original record argued for a flat package; the owner asked for
semantic folders and 0013 recorded that reversal; the owner has now asked for the opposite
again, in more precise terms: as few files and folders as possible, modular work preserved, and
**the main split should be backend against frontend**, because hopping between seven folders
costs more than it buys at this size.

## Decision

Two packages, and the boundary between them is the one that was always load bearing:

    src/pool_heat_exchanger_designer/
      __init__.py          the public API, the one real __init__
      __main__.py
      calculation/         backend: physics, reference data, user files, localization, CLI
      user_interface/      frontend: Flet, and the only place that imports it

- `calculation/` holds flat modules, one per concern. Four small cohesive modules were merged
  in the move: `liquid_water_properties` + `tube_wall_material` became `properties`, and
  `thermal_duty` + `log_mean_temperature_difference` + `overall_heat_transfer_coefficient` +
  `preliminary_sizing` became `thermal`. `design_evaluation` stays its own module because it is
  the one place that knows the order of the calculation steps.
- `language` and `translator` were **not** merged: `message_catalogue` imports `language`, and
  `translator` imports `message_catalogue`, so merging the two ends of that chain creates a
  circular import.
- The two correlation modules were **not** merged: they deliberately define same-named
  functions (`reynolds_number`, `mass_flux_...`) that read correctly only behind their module
  name.
- Every empty `__init__.py` is gone; both subpackages are namespace packages. The launcher
  moved from `user_interface/__init__.py` into `application.py`. `tests/__init__.py` stays,
  because `from tests.conftest import ...` in the regression suite needs `tests` importable as
  a package from the repository root.
- File count: 36 Python files became 24.

Verified the way 0013 prescribes: the gate is green, and the wheel was built, installed into a
throwaway virtual environment and run from outside the repository, which is the only way to
catch a broken `importlib.resources` anchor. The anchor moved to
`pool_heat_exchanger_designer.calculation`, and `importlib.resources.files` resolves it on a
namespace package.

## Alternatives considered and rejected

- **Fully flat with folder-name prefixes** (`thermal_design_evaluation.py`), the owner's first
  sketch. Rejected in favour of the two-package form of the same idea: it puts the nine
  interface files in with the physics, and it turns the enforced flet-import boundary
  (`test_the_calculation_core_never_imports_the_user_interface_library` checks path parts)
  into a naming convention. The owner's stated main split, backend against frontend, is a
  folder boundary by its own definition.
- **Keeping the seven semantic packages.** Rejected by the owner: the folder names carried
  information, but at twenty-odd modules the navigation cost exceeds it.
- **Naming the packages `backend` and `frontend`.** Rejected: honest web vocabulary, but this
  is a desktop and command line tool, and every document in the repository already says
  "calculation core" and "user interface".
- **Merging the three user-file modules into one `design_files.py`.** Rejected for now: at
  roughly 880 lines the merged file would be the kind of file the owner flags as a mess in
  other projects. Three files, one per format, each under 470 lines.

## Consequences

Imports read `pool_heat_exchanger_designer.calculation.thermal` instead of
`pool_heat_exchanger_designer.thermal.preliminary_sizing`. The console script entry point and
the CSV force-include in `pyproject.toml` moved with the modules. Module citations in
`validation.md` were updated. Anyone reading 0013 should read it as history.
