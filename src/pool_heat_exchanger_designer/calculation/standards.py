from __future__ import annotations

from dataclasses import dataclass, field

from pool_heat_exchanger_designer.calculation.message_catalogue import (
    UNIT_SYMBOL_BAR,
    UNIT_SYMBOL_DEGREE_CELSIUS,
    UNIT_SYMBOL_DIMENSIONLESS,
    MessageKey,
)
from pool_heat_exchanger_designer.calculation.translator import Translator

TEMA_LOWEST_SHELL_DIAMETER_TO_TUBE_LENGTH_RATIO = 0.0666
TEMA_HIGHEST_SHELL_DIAMETER_TO_TUBE_LENGTH_RATIO = 0.2
TEMA_LOWEST_PITCH_RATIO = 1.25
TEMA_HIGHEST_PITCH_RATIO = 1.5

FINA_LOWEST_POOL_TEMPERATURE_CELSIUS = 25.0
FINA_HIGHEST_POOL_TEMPERATURE_CELSIUS = 28.0

MAXIMUM_WORKING_PRESSURE_BAR = 6.0
SATURATION_TEMPERATURE_AT_MAXIMUM_WORKING_PRESSURE_CELSIUS = 158.8

PASCAL_PER_BAR = 1.0e5


@dataclass(frozen=True, slots=True)
class ConstraintCheck:
    quantity_key: MessageKey
    standard_key: MessageKey
    actual_value: float
    unit: str
    lowest_allowed_value: float | None = None
    highest_allowed_value: float | None = None
    quantity_parameters: dict[str, object] = field(default_factory=dict)

    @property
    def is_satisfied(self) -> bool:
        if self.lowest_allowed_value is not None and self.actual_value < self.lowest_allowed_value:
            return False
        return not (
            self.highest_allowed_value is not None
            and self.actual_value > self.highest_allowed_value
        )

    def quantity_text(self, translator: Translator) -> str:
        return translator.text(self.quantity_key, **self.quantity_parameters)

    def standard_text(self, translator: Translator) -> str:
        return translator.text(self.standard_key)

    def allowed_range_text(self, translator: Translator) -> str:
        if self.lowest_allowed_value is None:
            return translator.text(
                MessageKey.ALLOWED_RANGE_AT_MOST,
                highest=f"{self.highest_allowed_value:g}",
            )
        if self.highest_allowed_value is None:
            return translator.text(
                MessageKey.ALLOWED_RANGE_AT_LEAST,
                lowest=f"{self.lowest_allowed_value:g}",
            )
        return translator.text(
            MessageKey.ALLOWED_RANGE_BETWEEN,
            lowest=f"{self.lowest_allowed_value:g}",
            highest=f"{self.highest_allowed_value:g}",
        )

    def outcome_text(self, translator: Translator) -> str:
        return translator.text(
            MessageKey.CHECK_SATISFIED if self.is_satisfied else MessageKey.CHECK_FAILED
        )


def shell_diameter_to_tube_length_ratio_check(
    shell_inner_diameter_meters: float, tube_length_meters: float
) -> ConstraintCheck:
    return ConstraintCheck(
        quantity_key=MessageKey.CONSTRAINT_SHELL_SLENDERNESS,
        standard_key=MessageKey.STANDARD_TEMA,
        actual_value=shell_inner_diameter_meters / tube_length_meters,
        unit=UNIT_SYMBOL_DIMENSIONLESS,
        lowest_allowed_value=TEMA_LOWEST_SHELL_DIAMETER_TO_TUBE_LENGTH_RATIO,
        highest_allowed_value=TEMA_HIGHEST_SHELL_DIAMETER_TO_TUBE_LENGTH_RATIO,
    )


