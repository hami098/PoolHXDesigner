from __future__ import annotations

import math

from pool_heat_exchanger_designer.calculation.design_errors import InvalidOperatingConditionError
from pool_heat_exchanger_designer.calculation.message_catalogue import MessageKey

GNIELINSKI_MINIMUM_VALID_REYNOLDS_NUMBER = 1.0e4
GNIELINSKI_MINIMUM_VALID_PRANDTL_NUMBER = 0.5
GNIELINSKI_MAXIMUM_VALID_PRANDTL_NUMBER = 2000.0


def mean_velocity_meters_per_second(
    mass_flow_rate_kilograms_per_second: float,
    density_kilograms_per_cubic_meter: float,
    flow_area_square_meters: float,
) -> float:
    if flow_area_square_meters <= 0.0:
        raise InvalidOperatingConditionError(MessageKey.TUBE_SIDE_FLOW_AREA_MUST_BE_POSITIVE)
    return mass_flow_rate_kilograms_per_second / (
        density_kilograms_per_cubic_meter * flow_area_square_meters
    )


def mass_flux_kilograms_per_square_meter_second(
    mass_flow_rate_kilograms_per_second: float, flow_area_square_meters: float
) -> float:
    if flow_area_square_meters <= 0.0:
        raise InvalidOperatingConditionError(MessageKey.TUBE_SIDE_FLOW_AREA_MUST_BE_POSITIVE)
    return mass_flow_rate_kilograms_per_second / flow_area_square_meters


def reynolds_number(
    density_kilograms_per_cubic_meter: float,
    mean_velocity_meters_per_second_value: float,
    inner_diameter_meters: float,
    dynamic_viscosity_pascal_seconds: float,
) -> float:
    return (
        density_kilograms_per_cubic_meter
        * mean_velocity_meters_per_second_value
        * inner_diameter_meters
    ) / dynamic_viscosity_pascal_seconds


def petukhov_smooth_tube_fanning_friction_factor(reynolds_number_value: float) -> float:
    if reynolds_number_value <= 0.0:
        raise InvalidOperatingConditionError(MessageKey.TUBE_SIDE_REYNOLDS_NUMBER_MUST_BE_POSITIVE)
    denominator = 1.58 * math.log(reynolds_number_value) - 3.28
    if denominator <= 0.0:
        raise InvalidOperatingConditionError(
            MessageKey.TUBE_SIDE_REYNOLDS_NUMBER_TOO_LOW_FOR_PETUKHOV
        )
    return denominator**-2


def gnielinski_nusselt_number(reynolds_number_value: float, prandtl_number: float) -> float:
    fanning_friction_factor = petukhov_smooth_tube_fanning_friction_factor(reynolds_number_value)
    half_friction_factor = fanning_friction_factor / 2.0
    return float(
        (half_friction_factor * (reynolds_number_value - 1000.0) * prandtl_number)
        / (1.0 + 12.7 * math.sqrt(half_friction_factor) * (prandtl_number ** (2.0 / 3.0) - 1.0))
    )


def heat_transfer_coefficient_watts_per_square_meter_kelvin(
    nusselt_number: float,
    thermal_conductivity_watts_per_meter_kelvin: float,
    inner_diameter_meters: float,
) -> float:
    return nusselt_number * thermal_conductivity_watts_per_meter_kelvin / inner_diameter_meters


def pressure_drop_pascal(
    fanning_friction_factor: float,
    tube_length_meters: float,
    tube_side_pass_count: int,
    inner_diameter_meters: float,
    mass_flux_kilograms_per_square_meter_second_value: float,
    density_kilograms_per_cubic_meter: float,
) -> float:
    return (
        4.0
        * fanning_friction_factor
        * (tube_length_meters * tube_side_pass_count / inner_diameter_meters)
        * mass_flux_kilograms_per_square_meter_second_value**2
        / (2.0 * density_kilograms_per_cubic_meter)
    )


def gnielinski_was_applied_inside_its_validated_range(
    reynolds_number_value: float, prandtl_number: float
) -> bool:
    return (
        reynolds_number_value >= GNIELINSKI_MINIMUM_VALID_REYNOLDS_NUMBER
        and GNIELINSKI_MINIMUM_VALID_PRANDTL_NUMBER
        <= prandtl_number
        <= GNIELINSKI_MAXIMUM_VALID_PRANDTL_NUMBER
    )
