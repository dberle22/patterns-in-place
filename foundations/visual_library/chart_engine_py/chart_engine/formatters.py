"""
Shared number-formatting helpers.

These functions mirror the intent of the R standards helpers: charts should
format values consistently regardless of whether they are rendered from Python
or the legacy R implementation.
"""

from __future__ import annotations

from math import isfinite
from typing import Any


def _coerce_number(value: Any) -> float | int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return value if isfinite(value) else None
    try:
        coerced = float(value)
    except (TypeError, ValueError):
        return None
    return coerced if isfinite(coerced) else None


def _compact_number(value: float | int, decimals: int = 1, currency: bool = False) -> str:
    suffixes = [(1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")]
    for threshold, suffix in suffixes:
        if abs(value) >= threshold:
            scaled = value / threshold
            prefix = "$" if currency else ""
            formatted = f"{scaled:.{decimals}f}".rstrip("0").rstrip(".")
            return f"{prefix}{formatted}{suffix}"
    if currency:
        return format_dollar(value, compact=False)
    return format_number(value, decimals=decimals, compact=False)


def format_percent(value: Any, decimals: int = 1) -> str | None:
    number = _coerce_number(value)
    if number is None:
        return None
    return f"{number * 100:.{decimals}f}%"


def format_dollar(value: Any, compact: bool = False) -> str | None:
    number = _coerce_number(value)
    if number is None:
        return None
    if compact:
        return _compact_number(number, decimals=1, currency=True)
    decimals = 0 if float(number).is_integer() else 2
    return f"${number:,.{decimals}f}"


def format_number(value: Any, decimals: int = 1, compact: bool = False) -> str | None:
    number = _coerce_number(value)
    if number is None:
        return None
    if compact:
        return _compact_number(number, decimals=decimals, currency=False)
    formatted = f"{number:,.{decimals}f}"
    if decimals > 0:
        formatted = formatted.rstrip("0").rstrip(".")
    return formatted


def format_integer(value: Any) -> str | None:
    number = _coerce_number(value)
    if number is None:
        return None
    return f"{int(round(number)):,}"


def format_rank(value: Any) -> str | None:
    rank = format_integer(value)
    return f"#{rank}" if rank is not None else None


def format_year_range(start: Any, end: Any = None) -> str | None:
    if start is None:
        return None
    if end is None or start == end:
        return str(start)
    return f"{start}-{end}"


def format_value_for_request(value: Any, number_format: Any = None) -> str | None:
    if number_format is None:
        return format_number(value)

    unit = getattr(number_format, "unit", "count")
    decimals = getattr(number_format, "decimals", 1)
    compact = getattr(number_format, "compact", False)

    if unit == "percent":
        return format_percent(value, decimals=decimals)
    if unit == "currency":
        return format_dollar(value, compact=compact)
    if unit == "ratio":
        return format_number(value, decimals=decimals, compact=compact)
    if unit == "index":
        return format_number(value, decimals=decimals, compact=compact)
    return format_number(value, decimals=decimals, compact=compact)


def to_d3_format(number_format: Any = None) -> str:
    if number_format is None:
        return ",.1f"

    unit = getattr(number_format, "unit", "count")
    decimals = getattr(number_format, "decimals", 1)
    compact = getattr(number_format, "compact", False)
    precision = max(int(decimals), 0)

    if unit == "percent":
        return f".{precision}%"
    if unit == "currency":
        return f"${'.' + str(precision) if precision else ''}~s" if compact else f"$,.{precision}f"
    if compact:
        return f".{precision}~s"
    if unit == "count" and precision == 0:
        return ",d"
    return f",.{precision}f"
