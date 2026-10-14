from __future__ import annotations

import re
from typing import Any

import pytest

from pool_heat_exchanger_designer.calculation.design_evaluation import (
    DesignEvaluation,
    evaluate_design_case,
)
from pool_heat_exchanger_designer.calculation.properties import (
    LiquidWaterPropertiesInterpolatedFromTable,
)
from pool_heat_exchanger_designer.calculation.thermal import (
    preliminary_sizing_from_assumed_coefficients,
    referred_to_outside_area,
)
from tests.conftest import design_case_from_original_inputs

ORIGINAL_CASE_NAMES = (
    "olimpik_havuz_titanyum_tek_gecis",
    "yuksek_debi_paslanmaz_iki_gecis",
    "kucuk_boru_dusuk_debi",
    "sinir_yuz_derece_sicak_taraf",
)

UNCHANGED_RELATIVE_TOLERANCE = 1.0e-12
PRANDTL_ROUNDING_RELATIVE_TOLERANCE = 3.0e-3
REPORT_ROUNDING_RELATIVE_TOLERANCE = 5.0e-3


def _evaluate(
    original_implementation_behaviour: dict[str, Any],
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
    case_name: str,
) -> tuple[dict[str, Any], DesignEvaluation]:
    record = original_implementation_behaviour[case_name]
    design_case = design_case_from_original_inputs(case_name, record["inputs"])
    return record, evaluate_design_case(property_source, design_case)


def _pressure_drops_from_original_report_kilopascal(
    report_text: str,
) -> tuple[float, float]:
    numbers = re.search(
        r"ube side pressure drop:\s*([-\d.]+)\s*kPa\s+"
        r"Shell side pressure drop:\s*([-\d.]+)\s*kPa",
        report_text,
    )
    assert numbers is not None, report_text
    return float(numbers.group(1)), float(numbers.group(2))


@pytest.mark.parametrize("case_name", ORIGINAL_CASE_NAMES)
def test_the_energy_balance_is_unchanged(
    original_implementation_behaviour: dict[str, Any],
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
    case_name: str,
) -> None:
    record, evaluation = _evaluate(original_implementation_behaviour, property_source, case_name)
    outputs = record["outputs"]

    assert evaluation.thermal_duty.heat_duty_watts == pytest.approx(
        outputs["heat_duty_watts"], rel=UNCHANGED_RELATIVE_TOLERANCE
    )
    assert evaluation.thermal_duty.shell_side_outlet_temperature_celsius == pytest.approx(
        outputs["shell_outlet_temperature_celsius"],
        rel=UNCHANGED_RELATIVE_TOLERANCE,
    )
    assert evaluation.thermal_duty.tube_side_bulk_temperature_celsius == pytest.approx(
        outputs["cold_bulk_temperature_celsius"],
        rel=UNCHANGED_RELATIVE_TOLERANCE,
    )
    assert evaluation.thermal_duty.shell_side_bulk_temperature_celsius == pytest.approx(
        outputs["hot_bulk_temperature_celsius"],
        rel=UNCHANGED_RELATIVE_TOLERANCE,
    )


@pytest.mark.parametrize("case_name", ORIGINAL_CASE_NAMES)
def test_the_interpolated_water_properties_are_unchanged(
    original_implementation_behaviour: dict[str, Any],
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
    case_name: str,
) -> None:
    record, evaluation = _evaluate(original_implementation_behaviour, property_source, case_name)
    tube_side = evaluation.thermal_duty.tube_side_properties
    shell_side = evaluation.thermal_duty.shell_side_properties
    original_tube_side = record["outputs"]["cold_bulk_properties"]
    original_shell_side = record["outputs"]["hot_bulk_properties"]

    for computed, original in (
        (tube_side.density_kilograms_per_cubic_meter, original_tube_side["Density"]),
        (
            tube_side.specific_heat_joules_per_kilogram_kelvin,
            original_tube_side["Cp"],
        ),
        (
            tube_side.dynamic_viscosity_pascal_seconds,
            original_tube_side["Viscosity"],
        ),
        (
            tube_side.thermal_conductivity_watts_per_meter_kelvin,
            original_tube_side["K"],
        ),
        (tube_side.prandtl_number, original_tube_side["Pr"]),
        (
            shell_side.density_kilograms_per_cubic_meter,
            original_shell_side["Density"],
        ),
        (
            shell_side.dynamic_viscosity_pascal_seconds,
            original_shell_side["Viscosity"],
        ),
        (shell_side.prandtl_number, original_shell_side["Pr"]),
    ):
        assert computed == pytest.approx(original, rel=UNCHANGED_RELATIVE_TOLERANCE, abs=1.0e-15)


