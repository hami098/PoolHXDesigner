# Coding standards

What this repository actually does, and what was attended to while writing it. Every claim here
is checkable against the code, and most of them are enforced by a test rather than by goodwill.

## Naming

| Thing | Convention | Example from this repository |
|---|---|---|
| package | `lower_snake_case`, a noun naming a concern | `calculation`, `user_interface` |
| module | `lower_snake_case`, says what it holds | `shell_side_correlations.py` |
| class | `CapWords`, a noun | `TubeBundleGeometry`, `ConstraintCheck` |
| function | `lower_snake_case`, verb or noun phrase that names the result | `kern_pressure_drop_pascal` |
| constant | `UPPER_SNAKE_CASE` | `TEMA_LOWEST_PITCH_RATIO` |
| private | leading underscore | `_rate_shell_side`, `_value_line` |
| test | `test_` plus a full sentence | `test_the_shell_side_pressure_drop_is_exactly_half_the_original_which_omitted_the_factor_two` |

**No abbreviations.** `tube_inner_diameter_meters`, not `d_in` or `did`. The 2022 version used
`did`, `dod`, `Dsd` and `TColdInd`; two of those differ from a neighbouring variable by one
letter, and one reads as an English verb. The cost of the rule is long lines; the benefit is
that no reader has to guess.

**Units in names at module boundaries.** Every quantity crossing a module boundary carries its
unit: `tube_side_inlet_temperature_celsius`, `heat_duty_watts`,
`heat_transfer_coefficient_watts_per_square_meter_kelvin`. Variables local to one function do
not, because the enclosing function's name and its typed parameters already fix them. The rule
is about boundaries, not about every line.
`test_public_dataclass_fields_that_carry_a_physical_quantity_name_their_unit` walks every public
dataclass and fails on a `float` field whose name carries no unit, unless the class carries its
unit in a `unit` field — which `ConstraintCheck` does, because the quantity it holds changes
from check to check.

Decision records: [0004](decisions/0004-units-in-identifier-names-instead-of-a-units-library.md).

## No comments, no docstrings

There are zero of either under `src/` and `tests/`. This is not a style preference that decays;
`test_no_source_file_carries_a_comment` tokenises every source file and fails on a single
`COMMENT` token, and `test_no_source_file_carries_a_docstring` walks the AST and fails on any
module, class or function with one.

The "why" lives where it can be maintained:

| Kind of "why" | Where it lives |
|---|---|
| which correlation, from which source, valid over what range | [validation.md](validation.md) |
| why a design choice was made, and what was rejected | [decisions/](decisions/0000-index.md) |
| what a function is supposed to do | its name, and the test that names the behaviour |
| units | the identifier |

The cost is that `help()` is empty. Nothing in this project is imported from a REPL, so that
cost is not paid by anyone.

Decision record: [0003](decisions/0003-no-comments-and-no-docstrings.md).

## Folder layout

Two packages, and the boundary between them is the design:

| Folder | The decision it hides |
|---|---|
| `calculation/` | everything with no screen: physics, reference data, user files, the command line |
| `user_interface/` | everything with a screen: presentation, and the only place that imports Flet |

Inside `calculation/` the modules are flat, one per concern: `properties`, `geometry`, the two
correlation modules, `thermal`, `design_evaluation` (the one module that knows the order of the
calculation steps), `standards`, the three user-file modules, the three localization modules,
`design_errors` and `command_line_interface`.

There are no empty `__init__.py` files; both packages are namespace packages, and the one real
`__init__.py` at the package root is the public API.

Decision record: [0023](decisions/0023-two-packages-calculation-and-user-interface.md), which
records that this is the third layout, after a flat one and a seven-package semantic one.

## Types

`mypy` runs in `strict` mode over `src` and `tests`, with `warn_unreachable`. With no docstrings,
the signature is the contract, so it has to be complete.

- **Frozen dataclasses as validated value objects.** `TubeGeometry`, `ShellGeometry`,
  `TubeBundleGeometry`, `LiquidWaterProperties`, `ConstraintCheck`, `IterationRecord`. All
  `frozen=True`, most `slots=True`.
- **Guard clauses in `__post_init__`.** An invalid object never exists. A tube whose inner
  diameter is not smaller than its outer diameter cannot be constructed.
- **`typing.Protocol` as a seam.** `LiquidWaterPropertySource` declares
  `at_temperature_celsius`. The physics depends on that, not on the table file, which is why a
  correlation can be tested without touching a CSV.
