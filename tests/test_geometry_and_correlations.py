from __future__ import annotations

from typing import Any

import pytest

from pool_heat_exchanger_designer import (
    PitchLayout,
    ShellGeometry,
    TubeBundleGeometry,
    TubeGeometry,
)
from pool_heat_exchanger_designer.calculation import (
    shell_side_correlations,
    tube_side_correlations,
)
from pool_heat_exchanger_designer.calculation.design_errors import (
    InvalidGeometryError,
    InvalidOperatingConditionError,
)
from pool_heat_exchanger_designer.calculation.properties import (
    TITANIUM_ALLOY,
    tube_wall_material_named,
)
from pool_heat_exchanger_designer.calculation.thermal import (
    corrected_log_mean_temperature_difference_kelvin,
    counterflow_log_mean_temperature_difference_kelvin,
    referred_to_outside_area,
)


def a_tube() -> TubeGeometry:
    return TubeGeometry(
        outer_diameter_meters=0.019,
        inner_diameter_meters=0.016,
        length_meters=6.0,
    )


def a_bundle(**overrides: Any) -> TubeBundleGeometry:
    arguments: dict[str, Any] = {
        "tube": a_tube(),
        "tube_count": 700,
        "tube_side_pass_count": 1,
        "pitch_ratio": 1.25,
        "pitch_layout": PitchLayout.TRIANGULAR,
    }
    arguments.update(overrides)
    return TubeBundleGeometry(**arguments)


def test_a_tube_whose_inner_diameter_is_not_smaller_than_its_outer_diameter_is_refused() -> None:
    with pytest.raises(InvalidGeometryError, match="outer diameter must exceed"):
        TubeGeometry(
            outer_diameter_meters=0.016,
            inner_diameter_meters=0.016,
            length_meters=6.0,
        )


@pytest.mark.parametrize("pitch_ratio", [0.5, 1.0])
def test_a_pitch_ratio_that_would_overlap_adjacent_tubes_is_refused(
    pitch_ratio: float,
) -> None:
    with pytest.raises(InvalidGeometryError, match="Pitch ratio must exceed one"):
        a_bundle(pitch_ratio=pitch_ratio)


@pytest.mark.parametrize("tube_side_pass_count", [0, 3, 4])
def test_an_unsupported_tube_side_pass_count_is_refused(
    tube_side_pass_count: int,
) -> None:
    with pytest.raises(InvalidGeometryError, match="pass count must be one of"):
        a_bundle(tube_side_pass_count=tube_side_pass_count)


def test_the_pitch_and_the_clearance_follow_from_the_pitch_ratio() -> None:
    bundle = a_bundle(pitch_ratio=1.25)

    assert bundle.pitch_meters == pytest.approx(1.25 * 0.019)
    assert bundle.clearance_between_adjacent_tubes_meters == pytest.approx(1.25 * 0.019 - 0.019)


def test_the_tube_side_flow_area_halves_when_the_pass_count_doubles() -> None:
    one_pass = a_bundle(tube_side_pass_count=1)
    two_pass = a_bundle(tube_side_pass_count=2)

    assert two_pass.tube_side_flow_area_per_pass_square_meters == pytest.approx(
        one_pass.tube_side_flow_area_per_pass_square_meters / 2.0
    )


def test_the_square_and_the_triangular_layout_carry_the_textbook_layout_constants() -> None:
    assert PitchLayout.SQUARE.tube_layout_constant == 1.0
    assert PitchLayout.TRIANGULAR.tube_layout_constant == 0.87


def test_the_baffle_count_follows_from_the_tube_length_and_the_baffle_spacing() -> None:
    shell = ShellGeometry(inner_diameter_meters=0.9, baffle_spacing_meters=0.5)

    assert shell.baffle_count_over_tube_length(6.0) == pytest.approx(11.0)


@pytest.mark.parametrize("baffle_spacing_meters", [0.0, -0.1])
def test_a_non_positive_baffle_spacing_is_refused(baffle_spacing_meters: float) -> None:
    with pytest.raises(InvalidGeometryError, match="Baffle spacing must be positive"):
        ShellGeometry(inner_diameter_meters=0.9, baffle_spacing_meters=baffle_spacing_meters)


def test_the_two_pitch_layouts_give_different_equivalent_diameters() -> None:
    square = shell_side_correlations.equivalent_diameter_meters(0.02375, 0.019, PitchLayout.SQUARE)
    triangular = shell_side_correlations.equivalent_diameter_meters(
        0.02375, 0.019, PitchLayout.TRIANGULAR
    )

    assert square > 0.0
    assert triangular > 0.0
    assert square != pytest.approx(triangular)


def test_the_petukhov_friction_factor_falls_as_the_reynolds_number_rises() -> None:
    at_ten_thousand = tube_side_correlations.petukhov_smooth_tube_fanning_friction_factor(1.0e4)
    at_one_hundred_thousand = tube_side_correlations.petukhov_smooth_tube_fanning_friction_factor(
        1.0e5
    )

    assert at_ten_thousand > at_one_hundred_thousand > 0.0


def test_a_reynolds_number_too_low_for_the_petukhov_friction_factor_is_refused() -> None:
    with pytest.raises(InvalidOperatingConditionError, match="too low"):
        tube_side_correlations.petukhov_smooth_tube_fanning_friction_factor(5.0)


