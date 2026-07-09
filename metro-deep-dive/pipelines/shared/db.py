"""
DuckDB connection for metro-deep-dive market .qmd files.

Stub — flesh this out as the first market section needs it.
Pattern mirrors area-explorer/shared/db.py but scoped to mart_deep_dive.
"""
from __future__ import annotations
from pathlib import Path
import duckdb

# Repo root is three levels up from this file: pipelines/shared/db.py
REPO_ROOT = Path(__file__).resolve().parents[3]

# Intelligence parquet views — mirrors area-explorer/shared/db.py
INTELLIGENCE_PARQUETS = {
    "intelligence_character":   "exploration/intelligence_framework/phase_2_character_calibration/outputs/character_scores.parquet",
    "intelligence_livability":  "exploration/intelligence_framework/phase_3_livability_calibration/outputs/livability_scores.parquet",
    "intelligence_opportunity": "exploration/intelligence_framework/phase_4_opportunity_calibration/outputs/opportunity_scores.parquet",
    "intelligence_cross_frame": "exploration/intelligence_framework/phase_5_cross_frame_integration/outputs/cross_frame_scores.parquet",
}

# Phase 6 trajectory outputs
TRAJECTORY_PARQUETS = {
    "trajectory_scores":    "exploration/intelligence_framework/phase_6_trajectory/outputs/trajectory_scores.parquet",
    "phase6_candidate_list":"exploration/intelligence_framework/phase_6_trajectory/outputs/phase6_candidate_list.csv",
    "phase6_kpi_trajectory":"exploration/intelligence_framework/phase_6_trajectory/outputs/phase6_kpi_trajectory_long.csv",
    "phase6_turn_signals":  "exploration/intelligence_framework/phase_6_trajectory/outputs/phase6_opp_turn_signals.csv",
}


def get_conn() -> duckdb.DuckDBPyConnection:
    """Open an in-memory DuckDB connection with all standard views registered."""
    conn = duckdb.connect()
    conn.execute("CREATE SCHEMA IF NOT EXISTS mart_deep_dive")

    for view_name, rel_path in {**INTELLIGENCE_PARQUETS, **TRAJECTORY_PARQUETS}.items():
        full_path = REPO_ROOT / rel_path
        if full_path.exists():
            if rel_path.endswith(".parquet"):
                conn.execute(f"CREATE VIEW {view_name} AS SELECT * FROM read_parquet('{full_path}')")
            else:
                conn.execute(f"CREATE VIEW {view_name} AS SELECT * FROM read_csv_auto('{full_path}')")

    return conn
