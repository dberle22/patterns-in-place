"""Tests for data_qa helper functions.

Integration tests use prod_con (skipped if DB absent).
Edge-case tests use in-memory DuckDB instances.
"""

import duckdb
import pandas as pd
import pytest

from retail_opportunity_finder.app.data_qa import (
    _ROF_GOLD_TABLES,
    _SCORE_COLS,
    _TRACT_FEATURE_COLS,
    parcel_geometry_coverage,
    score_coverage,
    table_inventory,
    tract_coverage,
    zone_build_coverage,
)

_MARKET_KEY = "jacksonville_fl"
_CBSA_CODE = "27260"  # Jacksonville-St. Augustine, FL


class TestTableInventory:
    def test_returns_dataframe(self, prod_con):
        assert isinstance(table_inventory(prod_con), pd.DataFrame)

    def test_has_expected_columns(self, prod_con):
        result = table_inventory(prod_con)
        assert set(result.columns) == {"table", "rows", "status"}

    def test_returns_all_tables(self, prod_con):
        result = table_inventory(prod_con)
        assert len(result) == len(_ROF_GOLD_TABLES)

    def test_all_tables_present(self, prod_con):
        result = table_inventory(prod_con)
        missing = result[result["status"] == "missing"]["table"].tolist()
        assert not missing, f"Missing tables: {missing}"

    def test_populated_tables_have_ok_status(self, prod_con):
        result = table_inventory(prod_con)
        non_user = result[result["table"] != "rof_gold.user_shortlist"]
        bad = non_user[non_user["status"] != "ok"]["table"].tolist()
        assert not bad, f"Non-ok status: {bad}"

    def test_missing_schema_gives_missing_status(self):
        con = duckdb.connect(":memory:")
        result = table_inventory(con)
        assert all(result["status"] == "missing")

    def test_empty_table_gives_empty_status(self):
        con = duckdb.connect(":memory:")
        con.execute("CREATE SCHEMA rof_gold")
        con.execute("CREATE TABLE rof_gold.market_profiles (id INTEGER)")
        result = table_inventory(con)
        mkt = result[result["table"] == "rof_gold.market_profiles"].iloc[0]
        assert mkt["status"] == "empty"
        assert mkt["rows"] == 0


class TestTractCoverage:
    def test_returns_dataframe(self, prod_con):
        assert isinstance(tract_coverage(prod_con, _CBSA_CODE), pd.DataFrame)

    def test_has_expected_columns(self, prod_con):
        result = tract_coverage(prod_con, _CBSA_CODE)
        assert set(result.columns) == {"metric", "total", "non_null", "null_count", "coverage_pct"}

    def test_row_count_equals_feature_cols_plus_tract_score(self, prod_con):
        result = tract_coverage(prod_con, _CBSA_CODE)
        assert len(result) == len(_TRACT_FEATURE_COLS) + 1

    def test_includes_tract_score_row(self, prod_con):
        result = tract_coverage(prod_con, _CBSA_CODE)
        assert "tract_score" in result["metric"].values

    def test_all_feature_cols_present(self, prod_con):
        result = tract_coverage(prod_con, _CBSA_CODE)
        assert set(_TRACT_FEATURE_COLS).issubset(set(result["metric"].values))

    def test_coverage_pct_in_range(self, prod_con):
        result = tract_coverage(prod_con, _CBSA_CODE)
        assert (result["coverage_pct"] >= 0).all()
        assert (result["coverage_pct"] <= 100).all()

    def test_non_null_plus_null_equals_total(self, prod_con):
        result = tract_coverage(prod_con, _CBSA_CODE)
        assert (result["non_null"] + result["null_count"] == result["total"]).all()

    def test_unknown_cbsa_returns_empty_dataframe(self, prod_con):
        result = tract_coverage(prod_con, "00000")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert set(result.columns) == {"metric", "total", "non_null", "null_count", "coverage_pct"}


