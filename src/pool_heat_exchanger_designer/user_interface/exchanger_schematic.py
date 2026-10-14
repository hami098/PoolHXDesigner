from __future__ import annotations

from dataclasses import dataclass

import flet
import flet.canvas as canvas

from pool_heat_exchanger_designer.calculation.message_catalogue import (
    UNIT_SYMBOL_DEGREE_CELSIUS,
    MessageKey,
)
from pool_heat_exchanger_designer.calculation.translator import Translator
from pool_heat_exchanger_designer.user_interface.displayed_numbers import number_text
from pool_heat_exchanger_designer.user_interface.industrial_theme import (
    HOT_WATER_COLOR,
    METAL_COLOR,
    METAL_TINT_COLOR,
    POOL_WATER_COLOR,
    PRIMARY_TEXT_COLOR,
    SECONDARY_TEXT_COLOR,
    SMALL_TEXT_SIZE,
)

DRAWING_WIDTH = 700
DRAWING_HEIGHT = 200

SHELL_LEFT = 150
SHELL_RIGHT = 550
SHELL_TOP = 60
SHELL_BOTTOM = 140
SHELL_MIDDLE = (SHELL_TOP + SHELL_BOTTOM) / 2
HEAD_DEPTH = 36
TUBE_HEIGHTS = (72, 86, 100, 114, 128)
BAFFLE_COUNT = 4
BAFFLE_OPENING = 22
HOT_WATER_INLET_POSITION = 506
HOT_WATER_OUTLET_POSITION = 196
NOZZLE_LENGTH = 40
ARROWHEAD_LENGTH = 9
ARROWHEAD_HALF_WIDTH = 5
LABEL_LINE_HEIGHT = 16
TWO_PASS_INLET_HEIGHT = 80
TWO_PASS_OUTLET_HEIGHT = 120
TEMPERATURE_DECIMAL_PLACES = 1
SHELL_SIDE_PATH_DASHES = [5.0, 4.0]

POOL_WATER_TINT_COLOR = "#E2EFF9"


@dataclass(frozen=True, slots=True)
class StreamTemperatures:
    pool_water_inlet_celsius: float | None
    pool_water_outlet_celsius: float | None
    hot_water_inlet_celsius: float | None
    hot_water_outlet_celsius: float | None


def _stroke(color: str, width: float = 1.5, dashes: list[float] | None = None) -> flet.Paint:
    return flet.Paint(
        color=color,
        stroke_width=width,
        style=flet.PaintingStyle.STROKE,
        stroke_dash_pattern=dashes,
    )


def _fill(color: str) -> flet.Paint:
    return flet.Paint(color=color, style=flet.PaintingStyle.FILL)


def _arrow(
    start_x: float, start_y: float, end_x: float, end_y: float, color: str
) -> list[canvas.Shape]:
    horizontal = start_y == end_y
    direction = 1.0 if (end_x > start_x if horizontal else end_y > start_y) else -1.0
    if horizontal:
        base_x = end_x - direction * ARROWHEAD_LENGTH
        corners = [
            canvas.Path.MoveTo(end_x, end_y),
            canvas.Path.LineTo(base_x, end_y - ARROWHEAD_HALF_WIDTH),
            canvas.Path.LineTo(base_x, end_y + ARROWHEAD_HALF_WIDTH),
            canvas.Path.Close(),
        ]
    else:
        base_y = end_y - direction * ARROWHEAD_LENGTH
        corners = [
            canvas.Path.MoveTo(end_x, end_y),
            canvas.Path.LineTo(end_x - ARROWHEAD_HALF_WIDTH, base_y),
            canvas.Path.LineTo(end_x + ARROWHEAD_HALF_WIDTH, base_y),
            canvas.Path.Close(),
        ]
    return [
        canvas.Line(start_x, start_y, end_x, end_y, paint=_stroke(color, 2.5)),
        canvas.Path(corners, paint=_fill(color)),
    ]


def _label(x: float, y: float, name: str, value: str, color: str) -> list[canvas.Shape]:
    return [
        canvas.Text(
            x,
            y,
            name,
            style=flet.TextStyle(size=SMALL_TEXT_SIZE, color=color, weight=flet.FontWeight.W_600),
        ),
        canvas.Text(
            x,
            y + LABEL_LINE_HEIGHT,
            value,
            style=flet.TextStyle(size=SMALL_TEXT_SIZE, color=PRIMARY_TEXT_COLOR),
        ),
    ]


