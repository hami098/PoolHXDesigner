from __future__ import annotations

from collections.abc import Callable

import flet

from pool_heat_exchanger_designer.calculation.design_evaluation import (
    DEFAULT_CONVERGENCE_RELATIVE_TOLERANCE,
    DesignEvaluation,
)
from pool_heat_exchanger_designer.calculation.design_report import (
    CONVERGENCE_TOLERANCE_PERCENT_TEXT,
    correlation_notes,
)
from pool_heat_exchanger_designer.calculation.iteration_history import (
    IterationHistory,
    IterationRecord,
)
from pool_heat_exchanger_designer.calculation.message_catalogue import (
    UNIT_SYMBOL_DEGREE_CELSIUS,
    UNIT_SYMBOL_DIMENSIONLESS,
    UNIT_SYMBOL_KELVIN,
    UNIT_SYMBOL_KILOPASCAL,
    UNIT_SYMBOL_KILOWATT,
    UNIT_SYMBOL_METER,
    UNIT_SYMBOL_SQUARE_METER,
    UNIT_SYMBOL_WATTS_PER_SQUARE_METER_KELVIN,
    MessageKey,
)
from pool_heat_exchanger_designer.calculation.standards import ConstraintCheck
from pool_heat_exchanger_designer.calculation.translator import Translator
from pool_heat_exchanger_designer.user_interface.displayed_numbers import (
    magnitude_percent_text,
    number_text,
    signed_percent_text,
    unsigned_percent_text,
)
from pool_heat_exchanger_designer.user_interface.industrial_theme import (
    ATTENTION_COLOR,
    ATTENTION_TINT_COLOR,
    BODY_TEXT_SIZE,
    BORDER_WIDTH,
    COLUMN_GAP,
    CORNER_RADIUS,
    FAILURE_COLOR,
    GROUP_GAP,
    GROUP_PADDING,
    INLINE_ICON_SIZE,
    ONE_GROUP_PER_ROW,
    PANEL_BORDER_COLOR,
    PRIMARY_TEXT_COLOR,
    ROW_GAP,
    SATISFIED_COLOR,
    SATISFIED_TINT_COLOR,
    SECONDARY_TEXT_COLOR,
    SMALL_TEXT_SIZE,
    STATUS_ICON_SIZE,
    UNIT_COLUMN_WIDTH,
    grid_row,
    group_box,
    reference_text,
    secondary_button,
    secondary_text,
    status_line,
    toolbar_button,
    value_text,
)

PASCAL_PER_KILOPASCAL = 1.0e3
WATT_PER_KILOWATT = 1.0e3

HEAT_DUTY_DECIMAL_PLACES = 1
TEMPERATURE_DECIMAL_PLACES = 2
AREA_DECIMAL_PLACES = 2
RATIO_DECIMAL_PLACES = 3
COEFFICIENT_DECIMAL_PLACES = 0
REYNOLDS_NUMBER_DECIMAL_PLACES = 0
PRESSURE_DROP_DECIMAL_PLACES = 2
LENGTH_DECIMAL_PLACES = 3

CHECK_COLUMN_WIDTH = 108
ALLOWED_COLUMN_WIDTH = 120
SOURCE_COLUMN_WIDTH = 120
STATUS_COLUMN_WIDTH = 104
HISTORY_NUMBER_COLUMN_WIDTH = 32
HISTORY_VALUE_COLUMN_WIDTH = 96
VERDICT_ACCENT_WIDTH = 4


def _reported_row(label: str, value: str, unit: str, color: str = PRIMARY_TEXT_COLOR) -> flet.Row:
    return grid_row(label, value_text(value, color), unit)


def _table_cell(
    content: flet.Control,
    width: int | None = None,
    alignment: flet.Alignment = flet.Alignment.CENTER_RIGHT,
) -> flet.Container:
    return flet.Container(content=content, width=width, expand=width is None, alignment=alignment)


