"""Deep Dive Research Tool — data access layer.

Wraps the mart_intelligence tables and Phase 6/5 flat files.
Reuses shared.db for connection and CBSA list queries.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd
import streamlit as st

from config import (
    CANDIDATE_LIST_PATH,
    KPI_TRAJECTORY_LONG_PATH,
    OVERLAP_FLAGS_PATH,
    OPP_TURN_SIGNALS_PATH,
    TRAJECTORY_SCORES_PATH,
)
from shared.db import get_connection

# ---------------------------------------------------------------------------
# CBSA universe
# ---------------------------------------------------------------------------


@st.cache_data(ttl=3600)
def get_cbsa_list() -> pd.DataFrame:
    """Return CBSAs that have full intelligence profiles (inner join to livability mart)."""
    con = get_connection()
    try:
        return con.execute("""
            SELECT
                p.cbsa_code,
                p.cbsa_name,
                p.pop_total,
                p.division_name,
                p.region_name,
                p.state_name_primary
            FROM mart_area_explorer.cbsa_profile_year p
            INNER JOIN mart_intelligence.intelligence_livability l
                ON p.cbsa_code = l.cbsa_code
            WHERE p.year = (SELECT MAX(year) FROM mart_area_explorer.cbsa_profile_year)
            ORDER BY p.cbsa_name
        """).fetchdf()
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Full frame profiles
# ---------------------------------------------------------------------------


@st.cache_data(ttl=3600)
def get_livability_profile(cbsa_code: str) -> dict[str, Any]:
    con = get_connection()
    try:
        row = con.execute(
            "SELECT * FROM mart_intelligence.intelligence_livability WHERE cbsa_code = ?",
            [cbsa_code],
        ).fetchdf()
    finally:
        con.close()
    if row.empty:
        return {}
    return row.iloc[0].to_dict()


@st.cache_data(ttl=3600)
def get_opportunity_profile(cbsa_code: str) -> dict[str, Any]:
    con = get_connection()
    try:
        row = con.execute(
            "SELECT * FROM mart_intelligence.intelligence_opportunity WHERE cbsa_code = ?",
            [cbsa_code],
        ).fetchdf()
    finally:
        con.close()
    if row.empty:
        return {}
    return row.iloc[0].to_dict()


@st.cache_data(ttl=3600)
def get_character_profile(cbsa_code: str) -> dict[str, Any]:
    con = get_connection()
    try:
        row = con.execute(
            "SELECT * FROM mart_intelligence.intelligence_character WHERE cbsa_code = ?",
            [cbsa_code],
        ).fetchdf()
    finally:
        con.close()
    if row.empty:
        return {}
    return row.iloc[0].to_dict()


@st.cache_data(ttl=3600)
def get_cross_frame_profile(cbsa_code: str) -> dict[str, Any]:
    con = get_connection()
    try:
        row = con.execute(
            "SELECT * FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = ?",
            [cbsa_code],
        ).fetchdf()
    finally:
        con.close()
    if row.empty:
        return {}
    return row.iloc[0].to_dict()


@st.cache_data(ttl=3600)
def get_full_profile(cbsa_code: str) -> dict[str, Any]:
    """Bundle all four frame profiles into one dict."""
    return {
        "livability": get_livability_profile(cbsa_code),
        "opportunity": get_opportunity_profile(cbsa_code),
        "character": get_character_profile(cbsa_code),
        "cross_frame": get_cross_frame_profile(cbsa_code),
    }


# ---------------------------------------------------------------------------
# Scatter surface (all CBSAs — for Overview L/O chart)
# ---------------------------------------------------------------------------


@st.cache_data(ttl=3600)
def get_scatter_surface() -> pd.DataFrame:
    con = get_connection()
    try:
        return con.execute("""
            SELECT
                cf.cbsa_code,
                cf.cbsa_name,
                cf.livability__livability_percentile,
                cf.opportunity__opportunity_percentile,
                cf.character__character_percentile,
                cf.livability__livability_cluster_name,
                cf.opportunity__opportunity_cluster_name,
                cf.character__character_cluster_name,
                cf.cross_frame_cluster_name,
                cf.overlap_profile,
                cf.signature,
                p.pop_total,
                p.division_name
            FROM mart_intelligence.intelligence_cross_frame cf
            LEFT JOIN mart_area_explorer.cbsa_profile_year p
                ON p.cbsa_code = cf.cbsa_code
               AND p.year = (SELECT MAX(year) FROM mart_area_explorer.cbsa_profile_year)
        """).fetchdf()
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Frame-specific peer lists
# ---------------------------------------------------------------------------


@st.cache_data(ttl=3600)
def get_frame_peers(cbsa_code: str, frame: str) -> pd.DataFrame:
    """Return top-10 peers for a single frame from the mart's wide peer columns."""
    table = f"mart_intelligence.intelligence_{frame}"
    con = get_connection()
    try:
        row = con.execute(
            f"SELECT * FROM {table} WHERE cbsa_code = ?", [cbsa_code]
        ).fetchdf()
    finally:
        con.close()
    if row.empty:
        return pd.DataFrame()

    r = row.iloc[0]
    rows = []
    for i in range(1, 11):
        code = r.get(f"top10_peer_{i}_cbsa_code")
        name = r.get(f"top10_peer_{i}_cbsa_name")
        sim = r.get(f"top10_peer_{i}_similarity")
        if pd.notna(code):
            rows.append({"peer_rank": i, "cbsa_code": code, "cbsa_name": name, "similarity": sim})
    return pd.DataFrame(rows)


