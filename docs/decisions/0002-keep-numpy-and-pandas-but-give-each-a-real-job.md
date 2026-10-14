# 2. Keep numpy and pandas, but give each a real job

Date: 2026-10-14
Status: superseded by [0021](0021-numpy-and-pandas-are-removed-in-favour-of-the-standard-library.md)

## Context

The author wants numpy and pandas in this project as evidence of being able to use them, and
also wants as few dependencies as possible. Those two wishes pull against each other. The
2022 version imported pandas to read a 33 row table and never imported numpy at all; numpy was
present only transitively, underneath pandas.

A hostile reviewer would be right to call pandas-for-33-rows resume padding. So each library
has to be doing work that a senior engineer would actually give it, or it should go.

## Decision

Both stay, each on a job where it is the correct tool rather than a decorative one.

- **numpy** performs the property interpolation through `numpy.interp`. The property table is
  deliberately non uniform in temperature (5 K steps to 100 °C, then 10 K, then 50 K).
  `numpy.interp` handles non uniform abscissae natively, which is precisely the defect that
  made the 2022 interpolation raise `KeyError` above 100 °C. This is not padding: it is the
  fix.
- **pandas** reads and validates the property table, and holds the iteration history, where
  its real contribution is a stable tabular schema that exports to CSV for run to run
  comparison. Comparability of results is one of the author's stated requirements, and that
  is a dataframe shaped problem.

## Alternatives considered and rejected

- **Standard library `csv` plus `bisect`.** Honestly the lightest option, and it would remove
  both dependencies and the `pip install` step. Rejected because the author wants these two
  libraries demonstrated, and because once numpy is justified for the interpolation the
  marginal cost of pandas for the table and the history is small. A reviewer who disagrees is
  not wrong, and this record exists so the disagreement is about a stated choice rather than
  an oversight.
- **scipy.interpolate.** More capable than needed. Rejected: linear interpolation on a 33 row
  table does not warrant scipy's install footprint.
- **CoolProp or iapws for water properties.** More rigorous than a hand maintained table and
  would remove the table entirely. Rejected for now because the coursework the tool came from
  specifies the Kakaç table, and reproducing the 2022 numbers required that exact table.
  Worth revisiting if the tool outgrows coursework.
- **Inventing extra numpy usage to make the demonstration look richer.** Rejected outright.
  Padding a portfolio with work the problem does not need is the opposite of the signal the
  author wants to send.

## Consequences

Two runtime dependencies for the core. The property table layer is the only place that
imports pandas, so replacing it later touches one file.
