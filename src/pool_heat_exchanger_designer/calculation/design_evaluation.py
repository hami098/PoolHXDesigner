from __future__ import annotations

from dataclasses import dataclass

from pool_heat_exchanger_designer.calculation import (
    shell_side_correlations,
    tube_side_correlations,
)
from pool_heat_exchanger_designer.calculation.design_case import DesignCase, OperatingConditions
from pool_heat_exchanger_designer.calculation.geometry import (
    ShellGeometry,
    TubeBundleGeometry,
)
from pool_heat_exchanger_designer.calculation.properties import (
    LiquidWaterPropertySource,
)
from pool_heat_exchanger_designer.calculation.standards import (
    ConstraintCheck,
    evaluate_design_standard_limits,
)
from pool_heat_exchanger_designer.calculation.thermal import (
    OverallHeatTransferCoefficients,
    PreliminarySizing,
    ThermalDuty,
    corrected_log_mean_temperature_difference_kelvin,
    preliminary_sizing_from_assumed_coefficients,
    referred_to_outside_area,
    thermal_duty_from_tube_side_temperature_rise,
)

DEFAULT_CONVERGENCE_RELATIVE_TOLERANCE = 0.01


@dataclass(frozen=True, slots=True)
class SideRating:
    reynolds_number: float
    prandtl_number: float
    mass_flux_kilograms_per_square_meter_second: float
    heat_transfer_coefficient_watts_per_square_meter_kelvin: float
    pressure_drop_pascal: float
    correlation_name: str
    correlation_applied_inside_validated_range: bool


@dataclass(frozen=True, slots=True)
class CoefficientConvergence:
    assumed_tube_side_watts_per_square_meter_kelvin: float
    computed_tube_side_watts_per_square_meter_kelvin: float
    assumed_shell_side_watts_per_square_meter_kelvin: float
    computed_shell_side_watts_per_square_meter_kelvin: float

    @property
    def tube_side_relative_difference(self) -> float:
        return _relative_difference(
            self.assumed_tube_side_watts_per_square_meter_kelvin,
            self.computed_tube_side_watts_per_square_meter_kelvin,
        )

    @property
    def shell_side_relative_difference(self) -> float:
        return _relative_difference(
            self.assumed_shell_side_watts_per_square_meter_kelvin,
            self.computed_shell_side_watts_per_square_meter_kelvin,
        )

    @property
    def largest_relative_difference(self) -> float:
        return max(
            abs(self.tube_side_relative_difference),
            abs(self.shell_side_relative_difference),
        )

    def has_converged(
        self, relative_tolerance: float = DEFAULT_CONVERGENCE_RELATIVE_TOLERANCE
    ) -> bool:
        return self.largest_relative_difference <= relative_tolerance


@dataclass(frozen=True, slots=True)
class GeometryAgreement:
    suggested_shell_inner_diameter_meters: float
    entered_shell_inner_diameter_meters: float
    suggested_tube_count: int
    entered_tube_count: int
    suggested_baffle_spacing_meters: float
    entered_baffle_spacing_meters: float

    @property
    def largest_relative_difference(self) -> float:
        return max(
            abs(
                _relative_difference(
                    self.suggested_shell_inner_diameter_meters,
                    self.entered_shell_inner_diameter_meters,
                )
            ),
            abs(_relative_difference(self.suggested_tube_count, self.entered_tube_count)),
            abs(
                _relative_difference(
                    self.suggested_baffle_spacing_meters,
                    self.entered_baffle_spacing_meters,
                )
            ),
        )

    def entered_matches_suggested(
        self, relative_tolerance: float = DEFAULT_CONVERGENCE_RELATIVE_TOLERANCE
    ) -> bool:
        return self.largest_relative_difference <= relative_tolerance


@dataclass(frozen=True, slots=True)
class DesignEvaluation:
    design_case: DesignCase
    thermal_duty: ThermalDuty
    corrected_log_mean_temperature_difference_kelvin: float
    overall_coefficients_from_assumed: OverallHeatTransferCoefficients
    preliminary_sizing: PreliminarySizing
    tube_side: SideRating
    shell_side: SideRating
    overall_coefficients_from_rating: OverallHeatTransferCoefficients
    coefficient_convergence: CoefficientConvergence
    geometry_agreement: GeometryAgreement
    constraint_checks: tuple[ConstraintCheck, ...]

    def is_consistent(
        self, relative_tolerance: float = DEFAULT_CONVERGENCE_RELATIVE_TOLERANCE
    ) -> bool:
        return self.coefficient_convergence.has_converged(
            relative_tolerance
        ) and self.geometry_agreement.entered_matches_suggested(relative_tolerance)

    @property
    def correlations_outside_their_validated_range(self) -> tuple[str, ...]:
        return tuple(
            side.correlation_name
            for side in (self.tube_side, self.shell_side)
            if not side.correlation_applied_inside_validated_range
        )


