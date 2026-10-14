from __future__ import annotations

from pool_heat_exchanger_designer.calculation.language import Language
from pool_heat_exchanger_designer.calculation.message_catalogue import MessageKey
from pool_heat_exchanger_designer.calculation.translator import (
    english_text,
    text_in_language,
)


class DesignError(Exception):
    def __init__(self, message_key: MessageKey, **parameters: object) -> None:
        self.message_key = message_key
        self.parameters = parameters
        super().__init__(english_text(message_key, **parameters))

    def text_in_language(self, language: Language) -> str:
        return text_in_language(language, self.message_key, **self.parameters)


class TemperatureOutsideTabulatedRangeError(DesignError):
    pass


class InvalidGeometryError(DesignError):
    pass


class InvalidOperatingConditionError(DesignError):
    pass


class DesignCaseFileError(DesignError):
    pass


class PropertyTableFileError(DesignError):
    pass


class GraphicalInterfaceUnavailableError(DesignError):
    pass
