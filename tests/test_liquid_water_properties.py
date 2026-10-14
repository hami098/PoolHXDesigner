from __future__ import annotations

from importlib.resources import files

import pytest

from pool_heat_exchanger_designer.calculation.design_errors import (
    PropertyTableFileError,
    TemperatureOutsideTabulatedRangeError,
)
from pool_heat_exchanger_designer.calculation.properties import (
    PROPERTY_TABLE_FILE_NAME,
    LiquidWaterPropertiesInterpolatedFromTable,
    LiquidWaterPropertySource,
    prandtl_number_deviations_from_specific_heat_viscosity_and_conductivity,
    property_table_parsed_from_csv_text,
    read_property_table_shipped_with_this_package,
)

PRANDTL_NUMBER_INTERNAL_CONSISTENCY_TOLERANCE = 0.01


def shipped_table_csv_lines() -> list[str]:
    table_resource = files("pool_heat_exchanger_designer.calculation").joinpath(
        PROPERTY_TABLE_FILE_NAME
    )
    return table_resource.read_text(encoding="utf-8").splitlines()


def without_column(csv_lines: list[str], column_name: str) -> str:
    column_position = csv_lines[0].split(",").index(column_name)
    return "\n".join(
        ",".join(
            cell for position, cell in enumerate(line.split(",")) if position != column_position
        )
        for line in csv_lines
    )


def with_extra_column(csv_lines: list[str], column_name: str, cell: str) -> str:
    return "\n".join(
        [f"{csv_lines[0]},{column_name}", *(f"{line},{cell}" for line in csv_lines[1:])]
    )


def with_replaced_cell(csv_lines: list[str], line_number: int, column_name: str, cell: str) -> str:
    column_position = csv_lines[0].split(",").index(column_name)
    cells = csv_lines[line_number - 1].split(",")
    cells[column_position] = cell
    return "\n".join([*csv_lines[: line_number - 1], ",".join(cells), *csv_lines[line_number:]])


def test_the_shipped_table_satisfies_the_property_source_protocol(
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
) -> None:
    assert isinstance(property_source, LiquidWaterPropertySource)


def test_a_tabulated_temperature_returns_the_tabulated_row_exactly(
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
) -> None:
    properties = property_source.at_temperature_celsius(30.0)

    assert properties.density_kilograms_per_cubic_meter == pytest.approx(995.6)
    assert properties.specific_heat_joules_per_kilogram_kelvin == pytest.approx(4176.0)
    assert properties.dynamic_viscosity_pascal_seconds == pytest.approx(7.79e-04)
    assert properties.thermal_conductivity_watts_per_meter_kelvin == pytest.approx(0.618)
    assert properties.prandtl_number == pytest.approx(5.26)


def test_a_temperature_midway_between_two_rows_is_their_average(
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
) -> None:
    lower = property_source.at_temperature_celsius(20.0)
    upper = property_source.at_temperature_celsius(25.0)
    middle = property_source.at_temperature_celsius(22.5)

    assert middle.density_kilograms_per_cubic_meter == pytest.approx(
        (lower.density_kilograms_per_cubic_meter + upper.density_kilograms_per_cubic_meter) / 2.0
    )


def test_the_region_above_one_hundred_degrees_where_the_table_spacing_widens_is_usable(
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
) -> None:
    at_one_hundred = property_source.at_temperature_celsius(100.0)
    at_one_hundred_ten = property_source.at_temperature_celsius(110.0)
    at_one_hundred_five = property_source.at_temperature_celsius(105.0)

    assert at_one_hundred_five.density_kilograms_per_cubic_meter == pytest.approx(
        (
            at_one_hundred.density_kilograms_per_cubic_meter
            + at_one_hundred_ten.density_kilograms_per_cubic_meter
        )
        / 2.0
    )


