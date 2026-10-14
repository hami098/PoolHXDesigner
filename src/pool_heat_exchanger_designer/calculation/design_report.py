from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pool_heat_exchanger_designer.calculation.design_evaluation import (
    DEFAULT_CONVERGENCE_RELATIVE_TOLERANCE,
    DesignEvaluation,
    SideRating,
)
from pool_heat_exchanger_designer.calculation.language import Language
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
from pool_heat_exchanger_designer.calculation.shell_side_correlations import (
    KERN_MAXIMUM_VALID_REYNOLDS_NUMBER,
    KERN_MINIMUM_VALID_REYNOLDS_NUMBER,
)
from pool_heat_exchanger_designer.calculation.translator import Translator
from pool_heat_exchanger_designer.calculation.tube_side_correlations import (
    GNIELINSKI_MAXIMUM_VALID_PRANDTL_NUMBER,
    GNIELINSKI_MINIMUM_VALID_PRANDTL_NUMBER,
    GNIELINSKI_MINIMUM_VALID_REYNOLDS_NUMBER,
)

PASCAL_PER_KILOPASCAL = 1.0e3
WATT_PER_KILOWATT = 1.0e3

VALUE_COLUMN_CHARACTERS = 14
LABEL_COLUMN_PADDING_CHARACTERS = 2
PERCENT_PER_FRACTION = 100.0
CONVERGENCE_TOLERANCE_PERCENT_TEXT = (
    f"{DEFAULT_CONVERGENCE_RELATIVE_TOLERANCE * PERCENT_PER_FRACTION:g}"
)

VALUE_LABEL_KEYS = (
    MessageKey.RESULT_HEAT_DUTY,
    MessageKey.RESULT_SHELL_SIDE_OUTLET_TEMPERATURE,
    MessageKey.RESULT_CORRECTED_LOG_MEAN_TEMPERATURE_DIFFERENCE,
    MessageKey.RESULT_SUGGESTED_SHELL_INNER_DIAMETER,
    MessageKey.RESULT_SUGGESTED_TUBE_COUNT,
    MessageKey.RESULT_SUGGESTED_BAFFLE_SPACING,
    MessageKey.RESULT_REQUIRED_FOULED_AREA,
    MessageKey.RESULT_OVER_SURFACE_DESIGN_RATIO,
    MessageKey.RESULT_TUBE_SIDE_COEFFICIENT,
    MessageKey.RESULT_SHELL_SIDE_COEFFICIENT,
    MessageKey.RESULT_TUBE_SIDE_REYNOLDS_NUMBER,
    MessageKey.RESULT_SHELL_SIDE_REYNOLDS_NUMBER,
    MessageKey.RESULT_OVERALL_COEFFICIENT_FOULED,
    MessageKey.RESULT_TUBE_SIDE_PRESSURE_DROP,
    MessageKey.RESULT_SHELL_SIDE_PRESSURE_DROP,
    MessageKey.CHECK_LINE_GEOMETRY_MATCHES,
)


def label_column_characters(translator: Translator, evaluation: DesignEvaluation) -> int:
    labels = [
        *(translator.text(label_key) for label_key in VALUE_LABEL_KEYS),
        translator.text(MessageKey.REPORT_CONVERGED, tolerance=CONVERGENCE_TOLERANCE_PERCENT_TEXT),
        *(check.quantity_text(translator) for check in evaluation.constraint_checks),
    ]
    return max(len(label) for label in labels) + LABEL_COLUMN_PADDING_CHARACTERS


MACHINE_READABLE_TRANSLATOR = Translator(Language.ENGLISH)