@st.cache_data(ttl=3600)
def get_cross_frame_peers(cbsa_code: str) -> pd.DataFrame:
    return get_frame_peers(cbsa_code, "cross_frame")


# ---------------------------------------------------------------------------
# Phase 6 trajectory
# ---------------------------------------------------------------------------


@st.cache_data(ttl=3600)
def get_trajectory_scores() -> pd.DataFrame:
    return pd.read_parquet(str(TRAJECTORY_SCORES_PATH))


@st.cache_data(ttl=3600)
def get_trajectory_row(cbsa_code: str) -> dict[str, Any]:
    df = get_trajectory_scores()
    row = df[df["cbsa_code"] == cbsa_code]
    if row.empty:
        return {}
    return row.iloc[0].to_dict()


@st.cache_data(ttl=3600)
def get_candidate_list() -> pd.DataFrame:
    return pd.read_csv(str(CANDIDATE_LIST_PATH))


@st.cache_data(ttl=3600)
def get_kpi_trajectory(cbsa_code: str) -> pd.DataFrame:
    if not KPI_TRAJECTORY_LONG_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(str(KPI_TRAJECTORY_LONG_PATH))
    # cbsa_code is int64 in this CSV
    return df[df["cbsa_code"] == int(cbsa_code)].copy()


# ---------------------------------------------------------------------------
# Key stats for Overview and peer tables
# ---------------------------------------------------------------------------


@st.cache_data(ttl=3600)
def get_cbsa_key_stats(cbsa_code: str) -> dict[str, Any]:
    con = get_connection()
    try:
        row = con.execute("""
            SELECT
                cbsa_code, cbsa_name, pop_total, median_age,
                pop_growth_5yr, median_hh_income, value_to_income,
                division_name, state_name_primary
            FROM mart_area_explorer.cbsa_profile_year
            WHERE cbsa_code = ?
              AND year = (SELECT MAX(year) FROM mart_area_explorer.cbsa_profile_year)
        """, [cbsa_code]).fetchone()
    finally:
        con.close()
    if not row:
        return {}
    keys = ["cbsa_code", "cbsa_name", "pop_total", "median_age",
            "pop_growth_5yr", "median_hh_income", "value_to_income",
            "division_name", "state_name_primary"]
    return dict(zip(keys, row))


