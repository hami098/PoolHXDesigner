# 18. Every user facing string comes from one bilingual catalogue

Date: 2026-10-14
Status: accepted

## Context

The requirement, in the project owner's words: every piece of text must come from a single file,
for Turkish and English, so the application can run in either language, while all code stays
English.

Before this, English string literals were scattered across six interface modules, the report
formatter, the command line, the constraint checks and thirty three `raise` sites.

## Decision

`localization/` holds three small modules and nothing else:

- `language.py` — a two member `Language` enum
- `message_catalogue.py` — **the** mapping from a `MessageKey` to its English and Turkish text
- `translator.py` — resolves a key and its parameters into text in one language

Keys are an `Enum`, so a typo is an `AttributeError` at import rather than a missing string at
runtime. Parameterised messages use named `str.format` fields with the same field names in both
languages.

Four tests make the single source real rather than aspirational:

- every declared key appears in the catalogue, and the catalogue declares no key that does not exist
- every key has text in every language
- the `str.format` field names match between the two languages for every key
- Turkish letters appear in no source file except the catalogue and `language.py`

**Errors carry a key, not a string.** `DesignError.__init__` takes a `MessageKey` and keyword
parameters, stores both, and builds its English text for `super().__init__`. So `str(error)`
still reads as English for a traceback or a `pytest.raises(match=...)` assertion, while
`error.text_in_language(language)` renders Turkish at the boundary. The physics raises; it never
formats.

**Language is chosen explicitly.** `--language en|tr` on the command line, a selector in the
interface, nothing read from the environment or a configuration file.

## Alternatives considered and rejected

- **`gettext` with `.po` files.** The standard answer, with real tooling. Rejected: it puts the
  text in files outside the repository's own language, needs a compilation step, and the
  requirement was explicitly one file. A hundred and sixty keys do not need a translation
  pipeline.
- **A lazy translation proxy object, so a string retranslates itself when the language changes.**
  Rejected as cleverness: it makes every label a non-string that only looks like one, and
  rebuilding the screen is three lines.
- **A plain `dict[str, dict[str, str]]` keyed by string.** Rejected: a mistyped key would be a
  `KeyError` found by a user rather than an `AttributeError` found at import.
- **Putting unit symbols in the catalogue with a translation each.** Rejected: `°C` and `W/m²K`
  are SI notation, not language, and duplicating them per language would be ten identical pairs
  inviting a typo. They are constants in the catalogue module, so the single-file requirement
  holds without the duplication.
- **Translating the JSON result file.** Rejected deliberately. The result file is a machine
  record that `poolhx compare` diffs; if it changed language, the same design evaluated in
  Turkish and in English would compare as different, which would break the reproducibility
  promise in record 0006. Its keys and its constraint text stay English.
- **Leaving error messages English because they are "diagnostics".** Tempting, and it would have
  saved rewiring thirty three sites. Rejected: an error on screen is the text a user is most
  likely to need to understand, so exempting it would defeat the point.
- **`str.upper()` for headings.** Rejected once tested. Python's `upper()` turns "girilen" into
  "GIRILEN"; Turkish requires "GİRİLEN". `Language.uppercase` maps `i` to `İ` and `ı` to `I`
  first. This is language behaviour rather than text, so it lives on the enum, not in the
  mapping.
- **A fixed label column width in the report.** Rejected once tested. The longest Turkish label
  is longer than the longest English one, so a constant width broke the decimal alignment in
  Turkish. The width is computed from the longest label in the language actually in use, which
  cannot be broken by a future translation.

## Consequences

Adding a user facing message now means adding a key and both languages; the tests fail
otherwise. That is the intended friction.

The catalogue is a long file, and it is meant to be: it is the one place to look for anything a
user reads. `message_catalogue.py` and `language.py` are the only files in the repository
permitted to contain Turkish, and a test enforces it.
