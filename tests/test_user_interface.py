from __future__ import annotations

import asyncio
import types
from collections.abc import Iterator
from typing import Any

import pytest

pytest.importorskip("flet", reason="the graphical interface needs the gui extra")

import flet

from pool_heat_exchanger_designer import DesignCase
from pool_heat_exchanger_designer.calculation.language import Language
from pool_heat_exchanger_designer.calculation.translator import Translator
from pool_heat_exchanger_designer.user_interface.application import (
    DesignerApplication,
    StatusTone,
)
from pool_heat_exchanger_designer.user_interface.displayed_numbers import (
    number_text,
    signed_percent_text,
)
from pool_heat_exchanger_designer.user_interface.exchanger_schematic import (
    ExchangerSchematic,
    StreamTemperatures,
)
from pool_heat_exchanger_designer.user_interface.industrial_theme import FAILURE_COLOR


def make_offscreen_page(served_over_http: bool = False) -> Any:
    page = types.SimpleNamespace()
    page.added = []
    page.services = []
    page.title = None
    page.theme = None
    page.theme_mode = None
    page.bgcolor = None
    page.padding = None
    page.spacing = None
    page.width = None
    page.web = served_over_http
    page.on_resize = None
    page.window = types.SimpleNamespace(width=None, height=None, min_width=None, min_height=None)
    page.add = lambda *controls: page.added.extend(controls)
    page.clean = page.added.clear
    page.update = lambda *args, **kwargs: None
    page.run_task = lambda handler, *args, **kwargs: None
    page.run_thread = lambda handler, *args, **kwargs: None
    return page


def every_control_inside(control: Any) -> Iterator[Any]:
    yield control
    for child in getattr(control, "controls", None) or []:
        yield from every_control_inside(child)
    content = getattr(control, "content", None)
    if content is not None:
        yield from every_control_inside(content)


class FakeFilePicker:
    def __init__(self) -> None:
        self.saved: dict[str, Any] = {}

    async def save_file(self, **arguments: Any) -> str | None:
        self.saved = arguments
        return None


@pytest.fixture
def offscreen_page() -> Any:
    return make_offscreen_page()


@pytest.fixture
def application(offscreen_page: Any) -> DesignerApplication:
    built = DesignerApplication(offscreen_page)
    built.build()
    return built


def test_the_interface_builds_without_a_display(
    application: DesignerApplication, offscreen_page: Any
) -> None:
    assert offscreen_page.title
    assert len(offscreen_page.added) == 1
    assert len(offscreen_page.services) == 1
    assert offscreen_page.theme_mode == flet.ThemeMode.LIGHT


def test_the_interface_starts_on_the_inputs_page_ready_to_calculate(
    application: DesignerApplication,
) -> None:
    assert application._form.invalid_field_labels() == ()
    assert application._calculate_button.disabled is False
    assert application.showing_results is False
    assert application.status_tone is StatusTone.INFORMATION


def test_calculating_opens_the_results_page_and_records_one_iteration(
    application: DesignerApplication,
) -> None:
    application._calculate()

    assert len(application._history) == 1
    assert application._results.has_results
    assert application.showing_results is True
    assert application.status_tone is StatusTone.SUCCESS
    assert "Iteration 1" in application.status_message


def test_calculating_the_same_design_again_does_not_add_a_history_row(
    application: DesignerApplication,
) -> None:
    application._calculate()
    application._calculate()

    assert len(application._history) == 1


def test_using_the_computed_coefficients_makes_them_agree_but_does_not_claim_a_consistent_design(
    application: DesignerApplication,
) -> None:
    application._calculate()
    application._use_computed_coefficients()

    second = application._history.records()[1]
    assert second.has_converged is True
    assert second.is_consistent is False
    assert application._last_evaluation is not None
    assert not application._last_evaluation.is_consistent()


def test_using_the_suggested_geometry_enters_the_whole_suggested_tube_count(
    application: DesignerApplication,
) -> None:
    application._calculate()
    first = application._last_evaluation
    assert first is not None

    application._use_suggested_geometry()

    assert application._form.field("tube_count").entered_text == str(
        first.preliminary_sizing.suggested_whole_tube_count
    )
    assert application._last_evaluation is not None
    assert application._last_evaluation.geometry_agreement.entered_matches_suggested()


