from __future__ import annotations

import math
from dataclasses import dataclass

from pool_heat_exchanger_designer.calculation.design_errors import InvalidOperatingConditionError
from pool_heat_exchanger_designer.calculation.geometry import PitchLayout
from pool_heat_exchanger_designer.calculation.message_catalogue import MessageKey
from pool_heat_exchanger_designer.calculation.properties import (
    LiquidWaterProperties,
    LiquidWaterPropertySource,
)

SHELL_OUTLET_TEMPERATURE_CONVERGENCE_TOLERANCE_KELVIN = 1.0e-9
SHELL_OUTLET_TEMPERATURE_MAXIMUM_ITERATIONS = 50

EQUAL_TERMINAL_DIFFERENCE_TOLERANCE_KELVIN = 1.0e-9
DEFAULT_CORRECTION_FACTOR = 0.9

_SHELL_DIAMETER_LEADING_CONSTANT = 0.637
_TUBE_COUNT_LEADING_CONSTANT = 0.785
BAFFLE_SPACING_FRACTION_OF_SHELL_DIAMETER_FOR_TWENTY_FIVE_PERCENT_CUT = 0.6


@dataclass(frozen=True, slots=True)
class ThermalDuty:
    heat_duty_watts: float
    tube_side_bulk_temperature_celsius: float
    tube_side_properties: LiquidWaterProperties
    shell_side_outlet_temperature_celsius: float
    shell_side_bulk_temperature_celsius: float
    shell_side_properties: LiquidWaterProperties


def bulk_temperature_celsius(
    inlet_temperature_celsius: float, outlet_temperature_celsius: float
) -> float:
    return (inlet_temperature_celsius + outlet_temperature_celsius) / 2.0


def heat_duty_watts(
    mass_flow_rate_kilograms_per_second: float,
    specific_heat_joules_per_kilogram_kelvin: float,
    inlet_temperature_celsius: float,
    outlet_temperature_celsius: float,
) -> float:
    return (
        mass_flow_rate_kilograms_per_second
        * specific_heat_joules_per_kilogram_kelvin
        * (outlet_temperature_celsius - inlet_temperature_celsius)
    )


def thermal_duty_from_tube_side_temperature_rise(
    property_source: LiquidWaterPropertySource,
    tube_side_inlet_temperature_celsius: float,
    tube_side_outlet_temperature_celsius: float,
    tube_side_mass_flow_rate_kilograms_per_second: float,
    shell_side_inlet_temperature_celsius: float,
    shell_side_mass_flow_rate_kilograms_per_second: float,
) -> ThermalDuty:
    _reject_infeasible_temperature_rise(
        tube_side_inlet_temperature_celsius,
        tube_side_outlet_temperature_celsius,
        shell_side_inlet_temperature_celsius,
    )
    _reject_non_positive_mass_flow_rates(
        tube_side_mass_flow_rate_kilograms_per_second,
        shell_side_mass_flow_rate_kilograms_per_second,
    )

    tube_side_bulk_temperature = bulk_temperature_celsius(
        tube_side_inlet_temperature_celsius, tube_side_outlet_temperature_celsius
    )
    tube_side_properties = property_source.at_temperature_celsius(tube_side_bulk_temperature)
    duty_watts = heat_duty_watts(
        tube_side_mass_flow_rate_kilograms_per_second,
        tube_side_properties.specific_heat_joules_per_kilogram_kelvin,
        tube_side_inlet_temperature_celsius,
        tube_side_outlet_temperature_celsius,
    )

    shell_side_outlet_temperature = (
        _shell_side_outlet_temperature_converged_with_its_own_properties(
            property_source,
            duty_watts,
            shell_side_inlet_temperature_celsius,
            shell_side_mass_flow_rate_kilograms_per_second,
        )
    )
    shell_side_bulk_temperature = bulk_temperature_celsius(
        shell_side_inlet_temperature_celsius, shell_side_outlet_temperature
    )

    return ThermalDuty(
        heat_duty_watts=duty_watts,
        tube_side_bulk_temperature_celsius=tube_side_bulk_temperature,
        tube_side_properties=tube_side_properties,
        shell_side_outlet_temperature_celsius=shell_side_outlet_temperature,
        shell_side_bulk_temperature_celsius=shell_side_bulk_temperature,
        shell_side_properties=property_source.at_temperature_celsius(shell_side_bulk_temperature),
    )


