from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import flet

from pool_heat_exchanger_designer.calculation.message_catalogue import (
    UNIT_SYMBOL_DIMENSIONLESS,
    MessageKey,
)
from pool_heat_exchanger_designer.calculation.translator import Translator
from pool_heat_exchanger_designer.user_interface.industrial_theme import (
    ACCENT_COLOR,
    BODY_TEXT_SIZE,
    BORDER_WIDTH,
    COLUMN_GAP,
    CORNER_RADIUS,
    FAILURE_COLOR,
    INPUT_BORDER_COLOR,
    INPUT_TEXT_INSET,
    PANEL_BACKGROUND_COLOR,
    SMALL_TEXT_SIZE,
    VALUE_COLUMN_WIDTH,
    body_text,
    grid_row,
    reference_text,
    segmented_choice,
)

DIGITS_AND_EITHER_DECIMAL_SEPARATOR = flet.InputFilter(
    regex_string=r"[0-9.,]", allow=True, replacement_string=""
)
DECIMAL_COMMA = ","
DECIMAL_POINT = "."
REJECTION_LINE_GAP = 2


@dataclass(frozen=True, slots=True)
class NumericFieldSpecification:
    key: str
    label_key: MessageKey
    unit: str
    initial_value: float
    lowest_accepted_value: float
    highest_accepted_value: float
    decimal_places: int = 3
    accepts_only_whole_numbers: bool = False

    def formatted(self, value: float) -> str:
        if self.accepts_only_whole_numbers:
            return f"{round(value)}"
        return f"{value:.{self.decimal_places}f}".rstrip("0").rstrip(".") or "0"

    def label(self, translator: Translator) -> str:
        return translator.text(self.label_key)

    def rejection_message(self, translator: Translator) -> str:
        if self.unit == UNIT_SYMBOL_DIMENSIONLESS:
            return translator.text(
                MessageKey.FIELD_RANGE_REJECTION_WITHOUT_UNIT,
                lowest=f"{self.lowest_accepted_value:g}",
                highest=f"{self.highest_accepted_value:g}",
            )
        return translator.text(
            MessageKey.FIELD_RANGE_REJECTION_WITH_UNIT,
            lowest=f"{self.lowest_accepted_value:g}",
            highest=f"{self.highest_accepted_value:g}",
            unit=self.unit,
        )


class NumericInputField:
    def __init__(
        self,
        specification: NumericFieldSpecification,
        translator: Translator,
        on_any_change: Callable[[], None],
        on_submit: Callable[[], None],
    ) -> None:
        self._specification = specification
        self._translator = translator
        self._on_any_change = on_any_change
        self._on_submit = on_submit
        self._reference_text = reference_text()
        self._rejection_text = flet.Text(
            "", size=SMALL_TEXT_SIZE, color=FAILURE_COLOR, visible=False
        )
        self._text_field = flet.TextField(
            value=specification.formatted(specification.initial_value),
            width=VALUE_COLUMN_WIDTH,
            dense=True,
            text_size=BODY_TEXT_SIZE,
            text_align=flet.TextAlign.RIGHT,
            keyboard_type=flet.KeyboardType.NUMBER,
            input_filter=DIGITS_AND_EITHER_DECIMAL_SEPARATOR,
            content_padding=flet.Padding.symmetric(
                horizontal=INPUT_TEXT_INSET - BORDER_WIDTH, vertical=9
            ),
            border_color=INPUT_BORDER_COLOR,
            focused_border_color=ACCENT_COLOR,
            border_radius=CORNER_RADIUS,
            filled=True,
            fill_color=PANEL_BACKGROUND_COLOR,
            on_change=self._handle_change,
            on_submit=self._handle_submit,
        )

    @property
    def key(self) -> str:
        return self._specification.key

    @property
    def label(self) -> str:
        return self._specification.label(self._translator)

    @property
    def entered_text(self) -> str:
        return self._text_field.value or ""

    @property
    def parsed_value(self) -> float | None:
        entered_text = self.entered_text.replace(DECIMAL_COMMA, DECIMAL_POINT)
        try:
            value = float(entered_text)
        except ValueError:
            return None
        if not (
            self._specification.lowest_accepted_value
            <= value
            <= self._specification.highest_accepted_value
        ):
            return None
        return value

    @property
    def is_valid(self) -> bool:
        return self.parsed_value is not None

    @property
    def shown_rejection_message(self) -> str | None:
        if not self._rejection_text.visible:
            return None
        return self._rejection_text.value

    @property
    def shown_reference_value(self) -> str:
        return self._reference_text.value or ""

    def set_value(self, value: float) -> None:
        self._text_field.value = self._specification.formatted(value)
        self.refresh_validation_message()

    def set_text(self, text: str) -> None:
        self._text_field.value = text

    def show_reference_value(self, value: float | None) -> None:
        self._reference_text.value = "" if value is None else self._specification.formatted(value)

    def refresh_validation_message(self) -> None:
        if self.is_valid:
            self._rejection_text.visible = False
            self._text_field.border_color = INPUT_BORDER_COLOR
            return
        self._rejection_text.value = self._specification.rejection_message(self._translator)
        self._rejection_text.visible = True
        self._text_field.border_color = FAILURE_COLOR

    def as_row(self, show_reference_column: bool = False) -> flet.Column:
        return flet.Column(
            controls=[
                grid_row(
                    self.label,
                    self._text_field,
                    self._specification.unit,
                    reference=self._reference_text if show_reference_column else None,
                ),
                self._rejection_text,
            ],
            spacing=REJECTION_LINE_GAP,
        )

    def _handle_change(self) -> None:
        self.refresh_validation_message()
        self._on_any_change()

    def _handle_submit(self) -> None:
        self.refresh_validation_message()
        self._on_submit()


class ChoiceInputField:
    def __init__(
        self,
        key: str,
        label_key: MessageKey,
        options: tuple[tuple[str, MessageKey], ...],
        initial_key: str,
        translator: Translator,
        on_any_change: Callable[[], None],
    ) -> None:
        self._key = key
        self._label = translator.text(label_key)
        self._on_any_change = on_any_change
        self._segments = segmented_choice(
            [
                (option_key, translator.text(option_label_key))
                for option_key, option_label_key in options
            ],
            initial_key,
            self._handle_select,
        )

    @property
    def key(self) -> str:
        return self._key

    @property
    def selected_key(self) -> str:
        return self._segments.selected[0]

    def select(self, option_key: str) -> None:
        self._segments.selected = [option_key]

    def as_row(self) -> flet.Row:
        return flet.Row(
            controls=[
                flet.Container(
                    content=body_text(self._label),
                    expand=True,
                    alignment=flet.Alignment.CENTER_LEFT,
                ),
                self._segments,
            ],
            spacing=COLUMN_GAP,
            vertical_alignment=flet.CrossAxisAlignment.CENTER,
        )

    def _handle_select(self) -> None:
        self._on_any_change()
