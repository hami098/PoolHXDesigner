from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import flet

from pool_heat_exchanger_designer.calculation.design_case import (
    AssumedHeatTransferCoefficients,
    DesignCase,
    OperatingConditions,
)
from pool_heat_exchanger_designer.calculation.design_errors import DesignError
from pool_heat_exchanger_designer.calculation.design_evaluation import DesignEvaluation
from pool_heat_exchanger_designer.calculation.geometry import (
    PitchLayout,
    ShellGeometry,
    TubeBundleGeometry,
    TubeGeometry,
)
from pool_heat_exchanger_designer.calculation.message_catalogue import (
    UNIT_SYMBOL_DEGREE_CELSIUS,
    UNIT_SYMBOL_DIMENSIONLESS,
    UNIT_SYMBOL_KILOGRAMS_PER_SECOND,
    UNIT_SYMBOL_METER,
    UNIT_SYMBOL_MILLIMETER,
    UNIT_SYMBOL_WATTS_PER_SQUARE_METER_KELVIN,
    MessageKey,
)
from pool_heat_exchanger_designer.calculation.properties import (
    STAINLESS_STEEL,
    TITANIUM_ALLOY,
    tube_wall_material_named,
)
from pool_heat_exchanger_designer.calculation.translator import Translator
from pool_heat_exchanger_designer.user_interface.displayed_numbers import number_text
from pool_heat_exchanger_designer.user_interface.exchanger_schematic import StreamTemperatures
from pool_heat_exchanger_designer.user_interface.industrial_theme import (
    GROUP_GAP,
    HOT_WATER_COLOR,
    INPUT_TEXT_INSET,
    METAL_COLOR,
    POOL_WATER_COLOR,
    SECONDARY_TEXT_COLOR,
    TWO_GROUPS_PER_ROW_ON_WIDE_SCREENS,
    grid_heading,
    grid_row,
    group_box,
    toolbar_button,
    value_text,
)
from pool_heat_exchanger_designer.user_interface.numeric_input_field import (
    ChoiceInputField,
    NumericFieldSpecification,
    NumericInputField,
)

MILLIMETERS_PER_METER = 1000.0
COMPUTED_TEMPERATURE_DECIMAL_PLACES = 2

POOL_WATER_FIELDS = (
    NumericFieldSpecification(
        key="tube_side_inlet_temperature_celsius",
        label_key=MessageKey.FIELD_TUBE_SIDE_INLET_TEMPERATURE,
        unit=UNIT_SYMBOL_DEGREE_CELSIUS,
        initial_value=13.0,
        lowest_accepted_value=0.0,
        highest_accepted_value=300.0,
        decimal_places=2,
    ),
    NumericFieldSpecification(
        key="tube_side_outlet_temperature_celsius",
        label_key=MessageKey.FIELD_TUBE_SIDE_OUTLET_TEMPERATURE,
        unit=UNIT_SYMBOL_DEGREE_CELSIUS,
        initial_value=28.0,
        lowest_accepted_value=0.0,
        highest_accepted_value=300.0,
        decimal_places=2,
    ),
    NumericFieldSpecification(
        key="tube_side_mass_flow_rate_kilograms_per_second",
        label_key=MessageKey.FIELD_TUBE_SIDE_MASS_FLOW_RATE,
        unit=UNIT_SYMBOL_KILOGRAMS_PER_SECOND,
        initial_value=40.0,
        lowest_accepted_value=0.001,
        highest_accepted_value=500.0,
        decimal_places=3,
    ),
)

HOT_WATER_FIELDS = (
    NumericFieldSpecification(
        key="shell_side_inlet_temperature_celsius",
        label_key=MessageKey.FIELD_SHELL_SIDE_INLET_TEMPERATURE,
        unit=UNIT_SYMBOL_DEGREE_CELSIUS,
        initial_value=80.0,
        lowest_accepted_value=0.0,
        highest_accepted_value=300.0,
        decimal_places=2,
    ),
    NumericFieldSpecification(
        key="shell_side_mass_flow_rate_kilograms_per_second",
        label_key=MessageKey.FIELD_SHELL_SIDE_MASS_FLOW_RATE,
        unit=UNIT_SYMBOL_KILOGRAMS_PER_SECOND,
        initial_value=20.0,
        lowest_accepted_value=0.001,
        highest_accepted_value=500.0,
        decimal_places=3,
    ),
)

