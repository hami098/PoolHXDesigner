from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from pool_heat_exchanger_designer import (
    AssumedHeatTransferCoefficients,
    DesignCase,
    OperatingConditions,
    PitchLayout,
    ShellGeometry,
    TubeBundleGeometry,
    TubeGeometry,
    liquid_water_properties_shipped_with_this_package,
)
from pool_heat_exchanger_designer.calculation.properties import (
    LiquidWaterPropertiesInterpolatedFromTable,
    tube_wall_material_named,
)

REFERENCE_DIRECTORY = Path(__file__).parent / "reference"
ORIGINAL_BEHAVIOUR_PATH = REFERENCE_DIRECTORY / "original_implementation_behaviour.json"

MATERIAL_NAME_BY_ORIGINAL_LABEL = {
    "Titanium Alloy": "titanium alloy",
    "Stainless Steel": "stainless steel",
}
PITCH_LAYOUT_BY_ORIGINAL_LABEL = {
    "Square Pitch": PitchLayout.SQUARE,
    "Triangular Pitch": PitchLayout.TRIANGULAR,
}
PASS_COUNT_BY_ORIGINAL_LABEL = {"One Pass": 1, "Two Pass": 2}


@pytest.fixture(scope="session")
def property_source() -> LiquidWaterPropertiesInterpolatedFromTable:
    return liquid_water_properties_shipped_with_this_package()


@pytest.fixture(scope="session")
def original_implementation_behaviour() -> dict[str, Any]:
    parsed: dict[str, Any] = json.loads(ORIGINAL_BEHAVIOUR_PATH.read_text(encoding="utf-8"))
    return parsed


def design_case_from_original_inputs(case_name: str, original_inputs: dict[str, Any]) -> DesignCase:
    return DesignCase(
        name=case_name,
        operating_conditions=OperatingConditions(
            tube_side_inlet_temperature_celsius=original_inputs["tube_inlet"],
            tube_side_outlet_temperature_celsius=original_inputs["tube_outlet"],
            shell_side_inlet_temperature_celsius=original_inputs["shell_inlet"],
            tube_side_mass_flow_rate_kilograms_per_second=original_inputs["tube_flow"],
            shell_side_mass_flow_rate_kilograms_per_second=original_inputs["shell_flow"],
        ),
        tube_bundle=TubeBundleGeometry(
            tube=TubeGeometry(
                outer_diameter_meters=original_inputs["outer_diameter_mm"] / 1000.0,
                inner_diameter_meters=original_inputs["inner_diameter_mm"] / 1000.0,
                length_meters=original_inputs["length_m"],
            ),
            tube_count=int(original_inputs["tube_count"]),
            tube_side_pass_count=PASS_COUNT_BY_ORIGINAL_LABEL[original_inputs["passes"]],
            pitch_ratio=float(original_inputs["pitch_ratio"]),
            pitch_layout=PITCH_LAYOUT_BY_ORIGINAL_LABEL[original_inputs["pitch_layout"]],
        ),
        shell=ShellGeometry(
            inner_diameter_meters=original_inputs["shell_diameter_m"],
            baffle_spacing_meters=original_inputs["baffle_spacing_m"],
        ),
        tube_wall_material=tube_wall_material_named(
            MATERIAL_NAME_BY_ORIGINAL_LABEL[original_inputs["material"]]
        ),
        assumed_heat_transfer_coefficients=AssumedHeatTransferCoefficients(
            tube_side_watts_per_square_meter_kelvin=float(original_inputs["h_tube_assumed"]),
            shell_side_watts_per_square_meter_kelvin=float(original_inputs["h_shell_assumed"]),
        ),
    )


@pytest.fixture
def representative_design_case() -> DesignCase:
    return DesignCase(
        name="representative olympic pool case",
        operating_conditions=OperatingConditions(
            tube_side_inlet_temperature_celsius=13.0,
            tube_side_outlet_temperature_celsius=28.0,
            shell_side_inlet_temperature_celsius=80.0,
            tube_side_mass_flow_rate_kilograms_per_second=40.0,
            shell_side_mass_flow_rate_kilograms_per_second=20.0,
        ),
        tube_bundle=TubeBundleGeometry(
            tube=TubeGeometry(
                outer_diameter_meters=0.019,
                inner_diameter_meters=0.016,
                length_meters=6.0,
            ),
            tube_count=700,
            tube_side_pass_count=1,
            pitch_ratio=1.25,
            pitch_layout=PitchLayout.TRIANGULAR,
        ),
        shell=ShellGeometry(inner_diameter_meters=0.9, baffle_spacing_meters=0.45),
        tube_wall_material=tube_wall_material_named("titanium alloy"),
        assumed_heat_transfer_coefficients=AssumedHeatTransferCoefficients(
            tube_side_watts_per_square_meter_kelvin=3000.0,
            shell_side_watts_per_square_meter_kelvin=3000.0,
        ),
    )