class ResultsPage:
    def __init__(
        self,
        translator: Translator,
        on_use_computed_coefficients: Callable[[], None],
        on_use_suggested_geometry: Callable[[], None],
        on_export_history: Callable[[], None],
    ) -> None:
        self._translator = translator
        self._on_use_computed_coefficients = on_use_computed_coefficients
        self._on_use_suggested_geometry = on_use_suggested_geometry
        self._on_export_history = on_export_history
        self._column = flet.Column(spacing=GROUP_GAP)
        self.show_nothing(translator.text(MessageKey.STATUS_NO_RESULTS_YET))

    @property
    def control(self) -> flet.Column:
        return self._column

    @property
    def has_results(self) -> bool:
        return len(self._column.controls) > 1

    def show_nothing(self, reason: str) -> None:
        self._column.controls = [
            flet.Container(
                content=status_line(flet.Icons.INFO_OUTLINE, SECONDARY_TEXT_COLOR, reason),
                padding=flet.Padding.all(GROUP_PADDING),
            )
        ]

    def show(self, evaluation: DesignEvaluation, history: IterationHistory) -> None:
        self._column.controls = [
            self._verdict(evaluation),
            flet.ResponsiveRow(
                controls=[
                    self._thermal_duty_group(evaluation),
                    self._pressure_drop_group(evaluation),
                    self._sizing_group(evaluation),
                    self._rating_group(evaluation),
                ],
                spacing=GROUP_GAP,
                run_spacing=GROUP_GAP,
                vertical_alignment=flet.CrossAxisAlignment.STRETCH,
            ),
            flet.ResponsiveRow(
                controls=[self._convergence_group(evaluation)],
                spacing=GROUP_GAP,
                run_spacing=GROUP_GAP,
            ),
            flet.ResponsiveRow(
                controls=[self._standards_group(evaluation.constraint_checks)],
                spacing=GROUP_GAP,
                run_spacing=GROUP_GAP,
            ),
            flet.ResponsiveRow(
                controls=[self._notes_group(evaluation)],
                spacing=GROUP_GAP,
                run_spacing=GROUP_GAP,
            ),
            flet.ResponsiveRow(
                controls=[self._history_group(history)],
                spacing=GROUP_GAP,
                run_spacing=GROUP_GAP,
            ),
        ]

    def _verdict(self, evaluation: DesignEvaluation) -> flet.Container:
        text = self._translator.text
        convergence = evaluation.coefficient_convergence
        agreement = evaluation.geometry_agreement
        consistent = evaluation.is_consistent()
        coefficients_agree = convergence.has_converged()
        geometry_matches = agreement.entered_matches_suggested()
        verdict_color = SATISFIED_COLOR if consistent else ATTENTION_COLOR
        return flet.Container(
            content=flet.Column(
                controls=[
                    flet.Row(
                        controls=[
                            flet.Icon(
                                flet.Icons.CHECK_CIRCLE if consistent else flet.Icons.WARNING_AMBER,
                                size=STATUS_ICON_SIZE + 4,
                                color=verdict_color,
                            ),
                            flet.Text(
                                text(
                                    MessageKey.VERDICT_CONSISTENT
                                    if consistent
                                    else MessageKey.VERDICT_NOT_CONSISTENT_YET
                                ),
                                size=BODY_TEXT_SIZE + 3,
                                weight=flet.FontWeight.W_700,
                                color=PRIMARY_TEXT_COLOR,
                            ),
                        ],
                        spacing=COLUMN_GAP,
                        vertical_alignment=flet.CrossAxisAlignment.CENTER,
                    ),
                    self._check_line(
                        coefficients_agree,
                        text(
                            MessageKey.CHECK_LINE_COEFFICIENTS_AGREE,
                            tolerance=CONVERGENCE_TOLERANCE_PERCENT_TEXT,
                        )
                        if coefficients_agree
                        else text(
                            MessageKey.CHECK_LINE_COEFFICIENTS_DIFFER,
                            gap=magnitude_percent_text(convergence.largest_relative_difference),
                        ),
                    ),
                    self._check_line(
                        geometry_matches,
                        text(MessageKey.CHECK_LINE_GEOMETRY_MATCHES)
                        if geometry_matches
                        else text(
                            MessageKey.CHECK_LINE_GEOMETRY_DIFFERS,
                            gap=magnitude_percent_text(agreement.largest_relative_difference),
                        ),
                    ),
                    secondary_text(text(MessageKey.VERDICT_EXPLANATION)),
                    flet.Row(
                        controls=[
                            secondary_button(
                                text(MessageKey.BUTTON_USE_COMPUTED_COEFFICIENTS),
                                flet.Icons.AUTO_FIX_HIGH,
                                self._on_use_computed_coefficients,
                                disabled=coefficients_agree,
                            ),
                            secondary_button(
                                text(MessageKey.BUTTON_USE_SUGGESTED_GEOMETRY),
                                flet.Icons.AUTO_FIX_HIGH,
                                self._on_use_suggested_geometry,
                                disabled=geometry_matches,
                            ),
                        ],
                        spacing=COLUMN_GAP,
                        wrap=True,
                    ),
                ],
                spacing=ROW_GAP + 2,
            ),
            bgcolor=SATISFIED_TINT_COLOR if consistent else ATTENTION_TINT_COLOR,
            border=flet.Border.only(
                left=flet.BorderSide(VERDICT_ACCENT_WIDTH, verdict_color),
                top=flet.BorderSide(BORDER_WIDTH, PANEL_BORDER_COLOR),
                right=flet.BorderSide(BORDER_WIDTH, PANEL_BORDER_COLOR),
                bottom=flet.BorderSide(BORDER_WIDTH, PANEL_BORDER_COLOR),
            ),
            border_radius=flet.BorderRadius.all(CORNER_RADIUS),
            padding=flet.Padding.all(GROUP_PADDING + 2),
        )

    def _check_line(self, satisfied: bool, message: str) -> flet.Row:
        return status_line(
            flet.Icons.CHECK_CIRCLE if satisfied else flet.Icons.WARNING_AMBER,
            SATISFIED_COLOR if satisfied else ATTENTION_COLOR,
            message,
        )

    def _thermal_duty_group(self, evaluation: DesignEvaluation) -> flet.Container:
        text = self._translator.text
        duty = evaluation.thermal_duty
        return group_box(
            text(MessageKey.HEADING_THERMAL_DUTY),
            [
                _reported_row(
                    text(MessageKey.RESULT_HEAT_DUTY),
                    number_text(duty.heat_duty_watts / WATT_PER_KILOWATT, HEAT_DUTY_DECIMAL_PLACES),
                    UNIT_SYMBOL_KILOWATT,
                ),
                _reported_row(
                    text(MessageKey.RESULT_SHELL_SIDE_OUTLET_TEMPERATURE),
                    number_text(
                        duty.shell_side_outlet_temperature_celsius, TEMPERATURE_DECIMAL_PLACES
                    ),
                    UNIT_SYMBOL_DEGREE_CELSIUS,
                ),
                _reported_row(
                    text(MessageKey.RESULT_CORRECTED_LOG_MEAN_TEMPERATURE_DIFFERENCE),
                    number_text(
                        evaluation.corrected_log_mean_temperature_difference_kelvin,
                        TEMPERATURE_DECIMAL_PLACES,
                    ),
                    UNIT_SYMBOL_KELVIN,
                ),
            ],
        )

    def _pressure_drop_group(self, evaluation: DesignEvaluation) -> flet.Container:
        text = self._translator.text
        return group_box(
            text(MessageKey.HEADING_PRESSURE_DROP),
            [
                _reported_row(
                    text(MessageKey.RESULT_TUBE_SIDE_PRESSURE_DROP),
                    number_text(
                        evaluation.tube_side.pressure_drop_pascal / PASCAL_PER_KILOPASCAL,
                        PRESSURE_DROP_DECIMAL_PLACES,
                    ),
                    UNIT_SYMBOL_KILOPASCAL,
                ),
                _reported_row(
                    text(MessageKey.RESULT_SHELL_SIDE_PRESSURE_DROP),
                    number_text(
                        evaluation.shell_side.pressure_drop_pascal / PASCAL_PER_KILOPASCAL,
                        PRESSURE_DROP_DECIMAL_PLACES,
                    ),
                    UNIT_SYMBOL_KILOPASCAL,
                ),
            ],
        )

    def _sizing_group(self, evaluation: DesignEvaluation) -> flet.Container:
        text = self._translator.text
        sizing = evaluation.preliminary_sizing
        return group_box(
            text(MessageKey.HEADING_PRELIMINARY_SIZING),
            [
                _reported_row(
                    text(MessageKey.RESULT_REQUIRED_FOULED_AREA),
                    number_text(sizing.required_fouled_area_square_meters, AREA_DECIMAL_PLACES),
                    UNIT_SYMBOL_SQUARE_METER,
                ),
                _reported_row(
                    text(MessageKey.RESULT_OVER_SURFACE_DESIGN_RATIO),
                    number_text(sizing.over_surface_design_ratio, RATIO_DECIMAL_PLACES),
                    UNIT_SYMBOL_DIMENSIONLESS,
                ),
                _reported_row(
                    text(MessageKey.RESULT_SUGGESTED_SHELL_INNER_DIAMETER),
                    number_text(
                        sizing.suggested_shell_inner_diameter_meters, LENGTH_DECIMAL_PLACES
                    ),
                    UNIT_SYMBOL_METER,
                ),
                _reported_row(
                    text(MessageKey.RESULT_SUGGESTED_TUBE_COUNT),
                    str(sizing.suggested_whole_tube_count),
                    UNIT_SYMBOL_DIMENSIONLESS,
                ),
                _reported_row(
                    text(MessageKey.RESULT_SUGGESTED_BAFFLE_SPACING),
                    number_text(sizing.suggested_baffle_spacing_meters, LENGTH_DECIMAL_PLACES),
                    UNIT_SYMBOL_METER,
                ),
            ],
        )

    def _rating_group(self, evaluation: DesignEvaluation) -> flet.Container:
        text = self._translator.text
        tube_side = evaluation.tube_side
        shell_side = evaluation.shell_side
        rated = evaluation.overall_coefficients_from_rating
        return group_box(
            text(MessageKey.HEADING_RATING),
            [
                _reported_row(
                    text(MessageKey.RESULT_TUBE_SIDE_COEFFICIENT),
                    number_text(
                        tube_side.heat_transfer_coefficient_watts_per_square_meter_kelvin,
                        COEFFICIENT_DECIMAL_PLACES,
                    ),
                    UNIT_SYMBOL_WATTS_PER_SQUARE_METER_KELVIN,
                ),
                _reported_row(
                    text(MessageKey.RESULT_SHELL_SIDE_COEFFICIENT),
                    number_text(
                        shell_side.heat_transfer_coefficient_watts_per_square_meter_kelvin,
                        COEFFICIENT_DECIMAL_PLACES,
                    ),
                    UNIT_SYMBOL_WATTS_PER_SQUARE_METER_KELVIN,
                ),
                _reported_row(
                    text(MessageKey.RESULT_OVERALL_COEFFICIENT_FOULED),
                    number_text(
                        rated.fouled_watts_per_square_meter_kelvin, COEFFICIENT_DECIMAL_PLACES
                    ),
                    UNIT_SYMBOL_WATTS_PER_SQUARE_METER_KELVIN,
                ),
                _reported_row(
                    text(MessageKey.RESULT_OVER_SURFACE_DESIGN_RATIO),
                    number_text(rated.over_surface_design_ratio, RATIO_DECIMAL_PLACES),
                    UNIT_SYMBOL_DIMENSIONLESS,
                ),
                _reported_row(
                    text(MessageKey.RESULT_TUBE_SIDE_REYNOLDS_NUMBER),
                    number_text(tube_side.reynolds_number, REYNOLDS_NUMBER_DECIMAL_PLACES),
                    UNIT_SYMBOL_DIMENSIONLESS,
                    PRIMARY_TEXT_COLOR
                    if tube_side.correlation_applied_inside_validated_range
                    else ATTENTION_COLOR,
                ),
                _reported_row(
                    text(MessageKey.RESULT_SHELL_SIDE_REYNOLDS_NUMBER),
                    number_text(shell_side.reynolds_number, REYNOLDS_NUMBER_DECIMAL_PLACES),
                    UNIT_SYMBOL_DIMENSIONLESS,
                    PRIMARY_TEXT_COLOR
                    if shell_side.correlation_applied_inside_validated_range
                    else ATTENTION_COLOR,
                ),
            ],
        )

    def _convergence_group(self, evaluation: DesignEvaluation) -> flet.Container:
        text = self._translator.text
        convergence = evaluation.coefficient_convergence
        agreement = evaluation.geometry_agreement
        return group_box(
            text(MessageKey.HEADING_COEFFICIENT_CONVERGENCE),
            [
                self._comparison_heading(
                    text(MessageKey.COLUMN_ASSUMED), text(MessageKey.COLUMN_COMPUTED)
                ),
                self._comparison_row(
                    text(MessageKey.RESULT_TUBE_SIDE_COEFFICIENT_ROW),
                    convergence.assumed_tube_side_watts_per_square_meter_kelvin,
                    convergence.computed_tube_side_watts_per_square_meter_kelvin,
                    COEFFICIENT_DECIMAL_PLACES,
                    UNIT_SYMBOL_WATTS_PER_SQUARE_METER_KELVIN,
                    convergence.tube_side_relative_difference,
                ),
                self._comparison_row(
                    text(MessageKey.RESULT_SHELL_SIDE_COEFFICIENT_ROW),
                    convergence.assumed_shell_side_watts_per_square_meter_kelvin,
                    convergence.computed_shell_side_watts_per_square_meter_kelvin,
                    COEFFICIENT_DECIMAL_PLACES,
                    UNIT_SYMBOL_WATTS_PER_SQUARE_METER_KELVIN,
                    convergence.shell_side_relative_difference,
                ),
                self._comparison_heading(
                    text(MessageKey.COLUMN_ENTERED), text(MessageKey.COLUMN_SUGGESTED)
                ),
                self._comparison_row(
                    text(MessageKey.FIELD_SHELL_INNER_DIAMETER),
                    agreement.suggested_shell_inner_diameter_meters,
                    agreement.entered_shell_inner_diameter_meters,
                    LENGTH_DECIMAL_PLACES,
                    UNIT_SYMBOL_METER,
                    None,
                    entered_first=True,
                ),
                self._comparison_row(
                    text(MessageKey.FIELD_TUBE_COUNT),
                    agreement.suggested_tube_count,
                    agreement.entered_tube_count,
                    0,
                    UNIT_SYMBOL_DIMENSIONLESS,
                    None,
                    entered_first=True,
                ),
                self._comparison_row(
                    text(MessageKey.FIELD_BAFFLE_SPACING),
                    agreement.suggested_baffle_spacing_meters,
                    agreement.entered_baffle_spacing_meters,
                    LENGTH_DECIMAL_PLACES,
                    UNIT_SYMBOL_METER,
                    None,
                    entered_first=True,
                ),
            ],
            column_layout=ONE_GROUP_PER_ROW,
        )

    def _comparison_heading(self, first_heading: str, second_heading: str) -> flet.Row:
        return flet.Row(
            controls=[
                flet.Container(expand=True),
                _table_cell(secondary_text(first_heading), HISTORY_VALUE_COLUMN_WIDTH),
                _table_cell(secondary_text(second_heading), HISTORY_VALUE_COLUMN_WIDTH),
                flet.Container(width=UNIT_COLUMN_WIDTH),
                _table_cell(
                    secondary_text(self._translator.text(MessageKey.COLUMN_DIFFERENCE)),
                    HISTORY_VALUE_COLUMN_WIDTH,
                ),
            ],
            spacing=COLUMN_GAP,
        )

    def _comparison_row(
        self,
        label: str,
        reference_value: float,
        compared_value: float,
        decimal_places: int,
        unit: str,
        relative_difference: float | None,
        entered_first: bool = False,
    ) -> flet.Row:
        difference = (
            relative_difference
            if relative_difference is not None
            else (compared_value - reference_value) / reference_value
        )
        first, second = (
            (compared_value, reference_value)
            if entered_first
            else (reference_value, compared_value)
        )
        return flet.Row(
            controls=[
                _table_cell(
                    flet.Text(label, size=BODY_TEXT_SIZE), alignment=flet.Alignment.CENTER_LEFT
                ),
                _table_cell(
                    value_text(number_text(first, decimal_places)), HISTORY_VALUE_COLUMN_WIDTH
                ),
                _table_cell(
                    reference_text(number_text(second, decimal_places)), HISTORY_VALUE_COLUMN_WIDTH
                ),
                _table_cell(
                    secondary_text(unit, BODY_TEXT_SIZE),
                    UNIT_COLUMN_WIDTH,
                    flet.Alignment.CENTER_LEFT,
                ),
                _table_cell(
                    value_text(
                        signed_percent_text(difference),
                        SATISFIED_COLOR
                        if abs(difference) <= DEFAULT_CONVERGENCE_RELATIVE_TOLERANCE
                        else PRIMARY_TEXT_COLOR,
                    ),
                    HISTORY_VALUE_COLUMN_WIDTH,
                ),
            ],
            spacing=COLUMN_GAP,
            vertical_alignment=flet.CrossAxisAlignment.CENTER,
        )

    def _standards_group(self, checks: tuple[ConstraintCheck, ...]) -> flet.Container:
        text = self._translator.text
        heading = flet.Row(
            controls=[
                _table_cell(
                    secondary_text(text(MessageKey.COLUMN_CHECK)),
                    alignment=flet.Alignment.CENTER_LEFT,
                ),
                _table_cell(secondary_text(text(MessageKey.COLUMN_VALUE)), CHECK_COLUMN_WIDTH),
                _table_cell(
                    secondary_text(text(MessageKey.COLUMN_ALLOWED)),
                    ALLOWED_COLUMN_WIDTH,
                    flet.Alignment.CENTER_LEFT,
                ),
                _table_cell(
                    secondary_text(text(MessageKey.COLUMN_SOURCE)),
                    SOURCE_COLUMN_WIDTH,
                    flet.Alignment.CENTER_LEFT,
                ),
                _table_cell(
                    secondary_text(text(MessageKey.COLUMN_STATUS)),
                    STATUS_COLUMN_WIDTH,
                    flet.Alignment.CENTER_LEFT,
                ),
            ],
            spacing=COLUMN_GAP,
        )
        return group_box(
            text(MessageKey.HEADING_STANDARDS_AND_ENVELOPE),
            [heading, *(self._check_row(check) for check in checks)],
            column_layout=ONE_GROUP_PER_ROW,
        )

    def _check_row(self, check: ConstraintCheck) -> flet.Row:
        translator = self._translator
        status_color = SATISFIED_COLOR if check.is_satisfied else FAILURE_COLOR
        value_with_unit = f"{number_text(check.actual_value, RATIO_DECIMAL_PLACES)} {check.unit}"
        return flet.Row(
            controls=[
                _table_cell(
                    flet.Text(check.quantity_text(translator), size=BODY_TEXT_SIZE),
                    alignment=flet.Alignment.CENTER_LEFT,
                ),
                _table_cell(
                    value_text(
                        value_with_unit.strip(),
                        PRIMARY_TEXT_COLOR if check.is_satisfied else FAILURE_COLOR,
                    ),
                    CHECK_COLUMN_WIDTH,
                ),
                _table_cell(
                    secondary_text(check.allowed_range_text(translator), BODY_TEXT_SIZE),
                    ALLOWED_COLUMN_WIDTH,
                    flet.Alignment.CENTER_LEFT,
                ),
                _table_cell(
                    secondary_text(check.standard_text(translator), BODY_TEXT_SIZE),
                    SOURCE_COLUMN_WIDTH,
                    flet.Alignment.CENTER_LEFT,
                ),
                _table_cell(
                    flet.Row(
                        controls=[
                            flet.Icon(
                                flet.Icons.CHECK_CIRCLE
                                if check.is_satisfied
                                else flet.Icons.ERROR_OUTLINE,
                                size=INLINE_ICON_SIZE,
                                color=status_color,
                            ),
                            flet.Text(
                                check.outcome_text(translator),
                                size=BODY_TEXT_SIZE,
                                color=status_color,
                                weight=flet.FontWeight.W_600,
                            ),
                        ],
                        spacing=4,
                    ),
                    STATUS_COLUMN_WIDTH,
                    flet.Alignment.CENTER_LEFT,
                ),
            ],
            spacing=COLUMN_GAP,
            vertical_alignment=flet.CrossAxisAlignment.CENTER,
        )

    def _notes_group(self, evaluation: DesignEvaluation) -> flet.Container:
        notes = correlation_notes(evaluation, self._translator)
        rows: list[flet.Control] = (
            [status_line(flet.Icons.WARNING_AMBER, ATTENTION_COLOR, note) for note in notes]
            if notes
            else [
                status_line(
                    flet.Icons.CHECK_CIRCLE,
                    SATISFIED_COLOR,
                    self._translator.text(MessageKey.NOTE_NONE),
                )
            ]
        )
        return group_box(
            self._translator.text(MessageKey.HEADING_NOTES),
            rows,
            column_layout=ONE_GROUP_PER_ROW,
        )

    def _history_group(self, history: IterationHistory) -> flet.Container:
        text = self._translator.text
        export_button = toolbar_button(
            text(MessageKey.BUTTON_EXPORT_ITERATION_HISTORY),
            flet.Icons.DOWNLOAD,
            self._on_export_history,
        )
        export_button.disabled = len(history) == 0
        headings = (
            MessageKey.COLUMN_ASSUMED_TUBE_SIDE,
            MessageKey.COLUMN_COMPUTED_TUBE_SIDE,
            MessageKey.COLUMN_ASSUMED_SHELL_SIDE,
            MessageKey.COLUMN_COMPUTED_SHELL_SIDE,
            MessageKey.COLUMN_LARGEST_GAP,
            MessageKey.COLUMN_GEOMETRY_GAP,
        )
        heading_row = flet.Row(
            controls=[
                _table_cell(
                    secondary_text(text(MessageKey.COLUMN_ITERATION_NUMBER)),
                    HISTORY_NUMBER_COLUMN_WIDTH,
                    flet.Alignment.CENTER_LEFT,
                ),
                *(
                    _table_cell(secondary_text(text(heading)), HISTORY_VALUE_COLUMN_WIDTH)
                    for heading in headings
                ),
            ],
            spacing=COLUMN_GAP,
        )
        return group_box(
            text(MessageKey.HEADING_ITERATION_HISTORY),
            [
                flet.Row(
                    controls=[
                        flet.Column(
                            controls=[
                                heading_row,
                                flet.Divider(height=1, thickness=1, color=PANEL_BORDER_COLOR),
                                *(self._history_row(record) for record in history.records()),
                            ],
                            spacing=4,
                        )
                    ],
                    scroll=flet.ScrollMode.AUTO,
                )
            ],
            trailing=export_button,
            column_layout=ONE_GROUP_PER_ROW,
        )

    def _history_row(self, record: IterationRecord) -> flet.Row:
        def cell(value: str, color: str = PRIMARY_TEXT_COLOR) -> flet.Container:
            return _table_cell(
                flet.Text(
                    value, size=SMALL_TEXT_SIZE + 1, color=color, text_align=flet.TextAlign.RIGHT
                ),
                HISTORY_VALUE_COLUMN_WIDTH,
            )

        return flet.Row(
            controls=[
                _table_cell(
                    flet.Text(str(record.iteration_number), size=SMALL_TEXT_SIZE + 1),
                    HISTORY_NUMBER_COLUMN_WIDTH,
                    flet.Alignment.CENTER_LEFT,
                ),
                cell(
                    number_text(
                        record.assumed_tube_side_coefficient_watts_per_square_meter_kelvin,
                        COEFFICIENT_DECIMAL_PLACES,
                    )
                ),
                cell(
                    number_text(
                        record.computed_tube_side_coefficient_watts_per_square_meter_kelvin,
                        COEFFICIENT_DECIMAL_PLACES,
                    )
                ),
                cell(
                    number_text(
                        record.assumed_shell_side_coefficient_watts_per_square_meter_kelvin,
                        COEFFICIENT_DECIMAL_PLACES,
                    )
                ),
                cell(
                    number_text(
                        record.computed_shell_side_coefficient_watts_per_square_meter_kelvin,
                        COEFFICIENT_DECIMAL_PLACES,
                    )
                ),
                cell(
                    unsigned_percent_text(record.largest_relative_difference),
                    SATISFIED_COLOR if record.has_converged else PRIMARY_TEXT_COLOR,
                ),
                cell(
                    unsigned_percent_text(record.largest_relative_geometry_difference),
                    SATISFIED_COLOR
                    if record.largest_relative_geometry_difference
                    <= DEFAULT_CONVERGENCE_RELATIVE_TOLERANCE
                    else PRIMARY_TEXT_COLOR,
                ),
            ],
            spacing=COLUMN_GAP,
        )
