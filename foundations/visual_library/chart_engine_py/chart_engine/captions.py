"""
Caption and text-wrapping helpers shared across render functions.
"""

from __future__ import annotations

import textwrap


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


def wrap_text(text: str | None, width: int | None) -> str | None:
    if not text or not width or width <= 0:
        return text
    return "\n".join(textwrap.wrap(text, width=width))
