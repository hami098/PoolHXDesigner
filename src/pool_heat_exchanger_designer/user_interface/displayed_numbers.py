from __future__ import annotations

import math

from pool_heat_exchanger_designer.calculation.message_catalogue import (
    SYMBOL_NOT_AVAILABLE,
    UNIT_SYMBOL_PERCENT,
)

PERCENT_PER_FRACTION = 100.0
PERCENT_DECIMAL_PLACES = 1


def number_text(value: float | None, decimal_places: int) -> str:
    if value is None or not math.isfinite(value):
        return SYMBOL_NOT_AVAILABLE
    return f"{value:.{decimal_places}f}"


def signed_percent_text(fraction: float) -> str:
    if not math.isfinite(fraction):
        return SYMBOL_NOT_AVAILABLE
    return f"{fraction * PERCENT_PER_FRACTION:+.{PERCENT_DECIMAL_PLACES}f} {UNIT_SYMBOL_PERCENT}"


def magnitude_percent_text(fraction: float) -> str:
    if not math.isfinite(fraction):
        return SYMBOL_NOT_AVAILABLE
    return f"{abs(fraction) * PERCENT_PER_FRACTION:.{PERCENT_DECIMAL_PLACES}f}"


def unsigned_percent_text(fraction: float) -> str:
    if not math.isfinite(fraction):
        return SYMBOL_NOT_AVAILABLE
    return f"{magnitude_percent_text(fraction)} {UNIT_SYMBOL_PERCENT}"