def _caption(x: float, y: float, text: str) -> canvas.Text:
    return canvas.Text(
        x, y, text, style=flet.TextStyle(size=SMALL_TEXT_SIZE, color=SECONDARY_TEXT_COLOR)
    )


def _temperature(value: float | None) -> str:
    return f"{number_text(value, TEMPERATURE_DECIMAL_PLACES)} {UNIT_SYMBOL_DEGREE_CELSIUS}"


def _baffle_positions() -> list[float]:
    spacing = (SHELL_RIGHT - SHELL_LEFT) / (BAFFLE_COUNT + 1)
    return [SHELL_LEFT + spacing * index for index in range(1, BAFFLE_COUNT + 1)]


class ExchangerSchematic:
    def __init__(self, translator: Translator) -> None:
        self._translator = translator
        self._canvas = canvas.Canvas(width=DRAWING_WIDTH, height=DRAWING_HEIGHT, shapes=[])
        self._control = flet.Row(
            controls=[self._canvas],
            alignment=flet.MainAxisAlignment.CENTER,
            scroll=flet.ScrollMode.AUTO,
        )

    @property
    def control(self) -> flet.Row:
        return self._control

    @property
    def shape_count(self) -> int:
        return len(self._canvas.shapes)

    def show(self, temperatures: StreamTemperatures, tube_side_pass_count: int) -> None:
        self._canvas.shapes = [
            *self._shell_and_bundle(tube_side_pass_count),
            *self._shell_side_stream(temperatures),
            *self._tube_side_stream(temperatures, tube_side_pass_count),
        ]

    def _shell_and_bundle(self, tube_side_pass_count: int) -> list[canvas.Shape]:
        text = self._translator.text
        shapes: list[canvas.Shape] = [
            canvas.Rect(
                SHELL_LEFT - HEAD_DEPTH,
                SHELL_TOP,
                HEAD_DEPTH,
                SHELL_BOTTOM - SHELL_TOP,
                border_radius=6,
                paint=_fill(POOL_WATER_TINT_COLOR),
            ),
            canvas.Rect(
                SHELL_RIGHT,
                SHELL_TOP,
                HEAD_DEPTH,
                SHELL_BOTTOM - SHELL_TOP,
                border_radius=6,
                paint=_fill(POOL_WATER_TINT_COLOR),
            ),
            canvas.Rect(
                SHELL_LEFT,
                SHELL_TOP,
                SHELL_RIGHT - SHELL_LEFT,
                SHELL_BOTTOM - SHELL_TOP,
                paint=_fill(METAL_TINT_COLOR),
            ),
            canvas.Rect(
                SHELL_LEFT - HEAD_DEPTH,
                SHELL_TOP,
                SHELL_RIGHT - SHELL_LEFT + 2 * HEAD_DEPTH,
                SHELL_BOTTOM - SHELL_TOP,
                border_radius=6,
                paint=_stroke(METAL_COLOR, 2.0),
            ),
            *(
                canvas.Line(
                    SHELL_LEFT, height, SHELL_RIGHT, height, paint=_stroke(POOL_WATER_COLOR)
                )
                for height in TUBE_HEIGHTS
            ),
            *(
                canvas.Line(
                    position,
                    SHELL_TOP - 4,
                    position,
                    SHELL_BOTTOM + 4,
                    paint=_stroke(METAL_COLOR, 3.0),
                )
                for position in (SHELL_LEFT, SHELL_RIGHT)
            ),
        ]
        for index, position in enumerate(_baffle_positions()):
            starts_at_the_top = index % 2 == 1
            top = SHELL_TOP if starts_at_the_top else SHELL_TOP + BAFFLE_OPENING
            bottom = SHELL_BOTTOM - BAFFLE_OPENING if starts_at_the_top else SHELL_BOTTOM
            shapes.append(
                canvas.Line(position, top, position, bottom, paint=_stroke(METAL_COLOR, 3.0))
            )
        if tube_side_pass_count == 2:
            shapes.append(
                canvas.Line(
                    SHELL_LEFT - HEAD_DEPTH,
                    SHELL_MIDDLE,
                    SHELL_LEFT,
                    SHELL_MIDDLE,
                    paint=_stroke(METAL_COLOR, 2.0),
                )
            )
            shapes.append(
                _caption(SHELL_RIGHT - 6, SHELL_BOTTOM + 6, text(MessageKey.SCHEMATIC_RETURN_HEAD))
            )
        shapes.append(
            _caption(SHELL_LEFT + 150, SHELL_BOTTOM + 6, text(MessageKey.SCHEMATIC_SHELL))
        )
        shapes.append(
            _caption(SHELL_LEFT + 150, SHELL_TOP - 20, text(MessageKey.SCHEMATIC_BAFFLES))
        )
        return shapes

    def _shell_side_stream(self, temperatures: StreamTemperatures) -> list[canvas.Shape]:
        text = self._translator.text
        top_path = TUBE_HEIGHTS[0]
        bottom_path = TUBE_HEIGHTS[-1]
        first, second, third, fourth = _baffle_positions()
        turning_points = [
            (HOT_WATER_INLET_POSITION, SHELL_TOP + 6),
            (HOT_WATER_INLET_POSITION, bottom_path),
            ((fourth + third) / 2, bottom_path),
            ((fourth + third) / 2, top_path),
            ((third + second) / 2, top_path),
            ((third + second) / 2, bottom_path),
            ((second + first) / 2, bottom_path),
            ((second + first) / 2, top_path),
            (HOT_WATER_OUTLET_POSITION, top_path),
            (HOT_WATER_OUTLET_POSITION, SHELL_BOTTOM - 4),
        ]
        start_x, start_y = turning_points[0]
        path = canvas.Path(
            [
                canvas.Path.MoveTo(start_x, start_y),
                *(canvas.Path.LineTo(x, y) for x, y in turning_points[1:]),
            ],
            paint=_stroke(HOT_WATER_COLOR, 1.5, SHELL_SIDE_PATH_DASHES),
        )
        return [
            path,
            *_arrow(
                HOT_WATER_INLET_POSITION,
                SHELL_TOP - NOZZLE_LENGTH,
                HOT_WATER_INLET_POSITION,
                SHELL_TOP - 2,
                HOT_WATER_COLOR,
            ),
            *_arrow(
                HOT_WATER_OUTLET_POSITION,
                SHELL_BOTTOM + 2,
                HOT_WATER_OUTLET_POSITION,
                SHELL_BOTTOM + NOZZLE_LENGTH,
                HOT_WATER_COLOR,
            ),
            *_label(
                HOT_WATER_INLET_POSITION + 12,
                SHELL_TOP - NOZZLE_LENGTH - 4,
                text(MessageKey.SCHEMATIC_HOT_WATER_IN),
                _temperature(temperatures.hot_water_inlet_celsius),
                HOT_WATER_COLOR,
            ),
            *_label(
                HOT_WATER_OUTLET_POSITION + 12,
                SHELL_BOTTOM + NOZZLE_LENGTH - 20,
                text(MessageKey.SCHEMATIC_HOT_WATER_OUT),
                _temperature(temperatures.hot_water_outlet_celsius),
                HOT_WATER_COLOR,
            ),
        ]

    def _tube_side_stream(
        self, temperatures: StreamTemperatures, tube_side_pass_count: int
    ) -> list[canvas.Shape]:
        text = self._translator.text
        inlet_name = text(MessageKey.SCHEMATIC_POOL_WATER_IN)
        outlet_name = text(MessageKey.SCHEMATIC_POOL_WATER_OUT)
        inlet_value = _temperature(temperatures.pool_water_inlet_celsius)
        outlet_value = _temperature(temperatures.pool_water_outlet_celsius)
        left_end = SHELL_LEFT - HEAD_DEPTH - 2
        right_end = SHELL_RIGHT + HEAD_DEPTH + 2
        if tube_side_pass_count == 2:
            return [
                *_arrow(
                    20, TWO_PASS_INLET_HEIGHT, left_end, TWO_PASS_INLET_HEIGHT, POOL_WATER_COLOR
                ),
                *_arrow(
                    left_end, TWO_PASS_OUTLET_HEIGHT, 20, TWO_PASS_OUTLET_HEIGHT, POOL_WATER_COLOR
                ),
                *_label(4, TWO_PASS_INLET_HEIGHT - 38, inlet_name, inlet_value, POOL_WATER_COLOR),
                *_label(4, TWO_PASS_OUTLET_HEIGHT + 8, outlet_name, outlet_value, POOL_WATER_COLOR),
            ]
        return [
            *_arrow(20, SHELL_MIDDLE, left_end, SHELL_MIDDLE, POOL_WATER_COLOR),
            *_arrow(right_end, SHELL_MIDDLE, DRAWING_WIDTH - 20, SHELL_MIDDLE, POOL_WATER_COLOR),
            *_label(4, SHELL_MIDDLE - 38, inlet_name, inlet_value, POOL_WATER_COLOR),
            *_label(right_end + 4, SHELL_MIDDLE - 38, outlet_name, outlet_value, POOL_WATER_COLOR),
        ]
