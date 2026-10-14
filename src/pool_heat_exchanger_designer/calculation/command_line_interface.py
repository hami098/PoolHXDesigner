from __future__ import annotations

import argparse
import sys
import tomllib
from collections.abc import Sequence
from importlib.metadata import version as installed_distribution_version
from pathlib import Path

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
