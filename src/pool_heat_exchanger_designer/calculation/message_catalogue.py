from __future__ import annotations

from enum import Enum, auto

from pool_heat_exchanger_designer.calculation.language import Language


class MessageKey(Enum):
    TUBE_INNER_DIAMETER_MUST_BE_POSITIVE = auto()
    TUBE_OUTER_DIAMETER_MUST_EXCEED_INNER_DIAMETER = auto()
    TUBE_LENGTH_MUST_BE_POSITIVE = auto()
    TUBE_COUNT_MUST_BE_AT_LEAST_ONE = auto()
    TUBE_SIDE_PASS_COUNT_MUST_BE_SELECTABLE = auto()
    PITCH_RATIO_MUST_EXCEED_ONE = auto()
    SHELL_INNER_DIAMETER_MUST_BE_POSITIVE = auto()
    BAFFLE_SPACING_MUST_BE_POSITIVE = auto()
    BAFFLE_SPACING_CANNOT_EXCEED_TUBE_LENGTH = auto()
    THERMAL_CONDUCTIVITY_MUST_BE_POSITIVE = auto()
    FOULING_RESISTANCE_CANNOT_BE_NEGATIVE = auto()
    UNKNOWN_TUBE_WALL_MATERIAL = auto()
    ASSUMED_TUBE_SIDE_COEFFICIENT_MUST_BE_POSITIVE = auto()
    ASSUMED_SHELL_SIDE_COEFFICIENT_MUST_BE_POSITIVE = auto()

    TUBE_SIDE_FLOW_AREA_MUST_BE_POSITIVE = auto()
    TUBE_SIDE_REYNOLDS_NUMBER_MUST_BE_POSITIVE = auto()
    TUBE_SIDE_REYNOLDS_NUMBER_TOO_LOW_FOR_PETUKHOV = auto()
    SHELL_SIDE_CROSSFLOW_AREA_MUST_BE_POSITIVE = auto()
    SHELL_SIDE_REYNOLDS_NUMBER_MUST_BE_POSITIVE = auto()

    TUBE_SIDE_OUTLET_MUST_EXCEED_INLET = auto()
    SHELL_SIDE_INLET_MUST_EXCEED_TUBE_SIDE_OUTLET = auto()
    TUBE_SIDE_MASS_FLOW_RATE_MUST_BE_POSITIVE = auto()
    SHELL_SIDE_MASS_FLOW_RATE_MUST_BE_POSITIVE = auto()
    SHELL_SIDE_OUTLET_TEMPERATURE_DID_NOT_CONVERGE = auto()
    TERMINAL_TEMPERATURE_DIFFERENCES_MUST_BE_POSITIVE = auto()
    CORRECTION_FACTOR_MUST_LIE_IN_THE_UNIT_INTERVAL = auto()

    PROPERTY_TABLE_MISSING_COLUMNS = auto()
    PROPERTY_TABLE_UNEXPECTED_COLUMNS = auto()
    PROPERTY_TABLE_CONTAINS_EMPTY_CELLS = auto()
    PROPERTY_TABLE_DUPLICATE_TEMPERATURE = auto()
    PROPERTY_TABLE_ROW_IS_MALFORMED = auto()
    PROPERTY_TABLE_CELL_IS_NOT_A_NUMBER = auto()
    TEMPERATURE_OUTSIDE_TABULATED_RANGE = auto()

    DESIGN_CASE_MISSING_SECTIONS = auto()
    DESIGN_CASE_SECTION_MUST_BE_A_TABLE = auto()
    DESIGN_CASE_MISSING_KEY = auto()
    DESIGN_CASE_VALUE_MUST_BE_A_NUMBER = auto()
    DESIGN_CASE_VALUE_MUST_BE_TEXT = auto()
    DESIGN_CASE_FILE_NOT_FOUND = auto()
    DESIGN_CASE_FILE_IS_NOT_VALID_TOML = auto()
    UNKNOWN_PITCH_LAYOUT = auto()
    RESULT_FILE_NOT_FOUND = auto()
    RESULT_FILE_IS_NOT_VALID_JSON = auto()

    INTERFACE_CLIENT_PACKAGE_MISSING = auto()
    FIELD_IS_NOT_A_USABLE_NUMBER = auto()

    APPLICATION_TITLE = auto()
    UNTITLED_DESIGN_CASE = auto()
    LANGUAGE_SELECTOR_LABEL = auto()
    BUTTON_OPEN = auto()
    BUTTON_SAVE = auto()
    BUTTON_CALCULATE = auto()
    BUTTON_EXPORT_ITERATION_HISTORY = auto()

    FIELD_TUBE_SIDE_INLET_TEMPERATURE = auto()
    FIELD_TUBE_SIDE_OUTLET_TEMPERATURE = auto()
    FIELD_SHELL_SIDE_INLET_TEMPERATURE = auto()
    FIELD_TUBE_SIDE_MASS_FLOW_RATE = auto()
    FIELD_SHELL_SIDE_MASS_FLOW_RATE = auto()
    FIELD_TUBE_OUTER_DIAMETER = auto()
    FIELD_TUBE_INNER_DIAMETER = auto()
    FIELD_TUBE_LENGTH = auto()
    FIELD_PITCH_RATIO = auto()
    FIELD_SHELL_INNER_DIAMETER = auto()
    FIELD_TUBE_COUNT = auto()
    FIELD_BAFFLE_SPACING = auto()
    FIELD_ASSUMED_TUBE_SIDE_COEFFICIENT = auto()
    FIELD_ASSUMED_SHELL_SIDE_COEFFICIENT = auto()
    FIELD_CORRECTION_FACTOR = auto()
    FIELD_PITCH_LAYOUT = auto()
    FIELD_TUBE_WALL_MATERIAL = auto()
    FIELD_TUBE_SIDE_PASS_COUNT = auto()

    OPTION_SQUARE_PITCH = auto()
    OPTION_TRIANGULAR_PITCH = auto()
    OPTION_ONE_TUBE_SIDE_PASS = auto()
    OPTION_TWO_TUBE_SIDE_PASSES = auto()
    OPTION_TITANIUM_ALLOY = auto()
    OPTION_STAINLESS_STEEL = auto()

    COLUMN_SUGGESTED = auto()
    COLUMN_ENTERED = auto()
    COLUMN_ASSUMED = auto()
    COLUMN_COMPUTED = auto()
    COLUMN_DIFFERENCE = auto()
    COLUMN_ITERATION_NUMBER = auto()
    COLUMN_ASSUMED_TUBE_SIDE = auto()
    COLUMN_COMPUTED_TUBE_SIDE = auto()
    COLUMN_ASSUMED_SHELL_SIDE = auto()
    COLUMN_COMPUTED_SHELL_SIDE = auto()
    COLUMN_LARGEST_GAP = auto()

    HEADING_THERMAL_DUTY = auto()
    HEADING_PRELIMINARY_SIZING = auto()
    HEADING_RATING = auto()
    HEADING_STANDARDS_AND_ENVELOPE = auto()
    HEADING_COEFFICIENT_CONVERGENCE = auto()

    RESULT_HEAT_DUTY = auto()
    RESULT_SHELL_SIDE_OUTLET_TEMPERATURE = auto()
    RESULT_CORRECTED_LOG_MEAN_TEMPERATURE_DIFFERENCE = auto()
    RESULT_REQUIRED_FOULED_AREA = auto()
    RESULT_SUGGESTED_SHELL_INNER_DIAMETER = auto()
    RESULT_SUGGESTED_TUBE_COUNT = auto()
    RESULT_SUGGESTED_BAFFLE_SPACING = auto()
    RESULT_OVER_SURFACE_DESIGN_RATIO = auto()
    RESULT_TUBE_SIDE_COEFFICIENT = auto()
    RESULT_SHELL_SIDE_COEFFICIENT = auto()
    RESULT_TUBE_SIDE_REYNOLDS_NUMBER = auto()
    RESULT_SHELL_SIDE_REYNOLDS_NUMBER = auto()
    RESULT_OVERALL_COEFFICIENT_FOULED = auto()
    RESULT_TUBE_SIDE_PRESSURE_DROP = auto()
    RESULT_SHELL_SIDE_PRESSURE_DROP = auto()
    RESULT_TUBE_SIDE_COEFFICIENT_ROW = auto()
    RESULT_SHELL_SIDE_COEFFICIENT_ROW = auto()

    CONSTRAINT_SHELL_SLENDERNESS = auto()
    CONSTRAINT_PITCH_RATIO = auto()
    CONSTRAINT_POOL_WATER_TEMPERATURE = auto()
    CONSTRAINT_SINGLE_PHASE = auto()
    CONSTRAINT_TUBE_SIDE_PRESSURE_DROP = auto()
    CONSTRAINT_SHELL_SIDE_PRESSURE_DROP = auto()
    STANDARD_TEMA = auto()
    STANDARD_FINA = auto()
    STANDARD_DESIGN_ENVELOPE = auto()
    ALLOWED_RANGE_BETWEEN = auto()
    ALLOWED_RANGE_AT_MOST = auto()
    ALLOWED_RANGE_AT_LEAST = auto()
    CHECK_SATISFIED = auto()
    CHECK_FAILED = auto()

    STATUS_READY_TO_CALCULATE = auto()
    STATUS_STILL_TO_FIX = auto()
    STATUS_EVALUATED = auto()
    STATUS_NOT_CONVERGED = auto()
    STATUS_DESIGN_CASE_SAVED = auto()
    STATUS_ITERATION_HISTORY_WRITTEN = auto()
    STATUS_COULD_NOT_OPEN_DESIGN_CASE = auto()
    DIALOG_OPEN_DESIGN_CASE = auto()
    DIALOG_SAVE_DESIGN_CASE = auto()
    DIALOG_EXPORT_ITERATION_HISTORY = auto()

    FIELD_RANGE_REJECTION_WITH_UNIT = auto()
    FIELD_RANGE_REJECTION_WITHOUT_UNIT = auto()

    REPORT_DESIGN_CASE_NAME = auto()
    REPORT_ALLOWED = auto()
    REPORT_CONVERGED = auto()
    COMMAND_DESCRIPTION = auto()
    COMMAND_EVALUATE_HELP = auto()
    COMMAND_COMPARE_HELP = auto()
    COMMAND_GUI_HELP = auto()
    COMMAND_JSON_OUTPUT_HELP = auto()
    COMMAND_QUIET_HELP = auto()
    COMMAND_FAIL_ON_CONSTRAINT_HELP = auto()
    COMMAND_WEB_HELP = auto()
    COMMAND_LANGUAGE_HELP = auto()
    COMMAND_VERSION_HELP = auto()
    COMMAND_RESULTS_AGREE = auto()
    COMMAND_COMPARISON_QUANTITY = auto()
    COMMAND_COMPARISON_FIRST = auto()
    COMMAND_COMPARISON_SECOND = auto()
    COMMAND_COMPARISON_RELATIVE = auto()
    COMMAND_INTERFACE_NEEDS_FLET = auto()

    TAB_INPUTS = auto()
    TAB_RESULTS = auto()
    HINT_INPUTS = auto()
    GROUP_FLOW_ARRANGEMENT = auto()
    GROUP_POOL_WATER = auto()
    GROUP_HOT_WATER = auto()
    GROUP_TUBES = auto()
    GROUP_SHELL_AND_BAFFLES = auto()
    GROUP_DESIGN_ASSUMPTIONS = auto()
    BUTTON_USE_COMPUTED_COEFFICIENTS = auto()
    BUTTON_USE_SUGGESTED_GEOMETRY = auto()
    BUTTON_BACK_TO_INPUTS = auto()
    STATUS_NO_RESULTS_YET = auto()
    STATUS_DESIGN_CASE_DOWNLOADED = auto()
    STATUS_ITERATION_HISTORY_DOWNLOADED = auto()
    VERDICT_CONSISTENT = auto()
    VERDICT_NOT_CONSISTENT_YET = auto()
    VERDICT_EXPLANATION = auto()
    CHECK_LINE_COEFFICIENTS_AGREE = auto()
    CHECK_LINE_COEFFICIENTS_DIFFER = auto()
    CHECK_LINE_GEOMETRY_MATCHES = auto()
    CHECK_LINE_GEOMETRY_DIFFERS = auto()
    REPORT_DIFFERS_BY = auto()
    HEADING_PRESSURE_DROP = auto()
    HEADING_ITERATION_HISTORY = auto()
    HEADING_NOTES = auto()
    NOTE_TUBE_SIDE_CORRELATION_OUTSIDE_RANGE = auto()
    NOTE_SHELL_SIDE_CORRELATION_OUTSIDE_RANGE = auto()
    NOTE_NONE = auto()
    COLUMN_CHECK = auto()
    COLUMN_VALUE = auto()
    COLUMN_ALLOWED = auto()
    COLUMN_SOURCE = auto()
    COLUMN_STATUS = auto()
    SCHEMATIC_POOL_WATER_IN = auto()
    SCHEMATIC_POOL_WATER_OUT = auto()
    SCHEMATIC_HOT_WATER_IN = auto()
    SCHEMATIC_HOT_WATER_OUT = auto()
    SCHEMATIC_SHELL = auto()
    SCHEMATIC_BAFFLES = auto()
    SCHEMATIC_RETURN_HEAD = auto()
    FIELD_IN_GROUP = auto()
    STATUS_INPUTS_CHANGED = auto()
    COLUMN_GEOMETRY_GAP = auto()
    FIELD_SHELL_SIDE_OUTLET_TEMPERATURE_COMPUTED = auto()


