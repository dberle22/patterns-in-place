"""Shared helpers for split Market data products."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from site_prep import Site, get_connection


EMPLOYMENT_COLUMNS = {
    "pct_acs_ind_ag_mining": ("ag_mining", "Agriculture and mining", "acs_ind_ag_mining"),
    "pct_acs_ind_construction": ("construction", "Construction", "acs_ind_construction"),
    "pct_acs_ind_manufacturing": ("manufacturing", "Manufacturing", "acs_ind_manufacturing"),
    "pct_acs_ind_wholesale": ("wholesale", "Wholesale trade", "acs_ind_wholesale"),
    "pct_acs_ind_retail": ("retail", "Retail trade", "acs_ind_retail"),
    "pct_acs_ind_transport_util": ("transport_util", "Transportation and utilities", "acs_ind_transport_util"),
    "pct_acs_ind_information": ("information", "Information", "acs_ind_information"),
    "pct_acs_ind_finance_real": ("finance_real", "Finance and real estate", "acs_ind_finance_real"),
    "pct_acs_ind_professional": ("professional", "Professional services", "acs_ind_professional"),
    "pct_acs_ind_educ_health": ("educ_health", "Education and health", "acs_ind_educ_health"),
    "pct_acs_ind_arts_accomm_food": ("arts_accomm_food", "Arts, accommodation, and food", "acs_ind_arts_accomm_food"),
    "pct_acs_ind_other_services": ("other_services", "Other services", "acs_ind_other_services"),
    "pct_acs_ind_public_admin": ("public_admin", "Public administration", "acs_ind_public_admin"),
}
GDP_COLUMNS = {
    "pct_real_gdp_natural_resources": ("natural_resources", "Natural resources", "real_gdp_natural_resources"),
    "pct_real_gdp_manufacturing": ("manufacturing", "Manufacturing", "real_gdp_manufacturing"),
    "pct_real_gdp_construction": ("construction", "Construction", "real_gdp_construction"),
    "pct_real_gdp_trade": ("trade", "Trade", "real_gdp_trade"),
    "pct_real_gdp_transportation": ("transportation", "Transportation", "real_gdp_transportation"),
    "pct_real_gdp_information": ("information", "Information", "real_gdp_information"),
    "pct_real_gdp_fire": ("fire", "Finance, insurance, and real estate", "real_gdp_fire"),
    "pct_real_gdp_professional": ("professional", "Professional services", "real_gdp_professional"),
    "pct_real_gdp_edu_health": ("edu_health", "Education and health", "real_gdp_edu_health"),
    "pct_real_gdp_leisure": ("leisure", "Leisure and hospitality", "real_gdp_leisure"),
    "pct_real_gdp_gov": ("gov", "Government", "real_gdp_gov"),
    "pct_calc_real_gdp_other": ("other", "Other", "real_gdp_total"),
}


def build_market_payload(site: Site) -> dict[str, Any]:
    """Materialize the market payload from wide Gold surfaces with explicit long transforms."""

    employment_mix, gdp_mix = _query_market_industry_context(site.market_id)
    housing_context = _query_market_housing_context(site.market_id)
    return {
        "industry_context": {
            "employment_mix": employment_mix,
            "gdp_mix": gdp_mix,
        },
        "housing_context": housing_context,
        "candidate_note": "The Market tab is intentionally compact and remains a candidate for a reusable Metro Deep Dive summary component.",
    }


def empty_market_meta() -> dict[str, Any]:
    """Return a stable empty meta payload when market context is unavailable."""

    return {"candidate_note": None}


def normalize_market_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Keep Market outputs deterministic even when the source returns empty rows."""

    if frame.empty:
        return frame.copy()
    return frame.reset_index(drop=True)


def _query_market_industry_context(market_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read the latest CBSA industry row and reshape wide employment and GDP shares to long tables."""

    con = get_connection()
    try:
        employment_row = con.execute(
            """
            SELECT *
            FROM patterns_in_place.gold.economics_industry_wide
            WHERE geo_level = 'cbsa'
              AND geo_id = ?
              AND pct_acs_ind_retail IS NOT NULL
            ORDER BY year DESC
            LIMIT 1
            """,
            [str(market_id)],
        ).fetchdf()
        gdp_row = con.execute(
            """
            SELECT *
            FROM patterns_in_place.gold.economics_industry_wide
            WHERE geo_level = 'cbsa'
              AND geo_id = ?
              AND pct_real_gdp_trade IS NOT NULL
            ORDER BY year DESC
            LIMIT 1
            """,
            [str(market_id)],
        ).fetchdf()
    finally:
        con.close()

    if employment_row.empty and gdp_row.empty:
        return pd.DataFrame(), pd.DataFrame()

    employment = _reshape_market_mix(
        employment_row.iloc[0].to_dict() if not employment_row.empty else {},
        EMPLOYMENT_COLUMNS,
        source="gold.economics_industry_wide",
        share_scale=1.0,
    )
    gdp = _reshape_market_mix(
        gdp_row.iloc[0].to_dict() if not gdp_row.empty else {},
        GDP_COLUMNS,
        source="gold.economics_industry_wide",
        share_scale=1.0,
    )
    return employment, gdp


def _query_market_housing_context(market_id: str) -> pd.DataFrame:
    """Read the small CBSA housing trend series used by the Market tab."""

    con = get_connection()
    try:
        return con.execute(
            """
            SELECT
                year,
                geo_name,
                zhvi_annual_avg,
                zori_annual_avg,
                hpi_yoy_pct,
                zori_annual_avg_yoy_pct
            FROM patterns_in_place.gold.housing_market_wide
            WHERE geo_level = 'cbsa'
              AND geo_id = ?
            ORDER BY year
            """,
            [str(market_id)],
        ).fetchdf()
    finally:
        con.close()


def _reshape_market_mix(
    latest_row: dict[str, Any],
    column_map: dict[str, tuple[str, str, str]],
    *,
    source: str,
    share_scale: float,
) -> pd.DataFrame:
    """Turn one latest-year wide market row into a long sector-share table."""

    rows: list[dict[str, Any]] = []
    if not latest_row:
        return pd.DataFrame(columns=["year", "sector_id", "sector_label", "share_value", "raw_value", "source"])
    for share_column, (sector_id, sector_label, raw_column) in column_map.items():
        share_value = latest_row.get(share_column)
        raw_value = latest_row.get(raw_column)
        if pd.isna(share_value) and pd.isna(raw_value):
            continue
        normalized_share = None if pd.isna(share_value) else float(share_value) * share_scale
        rows.append(
            {
                "year": latest_row.get("year"),
                "sector_id": sector_id,
                "sector_label": sector_label,
                "share_value": normalized_share,
                "raw_value": None if pd.isna(raw_value) else float(raw_value),
                "source": source,
            }
        )
    if not rows:
        return pd.DataFrame(columns=["year", "sector_id", "sector_label", "share_value", "raw_value", "source"])
    return pd.DataFrame(rows).sort_values("share_value", ascending=False, kind="mergesort").reset_index(drop=True)
