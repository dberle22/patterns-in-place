"""
Caption and text-wrapping helpers shared across render functions.
"""

from __future__ import annotations

import textwrap
from typing import Any


def _compact_parts(parts: list[str | None]) -> list[str]:
    return [part.strip() for part in parts if isinstance(part, str) and part.strip()]


def build_caption(
    source: str | None = None,
    vintage: str | None = None,
    side_note: str | None = None,
    footer_note: str | None = None,
    methodology_note: str | None = None,
) -> str:
    parts = _compact_parts(
        [
            f"Source: {source}" if source else None,
            f"Vintage: {vintage}" if vintage else None,
            f"Note: {side_note}" if side_note else None,
            f"Method: {methodology_note}" if methodology_note else None,
            footer_note,
        ]
    )
    return " | ".join(parts)


def first_non_empty(df: Any, column: str) -> str | None:
    if not hasattr(df, "columns") or column not in df.columns:
        return None
    values = [str(value).strip() for value in df[column].dropna().unique() if str(value).strip()]
    return values[0] if values else None


def build_data_caption(
    df: Any,
    side_note: str | None = None,
    footer_note: str | None = None,
    methodology_note: str | None = None,
    note_column: str = "note",
) -> str:
    """
    Build a chart caption directly from the prepared dataframe so Python charts
    can keep source/vintage/note text visible in exported artifacts.
    """
    inherited_note = first_non_empty(df, note_column)
    merged_side_note = " ".join(
        part for part in [inherited_note, side_note] if isinstance(part, str) and part.strip()
    ) or None
    return build_caption(
        source=first_non_empty(df, "source"),
        vintage=first_non_empty(df, "vintage"),
        side_note=merged_side_note,
        footer_note=footer_note,
        methodology_note=methodology_note,
    )


def build_altair_title_params(
    title: str,
    subtitle: str | None = None,
    caption: str | None = None,
    *,
    title_size: float | int = 16,
    subtitle_wrap_width: int = 120,
    caption_wrap_width: int = 135,
) -> dict[str, Any]:
    """
    Altair does not have a first-class chart caption slot like ggplot2.
    To keep parity-critical notes visible in static exports, we append caption
    lines to the rendered subtitle block.
    """
    lines: list[str] = []
    if subtitle:
        wrapped = wrap_text(subtitle, subtitle_wrap_width)
        if wrapped:
            lines.extend(wrapped.split("\n"))
    if caption:
        wrapped_caption = wrap_text(caption, caption_wrap_width)
        if wrapped_caption:
            if lines:
                lines.append("")
            lines.extend(wrapped_caption.split("\n"))

    params: dict[str, Any] = {"text": title, "fontSize": title_size}
    if lines:
        params["subtitle"] = lines
    return params


def wrap_text(text: str | None, width: int | None) -> str | None:
    if not text or not width or width <= 0:
        return text
    return "\n".join(textwrap.wrap(text, width=width))