def _shell_side_outlet_temperature_converged_with_its_own_properties(
    property_source: LiquidWaterPropertySource,
    duty_watts: float,
    shell_side_inlet_temperature_celsius: float,
    shell_side_mass_flow_rate_kilograms_per_second: float,
) -> float:
    specific_heat = property_source.at_temperature_celsius(
        shell_side_inlet_temperature_celsius
    ).specific_heat_joules_per_kilogram_kelvin
    outlet_temperature = shell_side_inlet_temperature_celsius

    for _ in range(SHELL_OUTLET_TEMPERATURE_MAXIMUM_ITERATIONS):
        previous_outlet_temperature = outlet_temperature
        outlet_temperature = shell_side_inlet_temperature_celsius - duty_watts / (
            specific_heat * shell_side_mass_flow_rate_kilograms_per_second
        )
        specific_heat = property_source.at_temperature_celsius(
            bulk_temperature_celsius(shell_side_inlet_temperature_celsius, outlet_temperature)
        ).specific_heat_joules_per_kilogram_kelvin
        if (
            abs(outlet_temperature - previous_outlet_temperature)
            < SHELL_OUTLET_TEMPERATURE_CONVERGENCE_TOLERANCE_KELVIN
        ):
            return outlet_temperature

    raise InvalidOperatingConditionError(MessageKey.SHELL_SIDE_OUTLET_TEMPERATURE_DID_NOT_CONVERGE)


def _reject_infeasible_temperature_rise(
    tube_side_inlet_temperature_celsius: float,
    tube_side_outlet_temperature_celsius: float,
    shell_side_inlet_temperature_celsius: float,
) -> None:
    if tube_side_outlet_temperature_celsius <= tube_side_inlet_temperature_celsius:
        raise InvalidOperatingConditionError(MessageKey.TUBE_SIDE_OUTLET_MUST_EXCEED_INLET)
    if shell_side_inlet_temperature_celsius <= tube_side_outlet_temperature_celsius:
        raise InvalidOperatingConditionError(
            MessageKey.SHELL_SIDE_INLET_MUST_EXCEED_TUBE_SIDE_OUTLET
        )


def _reject_non_positive_mass_flow_rates(
    tube_side_mass_flow_rate_kilograms_per_second: float,
    shell_side_mass_flow_rate_kilograms_per_second: float,
) -> None:
    if tube_side_mass_flow_rate_kilograms_per_second <= 0.0:
        raise InvalidOperatingConditionError(MessageKey.TUBE_SIDE_MASS_FLOW_RATE_MUST_BE_POSITIVE)
    if shell_side_mass_flow_rate_kilograms_per_second <= 0.0:
        raise InvalidOperatingConditionError(MessageKey.SHELL_SIDE_MASS_FLOW_RATE_MUST_BE_POSITIVE)


def counterflow_log_mean_temperature_difference_kelvin(
    shell_side_inlet_temperature_celsius: float,
    shell_side_outlet_temperature_celsius: float,
    tube_side_inlet_temperature_celsius: float,
    tube_side_outlet_temperature_celsius: float,
) -> float:
    inlet_end_difference = (
        shell_side_inlet_temperature_celsius - tube_side_outlet_temperature_celsius
    )
    outlet_end_difference = (
        shell_side_outlet_temperature_celsius - tube_side_inlet_temperature_celsius
    )

    if inlet_end_difference <= 0.0 or outlet_end_difference <= 0.0:
        raise InvalidOperatingConditionError(
            MessageKey.TERMINAL_TEMPERATURE_DIFFERENCES_MUST_BE_POSITIVE
        )

    if (
        abs(inlet_end_difference - outlet_end_difference)
        < EQUAL_TERMINAL_DIFFERENCE_TOLERANCE_KELVIN
    ):
        return inlet_end_difference

    return (inlet_end_difference - outlet_end_difference) / math.log(
        inlet_end_difference / outlet_end_difference
    )


def corrected_log_mean_temperature_difference_kelvin(
    shell_side_inlet_temperature_celsius: float,
    shell_side_outlet_temperature_celsius: float,
    tube_side_inlet_temperature_celsius: float,
    tube_side_outlet_temperature_celsius: float,
    correction_factor: float = DEFAULT_CORRECTION_FACTOR,
) -> float:
    if not (0.0 < correction_factor <= 1.0):
        raise InvalidOperatingConditionError(
            MessageKey.CORRECTION_FACTOR_MUST_LIE_IN_THE_UNIT_INTERVAL
        )
    return correction_factor * counterflow_log_mean_temperature_difference_kelvin(
        shell_side_inlet_temperature_celsius,
        shell_side_outlet_temperature_celsius,
        tube_side_inlet_temperature_celsius,
        tube_side_outlet_temperature_celsius,
    )


@dataclass(frozen=True, slots=True)
class OverallHeatTransferCoefficients:
    clean_watts_per_square_meter_kelvin: float
    fouled_watts_per_square_meter_kelvin: float

    @property
    def over_surface_design_ratio(self) -> float:
        return self.clean_watts_per_square_meter_kelvin / self.fouled_watts_per_square_meter_kelvin


def tube_wall_resistance_square_meter_kelvin_per_watt(
    tube_outer_radius_meters: float,
    tube_inner_radius_meters: float,
    wall_thermal_conductivity_watts_per_meter_kelvin: float,
) -> float:
    return (
        tube_outer_radius_meters
        * math.log(tube_outer_radius_meters / tube_inner_radius_meters)
        / wall_thermal_conductivity_watts_per_meter_kelvin
    )