@st.cache_data(ttl=3600)
def get_cbsa_key_stats_batch(cbsa_codes: tuple[str, ...]) -> pd.DataFrame:
    if not cbsa_codes:
        return pd.DataFrame()
    con = get_connection()
    placeholders = ", ".join("?" for _ in cbsa_codes)
    try:
        return con.execute(f"""
            SELECT
                cbsa_code, cbsa_name, pop_total, median_age,
                pop_growth_5yr, median_hh_income, value_to_income
            FROM mart_area_explorer.cbsa_profile_year
            WHERE cbsa_code IN ({placeholders})
              AND year = (SELECT MAX(year) FROM mart_area_explorer.cbsa_profile_year)
        """, list(cbsa_codes)).fetchdf()
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Industry & occupation
# ---------------------------------------------------------------------------


@st.cache_data(ttl=3600)
def get_industry_profile(cbsa_code: str) -> pd.DataFrame:
    con = get_connection()
    try:
        row = con.execute("""
            SELECT
                pct_qcew_private_emp_manufacturing,   national_pct_qcew_private_emp_manufacturing,
                pct_qcew_private_emp_professional,    national_pct_qcew_private_emp_professional,
                pct_qcew_private_emp_educ_health,     national_pct_qcew_private_emp_educ_health,
                pct_qcew_private_emp_finance_real,    national_pct_qcew_private_emp_finance_real,
                pct_qcew_private_emp_information,     national_pct_qcew_private_emp_information,
                pct_qcew_private_emp_retail,          national_pct_qcew_private_emp_retail,
                pct_qcew_private_emp_construction,    national_pct_qcew_private_emp_construction,
                pct_qcew_private_emp_arts_accomm_food,national_pct_qcew_private_emp_arts_accomm_food,
                pct_qcew_private_emp_transport_util,  national_pct_qcew_private_emp_transport_util
            FROM gold.economics_industry_wide
            WHERE geo_level = 'cbsa' AND geo_id = ?
            ORDER BY year DESC LIMIT 1
        """, [cbsa_code]).fetchone()
    finally:
        con.close()

    industries = [
        "Manufacturing", "Professional Services", "Education & Health",
        "Finance & Real Estate", "Information", "Retail",
        "Construction", "Arts, Accomm & Food", "Transport & Utilities",
    ]
    if not row:
        return pd.DataFrame()
    cbsa_vals = list(row[0::2])
    nat_vals = list(row[1::2])
    metro_pcts = [v * 100 if v is not None else None for v in cbsa_vals]
    nat_pcts = [v * 100 if v is not None else None for v in nat_vals]
    lqs = [
        round(m / n, 2) if (m is not None and n and n > 0) else None
        for m, n in zip(metro_pcts, nat_pcts)
    ]
    return pd.DataFrame({
        "Industry": industries,
        "Metro %": metro_pcts,
        "National %": nat_pcts,
        "LQ": lqs,
    })


@st.cache_data(ttl=3600)
def get_occupation_profile(cbsa_code: str) -> pd.DataFrame:
    con = get_connection()
    try:
        row = con.execute("""
            SELECT
                oews_pct_emp_stem,
                oews_pct_emp_management_professional,
                oews_pct_emp_service,
                oews_pct_emp_production_transportation,
                oews_pct_emp_other,
                oews_lq_stem,
                oews_lq_management_professional,
                oews_lq_service,
                oews_lq_production_transportation,
                oews_lq_other
            FROM gold.economics_occupation_wide
            WHERE geo_level = 'cbsa' AND geo_id = ?
            ORDER BY year DESC LIMIT 1
        """, [cbsa_code]).fetchone()
    finally:
        con.close()

    occupations = ["STEM", "Mgmt & Professional", "Service", "Production & Transport", "Other"]
    if not row:
        return pd.DataFrame()
    pcts = [v * 100 if v is not None else None for v in row[:5]]
    lqs = list(row[5:])
    # Back-calculate national % from metro % and LQ (national_pct = metro_pct / lq)
    nat_pcts = [
        round(p / l, 1) if (p is not None and l and l > 0) else None
        for p, l in zip(pcts, lqs)
    ]
    return pd.DataFrame({
        "Occupation": occupations,
        "Metro %": pcts,
        "National %": nat_pcts,
        "LQ": [round(v, 2) if v is not None else None for v in lqs],
    })


