from __future__ import annotations

from collections.abc import Callable

import flet

PAGE_BACKGROUND_COLOR = "#E8EBEF"
PANEL_BACKGROUND_COLOR = "#FFFFFF"
PANEL_BORDER_COLOR = "#C3C9D1"
PRIMARY_TEXT_COLOR = "#1D232A"
SECONDARY_TEXT_COLOR = "#5A6573"
ACCENT_COLOR = "#1F5C99"
INPUT_BORDER_COLOR = "#9AA4B0"
SATISFIED_COLOR = "#2E7D32"
SATISFIED_TINT_COLOR = "#E8F3E9"
ATTENTION_COLOR = "#9A5B00"
ATTENTION_TINT_COLOR = "#FFF4E0"
FAILURE_COLOR = "#C62828"
POOL_WATER_COLOR = "#1E7FC2"
HOT_WATER_COLOR = "#C8441B"
METAL_COLOR = "#59636E"
METAL_TINT_COLOR = "#F1F3F5"

APPLICATION_TITLE_TEXT_SIZE = 17
GROUP_TITLE_TEXT_SIZE = 13
BODY_TEXT_SIZE = 13
SMALL_TEXT_SIZE = 12

VALUE_COLUMN_WIDTH = 104
UNIT_COLUMN_WIDTH = 52
REFERENCE_COLUMN_WIDTH = 84
COLUMN_GAP = 8
GROUP_MARKER_WIDTH = 4
GROUP_MARKER_HEIGHT = 16
GROUP_TITLE_HEIGHT = 28

ROW_GAP = 6
GROUP_GAP = 12
GROUP_PADDING = 12
PAGE_PADDING = 16
MAXIMUM_CONTENT_WIDTH = 1180
CORNER_RADIUS = 4
BORDER_WIDTH = 1
INPUT_TEXT_INSET = 9

STATUS_ICON_SIZE = 18
INLINE_ICON_SIZE = 16

type ColumnLayout = dict[str | flet.ResponsiveRowBreakpoint, int | float]

TWO_GROUPS_PER_ROW_ON_WIDE_SCREENS: ColumnLayout = {"xs": 12, "md": 6}
ONE_GROUP_PER_ROW: ColumnLayout = {"xs": 12}


def industrial_theme() -> flet.Theme:
    return flet.Theme(
        use_material3=True,
        visual_density=flet.VisualDensity.COMPACT,
        scaffold_bgcolor=PAGE_BACKGROUND_COLOR,
        divider_color=PANEL_BORDER_COLOR,
        color_scheme=flet.ColorScheme(
            primary=ACCENT_COLOR,
            on_primary=PANEL_BACKGROUND_COLOR,
            secondary=ACCENT_COLOR,
            surface=PANEL_BACKGROUND_COLOR,
            on_surface=PRIMARY_TEXT_COLOR,
            on_surface_variant=SECONDARY_TEXT_COLOR,
            outline=INPUT_BORDER_COLOR,
            outline_variant=PANEL_BORDER_COLOR,
            error=FAILURE_COLOR,
        ),
    )


def body_text(
    value: str,
    color: str = PRIMARY_TEXT_COLOR,
    size: int = BODY_TEXT_SIZE,
    weight: flet.FontWeight | None = None,
    text_align: flet.TextAlign = flet.TextAlign.START,
) -> flet.Text:
    return flet.Text(value, size=size, color=color, weight=weight, text_align=text_align)


def secondary_text(value: str, size: int = SMALL_TEXT_SIZE) -> flet.Text:
    return flet.Text(value, size=size, color=SECONDARY_TEXT_COLOR)


def group_box(
    title: str,
    rows: list[flet.Control],
    marker_color: str | None = None,
    trailing: flet.Control | None = None,
    column_layout: ColumnLayout | None = None,
) -> flet.Container:
    title_controls: list[flet.Control] = []
    if marker_color is not None:
        title_controls.append(
            flet.Container(
                width=GROUP_MARKER_WIDTH,
                height=GROUP_MARKER_HEIGHT,
                bgcolor=marker_color,
                border_radius=flet.BorderRadius.all(1),
            )
        )
    title_controls.append(
        flet.Text(
            title,
            size=GROUP_TITLE_TEXT_SIZE,
            weight=flet.FontWeight.W_600,
            color=PRIMARY_TEXT_COLOR,
            expand=True,
        )
    )
    if trailing is not None:
        title_controls.append(trailing)
    return flet.Container(
        content=flet.Column(
            controls=[
                flet.Container(
                    content=flet.Row(
                        controls=title_controls,
                        spacing=COLUMN_GAP,
                        vertical_alignment=flet.CrossAxisAlignment.CENTER,
                    ),
                    height=GROUP_TITLE_HEIGHT,
                ),
                flet.Divider(height=1, thickness=1, color=PANEL_BORDER_COLOR),
                *rows,
            ],
            spacing=ROW_GAP,
        ),
        bgcolor=PANEL_BACKGROUND_COLOR,
        border=flet.Border.all(BORDER_WIDTH, PANEL_BORDER_COLOR),
        border_radius=flet.BorderRadius.all(CORNER_RADIUS),
        padding=flet.Padding.all(GROUP_PADDING),
        col=column_layout or TWO_GROUPS_PER_ROW_ON_WIDE_SCREENS,
    )