- **`float ** float` widens to `Any` in mypy**, because a negative base can produce a complex
  result. Where that happens the result is bound to `float` explicitly at its source rather
  than suppressed with a cast at the return statement.

## Errors

Two different failures, handled two different ways.

**Impossible raises.** Physically or thermodynamically impossible input raises a `DesignError`
subclass. The hierarchy is `TemperatureOutsideTabulatedRangeError`, `InvalidGeometryError`,
`InvalidOperatingConditionError`, `DesignCaseFileError`, `PropertyTableFileError`,
`GraphicalInterfaceUnavailableError`.

Every error carries a `MessageKey` and its parameters rather than a formatted string, so the
same error renders in either language. `str(error)` still produces English, so a traceback and
a `pytest.raises(..., match=...)` both read naturally.

**Non-compliant reports.** A TEMA or FINA violation is returned as a `ConstraintCheck` carrying
the actual value, the allowed range, the standard that sets it, and whether it passes. The
calculation continues. Looking at a design just outside a standard is a legitimate thing to
want to do.

Command line exit codes:

| Code | Meaning |
|---|---|
| 0 | success |
| 2 | a `DesignError`, reported as one line with no traceback |
| 3 | a standards violation, only with `--fail-on-unsatisfied-constraint` |

Decision record: [0007](decisions/0007-impossible-geometry-raises-but-a-standards-violation-is-reported.md).

## Units

SI everywhere inside the package. Conversion happens only at two boundaries:

- the interface, where diameters are entered in millimetres and divided by `MILLIMETERS_PER_METER` once
- the report, where watts become kilowatts and pascals become kilopascals for display

The 2022 version converted millimetres in four separate button handlers. That is both repetition
and four chances to forget.

## Text

Every user facing string comes from `calculation/message_catalogue.py`: one mapping from a
`MessageKey` to English and Turkish. Nothing else in the package may hold a string a user
reads. This covers interface labels, section headings, button captions, column headings, status
lines, report headings, command line help, constraint names and error messages.

Enforced by:

- `test_every_message_key_appears_in_the_catalogue`
- `test_every_message_is_translated_into_every_language`
- `test_the_format_fields_match_between_the_languages_for_every_message` — a parameter present
  in one language and missing in the other is a failure, not a runtime surprise
- `test_only_the_text_catalogue_carries_turkish` — Turkish letters anywhere else fail the build
- `test_every_message_in_the_catalogue_is_used_somewhere` — a message written and never wired up
  is a failure; this is how a hard coded English error once survived next to its own unused
  Turkish translation

Every message starts with a capital letter in both languages. Turkish capitalisation of the
first letter follows the same rule as `Language.uppercase`, so a label starting with `i`
becomes `İ`, not `I`.

Unit symbols (`°C`, `kg/s`, `W/m²K`) are SI notation rather than language, so they are constants
in the catalogue module, declared once and identical in both languages.

Two language-specific behaviours that are not text, and therefore live on the `Language` enum
rather than in the mapping:

- `Language.endonym` — the language's own name for itself
- `Language.uppercase` — Turkish casing. `str.upper()` turns "girilen" into "GIRILEN"; Turkish
  needs "GİRİLEN". The enum translates `i` to `İ` and `ı` to `I` before uppercasing.

The report computes its label column width from the longest label in the current language, so a
longer translation cannot break the alignment. A hardcoded width did break it, and was fixed.

The JSON result file stays English in both its keys and its constraint text, deliberately. It is
a machine record meant to be diffed; if it changed language, two runs of the same design in
different languages would differ.

## Tests

Three kinds:

