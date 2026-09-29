#!/usr/bin/env python3
"""Build simplified, display-only Q4 boundary and infrastructure context."""
from __future__ import annotations

import json
from pathlib import Path

import duckdb
from shapely import wkb
from shapely.geometry import mapping


MARKETS = {"40060": "richmond_va", "27260": "jacksonville_fl"}


def repo_root() -> Path:
    """Resolve repository-relative input paths without machine-specific paths."""
    return Path(__file__).resolve().parents[4]


def collection(rows, identifier: str, tolerance: float) -> dict:
    """Simplify source geometries only for a lightweight display derivative."""
    features = []
    for row in rows.itertuples(index=False):
        geometry = wkb.loads(bytes(row.geometry))
        geometry = geometry.simplify(tolerance, preserve_topology=True)
        properties = {"id": str(getattr(row, identifier))}
        if hasattr(row, "feature_group"):
            properties["feature_group"] = row.feature_group
        features.append({"type": "Feature", "properties": properties, "geometry": mapping(geometry)})
    return {"type": "FeatureCollection", "features": features}


def main() -> None:
    """Export no-method map context for the two Q4 pilot markets."""
    root = repo_root()
    database = root / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
    output = Path(__file__).parent / "outputs" / "q4_poi_workbench_v1" / "q4_map_context.json"
    context = {}
    with duckdb.connect(str(database), read_only=True) as con:
        for market_id, slug in MARKETS.items():
            tracts = con.execute("""
                SELECT t.tract_geoid, t.geom_wkb AS geometry
                FROM geo.tracts_all_us t
                JOIN mart_geography.rollup_county_to_cbsa r USING (county_geoid)
                WHERE r.cbsa_code = ? ORDER BY t.tract_geoid
            """, [market_id]).fetchdf()
            counties = con.execute("""
                SELECT c.county_geoid, c.geom_wkb AS geometry
                FROM geo.counties c
                JOIN mart_geography.rollup_county_to_cbsa r USING (county_geoid)
                WHERE r.cbsa_code = ? ORDER BY c.county_geoid
            """, [market_id]).fetchdf()
            infrastructure_path = next((root / "metro-deep-dive-program" / "engines" / "infrastructure" / "outputs" / slug).glob("*/validated/osm_core_v1/infrastructure_feature.parquet"))
            infrastructure = con.execute("""
                SELECT source_record_key, feature_group, geometry
                FROM read_parquet(?)
                WHERE feature_group IN ('rail', 'water_network')
                   OR (feature_group = 'road' AND feature_type IN ('motorway', 'trunk', 'primary'))
                ORDER BY feature_group, source_record_key
            """, [str(infrastructure_path)]).fetchdf()
            context[market_id] = {
                "tracts": collection(tracts, "tract_geoid", 0.001),
                "counties": collection(counties, "county_geoid", 0.002),
                "infrastructure": collection(infrastructure, "source_record_key", 0.0003),
            }
    output.write_text(json.dumps(context, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