UNIT_SYMBOL_DEGREE_CELSIUS = "°C"
UNIT_SYMBOL_KELVIN = "K"
UNIT_SYMBOL_KILOGRAMS_PER_SECOND = "kg/s"
UNIT_SYMBOL_METER = "m"
UNIT_SYMBOL_MILLIMETER = "mm"
UNIT_SYMBOL_SQUARE_METER = "m²"
UNIT_SYMBOL_KILOWATT = "kW"
UNIT_SYMBOL_KILOPASCAL = "kPa"
UNIT_SYMBOL_BAR = "bar"
UNIT_SYMBOL_WATTS_PER_SQUARE_METER_KELVIN = "W/m²K"
UNIT_SYMBOL_PERCENT = "%"
UNIT_SYMBOL_DIMENSIONLESS = ""
SYMBOL_NOT_AVAILABLE = "—"


MESSAGE_CATALOGUE: dict[MessageKey, dict[Language, str]] = {
    MessageKey.TUBE_INNER_DIAMETER_MUST_BE_POSITIVE: {
        Language.ENGLISH: "Tube inner diameter must be positive",
        Language.TURKISH: "Boru iç çapı pozitif olmalı",
    },
    MessageKey.TUBE_OUTER_DIAMETER_MUST_EXCEED_INNER_DIAMETER: {
        Language.ENGLISH: "Tube outer diameter must exceed tube inner diameter",
        Language.TURKISH: "Boru dış çapı boru iç çapından büyük olmalı",
    },
    MessageKey.TUBE_LENGTH_MUST_BE_POSITIVE: {
        Language.ENGLISH: "Tube length must be positive",
        Language.TURKISH: "Boru boyu pozitif olmalı",
    },
    MessageKey.TUBE_COUNT_MUST_BE_AT_LEAST_ONE: {
        Language.ENGLISH: "Tube count must be at least one",
        Language.TURKISH: "Boru sayısı en az bir olmalı",
    },
    MessageKey.TUBE_SIDE_PASS_COUNT_MUST_BE_SELECTABLE: {
        Language.ENGLISH: "Tube side pass count must be one of {selectable}",
        Language.TURKISH: "Boru tarafı geçiş sayısı şunlardan biri olmalı: {selectable}",
    },
    MessageKey.PITCH_RATIO_MUST_EXCEED_ONE: {
        Language.ENGLISH: "Pitch ratio must exceed one, otherwise adjacent tubes overlap",
        Language.TURKISH: "Adım oranı birden büyük olmalı, aksi halde komşu borular çakışır",
    },
    MessageKey.SHELL_INNER_DIAMETER_MUST_BE_POSITIVE: {
        Language.ENGLISH: "Shell inner diameter must be positive",
        Language.TURKISH: "Gövde iç çapı pozitif olmalı",
    },
    MessageKey.BAFFLE_SPACING_MUST_BE_POSITIVE: {
        Language.ENGLISH: "Baffle spacing must be positive",
        Language.TURKISH: "Bafil aralığı pozitif olmalı",
    },
    MessageKey.BAFFLE_SPACING_CANNOT_EXCEED_TUBE_LENGTH: {
        Language.ENGLISH: "Baffle spacing cannot exceed the tube length",
        Language.TURKISH: "Bafil aralığı boru boyunu aşamaz",
    },
    MessageKey.THERMAL_CONDUCTIVITY_MUST_BE_POSITIVE: {
        Language.ENGLISH: "{material_name} thermal conductivity must be positive",
        Language.TURKISH: "{material_name} ısı iletim katsayısı pozitif olmalı",
    },
    MessageKey.FOULING_RESISTANCE_CANNOT_BE_NEGATIVE: {
        Language.ENGLISH: "{material_name} fouling resistance cannot be negative",
        Language.TURKISH: "{material_name} kirlenme direnci negatif olamaz",
    },
    MessageKey.UNKNOWN_TUBE_WALL_MATERIAL: {
        Language.ENGLISH: "Unknown tube wall material {name}; choose one of {selectable}",
        Language.TURKISH: (
            "Bilinmeyen boru cidar malzemesi {name}; şunlardan birini seçin: {selectable}"
        ),
    },
    MessageKey.ASSUMED_TUBE_SIDE_COEFFICIENT_MUST_BE_POSITIVE: {
        Language.ENGLISH: "Assumed tube side heat transfer coefficient must be positive",
        Language.TURKISH: "Varsayılan boru tarafı ısı taşınım katsayısı pozitif olmalı",
    },
    MessageKey.ASSUMED_SHELL_SIDE_COEFFICIENT_MUST_BE_POSITIVE: {
        Language.ENGLISH: "Assumed shell side heat transfer coefficient must be positive",
        Language.TURKISH: "Varsayılan gövde tarafı ısı taşınım katsayısı pozitif olmalı",
    },
    MessageKey.TUBE_SIDE_FLOW_AREA_MUST_BE_POSITIVE: {
        Language.ENGLISH: "Tube side flow area must be positive",
        Language.TURKISH: "Boru tarafı akış alanı pozitif olmalı",
    },
    MessageKey.TUBE_SIDE_REYNOLDS_NUMBER_MUST_BE_POSITIVE: {
        Language.ENGLISH: "Tube side Reynolds number must be positive",
        Language.TURKISH: "Boru tarafı Reynolds sayısı pozitif olmalı",
    },
    MessageKey.TUBE_SIDE_REYNOLDS_NUMBER_TOO_LOW_FOR_PETUKHOV: {
        Language.ENGLISH: "Tube side Reynolds number is too low for the Petukhov friction factor",
        Language.TURKISH: (
            "Boru tarafı Reynolds sayısı Petukhov sürtünme katsayısı için fazla düşük"
        ),
    },
    MessageKey.SHELL_SIDE_CROSSFLOW_AREA_MUST_BE_POSITIVE: {
        Language.ENGLISH: "Shell side crossflow area must be positive",
        Language.TURKISH: "Gövde tarafı çapraz akış alanı pozitif olmalı",
    },
    MessageKey.SHELL_SIDE_REYNOLDS_NUMBER_MUST_BE_POSITIVE: {
        Language.ENGLISH: "Shell side Reynolds number must be positive",
        Language.TURKISH: "Gövde tarafı Reynolds sayısı pozitif olmalı",
    },
    MessageKey.TUBE_SIDE_OUTLET_MUST_EXCEED_INLET: {
        Language.ENGLISH: (
            "Tube side outlet temperature must exceed tube side inlet temperature, "
            "otherwise the pool water is not being heated"
        ),
        Language.TURKISH: (
            "Boru tarafı çıkış sıcaklığı giriş sıcaklığından büyük olmalı, aksi halde havuz "
            "suyu ısıtılmıyor"
        ),
    },
    MessageKey.SHELL_SIDE_INLET_MUST_EXCEED_TUBE_SIDE_OUTLET: {
        Language.ENGLISH: (
            "Shell side inlet temperature must exceed tube side outlet temperature, "
            "otherwise heat cannot flow in the required direction"
        ),
        Language.TURKISH: (
            "Gövde tarafı giriş sıcaklığı boru tarafı çıkış sıcaklığından büyük olmalı, "
            "aksi halde ısı gereken yönde akamaz"
        ),
    },
    MessageKey.TUBE_SIDE_MASS_FLOW_RATE_MUST_BE_POSITIVE: {
        Language.ENGLISH: "Tube side mass flow rate must be positive",
        Language.TURKISH: "Boru tarafı kütlesel debisi pozitif olmalı",
    },
    MessageKey.SHELL_SIDE_MASS_FLOW_RATE_MUST_BE_POSITIVE: {
        Language.ENGLISH: "Shell side mass flow rate must be positive",
        Language.TURKISH: "Gövde tarafı kütlesel debisi pozitif olmalı",
    },
    MessageKey.SHELL_SIDE_OUTLET_TEMPERATURE_DID_NOT_CONVERGE: {
        Language.ENGLISH: (
            "Shell side outlet temperature did not converge; check the mass flow rates and "
            "the requested tube side temperature rise"
        ),
        Language.TURKISH: (
            "Gövde tarafı çıkış sıcaklığı yakınsamadı; kütlesel debileri ve istenen boru "
            "tarafı sıcaklık artışını gözden geçirin"
        ),
    },
    MessageKey.TERMINAL_TEMPERATURE_DIFFERENCES_MUST_BE_POSITIVE: {
        Language.ENGLISH: (
            "Both terminal temperature differences must be positive; the requested "
            "temperatures would require heat to flow from cold to hot"
        ),
        Language.TURKISH: (
            "Her iki uç sıcaklık farkı da pozitif olmalı; istenen sıcaklıklar ısının "
            "soğuktan sıcağa akmasını gerektirir"
        ),
    },
    MessageKey.CORRECTION_FACTOR_MUST_LIE_IN_THE_UNIT_INTERVAL: {
        Language.ENGLISH: "Log mean temperature difference correction factor must lie in (0, 1]",
        Language.TURKISH: (
            "Logaritmik ortalama sıcaklık farkı düzeltme çarpanı (0, 1] aralığında olmalı"
        ),
    },
    MessageKey.PROPERTY_TABLE_MISSING_COLUMNS: {
        Language.ENGLISH: "Property table is missing the columns {columns}",
        Language.TURKISH: "Özellik tablosunda şu kolonlar eksik: {columns}",
    },
    MessageKey.PROPERTY_TABLE_UNEXPECTED_COLUMNS: {
        Language.ENGLISH: "Property table has the unexpected columns {columns}",
        Language.TURKISH: "Özellik tablosunda beklenmeyen kolonlar var: {columns}",
    },
    MessageKey.PROPERTY_TABLE_CONTAINS_EMPTY_CELLS: {
        Language.ENGLISH: "Property table contains empty cells",
        Language.TURKISH: "Özellik tablosunda boş hücreler var",
    },
    MessageKey.PROPERTY_TABLE_DUPLICATE_TEMPERATURE: {
        Language.ENGLISH: "Property table lists the same temperature more than once",
        Language.TURKISH: "Özellik tablosu aynı sıcaklığı birden fazla kez listeliyor",
    },
    MessageKey.PROPERTY_TABLE_ROW_IS_MALFORMED: {
        Language.ENGLISH: "Property table row {row_number} does not have one cell per column",
        Language.TURKISH: "Özellik tablosunun {row_number}. satırında her kolon için bir hücre yok",
    },
    MessageKey.PROPERTY_TABLE_CELL_IS_NOT_A_NUMBER: {
        Language.ENGLISH: "Property table cell {value} is not a number",
        Language.TURKISH: "Özellik tablosundaki {value} hücresi bir sayı değil",
    },
    MessageKey.TEMPERATURE_OUTSIDE_TABULATED_RANGE: {
        Language.ENGLISH: "{temperature} °C is outside the tabulated range {lowest}–{highest} °C",
        Language.TURKISH: "{temperature} °C tablolanmış {lowest}–{highest} °C aralığının dışında",
    },
    MessageKey.DESIGN_CASE_MISSING_SECTIONS: {
        Language.ENGLISH: "Design case is missing the sections {sections}",
        Language.TURKISH: "Tasarım dosyasında şu bölümler eksik: {sections}",
    },
    MessageKey.DESIGN_CASE_SECTION_MUST_BE_A_TABLE: {
        Language.ENGLISH: "[{section}] must be a table",
        Language.TURKISH: "[{section}] bir tablo olmalı",
    },
    MessageKey.DESIGN_CASE_MISSING_KEY: {
        Language.ENGLISH: "[{section}] is missing {key}",
        Language.TURKISH: "[{section}] içinde {key} eksik",
    },
    MessageKey.DESIGN_CASE_VALUE_MUST_BE_A_NUMBER: {
        Language.ENGLISH: "[{section}] {key} must be a number, found {value}",
        Language.TURKISH: "[{section}] {key} bir sayı olmalı, bulunan {value}",
    },
    MessageKey.DESIGN_CASE_VALUE_MUST_BE_TEXT: {
        Language.ENGLISH: "[{section}] {key} must be text, found {value}",
        Language.TURKISH: "[{section}] {key} metin olmalı, bulunan {value}",
    },
    MessageKey.DESIGN_CASE_FILE_NOT_FOUND: {
        Language.ENGLISH: "Design case file not found: {path}",
        Language.TURKISH: "Tasarım dosyası bulunamadı: {path}",
    },
    MessageKey.DESIGN_CASE_FILE_IS_NOT_VALID_TOML: {
        Language.ENGLISH: "{path} is not valid TOML: {reason}",
        Language.TURKISH: "{path} geçerli TOML değil: {reason}",
    },
    MessageKey.UNKNOWN_PITCH_LAYOUT: {
        Language.ENGLISH: "Unknown pitch layout {name}; choose one of {selectable}",
        Language.TURKISH: "Bilinmeyen adım düzeni {name}; şunlardan birini seçin: {selectable}",
    },
    MessageKey.RESULT_FILE_NOT_FOUND: {
        Language.ENGLISH: "Result file not found: {path}",
        Language.TURKISH: "Sonuç dosyası bulunamadı: {path}",
    },
    MessageKey.RESULT_FILE_IS_NOT_VALID_JSON: {
        Language.ENGLISH: "{path} is not valid JSON: {reason}",
        Language.TURKISH: "{path} geçerli JSON değil: {reason}",
    },
    MessageKey.INTERFACE_CLIENT_PACKAGE_MISSING: {
        Language.ENGLISH: (
            "{client_package} is not installed, and Flet would try to install it over the "
            "network at startup. From the project folder, install it ahead of time with\n"
            '    pip install ".[{install_extra}]"'
        ),
        Language.TURKISH: (
            "{client_package} kurulu değil ve Flet açılışta onu ağ üzerinden kurmaya "
            "çalışır. Proje klasöründe önceden şu komutla kurun\n"
            '    pip install ".[{install_extra}]"'
        ),
    },
    MessageKey.FIELD_IS_NOT_A_USABLE_NUMBER: {
        Language.ENGLISH: "{label} is not a usable number",
        Language.TURKISH: "{label} kullanılabilir bir sayı değil",
    },
    MessageKey.APPLICATION_TITLE: {
        Language.ENGLISH: "Pool Heat Exchanger Designer",
        Language.TURKISH: "Havuz Isı Değiştirici Tasarımcısı",
    },
    MessageKey.UNTITLED_DESIGN_CASE: {
        Language.ENGLISH: "Untitled design case",
        Language.TURKISH: "Adsız tasarım",
    },
    MessageKey.LANGUAGE_SELECTOR_LABEL: {
        Language.ENGLISH: "Language",
        Language.TURKISH: "Dil",
    },
    MessageKey.BUTTON_OPEN: {
        Language.ENGLISH: "Open",
        Language.TURKISH: "Aç",
    },
    MessageKey.BUTTON_SAVE: {
        Language.ENGLISH: "Save",
        Language.TURKISH: "Kaydet",
    },
    MessageKey.BUTTON_CALCULATE: {
        Language.ENGLISH: "Calculate",
        Language.TURKISH: "Hesapla",
    },
    MessageKey.BUTTON_EXPORT_ITERATION_HISTORY: {
        Language.ENGLISH: "Export CSV",
        Language.TURKISH: "CSV olarak aktar",
    },
    MessageKey.FIELD_TUBE_SIDE_INLET_TEMPERATURE: {
        Language.ENGLISH: "Inlet temperature",
        Language.TURKISH: "Giriş sıcaklığı",
    },
    MessageKey.FIELD_TUBE_SIDE_OUTLET_TEMPERATURE: {
        Language.ENGLISH: "Outlet temperature",
        Language.TURKISH: "Çıkış sıcaklığı",
    },
    MessageKey.FIELD_SHELL_SIDE_INLET_TEMPERATURE: {
        Language.ENGLISH: "Inlet temperature",
        Language.TURKISH: "Giriş sıcaklığı",
    },
    MessageKey.FIELD_TUBE_SIDE_MASS_FLOW_RATE: {
        Language.ENGLISH: "Mass flow rate",
        Language.TURKISH: "Kütlesel debi",
    },
    MessageKey.FIELD_SHELL_SIDE_MASS_FLOW_RATE: {
        Language.ENGLISH: "Mass flow rate",
        Language.TURKISH: "Kütlesel debi",
    },
    MessageKey.FIELD_TUBE_OUTER_DIAMETER: {
        Language.ENGLISH: "Outer diameter",
        Language.TURKISH: "Dış çap",
    },
    MessageKey.FIELD_TUBE_INNER_DIAMETER: {
        Language.ENGLISH: "Inner diameter",
        Language.TURKISH: "İç çap",
    },
    MessageKey.FIELD_TUBE_LENGTH: {
        Language.ENGLISH: "Length",
        Language.TURKISH: "Boy",
    },
    MessageKey.FIELD_PITCH_RATIO: {
        Language.ENGLISH: "Pitch / outer diameter",
        Language.TURKISH: "Adım / dış çap",
    },
    MessageKey.FIELD_SHELL_INNER_DIAMETER: {
        Language.ENGLISH: "Inner diameter",
        Language.TURKISH: "İç çap",
    },
    MessageKey.FIELD_TUBE_COUNT: {
        Language.ENGLISH: "Tube count",
        Language.TURKISH: "Boru sayısı",
    },
    MessageKey.FIELD_BAFFLE_SPACING: {
        Language.ENGLISH: "Baffle spacing",
        Language.TURKISH: "Bafil aralığı",
    },
    MessageKey.FIELD_ASSUMED_TUBE_SIDE_COEFFICIENT: {
        Language.ENGLISH: "Tube side coefficient",
        Language.TURKISH: "Boru tarafı katsayısı",
    },
    MessageKey.FIELD_ASSUMED_SHELL_SIDE_COEFFICIENT: {
        Language.ENGLISH: "Shell side coefficient",
        Language.TURKISH: "Gövde tarafı katsayısı",
    },
    MessageKey.FIELD_CORRECTION_FACTOR: {
        Language.ENGLISH: "LMTD correction factor F",
        Language.TURKISH: "LMTD düzeltme çarpanı F",
    },
    MessageKey.FIELD_PITCH_LAYOUT: {
        Language.ENGLISH: "Pitch layout",
        Language.TURKISH: "Adım düzeni",
    },
    MessageKey.FIELD_TUBE_WALL_MATERIAL: {
        Language.ENGLISH: "Wall material",
        Language.TURKISH: "Cidar malzemesi",
    },
    MessageKey.FIELD_TUBE_SIDE_PASS_COUNT: {
        Language.ENGLISH: "Tube passes",
        Language.TURKISH: "Boru geçiş sayısı",
    },
    MessageKey.OPTION_SQUARE_PITCH: {
        Language.ENGLISH: "Square (90°, 45°)",
        Language.TURKISH: "Kare (90°, 45°)",
    },
    MessageKey.OPTION_TRIANGULAR_PITCH: {
        Language.ENGLISH: "Triangular (30°, 60°)",
        Language.TURKISH: "Üçgen (30°, 60°)",
    },
    MessageKey.OPTION_ONE_TUBE_SIDE_PASS: {
        Language.ENGLISH: "1 pass",
        Language.TURKISH: "1 geçiş",
    },
    MessageKey.OPTION_TWO_TUBE_SIDE_PASSES: {
        Language.ENGLISH: "2 passes",
        Language.TURKISH: "2 geçiş",
    },
    MessageKey.OPTION_TITANIUM_ALLOY: {
        Language.ENGLISH: "Titanium alloy",
        Language.TURKISH: "Titanyum alaşımı",
    },
    MessageKey.OPTION_STAINLESS_STEEL: {
        Language.ENGLISH: "Stainless steel",
        Language.TURKISH: "Paslanmaz çelik",
    },
    MessageKey.COLUMN_SUGGESTED: {
        Language.ENGLISH: "Suggested",
        Language.TURKISH: "Önerilen",
    },
    MessageKey.COLUMN_ENTERED: {
        Language.ENGLISH: "Entered",
        Language.TURKISH: "Girilen",
    },
    MessageKey.COLUMN_ASSUMED: {
        Language.ENGLISH: "Assumed",
        Language.TURKISH: "Varsayılan",
    },
    MessageKey.COLUMN_COMPUTED: {
        Language.ENGLISH: "Computed",
        Language.TURKISH: "Hesaplanan",
    },
    MessageKey.COLUMN_DIFFERENCE: {
        Language.ENGLISH: "Difference",
        Language.TURKISH: "Fark",
    },
    MessageKey.COLUMN_ITERATION_NUMBER: {
        Language.ENGLISH: "#",
        Language.TURKISH: "#",
    },
    MessageKey.COLUMN_ASSUMED_TUBE_SIDE: {
        Language.ENGLISH: "Assumed tube",
        Language.TURKISH: "Varsayılan boru",
    },
    MessageKey.COLUMN_COMPUTED_TUBE_SIDE: {
        Language.ENGLISH: "Computed tube",
        Language.TURKISH: "Hesaplanan boru",
    },
    MessageKey.COLUMN_ASSUMED_SHELL_SIDE: {
        Language.ENGLISH: "Assumed shell",
        Language.TURKISH: "Varsayılan gövde",
    },
    MessageKey.COLUMN_COMPUTED_SHELL_SIDE: {
        Language.ENGLISH: "Computed shell",
        Language.TURKISH: "Hesaplanan gövde",
    },
    MessageKey.COLUMN_LARGEST_GAP: {
        Language.ENGLISH: "Coefficient gap",
        Language.TURKISH: "Katsayı farkı",
    },
    MessageKey.HEADING_THERMAL_DUTY: {
        Language.ENGLISH: "Thermal duty",
        Language.TURKISH: "Isıl yük",
    },
    MessageKey.HEADING_PRELIMINARY_SIZING: {
        Language.ENGLISH: "Sizing from the assumed coefficients",
        Language.TURKISH: "Varsayılan katsayılardan boyutlandırma",
    },
    MessageKey.HEADING_RATING: {
        Language.ENGLISH: "Rating of the entered geometry",
        Language.TURKISH: "Girilen geometrinin değerlendirmesi",
    },
    MessageKey.HEADING_STANDARDS_AND_ENVELOPE: {
        Language.ENGLISH: "Standards and limits",
        Language.TURKISH: "Standartlar ve sınırlar",
    },
    MessageKey.HEADING_COEFFICIENT_CONVERGENCE: {
        Language.ENGLISH: "Design convergence",
        Language.TURKISH: "Tasarım yakınsaması",
    },
    MessageKey.RESULT_HEAT_DUTY: {
        Language.ENGLISH: "Heat duty",
        Language.TURKISH: "Isı yükü",
    },
    MessageKey.RESULT_SHELL_SIDE_OUTLET_TEMPERATURE: {
        Language.ENGLISH: "Hot water outlet temperature",
        Language.TURKISH: "Sıcak su çıkış sıcaklığı",
    },
    MessageKey.RESULT_CORRECTED_LOG_MEAN_TEMPERATURE_DIFFERENCE: {
        Language.ENGLISH: "Corrected log mean temperature difference",
        Language.TURKISH: "Düzeltilmiş logaritmik ortalama sıcaklık farkı",
    },
    MessageKey.RESULT_REQUIRED_FOULED_AREA: {
        Language.ENGLISH: "Required surface, fouled",
        Language.TURKISH: "Gereken yüzey, kirlenmiş",
    },
    MessageKey.RESULT_SUGGESTED_SHELL_INNER_DIAMETER: {
        Language.ENGLISH: "Suggested shell inner diameter",
        Language.TURKISH: "Önerilen gövde iç çapı",
    },
    MessageKey.RESULT_SUGGESTED_TUBE_COUNT: {
        Language.ENGLISH: "Suggested tube count",
        Language.TURKISH: "Önerilen boru sayısı",
    },
    MessageKey.RESULT_SUGGESTED_BAFFLE_SPACING: {
        Language.ENGLISH: "Suggested baffle spacing",
        Language.TURKISH: "Önerilen bafil aralığı",
    },
    MessageKey.RESULT_OVER_SURFACE_DESIGN_RATIO: {
        Language.ENGLISH: "Over surface design ratio",
        Language.TURKISH: "Aşırı yüzey tasarım oranı",
    },
    MessageKey.RESULT_TUBE_SIDE_COEFFICIENT: {
        Language.ENGLISH: "Tube side heat transfer coefficient",
        Language.TURKISH: "Boru tarafı ısı taşınım katsayısı",
    },
    MessageKey.RESULT_SHELL_SIDE_COEFFICIENT: {
        Language.ENGLISH: "Shell side heat transfer coefficient",
        Language.TURKISH: "Gövde tarafı ısı taşınım katsayısı",
    },
    MessageKey.RESULT_TUBE_SIDE_REYNOLDS_NUMBER: {
        Language.ENGLISH: "Tube side Reynolds number",
        Language.TURKISH: "Boru tarafı Reynolds sayısı",
    },
    MessageKey.RESULT_SHELL_SIDE_REYNOLDS_NUMBER: {
        Language.ENGLISH: "Shell side Reynolds number",
        Language.TURKISH: "Gövde tarafı Reynolds sayısı",
    },
    MessageKey.RESULT_OVERALL_COEFFICIENT_FOULED: {
        Language.ENGLISH: "Overall coefficient, fouled",
        Language.TURKISH: "Toplam katsayı, kirlenmiş",
    },
    MessageKey.RESULT_TUBE_SIDE_PRESSURE_DROP: {
        Language.ENGLISH: "Tube side pressure drop",
        Language.TURKISH: "Boru tarafı basınç düşümü",
    },
    MessageKey.RESULT_SHELL_SIDE_PRESSURE_DROP: {
        Language.ENGLISH: "Shell side pressure drop",
        Language.TURKISH: "Gövde tarafı basınç düşümü",
    },
    MessageKey.RESULT_TUBE_SIDE_COEFFICIENT_ROW: {
        Language.ENGLISH: "Tube side coefficient",
        Language.TURKISH: "Boru tarafı katsayısı",
    },
    MessageKey.RESULT_SHELL_SIDE_COEFFICIENT_ROW: {
        Language.ENGLISH: "Shell side coefficient",
        Language.TURKISH: "Gövde tarafı katsayısı",
    },
    MessageKey.CONSTRAINT_SHELL_SLENDERNESS: {
        Language.ENGLISH: "Shell inner diameter / tube length",
        Language.TURKISH: "Gövde iç çapı / boru boyu",
    },
    MessageKey.CONSTRAINT_PITCH_RATIO: {
        Language.ENGLISH: "Pitch / tube outer diameter",
        Language.TURKISH: "Adım / boru dış çapı",
    },
    MessageKey.CONSTRAINT_POOL_WATER_TEMPERATURE: {
        Language.ENGLISH: "Pool water temperature",
        Language.TURKISH: "Havuz suyu sıcaklığı",
    },
    MessageKey.CONSTRAINT_SINGLE_PHASE: {
        Language.ENGLISH: "Highest water temperature, below saturation at {pressure} bar",
        Language.TURKISH: "En yüksek su sıcaklığı, {pressure} bar doyma sıcaklığının altında",
    },
    MessageKey.CONSTRAINT_TUBE_SIDE_PRESSURE_DROP: {
        Language.ENGLISH: "Tube side pressure drop",
        Language.TURKISH: "Boru tarafı basınç düşümü",
    },
    MessageKey.CONSTRAINT_SHELL_SIDE_PRESSURE_DROP: {
        Language.ENGLISH: "Shell side pressure drop",
        Language.TURKISH: "Gövde tarafı basınç düşümü",
    },
    MessageKey.STANDARD_TEMA: {
        Language.ENGLISH: "TEMA",
        Language.TURKISH: "TEMA",
    },
    MessageKey.STANDARD_FINA: {
        Language.ENGLISH: "FINA",
        Language.TURKISH: "FINA",
    },
    MessageKey.STANDARD_DESIGN_ENVELOPE: {
        Language.ENGLISH: "Design envelope",
        Language.TURKISH: "Çalışma zarfı",
    },
    MessageKey.ALLOWED_RANGE_BETWEEN: {
        Language.ENGLISH: "{lowest} – {highest}",
        Language.TURKISH: "{lowest} – {highest}",
    },
    MessageKey.ALLOWED_RANGE_AT_MOST: {
        Language.ENGLISH: "≤ {highest}",
        Language.TURKISH: "≤ {highest}",
    },
    MessageKey.ALLOWED_RANGE_AT_LEAST: {
        Language.ENGLISH: "≥ {lowest}",
        Language.TURKISH: "≥ {lowest}",
    },
    MessageKey.CHECK_SATISFIED: {
        Language.ENGLISH: "OK",
        Language.TURKISH: "Uygun",
    },
    MessageKey.CHECK_FAILED: {
        Language.ENGLISH: "Not met",
        Language.TURKISH: "Sağlanmıyor",
    },
    MessageKey.STATUS_READY_TO_CALCULATE: {
        Language.ENGLISH: "All inputs are valid. Press Calculate.",
        Language.TURKISH: "Tüm girdiler geçerli. Hesapla'ya basın.",
    },
    MessageKey.STATUS_STILL_TO_FIX: {
        Language.ENGLISH: "Fix these inputs first: {labels}",
        Language.TURKISH: "Önce şu girdileri düzeltin: {labels}",
    },
    MessageKey.STATUS_EVALUATED: {
        Language.ENGLISH: "Calculated. Iteration {iteration_number} recorded.",
        Language.TURKISH: "Hesaplandı. {iteration_number}. iterasyon kaydedildi.",
    },
    MessageKey.STATUS_NOT_CONVERGED: {
        Language.ENGLISH: "Not yet, keep iterating",
        Language.TURKISH: "Henüz değil, iterasyona devam edin",
    },
    MessageKey.STATUS_DESIGN_CASE_SAVED: {
        Language.ENGLISH: "Design case saved to {path}",
        Language.TURKISH: "Tasarım {path} dosyasına kaydedildi",
    },
    MessageKey.STATUS_ITERATION_HISTORY_WRITTEN: {
        Language.ENGLISH: "Iteration history written to {path}",
        Language.TURKISH: "İterasyon geçmişi {path} dosyasına yazıldı",
    },
    MessageKey.STATUS_COULD_NOT_OPEN_DESIGN_CASE: {
        Language.ENGLISH: "Could not open {name}: {reason}",
        Language.TURKISH: "{name} açılamadı: {reason}",
    },
    MessageKey.DIALOG_OPEN_DESIGN_CASE: {
        Language.ENGLISH: "Open a design case",
        Language.TURKISH: "Tasarım dosyası aç",
    },
    MessageKey.DIALOG_SAVE_DESIGN_CASE: {
        Language.ENGLISH: "Save the design case",
        Language.TURKISH: "Tasarımı kaydet",
    },
    MessageKey.DIALOG_EXPORT_ITERATION_HISTORY: {
        Language.ENGLISH: "Export the iteration history",
        Language.TURKISH: "İterasyon geçmişini aktar",
    },
    MessageKey.FIELD_RANGE_REJECTION_WITH_UNIT: {
        Language.ENGLISH: "Enter {lowest} to {highest} {unit}",
        Language.TURKISH: "{lowest} ile {highest} {unit} arasında girin",
    },
    MessageKey.FIELD_RANGE_REJECTION_WITHOUT_UNIT: {
        Language.ENGLISH: "Enter {lowest} to {highest}",
        Language.TURKISH: "{lowest} ile {highest} arasında girin",
    },
    MessageKey.REPORT_DESIGN_CASE_NAME: {
        Language.ENGLISH: "Design case: {name}",
        Language.TURKISH: "Tasarım: {name}",
    },
    MessageKey.REPORT_ALLOWED: {
        Language.ENGLISH: "Allowed",
        Language.TURKISH: "İzin verilen",
    },
    MessageKey.REPORT_CONVERGED: {
        Language.ENGLISH: "Coefficients agree within {tolerance} %",
        Language.TURKISH: "Katsayılar %{tolerance} içinde uyuşuyor",
    },
    MessageKey.COMMAND_DESCRIPTION: {
        Language.ENGLISH: "Shell and tube heat exchanger design tool for olympic swimming pools",
        Language.TURKISH: "Olimpik havuzlar için gövde borulu ısı değiştirici tasarım aracı",
    },
    MessageKey.COMMAND_EVALUATE_HELP: {
        Language.ENGLISH: "Evaluate one design case and report the results",
        Language.TURKISH: "Bir tasarımı değerlendir ve sonuçları raporla",
    },
    MessageKey.COMMAND_COMPARE_HELP: {
        Language.ENGLISH: "Compare two JSON results produced by evaluate",
        Language.TURKISH: "Evaluate ile üretilmiş iki JSON sonucu karşılaştır",
    },
    MessageKey.COMMAND_GUI_HELP: {
        Language.ENGLISH: "Start the graphical user interface",
        Language.TURKISH: "Grafik arayüzü başlat",
    },
    MessageKey.COMMAND_JSON_OUTPUT_HELP: {
        Language.ENGLISH: "Write the full result as JSON for later comparison",
        Language.TURKISH: "Sonucun tamamını sonraki karşılaştırma için JSON olarak yaz",
    },
    MessageKey.COMMAND_QUIET_HELP: {
        Language.ENGLISH: "Suppress the aligned text report on standard output",
        Language.TURKISH: "Standart çıktıdaki hizalı metin raporunu bastırma",
    },
    MessageKey.COMMAND_FAIL_ON_CONSTRAINT_HELP: {
        Language.ENGLISH: "Exit with a non zero status when a TEMA or FINA limit is violated",
        Language.TURKISH: "Bir TEMA veya FINA sınırı aşıldığında sıfırdan farklı durumla çık",
    },
    MessageKey.COMMAND_WEB_HELP: {
        Language.ENGLISH: "Serve the interface over http instead of opening a desktop window",
        Language.TURKISH: "Arayüzü masaüstü penceresi yerine http üzerinden sun",
    },
    MessageKey.COMMAND_LANGUAGE_HELP: {
        Language.ENGLISH: "Language for every message this program prints or displays",
        Language.TURKISH: "Bu programın yazdığı ve gösterdiği her mesajın dili",
    },
    MessageKey.COMMAND_VERSION_HELP: {
        Language.ENGLISH: "Print the program version and exit",
        Language.TURKISH: "Program sürümünü yazdır ve çık",
    },
    MessageKey.COMMAND_RESULTS_AGREE: {
        Language.ENGLISH: "The two results agree within the requested tolerance",
        Language.TURKISH: "İki sonuç istenen tolerans içinde uyuşuyor",
    },
    MessageKey.COMMAND_COMPARISON_QUANTITY: {
        Language.ENGLISH: "Quantity",
        Language.TURKISH: "Büyüklük",
    },
    MessageKey.COMMAND_COMPARISON_FIRST: {
        Language.ENGLISH: "First",
        Language.TURKISH: "Birinci",
    },
    MessageKey.COMMAND_COMPARISON_SECOND: {
        Language.ENGLISH: "Second",
        Language.TURKISH: "İkinci",
    },
    MessageKey.COMMAND_COMPARISON_RELATIVE: {
        Language.ENGLISH: "Relative",
        Language.TURKISH: "Bağıl",
    },
    MessageKey.COMMAND_INTERFACE_NEEDS_FLET: {
        Language.ENGLISH: (
            "The graphical interface needs Flet. From the project folder, install the "
            "matching extra with\n"
            '    pip install ".[desktop-interface]"\n'
            "or, to serve it over http,\n"
            '    pip install ".[web-interface]"\n'
            "Import failed with: {reason}"
        ),
        Language.TURKISH: (
            "Grafik arayüz Flet gerektirir. Proje klasöründe uygun eklentiyi şu komutla "
            "kurun\n"
            '    pip install ".[desktop-interface]"\n'
            "ya da http üzerinden sunmak için\n"
            '    pip install ".[web-interface]"\n'
            "İçe aktarma şu hatayla başarısız oldu: {reason}"
        ),
    },
    MessageKey.TAB_INPUTS: {
        Language.ENGLISH: "1   Inputs",
        Language.TURKISH: "1   Girdiler",
    },
    MessageKey.TAB_RESULTS: {
        Language.ENGLISH: "2   Results",
        Language.TURKISH: "2   Sonuçlar",
    },
    MessageKey.HINT_INPUTS: {
        Language.ENGLISH: (
            "Enter the operating conditions and the geometry, then press Calculate. The "
            "values already filled in are a working example."
        ),
        Language.TURKISH: (
            "Çalışma koşullarını ve geometriyi girin, ardından Hesapla'ya basın. "
            "Doldurulmuş değerler çalışan bir örnektir."
        ),
    },
    MessageKey.GROUP_FLOW_ARRANGEMENT: {
        Language.ENGLISH: "Flow arrangement",
        Language.TURKISH: "Akış düzeni",
    },
    MessageKey.GROUP_POOL_WATER: {
        Language.ENGLISH: "Pool water · tube side",
        Language.TURKISH: "Havuz suyu · boru tarafı",
    },
    MessageKey.GROUP_HOT_WATER: {
        Language.ENGLISH: "Hot water · shell side",
        Language.TURKISH: "Sıcak su · gövde tarafı",
    },
    MessageKey.GROUP_TUBES: {
        Language.ENGLISH: "Tubes",
        Language.TURKISH: "Borular",
    },
    MessageKey.GROUP_SHELL_AND_BAFFLES: {
        Language.ENGLISH: "Shell and baffles",
        Language.TURKISH: "Gövde ve bafiller",
    },
    MessageKey.GROUP_DESIGN_ASSUMPTIONS: {
        Language.ENGLISH: "Design assumptions",
        Language.TURKISH: "Tasarım varsayımları",
    },
    MessageKey.BUTTON_USE_COMPUTED_COEFFICIENTS: {
        Language.ENGLISH: "Use computed coefficients",
        Language.TURKISH: "Hesaplanan katsayıları kullan",
    },
    MessageKey.BUTTON_USE_SUGGESTED_GEOMETRY: {
        Language.ENGLISH: "Use suggested geometry",
        Language.TURKISH: "Önerilen geometriyi kullan",
    },
    MessageKey.BUTTON_BACK_TO_INPUTS: {
        Language.ENGLISH: "Back to inputs",
        Language.TURKISH: "Girdilere dön",
    },
    MessageKey.STATUS_NO_RESULTS_YET: {
        Language.ENGLISH: "No results yet. Fill in the inputs and press Calculate.",
        Language.TURKISH: "Henüz sonuç yok. Girdileri doldurup Hesapla'ya basın.",
    },
    MessageKey.STATUS_DESIGN_CASE_DOWNLOADED: {
        Language.ENGLISH: "Design case downloaded as {file_name}",
        Language.TURKISH: "Tasarım {file_name} olarak indirildi",
    },
    MessageKey.STATUS_ITERATION_HISTORY_DOWNLOADED: {
        Language.ENGLISH: "Iteration history downloaded as {file_name}",
        Language.TURKISH: "İterasyon geçmişi {file_name} olarak indirildi",
    },
    MessageKey.VERDICT_CONSISTENT: {
        Language.ENGLISH: "Design consistent",
        Language.TURKISH: "Tasarım tutarlı",
    },
    MessageKey.VERDICT_NOT_CONSISTENT_YET: {
        Language.ENGLISH: "Not consistent yet",
        Language.TURKISH: "Henüz tutarlı değil",
    },
    MessageKey.VERDICT_EXPLANATION: {
        Language.ENGLISH: (
            "A design is consistent when the assumed coefficients match the computed ones "
            "and the entered geometry is the suggested one. Each button applies one "
            "correction and calculates again."
        ),
        Language.TURKISH: (
            "Varsayılan katsayılar hesaplananlarla, girilen geometri de önerilenle aynı "
            "olduğunda tasarım tutarlıdır. Her düğme bir düzeltme uygular ve yeniden "
            "hesaplar."
        ),
    },
    MessageKey.CHECK_LINE_COEFFICIENTS_AGREE: {
        Language.ENGLISH: "Assumed and computed coefficients agree within {tolerance} %",
        Language.TURKISH: "Varsayılan ve hesaplanan katsayılar %{tolerance} içinde uyuşuyor",
    },
    MessageKey.CHECK_LINE_COEFFICIENTS_DIFFER: {
        Language.ENGLISH: "Assumed and computed coefficients differ by up to {gap} %",
        Language.TURKISH: "Varsayılan ve hesaplanan katsayılar %{gap} kadar farklı",
    },
    MessageKey.CHECK_LINE_GEOMETRY_MATCHES: {
        Language.ENGLISH: "Entered geometry is the suggested geometry",
        Language.TURKISH: "Girilen geometri önerilen geometriyle aynı",
    },
    MessageKey.CHECK_LINE_GEOMETRY_DIFFERS: {
        Language.ENGLISH: "Entered geometry differs from the suggested geometry by up to {gap} %",
        Language.TURKISH: "Girilen geometri önerilenden %{gap} kadar farklı",
    },
    MessageKey.REPORT_DIFFERS_BY: {
        Language.ENGLISH: "Differs by {gap} %",
        Language.TURKISH: "%{gap} farklı",
    },
    MessageKey.HEADING_PRESSURE_DROP: {
        Language.ENGLISH: "Pressure drop",
        Language.TURKISH: "Basınç düşümü",
    },
    MessageKey.HEADING_ITERATION_HISTORY: {
        Language.ENGLISH: "Iteration history",
        Language.TURKISH: "İterasyon geçmişi",
    },
    MessageKey.HEADING_NOTES: {
        Language.ENGLISH: "Notes",
        Language.TURKISH: "Notlar",
    },
    MessageKey.NOTE_TUBE_SIDE_CORRELATION_OUTSIDE_RANGE: {
        Language.ENGLISH: (
            "Tube side: Reynolds number {reynolds} (Prandtl {prandtl}) is outside the "
            "validated range of the {correlation_name} correlation (Re ≥ {minimum}, "
            "{lowest_prandtl} ≤ Pr ≤ {highest_prandtl}). Treat the tube side coefficient "
            "with care."
        ),
        Language.TURKISH: (
            "Boru tarafı: Reynolds sayısı {reynolds} (Prandtl {prandtl}), "
            "{correlation_name} korelasyonunun doğrulanmış aralığının dışında (Re ≥ "
            "{minimum}, {lowest_prandtl} ≤ Pr ≤ {highest_prandtl}). Boru tarafı katsayısını "
            "dikkatle değerlendirin."
        ),
    },
    MessageKey.NOTE_SHELL_SIDE_CORRELATION_OUTSIDE_RANGE: {
        Language.ENGLISH: (
            "Shell side: Reynolds number {reynolds} is outside the validated range of the "
            "{correlation_name} correlation ({minimum} ≤ Re ≤ {maximum}). Treat the shell "
            "side coefficient with care."
        ),
        Language.TURKISH: (
            "Gövde tarafı: Reynolds sayısı {reynolds}, {correlation_name} korelasyonunun "
            "doğrulanmış aralığının dışında ({minimum} ≤ Re ≤ {maximum}). Gövde tarafı "
            "katsayısını dikkatle değerlendirin."
        ),
    },
    MessageKey.NOTE_NONE: {
        Language.ENGLISH: "No notes. Every correlation was applied inside its validated range.",
        Language.TURKISH: "Not yok. Her korelasyon doğrulanmış aralığında uygulandı.",
    },
    MessageKey.COLUMN_CHECK: {
        Language.ENGLISH: "Check",
        Language.TURKISH: "Kontrol",
    },
    MessageKey.COLUMN_VALUE: {
        Language.ENGLISH: "Value",
        Language.TURKISH: "Değer",
    },
    MessageKey.COLUMN_ALLOWED: {
        Language.ENGLISH: "Allowed",
        Language.TURKISH: "İzin verilen",
    },
    MessageKey.COLUMN_SOURCE: {
        Language.ENGLISH: "Source",
        Language.TURKISH: "Kaynak",
    },
    MessageKey.COLUMN_STATUS: {
        Language.ENGLISH: "Status",
        Language.TURKISH: "Durum",
    },
    MessageKey.SCHEMATIC_POOL_WATER_IN: {
        Language.ENGLISH: "Pool water in",
        Language.TURKISH: "Havuz suyu girişi",
    },
    MessageKey.SCHEMATIC_POOL_WATER_OUT: {
        Language.ENGLISH: "Pool water out",
        Language.TURKISH: "Havuz suyu çıkışı",
    },
    MessageKey.SCHEMATIC_HOT_WATER_IN: {
        Language.ENGLISH: "Hot water in",
        Language.TURKISH: "Sıcak su girişi",
    },
    MessageKey.SCHEMATIC_HOT_WATER_OUT: {
        Language.ENGLISH: "Hot water out",
        Language.TURKISH: "Sıcak su çıkışı",
    },
    MessageKey.SCHEMATIC_SHELL: {
        Language.ENGLISH: "Shell",
        Language.TURKISH: "Gövde",
    },
    MessageKey.SCHEMATIC_BAFFLES: {
        Language.ENGLISH: "Baffles",
        Language.TURKISH: "Bafiller",
    },
    MessageKey.SCHEMATIC_RETURN_HEAD: {
        Language.ENGLISH: "Return head",
        Language.TURKISH: "Dönüş başlığı",
    },
    MessageKey.FIELD_IN_GROUP: {
        Language.ENGLISH: "{group} › {field}",
        Language.TURKISH: "{group} › {field}",
    },
    MessageKey.STATUS_INPUTS_CHANGED: {
        Language.ENGLISH: (
            "Inputs changed since the last calculation. Press Calculate to update the results."
        ),
        Language.TURKISH: (
            "Girdiler son hesaplamadan beri değişti. Sonuçları güncellemek için Hesapla'ya basın."
        ),
    },
    MessageKey.COLUMN_GEOMETRY_GAP: {
        Language.ENGLISH: "Geometry gap",
        Language.TURKISH: "Geometri farkı",
    },
    MessageKey.FIELD_SHELL_SIDE_OUTLET_TEMPERATURE_COMPUTED: {
        Language.ENGLISH: "Outlet temperature (computed)",
        Language.TURKISH: "Çıkış sıcaklığı (hesaplanan)",
    },
}