**Unit tests with named behaviour.** Test names are the specification, because there are no
docstrings. `test_equal_terminal_differences_return_that_difference_not_a_division_by_zero`
says what the code must do and why the edge case matters. During the rewrite a fourth kind
existed: a characterisation suite that drove the 2022 program headlessly and pinned every
quantity to twelve significant figures. It served its purpose and was retired
([0027](decisions/0027-the-2022-regression-apparatus-is-removed.md)); the four corrections it
proved are recorded in [validation.md](validation.md#deliberate-numerical-differences-from-the-2022-implementation).

**Numerical tolerance.** `pytest.approx` with an explicit `rel` that states how large a
deviation is allowed to be, never a bare `approx`.

**Standards tests.** `test_the_project_standards_hold.py` polices this document: no comments
and no docstrings in `src/` or `tests/`, no Flet in the core, every catalogue message used, no Turkish outside the catalogue, units in boundary names,
every correlation cited in `validation.md`, every decision record indexed and stating what was
rejected.

## Tooling

    python -m pytest -q
    python -m ruff check .
    python -m ruff format --check .
    python -m mypy

**ruff**, rule sets `E W F I N UP B A C4 SIM RET ARG PTH NPY PD RUF`. Three ignores, each for a
stated reason:

- `D` — pydocstyle would demand the docstrings this project forbids
- `ANN` — mypy strict already requires annotations, so a second rule set checking them is noise
- `RUF001`, `RUF003` — the en dash in a range such as `0.0666 – 0.2` is deliberate typography,
  not a homoglyph mistake

`line-length = 100`. Not longer, despite long identifiers: a line that does not fit at 100
characters is usually a call that should be broken across lines anyway, and the wrapping makes
long argument lists readable rather than hiding them off the right edge. `docs/` is excluded
from linting.

**mypy** strict over `src` and `tests`, nothing excluded.

## Dependencies

Every dependency must be justifiable out loud.

| Dependency | Required? | Job |
|---|---|---|
| `flet[desktop]` | `desktop-interface` extra | the desktop window |
| `flet[web]` | `web-interface` extra | the interface served over HTTP, and the container |
| `pytest`, `ruff`, `mypy` | development group | the gate |

The calculation core and the command line have **no third party dependencies**. The property
table is read with `csv` and interpolated with `bisect`; the iteration history exports through
`csv`. numpy and pandas did these jobs until the owner removed them
([0021](decisions/0021-numpy-and-pandas-are-removed-in-favour-of-the-standard-library.md)).

There are **two** interface extras rather than one because Flet 1.0 ships its desktop and web
clients as separate distributions and the base `flet` package contains neither; a missing client
makes Flet shell out to `pip install` at startup and `exit(1)` if that fails, which in a
container is a hard stop. `require_the_client_package` checks first and refuses with the extra to
install.

[0002](decisions/0002-keep-numpy-and-pandas-but-give-each-a-real-job.md) once argued for keeping
pandas despite the thirty three row table; the owner decided the other way on 2026-10-14 and
[0021](decisions/0021-numpy-and-pandas-are-removed-in-favour-of-the-standard-library.md)
records the reversal.

## What was deliberately not done

| Not done | Why | Record |
|---|---|---|
| a units library such as `pint` | third runtime dependency, and it hides the textbook form of each formula | [0004](decisions/0004-units-in-identifier-names-instead-of-a-units-library.md) |
| docstrings | the owner's instruction, and the citations are better in one validation document | [0003](decisions/0003-no-comments-and-no-docstrings.md) |
| nesting deeper than one level | one level of semantic packages is enough for this many modules; more directories would be ceremony | [0013](decisions/0013-a-flat-module-layout-rather-than-a-deep-package-tree.md) |
| an automatic convergence solver | the visible manual loop is the method, not a limitation | [0008](decisions/0008-the-manual-coefficient-iteration-is-kept.md) |
| `click` or `typer` | `argparse` is in the standard library and the surface is three subcommands | [0009](decisions/0009-argparse-from-the-standard-library.md) |
| `tomli-w` | the schema is fixed, so the writer is thirty lines and the round trip is tested | [0006](decisions/0006-reproducibility-comes-from-a-design-case-file-and-a-command-line.md) |
| a worker thread for the calculation | it takes microseconds; `page.run_thread` here would be cargo cult | [0016](decisions/0016-the-calculation-runs-on-the-event-loop-because-it-is-microseconds.md) |
| a bundled monospace font | numbers are right aligned with a fixed number of decimals per quantity, as on an engineering data sheet | [0019](decisions/0019-an-industrial-input-dialog-with-a-separate-results-page.md) |
| dropdown menus | every choice has two options, so both are shown as segmented buttons and nothing hides behind a click | [0019](decisions/0019-an-industrial-input-dialog-with-a-separate-results-page.md) |
| one button that copies both the coefficients and the geometry | pressed repeatedly it is the automatic solver record 0008 declined, and the loop does not settle on its own | [0020](decisions/0020-a-consistent-design-needs-agreeing-coefficients-and-the-suggested-geometry.md) |
| a class per correlation | a stateless single method class is a function wearing a costume | [0013](decisions/0013-a-flat-module-layout-rather-than-a-deep-package-tree.md) |
| applying the Liskov substitution principle | there is no inheritance hierarchy for it to govern, and inventing one to have somewhere to apply it would be the opposite of the principle | [0013](decisions/0013-a-flat-module-layout-rather-than-a-deep-package-tree.md) |
