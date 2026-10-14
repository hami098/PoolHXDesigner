from __future__ import annotations

import string

import pytest

from pool_heat_exchanger_designer.calculation.language import SELECTABLE_LANGUAGES, Language
from pool_heat_exchanger_designer.calculation.message_catalogue import (
    MESSAGE_CATALOGUE,
    MessageKey,
)
from pool_heat_exchanger_designer.calculation.translator import (
    Translator,
    english_text,
    text_in_language,
)


def format_field_names(template: str) -> set[str]:
    return {field_name for _, field_name, _, _ in string.Formatter().parse(template) if field_name}


def test_every_message_key_appears_in_the_catalogue() -> None:
    missing = [key.name for key in MessageKey if key not in MESSAGE_CATALOGUE]

    assert missing == []


def test_the_catalogue_contains_no_key_that_is_not_declared() -> None:
    declared = set(MessageKey)
    undeclared = [key for key in MESSAGE_CATALOGUE if key not in declared]

    assert undeclared == []


@pytest.mark.parametrize("language", SELECTABLE_LANGUAGES, ids=lambda item: item.value)
def test_every_message_is_translated_into_every_language(language: Language) -> None:
    untranslated = [
        key.name
        for key, translations in MESSAGE_CATALOGUE.items()
        if language not in translations or not translations[language].strip()
    ]

    assert untranslated == []


def test_the_format_fields_match_between_the_languages_for_every_message() -> None:
    mismatched = [
        key.name
        for key, translations in MESSAGE_CATALOGUE.items()
        if format_field_names(translations[Language.ENGLISH])
        != format_field_names(translations[Language.TURKISH])
    ]

    assert mismatched == []


def test_no_translation_repeats_the_english_wording_where_a_translation_is_expected() -> None:
    symbols_and_abbreviations = {
        MessageKey.COLUMN_ITERATION_NUMBER,
        MessageKey.STANDARD_TEMA,
        MessageKey.STANDARD_FINA,
        MessageKey.ALLOWED_RANGE_BETWEEN,
        MessageKey.ALLOWED_RANGE_AT_MOST,
        MessageKey.ALLOWED_RANGE_AT_LEAST,
        MessageKey.FIELD_IN_GROUP,
    }
    identical = [
        key.name
        for key, translations in MESSAGE_CATALOGUE.items()
        if key not in symbols_and_abbreviations
        and translations[Language.ENGLISH] == translations[Language.TURKISH]
    ]

    assert identical == []


def test_a_translator_renders_in_the_language_it_was_given() -> None:
    english = Translator(Language.ENGLISH)
    turkish = Translator(Language.TURKISH)

    assert english.text(MessageKey.BUTTON_CALCULATE) == "Calculate"
    assert turkish.text(MessageKey.BUTTON_CALCULATE) == "Hesapla"


def test_a_translator_can_switch_language_in_place() -> None:
    translator = Translator(Language.ENGLISH)
    translator.switch_to(Language.TURKISH)

    assert translator.language is Language.TURKISH
    assert translator.text(MessageKey.BUTTON_SAVE) == "Kaydet"


def test_parameters_are_substituted_in_both_languages() -> None:
    english = text_in_language(Language.ENGLISH, MessageKey.STATUS_EVALUATED, iteration_number=3)
    turkish = text_in_language(Language.TURKISH, MessageKey.STATUS_EVALUATED, iteration_number=3)

    assert "3" in english
    assert "3" in turkish


def test_english_text_is_available_without_constructing_a_translator() -> None:
    assert english_text(MessageKey.BUTTON_OPEN) == "Open"


def test_a_language_knows_its_own_name_in_its_own_language() -> None:
    assert Language.ENGLISH.endonym == "English"
    assert Language.TURKISH.endonym == "Türkçe"