# ---------------------------------------------------------------------------
# Phase 5 overlap flags
# ---------------------------------------------------------------------------


@st.cache_data(ttl=3600)
def get_kpi_zscore_params() -> dict[str, dict[str, float]]:
    """Return {col: {mean, std}} for every scored_ KPI column across all CBSAs.

    These are used in the app to convert polarity-adjusted raw values into
    proper z-scores on the fly, without changing the mart schema.
    """
    con = get_connection()
    try:
        frames = {
            "livability": "mart_intelligence.intelligence_livability",
            "opportunity": "mart_intelligence.intelligence_opportunity",
            "character": "mart_intelligence.intelligence_character",
        }
        params: dict[str, dict[str, float]] = {}
        for frame, table in frames.items():
            scored_cols = con.execute(f"""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'mart_intelligence'
                  AND table_name = 'intelligence_{frame}'
                  AND column_name LIKE 'scored_%'
                ORDER BY column_name
            """).fetchdf()["column_name"].tolist()

            if not scored_cols:
                continue

            agg_exprs = ", ".join(
                f"AVG({c}) AS {c}__mean, STDDEV_SAMP({c}) AS {c}__std"
                for c in scored_cols
            )
            row = con.execute(f"SELECT {agg_exprs} FROM {table}").fetchone()
            col_names = con.execute(f"SELECT {agg_exprs} FROM {table}").description

            # Parse interleaved mean/std pairs
            for i, col in enumerate(scored_cols):
                mean_val = row[i * 2]
                std_val = row[i * 2 + 1]
                if mean_val is not None and std_val and std_val > 0:
                    params[col] = {"mean": mean_val, "std": std_val}
        return params
    finally:
        con.close()


