from __future__ import annotations

import os
import tomllib
from enum import Enum
from importlib.util import find_spec
from pathlib import Path

import flet

from pool_heat_exchanger_designer.calculation.design_case import (
    design_case_as_toml_text,
    design_case_from_mapping,
)
from pool_heat_exchanger_designer.calculation.design_errors import (
    DesignError,
    GraphicalInterfaceUnavailableError,
)
from pool_heat_exchanger_designer.calculation.design_evaluation import (
    DesignEvaluation,
    evaluate_design_case,
)
from pool_heat_exchanger_designer.calculation.iteration_history import IterationHistory
from pool_heat_exchanger_designer.calculation.language import (
    DEFAULT_LANGUAGE,
    SELECTABLE_LANGUAGES,
    Language,
)
from pool_heat_exchanger_designer.calculation.message_catalogue import MessageKey
from pool_heat_exchanger_designer.calculation.properties import (
    liquid_water_properties_shipped_with_this_package,
)
from pool_heat_exchanger_designer.calculation.translator import Translator
from pool_heat_exchanger_designer.user_interface.design_form import DesignForm
from pool_heat_exchanger_designer.user_interface.exchanger_schematic import ExchangerSchematic
from pool_heat_exchanger_designer.user_interface.industrial_theme import (
    ACCENT_COLOR,
    APPLICATION_TITLE_TEXT_SIZE,
    ATTENTION_COLOR,
    BODY_TEXT_SIZE,
    BORDER_WIDTH,
    COLUMN_GAP,
    FAILURE_COLOR,
    GROUP_GAP,
    ONE_GROUP_PER_ROW,
    PAGE_BACKGROUND_COLOR,
    PAGE_PADDING,
    PANEL_BACKGROUND_COLOR,
    PANEL_BORDER_COLOR,
    PRIMARY_TEXT_COLOR,
    SATISFIED_COLOR,
    SECONDARY_TEXT_COLOR,
    STATUS_ICON_SIZE,
    centred_to_content_width,
    content_width_for,
    group_box,
    industrial_theme,
    primary_button,
    secondary_button,
    secondary_text,
    segmented_choice,
    toolbar_button,
)
from pool_heat_exchanger_designer.user_interface.result_panels import ResultsPage

DESIGN_CASE_FILE_NAME = "design_case.toml"
ITERATION_HISTORY_FILE_NAME = "iteration_history.csv"
DESIGN_CASE_FILE_EXTENSION = "toml"
ITERATION_HISTORY_FILE_EXTENSION = "csv"
TEXT_FILE_ENCODING = "utf-8"

INITIAL_WINDOW_WIDTH = 1360
INITIAL_WINDOW_HEIGHT = 900
MINIMUM_WINDOW_WIDTH = 760
MINIMUM_WINDOW_HEIGHT = 560
ACTIVE_TAB_UNDERLINE_WIDTH = 3

DESKTOP_WINDOW_CLIENT_PACKAGE = "flet_desktop"
WEB_SERVER_CLIENT_PACKAGE = "flet_web"

INSTALL_EXTRA_FOR_CLIENT_PACKAGE = {
    DESKTOP_WINDOW_CLIENT_PACKAGE: "desktop-interface",
    WEB_SERVER_CLIENT_PACKAGE: "web-interface",
}


class StatusTone(Enum):
    INFORMATION = (flet.Icons.INFO_OUTLINE, SECONDARY_TEXT_COLOR)
    SUCCESS = (flet.Icons.CHECK_CIRCLE, SATISFIED_COLOR)
    ATTENTION = (flet.Icons.WARNING_AMBER, ATTENTION_COLOR)
    FAILURE = (flet.Icons.ERROR_OUTLINE, FAILURE_COLOR)

    @property
    def icon(self) -> flet.IconData:
        return self.value[0]

    @property
    def color(self) -> str:
        return self.value[1]


