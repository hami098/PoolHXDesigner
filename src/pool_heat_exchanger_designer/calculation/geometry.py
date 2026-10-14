from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from pool_heat_exchanger_designer.calculation.design_errors import InvalidGeometryError
from pool_heat_exchanger_designer.calculation.message_catalogue import MessageKey


class PitchLayout(Enum):
    SQUARE = "square"
    TRIANGULAR = "triangular"

    @property
    def tube_layout_constant(self) -> float:
        return _TUBE_LAYOUT_CONSTANT_BY_PITCH_LAYOUT[self]


_TUBE_LAYOUT_CONSTANT_BY_PITCH_LAYOUT = {
    PitchLayout.SQUARE: 1.0,
    PitchLayout.TRIANGULAR: 0.87,
}

TUBE_COUNT_CALCULATION_CONSTANT_BY_PASS_COUNT = {1: 0.93, 2: 0.90}

SELECTABLE_TUBE_SIDE_PASS_COUNTS = tuple(TUBE_COUNT_CALCULATION_CONSTANT_BY_PASS_COUNT)


@dataclass(frozen=True, slots=True)
class TubeGeometry:
    outer_diameter_meters: float
    inner_diameter_meters: float
    length_meters: float

    def __post_init__(self) -> None:
        if self.inner_diameter_meters <= 0.0:
            raise InvalidGeometryError(MessageKey.TUBE_INNER_DIAMETER_MUST_BE_POSITIVE)
        if self.outer_diameter_meters <= self.inner_diameter_meters:
            raise InvalidGeometryError(MessageKey.TUBE_OUTER_DIAMETER_MUST_EXCEED_INNER_DIAMETER)
        if self.length_meters <= 0.0:
            raise InvalidGeometryError(MessageKey.TUBE_LENGTH_MUST_BE_POSITIVE)

    @property
    def outer_radius_meters(self) -> float:
        return self.outer_diameter_meters / 2.0

    @property
    def inner_radius_meters(self) -> float:
        return self.inner_diameter_meters / 2.0

    @property
    def inner_cross_section_area_square_meters(self) -> float:
        return math.pi * self.inner_diameter_meters**2 / 4.0


@dataclass(frozen=True, slots=True)
class TubeBundleGeometry:
    tube: TubeGeometry
    tube_count: int
    tube_side_pass_count: int
    pitch_ratio: float
    pitch_layout: PitchLayout

    def __post_init__(self) -> None:
        if self.tube_count < 1:
            raise InvalidGeometryError(MessageKey.TUBE_COUNT_MUST_BE_AT_LEAST_ONE)
        if self.tube_side_pass_count not in TUBE_COUNT_CALCULATION_CONSTANT_BY_PASS_COUNT:
            selectable = ", ".join(
                str(pass_count) for pass_count in SELECTABLE_TUBE_SIDE_PASS_COUNTS
            )
            raise InvalidGeometryError(
                MessageKey.TUBE_SIDE_PASS_COUNT_MUST_BE_SELECTABLE,
                selectable=selectable,
            )
        if self.pitch_ratio <= 1.0:
            raise InvalidGeometryError(MessageKey.PITCH_RATIO_MUST_EXCEED_ONE)

    @property
    def tube_outer_diameter_meters(self) -> float:
        return self.tube.outer_diameter_meters

    @property
    def tube_inner_diameter_meters(self) -> float:
        return self.tube.inner_diameter_meters

    @property
    def tube_length_meters(self) -> float:
        return self.tube.length_meters

    @property
    def pitch_meters(self) -> float:
        return self.pitch_ratio * self.tube.outer_diameter_meters

    @property
    def clearance_between_adjacent_tubes_meters(self) -> float:
        return self.pitch_meters - self.tube.outer_diameter_meters

    @property
    def tube_side_flow_area_per_pass_square_meters(self) -> float:
        return (
            self.tube.inner_cross_section_area_square_meters
            * self.tube_count
            / self.tube_side_pass_count
        )

    @property
    def tube_count_calculation_constant(self) -> float:
        return TUBE_COUNT_CALCULATION_CONSTANT_BY_PASS_COUNT[self.tube_side_pass_count]


@dataclass(frozen=True, slots=True)
class ShellGeometry:
    inner_diameter_meters: float
    baffle_spacing_meters: float

    def __post_init__(self) -> None:
        if self.inner_diameter_meters <= 0.0:
            raise InvalidGeometryError(MessageKey.SHELL_INNER_DIAMETER_MUST_BE_POSITIVE)
        if self.baffle_spacing_meters <= 0.0:
            raise InvalidGeometryError(MessageKey.BAFFLE_SPACING_MUST_BE_POSITIVE)

    def baffle_count_over_tube_length(self, tube_length_meters: float) -> float:
        return tube_length_meters / self.baffle_spacing_meters - 1.0