# Mapping from trajectory metric_id → (gold_schema_table, gold_column)
# Verified against information_schema. KPIs without a multi-year gold source are omitted
# (aqi_unhealthy_days has no matching col; jobs_access_45min_transit is single-year SLD only).
_KPI_GOLD_SOURCE: dict[str, tuple[str, str]] = {
    # Affordability
    "value_to_income":              ("affordability_wide",       "value_to_income"),
    "pct_rent_burden_30plus":       ("affordability_wide",       "pct_rent_burden_30plus"),
    "vacancy_rate":                 ("affordability_wide",       "vacancy_rate"),
    # Housing supply / structure
    "permits_per_1000_housing_units": ("housing_core_wide",     "permits_per_1000_housing_units"),
    "permits_share_units_5_plus":   ("housing_core_wide",       "permits_share_units_5_plus"),
    "pct_struct_mobile":            ("housing_core_wide",       "pct_struct_mobile"),
    "pct_struct_small_mf":          ("housing_core_wide",       "pct_struct_small_mf"),
    "pct_struct_mid_mf":            ("housing_core_wide",       "pct_struct_mid_mf"),
    "pct_struct_multifam":          ("housing_core_wide",       "pct_struct_multifam"),
    # Health
    "premature_death_rate":         ("health_wide",             "premature_death_rate"),
    "mental_health_provider_ratio": ("health_wide",             "mental_health_provider_ratio"),
    "drug_overdose_death_rate":     ("health_wide",             "drug_overdose_death_rate"),
    "pct_uninsured_adults":         ("health_wide",             "pct_uninsured_adults"),
    "preventable_hospital_stay_rate": ("health_wide",           "preventable_hospital_stay_rate"),
    "firearm_fatality_rate":        ("health_wide",             "firearm_fatality_rate"),
    "motor_vehicle_crash_rate":     ("health_wide",             "motor_vehicle_crash_rate"),
    "social_associations_per_10k":  ("health_wide",             "social_associations_per_10k"),
    # Transport / access
    "pct_commute_walk":             ("transport_built_form_wide", "pct_commute_walk"),
    "pct_commute_wfh":              ("transport_built_form_wide", "pct_commute_wfh"),
    "pct_hh_0_vehicles":            ("transport_built_form_wide", "pct_hh_0_vehicles"),
    "pop_weighted_density_sqmi":    ("transport_built_form_wide", "pop_weighted_density_sqmi"),
    # Internet access (social_infra_wide, 2015–2024)
    "pct_no_internet_access":       ("social_infra_wide",        "pct_no_internet_access"),
    # Environment
    "fema_risk_score":              ("environment_wide",         "fema_risk_score"),
    "aqi_unhealthy_days":           ("environment_wide",         "max_aqi"),  # closest proxy; aqi_unhealthy_days not in gold
    # Labor / income
    "pct_unemployment_rate":        ("economics_labor_wide",     "pct_unemployment_rate"),
    "lfpr":                         ("economics_labor_wide",     "lfpr"),
    "qcew_private_avg_wkly_wage":   ("economics_industry_wide",  "qcew_private_avg_wkly_wage"),
    "income_pc_growth_5yr":         ("economics_income_wide",    "income_pc_growth_5yr"),
    "pov_rate":                     ("economics_income_wide",    "pov_rate"),
    "pov_rate_change_5yr":          ("economics_income_wide",    "pov_rate_change_5yr"),
    "economic_connectedness":       ("social_fabric_wide",       "economic_connectedness"),
    # Housing market
    "hpi_5yr_pct":                  ("housing_market_wide",      "hpi_5yr_pct"),
    "hpi_yoy_pct":                  ("housing_market_wide",      "hpi_yoy_pct"),
    "zori_annual_avg_yoy_pct":      ("housing_market_wide",      "zori_annual_avg_yoy_pct"),
    # Migration / population
    "pop_growth_5yr":               ("migration_wide",           "pop_growth_5yr"),
    "irs_net_migration_rate":       ("migration_wide",           "irs_net_migration_rate"),
    "irs_net_agi":                  ("migration_wide",           "irs_net_agi"),
    "pct_moved_diff_st":            ("migration_wide",           "pct_moved_diff_st"),
    "pct_moved_abroad":             ("migration_wide",           "pct_moved_abroad"),
    # Business / industry
    "productivity_growth_5yr":      ("economics_gdp_wide",       "productivity_growth_5yr"),
    "pct_real_gdp_information":     ("economics_industry_wide",  "pct_qcew_private_emp_information"),
    "bfs_business_application_rate_per_1000_establishments": ("economics_industry_wide", "bfs_business_application_rate_per_1000_establishments"),
    "cbp_estabs_per_1000_residents": ("economics_industry_wide", "cbp_estabs_per_1000_residents"),
    "industry_concentration_hhi":   ("economics_industry_wide",  "industry_concentration_hhi"),
    "lq_information":               ("economics_industry_wide",  "lq_information"),
    "lq_manufacturing":             ("economics_industry_wide",  "lq_manufacturing"),
    "lq_professional":              ("economics_industry_wide",  "lq_professional"),
    # Demographics
    "pct_ba_plus":                  ("population_demographics",  "pct_ba_plus"),
    "pct_ba_plus_change_5yr":       ("population_demographics",  "pct_ba_plus_change_5yr"),
    "diversity_index":              ("population_demographics",  "diversity_index"),
    "pct_black_nh":                 ("population_demographics",  "pct_black_nh"),
    "pct_asian_nh":                 ("population_demographics",  "pct_asian_nh"),
    "pct_hispanic":                 ("population_demographics",  "pct_hispanic"),
    "pct_age_over_64":              ("population_demographics",  "pct_age_over_64"),
    "pct_foreign_born":             ("population_demographics",  "pct_foreign_born"),
    # Social fabric
    "friending_bias":               ("social_fabric_wide",       "friending_bias"),
    "civic_engagement_volunteering_rate": ("social_fabric_wide", "civic_engagement_volunteering_rate"),
    "civic_organizations_per_1000": ("social_fabric_wide",       "civic_organizations_per_1000"),
    "nonprofits_per_100k":          ("social_fabric_wide",       "nonprofits_per_100k"),
}


