from __future__ import annotations

import ast
import re
import tokenize
from pathlib import Path

import pytest

REPOSITORY_DIRECTORY = Path(__file__).parent.parent
TESTS_DIRECTORY = Path(__file__).parent
PACKAGE_DIRECTORY = REPOSITORY_DIRECTORY / "src" / "pool_heat_exchanger_designer"
MESSAGE_CATALOGUE_FILE = PACKAGE_DIRECTORY / "calculation" / "message_catalogue.py"
DECISION_RECORD_DIRECTORY = Path(__file__).parent.parent / "docs" / "decisions"
VALIDATION_DOCUMENT = Path(__file__).parent.parent / "docs" / "validation.md"

UNITS_THAT_MUST_APPEAR_IN_A_NAME = (
    "celsius",
    "kelvin",
    "meters",
    "watts",
    "pascal",
    "kilograms",
    "joules",
)

CORRELATION_FUNCTIONS_THAT_MUST_BE_CITED = (
    "petukhov_smooth_tube_fanning_friction_factor",
    "gnielinski_nusselt_number",
    "kern_heat_transfer_coefficient_watts_per_square_meter_kelvin",
    "kern_friction_factor",
    "kern_pressure_drop_pascal",
    "equivalent_diameter_meters",
    "referred_to_outside_area",
    "counterflow_log_mean_temperature_difference_kelvin",
)


def package_source_files() -> list[Path]:
    return sorted(PACKAGE_DIRECTORY.rglob("*.py"))


def package_and_test_source_files() -> list[Path]:
    return [*package_source_files(), *sorted(TESTS_DIRECTORY.rglob("*.py"))]


def repository_relative_name(path: Path) -> str:
    return path.relative_to(REPOSITORY_DIRECTORY).as_posix()


@pytest.mark.parametrize(
    "source_file", package_and_test_source_files(), ids=repository_relative_name
)
def test_no_source_file_carries_a_comment(source_file: Path) -> None:
    with source_file.open("rb") as handle:
        comments = [
            f"{source_file.name}:{token.start[0]}: {token.string}"
            for token in tokenize.tokenize(handle.readline)
            if token.type == tokenize.COMMENT
        ]

    assert comments == []


@pytest.mark.parametrize(
    "source_file", package_and_test_source_files(), ids=repository_relative_name
)
def test_no_source_file_carries_a_docstring(source_file: Path) -> None:
    tree = ast.parse(source_file.read_text(encoding="utf-8"))
    documented = [
        getattr(node, "name", "<module>")
        for node in ast.walk(tree)
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
        and ast.get_docstring(node)
    ]

    assert documented == []


def test_every_message_in_the_catalogue_is_used_somewhere() -> None:
    from pool_heat_exchanger_designer.calculation.message_catalogue import MessageKey

    sources = "\n".join(
        source_file.read_text(encoding="utf-8")
        for source_file in package_source_files()
        if source_file != MESSAGE_CATALOGUE_FILE
    )
    unused = [
        key.name for key in MessageKey if not re.search(rf"MessageKey\.{key.name}\b", sources)
    ]

    assert unused == []


def test_the_calculation_core_never_imports_the_user_interface_library() -> None:
    offenders = []
    for source_file in package_source_files():
        if "user_interface" in source_file.parts:
            continue
        tree = ast.parse(source_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) and any(
                alias.name.split(".")[0] == "flet" for alias in node.names
            ):
                offenders.append(source_file.name)
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("flet"):
                offenders.append(source_file.name)

    assert offenders == []


def test_every_correlation_is_cited_in_the_validation_document() -> None:
    validation_text = VALIDATION_DOCUMENT.read_text(encoding="utf-8")
    uncited = [
        function_name
        for function_name in CORRELATION_FUNCTIONS_THAT_MUST_BE_CITED
        if function_name not in validation_text
    ]

    assert uncited == []


def test_every_decision_record_is_listed_in_the_index() -> None:
    index_text = (DECISION_RECORD_DIRECTORY / "0000-index.md").read_text(encoding="utf-8")
    unlisted = [
        record.name
        for record in sorted(DECISION_RECORD_DIRECTORY.glob("0*.md"))
        if record.name != "0000-index.md" and record.name not in index_text
    ]

    assert unlisted == []


def test_every_decision_record_states_what_was_rejected() -> None:
    without_rejected_alternatives = [
        record.name
        for record in sorted(DECISION_RECORD_DIRECTORY.glob("0*.md"))
        if record.name != "0000-index.md"
        and "rejected" not in record.read_text(encoding="utf-8").lower()
    ]

    assert without_rejected_alternatives == []


def _class_carries_its_unit_as_a_field(node: ast.ClassDef) -> bool:
    return any(
        isinstance(statement, ast.AnnAssign)
        and isinstance(statement.target, ast.Name)
        and statement.target.id == "unit"
        for statement in node.body
    )


def test_public_dataclass_fields_that_carry_a_physical_quantity_name_their_unit() -> None:
    offenders: list[str] = []
    for source_file in package_source_files():
        if "user_interface" in source_file.parts:
            continue
        tree = ast.parse(source_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if _class_carries_its_unit_as_a_field(node):
                continue
            for statement in node.body:
                if not isinstance(statement, ast.AnnAssign):
                    continue
                if not isinstance(statement.target, ast.Name):
                    continue
                field_name = statement.target.id
                annotation = ast.unparse(statement.annotation)
                if annotation != "float":
                    continue
                dimensionless = (
                    "number" in field_name
                    or "ratio" in field_name
                    or "factor" in field_name
                    or "count" in field_name
                    or ("difference" in field_name and "temperature" not in field_name)
                )
                if dimensionless:
                    continue
                if not any(unit in field_name for unit in UNITS_THAT_MUST_APPEAR_IN_A_NAME):
                    offenders.append(f"{source_file.name}:{node.name}.{field_name}")

    assert offenders == []


TURKISH_SPECIFIC_LETTERS = "ğĞışŞİöÖüÜçÇ"

FILES_ALLOWED_TO_CARRY_TURKISH = frozenset({"message_catalogue.py", "language.py"})


@pytest.mark.parametrize("source_file", package_source_files(), ids=lambda path: path.name)
def test_only_the_text_catalogue_carries_turkish(source_file: Path) -> None:
    if source_file.name in FILES_ALLOWED_TO_CARRY_TURKISH:
        return
    offending_lines = [
        f"{line_number}: {line.strip()}"
        for line_number, line in enumerate(source_file.read_text(encoding="utf-8").splitlines(), 1)
        if any(letter in line for letter in TURKISH_SPECIFIC_LETTERS)
    ]

    assert offending_lines == []


def test_the_text_catalogue_is_the_only_place_that_names_a_language() -> None:
    package_modules_naming_turkish = [
        source_file.name
        for source_file in package_source_files()
        if source_file.name not in FILES_ALLOWED_TO_CARRY_TURKISH
        and "TURKISH" in source_file.read_text(encoding="utf-8")
    ]

    assert package_modules_naming_turkish == []
