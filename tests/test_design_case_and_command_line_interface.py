from __future__ import annotations

import dataclasses
import json
import tomllib
from pathlib import Path

import pytest

from pool_heat_exchanger_designer import (
    AssumedHeatTransferCoefficients,
    DesignCase,
    PitchLayout,
    design_case_as_toml_text,
    read_design_case_from_toml_path,
    write_design_case_to_toml_path,
)
from pool_heat_exchanger_designer.calculation.command_line_interface import (
    EXIT_CODE_CONSTRAINT_VIOLATED,
    EXIT_CODE_DESIGN_ERROR,
    EXIT_CODE_RESULTS_DIFFER,
    EXIT_CODE_SUCCESS,
    compare_result_dictionaries,
    main,
)
from pool_heat_exchanger_designer.calculation.design_errors import (
    DesignCaseFileError,
    InvalidGeometryError,
    InvalidOperatingConditionError,
)
from pool_heat_exchanger_designer.calculation.design_evaluation import evaluate_design_case
from pool_heat_exchanger_designer.calculation.iteration_history import IterationHistory
from pool_heat_exchanger_designer.calculation.language import Language
from pool_heat_exchanger_designer.calculation.message_catalogue import MessageKey
from pool_heat_exchanger_designer.calculation.properties import (
    LiquidWaterPropertiesInterpolatedFromTable as PropertySource,
)
from pool_heat_exchanger_designer.calculation.standards import (
    pitch_ratio_check,
    pool_temperature_check,
    shell_diameter_to_tube_length_ratio_check,
    unsatisfied_checks,
)
from pool_heat_exchanger_designer.calculation.thermal import (
    thermal_duty_from_tube_side_temperature_rise,
)
from pool_heat_exchanger_designer.calculation.translator import Translator

EXAMPLE_DESIGN_CASE_PATH = (
    Path(__file__).parent.parent / "examples" / "olympic_pool_fifty_meter.toml"
)

PYPROJECT_PATH = Path(__file__).parent.parent / "pyproject.toml"