@pytest.mark.parametrize("case_name", ORIGINAL_CASE_NAMES)
def test_the_corrected_log_mean_temperature_difference_is_unchanged(
    original_implementation_behaviour: dict[str, Any],
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
    case_name: str,
) -> None:
    record, evaluation = _evaluate(original_implementation_behaviour, property_source, case_name)
    assert evaluation.corrected_log_mean_temperature_difference_kelvin == pytest.approx(
        record["outputs"]["preliminary"]["corrected_log_mean_temperature_difference"],
        rel=UNCHANGED_RELATIVE_TOLERANCE,
    )


@pytest.mark.parametrize("case_name", ORIGINAL_CASE_NAMES)
def test_the_tube_side_heat_transfer_coefficient_is_unchanged(
    original_implementation_behaviour: dict[str, Any],
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
    case_name: str,
) -> None:
    record, evaluation = _evaluate(original_implementation_behaviour, property_source, case_name)
    assert (
        evaluation.tube_side.heat_transfer_coefficient_watts_per_square_meter_kelvin
        == pytest.approx(
            record["outputs"]["rating"]["tube_side_coefficient"],
            rel=UNCHANGED_RELATIVE_TOLERANCE,
        )
    )


@pytest.mark.parametrize("case_name", ORIGINAL_CASE_NAMES)
def test_the_shell_side_reynolds_number_is_unchanged(
    original_implementation_behaviour: dict[str, Any],
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
    case_name: str,
) -> None:
    record, evaluation = _evaluate(original_implementation_behaviour, property_source, case_name)
    assert evaluation.shell_side.reynolds_number == pytest.approx(
        record["outputs"]["rating"]["shell_side_reynolds_number"],
        rel=UNCHANGED_RELATIVE_TOLERANCE,
    )


@pytest.mark.parametrize("case_name", ORIGINAL_CASE_NAMES)
def test_the_shell_side_heat_transfer_coefficient_changed_only_by_the_prandtl_rounding(
    original_implementation_behaviour: dict[str, Any],
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
    case_name: str,
) -> None:
    record, evaluation = _evaluate(original_implementation_behaviour, property_source, case_name)
    assert (
        evaluation.shell_side.heat_transfer_coefficient_watts_per_square_meter_kelvin
        == pytest.approx(
            record["outputs"]["rating"]["shell_side_coefficient"],
            rel=PRANDTL_ROUNDING_RELATIVE_TOLERANCE,
        )
    )