def grid_row(
    label: str,
    value: flet.Control,
    unit: str = "",
    reference: flet.Control | None = None,
) -> flet.Row:
    controls: list[flet.Control] = [
        flet.Container(
            content=body_text(label),
            expand=True,
            alignment=flet.Alignment.CENTER_LEFT,
        ),
        flet.Container(
            content=value,
            width=VALUE_COLUMN_WIDTH,
            alignment=flet.Alignment.CENTER_RIGHT,
        ),
        flet.Container(
            content=secondary_text(unit, BODY_TEXT_SIZE),
            width=UNIT_COLUMN_WIDTH,
            alignment=flet.Alignment.CENTER_LEFT,
        ),
    ]
    if reference is not None:
        controls.append(
            flet.Container(
                content=reference,
                width=REFERENCE_COLUMN_WIDTH,
                alignment=flet.Alignment.CENTER_RIGHT,
            )
        )
    return flet.Row(
        controls=controls,
        spacing=COLUMN_GAP,
        vertical_alignment=flet.CrossAxisAlignment.CENTER,
    )


def grid_heading(value_heading: str, reference_heading: str | None = None) -> flet.Row:
    controls: list[flet.Control] = [
        flet.Container(expand=True),
        flet.Container(
            content=secondary_text(value_heading),
            width=VALUE_COLUMN_WIDTH,
            alignment=flet.Alignment.CENTER_RIGHT,
        ),
        flet.Container(width=UNIT_COLUMN_WIDTH),
    ]
    if reference_heading is not None:
        controls.append(
            flet.Container(
                content=secondary_text(reference_heading),
                width=REFERENCE_COLUMN_WIDTH,
                alignment=flet.Alignment.CENTER_RIGHT,
            )
        )
    return flet.Row(controls=controls, spacing=COLUMN_GAP)


def value_text(value: str, color: str = PRIMARY_TEXT_COLOR) -> flet.Text:
    return flet.Text(
        value,
        size=BODY_TEXT_SIZE,
        color=color,
        weight=flet.FontWeight.W_500,
        text_align=flet.TextAlign.RIGHT,
        selectable=True,
    )


def reference_text(value: str = "") -> flet.Text:
    return flet.Text(
        value,
        size=BODY_TEXT_SIZE,
        color=SECONDARY_TEXT_COLOR,
        text_align=flet.TextAlign.RIGHT,
        selectable=True,
    )


def primary_button(
    text: str,
    icon: flet.IconData,
    on_click: Callable[[], None],
    disabled: bool = False,
) -> flet.FilledButton:
    return flet.FilledButton(
        content=flet.Text(text, size=BODY_TEXT_SIZE, weight=flet.FontWeight.W_600),
        icon=icon,
        on_click=on_click,
        disabled=disabled,
        style=flet.ButtonStyle(
            shape=flet.RoundedRectangleBorder(radius=CORNER_RADIUS),
            padding=flet.Padding.symmetric(horizontal=20, vertical=14),
        ),
    )


def secondary_button(
    text: str,
    icon: flet.IconData,
    on_click: Callable[[], None],
    disabled: bool = False,
) -> flet.OutlinedButton:
    return flet.OutlinedButton(
        content=flet.Text(text, size=BODY_TEXT_SIZE),
        icon=icon,
        on_click=on_click,
        disabled=disabled,
        style=flet.ButtonStyle(
            shape=flet.RoundedRectangleBorder(radius=CORNER_RADIUS),
            padding=flet.Padding.symmetric(horizontal=14, vertical=10),
        ),
    )


def toolbar_button(
    text: str,
    icon: flet.IconData,
    on_click: Callable[[], None],
) -> flet.TextButton:
    return flet.TextButton(
        content=flet.Text(text, size=BODY_TEXT_SIZE),
        icon=icon,
        on_click=on_click,
        style=flet.ButtonStyle(
            shape=flet.RoundedRectangleBorder(radius=CORNER_RADIUS),
            padding=flet.Padding.symmetric(horizontal=8, vertical=0),
            visual_density=flet.VisualDensity.COMPACT,
        ),
    )


def segmented_choice(
    options: list[tuple[str, str]],
    selected_key: str,
    on_change: Callable[[], None],
) -> flet.SegmentedButton:
    return flet.SegmentedButton(
        segments=[
            flet.Segment(value=key, label=flet.Text(label, size=BODY_TEXT_SIZE))
            for key, label in options
        ],
        selected=[selected_key],
        show_selected_icon=False,
        on_change=on_change,
        style=flet.ButtonStyle(
            shape=flet.RoundedRectangleBorder(radius=CORNER_RADIUS),
            visual_density=flet.VisualDensity.COMPACT,
            padding=flet.Padding.symmetric(horizontal=12, vertical=0),
            side=flet.BorderSide(BORDER_WIDTH, INPUT_BORDER_COLOR),
        ),
    )


def status_line(icon: flet.IconData, color: str, message: str) -> flet.Row:
    return flet.Row(
        controls=[
            flet.Icon(icon, size=INLINE_ICON_SIZE, color=color),
            flet.Text(message, size=BODY_TEXT_SIZE, color=PRIMARY_TEXT_COLOR, expand=True),
        ],
        spacing=COLUMN_GAP,
        vertical_alignment=flet.CrossAxisAlignment.START,
    )


def centred_to_content_width(content: flet.Control) -> tuple[flet.Container, flet.Row]:
    sized = flet.Container(content=content, width=MAXIMUM_CONTENT_WIDTH)
    return sized, flet.Row(controls=[sized], alignment=flet.MainAxisAlignment.CENTER)


def content_width_for(page_width: float | None) -> float:
    if page_width is None or page_width <= 0:
        return MAXIMUM_CONTENT_WIDTH
    return min(MAXIMUM_CONTENT_WIDTH, page_width - 2 * PAGE_PADDING)
