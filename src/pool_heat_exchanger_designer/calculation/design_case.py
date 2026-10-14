from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pool_heat_exchanger_designer.calculation.design_errors import (
    DesignCaseFileError,
    InvalidGeometryError,
)
from pool_heat_exchanger_designer.calculation.geometry import (
    PitchLayout,
    ShellGeometry,
    TubeBundleGeometry,
    TubeGeometry,
)
from pool_heat_exchanger_designer.calculation.message_catalogue import MessageKey
from pool_heat_exchanger_designer.calculation.properties import (
    TubeWallMaterial,
    tube_wall_material_named,
)
from pool_heat_exchanger_designer.calculation.thermal import (
    DEFAULT_CORRECTION_FACTOR,
)


@dataclass(frozen=True, slots=True)
class OperatingConditions:
    tube_side_inlet_temperature_celsius: float
    tube_side_outlet_temperature_celsius: float
    shell_side_inlet_temperature_celsius: float
    tube_side_mass_flow_rate_kilograms_per_second: float
    shell_side_mass_flow_rate_kilograms_per_second: float


@dataclass(frozen=True, slots=True)
class AssumedHeatTransferCoefficients:
    tube_side_watts_per_square_meter_kelvin: float
    shell_side_watts_per_square_meter_kelvin: float

    def __post_init__(self) -> None:
        if self.tube_side_watts_per_square_meter_kelvin <= 0.0:
            raise InvalidGeometryError(MessageKey.ASSUMED_TUBE_SIDE_COEFFICIENT_MUST_BE_POSITIVE)
        if self.shell_side_watts_per_square_meter_kelvin <= 0.0:
            raise InvalidGeometryError(MessageKey.ASSUMED_SHELL_SIDE_COEFFICIENT_MUST_BE_POSITIVE)


@dataclass(frozen=True, slots=True)
class DesignCase:
    name: str
    operating_conditions: OperatingConditions
    tube_bundle: TubeBundleGeometry
    shell: ShellGeometry
    tube_wall_material: TubeWallMaterial
    assumed_heat_transfer_coefficients: AssumedHeatTransferCoefficients
    log_mean_temperature_difference_correction_factor: float = DEFAULT_CORRECTION_FACTOR

    def __post_init__(self) -> None:
        if self.shell.baffle_spacing_meters > self.tube_bundle.tube_length_meters:
            raise InvalidGeometryError(MessageKey.BAFFLE_SPACING_CANNOT_EXCEED_TUBE_LENGTH)


DESIGN_CASE_FILE_SECTION_NAMES = (
    "operating_conditions",
    "tube",
    "tube_bundle",
    "shell",
    "tube_wall",
    "assumed_heat_transfer_coefficients",
)


def read_design_case_from_toml_path(path: str | Path) -> DesignCase:
    file_path = Path(path)
    try:
        with file_path.open("rb") as design_case_file:
            parsed = tomllib.load(design_case_file)
    except FileNotFoundError as missing_file:
        raise DesignCaseFileError(MessageKey.DESIGN_CASE_FILE_NOT_FOUND, path=file_path) from (
            missing_file
        )
    except tomllib.TOMLDecodeError as malformed_file:
        raise DesignCaseFileError(
            MessageKey.DESIGN_CASE_FILE_IS_NOT_VALID_TOML,
            path=file_path,
            reason=malformed_file,
        ) from malformed_file
    return design_case_from_mapping(parsed, default_name=file_path.stem)


