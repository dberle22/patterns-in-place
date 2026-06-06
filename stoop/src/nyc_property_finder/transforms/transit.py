"""Transit transforms."""

from __future__ import annotations

import pandas as pd


def count_subway_lines(lines: str | None) -> int:
    """Count subway lines from a whitespace-delimited line string."""

    if not lines:
        return 0
    return len(str(lines).split())