def evaluate_design_case(
    property_source: LiquidWaterPropertySource, design_case: DesignCase
) -> DesignEvaluation:
    conditions = design_case.operating_conditions
    bundle = design_case.tube_bundle
    shell = design_case.shell
    material = design_case.tube_wall_material
    assumed = design_case.assumed_heat_transfer_coefficients

    duty = thermal_duty_from_tube_side_temperature_rise(
        property_source,
        conditions.tube_side_inlet_temperature_celsius,
        conditions.tube_side_outlet_temperature_celsius,
        conditions.tube_side_mass_flow_rate_kilograms_per_second,
        conditions.shell_side_inlet_temperature_celsius,
        conditions.shell_side_mass_flow_rate_kilograms_per_second,
    )

    temperature_difference = corrected_log_mean_temperature_difference_kelvin(
        conditions.shell_side_inlet_temperature_celsius,
        duty.shell_side_outlet_temperature_celsius,
        conditions.tube_side_inlet_temperature_celsius,
        conditions.tube_side_outlet_temperature_celsius,
        design_case.log_mean_temperature_difference_correction_factor,
    )

    coefficients_from_assumed = referred_to_outside_area(
        shell_side_coefficient_watts_per_square_meter_kelvin=(
            assumed.shell_side_watts_per_square_meter_kelvin
        ),
        tube_side_coefficient_watts_per_square_meter_kelvin=(
            assumed.tube_side_watts_per_square_meter_kelvin
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

    sizing = preliminary_sizing_from_assumed_coefficients(
        heat_duty_watts=duty.heat_duty_watts,
        corrected_log_mean_temperature_difference_kelvin=temperature_difference,
        clean_overall_coefficient_watts_per_square_meter_kelvin=(
            coefficients_from_assumed.clean_watts_per_square_meter_kelvin
        ),
        fouled_overall_coefficient_watts_per_square_meter_kelvin=(
            coefficients_from_assumed.fouled_watts_per_square_meter_kelvin
        ),
        tube_outer_diameter_meters=bundle.tube_outer_diameter_meters,
        tube_length_meters=bundle.tube_length_meters,
        pitch_ratio=bundle.pitch_ratio,
        pitch_layout=bundle.pitch_layout,
        tube_count_calculation_constant=bundle.tube_count_calculation_constant,
    )

    tube_side = _rate_tube_side(duty, bundle, conditions)
    shell_side = _rate_shell_side(property_source, duty, bundle, shell, conditions)

    coefficients_from_rating = referred_to_outside_area(
        shell_side_coefficient_watts_per_square_meter_kelvin=(
            shell_side.heat_transfer_coefficient_watts_per_square_meter_kelvin
        ),
        tube_side_coefficient_watts_per_square_meter_kelvin=(
            tube_side.heat_transfer_coefficient_watts_per_square_meter_kelvin
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

    return DesignEvaluation(
        design_case=design_case,
        thermal_duty=duty,
        corrected_log_mean_temperature_difference_kelvin=temperature_difference,
        overall_coefficients_from_assumed=coefficients_from_assumed,
        preliminary_sizing=sizing,
        tube_side=tube_side,
        shell_side=shell_side,
        overall_coefficients_from_rating=coefficients_from_rating,
        coefficient_convergence=CoefficientConvergence(
            assumed_tube_side_watts_per_square_meter_kelvin=(
                assumed.tube_side_watts_per_square_meter_kelvin
            ),
            computed_tube_side_watts_per_square_meter_kelvin=(
                tube_side.heat_transfer_coefficient_watts_per_square_meter_kelvin
            ),
            assumed_shell_side_watts_per_square_meter_kelvin=(
                assumed.shell_side_watts_per_square_meter_kelvin
            ),
            computed_shell_side_watts_per_square_meter_kelvin=(
                shell_side.heat_transfer_coefficient_watts_per_square_meter_kelvin
            ),
        ),
        geometry_agreement=GeometryAgreement(
            suggested_shell_inner_diameter_meters=sizing.suggested_shell_inner_diameter_meters,
            entered_shell_inner_diameter_meters=shell.inner_diameter_meters,
            suggested_tube_count=sizing.suggested_whole_tube_count,
            entered_tube_count=bundle.tube_count,
            suggested_baffle_spacing_meters=sizing.suggested_baffle_spacing_meters,
            entered_baffle_spacing_meters=shell.baffle_spacing_meters,
        ),
        constraint_checks=evaluate_design_standard_limits(
            shell_inner_diameter_meters=shell.inner_diameter_meters,
            tube_length_meters=bundle.tube_length_meters,
            pitch_ratio=bundle.pitch_ratio,
            tube_side_outlet_temperature_celsius=(conditions.tube_side_outlet_temperature_celsius),
            shell_side_inlet_temperature_celsius=(conditions.shell_side_inlet_temperature_celsius),
            tube_side_pressure_drop_pascal=tube_side.pressure_drop_pascal,
            shell_side_pressure_drop_pascal=shell_side.pressure_drop_pascal,
        ),
    )


def _rate_tube_side(
    duty: ThermalDuty,
    bundle: TubeBundleGeometry,
    conditions: OperatingConditions,
) -> SideRating:
    properties = duty.tube_side_properties
    flow_area = bundle.tube_side_flow_area_per_pass_square_meters
    velocity = tube_side_correlations.mean_velocity_meters_per_second(
        conditions.tube_side_mass_flow_rate_kilograms_per_second,
        properties.density_kilograms_per_cubic_meter,
        flow_area,
    )
    mass_flux = tube_side_correlations.mass_flux_kilograms_per_square_meter_second(
        conditions.tube_side_mass_flow_rate_kilograms_per_second, flow_area
    )
    reynolds = tube_side_correlations.reynolds_number(
        properties.density_kilograms_per_cubic_meter,
        velocity,
        bundle.tube_inner_diameter_meters,
        properties.dynamic_viscosity_pascal_seconds,
    )
    nusselt = tube_side_correlations.gnielinski_nusselt_number(reynolds, properties.prandtl_number)
    friction_factor = tube_side_correlations.petukhov_smooth_tube_fanning_friction_factor(reynolds)
    return SideRating(
        reynolds_number=reynolds,
        prandtl_number=properties.prandtl_number,
        mass_flux_kilograms_per_square_meter_second=mass_flux,
        heat_transfer_coefficient_watts_per_square_meter_kelvin=(
            tube_side_correlations.heat_transfer_coefficient_watts_per_square_meter_kelvin(
                nusselt,
                properties.thermal_conductivity_watts_per_meter_kelvin,
                bundle.tube_inner_diameter_meters,
            )
        ),
        pressure_drop_pascal=tube_side_correlations.pressure_drop_pascal(
            friction_factor,
            bundle.tube_length_meters,
            bundle.tube_side_pass_count,
            bundle.tube_inner_diameter_meters,
            mass_flux,
            properties.density_kilograms_per_cubic_meter,
        ),
        correlation_name="Gnielinski",
        correlation_applied_inside_validated_range=(
            tube_side_correlations.gnielinski_was_applied_inside_its_validated_range(
                reynolds, properties.prandtl_number
            )
        ),
    )


def _rate_shell_side(
    property_source: LiquidWaterPropertySource,
    duty: ThermalDuty,
    bundle: TubeBundleGeometry,
    shell: ShellGeometry,
    conditions: OperatingConditions,
) -> SideRating:
    properties = duty.shell_side_properties
    wall_dynamic_viscosity = property_source.at_temperature_celsius(
        shell_side_correlations.wall_temperature_celsius(
            duty.tube_side_bulk_temperature_celsius,
            duty.shell_side_bulk_temperature_celsius,
        )
    ).dynamic_viscosity_pascal_seconds
    equivalent_diameter = shell_side_correlations.equivalent_diameter_meters(
        bundle.pitch_meters, bundle.tube_outer_diameter_meters, bundle.pitch_layout
    )
    crossflow_area = shell_side_correlations.crossflow_area_square_meters(
        shell.inner_diameter_meters,
        bundle.clearance_between_adjacent_tubes_meters,
        shell.baffle_spacing_meters,
        bundle.pitch_meters,
    )
    mass_flux = shell_side_correlations.mass_flux_kilograms_per_square_meter_second(
        conditions.shell_side_mass_flow_rate_kilograms_per_second, crossflow_area
    )
    reynolds = shell_side_correlations.reynolds_number(
        mass_flux, equivalent_diameter, properties.dynamic_viscosity_pascal_seconds
    )
    friction_factor = shell_side_correlations.kern_friction_factor(reynolds)
    return SideRating(
        reynolds_number=reynolds,
        prandtl_number=properties.prandtl_number,
        mass_flux_kilograms_per_square_meter_second=mass_flux,
        heat_transfer_coefficient_watts_per_square_meter_kelvin=(
            shell_side_correlations.kern_heat_transfer_coefficient_watts_per_square_meter_kelvin(
                reynolds,
                properties.prandtl_number,
                properties.thermal_conductivity_watts_per_meter_kelvin,
                equivalent_diameter,
                properties.dynamic_viscosity_pascal_seconds,
                wall_dynamic_viscosity,
            )
        ),
        pressure_drop_pascal=shell_side_correlations.kern_pressure_drop_pascal(
            friction_factor,
            mass_flux,
            shell.baffle_count_over_tube_length(bundle.tube_length_meters),
            shell.inner_diameter_meters,
            properties.density_kilograms_per_cubic_meter,
            equivalent_diameter,
            properties.dynamic_viscosity_pascal_seconds,
            wall_dynamic_viscosity,
        ),
        correlation_name="Kern",
        correlation_applied_inside_validated_range=(
            shell_side_correlations.kern_was_applied_inside_its_validated_range(reynolds)
        ),
    )


def _relative_difference(reference_value: float, compared_value: float) -> float:
    return (compared_value - reference_value) / reference_value