def test_an_empty_field_blocks_calculation_and_names_its_group_and_itself(
    application: DesignerApplication,
) -> None:
    field = application._form.field("tube_count")
    field.set_text("")
    field.refresh_validation_message()
    application._refresh_readiness()

    assert application._calculate_button.disabled is True
    assert application.status_tone is StatusTone.FAILURE
    assert "Shell and baffles › Tube count" in application.status_message
    assert field.shown_rejection_message == "Enter 1 to 20000"


def test_an_impossible_temperature_rise_is_reported_and_keeps_the_inputs_page_open(
    application: DesignerApplication,
) -> None:
    application._form.field("tube_side_outlet_temperature_celsius").set_value(5.0)
    application._calculate()

    assert "not being heated" in application.status_message
    assert application.status_tone is StatusTone.FAILURE
    assert application.showing_results is False
    assert not application._results.has_results


def test_a_standards_violation_is_shown_as_one_failed_check_while_results_still_appear(
    application: DesignerApplication,
) -> None:
    application._form.field("shell_inner_diameter_meters").set_value(1.5)
    application._calculate()

    failed_icons = [
        control
        for control in every_control_inside(application._results.control)
        if isinstance(control, flet.Icon) and control.color == FAILURE_COLOR
    ]
    assert application._results.has_results
    assert len(failed_icons) == 1


def test_the_suggested_and_computed_columns_are_filled_after_a_calculation(
    application: DesignerApplication,
) -> None:
    application._calculate()
    evaluation = application._last_evaluation
    assert evaluation is not None

    assert application._form.field("shell_inner_diameter_meters").shown_reference_value
    assert application._form.field("tube_count").shown_reference_value == str(
        evaluation.preliminary_sizing.suggested_whole_tube_count
    )
    assert application._form.field(
        "assumed_tube_side_watts_per_square_meter_kelvin"
    ).shown_reference_value


def test_changing_an_input_after_calculating_says_the_results_are_out_of_date(
    application: DesignerApplication,
) -> None:
    application._calculate()
    application._form.field("tube_count").set_text("800")
    application._handle_input_change()

    assert application.status_tone is StatusTone.ATTENTION
    assert "Inputs changed" in application.status_message


def test_a_design_case_loaded_into_the_form_round_trips_back_out(
    application: DesignerApplication, representative_design_case: DesignCase
) -> None:
    application._form.load_design_case(representative_design_case)
    rebuilt = application._form.build_design_case(representative_design_case.name)

    assert rebuilt.operating_conditions == representative_design_case.operating_conditions
    assert rebuilt.tube_bundle == representative_design_case.tube_bundle
    assert rebuilt.shell == representative_design_case.shell


