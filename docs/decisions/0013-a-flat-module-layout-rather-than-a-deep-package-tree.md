# 13. Semantic packages, replacing the flat module layout

Date: 2026-10-14
Status: superseded by [0023](0023-two-packages-calculation-and-user-interface.md), which itself
superseded the flat layout originally recorded here

## Context

This record originally argued for a flat package of fourteen modules. The reasoning was that
Parnas's criterion is satisfied by a module hiding one changeable decision, that a flat
namespace of fourteen modules averaging sixty lines is navigable without a map, and that the
rule of three says to wait before grouping.

The project owner has since asked for folders grouped semantically, by meaning and by how the
program works. That is their call to make, and this record is rewritten rather than deleted so
the reversal is visible.

## Decision

One level of semantic packages. Each folder still hides one changeable decision; the folder
boundary now also tells a reader what kind of thing is inside before they open anything.

    src/pool_heat_exchanger_designer/
      design_errors.py                 the error hierarchy, used from everywhere
      command_line_interface.py        argparse, the headless entry point
      properties/                      where reference data comes from, and interpolation
        liquid_water_properties.py
        liquid_water_properties_table.csv
        tube_wall_material.py
      geometry/                        how the exchanger is described, and what is possible
        exchanger_geometry.py
      correlations/                    which published correlation is used on each side
        tube_side_correlations.py
        shell_side_correlations.py
      thermal/                         the calculation, and the order its steps run in
        thermal_duty.py
        log_mean_temperature_difference.py
        overall_heat_transfer_coefficient.py
        preliminary_sizing.py
        design_evaluation.py
      standards/                       which external limits apply, and what they are
        design_standard_limits.py
      design_files/                    everything that reads or writes a file the user keeps
        design_case.py
        design_report.py
        iteration_history.py
      localization/                    every user facing string, in every language
        language.py
        message_catalogue.py
        translator.py
      user_interface/                  presentation, the only place that imports Flet

`design_errors.py` and `command_line_interface.py` stay at the package root because they are
used from everywhere and belong to no single concern. Imports remain absolute throughout.

## Alternatives considered and rejected

- **Keeping the flat layout.** Its argument is preserved above and is not wrong. Rejected
  because the owner reads this code and finds the grouping clearer, and because the folder names
  now carry information that previously existed only in a table in a decision record.
- **Naming the file-handling package `io`.** Rejected: it shadows a standard library module, so
  `from . import io` would be a trap. `design_files` says what the files are.
- **Two levels of nesting, for example `properties/water/`.** Rejected as ceremony: there are
  three property modules, not thirty.
- **A facade `__init__.py` per package re-exporting everything.** Rejected. Each new
  `__init__.py` is empty, because nothing imports through the subpackage; callers name the
  module they want. Writing a facade nobody calls is the premature abstraction YAGNI warns about.
- **A class per correlation, `GnielinskiCalculator` and the like, to satisfy SOLID literally.**
  Still rejected: a stateless single-method class is a function wearing a costume. Single
  responsibility is honoured at module level, as Parnas intended, and classes are used where
  they earn their place, as frozen value objects that validate their own invariants.
- **Applying the Liskov substitution principle.** Still rejected as having nothing to govern:
  there is no inheritance hierarchy in this design apart from the error classes, which add no
  behaviour. Inventing a base class to have somewhere to apply the principle would be the
  opposite of its intent.

## Consequences

Seven subpackages and one more `__init__.py` each. Every import line is longer:
`pool_heat_exchanger_designer.thermal.design_evaluation` rather than
`pool_heat_exchanger_designer.design_evaluation`.

`thermal/design_evaluation.py` remains the only module that knows the order of the calculation
steps, so it is still the one place that changes when a step is added. That was the point of the
original decomposition and it survives the move.

The move was verified by building the wheel, installing it into a throwaway virtual environment
and running the console script from a directory outside the repository, which is the only way to
catch a broken `importlib.resources` anchor for the property table. The anchor had to change
from the package root to `pool_heat_exchanger_designer.properties`, and the
`force-include` entry in `pyproject.toml` with it.