def test_the_version_flag_prints_the_version_declared_in_pyproject(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with PYPROJECT_PATH.open("rb") as pyproject_file:
        declared_version = tomllib.load(pyproject_file)["project"]["version"]

    with pytest.raises(SystemExit) as exit_information:
        main(["--version"])

    assert exit_information.value.code == 0
    assert capsys.readouterr().out.strip() == f"poolhx {declared_version}"


def test_a_design_case_survives_a_write_and_read_round_trip(
    representative_design_case: DesignCase, tmp_path: Path
) -> None:
    written_path = tmp_path / "round_trip.toml"
    write_design_case_to_toml_path(representative_design_case, written_path)
    read_back = read_design_case_from_toml_path(written_path)

    assert read_back.operating_conditions == (representative_design_case.operating_conditions)
    assert read_back.tube_bundle == representative_design_case.tube_bundle
    assert read_back.shell == representative_design_case.shell
    assert read_back.tube_wall_material == representative_design_case.tube_wall_material
    assert read_back.assumed_heat_transfer_coefficients == (
        representative_design_case.assumed_heat_transfer_coefficients
    )


def test_the_shipped_example_design_case_reads_and_evaluates(
    property_source: PropertySource,
) -> None:
    design_case = read_design_case_from_toml_path(EXAMPLE_DESIGN_CASE_PATH)
    evaluation = evaluate_design_case(property_source, design_case)

    assert evaluation.thermal_duty.heat_duty_watts > 0.0
    assert design_case.tube_bundle.pitch_layout is PitchLayout.TRIANGULAR


def test_a_design_case_missing_a_section_names_the_missing_section(
    tmp_path: Path,
) -> None:
    incomplete_path = tmp_path / "incomplete.toml"
    incomplete_path.write_text('name = "incomplete"\n', encoding="utf-8")

    with pytest.raises(DesignCaseFileError, match="missing the sections"):
        read_design_case_from_toml_path(incomplete_path)


def test_a_design_case_with_text_where_a_number_belongs_is_refused(
    representative_design_case: DesignCase, tmp_path: Path
) -> None:
    broken_path = tmp_path / "broken.toml"
    broken_path.write_text(
        design_case_as_toml_text(representative_design_case).replace(
            "tube_count = 700", 'tube_count = "seven hundred"'
        ),
        encoding="utf-8",
    )

    with pytest.raises(DesignCaseFileError, match="must be a number"):
        read_design_case_from_toml_path(broken_path)


def test_a_design_case_with_an_unknown_pitch_layout_lists_the_selectable_ones(
    representative_design_case: DesignCase, tmp_path: Path
) -> None:
    broken_path = tmp_path / "unknown_layout.toml"
    broken_path.write_text(
        design_case_as_toml_text(representative_design_case).replace(
            'pitch_layout = "triangular"', 'pitch_layout = "hexagonal"'
        ),
        encoding="utf-8",
    )

    with pytest.raises(DesignCaseFileError, match="square, triangular"):
        read_design_case_from_toml_path(broken_path)


def test_a_missing_design_case_file_is_reported_as_a_design_error(
    tmp_path: Path,
) -> None:
    with pytest.raises(DesignCaseFileError, match="not found"):
        read_design_case_from_toml_path(tmp_path / "absent.toml")


def test_a_baffle_spacing_longer_than_the_tube_is_refused(
    representative_design_case: DesignCase,
) -> None:
    with pytest.raises(InvalidGeometryError, match="Baffle spacing cannot exceed"):
        DesignCase(
            name=representative_design_case.name,
            operating_conditions=representative_design_case.operating_conditions,
            tube_bundle=representative_design_case.tube_bundle,
            shell=type(representative_design_case.shell)(
                inner_diameter_meters=0.9, baffle_spacing_meters=99.0
            ),
            tube_wall_material=representative_design_case.tube_wall_material,
            assumed_heat_transfer_coefficients=(
                representative_design_case.assumed_heat_transfer_coefficients
            ),
        )


def test_a_tube_side_outlet_below_the_inlet_is_refused(property_source: PropertySource) -> None:
    with pytest.raises(InvalidOperatingConditionError, match="not being heated"):
        thermal_duty_from_tube_side_temperature_rise(property_source, 28.0, 13.0, 40.0, 80.0, 20.0)


def test_a_shell_side_inlet_below_the_tube_side_outlet_is_refused(
    property_source: PropertySource,
) -> None:
    with pytest.raises(InvalidOperatingConditionError, match="required direction"):
        thermal_duty_from_tube_side_temperature_rise(property_source, 13.0, 28.0, 40.0, 25.0, 20.0)


@pytest.mark.parametrize("tube_side_mass_flow_rate", [0.0, -5.0])
def test_a_non_positive_mass_flow_rate_is_refused(
    property_source: PropertySource, tube_side_mass_flow_rate: float
) -> None:
    with pytest.raises(InvalidOperatingConditionError, match="must be positive"):
        thermal_duty_from_tube_side_temperature_rise(
            property_source, 13.0, 28.0, tube_side_mass_flow_rate, 80.0, 20.0
        )


def test_the_tema_shell_slenderness_limit_catches_a_shell_that_is_too_wide() -> None:
    check = shell_diameter_to_tube_length_ratio_check(
        shell_inner_diameter_meters=1.5, tube_length_meters=6.0
    )

    assert check.actual_value == pytest.approx(0.25)
    assert not check.is_satisfied
    assert check.standard_key is MessageKey.STANDARD_TEMA
    assert check.standard_text(Translator(Language.ENGLISH)) == "TEMA"
    assert check.quantity_text(Translator(Language.TURKISH)) == "Gövde iç çapı / boru boyu"


def test_the_tema_pitch_ratio_limits_accept_the_textbook_window() -> None:
    assert pitch_ratio_check(1.25).is_satisfied
    assert pitch_ratio_check(1.5).is_satisfied
    assert not pitch_ratio_check(1.6).is_satisfied


def test_the_fina_pool_temperature_window_is_enforced_as_a_reported_check() -> None:
    assert pool_temperature_check(26.0).is_satisfied
    assert not pool_temperature_check(31.0).is_satisfied
    assert unsatisfied_checks((pool_temperature_check(31.0),))


def test_the_iteration_history_grows_with_each_new_design_and_exports_to_csv(
    property_source: PropertySource,
    representative_design_case: DesignCase,
) -> None:
    variant = dataclasses.replace(
        representative_design_case,
        assumed_heat_transfer_coefficients=AssumedHeatTransferCoefficients(1500.0, 3200.0),
    )
    history = IterationHistory()
    history.record(evaluate_design_case(property_source, representative_design_case))
    history.record(evaluate_design_case(property_source, variant))

    assert len(history) == 2
    assert [record.iteration_number for record in history.records()] == [1, 2]
    assert "is_consistent" in history.as_csv_text().splitlines()[0]


def test_recording_the_same_design_twice_in_a_row_adds_one_iteration(
    property_source: PropertySource,
    representative_design_case: DesignCase,
) -> None:
    history = IterationHistory()
    history.record(evaluate_design_case(property_source, representative_design_case))
    history.record(evaluate_design_case(property_source, representative_design_case))

    assert len(history) == 1


def test_the_command_line_interface_evaluates_the_example_case(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    json_output_path = tmp_path / "result.json"
    exit_code = main(
        [
            "evaluate",
            str(EXAMPLE_DESIGN_CASE_PATH),
            "--json-output-path",
            str(json_output_path),
        ]
    )

    assert exit_code == EXIT_CODE_SUCCESS
    assert "THERMAL DUTY" in capsys.readouterr().out
    assert json.loads(json_output_path.read_text(encoding="utf-8"))["design_case_name"]


def test_the_command_line_interface_reports_a_missing_file_without_a_traceback(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    exit_code = main(["evaluate", str(tmp_path / "absent.toml")])

    assert exit_code == EXIT_CODE_DESIGN_ERROR
    assert "DesignCaseFileError" in capsys.readouterr().err


def test_the_command_line_interface_can_fail_on_an_unsatisfied_constraint(
    representative_design_case: DesignCase, tmp_path: Path
) -> None:
    violating_path = tmp_path / "violates_tema.toml"
    violating_path.write_text(
        design_case_as_toml_text(representative_design_case).replace(
            "inner_diameter_meters = 0.9", "inner_diameter_meters = 1.5"
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "evaluate",
            str(violating_path),
            "--quiet",
            "--fail-on-unsatisfied-constraint",
        ]
    )

    assert exit_code == EXIT_CODE_CONSTRAINT_VIOLATED


def test_two_identical_results_compare_as_equal(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"
    for output_path in (first_path, second_path):
        main(
            [
                "evaluate",
                str(EXAMPLE_DESIGN_CASE_PATH),
                "--quiet",
                "--json-output-path",
                str(output_path),
            ]
        )
    capsys.readouterr()

    exit_code = main(["compare", str(first_path), str(second_path)])

    assert exit_code == EXIT_CODE_SUCCESS
    assert "agree within" in capsys.readouterr().out


def test_two_different_results_compare_as_different_and_name_the_quantity(
    representative_design_case: DesignCase,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"
    changed_case_path = tmp_path / "changed.toml"
    changed_case_path.write_text(
        design_case_as_toml_text(representative_design_case).replace(
            "tube_count = 700", "tube_count = 800"
        ),
        encoding="utf-8",
    )
    write_design_case_to_toml_path(representative_design_case, tmp_path / "original.toml")

    for case_path, output_path in (
        (tmp_path / "original.toml", first_path),
        (changed_case_path, second_path),
    ):
        main(
            [
                "evaluate",
                str(case_path),
                "--quiet",
                "--json-output-path",
                str(output_path),
            ]
        )
    capsys.readouterr()

    exit_code = main(["compare", str(first_path), str(second_path)])
    output = capsys.readouterr().out

    assert exit_code == EXIT_CODE_RESULTS_DIFFER
    assert "inputs.tube_count" in output
    assert "tube_side.reynolds_number" in output


def test_the_comparison_ignores_differences_below_the_requested_tolerance() -> None:
    first = {"value": 1.0}
    second = {"value": 1.0 + 1.0e-12}

    assert compare_result_dictionaries(first, second, 1.0e-9) == []
    assert compare_result_dictionaries(first, second, 1.0e-15)