@pytest.mark.parametrize("case_name", ORIGINAL_CASE_NAMES)
def test_the_suggested_sizing_differs_only_because_the_original_swapped_the_two_film_coefficients(
    original_implementation_behaviour: dict[str, Any],
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
    case_name: str,
) -> None:
    record, evaluation = _evaluate(original_implementation_behaviour, property_source, case_name)
    design_case = evaluation.design_case
    bundle = design_case.tube_bundle
    material = design_case.tube_wall_material
    assumed = design_case.assumed_heat_transfer_coefficients

    coefficients_with_the_original_swap = referred_to_outside_area(
        shell_side_coefficient_watts_per_square_meter_kelvin=(
            assumed.tube_side_watts_per_square_meter_kelvin
        ),
        tube_side_coefficient_watts_per_square_meter_kelvin=(
            assumed.shell_side_watts_per_square_meter_kelvin
        ),
        tube_outer_radius_meters=bundle.tube.outer_radius_meters,
        tube_inner_radius_meters=bundle.tube.inner_radius_meters,
        wall_thermal_conductivity_watts_per_meter_kelvin=(
            material.thermal_conductivity_watts_per_meter_kelvin
        ),
        fouling_resistance_square_meter_kelvin_per_watt=(
            material.fouling_resistance_square_meter_kelvin_per_watt
        ),
    )
    sizing_reproducing_the_original = preliminary_sizing_from_assumed_coefficients(
        heat_duty_watts=evaluation.thermal_duty.heat_duty_watts,
        corrected_log_mean_temperature_difference_kelvin=(
            evaluation.corrected_log_mean_temperature_difference_kelvin
        ),
        clean_overall_coefficient_watts_per_square_meter_kelvin=(
            coefficients_with_the_original_swap.clean_watts_per_square_meter_kelvin
        ),
        fouled_overall_coefficient_watts_per_square_meter_kelvin=(
            coefficients_with_the_original_swap.fouled_watts_per_square_meter_kelvin
        ),
        tube_outer_diameter_meters=bundle.tube_outer_diameter_meters,
        tube_length_meters=bundle.tube_length_meters,
        pitch_ratio=bundle.pitch_ratio,
        pitch_layout=bundle.pitch_layout,
        tube_count_calculation_constant=bundle.tube_count_calculation_constant,
    )

    original_preliminary = record["outputs"]["preliminary"]
    assert sizing_reproducing_the_original.suggested_shell_inner_diameter_meters == pytest.approx(
        original_preliminary["suggested_shell_diameter_meters"],
        rel=UNCHANGED_RELATIVE_TOLERANCE,
    )
    assert sizing_reproducing_the_original.suggested_tube_count == pytest.approx(
        original_preliminary["suggested_tube_count"],
        rel=UNCHANGED_RELATIVE_TOLERANCE,
    )

    assumed_coefficients_are_equal = (
        assumed.tube_side_watts_per_square_meter_kelvin
        == assumed.shell_side_watts_per_square_meter_kelvin
    )
    sizing_now = evaluation.preliminary_sizing
    if assumed_coefficients_are_equal:
        assert sizing_now.suggested_shell_inner_diameter_meters == pytest.approx(
            original_preliminary["suggested_shell_diameter_meters"],
            rel=UNCHANGED_RELATIVE_TOLERANCE,
        )
    else:
        assert sizing_now.suggested_shell_inner_diameter_meters != pytest.approx(
            original_preliminary["suggested_shell_diameter_meters"],
            rel=1.0e-6,
        )


@pytest.mark.parametrize("case_name", ORIGINAL_CASE_NAMES)
def test_the_shell_side_pressure_drop_is_exactly_half_the_original_which_omitted_the_factor_two(
    original_implementation_behaviour: dict[str, Any],
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
    case_name: str,
) -> None:
    record, evaluation = _evaluate(original_implementation_behaviour, property_source, case_name)
    _, original_shell_side_kilopascal = _pressure_drops_from_original_report_kilopascal(
        record["outputs"]["final_report_text"]
    )
    rewritten_shell_side_kilopascal = evaluation.shell_side.pressure_drop_pascal / 1.0e3

    assert original_shell_side_kilopascal / rewritten_shell_side_kilopascal == (
        pytest.approx(2.0, rel=REPORT_ROUNDING_RELATIVE_TOLERANCE)
    )


@pytest.mark.parametrize("case_name", ORIGINAL_CASE_NAMES)
def test_the_tube_side_pressure_drop_grew_because_the_original_used_the_shell_side_mass_flux(
    original_implementation_behaviour: dict[str, Any],
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
    case_name: str,
) -> None:
    record, evaluation = _evaluate(original_implementation_behaviour, property_source, case_name)
    original_tube_side_kilopascal, _ = _pressure_drops_from_original_report_kilopascal(
        record["outputs"]["final_report_text"]
    )
    rewritten_tube_side_kilopascal = evaluation.tube_side.pressure_drop_pascal / 1.0e3

    assert rewritten_tube_side_kilopascal > original_tube_side_kilopascal
    assert (
        evaluation.tube_side.mass_flux_kilograms_per_square_meter_second
        > record["outputs"]["rating"]["shell_mass_flux"]
    )