def correlation_notes(evaluation: DesignEvaluation, translator: Translator) -> tuple[str, ...]:
    notes: list[str] = []
    tube_side = evaluation.tube_side
    shell_side = evaluation.shell_side
    if not tube_side.correlation_applied_inside_validated_range:
        notes.append(
            translator.text(
                MessageKey.NOTE_TUBE_SIDE_CORRELATION_OUTSIDE_RANGE,
                reynolds=f"{tube_side.reynolds_number:.0f}",
                prandtl=f"{tube_side.prandtl_number:.2f}",
                correlation_name=tube_side.correlation_name,
                minimum=f"{GNIELINSKI_MINIMUM_VALID_REYNOLDS_NUMBER:.0f}",
                lowest_prandtl=f"{GNIELINSKI_MINIMUM_VALID_PRANDTL_NUMBER:g}",
                highest_prandtl=f"{GNIELINSKI_MAXIMUM_VALID_PRANDTL_NUMBER:g}",
            )
        )
    if not shell_side.correlation_applied_inside_validated_range:
        notes.append(
            translator.text(
                MessageKey.NOTE_SHELL_SIDE_CORRELATION_OUTSIDE_RANGE,
                reynolds=f"{shell_side.reynolds_number:.0f}",
                correlation_name=shell_side.correlation_name,
                minimum=f"{KERN_MINIMUM_VALID_REYNOLDS_NUMBER:.0f}",
                maximum=f"{KERN_MAXIMUM_VALID_REYNOLDS_NUMBER:.0f}",
            )
        )
    return tuple(notes)


