"""Regression checks for state clipping without a local warehouse dependency.

Run from the repo root with .venv-marimo/bin/python -m unittest discover
-s metro-deep-dive-program/engines/infrastructure/qa -p 'test_*.py'.
"""

from pathlib import Path
import sys
import tempfile
import unittest

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from acquire_osm_infrastructure import core_source_sql, diagnostics, prepare_views, resolve_boundary, resolve_market, scalar_counts, source_columns
from validate_osm_infrastructure import qa_summary


class BoundaryScopeTests(unittest.TestCase):
    """Use distinct boundaries/vintages so a silent CBSA fallback cannot pass."""

    def setUp(self):
        self.con = duckdb.connect()
        self.con.execute("LOAD spatial")
        self.con.execute("CREATE SCHEMA geo; CREATE SCHEMA mart_geography")
        # The state identity vintage intentionally differs from its geometry:
        # a source manifest must describe the boundary actually used to clip.
        self.con.execute("""
            CREATE TABLE mart_geography.identity_current AS
            SELECT 'state' AS geo_level, '36' AS geo_id, 2020 AS boundary_vintage
            UNION ALL SELECT 'cbsa', '40060', 2023;
            CREATE TABLE mart_geography.geometry_catalog AS
            SELECT 'state' AS geo_level, 'states_analysis' AS table_name, 'analysis' AS geometry_role
            UNION ALL SELECT 'cbsa', 'cbsas_analysis', 'analysis';
            CREATE TABLE geo.states_analysis AS
            SELECT '36' AS state_fips, '2023' AS boundary_vintage,
                ST_GeomFromText('POLYGON((-80 40,-71 40,-71 45,-80 45,-80 40))') AS geom;
            CREATE TABLE geo.cbsas_analysis AS
            SELECT '40060' AS cbsa_code,
                ST_GeomFromText('POLYGON((-78 36,-76 36,-76 38,-78 38,-78 36))') AS geom;
        """)

    def tearDown(self):
        self.con.close()

    def test_state_uses_analytical_geometry_vintage(self):
        boundary = resolve_boundary(self.con, "36", "state")
        self.assertEqual(boundary["geo_level"], "state")
        self.assertEqual(boundary["boundary_vintage"], 2023)
        self.assertEqual(boundary["geometry_role"], "analysis")
        self.assertEqual((boundary["west"], boundary["north"]), (-80, 45))

    def test_existing_market_defaults_to_cbsa(self):
        boundary = resolve_boundary(self.con, "40060")
        self.assertEqual(boundary["geo_level"], "cbsa")
        self.assertEqual(boundary["boundary_vintage"], 2023)
        self.assertEqual((boundary["west"], boundary["north"]), (-78, 38))

    def test_missing_state_has_no_bbox_or_cbsa_fallback(self):
        with self.assertRaisesRegex(RuntimeError, "no current state geometry"):
            resolve_boundary(self.con, "99", "state")

    def test_state_clip_uses_boundary_and_caches_source_stages(self):
        source = """(SELECT 'lines' AS source_layer, '1' AS source_feature_id,
            NULL::VARCHAR AS source_name, 'road' AS source_group,
            'motorway' AS source_type, 'line' AS geometry_type,
            ST_AsWKB(ST_GeomFromText('LINESTRING(-81 42,-79 42)')) AS source_geometry_wkb,
            'geometry-1' AS source_geometry_id, '{}' AS source_tags)"""
        prepare_views(self.con, source, resolve_boundary(self.con, "36", "state"), "36", "test")
        self.assertEqual(scalar_counts(self.con)["retained_market"], 1)
        geometry, clipped = self.con.execute("""SELECT
            ST_AsText(ST_GeomFromWKB(geometry_wkb)), was_clipped FROM market_features""").fetchone()
        self.assertEqual(geometry, "LINESTRING (-80 42, -79 42)")
        self.assertTrue(clipped)

    def test_unsupported_scope_rejected_before_sql(self):
        market = dict(market_id="36", boundary_level="county", source_release="test",
                      provider="test", source_asset_uri="test", source_asset_path="test",
                      source_adapter_path="test")
        with self.assertRaisesRegex(ValueError, "cbsa or state"):
            resolve_market({"markets": {"test_market": market}}, "test_market")

    def test_polygon_way_identity_is_retained_without_relation_collision(self):
        import geopandas as gpd
        from shapely.geometry import LineString, box

        # A GDAL polygon way has a null osm_id, while a relation uses osm_id.
        # Equal numeric IDs belong to distinct OSM namespaces. A genuinely
        # missing identity must remain null for the rejection stream.
        with tempfile.TemporaryDirectory() as directory:
            adapter = Path(directory) / "source.gpkg"
            gpd.GeoDataFrame(
                {"osm_id": ["9"], "highway": ["residential"]},
                geometry=[LineString([(0, 0), (1, 1)])], crs=4326,
            ).to_file(adapter, layer="lines", driver="GPKG", GEOMETRY_NAME="geometry")
            gpd.GeoDataFrame(
                {"osm_id": ["7", None, None], "osm_way_id": [None, "7", None],
                 "water": ["river"] * 3}, geometry=[box(0, 0, 1, 1)] * 3, crs=4326,
            ).to_file(adapter, layer="multipolygons", driver="GPKG", GEOMETRY_NAME="geometry")
            query = core_source_sql(
                adapter, source_columns(self.con, adapter, "lines"),
                source_columns(self.con, adapter, "multipolygons"),
            )
            ids = self.con.execute(f"SELECT source_feature_id FROM {query}").fetchall()
            self.assertEqual({row[0] for row in ids}, {"7", "way:7", None})

    def test_metric_qa_uses_longitude_latitude_order(self):
        # This small NY rectangle is about 0.92 km². A silent authority-axis
        # swap measures a patch near 74 degrees south and fails this bound.
        self.con.execute("""
            CREATE TEMP VIEW bbox_candidates AS SELECT 'water_network' AS source_group,
                'river' AS source_type, 'polygon' AS geometry_type,
                'multipolygons' AS source_layer,
                ST_AsWKB(ST_GeomFromText(
                    'POLYGON((-74 42,-73.99 42,-73.99 42.01,-74 42.01,-74 42))'
                )) AS source_geometry_wkb;
            CREATE TEMP VIEW market_features AS SELECT *,
                source_geometry_wkb AS geometry_wkb, 'retained' AS record_status
                FROM bbox_candidates;
        """)
        area = diagnostics(self.con)[0]["clipped_polygon_area_sqm"]
        self.assertTrue(900_000 < area < 930_000, area)
        query = """SELECT record_status, 'valid' AS geometry_status,
            NULL::VARCHAR AS rejection_reason, source_group AS feature_group,
            source_type AS feature_type, 'surface' AS feature_form, geometry_type,
            'mapped' AS mapping_status, 'test' AS mapping_rule_id,
            '{}' AS source_tags, geometry_wkb AS geometry FROM market_features"""
        area = qa_summary(self.con, query, "EPSG:5070")["water_profile"][0]["area_sqm"]
        self.assertTrue(900_000 < area < 930_000, area)


if __name__ == "__main__":
    unittest.main()
