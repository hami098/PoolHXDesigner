# 21. numpy and pandas are removed in favour of the standard library

Date: 2026-10-14
Status: accepted, supersedes [0002](0002-keep-numpy-and-pandas-but-give-each-a-real-job.md)

## Context

Record 0002 kept numpy and pandas because the owner wanted them demonstrated, while admitting
that "standard library `csv` plus `bisect`" was honestly the lightest option and that a reviewer
who disagreed would not be wrong. On 2026-10-14 the owner disagreed: for a project this small
the two libraries are not needed. Together they cost about 122 MB of installed footprint for
one interpolation and one CSV export.

## Decision

Both libraries are removed. The standard library replaces them exactly where 0002 predicted:

- `numpy.interp` becomes a `bisect_left` lookup plus the same linear interpolation formula,
  slope times distance plus the lower value, in `LiquidWaterPropertiesInterpolatedFromTable`.
  Non uniform temperature spacing still needs no special handling, and an exactly tabulated
  temperature still returns the tabulated row bit for bit.
- `pandas.read_csv` plus dataframe validation becomes `csv.reader` plus explicit checks in
  `property_table_parsed_from_csv_text`, which returns a frozen `LiquidWaterPropertyTable`.
  The validation got stricter in the exchange: a non numeric or non finite cell now raises
  `PropertyTableFileError` with its own catalogue message, where the pandas version would have
  crashed with an unhandled `ValueError` during `to_numpy(dtype=float)`.
- `pandas.DataFrame.to_csv` in the iteration history becomes `csv.writer` over the same
  `IterationRecord` fields, with `\n` line endings as before. `as_data_frame` is deleted; the
  interface table and the export both keep reading `records()`.
- `read_property_table_from_path` is deleted outright: nothing called it.

The 36 regression tests against the 2022 implementation pass unchanged, which is the proof
that the numbers did not move.

## Alternatives considered and rejected

- **Keeping both libraries as a demonstration of being able to use them.** This was 0002's
  reason, and the owner has now withdrawn it. A portfolio reads better with zero unneeded
  dependencies than with two justified-at-length ones.
- **Keeping only numpy for the interpolation.** Rejected: eleven lines of `bisect` and
  arithmetic replace it exactly, and a 60 MB dependency for eleven lines fails the
  "justifiable out loud" test once the demonstration motive is gone.
- **scipy.interpolate and CoolProp/iapws.** Rejected in 0002 and still rejected, for the same
  reasons: more capability than a 33 row Kakaç table warrants, and the coursework specifies
  that exact table.

## Consequences

The calculation core and the command line now run on the Python standard library alone;
`pip install .` installs nothing else. Flet remains the only third party runtime dependency,
behind the two interface extras. The install lost about 122 MB and four pinned distributions
(`numpy`, `pandas`, `python-dateutil`, `tzdata`), and the development group lost
`pandas-stubs`. The ruff rule families `NPY` and `PD` no longer select anything and are
dropped. What 0005 said about the core's dependencies ("numpy and pandas and a working command
line") and what 0016 said about `numpy.interp` should be read with this record in mind; those
records stay as written because they describe the decisions of their dates.