def referred_to_outside_area(
    shell_side_coefficient_watts_per_square_meter_kelvin: float,
    tube_side_coefficient_watts_per_square_meter_kelvin: float,
    tube_outer_radius_meters: float,
    tube_inner_radius_meters: float,
    wall_thermal_conductivity_watts_per_meter_kelvin: float,
    fouling_resistance_square_meter_kelvin_per_watt: float,
) -> OverallHeatTransferCoefficients:
    shell_side_resistance = 1.0 / shell_side_coefficient_watts_per_square_meter_kelvin
    tube_side_resistance = (
        tube_outer_radius_meters / tube_inner_radius_meters
    ) / tube_side_coefficient_watts_per_square_meter_kelvin
    wall_resistance = tube_wall_resistance_square_meter_kelvin_per_watt(
        tube_outer_radius_meters,
        tube_inner_radius_meters,
        wall_thermal_conductivity_watts_per_meter_kelvin,
    )

    clean_resistance = shell_side_resistance + tube_side_resistance + wall_resistance
    fouled_resistance = clean_resistance + fouling_resistance_square_meter_kelvin_per_watt

    return OverallHeatTransferCoefficients(
        clean_watts_per_square_meter_kelvin=1.0 / clean_resistance,
        fouled_watts_per_square_meter_kelvin=1.0 / fouled_resistance,
    )


@dataclass(frozen=True, slots=True)
class PreliminarySizing:
    required_clean_area_square_meters: float
    required_fouled_area_square_meters: float
    suggested_shell_inner_diameter_meters: float
    suggested_tube_count: float
    suggested_baffle_spacing_meters: float

    @property
    def over_surface_design_ratio(self) -> float:
        return self.required_fouled_area_square_meters / self.required_clean_area_square_meters

    @property
    def suggested_whole_tube_count(self) -> int:
        return math.ceil(self.suggested_tube_count)


def required_area_square_meters(
    heat_duty_watts: float,
    overall_heat_transfer_coefficient_watts_per_square_meter_kelvin: float,
    corrected_log_mean_temperature_difference_kelvin: float,
) -> float:
    return heat_duty_watts / (
        overall_heat_transfer_coefficient_watts_per_square_meter_kelvin
        * corrected_log_mean_temperature_difference_kelvin
    )


def shell_inner_diameter_meters(
    required_area_square_meters_value: float,
    tube_outer_diameter_meters: float,
    tube_length_meters: float,
    pitch_ratio: float,
    pitch_layout: PitchLayout,
    tube_count_calculation_constant: float,
) -> float:
    return (
        _SHELL_DIAMETER_LEADING_CONSTANT
        * math.sqrt(pitch_layout.tube_layout_constant / tube_count_calculation_constant)
        * math.sqrt(
            required_area_square_meters_value
            * pitch_ratio**2
            * tube_outer_diameter_meters
            / tube_length_meters
        )
    )


def tube_count(
    shell_inner_diameter_meters_value: float,
    tube_outer_diameter_meters: float,
    pitch_ratio: float,
    pitch_layout: PitchLayout,
    tube_count_calculation_constant: float,
) -> float:
    return (
        _TUBE_COUNT_LEADING_CONSTANT
        * (tube_count_calculation_constant / pitch_layout.tube_layout_constant)
        * shell_inner_diameter_meters_value**2
        / (pitch_ratio**2 * tube_outer_diameter_meters**2)
    )


def preliminary_sizing_from_assumed_coefficients(
    heat_duty_watts: float,
    corrected_log_mean_temperature_difference_kelvin: float,
    clean_overall_coefficient_watts_per_square_meter_kelvin: float,
    fouled_overall_coefficient_watts_per_square_meter_kelvin: float,
    tube_outer_diameter_meters: float,
    tube_length_meters: float,
    pitch_ratio: float,
    pitch_layout: PitchLayout,
    tube_count_calculation_constant: float,
) -> PreliminarySizing:
    clean_area = required_area_square_meters(
        heat_duty_watts,
        clean_overall_coefficient_watts_per_square_meter_kelvin,
        corrected_log_mean_temperature_difference_kelvin,
    )
    fouled_area = required_area_square_meters(
        heat_duty_watts,
        fouled_overall_coefficient_watts_per_square_meter_kelvin,
        corrected_log_mean_temperature_difference_kelvin,
    )
    suggested_shell_diameter = shell_inner_diameter_meters(
        fouled_area,
        tube_outer_diameter_meters,
        tube_length_meters,
        pitch_ratio,
        pitch_layout,
        tube_count_calculation_constant,
    )
    return PreliminarySizing(
        required_clean_area_square_meters=clean_area,
        required_fouled_area_square_meters=fouled_area,
        suggested_shell_inner_diameter_meters=suggested_shell_diameter,
        suggested_tube_count=tube_count(
            suggested_shell_diameter,
            tube_outer_diameter_meters,
            pitch_ratio,
            pitch_layout,
            tube_count_calculation_constant,
        ),
        suggested_baffle_spacing_meters=(
            suggested_shell_diameter
            * BAFFLE_SPACING_FRACTION_OF_SHELL_DIAMETER_FOR_TWENTY_FIVE_PERCENT_CUT
        ),
    )