@pytest.mark.parametrize("temperature_celsius", [102.0, 105.0, 112.0, 205.0, 275.0])
def test_temperatures_the_original_implementation_could_not_evaluate_now_succeed(
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
    temperature_celsius: float,
) -> None:
    properties = property_source.at_temperature_celsius(temperature_celsius)

    assert properties.density_kilograms_per_cubic_meter > 0.0
    assert properties.specific_heat_joules_per_kilogram_kelvin > 0.0


@pytest.mark.parametrize("temperature_celsius", [-0.5, 300.5, 1000.0])
def test_a_temperature_outside_the_tabulated_range_is_refused(
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
    temperature_celsius: float,
) -> None:
    with pytest.raises(TemperatureOutsideTabulatedRangeError):
        property_source.at_temperature_celsius(temperature_celsius)


def test_the_tabulated_prandtl_number_agrees_with_the_other_tabulated_columns() -> None:
    deviations = prandtl_number_deviations_from_specific_heat_viscosity_and_conductivity(
        read_property_table_shipped_with_this_package()
    )

    assert max(deviations) < PRANDTL_NUMBER_INTERNAL_CONSISTENCY_TOLERANCE


def test_a_table_missing_a_column_is_refused() -> None:
    csv_text = without_column(shipped_table_csv_lines(), "prandtl_number")

    with pytest.raises(PropertyTableFileError, match="missing the columns"):
        property_table_parsed_from_csv_text(csv_text)


def test_a_table_with_an_unexpected_column_is_refused() -> None:
    csv_text = with_extra_column(
        shipped_table_csv_lines(), "surface_tension_newtons_per_meter", "0.072"
    )

    with pytest.raises(PropertyTableFileError, match="unexpected columns"):
        property_table_parsed_from_csv_text(csv_text)


def test_a_table_listing_the_same_column_twice_is_refused() -> None:
    csv_text = with_extra_column(shipped_table_csv_lines(), "prandtl_number", "5.26")

    with pytest.raises(PropertyTableFileError, match="unexpected columns"):
        property_table_parsed_from_csv_text(csv_text)


def test_a_table_listing_the_same_temperature_twice_is_refused() -> None:
    csv_lines = shipped_table_csv_lines()
    csv_text = "\n".join([*csv_lines, csv_lines[1]])

    with pytest.raises(PropertyTableFileError, match="more than once"):
        property_table_parsed_from_csv_text(csv_text)


def test_a_table_with_an_empty_cell_is_refused() -> None:
    csv_text = with_replaced_cell(shipped_table_csv_lines(), 5, "prandtl_number", "")

    with pytest.raises(PropertyTableFileError, match="empty cells"):
        property_table_parsed_from_csv_text(csv_text)


@pytest.mark.parametrize("cell", ["not_a_number", "nan", "inf"])
def test_a_table_with_a_cell_that_is_not_a_finite_number_is_refused(cell: str) -> None:
    csv_text = with_replaced_cell(shipped_table_csv_lines(), 5, "prandtl_number", cell)

    with pytest.raises(PropertyTableFileError, match="is not a number"):
        property_table_parsed_from_csv_text(csv_text)


def test_a_table_row_with_a_missing_cell_is_refused() -> None:
    csv_lines = shipped_table_csv_lines()
    csv_text = "\n".join([*csv_lines, "310.0,700.0"])

    with pytest.raises(PropertyTableFileError, match="one cell per column"):
        property_table_parsed_from_csv_text(csv_text)


def test_a_table_given_out_of_order_is_sorted_by_temperature() -> None:
    csv_lines = shipped_table_csv_lines()
    csv_text = "\n".join([csv_lines[0], *reversed(csv_lines[1:])])

    property_table = property_table_parsed_from_csv_text(csv_text)

    assert list(property_table.temperatures_celsius) == sorted(property_table.temperatures_celsius)


def test_the_shipped_table_covers_the_whole_documented_range(
    property_source: LiquidWaterPropertiesInterpolatedFromTable,
) -> None:
    assert property_source.lowest_tabulated_temperature_celsius == 0.0
    assert property_source.highest_tabulated_temperature_celsius == 300.0