@pytest.mark.parametrize(
    ("reynolds_number", "prandtl_number", "inside_range"),
    [
        (1.0e4, 5.0, True),
        (5.0e4, 5.0, True),
        (9.9e3, 5.0, False),
        (1.0e4, 0.2, False),
        (1.0e4, 3000.0, False),
    ],
)
def test_the_gnielinski_validity_window_is_reported_rather_than_enforced(
    reynolds_number: float, prandtl_number: float, inside_range: bool
) -> None:
    assert (
        tube_side_correlations.gnielinski_was_applied_inside_its_validated_range(
            reynolds_number, prandtl_number
        )
        is inside_range
    )


@pytest.mark.parametrize(
    ("reynolds_number", "inside_range"),
    [(2.0e3, True), (5.0e4, True), (1.9e3, False), (1.1e6, False)],
)
def test_the_kern_validity_window_is_reported_rather_than_enforced(
    reynolds_number: float, inside_range: bool
) -> None:
    assert (
        shell_side_correlations.kern_was_applied_inside_its_validated_range(reynolds_number)
        is inside_range
    )


def test_equal_terminal_differences_return_that_difference_not_a_division_by_zero() -> None:
    difference = counterflow_log_mean_temperature_difference_kelvin(
        shell_side_inlet_temperature_celsius=60.0,
        shell_side_outlet_temperature_celsius=40.0,
        tube_side_inlet_temperature_celsius=20.0,
        tube_side_outlet_temperature_celsius=40.0,
    )

    assert difference == pytest.approx(20.0)


def test_the_log_mean_temperature_difference_lies_between_the_two_terminal_differences() -> None:
    difference = counterflow_log_mean_temperature_difference_kelvin(
        shell_side_inlet_temperature_celsius=80.0,
        shell_side_outlet_temperature_celsius=50.0,
        tube_side_inlet_temperature_celsius=13.0,
        tube_side_outlet_temperature_celsius=28.0,
    )

    assert 37.0 < difference < 52.0


def test_temperatures_that_would_need_heat_to_flow_from_cold_to_hot_are_refused() -> None:
    with pytest.raises(InvalidOperatingConditionError, match="cold to hot"):
        counterflow_log_mean_temperature_difference_kelvin(
            shell_side_inlet_temperature_celsius=30.0,
            shell_side_outlet_temperature_celsius=25.0,
            tube_side_inlet_temperature_celsius=20.0,
            tube_side_outlet_temperature_celsius=40.0,
        )


def test_the_correction_factor_scales_the_log_mean_temperature_difference() -> None:
    uncorrected = counterflow_log_mean_temperature_difference_kelvin(80.0, 50.0, 13.0, 28.0)
    corrected = corrected_log_mean_temperature_difference_kelvin(
        80.0, 50.0, 13.0, 28.0, correction_factor=0.9
    )

    assert corrected == pytest.approx(0.9 * uncorrected)


@pytest.mark.parametrize("correction_factor", [0.0, -0.5, 1.5])
def test_a_correction_factor_outside_the_unit_interval_is_refused(
    correction_factor: float,
) -> None:
    with pytest.raises(InvalidOperatingConditionError, match="correction factor"):
        corrected_log_mean_temperature_difference_kelvin(
            80.0, 50.0, 13.0, 28.0, correction_factor=correction_factor
        )


def test_fouling_always_lowers_the_overall_heat_transfer_coefficient() -> None:
    coefficients = referred_to_outside_area(
        shell_side_coefficient_watts_per_square_meter_kelvin=3000.0,
        tube_side_coefficient_watts_per_square_meter_kelvin=1400.0,
        tube_outer_radius_meters=0.0095,
        tube_inner_radius_meters=0.008,
        wall_thermal_conductivity_watts_per_meter_kelvin=(
            TITANIUM_ALLOY.thermal_conductivity_watts_per_meter_kelvin
        ),
        fouling_resistance_square_meter_kelvin_per_watt=(
            TITANIUM_ALLOY.fouling_resistance_square_meter_kelvin_per_watt
        ),
    )

    assert (
        coefficients.fouled_watts_per_square_meter_kelvin
        < coefficients.clean_watts_per_square_meter_kelvin
    )
    assert coefficients.over_surface_design_ratio > 1.0


def test_the_overall_coefficient_is_not_symmetric_in_the_two_film_coefficients() -> None:
    arguments = {
        "tube_outer_radius_meters": 0.0095,
        "tube_inner_radius_meters": 0.008,
        "wall_thermal_conductivity_watts_per_meter_kelvin": 25.0,
        "fouling_resistance_square_meter_kelvin_per_watt": 5.0e-05,
    }
    one_way = referred_to_outside_area(
        shell_side_coefficient_watts_per_square_meter_kelvin=3000.0,
        tube_side_coefficient_watts_per_square_meter_kelvin=1400.0,
        **arguments,
    )
    the_other_way = referred_to_outside_area(
        shell_side_coefficient_watts_per_square_meter_kelvin=1400.0,
        tube_side_coefficient_watts_per_square_meter_kelvin=3000.0,
        **arguments,
    )

    assert one_way.fouled_watts_per_square_meter_kelvin != pytest.approx(
        the_other_way.fouled_watts_per_square_meter_kelvin
    )


def test_an_unknown_tube_wall_material_is_refused_with_the_selectable_names() -> None:
    with pytest.raises(InvalidGeometryError, match="titanium alloy, stainless steel"):
        tube_wall_material_named("copper")
