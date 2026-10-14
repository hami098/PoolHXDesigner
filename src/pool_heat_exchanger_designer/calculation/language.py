from __future__ import annotations

from enum import Enum


class Language(Enum):
    ENGLISH = "en"
    TURKISH = "tr"

    def __str__(self) -> str:
        return self.value

    @property
    def endonym(self) -> str:
        return _ENDONYM_BY_LANGUAGE[self]

    def uppercase(self, text: str) -> str:
        return text.translate(_LOWERCASE_TO_UPPERCASE_BY_LANGUAGE[self]).upper()


_ENDONYM_BY_LANGUAGE = {
    Language.ENGLISH: "English",
    Language.TURKISH: "Türkçe",
}

_LOWERCASE_TO_UPPERCASE_BY_LANGUAGE = {
    Language.ENGLISH: str.maketrans("", ""),
    Language.TURKISH: str.maketrans("iı", "İI"),
}

DEFAULT_LANGUAGE = Language.ENGLISH

SELECTABLE_LANGUAGES = tuple(Language)
