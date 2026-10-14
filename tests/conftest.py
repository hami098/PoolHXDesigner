from __future__ import annotations

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


@pytest.fixture(scope="session")
def property_source() -> LiquidWaterPropertiesInterpolatedFromTable:
    return liquid_water_properties_shipped_with_this_package()


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