TUBE_FIELDS = (
    NumericFieldSpecification(
        key="tube_outer_diameter_millimeters",
        label_key=MessageKey.FIELD_TUBE_OUTER_DIAMETER,
        unit=UNIT_SYMBOL_MILLIMETER,
        initial_value=19.0,
        lowest_accepted_value=1.0,
        highest_accepted_value=250.0,
        decimal_places=2,
    ),
    NumericFieldSpecification(
        key="tube_inner_diameter_millimeters",
        label_key=MessageKey.FIELD_TUBE_INNER_DIAMETER,
        unit=UNIT_SYMBOL_MILLIMETER,
        initial_value=16.0,
        lowest_accepted_value=0.5,
        highest_accepted_value=250.0,
        decimal_places=2,
    ),
    NumericFieldSpecification(
        key="tube_length_meters",
        label_key=MessageKey.FIELD_TUBE_LENGTH,
        unit=UNIT_SYMBOL_METER,
        initial_value=6.0,
        lowest_accepted_value=0.1,
        highest_accepted_value=35.0,
        decimal_places=3,
    ),
    NumericFieldSpecification(
        key="pitch_ratio",
        label_key=MessageKey.FIELD_PITCH_RATIO,
        unit=UNIT_SYMBOL_DIMENSIONLESS,
        initial_value=1.25,
        lowest_accepted_value=1.001,
        highest_accepted_value=3.0,
        decimal_places=3,
    ),
)

SHELL_AND_BAFFLE_FIELDS = (
    NumericFieldSpecification(
        key="shell_inner_diameter_meters",
        label_key=MessageKey.FIELD_SHELL_INNER_DIAMETER,
        unit=UNIT_SYMBOL_METER,
        initial_value=0.9,
        lowest_accepted_value=0.01,
        highest_accepted_value=10.0,
        decimal_places=4,
    ),
    NumericFieldSpecification(
        key="tube_count",
        label_key=MessageKey.FIELD_TUBE_COUNT,
        unit=UNIT_SYMBOL_DIMENSIONLESS,
        initial_value=700,
        lowest_accepted_value=1,
        highest_accepted_value=20000,
        accepts_only_whole_numbers=True,
    ),
    NumericFieldSpecification(
        key="baffle_spacing_meters",
        label_key=MessageKey.FIELD_BAFFLE_SPACING,
        unit=UNIT_SYMBOL_METER,
        initial_value=0.45,
        lowest_accepted_value=0.01,
        highest_accepted_value=35.0,
        decimal_places=4,
    ),
)

DESIGN_ASSUMPTION_FIELDS = (
    NumericFieldSpecification(
        key="assumed_tube_side_watts_per_square_meter_kelvin",
        label_key=MessageKey.FIELD_ASSUMED_TUBE_SIDE_COEFFICIENT,
        unit=UNIT_SYMBOL_WATTS_PER_SQUARE_METER_KELVIN,
        initial_value=3000.0,
        lowest_accepted_value=1.0,
        highest_accepted_value=100000.0,
        decimal_places=1,
    ),
    NumericFieldSpecification(
        key="assumed_shell_side_watts_per_square_meter_kelvin",
        label_key=MessageKey.FIELD_ASSUMED_SHELL_SIDE_COEFFICIENT,
        unit=UNIT_SYMBOL_WATTS_PER_SQUARE_METER_KELVIN,
        initial_value=3000.0,
        lowest_accepted_value=1.0,
        highest_accepted_value=100000.0,
        decimal_places=1,
    ),
    NumericFieldSpecification(
        key="log_mean_temperature_difference_correction_factor",
        label_key=MessageKey.FIELD_CORRECTION_FACTOR,
        unit=UNIT_SYMBOL_DIMENSIONLESS,
        initial_value=0.9,
        lowest_accepted_value=0.01,
        highest_accepted_value=1.0,
        decimal_places=3,
    ),
)