class TestZoneBuildCoverage:
    def test_returns_dataframe(self, prod_con):
        assert isinstance(zone_build_coverage(prod_con, _MARKET_KEY), pd.DataFrame)

    def test_has_two_rows(self, prod_con):
        result = zone_build_coverage(prod_con, _MARKET_KEY)
        assert len(result) == 2

    def test_has_both_zone_systems(self, prod_con):
        result = zone_build_coverage(prod_con, _MARKET_KEY)
        assert set(result["zone_system"]) == {"cluster", "contiguity"}

    def test_has_expected_columns(self, prod_con):
        result = zone_build_coverage(prod_con, _MARKET_KEY)
        expected = {"zone_system", "total_tracts", "assigned", "unassigned", "coverage_pct", "note"}
        assert expected.issubset(set(result.columns))

    def test_coverage_pct_in_range(self, prod_con):
        result = zone_build_coverage(prod_con, _MARKET_KEY)
        assert (result["coverage_pct"] >= 0).all()
        assert (result["coverage_pct"] <= 100).all()

    def test_assigned_plus_unassigned_equals_total(self, prod_con):
        result = zone_build_coverage(prod_con, _MARKET_KEY)
        assert (result["assigned"] + result["unassigned"] == result["total_tracts"]).all()

    def test_assigned_not_greater_than_total(self, prod_con):
        result = zone_build_coverage(prod_con, _MARKET_KEY)
        assert (result["assigned"] <= result["total_tracts"]).all()

    def test_unknown_market_key_returns_empty(self, prod_con):
        result = zone_build_coverage(prod_con, "invalid_market_xyz")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestParcelGeometryCoverage:
    def test_returns_dataframe(self, prod_con):
        assert isinstance(parcel_geometry_coverage(prod_con), pd.DataFrame)

    def test_has_expected_columns(self, prod_con):
        result = parcel_geometry_coverage(prod_con)
        expected = {"county_name", "total_parcels", "with_geometry", "missing_geometry", "coverage_pct"}
        assert expected.issubset(set(result.columns))

    def test_has_multiple_counties(self, prod_con):
        result = parcel_geometry_coverage(prod_con)
        assert len(result) >= 2

    def test_coverage_pct_in_range(self, prod_con):
        result = parcel_geometry_coverage(prod_con)
        assert (result["coverage_pct"] >= 0).all()
        assert (result["coverage_pct"] <= 100).all()

    def test_with_plus_missing_equals_total(self, prod_con):
        result = parcel_geometry_coverage(prod_con)
        assert (result["with_geometry"] + result["missing_geometry"] == result["total_parcels"]).all()

    def test_all_total_parcels_positive(self, prod_con):
        result = parcel_geometry_coverage(prod_con)
        assert (result["total_parcels"] > 0).all()

    def test_ordered_by_county_name(self, prod_con):
        result = parcel_geometry_coverage(prod_con)
        names = list(result["county_name"])
        assert names == sorted(names)


class TestScoreCoverage:
    def test_returns_dataframe(self, prod_con):
        assert isinstance(score_coverage(prod_con, _MARKET_KEY), pd.DataFrame)

    def test_has_expected_columns(self, prod_con):
        result = score_coverage(prod_con, _MARKET_KEY)
        assert set(result.columns) == {"score", "total", "scored", "missing", "coverage_pct"}

    def test_has_one_row_per_score_col(self, prod_con):
        result = score_coverage(prod_con, _MARKET_KEY)
        assert len(result) == len(_SCORE_COLS)

    def test_all_score_cols_present(self, prod_con):
        result = score_coverage(prod_con, _MARKET_KEY)
        assert set(result["score"]) == set(_SCORE_COLS)

    def test_scored_plus_missing_equals_total(self, prod_con):
        result = score_coverage(prod_con, _MARKET_KEY)
        assert (result["scored"] + result["missing"] == result["total"]).all()

    def test_coverage_pct_in_range(self, prod_con):
        result = score_coverage(prod_con, _MARKET_KEY)
        assert (result["coverage_pct"] >= 0).all()
        assert (result["coverage_pct"] <= 100).all()

    def test_unknown_market_returns_empty_with_columns(self, prod_con):
        result = score_coverage(prod_con, "invalid_market_xyz")
        assert isinstance(result, pd.DataFrame)
        assert set(result.columns) == {"score", "total", "scored", "missing", "coverage_pct"}
        assert len(result) == 0
