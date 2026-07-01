"""DuckDB data access for the Phase 7 tract EDA app."""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

from config import TRACT_KPIS


TRACT_FRAME_TABLE = "gold.intelligence_zone_inputs"
INTELLIGENCE_CROSS_FRAME_PARQUET = (
    "exploration/intelligence_framework/phase_5_cross_frame_integration/outputs/"
    "cross_frame_scores.parquet"
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _default_db_path() -> Path:
    return _repo_root() / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"


def resolve_db_path() -> Path:
    db_connection = os.getenv("DB_CONNECTION") or os.getenv("DB_PATH")
    if db_connection:
        return Path(db_connection)
    return _default_db_path()


def get_connection() -> duckdb.DuckDBPyConnection:
    db_path = resolve_db_path()
    if not db_path.exists():
        raise FileNotFoundError(f"DuckDB file does not exist: {db_path}")
    return duckdb.connect(str(db_path), read_only=True)


@st.cache_data(ttl=3600)
def has_intelligence_datamart() -> bool:
    """Return whether the promoted intelligence marts are available in DuckDB."""
    con = get_connection()
    try:
        row = con.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'mart_intelligence'
              AND table_name = 'intelligence_cross_frame'
            """
        ).fetchone()
    finally:
        con.close()
    return bool(row and row[0] >= 1)


def _cross_frame_relation() -> str:
    """Resolve the CBSA cluster source to the promoted mart or Phase 5 parquet."""
    if has_intelligence_datamart():
        return "mart_intelligence.intelligence_cross_frame"

    parquet_path = _repo_root() / INTELLIGENCE_CROSS_FRAME_PARQUET
    if not parquet_path.exists():
        raise FileNotFoundError(f"Cross-frame parquet does not exist: {parquet_path}")
    return f"read_parquet('{parquet_path.as_posix()}')"


@st.cache_data(ttl=3600)
def load_cbsa_options() -> list[tuple[str, str]]:
    """Return (cbsa_code, cbsa_name) pairs for CBSAs in the crosswalk."""
    con = get_connection()
    try:
        rows = con.execute(
            """
            SELECT DISTINCT xwc.cbsa_code, dg.geo_name AS cbsa_name
            FROM silver.xwalk_cbsa_county xwc
            LEFT JOIN gold.dim_geo dg
                ON dg.geo_level = 'cbsa' AND dg.geo_id = xwc.cbsa_code
            ORDER BY cbsa_name
            """
        ).fetchall()
    finally:
        con.close()
    return [(cbsa_code, cbsa_name or cbsa_code) for cbsa_code, cbsa_name in rows]


@st.cache_data(ttl=3600)
def load_cross_frame_clusters() -> pd.DataFrame:
    """Return one cross-frame cluster label per CBSA for scatterplot enrichment."""
    relation = _cross_frame_relation()
    con = get_connection()
    try:
        if has_intelligence_datamart():
            df = con.execute(
                f"""
                SELECT cbsa_code, combined_cluster
                FROM {relation}
                """
            ).fetchdf()
        else:
            df = con.execute(
                f"""
                SELECT
                    cbsa_code,
                    cross_frame_cluster_name AS combined_cluster
                FROM {relation}
                """
            ).fetchdf()
    finally:
        con.close()
    return df


@st.cache_data(ttl=3600)
def load_tract_frame() -> pd.DataFrame:
    """Load the wide tract frame from the governed Gold table.

    The table is materialized upstream by `gold_intelligence_zone_inputs.sql`,
    so the app reads the same tract input surface that later Phase 7 runners
    will use. The national frame is cached once, and the sidebar CBSA filter
    slices that in-memory DataFrame for fast iteration across tabs.
    """
    con = get_connection()
    try:
        df = con.execute(f"select * from {TRACT_FRAME_TABLE}").fetchdf()
    finally:
        con.close()

    return df


@st.cache_data(ttl=3600)
def _cached_full_frame() -> pd.DataFrame:
    """Load and cache the national tract frame once per session."""
    return load_tract_frame()


def get_tract_frame(cbsa_codes: tuple[str, ...] | None = None) -> pd.DataFrame:
    """Return the tract frame, using the cached national frame when no filter is set."""
    if cbsa_codes:
        df = _cached_full_frame()
        return df[df["cbsa_code"].isin(set(cbsa_codes))].reset_index(drop=True)
    return _cached_full_frame()


def compute_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """Return a per-KPI coverage summary for the provided tract frame."""
    total = len(df)
    rows = []
    for kpi in TRACT_KPIS:
        kpi_id = kpi["kpi_id"]
        if kpi_id not in df.columns:
            rows.append({"kpi_id": kpi_id, "display_name": kpi["display_name"],
                         "theme": kpi["theme"], "n_present": 0, "n_missing": total,
                         "pct_present": 0.0, "pct_missing": 100.0})
            continue
        n_present = int(df[kpi_id].notna().sum())
        n_missing = total - n_present
        rows.append({
            "kpi_id": kpi_id,
            "display_name": kpi["display_name"],
            "theme": kpi["theme"],
            "n_present": n_present,
            "n_missing": n_missing,
            "pct_present": round(100 * n_present / total, 1) if total > 0 else 0.0,
            "pct_missing": round(100 * n_missing / total, 1) if total > 0 else 0.0,
        })
    return pd.DataFrame(rows)
