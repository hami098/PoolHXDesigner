from __future__ import annotations

import math

from pool_heat_exchanger_designer.calculation.design_errors import InvalidOperatingConditionError
from pool_heat_exchanger_designer.calculation.geometry import PitchLayout
from pool_heat_exchanger_designer.calculation.message_catalogue import MessageKey

KERN_MINIMUM_VALID_REYNOLDS_NUMBER = 2.0e3
KERN_MAXIMUM_VALID_REYNOLDS_NUMBER = 1.0e6

_HEAT_TRANSFER_COEFFICIENT_LEADING_CONSTANT = 0.36
_HEAT_TRANSFER_REYNOLDS_EXPONENT = 0.55
_WALL_VISCOSITY_CORRECTION_EXPONENT = 0.14
_PRESSURE_DROP_FRICTION_INTERCEPT = 0.576
_PRESSURE_DROP_FRICTION_SLOPE = 0.19


def equivalent_diameter_meters(
    pitch_meters: float,
    tube_outer_diameter_meters: float,
    pitch_layout: PitchLayout,
) -> float:
    if pitch_layout is PitchLayout.SQUARE:
        return (
            4.0
            * (pitch_meters**2 - math.pi * tube_outer_diameter_meters**2 / 4.0)
            / (math.pi * tube_outer_diameter_meters)
        )
    return (
        4.0
        * (pitch_meters**2 * math.sqrt(3.0) / 4.0 - math.pi * tube_outer_diameter_meters**2 / 8.0)
        / (math.pi * tube_outer_diameter_meters / 2.0)
    )


def crossflow_area_square_meters(
    shell_inner_diameter_meters: float,
    clearance_between_adjacent_tubes_meters: float,
    baffle_spacing_meters: float,
    pitch_meters: float,
) -> float:
    return (
        shell_inner_diameter_meters
        * clearance_between_adjacent_tubes_meters
        * baffle_spacing_meters
        / pitch_meters
    )


def mass_flux_kilograms_per_square_meter_second(
    mass_flow_rate_kilograms_per_second: float, crossflow_area_square_meters_value: float
) -> float:
    if crossflow_area_square_meters_value <= 0.0:
        raise InvalidOperatingConditionError(MessageKey.SHELL_SIDE_CROSSFLOW_AREA_MUST_BE_POSITIVE)
    return mass_flow_rate_kilograms_per_second / crossflow_area_square_meters_value


def reynolds_number(
    mass_flux_kilograms_per_square_meter_second_value: float,
    equivalent_diameter_meters_value: float,
    dynamic_viscosity_pascal_seconds: float,
) -> float:
    return (
        mass_flux_kilograms_per_square_meter_second_value
        * equivalent_diameter_meters_value
        / dynamic_viscosity_pascal_seconds
    )


def wall_temperature_celsius(
    tube_side_bulk_temperature_celsius: float,
    shell_side_bulk_temperature_celsius: float,
) -> float:
    return (tube_side_bulk_temperature_celsius + shell_side_bulk_temperature_celsius) / 2.0


def kern_heat_transfer_coefficient_watts_per_square_meter_kelvin(
    reynolds_number_value: float,
    prandtl_number: float,
    thermal_conductivity_watts_per_meter_kelvin: float,
    equivalent_diameter_meters_value: float,
    bulk_dynamic_viscosity_pascal_seconds: float,
    wall_dynamic_viscosity_pascal_seconds: float,
) -> float:
    wall_viscosity_correction = float(
        (bulk_dynamic_viscosity_pascal_seconds / wall_dynamic_viscosity_pascal_seconds)
        ** _WALL_VISCOSITY_CORRECTION_EXPONENT
    )
    return float(
        _HEAT_TRANSFER_COEFFICIENT_LEADING_CONSTANT
        * thermal_conductivity_watts_per_meter_kelvin
        / equivalent_diameter_meters_value
        * reynolds_number_value**_HEAT_TRANSFER_REYNOLDS_EXPONENT
        * prandtl_number ** (1.0 / 3.0)
        * wall_viscosity_correction
    )


def kern_friction_factor(reynolds_number_value: float) -> float:
    if reynolds_number_value <= 0.0:
        raise InvalidOperatingConditionError(MessageKey.SHELL_SIDE_REYNOLDS_NUMBER_MUST_BE_POSITIVE)
    return math.exp(
        _PRESSURE_DROP_FRICTION_INTERCEPT
        - _PRESSURE_DROP_FRICTION_SLOPE * math.log(reynolds_number_value)
    )


def kern_pressure_drop_pascal(
    friction_factor: float,
    mass_flux_kilograms_per_square_meter_second_value: float,
    baffle_count: float,
    shell_inner_diameter_meters: float,
    density_kilograms_per_cubic_meter: float,
    equivalent_diameter_meters_value: float,
    bulk_dynamic_viscosity_pascal_seconds: float,
    wall_dynamic_viscosity_pascal_seconds: float,
) -> float:
    wall_viscosity_correction = float(
        (bulk_dynamic_viscosity_pascal_seconds / wall_dynamic_viscosity_pascal_seconds)
        ** _WALL_VISCOSITY_CORRECTION_EXPONENT
    )
    return (
        friction_factor
        * mass_flux_kilograms_per_square_meter_second_value**2
        * (baffle_count + 1.0)
        * shell_inner_diameter_meters
    ) / (
        2.0
        * density_kilograms_per_cubic_meter
        * equivalent_diameter_meters_value
        * wall_viscosity_correction
    )


def kern_was_applied_inside_its_validated_range(reynolds_number_value: float) -> bool:
    return (
        KERN_MINIMUM_VALID_REYNOLDS_NUMBER
        <= reynolds_number_value
        <= KERN_MAXIMUM_VALID_REYNOLDS_NUMBER
    )
