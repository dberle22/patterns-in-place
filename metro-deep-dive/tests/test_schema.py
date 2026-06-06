"""Tests that the rof_gold schema and key tables exist with expected structure.

Requires the production app database. Tests are skipped automatically if the
database file is not present (e.g., in CI without data).
"""

import pytest


_EXPECTED_TABLES = [
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

# Minimum expected row counts (conservative — actual counts may be higher)
_MIN_ROWS = {
    "market_profiles": 1,
    "cbsa_geometry": 1,
    "county_geometry": 4,
    "tract_geometry": 300,
    "tract_features": 300,
    "tract_scores": 300,
    "cluster_assignments": 50,
    "cluster_zone_summary": 8,
    "cluster_zone_geometries": 8,
    "contiguity_zone_summary": 20,
    "contiguity_zone_geometries": 20,
    "retail_parcels": 10_000,
    "parcel_geometry": 10_000,
    "parcel_shortlist": 5_000,
    "parcel_zone_overlay": 20,
    "retail_intensity_by_tract": 300,
    "retail_parcel_tract_assignment": 10_000,
    "user_shortlist": 0,  # starts empty — just verify it exists
}

# Key columns expected in each table (non-exhaustive)
_KEY_COLUMNS = {
    "market_profiles": {"market_key", "cbsa_code", "market_name"},
    "tract_geometry": {"cbsa_code", "tract_geoid", "geom_wkt"},
    "tract_features": {
        "cbsa_code", "tract_geoid", "pop_total", "median_hh_income",
        "gate_pop", "gate_price", "gate_density", "eligible_v1",
    },
    "tract_scores": {"cbsa_code", "tract_geoid", "tract_score", "is_scored"},
    "cluster_zone_summary": {
        "market_key", "cluster_id", "cluster_label", "mean_tract_score",
    },
    "parcel_shortlist": {
        "market_key", "zone_system", "parcel_uid", "parcel_id",
        "shortlist_score", "zone_quality_score", "parcel_characteristics_score",
    },
    "parcel_geometry": {"join_key", "geom_wkt", "centroid_lat", "centroid_lon", "area_sqmi"},
    "user_shortlist": {"parcel_uid", "market_key", "user_id", "status", "notes"},
}


@pytest.mark.parametrize("table", _EXPECTED_TABLES)
def test_table_exists(prod_con, table):
    count = prod_con.execute(f"SELECT COUNT(*) FROM rof_gold.{table}").fetchone()[0]
    assert count is not None, f"rof_gold.{table} is not accessible"


@pytest.mark.parametrize("table,min_rows", _MIN_ROWS.items())
def test_table_row_count(prod_con, table, min_rows):
    count = prod_con.execute(f"SELECT COUNT(*) FROM rof_gold.{table}").fetchone()[0]
    assert count >= min_rows, (
        f"rof_gold.{table} has {count} rows, expected >= {min_rows}"
    )


@pytest.mark.parametrize("table,columns", _KEY_COLUMNS.items())
def test_table_has_key_columns(prod_con, table, columns):
    result = prod_con.execute(f"SELECT * FROM rof_gold.{table} LIMIT 0").description
    actual_cols = {col[0] for col in result}
    missing = columns - actual_cols
    assert not missing, (
        f"rof_gold.{table} is missing expected columns: {missing}"
    )


def test_parcel_shortlist_has_both_zone_systems(prod_con):
    systems = prod_con.execute(
        "SELECT DISTINCT zone_system FROM rof_gold.parcel_shortlist"
    ).fetchall()
    system_set = {row[0] for row in systems}
    assert "cluster" in system_set
    assert "contiguity" in system_set


def test_parcel_geometry_join_key_matches_shortlist(prod_con):
    """parcel_id in parcel_shortlist should resolve in parcel_geometry."""
    unmatched = prod_con.execute(
        """
        SELECT COUNT(*) FROM rof_gold.parcel_shortlist ps
        LEFT JOIN rof_gold.parcel_geometry pg ON ps.parcel_id = pg.join_key
        WHERE ps.zone_system = 'cluster' AND pg.join_key IS NULL
        """
    ).fetchone()[0]
    total = prod_con.execute(
        "SELECT COUNT(*) FROM rof_gold.parcel_shortlist WHERE zone_system = 'cluster'"
    ).fetchone()[0]
    # Allow up to 5% unmatched (some parcels may legitimately lack geometry)
    assert unmatched / total < 0.05, (
        f"{unmatched}/{total} shortlist parcels have no geometry ({unmatched/total:.1%})"
    )


def test_tract_features_gate_values_are_binary(prod_con):
    invalid = prod_con.execute(
        """
        SELECT COUNT(*) FROM rof_gold.tract_features
        WHERE gate_pop NOT IN (0, 1)
           OR gate_price NOT IN (0, 1)
           OR gate_density NOT IN (0, 1)
           OR eligible_v1 NOT IN (0, 1)
        """
    ).fetchone()[0]
    assert invalid == 0, f"{invalid} rows have non-binary gate values"


def test_eligible_tracts_pass_all_gates(prod_con):
    """eligible_v1=1 should imply gate_pop=1 AND gate_price=1 AND gate_density=1."""
    inconsistent = prod_con.execute(
        """
        SELECT COUNT(*) FROM rof_gold.tract_features
        WHERE eligible_v1 = 1
          AND NOT (gate_pop = 1 AND gate_price = 1 AND gate_density = 1)
        """
    ).fetchone()[0]
    assert inconsistent == 0


def test_tract_scores_range(prod_con):
    result = prod_con.execute(
        "SELECT MIN(tract_score), MAX(tract_score) FROM rof_gold.tract_scores "
        "WHERE is_scored = true"
    ).fetchone()
    assert result[0] is not None
    assert -10 < result[0] < 10  # z-score based, so bounded


def test_shortlist_scores_in_unit_interval(prod_con):
    result = prod_con.execute(
        "SELECT MIN(shortlist_score), MAX(shortlist_score) FROM rof_gold.parcel_shortlist"
    ).fetchone()
    assert 0.0 <= result[0] <= 1.0
    assert 0.0 <= result[1] <= 1.0