@st.cache_data(ttl=3600)
def get_kpi_timeseries(cbsa_code: str, metric_ids: tuple[str, ...]) -> pd.DataFrame:
    """Return annual time series for the selected KPIs for one CBSA + national median.

    Returns a DataFrame with columns: year, metric_id, cbsa_value, national_median.
    Only returns rows where both values are non-null.
    """
    if not metric_ids:
        return pd.DataFrame()

    con = get_connection()
    frames: list[pd.DataFrame] = []
    try:
        for metric_id in metric_ids:
            source = _KPI_GOLD_SOURCE.get(metric_id)
            if source is None:
                continue
            table, col = source
            # Skip mappings that use the fallback `if False else` trick pointing to wrong col
            try:
                df = con.execute(f"""
                    SELECT
                        year,
                        MAX(CASE WHEN geo_id = ? THEN {col} END) AS cbsa_value,
                        MEDIAN({col}) AS national_median
                    FROM gold.{table}
                    WHERE geo_level = 'cbsa'
                    GROUP BY year
                    HAVING cbsa_value IS NOT NULL OR national_median IS NOT NULL
                    ORDER BY year
                """, [cbsa_code]).fetchdf()
                df["metric_id"] = metric_id
                frames.append(df)
            except Exception:
                continue
    finally:
        con.close()

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


@st.cache_data(ttl=3600)
def get_overlap_flags() -> pd.DataFrame:
    return pd.read_csv(str(OVERLAP_FLAGS_PATH))


@st.cache_data(ttl=3600)
def get_overlap_row(cbsa_code: str) -> dict[str, Any]:
    df = get_overlap_flags()
    row = df[df["cbsa_code"] == cbsa_code]
    if row.empty:
        return {}
    return row.iloc[0].to_dict()


# ---------------------------------------------------------------------------
# Zone map
# ---------------------------------------------------------------------------


@st.cache_data(ttl=3600)
def get_zone_data(cbsa_code: str) -> pd.DataFrame:
    """Return zone cluster assignments + scores for one CBSA's tracts."""
    con = get_connection()
    try:
        return con.execute(
            "SELECT * FROM mart_intelligence.intelligence_zones WHERE cbsa_code = ?",
            [cbsa_code],
        ).fetchdf()
    finally:
        con.close()


@st.cache_data(ttl=3600)
def get_zone_geojson(cbsa_code: str) -> dict | None:
    """Export tract polygons for one CBSA as GeoJSON using DuckDB spatial."""
    con = get_connection()
    try:
        # Check if spatial extension is available
        con.execute("LOAD spatial")
        result = con.execute("""
            SELECT
                t.tract_geoid,
                ST_AsGeoJSON(t.geom) AS geojson_geom
            FROM geo.tracts_all_us t
            JOIN silver.xwalk_tract_county x ON x.tract_geoid = t.tract_geoid
            JOIN silver.xwalk_cbsa_county c
                ON c.county_fips = x.county_fip
               AND c.state_fips = x.state_fip
            WHERE c.cbsa_code = ?
              AND t.geom IS NOT NULL
        """, [cbsa_code]).fetchdf()
    except Exception:
        return None
    finally:
        con.close()

    if result.empty:
        return None

    import json
    features = []
    for _, row in result.iterrows():
        geom = json.loads(row["geojson_geom"])
        features.append({
            "type": "Feature",
            "properties": {"tract_geoid": row["tract_geoid"]},
            "geometry": geom,
        })
    return {"type": "FeatureCollection", "features": features}
