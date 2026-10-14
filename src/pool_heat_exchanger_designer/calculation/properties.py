from __future__ import annotations

import csv
from bisect import bisect_left
from dataclasses import dataclass, fields
from importlib.resources import files
from io import StringIO
from math import isfinite
from typing import Protocol, runtime_checkable

from pool_heat_exchanger_designer.calculation.design_errors import (
    InvalidGeometryError,
    PropertyTableFileError,
    TemperatureOutsideTabulatedRangeError,
)
from pool_heat_exchanger_designer.calculation.message_catalogue import MessageKey

PROPERTY_TABLE_FILE_NAME = "liquid_water_properties_table.csv"
TEMPERATURE_COLUMN_NAME = "temperature_celsius"


@dataclass(frozen=True, slots=True)
class LiquidWaterProperties:
    density_kilograms_per_cubic_meter: float
    specific_heat_joules_per_kilogram_kelvin: float
    dynamic_viscosity_pascal_seconds: float
    thermal_conductivity_watts_per_meter_kelvin: float
    prandtl_number: float
    thermal_diffusivity_square_meters_per_second: float


PROPERTY_COLUMN_NAMES = tuple(field.name for field in fields(LiquidWaterProperties))
EXPECTED_COLUMN_NAMES = (TEMPERATURE_COLUMN_NAME, *PROPERTY_COLUMN_NAMES)


@dataclass(frozen=True, slots=True)
class LiquidWaterPropertyTable:
    temperatures_celsius: tuple[float, ...]
    values_by_column_name: dict[str, tuple[float, ...]]


@runtime_checkable
class LiquidWaterPropertySource(Protocol):
    def at_temperature_celsius(self, temperature_celsius: float) -> LiquidWaterProperties: ...


class LiquidWaterPropertiesInterpolatedFromTable:
    def __init__(self, property_table: LiquidWaterPropertyTable) -> None:
        self._tabulated_temperatures_celsius = property_table.temperatures_celsius
        self._tabulated_properties = property_table.values_by_column_name

    @property
    def lowest_tabulated_temperature_celsius(self) -> float:
        return self._tabulated_temperatures_celsius[0]

    @property
    def highest_tabulated_temperature_celsius(self) -> float:
        return self._tabulated_temperatures_celsius[-1]

    def at_temperature_celsius(self, temperature_celsius: float) -> LiquidWaterProperties:
        self._reject_temperature_outside_tabulated_range(temperature_celsius)
        return LiquidWaterProperties(
            **{
                column_name: self._linearly_interpolated(temperature_celsius, tabulated_values)
                for column_name, tabulated_values in self._tabulated_properties.items()
            }
        )

    def _linearly_interpolated(
        self, temperature_celsius: float, tabulated_values: tuple[float, ...]
    ) -> float:
        temperatures = self._tabulated_temperatures_celsius
        position = bisect_left(temperatures, temperature_celsius)
        if temperatures[position] == temperature_celsius:
            return tabulated_values[position]
        slope = (tabulated_values[position] - tabulated_values[position - 1]) / (
            temperatures[position] - temperatures[position - 1]
        )
        return tabulated_values[position - 1] + slope * (
            temperature_celsius - temperatures[position - 1]
        )

    def _reject_temperature_outside_tabulated_range(self, temperature_celsius: float) -> None:
        if not (
            self.lowest_tabulated_temperature_celsius
            <= temperature_celsius
            <= self.highest_tabulated_temperature_celsius
        ):
            raise TemperatureOutsideTabulatedRangeError(
                MessageKey.TEMPERATURE_OUTSIDE_TABULATED_RANGE,
                temperature=temperature_celsius,
                lowest=self.lowest_tabulated_temperature_celsius,
                highest=self.highest_tabulated_temperature_celsius,
            )


def read_property_table_shipped_with_this_package() -> LiquidWaterPropertyTable:
    table_resource = files("pool_heat_exchanger_designer.calculation").joinpath(
        PROPERTY_TABLE_FILE_NAME
    )
    return property_table_parsed_from_csv_text(table_resource.read_text(encoding="utf-8"))


def property_table_parsed_from_csv_text(csv_text: str) -> LiquidWaterPropertyTable:
    rows = [row for row in csv.reader(StringIO(csv_text)) if row]
    column_names = _validated_column_names(rows[0] if rows else [])
    table_rows = sorted(
        (
            _parsed_row(column_names, cells, row_number)
            for row_number, cells in enumerate(rows[1:], start=2)
        ),
        key=lambda table_row: table_row[TEMPERATURE_COLUMN_NAME],
    )
    _reject_duplicate_temperatures(table_rows)
    return LiquidWaterPropertyTable(
        temperatures_celsius=tuple(table_row[TEMPERATURE_COLUMN_NAME] for table_row in table_rows),
        values_by_column_name={
            column_name: tuple(table_row[column_name] for table_row in table_rows)
            for column_name in PROPERTY_COLUMN_NAMES
        },
    )