class DesignerApplication:
    def __init__(self, page: flet.Page, language: Language = DEFAULT_LANGUAGE) -> None:
        self._page = page
        self._translator = Translator(language)
        self._property_source = liquid_water_properties_shipped_with_this_package()
        self._history = IterationHistory()
        self._last_evaluation: DesignEvaluation | None = None
        self._results_are_stale = False
        self._showing_results = False
        self._design_case_name = self._translator.text(MessageKey.UNTITLED_DESIGN_CASE)
        self._file_picker = flet.FilePicker()
        page.services.append(self._file_picker)
        self._assemble_widgets()

    @property
    def showing_results(self) -> bool:
        return self._showing_results

    @property
    def status_message(self) -> str:
        return self._status_text.value or ""

    @property
    def status_tone(self) -> StatusTone:
        return self._status_tone

    def _assemble_widgets(self) -> None:
        text = self._translator.text
        self._form = DesignForm(
            self._translator,
            on_any_change=self._handle_input_change,
            on_submit=self._calculate,
            on_use_suggested_geometry=self._use_suggested_geometry,
            on_use_computed_coefficients=self._use_computed_coefficients,
        )
        self._schematic = ExchangerSchematic(self._translator)
        self._results = ResultsPage(
            self._translator,
            on_use_computed_coefficients=self._use_computed_coefficients,
            on_use_suggested_geometry=self._use_suggested_geometry,
            on_export_history=self._export_history_in_the_background,
        )
        self._status_tone = StatusTone.INFORMATION
        self._status_icon = flet.Icon(
            StatusTone.INFORMATION.icon,
            size=STATUS_ICON_SIZE,
            color=StatusTone.INFORMATION.color,
        )
        self._status_text = flet.Text(
            text(MessageKey.STATUS_READY_TO_CALCULATE),
            size=BODY_TEXT_SIZE,
            color=PRIMARY_TEXT_COLOR,
            expand=True,
        )
        self._calculate_button = primary_button(
            text(MessageKey.BUTTON_CALCULATE), flet.Icons.CALCULATE, self._calculate
        )
        self._back_button = secondary_button(
            text(MessageKey.BUTTON_BACK_TO_INPUTS), flet.Icons.ARROW_BACK, self._show_inputs_page
        )
        self._design_case_name_text = flet.Text(
            self._design_case_name, size=BODY_TEXT_SIZE, color=SECONDARY_TEXT_COLOR
        )
        self._language_selector = segmented_choice(
            [(item.value, item.endonym) for item in SELECTABLE_LANGUAGES],
            self._translator.language.value,
            self._handle_language_selected,
        )
        self._language_selector.tooltip = text(MessageKey.LANGUAGE_SELECTOR_LABEL)
        self._inputs_tab_label = flet.Text(text(MessageKey.TAB_INPUTS), size=BODY_TEXT_SIZE)
        self._results_tab_label = flet.Text(text(MessageKey.TAB_RESULTS), size=BODY_TEXT_SIZE)
        self._inputs_tab = flet.Container(
            content=self._inputs_tab_label,
            padding=flet.Padding.symmetric(horizontal=16, vertical=10),
            on_click=self._show_inputs_page,
        )
        self._results_tab = flet.Container(
            content=self._results_tab_label,
            padding=flet.Padding.symmetric(horizontal=16, vertical=10),
            on_click=self._show_results_page,
        )
        self._inputs_content, inputs_centred = centred_to_content_width(
            flet.Column(
                controls=[
                    secondary_text(text(MessageKey.HINT_INPUTS), BODY_TEXT_SIZE),
                    flet.ResponsiveRow(
                        controls=[
                            group_box(
                                text(MessageKey.GROUP_FLOW_ARRANGEMENT),
                                [self._schematic.control],
                                column_layout=ONE_GROUP_PER_ROW,
                            ),
                            *self._form.group_controls(),
                        ],
                        spacing=GROUP_GAP,
                        run_spacing=GROUP_GAP,
                        vertical_alignment=flet.CrossAxisAlignment.STRETCH,
                    ),
                ],
                spacing=GROUP_GAP,
            )
        )
        self._results_content, results_centred = centred_to_content_width(self._results.control)
        self._inputs_page = flet.Column(
            controls=[inputs_centred], scroll=flet.ScrollMode.AUTO, expand=True
        )
        self._results_page = flet.Column(
            controls=[results_centred], scroll=flet.ScrollMode.AUTO, expand=True
        )
        self._body = flet.Container(
            content=self._inputs_page,
            expand=True,
            padding=flet.Padding.symmetric(horizontal=PAGE_PADDING, vertical=GROUP_GAP),
        )

    def build(self) -> None:
        page = self._page
        page.title = self._translator.text(MessageKey.APPLICATION_TITLE)
        page.theme = industrial_theme()
        page.theme_mode = flet.ThemeMode.LIGHT
        page.bgcolor = PAGE_BACKGROUND_COLOR
        page.padding = 0
        page.spacing = 0
        page.window.width = INITIAL_WINDOW_WIDTH
        page.window.height = INITIAL_WINDOW_HEIGHT
        page.window.min_width = MINIMUM_WINDOW_WIDTH
        page.window.min_height = MINIMUM_WINDOW_HEIGHT
        page.on_resize = self._fit_content_width
        page.add(self._layout())
        self._after_layout()
        self._refresh_readiness()

    def _after_layout(self) -> None:
        self._fit_content_width()
        self._refresh_schematic()
        if self._showing_results:
            self._show_results_page()
        else:
            self._show_inputs_page()

    def _layout(self) -> flet.Control:
        text = self._translator.text
        return flet.Column(
            controls=[
                flet.Container(
                    content=flet.Row(
                        controls=[
                            flet.Text(
                                text(MessageKey.APPLICATION_TITLE),
                                size=APPLICATION_TITLE_TEXT_SIZE,
                                weight=flet.FontWeight.W_700,
                                color=PRIMARY_TEXT_COLOR,
                            ),
                            flet.Container(
                                width=BORDER_WIDTH, height=18, bgcolor=PANEL_BORDER_COLOR
                            ),
                            self._design_case_name_text,
                            flet.Container(expand=True),
                            flet.Icon(flet.Icons.TRANSLATE, size=18, color=SECONDARY_TEXT_COLOR),
                            self._language_selector,
                            toolbar_button(
                                text(MessageKey.BUTTON_OPEN),
                                flet.Icons.FOLDER_OPEN,
                                self._open_design_case_in_the_background,
                            ),
                            toolbar_button(
                                text(MessageKey.BUTTON_SAVE),
                                flet.Icons.SAVE_OUTLINED,
                                self._save_design_case_in_the_background,
                            ),
                        ],
                        spacing=COLUMN_GAP + 4,
                        vertical_alignment=flet.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=PANEL_BACKGROUND_COLOR,
                    padding=flet.Padding.symmetric(horizontal=PAGE_PADDING, vertical=10),
                ),
                flet.Container(
                    content=flet.Row(
                        controls=[self._inputs_tab, self._results_tab],
                        spacing=0,
                    ),
                    bgcolor=PANEL_BACKGROUND_COLOR,
                    padding=flet.Padding.only(left=PAGE_PADDING - 8),
                    border=flet.Border.only(
                        top=flet.BorderSide(BORDER_WIDTH, PANEL_BORDER_COLOR),
                        bottom=flet.BorderSide(BORDER_WIDTH, PANEL_BORDER_COLOR),
                    ),
                ),
                self._body,
                flet.Container(
                    content=flet.Row(
                        controls=[
                            self._status_icon,
                            self._status_text,
                            self._back_button,
                            self._calculate_button,
                        ],
                        spacing=COLUMN_GAP + 4,
                        vertical_alignment=flet.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=PANEL_BACKGROUND_COLOR,
                    padding=flet.Padding.symmetric(horizontal=PAGE_PADDING, vertical=10),
                    border=flet.Border.only(top=flet.BorderSide(BORDER_WIDTH, PANEL_BORDER_COLOR)),
                ),
            ],
            spacing=0,
            expand=True,
        )

    def _fit_content_width(self) -> None:
        width = content_width_for(self._page.width)
        self._inputs_content.width = width
        self._results_content.width = width

    def _show_inputs_page(self) -> None:
        self._showing_results = False
        self._body.content = self._inputs_page
        self._back_button.visible = False
        self._style_tabs()

    def _show_results_page(self) -> None:
        self._showing_results = True
        self._body.content = self._results_page
        self._back_button.visible = True
        self._style_tabs()

    def _style_tabs(self) -> None:
        for tab, label, active in (
            (self._inputs_tab, self._inputs_tab_label, not self._showing_results),
            (self._results_tab, self._results_tab_label, self._showing_results),
        ):
            label.color = ACCENT_COLOR if active else SECONDARY_TEXT_COLOR
            label.weight = flet.FontWeight.W_700 if active else flet.FontWeight.W_500
            tab.border = flet.Border.only(
                bottom=flet.BorderSide(
                    ACTIVE_TAB_UNDERLINE_WIDTH,
                    ACCENT_COLOR if active else PANEL_BACKGROUND_COLOR,
                )
            )

    def _handle_language_selected(self) -> None:
        chosen = Language(self._language_selector.selected[0])
        if chosen is self._translator.language:
            return
        self.rebuild_in_language(chosen)

    def rebuild_in_language(self, language: Language) -> None:
        remembered = self._form.remembered_entries()
        self._translator.switch_to(language)
        if self._design_case_name_is_the_untitled_placeholder():
            self._design_case_name = self._translator.text(MessageKey.UNTITLED_DESIGN_CASE)
        self._assemble_widgets()
        self._form.restore_entries(remembered)
        self._page.title = self._translator.text(MessageKey.APPLICATION_TITLE)
        self._page.clean()
        self._page.add(self._layout())
        if self._last_evaluation is not None:
            self._show_evaluation(self._last_evaluation)
            self._set_status(
                self._translator.text(
                    MessageKey.STATUS_EVALUATED, iteration_number=len(self._history)
                ),
                StatusTone.SUCCESS,
            )
        self._after_layout()
        self._refresh_readiness()
        self._page.update()

    def _design_case_name_is_the_untitled_placeholder(self) -> bool:
        return any(
            self._design_case_name == Translator(language).text(MessageKey.UNTITLED_DESIGN_CASE)
            for language in SELECTABLE_LANGUAGES
        )

    def _set_status(self, message: str, tone: StatusTone) -> None:
        self._status_tone = tone
        self._status_text.value = message
        self._status_icon.icon = tone.icon
        self._status_icon.color = tone.color

    def _handle_input_change(self) -> None:
        self._results_are_stale = self._last_evaluation is not None
        self._refresh_schematic()
        self._refresh_readiness()

    def _refresh_readiness(self) -> None:
        invalid_labels = self._form.invalid_field_labels()
        self._calculate_button.disabled = bool(invalid_labels)
        if invalid_labels:
            self._set_status(
                self._translator.text(
                    MessageKey.STATUS_STILL_TO_FIX, labels=", ".join(invalid_labels)
                ),
                StatusTone.FAILURE,
            )
        elif self._results_are_stale:
            self._set_status(
                self._translator.text(MessageKey.STATUS_INPUTS_CHANGED), StatusTone.ATTENTION
            )
        elif self._last_evaluation is None:
            self._set_status(
                self._translator.text(MessageKey.STATUS_READY_TO_CALCULATE),
                StatusTone.INFORMATION,
            )

    def _refresh_schematic(self) -> None:
        hot_water_outlet_celsius = (
            None
            if self._last_evaluation is None or self._results_are_stale
            else self._last_evaluation.thermal_duty.shell_side_outlet_temperature_celsius
        )
        self._schematic.show(
            self._form.entered_stream_temperatures(hot_water_outlet_celsius),
            self._form.tube_side_pass_count,
        )
        self._form.show_computed_hot_water_outlet(hot_water_outlet_celsius)

    def _calculate(self) -> None:
        self._form.refresh_all_validation_messages()
        if self._form.invalid_field_labels():
            self._refresh_readiness()
            self._show_inputs_page()
            return

        try:
            design_case = self._form.build_design_case(self._design_case_name)
            evaluation = evaluate_design_case(self._property_source, design_case)
        except DesignError as design_error:
            self._report_design_error(design_error)
            return

        self._history.record(evaluation)
        self._last_evaluation = evaluation
        self._results_are_stale = False
        self._show_evaluation(evaluation)
        self._set_status(
            self._translator.text(MessageKey.STATUS_EVALUATED, iteration_number=len(self._history)),
            StatusTone.SUCCESS,
        )
        self._show_results_page()

    def _show_evaluation(self, evaluation: DesignEvaluation) -> None:
        self._results.show(evaluation, self._history)
        self._form.show_reference_values(evaluation)
        self._refresh_schematic()

    def _report_design_error(self, design_error: DesignError) -> None:
        message = design_error.text_in_language(self._translator.language)
        self._last_evaluation = None
        self._results_are_stale = False
        self._results.show_nothing(message)
        self._form.show_reference_values(None)
        self._refresh_schematic()
        self._set_status(message, StatusTone.FAILURE)
        self._show_inputs_page()

    def _use_suggested_geometry(self) -> None:
        if self._last_evaluation is None:
            return
        self._form.use_suggested_geometry(self._last_evaluation)
        self._calculate()

    def _use_computed_coefficients(self) -> None:
        if self._last_evaluation is None:
            return
        self._form.use_computed_coefficients(self._last_evaluation)
        self._calculate()

    def _export_history_in_the_background(self) -> None:
        self._page.run_task(self._export_history)

    def _open_design_case_in_the_background(self) -> None:
        self._page.run_task(self._open_design_case)

    def _save_design_case_in_the_background(self) -> None:
        self._page.run_task(self._save_design_case)

    async def _export_history(self) -> None:
        chosen_path = await self._file_picker.save_file(
            dialog_title=self._translator.text(MessageKey.DIALOG_EXPORT_ITERATION_HISTORY),
            file_name=ITERATION_HISTORY_FILE_NAME,
            file_type=flet.FilePickerFileType.CUSTOM,
            allowed_extensions=[ITERATION_HISTORY_FILE_EXTENSION],
            src_bytes=self._history.as_csv_text().encode(TEXT_FILE_ENCODING),
        )
        if self._page.web:
            self._announce(
                self._translator.text(
                    MessageKey.STATUS_ITERATION_HISTORY_DOWNLOADED,
                    file_name=ITERATION_HISTORY_FILE_NAME,
                )
            )
            return
        if chosen_path is None:
            return
        self._announce(
            self._translator.text(MessageKey.STATUS_ITERATION_HISTORY_WRITTEN, path=chosen_path)
        )

    async def _save_design_case(self) -> None:
        try:
            design_case = self._form.build_design_case(self._design_case_name)
        except DesignError as design_error:
            self._report_design_error(design_error)
            self._page.update()
            return

        chosen_path = await self._file_picker.save_file(
            dialog_title=self._translator.text(MessageKey.DIALOG_SAVE_DESIGN_CASE),
            file_name=DESIGN_CASE_FILE_NAME,
            file_type=flet.FilePickerFileType.CUSTOM,
            allowed_extensions=[DESIGN_CASE_FILE_EXTENSION],
            src_bytes=design_case_as_toml_text(design_case).encode(TEXT_FILE_ENCODING),
        )
        if self._page.web:
            self._announce(
                self._translator.text(
                    MessageKey.STATUS_DESIGN_CASE_DOWNLOADED, file_name=DESIGN_CASE_FILE_NAME
                )
            )
            return
        if chosen_path is None:
            return
        self._design_case_name = Path(chosen_path).stem
        self._design_case_name_text.value = self._design_case_name
        self._announce(self._translator.text(MessageKey.STATUS_DESIGN_CASE_SAVED, path=chosen_path))

    async def _open_design_case(self) -> None:
        chosen_files = await self._file_picker.pick_files(
            dialog_title=self._translator.text(MessageKey.DIALOG_OPEN_DESIGN_CASE),
            file_type=flet.FilePickerFileType.CUSTOM,
            allowed_extensions=[DESIGN_CASE_FILE_EXTENSION],
            allow_multiple=False,
            with_data=True,
        )
        if not chosen_files:
            return
        chosen_file = chosen_files[0]
        try:
            raw_bytes = (
                chosen_file.bytes
                if chosen_file.bytes is not None
                else Path(str(chosen_file.path)).read_bytes()
            )
            design_case = design_case_from_mapping(
                tomllib.loads(raw_bytes.decode(TEXT_FILE_ENCODING)),
                default_name=Path(chosen_file.name).stem,
            )
        except (
            DesignError,
            tomllib.TOMLDecodeError,
            OSError,
            UnicodeDecodeError,
        ) as failure:
            self._set_status(
                self._translator.text(
                    MessageKey.STATUS_COULD_NOT_OPEN_DESIGN_CASE,
                    name=chosen_file.name,
                    reason=failure,
                ),
                StatusTone.FAILURE,
            )
            self._page.update()
            return

        self._form.load_design_case(design_case)
        self._design_case_name = design_case.name
        self._design_case_name_text.value = design_case.name
        self._history.clear()
        self._last_evaluation = None
        self._results_are_stale = False
        self._calculate()
        self._page.update()

    def _announce(self, message: str) -> None:
        self._set_status(message, StatusTone.SUCCESS)
        self._page.update()


def packaged_host_provides_the_desktop_client() -> bool:
    return os.environ.get("FLET_PLATFORM") is not None


def require_the_client_package(client_package: str) -> None:
    if find_spec(client_package) is not None:
        return
    install_extra = INSTALL_EXTRA_FOR_CLIENT_PACKAGE[client_package]
    raise GraphicalInterfaceUnavailableError(
        MessageKey.INTERFACE_CLIENT_PACKAGE_MISSING,
        client_package=client_package,
        install_extra=install_extra,
    )


def start_graphical_interface(
    serve_over_http: bool = False,
    host: str = "127.0.0.1",
    port: int = 8550,
    language: Language = DEFAULT_LANGUAGE,
) -> None:
    def main(page: flet.Page) -> None:
        DesignerApplication(page, language).build()

    if serve_over_http:
        require_the_client_package(WEB_SERVER_CLIENT_PACKAGE)
        flet.run(
            main,
            view=flet.AppView.WEB_BROWSER,
            host=host,
            port=port,
            no_cdn=True,
        )
        return

    if not packaged_host_provides_the_desktop_client():
        require_the_client_package(DESKTOP_WINDOW_CLIENT_PACKAGE)
    flet.run(main)
