"""Data QA helper functions: table inventory, coverage summaries, and build freshness."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

_ROF_GOLD_TABLES = [
    "market_profiles",
    "cbsa_geometry",
    "county_geometry",
    "tract_geometry",
    "tract_features",
    "tract_scores",
    "cluster_assignments",
    "cluster_zone_summary",
    "cluster_zone_geometries",
    "contiguity_zone_summary",
    "contiguity_zone_geometries",
    "retail_parcels",
    "parcel_geometry",
    "parcel_shortlist",
    "parcel_zone_overlay",
    "retail_intensity_by_tract",
    "retail_parcel_tract_assignment",
    "user_shortlist",
]

_TRACT_FEATURE_COLS = [
    "pop_total",
    "pop_growth_3yr",
    "median_hh_income",
    "per_capita_income",
    "pov_rate",
    "median_gross_rent",
    "median_home_value",
    "pop_density",
    "units_per_1k_3yr",
]

_SCORE_COLS = [
    "shortlist_score",
    "zone_quality_score",
    "parcel_characteristics_score",
    "local_retail_context_score",
    "mean_tract_score",
]


def table_inventory(con) -> pd.DataFrame:
    """Returns row counts and status for all rof_gold tables."""
    rows = []
    for table in _ROF_GOLD_TABLES:
        try:
            n = con.execute(f"SELECT COUNT(*) FROM rof_gold.{table}").fetchone()[0]
            status = "ok" if n > 0 else "empty"
        except Exception:
            n = None
            status = "missing"
        rows.append({"table": f"rof_gold.{table}", "rows": n, "status": status})
    return pd.DataFrame(rows)


def tract_coverage(con, cbsa_code: str) -> pd.DataFrame:
    """Returns null rate per feature metric and tract_score for a given CBSA."""
    total = con.execute(
        "SELECT COUNT(*) FROM rof_gold.tract_features WHERE cbsa_code = ?",
        [cbsa_code],
    ).fetchone()[0]

    if total == 0:
        return pd.DataFrame(
            columns=["metric", "total", "non_null", "null_count", "coverage_pct"]
        )

    null_selects = ", ".join(
        f"SUM(CASE WHEN {c} IS NULL THEN 1 ELSE 0 END) AS {c}"
        for c in _TRACT_FEATURE_COLS
    )
    row = con.execute(
        f"SELECT {null_selects} FROM rof_gold.tract_features WHERE cbsa_code = ?",
        [cbsa_code],
    ).fetchone()

    records = []
    for i, col in enumerate(_TRACT_FEATURE_COLS):
        nulls = row[i]
        records.append(
            {
                "metric": col,
                "total": total,
                "non_null": total - nulls,
                "null_count": nulls,
                "coverage_pct": (total - nulls) / total * 100,
            }
        )

    # tract_score lives in tract_scores (separate table)
    score_null = con.execute(
        """
        SELECT COUNT(*) FROM rof_gold.tract_features tf
        LEFT JOIN rof_gold.tract_scores ts
            ON tf.cbsa_code = ts.cbsa_code AND tf.tract_geoid = ts.tract_geoid
        WHERE tf.cbsa_code = ? AND ts.tract_score IS NULL
        """,
        [cbsa_code],
    ).fetchone()[0]
    records.append(
        {
            "metric": "tract_score",
            "total": total,
            "non_null": total - score_null,
            "null_count": score_null,
            "coverage_pct": (total - score_null) / total * 100,
        }
    )

    return pd.DataFrame(records)


def zone_build_coverage(con, market_key: str) -> pd.DataFrame:
    """
    Returns tract assignment coverage per zone system.
    Cluster uses the cluster_assignments table (explicit mapping).
    Contiguity uses distinct tract_geoids from parcel_shortlist as a proxy.
    """
    cbsa_code = con.execute(
        "SELECT cbsa_code FROM rof_gold.market_profiles WHERE market_key = ?",
        [market_key],
    ).fetchone()
    if cbsa_code is None:
        return pd.DataFrame()
    cbsa_code = cbsa_code[0]

    total_tracts = con.execute(
        "SELECT COUNT(DISTINCT tract_geoid) FROM rof_gold.tract_geometry WHERE cbsa_code = ?",
        [cbsa_code],
    ).fetchone()[0]

    cluster_assigned = con.execute(
        "SELECT COUNT(DISTINCT tract_geoid) FROM rof_gold.cluster_assignments WHERE market_key = ?",
        [market_key],
    ).fetchone()[0]

    contiguity_tracts = con.execute(
        "SELECT COUNT(DISTINCT tract_geoid) FROM rof_gold.parcel_shortlist "
        "WHERE market_key = ? AND zone_system = 'contiguity'",
        [market_key],
    ).fetchone()[0]

    records = [
        {
            "zone_system": "cluster",
            "total_tracts": total_tracts,
            "assigned": cluster_assigned,
            "unassigned": total_tracts - cluster_assigned,
            "coverage_pct": cluster_assigned / total_tracts * 100 if total_tracts else 0,
            "note": "from cluster_assignments table",
        },
        {
            "zone_system": "contiguity",
            "total_tracts": total_tracts,
            "assigned": contiguity_tracts,
            "unassigned": total_tracts - contiguity_tracts,
            "coverage_pct": contiguity_tracts / total_tracts * 100 if total_tracts else 0,
            "note": "proxy via parcel_shortlist tract_geoids",
        },
    ]
    return pd.DataFrame(records)


def parcel_geometry_coverage(con) -> pd.DataFrame:
    """Returns county-level geometry match rates between retail_parcels and parcel_geometry."""
    return con.execute(
        """
        SELECT
            rp.county_name,
            COUNT(rp.parcel_uid)                                        AS total_parcels,
            COUNT(pg.join_key)                                          AS with_geometry,
            COUNT(rp.parcel_uid) - COUNT(pg.join_key)                   AS missing_geometry,
            ROUND(COUNT(pg.join_key) * 100.0 / COUNT(rp.parcel_uid), 1) AS coverage_pct
        FROM rof_gold.retail_parcels rp
        LEFT JOIN rof_gold.parcel_geometry pg ON rp.join_key = pg.join_key
        GROUP BY rp.county_name
        ORDER BY rp.county_name
        """
    ).df()


def score_coverage(con, market_key: str) -> pd.DataFrame:
    """Returns scored vs. null counts for each score column in parcel_shortlist (cluster)."""
    total = con.execute(
        "SELECT COUNT(*) FROM rof_gold.parcel_shortlist "
        "WHERE market_key = ? AND zone_system = 'cluster'",
        [market_key],
    ).fetchone()[0]

    if total == 0:
        return pd.DataFrame(
            columns=["score", "total", "scored", "missing", "coverage_pct"]
        )

    scored_selects = ", ".join(
        f"SUM(CASE WHEN {c} IS NOT NULL THEN 1 ELSE 0 END) AS {c}" for c in _SCORE_COLS
    )
    row = con.execute(
        f"SELECT {scored_selects} FROM rof_gold.parcel_shortlist "
        f"WHERE market_key = ? AND zone_system = 'cluster'",
        [market_key],
    ).fetchone()

    records = []
    for i, col in enumerate(_SCORE_COLS):
        scored = row[i]
        records.append(
            {
                "score": col,
                "total": total,
                "scored": scored,
                "missing": total - scored,
                "coverage_pct": scored / total * 100,
            }
        )
    return pd.DataFrame(records)
