from __future__ import annotations

from pool_heat_exchanger_designer.calculation.language import (
    DEFAULT_LANGUAGE,
    Language,
)
from pool_heat_exchanger_designer.calculation.message_catalogue import (
    MESSAGE_CATALOGUE,
    MessageKey,
)


def text_in_language(language: Language, message_key: MessageKey, **parameters: object) -> str:
    return MESSAGE_CATALOGUE[message_key][language].format(**parameters)


def english_text(message_key: MessageKey, **parameters: object) -> str:
    return text_in_language(Language.ENGLISH, message_key, **parameters)


def uppercase_in_language(text: str, language: Language) -> str:
    return language.uppercase(text)


class Translator:
    def __init__(self, language: Language = DEFAULT_LANGUAGE) -> None:
        self._language = language

    @property
    def language(self) -> Language:
        return self._language

    def switch_to(self, language: Language) -> None:
        self._language = language

    def text(self, message_key: MessageKey, **parameters: object) -> str:
        return text_in_language(self._language, message_key, **parameters)

    def uppercase_text(self, message_key: MessageKey, **parameters: object) -> str:
        return uppercase_in_language(self.text(message_key, **parameters), self._language)
