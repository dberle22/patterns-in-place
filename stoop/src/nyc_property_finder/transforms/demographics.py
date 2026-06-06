"""Demographic feature transforms."""

from __future__ import annotations

import pandas as pd


def coerce_demographic_numeric_columns(dataframe: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Convert selected demographic columns to numeric values."""

    output = dataframe.copy()
    for column in columns:
        if column in output.columns:
            output[column] = pd.to_numeric(output[column], errors="coerce")
    return output