def design_case_from_mapping(
    parsed: dict[str, Any], default_name: str = "unnamed design case"
) -> DesignCase:
    missing_sections = [
        section_name
        for section_name in DESIGN_CASE_FILE_SECTION_NAMES
        if section_name not in parsed
    ]
    if missing_sections:
        raise DesignCaseFileError(
            MessageKey.DESIGN_CASE_MISSING_SECTIONS, sections=missing_sections
        )

    tube_section = _section(parsed, "tube")
    bundle_section = _section(parsed, "tube_bundle")
    shell_section = _section(parsed, "shell")
    conditions_section = _section(parsed, "operating_conditions")
    wall_section = _section(parsed, "tube_wall")
    assumed_section = _section(parsed, "assumed_heat_transfer_coefficients")
    method_section = parsed.get("method", {})

    tube = TubeGeometry(
        outer_diameter_meters=_required_number(tube_section, "outer_diameter_meters", "tube"),
        inner_diameter_meters=_required_number(tube_section, "inner_diameter_meters", "tube"),
        length_meters=_required_number(tube_section, "length_meters", "tube"),
    )

    return DesignCase(
        name=str(parsed.get("name", default_name)),
        operating_conditions=OperatingConditions(
            tube_side_inlet_temperature_celsius=_required_number(
                conditions_section,
                "tube_side_inlet_temperature_celsius",
                "operating_conditions",
            ),
            tube_side_outlet_temperature_celsius=_required_number(
                conditions_section,
                "tube_side_outlet_temperature_celsius",
                "operating_conditions",
            ),
            shell_side_inlet_temperature_celsius=_required_number(
                conditions_section,
                "shell_side_inlet_temperature_celsius",
                "operating_conditions",
            ),
            tube_side_mass_flow_rate_kilograms_per_second=_required_number(
                conditions_section,
                "tube_side_mass_flow_rate_kilograms_per_second",
                "operating_conditions",
            ),
            shell_side_mass_flow_rate_kilograms_per_second=_required_number(
                conditions_section,
                "shell_side_mass_flow_rate_kilograms_per_second",
                "operating_conditions",
            ),
        ),
        tube_bundle=TubeBundleGeometry(
            tube=tube,
            tube_count=int(_required_number(bundle_section, "tube_count", "tube_bundle")),
            tube_side_pass_count=int(
                _required_number(bundle_section, "tube_side_pass_count", "tube_bundle")
            ),
            pitch_ratio=_required_number(bundle_section, "pitch_ratio", "tube_bundle"),
            pitch_layout=_pitch_layout_named(
                _required_text(bundle_section, "pitch_layout", "tube_bundle")
            ),
        ),
        shell=ShellGeometry(
            inner_diameter_meters=_required_number(shell_section, "inner_diameter_meters", "shell"),
            baffle_spacing_meters=_required_number(shell_section, "baffle_spacing_meters", "shell"),
        ),
        tube_wall_material=tube_wall_material_named(
            _required_text(wall_section, "material", "tube_wall")
        ),
        assumed_heat_transfer_coefficients=AssumedHeatTransferCoefficients(
            tube_side_watts_per_square_meter_kelvin=_required_number(
                assumed_section,
                "tube_side_watts_per_square_meter_kelvin",
                "assumed_heat_transfer_coefficients",
            ),
            shell_side_watts_per_square_meter_kelvin=_required_number(
                assumed_section,
                "shell_side_watts_per_square_meter_kelvin",
                "assumed_heat_transfer_coefficients",
            ),
        ),
        log_mean_temperature_difference_correction_factor=float(
            method_section.get(
                "log_mean_temperature_difference_correction_factor",
                DEFAULT_CORRECTION_FACTOR,
            )
        ),
    )


def _number_assignment(key: str, value: float | int) -> str:
    return f"{key} = {value!r}"


def _text_assignment(key: str, value: str) -> str:
    return f'{key} = "{value}"'