def pitch_ratio_check(pitch_ratio: float) -> ConstraintCheck:
    return ConstraintCheck(
        quantity_key=MessageKey.CONSTRAINT_PITCH_RATIO,
        standard_key=MessageKey.STANDARD_TEMA,
        actual_value=pitch_ratio,
        unit=UNIT_SYMBOL_DIMENSIONLESS,
        lowest_allowed_value=TEMA_LOWEST_PITCH_RATIO,
        highest_allowed_value=TEMA_HIGHEST_PITCH_RATIO,
    )


def pool_temperature_check(
    tube_side_outlet_temperature_celsius: float,
) -> ConstraintCheck:
    return ConstraintCheck(
        quantity_key=MessageKey.CONSTRAINT_POOL_WATER_TEMPERATURE,
        standard_key=MessageKey.STANDARD_FINA,
        actual_value=tube_side_outlet_temperature_celsius,
        unit=UNIT_SYMBOL_DEGREE_CELSIUS,
        lowest_allowed_value=FINA_LOWEST_POOL_TEMPERATURE_CELSIUS,
        highest_allowed_value=FINA_HIGHEST_POOL_TEMPERATURE_CELSIUS,
    )


def single_phase_check(
    highest_temperature_in_the_design_celsius: float,
) -> ConstraintCheck:
    return ConstraintCheck(
        quantity_key=MessageKey.CONSTRAINT_SINGLE_PHASE,
        standard_key=MessageKey.STANDARD_DESIGN_ENVELOPE,
        actual_value=highest_temperature_in_the_design_celsius,
        unit=UNIT_SYMBOL_DEGREE_CELSIUS,
        highest_allowed_value=SATURATION_TEMPERATURE_AT_MAXIMUM_WORKING_PRESSURE_CELSIUS,
        quantity_parameters={"pressure": f"{MAXIMUM_WORKING_PRESSURE_BAR:g}"},
    )


def tube_side_pressure_drop_check(pressure_drop_pascal: float) -> ConstraintCheck:
    return ConstraintCheck(
        quantity_key=MessageKey.CONSTRAINT_TUBE_SIDE_PRESSURE_DROP,
        standard_key=MessageKey.STANDARD_DESIGN_ENVELOPE,
        actual_value=pressure_drop_pascal / PASCAL_PER_BAR,
        unit=UNIT_SYMBOL_BAR,
        highest_allowed_value=MAXIMUM_WORKING_PRESSURE_BAR,
    )


def shell_side_pressure_drop_check(pressure_drop_pascal: float) -> ConstraintCheck:
    return ConstraintCheck(
        quantity_key=MessageKey.CONSTRAINT_SHELL_SIDE_PRESSURE_DROP,
        standard_key=MessageKey.STANDARD_DESIGN_ENVELOPE,
        actual_value=pressure_drop_pascal / PASCAL_PER_BAR,
        unit=UNIT_SYMBOL_BAR,
        highest_allowed_value=MAXIMUM_WORKING_PRESSURE_BAR,
    )


def evaluate_design_standard_limits(
    shell_inner_diameter_meters: float,
    tube_length_meters: float,
    pitch_ratio: float,
    tube_side_outlet_temperature_celsius: float,
    shell_side_inlet_temperature_celsius: float,
    tube_side_pressure_drop_pascal: float,
    shell_side_pressure_drop_pascal: float,
) -> tuple[ConstraintCheck, ...]:
    return (
        shell_diameter_to_tube_length_ratio_check(shell_inner_diameter_meters, tube_length_meters),
        pitch_ratio_check(pitch_ratio),
        pool_temperature_check(tube_side_outlet_temperature_celsius),
        single_phase_check(shell_side_inlet_temperature_celsius),
        tube_side_pressure_drop_check(tube_side_pressure_drop_pascal),
        shell_side_pressure_drop_check(shell_side_pressure_drop_pascal),
    )


def unsatisfied_checks(
    checks: tuple[ConstraintCheck, ...],
) -> tuple[ConstraintCheck, ...]:
    return tuple(check for check in checks if not check.is_satisfied)
