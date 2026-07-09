"""
Data contract validation. Turns a silent wrong-shape bug into a specific,
readable error before it ever reaches a rendering library's own (much
less friendly) stack trace.
"""

from __future__ import annotations

import pandas as pd

from .specs import ChartSpec


class ContractError(ValueError):
    pass


def validate_contract(df: pd.DataFrame, spec: ChartSpec) -> None:
    missing = [f for f in spec.required_fields if f not in df.columns]
    if missing:
        raise ContractError(
            f"'{spec.chart_type}' requires {spec.required_fields}, "
            f"but {missing} missing after prep. "
            f"Available columns: {list(df.columns)}"
        )
    if df.empty:
        raise ContractError(f"'{spec.chart_type}' received an empty dataframe after prep.")
