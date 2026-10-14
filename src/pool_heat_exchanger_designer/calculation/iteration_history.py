from __future__ import annotations

import csv
from dataclasses import astuple, dataclass, fields
from io import StringIO

from pool_heat_exchanger_designer.calculation.design_case import DesignCase
from pool_heat_exchanger_designer.calculation.design_evaluation import DesignEvaluation


@dataclass(frozen=True, slots=True)
class IterationRecord:
    iteration_number: int
    assumed_tube_side_coefficient_watts_per_square_meter_kelvin: float
    computed_tube_side_coefficient_watts_per_square_meter_kelvin: float
    tube_side_relative_difference: float
    assumed_shell_side_coefficient_watts_per_square_meter_kelvin: float
    computed_shell_side_coefficient_watts_per_square_meter_kelvin: float
    shell_side_relative_difference: float
    largest_relative_difference: float
    has_converged: bool
    fouled_overall_coefficient_watts_per_square_meter_kelvin: float
    entered_shell_inner_diameter_meters: float
    suggested_shell_inner_diameter_meters: float
    entered_tube_count: int
    suggested_tube_count: float
    entered_baffle_spacing_meters: float
    suggested_baffle_spacing_meters: float
    largest_relative_geometry_difference: float
    is_consistent: bool


ITERATION_HISTORY_COLUMN_NAMES = tuple(field.name for field in fields(IterationRecord))


class IterationHistory:
    def __init__(self) -> None:
        self._records: list[IterationRecord] = []
        self._last_recorded_design_case: DesignCase | None = None

    def __len__(self) -> int:
        return len(self._records)

    def records(self) -> tuple[IterationRecord, ...]:
        return tuple(self._records)

    def record(self, evaluation: DesignEvaluation) -> None:
        if evaluation.design_case == self._last_recorded_design_case:
            return
        self._last_recorded_design_case = evaluation.design_case
        convergence = evaluation.coefficient_convergence
        rating = evaluation.overall_coefficients_from_rating
        sizing = evaluation.preliminary_sizing
        agreement = evaluation.geometry_agreement
        self._records.append(
            IterationRecord(
                iteration_number=len(self._records) + 1,
                assumed_tube_side_coefficient_watts_per_square_meter_kelvin=(
                    convergence.assumed_tube_side_watts_per_square_meter_kelvin
                ),
                computed_tube_side_coefficient_watts_per_square_meter_kelvin=(
                    convergence.computed_tube_side_watts_per_square_meter_kelvin
                ),
                tube_side_relative_difference=convergence.tube_side_relative_difference,
                assumed_shell_side_coefficient_watts_per_square_meter_kelvin=(
                    convergence.assumed_shell_side_watts_per_square_meter_kelvin
                ),
                computed_shell_side_coefficient_watts_per_square_meter_kelvin=(
                    convergence.computed_shell_side_watts_per_square_meter_kelvin
                ),
                shell_side_relative_difference=(convergence.shell_side_relative_difference),
                largest_relative_difference=convergence.largest_relative_difference,
                has_converged=convergence.has_converged(),
                fouled_overall_coefficient_watts_per_square_meter_kelvin=(
                    rating.fouled_watts_per_square_meter_kelvin
                ),
                entered_shell_inner_diameter_meters=(agreement.entered_shell_inner_diameter_meters),
                suggested_shell_inner_diameter_meters=(
                    sizing.suggested_shell_inner_diameter_meters
                ),
                entered_tube_count=agreement.entered_tube_count,
                suggested_tube_count=sizing.suggested_tube_count,
                entered_baffle_spacing_meters=agreement.entered_baffle_spacing_meters,
                suggested_baffle_spacing_meters=sizing.suggested_baffle_spacing_meters,
                largest_relative_geometry_difference=agreement.largest_relative_difference,
                is_consistent=evaluation.is_consistent(),
            )
        )

    def as_csv_text(self) -> str:
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer, lineterminator="\n")
        writer.writerow(ITERATION_HISTORY_COLUMN_NAMES)
        writer.writerows(astuple(record) for record in self._records)
        return csv_buffer.getvalue()

    def clear(self) -> None:
        self._records.clear()
        self._last_recorded_design_case = None