@dataclass(frozen=True, slots=True)
class FieldGroup:
    title_key: MessageKey
    fields: tuple[NumericFieldSpecification, ...]


FIELD_GROUPS = (
    FieldGroup(MessageKey.GROUP_POOL_WATER, POOL_WATER_FIELDS),
    FieldGroup(MessageKey.GROUP_HOT_WATER, HOT_WATER_FIELDS),
    FieldGroup(MessageKey.GROUP_TUBES, TUBE_FIELDS),
    FieldGroup(MessageKey.GROUP_SHELL_AND_BAFFLES, SHELL_AND_BAFFLE_FIELDS),
    FieldGroup(MessageKey.GROUP_DESIGN_ASSUMPTIONS, DESIGN_ASSUMPTION_FIELDS),
)

ALL_FIELD_SPECIFICATIONS = tuple(
    specification for group in FIELD_GROUPS for specification in group.fields
)

ASSUMED_COEFFICIENT_FIELD_KEYS = (
    "assumed_tube_side_watts_per_square_meter_kelvin",
    "assumed_shell_side_watts_per_square_meter_kelvin",
)

PITCH_LAYOUT_OPTIONS = (
    (PitchLayout.TRIANGULAR.value, MessageKey.OPTION_TRIANGULAR_PITCH),
    (PitchLayout.SQUARE.value, MessageKey.OPTION_SQUARE_PITCH),
)

TUBE_SIDE_PASS_COUNT_OPTIONS = (
    ("1", MessageKey.OPTION_ONE_TUBE_SIDE_PASS),
    ("2", MessageKey.OPTION_TWO_TUBE_SIDE_PASSES),
)

TUBE_WALL_MATERIAL_OPTIONS = (
    (TITANIUM_ALLOY.name, MessageKey.OPTION_TITANIUM_ALLOY),
    (STAINLESS_STEEL.name, MessageKey.OPTION_STAINLESS_STEEL),
)