def design_evaluation_as_dictionary(evaluation: DesignEvaluation) -> dict[str, Any]:
    design_case = evaluation.design_case
    conditions = design_case.operating_conditions
    bundle = design_case.tube_bundle
    duty = evaluation.thermal_duty
    sizing = evaluation.preliminary_sizing
    convergence = evaluation.coefficient_convergence
    agreement = evaluation.geometry_agreement

    return {
        "design_case_name": design_case.name,
        "inputs": {
            "tube_side_inlet_temperature_celsius": (conditions.tube_side_inlet_temperature_celsius),
            "tube_side_outlet_temperature_celsius": (
                conditions.tube_side_outlet_temperature_celsius
            ),
            "shell_side_inlet_temperature_celsius": (
                conditions.shell_side_inlet_temperature_celsius
            ),
            "tube_side_mass_flow_rate_kilograms_per_second": (
                conditions.tube_side_mass_flow_rate_kilograms_per_second
            ),
            "shell_side_mass_flow_rate_kilograms_per_second": (
                conditions.shell_side_mass_flow_rate_kilograms_per_second
            ),
            "tube_outer_diameter_meters": bundle.tube_outer_diameter_meters,
            "tube_inner_diameter_meters": bundle.tube_inner_diameter_meters,
            "tube_length_meters": bundle.tube_length_meters,
            "tube_count": bundle.tube_count,
            "tube_side_pass_count": bundle.tube_side_pass_count,
            "pitch_ratio": bundle.pitch_ratio,
            "pitch_layout": bundle.pitch_layout.value,
            "shell_inner_diameter_meters": design_case.shell.inner_diameter_meters,
            "baffle_spacing_meters": design_case.shell.baffle_spacing_meters,
            "tube_wall_material": design_case.tube_wall_material.name,
            "assumed_tube_side_coefficient_watts_per_square_meter_kelvin": (
                convergence.assumed_tube_side_watts_per_square_meter_kelvin
            ),
            "assumed_shell_side_coefficient_watts_per_square_meter_kelvin": (
                convergence.assumed_shell_side_watts_per_square_meter_kelvin
            ),
            "log_mean_temperature_difference_correction_factor": (
                design_case.log_mean_temperature_difference_correction_factor
            ),
        },
        "thermal_duty": {
            "heat_duty_watts": duty.heat_duty_watts,
            "shell_side_outlet_temperature_celsius": (duty.shell_side_outlet_temperature_celsius),
            "tube_side_bulk_temperature_celsius": (duty.tube_side_bulk_temperature_celsius),
            "shell_side_bulk_temperature_celsius": (duty.shell_side_bulk_temperature_celsius),
            "corrected_log_mean_temperature_difference_kelvin": (
                evaluation.corrected_log_mean_temperature_difference_kelvin
            ),
        },
        "preliminary_sizing": {
            "required_clean_area_square_meters": (sizing.required_clean_area_square_meters),
            "required_fouled_area_square_meters": (sizing.required_fouled_area_square_meters),
            "suggested_shell_inner_diameter_meters": (sizing.suggested_shell_inner_diameter_meters),
            "suggested_tube_count": sizing.suggested_tube_count,
            "suggested_baffle_spacing_meters": sizing.suggested_baffle_spacing_meters,
            "over_surface_design_ratio": sizing.over_surface_design_ratio,
        },
        "tube_side": _side_as_dictionary(evaluation.tube_side),
        "shell_side": _side_as_dictionary(evaluation.shell_side),
        "overall_heat_transfer_coefficients": {
            "clean_watts_per_square_meter_kelvin": (
                evaluation.overall_coefficients_from_rating.clean_watts_per_square_meter_kelvin
            ),
            "fouled_watts_per_square_meter_kelvin": (
                evaluation.overall_coefficients_from_rating.fouled_watts_per_square_meter_kelvin
            ),
            "over_surface_design_ratio": (
                evaluation.overall_coefficients_from_rating.over_surface_design_ratio
            ),
        },
        "coefficient_convergence": {
            "computed_tube_side_watts_per_square_meter_kelvin": (
                convergence.computed_tube_side_watts_per_square_meter_kelvin
            ),
            "computed_shell_side_watts_per_square_meter_kelvin": (
                convergence.computed_shell_side_watts_per_square_meter_kelvin
            ),
            "tube_side_relative_difference": convergence.tube_side_relative_difference,
            "shell_side_relative_difference": (convergence.shell_side_relative_difference),
            "largest_relative_difference": convergence.largest_relative_difference,
            "has_converged": convergence.has_converged(),
        },
        "geometry_agreement": {
            "suggested_shell_inner_diameter_meters": (
                agreement.suggested_shell_inner_diameter_meters
            ),
            "suggested_whole_tube_count": agreement.suggested_tube_count,
            "suggested_baffle_spacing_meters": agreement.suggested_baffle_spacing_meters,
            "largest_relative_difference": agreement.largest_relative_difference,
            "entered_matches_suggested": agreement.entered_matches_suggested(),
        },
        "is_consistent": evaluation.is_consistent(),
        "constraint_checks": [
            {
                "quantity": check.quantity_text(MACHINE_READABLE_TRANSLATOR),
                "standard": check.standard_text(MACHINE_READABLE_TRANSLATOR),
                "actual_value": check.actual_value,
                "unit": check.unit,
                "allowed_range": check.allowed_range_text(MACHINE_READABLE_TRANSLATOR),
                "is_satisfied": check.is_satisfied,
            }
            for check in evaluation.constraint_checks
        ],
        "correlations_outside_their_validated_range": list(
            evaluation.correlations_outside_their_validated_range
        ),
    }


def _side_as_dictionary(side: SideRating) -> dict[str, Any]:
    return {
        "reynolds_number": side.reynolds_number,
        "prandtl_number": side.prandtl_number,
        "mass_flux_kilograms_per_square_meter_second": (
            side.mass_flux_kilograms_per_square_meter_second
        ),
        "heat_transfer_coefficient_watts_per_square_meter_kelvin": (
            side.heat_transfer_coefficient_watts_per_square_meter_kelvin
        ),
        "pressure_drop_pascal": side.pressure_drop_pascal,
        "correlation_name": side.correlation_name,
        "correlation_applied_inside_validated_range": (
            side.correlation_applied_inside_validated_range
        ),
    }


def write_design_evaluation_to_json_path(evaluation: DesignEvaluation, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(design_evaluation_as_dictionary(evaluation), indent=2) + "\n",
        encoding="utf-8",
    )


