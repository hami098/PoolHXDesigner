from __future__ import annotations

import argparse
import json
import sys
import tomllib
from collections.abc import Sequence
from importlib.metadata import version as installed_distribution_version
from pathlib import Path
from typing import Any

from pool_heat_exchanger_designer.calculation.design_case import read_design_case_from_toml_path
from pool_heat_exchanger_designer.calculation.design_errors import DesignError
from pool_heat_exchanger_designer.calculation.design_evaluation import evaluate_design_case
from pool_heat_exchanger_designer.calculation.design_report import (
    design_evaluation_as_aligned_text,
    write_design_evaluation_to_json_path,
)
from pool_heat_exchanger_designer.calculation.language import (
    DEFAULT_LANGUAGE,
    SELECTABLE_LANGUAGES,
    Language,
)
from pool_heat_exchanger_designer.calculation.message_catalogue import MessageKey
from pool_heat_exchanger_designer.calculation.properties import (
    liquid_water_properties_shipped_with_this_package,
)
from pool_heat_exchanger_designer.calculation.standards import unsatisfied_checks
from pool_heat_exchanger_designer.calculation.translator import Translator

EXIT_CODE_SUCCESS = 0
EXIT_CODE_DESIGN_ERROR = 2
EXIT_CODE_CONSTRAINT_VIOLATED = 3
EXIT_CODE_RESULTS_DIFFER = 4

COMPARISON_RELATIVE_TOLERANCE = 1.0e-9


def program_version() -> str:
    pyproject_path = Path(__file__).resolve().parents[3] / "pyproject.toml"
    if pyproject_path.exists():
        with pyproject_path.open("rb") as pyproject_file:
            return str(tomllib.load(pyproject_file)["project"]["version"])
    return installed_distribution_version("pool-heat-exchanger-designer")


def build_argument_parser() -> argparse.ArgumentParser:
    english = Translator(DEFAULT_LANGUAGE)
    parser = argparse.ArgumentParser(
        prog="poolhx",
        description=english.text(MessageKey.COMMAND_DESCRIPTION),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {program_version()}",
        help=english.text(MessageKey.COMMAND_VERSION_HELP),
    )
    parser.add_argument(
        "--language",
        type=Language,
        choices=SELECTABLE_LANGUAGES,
        default=DEFAULT_LANGUAGE,
        help=english.text(MessageKey.COMMAND_LANGUAGE_HELP),
    )
    subcommands = parser.add_subparsers(dest="subcommand", required=True)

    evaluate = subcommands.add_parser(
        "evaluate",
        help=english.text(MessageKey.COMMAND_EVALUATE_HELP),
    )
    evaluate.add_argument("design_case_path", type=Path)
    evaluate.add_argument(
        "--json-output-path",
        type=Path,
        default=None,
        help=english.text(MessageKey.COMMAND_JSON_OUTPUT_HELP),
    )
    evaluate.add_argument(
        "--quiet",
        action="store_true",
        help=english.text(MessageKey.COMMAND_QUIET_HELP),
    )
    evaluate.add_argument(
        "--fail-on-unsatisfied-constraint",
        action="store_true",
        help=english.text(MessageKey.COMMAND_FAIL_ON_CONSTRAINT_HELP),
    )

    compare = subcommands.add_parser(
        "compare",
        help=english.text(MessageKey.COMMAND_COMPARE_HELP),
    )
    compare.add_argument("first_result_path", type=Path)
    compare.add_argument("second_result_path", type=Path)
    compare.add_argument(
        "--relative-tolerance",
        type=float,
        default=COMPARISON_RELATIVE_TOLERANCE,
    )

    graphical_interface = subcommands.add_parser(
        "gui",
        help=english.text(MessageKey.COMMAND_GUI_HELP),
    )
    graphical_interface.add_argument(
        "--web",
        action="store_true",
        help=english.text(MessageKey.COMMAND_WEB_HELP),
    )
    graphical_interface.add_argument("--host", default="127.0.0.1")
    graphical_interface.add_argument("--port", type=int, default=8550)

    return parser


def main(argument_values: Sequence[str] | None = None) -> int:
    arguments = build_argument_parser().parse_args(argument_values)
    translator = Translator(arguments.language)
    try:
        if arguments.subcommand == "evaluate":
            return _run_evaluate(arguments, translator)
        if arguments.subcommand == "compare":
            return _run_compare(arguments, translator)
        return _run_graphical_interface(arguments, translator)
    except DesignError as design_error:
        print(
            f"{type(design_error).__name__}: {design_error.text_in_language(translator.language)}",
            file=sys.stderr,
        )
        return EXIT_CODE_DESIGN_ERROR