class DesignForm:
    def __init__(
        self,
        translator: Translator,
        on_any_change: Callable[[], None],
        on_submit: Callable[[], None],
        on_use_suggested_geometry: Callable[[], None],
        on_use_computed_coefficients: Callable[[], None],
    ) -> None:
        self._translator = translator
        self._fields: dict[str, NumericInputField] = {
            specification.key: NumericInputField(
                specification, translator, on_any_change, on_submit
            )
            for specification in ALL_FIELD_SPECIFICATIONS
        }
        self._group_title_key_by_field_key = {
            specification.key: group.title_key
            for group in FIELD_GROUPS
            for specification in group.fields
        }
        self._pitch_layout = ChoiceInputField(
            key="pitch_layout",
            label_key=MessageKey.FIELD_PITCH_LAYOUT,
            options=PITCH_LAYOUT_OPTIONS,
            initial_key=PitchLayout.TRIANGULAR.value,
            translator=translator,
            on_any_change=on_any_change,
        )
        self._tube_side_pass_count = ChoiceInputField(
            key="tube_side_pass_count",
            label_key=MessageKey.FIELD_TUBE_SIDE_PASS_COUNT,
            options=TUBE_SIDE_PASS_COUNT_OPTIONS,
            initial_key="1",
            translator=translator,
            on_any_change=on_any_change,
        )
        self._tube_wall_material = ChoiceInputField(
            key="tube_wall_material",
            label_key=MessageKey.FIELD_TUBE_WALL_MATERIAL,
            options=TUBE_WALL_MATERIAL_OPTIONS,
            initial_key=TITANIUM_ALLOY.name,
            translator=translator,
            on_any_change=on_any_change,
        )
        self._use_suggested_geometry_button = toolbar_button(
            translator.text(MessageKey.BUTTON_USE_SUGGESTED_GEOMETRY),
            flet.Icons.AUTO_FIX_HIGH,
            on_use_suggested_geometry,
        )
        self._use_computed_coefficients_button = toolbar_button(
            translator.text(MessageKey.BUTTON_USE_COMPUTED_COEFFICIENTS),
            flet.Icons.AUTO_FIX_HIGH,
            on_use_computed_coefficients,
        )
        self._use_suggested_geometry_button.disabled = True
        self._use_computed_coefficients_button.disabled = True
        self._computed_hot_water_outlet_text = value_text(
            number_text(None, COMPUTED_TEMPERATURE_DECIMAL_PLACES), SECONDARY_TEXT_COLOR
        )

    def field(self, key: str) -> NumericInputField:
        return self._fields[key]

    @property
    def tube_side_pass_count(self) -> int:
        return int(self._tube_side_pass_count.selected_key)

    def invalid_field_labels(self) -> tuple[str, ...]:
        return tuple(
            self._translator.text(
                MessageKey.FIELD_IN_GROUP,
                group=self._translator.text(self._group_title_key_by_field_key[key]),
                field=field.label,
            )
            for key, field in self._fields.items()
            if not field.is_valid
        )

    def refresh_all_validation_messages(self) -> None:
        for field in self._fields.values():
            field.refresh_validation_message()

    def remembered_entries(self) -> dict[str, str]:
        return {
            **{key: field.entered_text for key, field in self._fields.items()},
            self._pitch_layout.key: self._pitch_layout.selected_key,
            self._tube_wall_material.key: self._tube_wall_material.selected_key,
            self._tube_side_pass_count.key: self._tube_side_pass_count.selected_key,
        }

    def restore_entries(self, remembered: dict[str, str]) -> None:
        for key, field in self._fields.items():
            if key in remembered:
                field.set_text(remembered[key])
        for choice in (
            self._pitch_layout,
            self._tube_wall_material,
            self._tube_side_pass_count,
        ):
            if choice.key in remembered:
                choice.select(remembered[choice.key])

    def value_of(self, key: str) -> float:
        parsed = self._fields[key].parsed_value
        if parsed is None:
            raise DesignError(
                MessageKey.FIELD_IS_NOT_A_USABLE_NUMBER,
                label=self._fields[key].label,
            )
        return parsed

    def entered_stream_temperatures(
        self, hot_water_outlet_celsius: float | None
    ) -> StreamTemperatures:
        return StreamTemperatures(
            pool_water_inlet_celsius=self._fields[
                "tube_side_inlet_temperature_celsius"
            ].parsed_value,
            pool_water_outlet_celsius=self._fields[
                "tube_side_outlet_temperature_celsius"
            ].parsed_value,
            hot_water_inlet_celsius=self._fields[
                "shell_side_inlet_temperature_celsius"
            ].parsed_value,
            hot_water_outlet_celsius=hot_water_outlet_celsius,
        )

    def build_design_case(self, name: str) -> DesignCase:
        return DesignCase(
            name=name,
            operating_conditions=OperatingConditions(
                tube_side_inlet_temperature_celsius=self.value_of(
                    "tube_side_inlet_temperature_celsius"
                ),
                tube_side_outlet_temperature_celsius=self.value_of(
                    "tube_side_outlet_temperature_celsius"
                ),
                shell_side_inlet_temperature_celsius=self.value_of(
                    "shell_side_inlet_temperature_celsius"
                ),
                tube_side_mass_flow_rate_kilograms_per_second=self.value_of(
                    "tube_side_mass_flow_rate_kilograms_per_second"
                ),
                shell_side_mass_flow_rate_kilograms_per_second=self.value_of(
                    "shell_side_mass_flow_rate_kilograms_per_second"
                ),
            ),
            tube_bundle=TubeBundleGeometry(
                tube=TubeGeometry(
                    outer_diameter_meters=self.value_of("tube_outer_diameter_millimeters")
                    / MILLIMETERS_PER_METER,
                    inner_diameter_meters=self.value_of("tube_inner_diameter_millimeters")
                    / MILLIMETERS_PER_METER,
                    length_meters=self.value_of("tube_length_meters"),
                ),
                tube_count=int(self.value_of("tube_count")),
                tube_side_pass_count=self.tube_side_pass_count,
                pitch_ratio=self.value_of("pitch_ratio"),
                pitch_layout=PitchLayout(self._pitch_layout.selected_key),
            ),
            shell=ShellGeometry(
                inner_diameter_meters=self.value_of("shell_inner_diameter_meters"),
                baffle_spacing_meters=self.value_of("baffle_spacing_meters"),
            ),
            tube_wall_material=tube_wall_material_named(self._tube_wall_material.selected_key),
            assumed_heat_transfer_coefficients=AssumedHeatTransferCoefficients(
                tube_side_watts_per_square_meter_kelvin=self.value_of(
                    "assumed_tube_side_watts_per_square_meter_kelvin"
                ),
                shell_side_watts_per_square_meter_kelvin=self.value_of(
                    "assumed_shell_side_watts_per_square_meter_kelvin"
                ),
            ),
            log_mean_temperature_difference_correction_factor=self.value_of(
                "log_mean_temperature_difference_correction_factor"
            ),
        )

    def load_design_case(self, design_case: DesignCase) -> None:
        conditions = design_case.operating_conditions
        bundle = design_case.tube_bundle
        assumed = design_case.assumed_heat_transfer_coefficients
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
            (
                "tube_outer_diameter_millimeters",
                bundle.tube_outer_diameter_meters * MILLIMETERS_PER_METER,
            ),
            (
                "tube_inner_diameter_millimeters",
                bundle.tube_inner_diameter_meters * MILLIMETERS_PER_METER,
            ),
            ("tube_length_meters", bundle.tube_length_meters),
            ("pitch_ratio", bundle.pitch_ratio),
            ("shell_inner_diameter_meters", design_case.shell.inner_diameter_meters),
            ("tube_count", bundle.tube_count),
            ("baffle_spacing_meters", design_case.shell.baffle_spacing_meters),
            (
                "assumed_tube_side_watts_per_square_meter_kelvin",
                assumed.tube_side_watts_per_square_meter_kelvin,
            ),
            (
                "assumed_shell_side_watts_per_square_meter_kelvin",
                assumed.shell_side_watts_per_square_meter_kelvin,
            ),
            (
                "log_mean_temperature_difference_correction_factor",
                design_case.log_mean_temperature_difference_correction_factor,
            ),
        ):
            self._fields[key].set_value(value)
        self._pitch_layout.select(bundle.pitch_layout.value)
        self._tube_wall_material.select(design_case.tube_wall_material.name)
        self._tube_side_pass_count.select(str(bundle.tube_side_pass_count))

    def show_computed_hot_water_outlet(self, temperature_celsius: float | None) -> None:
        self._computed_hot_water_outlet_text.value = number_text(
            temperature_celsius, COMPUTED_TEMPERATURE_DECIMAL_PLACES
        )

    def show_reference_values(self, evaluation: DesignEvaluation | None) -> None:
        if evaluation is None:
            for key in (
                *ASSUMED_COEFFICIENT_FIELD_KEYS,
                *(spec.key for spec in SHELL_AND_BAFFLE_FIELDS),
            ):
                self._fields[key].show_reference_value(None)
            self._use_suggested_geometry_button.disabled = True
            self._use_computed_coefficients_button.disabled = True
            return
        agreement = evaluation.geometry_agreement
        convergence = evaluation.coefficient_convergence
        self._fields["shell_inner_diameter_meters"].show_reference_value(
            agreement.suggested_shell_inner_diameter_meters
        )
        self._fields["tube_count"].show_reference_value(agreement.suggested_tube_count)
        self._fields["baffle_spacing_meters"].show_reference_value(
            agreement.suggested_baffle_spacing_meters
        )
        self._fields["assumed_tube_side_watts_per_square_meter_kelvin"].show_reference_value(
            convergence.computed_tube_side_watts_per_square_meter_kelvin
        )
        self._fields["assumed_shell_side_watts_per_square_meter_kelvin"].show_reference_value(
            convergence.computed_shell_side_watts_per_square_meter_kelvin
        )
        self._use_suggested_geometry_button.disabled = agreement.entered_matches_suggested()
        self._use_computed_coefficients_button.disabled = convergence.has_converged()

    def use_suggested_geometry(self, evaluation: DesignEvaluation) -> None:
        agreement = evaluation.geometry_agreement
        self._fields["shell_inner_diameter_meters"].set_value(
            agreement.suggested_shell_inner_diameter_meters
        )
        self._fields["tube_count"].set_value(agreement.suggested_tube_count)
        self._fields["baffle_spacing_meters"].set_value(agreement.suggested_baffle_spacing_meters)

    def use_computed_coefficients(self, evaluation: DesignEvaluation) -> None:
        convergence = evaluation.coefficient_convergence
        self._fields["assumed_tube_side_watts_per_square_meter_kelvin"].set_value(
            convergence.computed_tube_side_watts_per_square_meter_kelvin
        )
        self._fields["assumed_shell_side_watts_per_square_meter_kelvin"].set_value(
            convergence.computed_shell_side_watts_per_square_meter_kelvin
        )

    def group_controls(self) -> list[flet.Control]:
        text = self._translator.text
        return [
            group_box(
                text(MessageKey.GROUP_POOL_WATER),
                self._rows(POOL_WATER_FIELDS),
                marker_color=POOL_WATER_COLOR,
            ),
            group_box(
                text(MessageKey.GROUP_HOT_WATER),
                [
                    *self._rows(HOT_WATER_FIELDS),
                    grid_row(
                        text(MessageKey.FIELD_SHELL_SIDE_OUTLET_TEMPERATURE_COMPUTED),
                        flet.Container(
                            content=self._computed_hot_water_outlet_text,
                            padding=flet.Padding.only(right=INPUT_TEXT_INSET),
                        ),
                        UNIT_SYMBOL_DEGREE_CELSIUS,
                    ),
                ],
                marker_color=HOT_WATER_COLOR,
            ),
            group_box(
                text(MessageKey.GROUP_TUBES),
                [
                    *self._rows(TUBE_FIELDS),
                    self._pitch_layout.as_row(),
                    self._tube_side_pass_count.as_row(),
                    self._tube_wall_material.as_row(),
                ],
                marker_color=METAL_COLOR,
            ),
            flet.Column(
                controls=[self._shell_and_baffle_group(), self._design_assumption_group()],
                spacing=GROUP_GAP,
                col=TWO_GROUPS_PER_ROW_ON_WIDE_SCREENS,
            ),
        ]

    def _shell_and_baffle_group(self) -> flet.Container:
        text = self._translator.text
        return group_box(
            text(MessageKey.GROUP_SHELL_AND_BAFFLES),
            [
                grid_heading(text(MessageKey.COLUMN_ENTERED), text(MessageKey.COLUMN_SUGGESTED)),
                *self._rows(SHELL_AND_BAFFLE_FIELDS, show_reference_column=True),
            ],
            marker_color=METAL_COLOR,
            trailing=self._use_suggested_geometry_button,
        )

    def _design_assumption_group(self) -> flet.Container:
        text = self._translator.text
        return group_box(
            text(MessageKey.GROUP_DESIGN_ASSUMPTIONS),
            [
                grid_heading(text(MessageKey.COLUMN_ASSUMED), text(MessageKey.COLUMN_COMPUTED)),
                *self._rows(DESIGN_ASSUMPTION_FIELDS, show_reference_column=True),
            ],
            marker_color=METAL_COLOR,
            trailing=self._use_computed_coefficients_button,
        )

    def _rows(
        self,
        specifications: tuple[NumericFieldSpecification, ...],
        show_reference_column: bool = False,
    ) -> list[flet.Control]:
        return [
            self._fields[specification.key].as_row(show_reference_column)
            for specification in specifications
        ]