def design_evaluation_as_aligned_text(evaluation: DesignEvaluation, translator: Translator) -> str:
    label_width = label_column_characters(translator, evaluation)
    duty = evaluation.thermal_duty
    sizing = evaluation.preliminary_sizing
    convergence = evaluation.coefficient_convergence
    agreement = evaluation.geometry_agreement
    rated = evaluation.overall_coefficients_from_rating

    lines = [
        translator.text(MessageKey.REPORT_DESIGN_CASE_NAME, name=evaluation.design_case.name),
        "",
        translator.uppercase_text(MessageKey.HEADING_THERMAL_DUTY),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_HEAT_DUTY,
            duty.heat_duty_watts / WATT_PER_KILOWATT,
            UNIT_SYMBOL_KILOWATT,
        ),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_SHELL_SIDE_OUTLET_TEMPERATURE,
            duty.shell_side_outlet_temperature_celsius,
            UNIT_SYMBOL_DEGREE_CELSIUS,
        ),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_CORRECTED_LOG_MEAN_TEMPERATURE_DIFFERENCE,
            evaluation.corrected_log_mean_temperature_difference_kelvin,
            UNIT_SYMBOL_KELVIN,
        ),
        "",
        translator.uppercase_text(MessageKey.HEADING_PRELIMINARY_SIZING),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_SUGGESTED_SHELL_INNER_DIAMETER,
            sizing.suggested_shell_inner_diameter_meters,
            UNIT_SYMBOL_METER,
        ),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_SUGGESTED_TUBE_COUNT,
            sizing.suggested_whole_tube_count,
            UNIT_SYMBOL_DIMENSIONLESS,
            decimal_places=0,
        ),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_SUGGESTED_BAFFLE_SPACING,
            sizing.suggested_baffle_spacing_meters,
            UNIT_SYMBOL_METER,
        ),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_REQUIRED_FOULED_AREA,
            sizing.required_fouled_area_square_meters,
            UNIT_SYMBOL_SQUARE_METER,
        ),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_OVER_SURFACE_DESIGN_RATIO,
            sizing.over_surface_design_ratio,
            UNIT_SYMBOL_DIMENSIONLESS,
        ),
        "",
        translator.uppercase_text(MessageKey.HEADING_RATING),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_TUBE_SIDE_COEFFICIENT,
            evaluation.tube_side.heat_transfer_coefficient_watts_per_square_meter_kelvin,
            UNIT_SYMBOL_WATTS_PER_SQUARE_METER_KELVIN,
        ),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_SHELL_SIDE_COEFFICIENT,
            evaluation.shell_side.heat_transfer_coefficient_watts_per_square_meter_kelvin,
            UNIT_SYMBOL_WATTS_PER_SQUARE_METER_KELVIN,
        ),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_TUBE_SIDE_REYNOLDS_NUMBER,
            evaluation.tube_side.reynolds_number,
            UNIT_SYMBOL_DIMENSIONLESS,
        ),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_SHELL_SIDE_REYNOLDS_NUMBER,
            evaluation.shell_side.reynolds_number,
            UNIT_SYMBOL_DIMENSIONLESS,
        ),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_OVERALL_COEFFICIENT_FOULED,
            rated.fouled_watts_per_square_meter_kelvin,
            UNIT_SYMBOL_WATTS_PER_SQUARE_METER_KELVIN,
        ),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_OVER_SURFACE_DESIGN_RATIO,
            rated.over_surface_design_ratio,
            UNIT_SYMBOL_DIMENSIONLESS,
        ),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_TUBE_SIDE_PRESSURE_DROP,
            evaluation.tube_side.pressure_drop_pascal / PASCAL_PER_KILOPASCAL,
            UNIT_SYMBOL_KILOPASCAL,
        ),
        _value_line(
            translator,
            label_width,
            MessageKey.RESULT_SHELL_SIDE_PRESSURE_DROP,
            evaluation.shell_side.pressure_drop_pascal / PASCAL_PER_KILOPASCAL,
            UNIT_SYMBOL_KILOPASCAL,
        ),
        "",
        translator.uppercase_text(MessageKey.HEADING_COEFFICIENT_CONVERGENCE),
        _convergence_line(
            translator,
            label_width,
            MessageKey.RESULT_TUBE_SIDE_COEFFICIENT_ROW,
            convergence.assumed_tube_side_watts_per_square_meter_kelvin,
            convergence.computed_tube_side_watts_per_square_meter_kelvin,
            convergence.tube_side_relative_difference,
        ),
        _convergence_line(
            translator,
            label_width,
            MessageKey.RESULT_SHELL_SIDE_COEFFICIENT_ROW,
            convergence.assumed_shell_side_watts_per_square_meter_kelvin,
            convergence.computed_shell_side_watts_per_square_meter_kelvin,
            convergence.shell_side_relative_difference,
        ),
        "  "
        + translator.text(
            MessageKey.REPORT_CONVERGED, tolerance=CONVERGENCE_TOLERANCE_PERCENT_TEXT
        ).ljust(label_width)
        + (
            translator.text(MessageKey.CHECK_SATISFIED)
            if convergence.has_converged()
            else translator.text(MessageKey.STATUS_NOT_CONVERGED)
        ).rjust(VALUE_COLUMN_CHARACTERS),
        "  "
        + translator.text(MessageKey.CHECK_LINE_GEOMETRY_MATCHES).ljust(label_width)
        + (
            translator.text(MessageKey.CHECK_SATISFIED)
            if agreement.entered_matches_suggested()
            else translator.text(
                MessageKey.REPORT_DIFFERS_BY,
                gap=f"{agreement.largest_relative_difference * PERCENT_PER_FRACTION:.1f}",
            )
        ).rjust(VALUE_COLUMN_CHARACTERS),
        "",
        translator.uppercase_text(MessageKey.HEADING_STANDARDS_AND_ENVELOPE),
    ]

    allowed_word = translator.text(MessageKey.REPORT_ALLOWED)
    for check in evaluation.constraint_checks:
        lines.append(
            f"  {check.quantity_text(translator):<{label_width}}"
            f"{check.actual_value:>{VALUE_COLUMN_CHARACTERS}.4f} {check.unit:<6}"
            f"{allowed_word} {check.allowed_range_text(translator):<16}"
            f"{check.standard_text(translator):<18}{check.outcome_text(translator)}"
        )

    notes = correlation_notes(evaluation, translator)
    if notes:
        lines.extend(
            [
                "",
                translator.uppercase_text(MessageKey.HEADING_NOTES),
                *(f"  {note}" for note in notes),
            ]
        )

    return "\n".join(lines) + "\n"


def _value_line(
    translator: Translator,
    label_width: int,
    label_key: MessageKey,
    value: float,
    unit: str,
    decimal_places: int = 4,
) -> str:
    label = translator.text(label_key)
    return f"  {label:<{label_width}}{value:>{VALUE_COLUMN_CHARACTERS}.{decimal_places}f} {unit}"


def _convergence_line(
    translator: Translator,
    label_width: int,
    label_key: MessageKey,
    assumed_value: float,
    computed_value: float,
    relative_difference: float,
) -> str:
    label = translator.text(label_key)
    assumed_word = translator.text(MessageKey.COLUMN_ASSUMED)
    computed_word = translator.text(MessageKey.COLUMN_COMPUTED)
    difference_word = translator.text(MessageKey.COLUMN_DIFFERENCE)
    return (
        f"  {label:<{label_width}}{assumed_word} {assumed_value:>10.2f}   "
        f"{computed_word} {computed_value:>10.2f}   "
        f"{difference_word} {relative_difference * PERCENT_PER_FRACTION:>+8.3f} %"
    )