def test_saving_in_a_browser_hands_the_file_contents_over_as_a_download(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    page = make_offscreen_page(served_over_http=True)
    application = DesignerApplication(page)
    application.build()
    file_picker = FakeFilePicker()
    monkeypatch.setattr(application, "_file_picker", file_picker)

    asyncio.run(application._save_design_case())

    assert file_picker.saved["src_bytes"].startswith(b"name = ")
    assert file_picker.saved["file_name"] == "design_case.toml"
    assert file_picker.saved["file_type"] == flet.FilePickerFileType.CUSTOM
    assert "downloaded" in application.status_message


def test_numbers_are_shown_with_a_fixed_number_of_decimals() -> None:
    assert number_text(2508.96, 1) == "2509.0"
    assert number_text(0.59861, 2) == "0.60"
    assert signed_percent_text(-0.53355) == "-53.4 %"


def test_a_missing_or_non_finite_value_renders_as_a_dash_instead_of_crashing() -> None:
    assert number_text(None, 2) == "—"
    assert number_text(float("inf"), 2) == "—"


def test_the_schematic_draws_the_return_head_only_for_two_tube_passes() -> None:
    schematic = ExchangerSchematic(Translator(Language.ENGLISH))
    temperatures = StreamTemperatures(13.0, 28.0, 80.0, None)

    schematic.show(temperatures, tube_side_pass_count=1)
    one_pass_shapes = schematic.shape_count
    schematic.show(temperatures, tube_side_pass_count=2)

    assert schematic.shape_count > one_pass_shapes


@pytest.mark.parametrize(
    ("entered_text", "expected_value"),
    [("19", 19.0), ("19.5", 19.5), ("19,5", 19.5), ("22,75", 22.75)],
)
def test_a_decimal_comma_is_accepted_because_a_turkish_keyboard_produces_one(
    application: DesignerApplication, entered_text: str, expected_value: float
) -> None:
    field = application._form.field("tube_outer_diameter_millimeters")
    field.set_text(entered_text)

    assert field.parsed_value == pytest.approx(expected_value)
    assert field.is_valid


def test_text_that_is_not_a_number_at_all_is_rejected_without_raising(
    application: DesignerApplication,
) -> None:
    field = application._form.field("tube_outer_diameter_millimeters")
    field.set_text("1.2.3")

    assert field.parsed_value is None
    assert not field.is_valid


def test_a_value_below_the_fields_accepted_range_is_rejected_with_the_range_named(
    application: DesignerApplication,
) -> None:
    field = application._form.field("tube_outer_diameter_millimeters")
    field.set_text("0,45")
    field.refresh_validation_message()

    assert field.parsed_value is None
    assert field.shown_rejection_message == "Enter 1 to 250 mm"


def test_a_missing_interface_client_package_names_the_extra_to_install(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pool_heat_exchanger_designer.calculation.design_errors import (
        GraphicalInterfaceUnavailableError,
    )
    from pool_heat_exchanger_designer.user_interface import application

    monkeypatch.setattr(application, "find_spec", lambda name: None)

    with pytest.raises(GraphicalInterfaceUnavailableError, match="web-interface"):
        application.require_the_client_package(application.WEB_SERVER_CLIENT_PACKAGE)
    with pytest.raises(GraphicalInterfaceUnavailableError, match="desktop-interface"):
        application.require_the_client_package(application.DESKTOP_WINDOW_CLIENT_PACKAGE)


def test_an_installed_interface_client_package_is_accepted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pool_heat_exchanger_designer.user_interface import application

    monkeypatch.setattr(application, "find_spec", lambda name: object())

    application.require_the_client_package(application.WEB_SERVER_CLIENT_PACKAGE)


def test_a_packaged_desktop_app_starts_without_the_desktop_client_package(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import flet

    from pool_heat_exchanger_designer.user_interface import application

    launched = []
    monkeypatch.setattr(application, "find_spec", lambda name: None)
    monkeypatch.setenv("FLET_PLATFORM", "windows")
    monkeypatch.setattr(flet, "run", lambda main: launched.append(main))

    application.start_graphical_interface()

    assert len(launched) == 1


@pytest.mark.parametrize(
    ("language", "expected_title"),
    [
        (Language.ENGLISH, "Pool Heat Exchanger Designer"),
        (Language.TURKISH, "Havuz Isı Değiştirici Tasarımcısı"),
    ],
    ids=lambda item: getattr(item, "value", item),
)
def test_the_interface_builds_in_the_language_it_was_given(
    language: Language, expected_title: str
) -> None:
    page = make_offscreen_page()
    DesignerApplication(page, language).build()

    assert page.title == expected_title


def test_switching_language_retranslates_the_screen_and_keeps_what_was_typed() -> None:
    page = make_offscreen_page()
    application = DesignerApplication(page, Language.ENGLISH)
    application.build()
    application._form.field("tube_count").set_text("850")
    application._calculate()

    application.rebuild_in_language(Language.TURKISH)

    assert page.title == "Havuz Isı Değiştirici Tasarımcısı"
    assert application._form.field("tube_count").entered_text == "850"
    assert application._results.has_results
    assert application.showing_results is True
    assert "Hesaplandı" in application.status_message


def test_a_field_rejection_message_is_translated() -> None:
    page = make_offscreen_page()
    application = DesignerApplication(page, Language.TURKISH)
    application.build()
    field = application._form.field("tube_count")
    field.set_text("")
    field.refresh_validation_message()

    assert field.shown_rejection_message == "1 ile 20000 arasında girin"