def _validated_column_names(column_names: list[str]) -> list[str]:
    missing_column_names = [name for name in EXPECTED_COLUMN_NAMES if name not in column_names]
    if missing_column_names:
        raise PropertyTableFileError(
            MessageKey.PROPERTY_TABLE_MISSING_COLUMNS, columns=missing_column_names
        )
    unexpected_column_names = [
        column_name for column_name in column_names if column_name not in EXPECTED_COLUMN_NAMES
    ]
    duplicated_column_names = [
        column_name for column_name in EXPECTED_COLUMN_NAMES if column_names.count(column_name) > 1
    ]
    if unexpected_column_names or duplicated_column_names:
        raise PropertyTableFileError(
            MessageKey.PROPERTY_TABLE_UNEXPECTED_COLUMNS,
            columns=unexpected_column_names + duplicated_column_names,
        )
    return column_names


def _parsed_row(column_names: list[str], cells: list[str], row_number: int) -> dict[str, float]:
    if len(cells) != len(column_names):
        raise PropertyTableFileError(
            MessageKey.PROPERTY_TABLE_ROW_IS_MALFORMED, row_number=row_number
        )
    return {
        column_name: _parsed_cell(cell)
        for column_name, cell in zip(column_names, cells, strict=True)
    }


def _parsed_cell(cell: str) -> float:
    stripped_cell = cell.strip()
    if not stripped_cell:
        raise PropertyTableFileError(MessageKey.PROPERTY_TABLE_CONTAINS_EMPTY_CELLS)
    try:
        value = float(stripped_cell)
    except ValueError as not_a_number:
        raise PropertyTableFileError(
            MessageKey.PROPERTY_TABLE_CELL_IS_NOT_A_NUMBER, value=stripped_cell
        ) from not_a_number
    if not isfinite(value):
        raise PropertyTableFileError(
            MessageKey.PROPERTY_TABLE_CELL_IS_NOT_A_NUMBER, value=stripped_cell
        )
    return value


def _reject_duplicate_temperatures(table_rows: list[dict[str, float]]) -> None:
    temperatures = [table_row[TEMPERATURE_COLUMN_NAME] for table_row in table_rows]
    if len(set(temperatures)) != len(temperatures):
        raise PropertyTableFileError(MessageKey.PROPERTY_TABLE_DUPLICATE_TEMPERATURE)


def prandtl_number_deviations_from_specific_heat_viscosity_and_conductivity(
    property_table: LiquidWaterPropertyTable,
) -> tuple[float, ...]:
    values = property_table.values_by_column_name
    return tuple(
        abs(specific_heat * viscosity / conductivity - prandtl_number) / prandtl_number
        for specific_heat, viscosity, conductivity, prandtl_number in zip(
            values["specific_heat_joules_per_kilogram_kelvin"],
            values["dynamic_viscosity_pascal_seconds"],
            values["thermal_conductivity_watts_per_meter_kelvin"],
            values["prandtl_number"],
            strict=True,
        )
    )


def liquid_water_properties_shipped_with_this_package() -> (
    LiquidWaterPropertiesInterpolatedFromTable
):
    return LiquidWaterPropertiesInterpolatedFromTable(
        read_property_table_shipped_with_this_package()
    )


@dataclass(frozen=True, slots=True)
class TubeWallMaterial:
    name: str
    thermal_conductivity_watts_per_meter_kelvin: float
    fouling_resistance_square_meter_kelvin_per_watt: float

    def __post_init__(self) -> None:
        if self.thermal_conductivity_watts_per_meter_kelvin <= 0.0:
            raise InvalidGeometryError(
                MessageKey.THERMAL_CONDUCTIVITY_MUST_BE_POSITIVE,
                material_name=self.name,
            )
        if self.fouling_resistance_square_meter_kelvin_per_watt < 0.0:
            raise InvalidGeometryError(
                MessageKey.FOULING_RESISTANCE_CANNOT_BE_NEGATIVE,
                material_name=self.name,
            )


TITANIUM_ALLOY = TubeWallMaterial(
    name="titanium alloy",
    thermal_conductivity_watts_per_meter_kelvin=25.0,
    fouling_resistance_square_meter_kelvin_per_watt=5.0e-05,
)

STAINLESS_STEEL = TubeWallMaterial(
    name="stainless steel",
    thermal_conductivity_watts_per_meter_kelvin=15.0,
    fouling_resistance_square_meter_kelvin_per_watt=9.0e-05,
)

SELECTABLE_TUBE_WALL_MATERIALS = (TITANIUM_ALLOY, STAINLESS_STEEL)


def tube_wall_material_named(name: str) -> TubeWallMaterial:
    for material in SELECTABLE_TUBE_WALL_MATERIALS:
        if material.name == name:
            return material
    selectable_names = ", ".join(material.name for material in SELECTABLE_TUBE_WALL_MATERIALS)
    raise InvalidGeometryError(
        MessageKey.UNKNOWN_TUBE_WALL_MATERIAL,
        name=repr(name),
        selectable=selectable_names,
    )
