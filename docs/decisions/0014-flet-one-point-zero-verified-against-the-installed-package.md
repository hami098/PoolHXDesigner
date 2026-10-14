# 14. Flet 1.0 verified against the installed package, not against documentation from memory

Date: 2026-10-14
Status: accepted

## Context

Flet 1.0.0 shipped on 2026-09-14 and 1.0.4 on 2026-10-08, six days before this rewrite. It was
a ground-up re-architecture, so nearly every Flet example in circulation, and nearly everything
a tutorial or a blog post will tell you about Flet, is now wrong.

The renames that would each have cost a debugging cycle:

| Pre-1.0 | 1.0.4 |
|---|---|
| `ft.app(target=main)` | `ft.run(main)`; `ft.app` no longer exists |
| `ft.ElevatedButton(text=...)` | `ft.Button(content=...)`; there is no `text` field |
| `ft.colors.X` | `ft.Colors.X`; `ft.colors` no longer exists |
| `ft.padding.all(n)` | `ft.Padding.all(n)` |
| `ft.alignment.center` | `ft.Alignment.CENTER` |
| `TextField(error_text=, helper_text=)` | `TextField(error=, helper=)` |
| `Tabs(tabs=[...])` | `Tabs(length=, content=)` with `TabBar` and `TabBarView` |
| `FilePicker` as an overlay control | a service appended to `page.services`, methods are awaitable and return their result |

## Decision

Every Flet name used in this project was checked against the **installed** package by
introspecting its dataclass fields and signatures, not taken from documentation or recall.
Three claims that sounded right turned out to be wrong or incomplete when checked:

- `ft.app` appears to exist after any attribute access that imports the `flet.app` submodule,
  so a naive `hasattr` check passes. On a clean import it raises `AttributeError`. The old call
  fails either way, but for a different reason than expected.
- `ft.padding`, `ft.margin`, `ft.alignment` and `ft.icons` still resolve, as modules, while
  `ft.colors` is genuinely gone. The capitalised classes are used throughout regardless.
- **`Dropdown` does not follow `TextField`.** It extends `LayoutControl` rather than
  `FormFieldControl`, it keeps `error_text` and `helper_text`, and it has no `on_change` at all
  — the selection event is `on_select`. That inconsistency is contained in `ChoiceInputField`
  so the rest of the interface never has to know about it.

`flet>=1.0.4,<2` is the declared constraint, because a 2.0 would be free to break all of this
again.

## Alternatives considered and rejected

- **Writing the interface from remembered Flet API and fixing it by running.** Rejected: the
  headless smoke test cannot catch a wrong keyword argument that silently becomes an unknown
  field, and the desktop window cannot be opened in this environment.
- **Pinning `flet==1.0.4` exactly.** Rejected as too tight for a library on a weekly release
  cadence; patch releases inside 1.0.x are what should be picked up.
- **Keeping `ignore_missing_imports` for `flet` in the mypy configuration.** Rejected once it
  was noticed that Flet 1.0.4 ships a `py.typed` marker. The override was throwing away real
  type information; removing it type checks the whole interface against the actual API.
- **`ft.DropdownM2` to remove the asymmetry.** `DropdownM2` does inherit `FormFieldControl`, so
  it takes `error`, `helper` and `on_change` exactly like `TextField`, and one field factory
  could then cover all nineteen inputs. Rejected because M2 is the Material 2 control, and the
  rest of the interface is deliberately Material 3 (`use_material3=True`); mixing design
  languages to save a wrapper is the wrong trade. The asymmetry is confined to
  `ChoiceInputField`, which is what an adapter is for.
- **Setting `FLET_WEB_NO_CDN` in the Dockerfile.** Rejected because that variable does not
  exist in the installed 1.0.4 package — a grep of the package found nothing. Flet's web mode
  does fetch CanvasKit from a CDN by default, which would serve a blank page in a container with
  no outbound network, so the fix is real; the mechanism is the verified `no_cdn=True` argument
  to `ft.run`, which the web path now passes.

## Consequences

The interface is pinned to a six day old major version of a fast moving library. That is a real
risk for a portfolio piece, and the mitigation is that the calculation core does not depend on
Flet at all (record 0005), so replacing the interface would not touch the physics.