def design_case_as_toml_text(design_case: DesignCase) -> str:
    conditions = design_case.operating_conditions
    bundle = design_case.tube_bundle
    shell = design_case.shell
    assumed = design_case.assumed_heat_transfer_coefficients
    lines = [
        _text_assignment("name", design_case.name),
        "",
        "[operating_conditions]",
        *(
            _number_assignment(key, value)
            for key, value in (
                (
                    "tube_side_inlet_temperature_celsius",
                    conditions.tube_side_inlet_temperature_celsius,
                ),
                (
                    "tube_side_outlet_temperature_celsius",
                    conditions.tube_side_outlet_temperature_celsius,
                ),
                (
                    "shell_side_inlet_temperature_celsius",
                    conditions.shell_side_inlet_temperature_celsius,
                ),
                (
                    "tube_side_mass_flow_rate_kilograms_per_second",
                    conditions.tube_side_mass_flow_rate_kilograms_per_second,
                ),
                (
                    "shell_side_mass_flow_rate_kilograms_per_second",
                    conditions.shell_side_mass_flow_rate_kilograms_per_second,
                ),
            )
        ),
        "",
        "[tube]",
        _number_assignment("outer_diameter_meters", bundle.tube_outer_diameter_meters),
        _number_assignment("inner_diameter_meters", bundle.tube_inner_diameter_meters),
        _number_assignment("length_meters", bundle.tube_length_meters),
        "",
        "[tube_bundle]",
        _number_assignment("tube_count", bundle.tube_count),
        _number_assignment("tube_side_pass_count", bundle.tube_side_pass_count),
        _number_assignment("pitch_ratio", bundle.pitch_ratio),
        _text_assignment("pitch_layout", bundle.pitch_layout.value),
        "",
        "[shell]",
        _number_assignment("inner_diameter_meters", shell.inner_diameter_meters),
        _number_assignment("baffle_spacing_meters", shell.baffle_spacing_meters),
        "",
        "[tube_wall]",
        _text_assignment("material", design_case.tube_wall_material.name),
        "",
        "[assumed_heat_transfer_coefficients]",
        _number_assignment(
            "tube_side_watts_per_square_meter_kelvin",
            assumed.tube_side_watts_per_square_meter_kelvin,
        ),
        _number_assignment(
            "shell_side_watts_per_square_meter_kelvin",
            assumed.shell_side_watts_per_square_meter_kelvin,
        ),
        "",
        "[method]",
        _number_assignment(
            "log_mean_temperature_difference_correction_factor",
            design_case.log_mean_temperature_difference_correction_factor,
        ),
        "",
    ]
    return "\n".join(lines)


def write_design_case_to_toml_path(design_case: DesignCase, path: str | Path) -> None:
    Path(path).write_text(design_case_as_toml_text(design_case), encoding="utf-8")


def _section(parsed: dict[str, Any], section_name: str) -> dict[str, Any]:
    section = parsed[section_name]
    if not isinstance(section, dict):
        raise DesignCaseFileError(
            MessageKey.DESIGN_CASE_SECTION_MUST_BE_A_TABLE, section=section_name
        )
    return section


def _required_number(section: dict[str, Any], key: str, section_name: str) -> float:
    if key not in section:
        raise DesignCaseFileError(MessageKey.DESIGN_CASE_MISSING_KEY, section=section_name, key=key)
    value = section[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DesignCaseFileError(
            MessageKey.DESIGN_CASE_VALUE_MUST_BE_A_NUMBER,
            section=section_name,
            key=key,
            value=repr(value),
        )
    return float(value)


def _required_text(section: dict[str, Any], key: str, section_name: str) -> str:
    if key not in section:
        raise DesignCaseFileError(MessageKey.DESIGN_CASE_MISSING_KEY, section=section_name, key=key)
    value = section[key]
    if not isinstance(value, str):
        raise DesignCaseFileError(
            MessageKey.DESIGN_CASE_VALUE_MUST_BE_TEXT,
            section=section_name,
            key=key,
            value=repr(value),
        )
    return value


def _pitch_layout_named(name: str) -> PitchLayout:
    try:
        return PitchLayout(name)
    except ValueError as unknown_layout:
        selectable = ", ".join(layout.value for layout in PitchLayout)
        raise DesignCaseFileError(
            MessageKey.UNKNOWN_PITCH_LAYOUT, name=repr(name), selectable=selectable
        ) from unknown_layout