def _run_evaluate(arguments: argparse.Namespace, translator: Translator) -> int:
    design_case = read_design_case_from_toml_path(arguments.design_case_path)
    evaluation = evaluate_design_case(
        liquid_water_properties_shipped_with_this_package(), design_case
    )

    if not arguments.quiet:
        print(design_evaluation_as_aligned_text(evaluation, translator), end="")

    if arguments.json_output_path is not None:
        write_design_evaluation_to_json_path(evaluation, arguments.json_output_path)

    unsatisfied = unsatisfied_checks(evaluation.constraint_checks)
    if unsatisfied and arguments.fail_on_unsatisfied_constraint:
        return EXIT_CODE_CONSTRAINT_VIOLATED
    return EXIT_CODE_SUCCESS


def _run_compare(arguments: argparse.Namespace, translator: Translator) -> int:
    first = _read_json(arguments.first_result_path)
    second = _read_json(arguments.second_result_path)
    differences = compare_result_dictionaries(first, second, arguments.relative_tolerance)

    if not differences:
        print(translator.text(MessageKey.COMMAND_RESULTS_AGREE))
        return EXIT_CODE_SUCCESS

    quantity_word = translator.text(MessageKey.COMMAND_COMPARISON_QUANTITY)
    first_word = translator.text(MessageKey.COMMAND_COMPARISON_FIRST)
    second_word = translator.text(MessageKey.COMMAND_COMPARISON_SECOND)
    relative_word = translator.text(MessageKey.COMMAND_COMPARISON_RELATIVE)
    print(f"{quantity_word:<66}{first_word:>16}{second_word:>16}{relative_word:>14}")
    for path, first_value, second_value, relative_difference in differences:
        relative_text = "-" if relative_difference is None else f"{relative_difference:.3e}"
        print(
            f"{path:<66}{_format_value(first_value):>16}"
            f"{_format_value(second_value):>16}{relative_text:>14}"
        )
    return EXIT_CODE_RESULTS_DIFFER


def _run_graphical_interface(arguments: argparse.Namespace, translator: Translator) -> int:
    try:
        from pool_heat_exchanger_designer.user_interface.application import (
            start_graphical_interface,
        )
    except ImportError as missing_graphical_dependency:
        print(
            translator.text(
                MessageKey.COMMAND_INTERFACE_NEEDS_FLET,
                reason=missing_graphical_dependency,
            ),
            file=sys.stderr,
        )
        return EXIT_CODE_DESIGN_ERROR

    start_graphical_interface(
        serve_over_http=arguments.web,
        host=arguments.host,
        port=arguments.port,
        language=translator.language,
    )
    return EXIT_CODE_SUCCESS


def compare_result_dictionaries(
    first: dict[str, Any],
    second: dict[str, Any],
    relative_tolerance: float = COMPARISON_RELATIVE_TOLERANCE,
) -> list[tuple[str, Any, Any, float | None]]:
    differences: list[tuple[str, Any, Any, float | None]] = []
    _collect_differences(first, second, "", relative_tolerance, differences)
    return differences


def _collect_differences(
    first: Any,
    second: Any,
    path: str,
    relative_tolerance: float,
    differences: list[tuple[str, Any, Any, float | None]],
) -> None:
    if isinstance(first, dict) and isinstance(second, dict):
        for key in dict.fromkeys([*first, *second]):
            _collect_differences(
                first.get(key),
                second.get(key),
                f"{path}.{key}" if path else str(key),
                relative_tolerance,
                differences,
            )
        return

    if isinstance(first, list) and isinstance(second, list):
        for index in range(max(len(first), len(second))):
            _collect_differences(
                first[index] if index < len(first) else None,
                second[index] if index < len(second) else None,
                f"{path}[{index}]",
                relative_tolerance,
                differences,
            )
        return

    if isinstance(first, bool) or isinstance(second, bool):
        if first != second:
            differences.append((path, first, second, None))
        return

    if isinstance(first, (int, float)) and isinstance(second, (int, float)):
        relative_difference = _relative_difference(float(first), float(second))
        if relative_difference > relative_tolerance:
            differences.append((path, first, second, relative_difference))
        return

    if first != second:
        differences.append((path, first, second, None))


def _relative_difference(first: float, second: float) -> float:
    if first == second:
        return 0.0
    largest_magnitude = max(abs(first), abs(second))
    if largest_magnitude == 0.0:
        return 0.0
    return abs(first - second) / largest_magnitude


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return parsed
    except FileNotFoundError as missing_file:
        raise DesignError(MessageKey.RESULT_FILE_NOT_FOUND, path=path) from missing_file
    except json.JSONDecodeError as malformed_file:
        raise DesignError(
            MessageKey.RESULT_FILE_IS_NOT_VALID_JSON,
            path=path,
            reason=malformed_file,
        ) from (malformed_file)


def _format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)
