# 28. The application icon is the PHXD symbol

Date: 2026-10-15
Status: accepted

## Context

Every surface showed Flet's own branding: the browser tab favicon, the PWA icons, the Flet
logo on the web loading screen, and the Flutter icon on the built Windows executable. The
owner supplied the project's logo as `PHXD.svg`: a shell and tube heat exchanger symbol with
flow arrows, black artwork on a transparent background, one clean path, no scripts.

## Decision

One master SVG, committed at `src/assets/PHXD.svg`, and raster renderings of it everywhere an
icon is consumed:

- `src/assets/icon.png` (1024²) — `flet build` reads it from the app directory's `assets/`
  folder and generates every Windows size from it; it does not decode SVG.
- `src/pool_heat_exchanger_designer/user_interface/web_assets/` — `favicon.png`,
  `icons/icon-192.png`, `icons/icon-512.png`, `icons/apple-touch-icon-192.png`,
  `icons/icon-maskable-192.png`, `icons/icon-maskable-512.png` and
  `icons/loading-animation.png`. The file names mirror `flet_web`'s static files exactly, and
  the web launcher passes this folder as `assets_dir`, so they shadow Flet's defaults. The
  maskable pair holds the artwork at 72 % so Android's circular mask does not clip it.
  Hatchling packages the folder into the wheel on its own — a force-include entry would add
  the files twice and fail the build, which is why the property table's entry is the only one.

Rendering method, since neither ImageMagick nor Inkscape is installed and the `convert` on
PATH is Windows' filesystem converter: headless Edge draws the SVG on a transparent 1024²
canvas over the DevTools protocol, and Pillow (already present under flet-cli) scales the
capture to every size. Verified: the served `favicon.png` and `icon-192.png` match the shipped
files byte for byte, and the rebuilt executable carries the generated icons.

## Alternatives considered and rejected

- **A white symbol on a steel blue (#1F5C99) rounded plate**, proposed earlier because black
  on transparent disappears on dark tabs and taskbars. Rejected: the owner supplied this
  artwork as the logo, and it ships unaltered. The dark-surface caveat stands; recolouring is
  a one-line SVG edit away if the owner ever wants it.
- **Installing ImageMagick or Inkscape to rasterise.** Rejected: a system dependency for eight
  small files that Edge and Pillow, both already present, produce.
- **Committing only the SVG and rasterising during the build.** Rejected: it puts a browser
  automation step inside every build for files that change only when the logo does. The PNGs
  are committed; this record describes how to regenerate them from the master.

## Consequences

About 70 KB of committed images. The desktop window while running **from source** still shows
Flet's icon — that window comes from the flet_desktop client, not from our build; the packaged
executable shows the PHXD symbol.
