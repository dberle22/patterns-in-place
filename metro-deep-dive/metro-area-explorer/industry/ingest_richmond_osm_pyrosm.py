"""Richmond-first OSM infrastructure ingestion via pyrosm.

This path replaces the fragile live Overpass approach for metro-scale
infrastructure work. It downloads a covering `.osm.pbf` extract, parses it
locally with pyrosm, and writes cache outputs for D4 review.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path

import duckdb
import geopandas as gpd
import pandas as pd
from pyrosm import OSM, get_data_by_bbox

from ingest_spatial import build_manifest, get_market_bbox


SECTION_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = SECTION_ROOT / "outputs" / "richmond_va"
RAW_DIR = OUTPUT_DIR / "osm_raw"
MARKET_ID = "40060"

MAJOR_HIGHWAY_VALUES = {"motorway", "motorway_link", "trunk", "trunk_link"}
MAJOR_ROAD_VALUES = {
    "primary",
    "primary_link",
    "secondary",
    "secondary_link",
    "tertiary",
    "tertiary_link",
}


def _write_parquet(frame: pd.DataFrame, path: Path) -> None:
    """Write one frame to parquet via DuckDB without adding a direct pyarrow dependency."""
    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    try:
        con.register("frame", frame)
        escaped_path = str(path).replace("'", "''")
        con.execute(f"COPY frame TO '{escaped_path}' (FORMAT PARQUET)")
    finally:
        con.close()


def _merge_manifest(existing: dict | None, new_manifest: dict) -> dict:
    """Merge pyrosm-backed OSM results into an existing combined manifest if present."""
    if not existing:
        return new_manifest

    kept_layers = [layer for layer in existing.get("layers", []) if layer.get("source") != "osm"]
    kept_notes = [note for note in existing.get("notes", []) if "OSM" not in str(note)]
    return {
        "market_id": new_manifest["market_id"],
        "bbox": new_manifest["bbox"],
        "extract_date": new_manifest["extract_date"],
        "layers": kept_layers + new_manifest.get("layers", []),
        "notes": kept_notes + new_manifest.get("notes", []),
    }


def _parse_bbox_arg(bbox_text: str) -> tuple[float, float, float, float]:
    """Parse west,south,east,north bbox text."""
    parts = [float(value.strip()) for value in bbox_text.split(",")]
    if len(parts) != 4:
        raise ValueError("Expected bbox as west,south,east,north.")
    return parts[0], parts[1], parts[2], parts[3]


def _as_wgs84(frame: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Normalize CRS so cache outputs are stable and centroids are in lon/lat."""
    if frame.empty:
        return frame
    if frame.crs is None:
        frame = frame.set_crs(4326)
    elif frame.crs.to_epsg() != 4326:
        frame = frame.to_crs(4326)
    return frame


def _standardize_frame(
    frame: gpd.GeoDataFrame,
    *,
    layer_group: str,
    category: str,
    subcategory,
    extract_date: str,
) -> pd.DataFrame:
    """Convert a pyrosm GeoDataFrame into the shared cache schema."""
    if frame is None or frame.empty:
        return pd.DataFrame(
            columns=[
                "market_id",
                "source_system",
                "source_id",
                "feature_name",
                "layer_group",
                "category",
                "subcategory",
                "geometry_type",
                "geometry",
                "centroid_lat",
                "centroid_lon",
                "attributes_json",
                "extract_date",
            ]
        )

    frame = _as_wgs84(frame.copy())
    frame["centroid_lon"] = frame.geometry.centroid.x
    frame["centroid_lat"] = frame.geometry.centroid.y
    frame["geometry_type"] = frame.geometry.geom_type
    frame["geometry"] = frame.geometry.apply(lambda geom: json.dumps(geom.__geo_interface__))
    if "name" in frame.columns:
        frame["feature_name"] = frame["name"].fillna("")
    else:
        frame["feature_name"] = ""

    if "id" in frame.columns:
        frame["source_id"] = frame["id"].astype(str)
    else:
        frame["source_id"] = frame.index.astype(str)
    if callable(subcategory):
        frame["subcategory"] = frame.apply(subcategory, axis=1)
    else:
        frame["subcategory"] = subcategory

    attribute_columns = [col for col in frame.columns if col not in {"geometry"}]
    frame["attributes_json"] = frame[attribute_columns].apply(
        lambda row: json.dumps(
            {
                key: (
                    value.tolist()
                    if hasattr(value, "tolist")
                    else (None if pd.isna(value) else value)
                )
                for key, value in row.items()
                if key
                not in {
                    "market_id",
                    "source_system",
                    "source_id",
                    "feature_name",
                    "layer_group",
                    "category",
                    "subcategory",
                    "geometry_type",
                    "geometry",
                    "centroid_lat",
                    "centroid_lon",
                    "attributes_json",
                    "extract_date",
                }
            },
            sort_keys=True,
            default=str,
        ),
        axis=1,
    )
    frame["market_id"] = MARKET_ID
    frame["source_system"] = "osm"
    frame["layer_group"] = layer_group
    frame["category"] = category
    frame["extract_date"] = extract_date
    return frame[
        [
            "market_id",
            "source_system",
            "source_id",
            "feature_name",
            "layer_group",
            "category",
            "subcategory",
            "geometry_type",
            "geometry",
            "centroid_lat",
            "centroid_lon",
            "attributes_json",
            "extract_date",
        ]
    ].copy()


def _load_richmond_osm(bbox: tuple[float, float, float, float], refresh: bool) -> tuple[OSM, Path]:
    """Download or reuse the covering Richmond `.osm.pbf` extract and return an OSM parser."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    pbf_path = Path(
        get_data_by_bbox(
            list(bbox),
            crop=True,
            update=refresh,
            directory=str(RAW_DIR),
        )
    )
    osm = OSM(str(pbf_path), bounding_box=list(bbox))
    return osm, pbf_path


def _extract_driving_network(osm: OSM) -> gpd.GeoDataFrame:
    """Get the Richmond driving network with highway tags preserved."""
    return osm.get_network(
        network_type="driving",
        extra_attributes=["name", "highway", "maxspeed", "lanes", "oneway"],
        nodes=False,
    )


def _extract_rail(osm: OSM) -> gpd.GeoDataFrame:
    """Extract Richmond rail features as line geometry where available."""
    rail = osm.get_data_by_custom_criteria(
        custom_filter={"railway": ["rail", "light_rail", "subway"]},
        filter_type="keep",
        keep_nodes=False,
        keep_ways=True,
        keep_relations=False,
        extra_attributes=["name", "railway", "service", "usage"],
    )
    return rail if isinstance(rail, gpd.GeoDataFrame) else gpd.GeoDataFrame()


def _extract_airports(osm: OSM) -> gpd.GeoDataFrame:
    """Extract airport-related OSM features."""
    airport = osm.get_data_by_custom_criteria(
        custom_filter={"aeroway": ["aerodrome", "terminal", "runway", "helipad"]},
        filter_type="keep",
        keep_nodes=True,
        keep_ways=True,
        keep_relations=True,
        extra_attributes=["name", "aeroway", "iata", "icao"],
    )
    return airport if isinstance(airport, gpd.GeoDataFrame) else gpd.GeoDataFrame()


def _extract_ports(osm: OSM) -> gpd.GeoDataFrame:
    """Extract port and harbor-like OSM features."""
    port = osm.get_data_by_custom_criteria(
        custom_filter={
            "harbour": True,
            "landuse": ["port"],
            "industrial": ["port"],
            "amenity": ["ferry_terminal"],
        },
        filter_type="keep",
        keep_nodes=True,
        keep_ways=True,
        keep_relations=True,
        extra_attributes=["name", "harbour", "landuse", "industrial", "amenity"],
    )
    return port if isinstance(port, gpd.GeoDataFrame) else gpd.GeoDataFrame()


def _extract_warehouses(osm: OSM) -> gpd.GeoDataFrame:
    """Extract warehouse and logistics candidate features."""
    warehouse = osm.get_data_by_custom_criteria(
        custom_filter={
            "building": ["warehouse"],
            "office": ["logistics"],
            "industrial": ["logistics", "depot"],
        },
        filter_type="keep",
        keep_nodes=True,
        keep_ways=True,
        keep_relations=True,
        extra_attributes=["name", "building", "office", "industrial"],
    )
    return warehouse if isinstance(warehouse, gpd.GeoDataFrame) else gpd.GeoDataFrame()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI args for the Richmond pyrosm run."""
    parser = argparse.ArgumentParser(description="Extract Richmond OSM infrastructure via pyrosm.")
    parser.add_argument(
        "--bbox",
        help="Optional west,south,east,north override. If omitted, derive from Richmond tract geometry.",
    )
    parser.add_argument(
        "--refresh-pbf",
        action="store_true",
        help="Refresh the downloaded PBF extract instead of reusing the cached one.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the Richmond pyrosm extraction and update the combined manifest."""
    args = parse_args(argv)
    extract_date = datetime.now(UTC).isoformat(timespec="seconds")
    bbox = _parse_bbox_arg(args.bbox) if args.bbox else get_market_bbox(MARKET_ID)

    osm, pbf_path = _load_richmond_osm(bbox, refresh=args.refresh_pbf)
    driving = _extract_driving_network(osm)
    rail = _extract_rail(osm)
    airports = _extract_airports(osm)
    ports = _extract_ports(osm)
    warehouses = _extract_warehouses(osm)

    highways = driving[driving.get("highway").isin(MAJOR_HIGHWAY_VALUES)].copy()
    major_roads = driving[driving.get("highway").isin(MAJOR_ROAD_VALUES)].copy()

    line_frames = [
        _standardize_frame(highways, layer_group="highways", category="infrastructure", subcategory="highway", extract_date=extract_date),
        _standardize_frame(major_roads, layer_group="major_roads", category="infrastructure", subcategory="major_road", extract_date=extract_date),
        _standardize_frame(rail, layer_group="rail", category="infrastructure", subcategory="rail", extract_date=extract_date),
    ]
    feature_frames = [
        _standardize_frame(airports, layer_group="airports", category="infrastructure", subcategory=lambda row: row.get("aeroway", "airport"), extract_date=extract_date),
        _standardize_frame(ports, layer_group="ports", category="infrastructure", subcategory="port", extract_date=extract_date),
        _standardize_frame(warehouses, layer_group="warehouses_logistics", category="infrastructure", subcategory="warehouse_logistics", extract_date=extract_date),
    ]

    lines = pd.concat(line_frames, ignore_index=True) if line_frames else pd.DataFrame()
    features = pd.concat(feature_frames, ignore_index=True) if feature_frames else pd.DataFrame()
    polygons = features[features["geometry_type"].isin(["Polygon", "MultiPolygon"])].copy()
    points = features[features["geometry_type"].isin(["Point", "MultiPoint"])].copy()
    extra_lines = features[features["geometry_type"].isin(["LineString", "MultiLineString"])].copy()
    if not extra_lines.empty:
        lines = pd.concat([lines, extra_lines], ignore_index=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_parquet(lines, OUTPUT_DIR / "osm_infrastructure_lines.parquet")
    _write_parquet(polygons, OUTPUT_DIR / "osm_infrastructure_polygons.parquet")
    _write_parquet(points, OUTPUT_DIR / "osm_infrastructure_points.parquet")

    manifest = build_manifest(
        market_id=MARKET_ID,
        bbox=bbox,
        extract_date=extract_date,
        layers=[
            {
                "source": "osm",
                "layer_name": "highways",
                "geometry_type": "line",
                "row_count": int((lines["layer_group"] == "highways").sum()) if not lines.empty else 0,
                "query_config": {"method": "pyrosm.get_network", "filter": sorted(MAJOR_HIGHWAY_VALUES)},
                "notes_on_sparse_or_missing_layers": "",
            },
            {
                "source": "osm",
                "layer_name": "major_roads",
                "geometry_type": "line",
                "row_count": int((lines["layer_group"] == "major_roads").sum()) if not lines.empty else 0,
                "query_config": {"method": "pyrosm.get_network", "filter": sorted(MAJOR_ROAD_VALUES)},
                "notes_on_sparse_or_missing_layers": "",
            },
            {
                "source": "osm",
                "layer_name": "rail",
                "geometry_type": "line",
                "row_count": int((lines["layer_group"] == "rail").sum()) if not lines.empty else 0,
                "query_config": {"method": "pyrosm.get_data_by_custom_criteria", "filter": {"railway": ["rail", "light_rail", "subway"]}},
                "notes_on_sparse_or_missing_layers": "",
            },
            {
                "source": "osm",
                "layer_name": "airports",
                "geometry_type": "mixed",
                "row_count": int((features["layer_group"] == "airports").sum()) if not features.empty else 0,
                "query_config": {"method": "pyrosm.get_data_by_custom_criteria", "filter": {"aeroway": ["aerodrome", "terminal", "runway", "helipad"]}},
                "notes_on_sparse_or_missing_layers": "",
            },
            {
                "source": "osm",
                "layer_name": "ports",
                "geometry_type": "mixed",
                "row_count": int((features["layer_group"] == "ports").sum()) if not features.empty else 0,
                "query_config": {"method": "pyrosm.get_data_by_custom_criteria", "filter": {"harbour": True, "landuse": ["port"], "industrial": ["port"], "amenity": ["ferry_terminal"]}},
                "notes_on_sparse_or_missing_layers": "",
            },
            {
                "source": "osm",
                "layer_name": "warehouses_logistics",
                "geometry_type": "mixed",
                "row_count": int((features["layer_group"] == "warehouses_logistics").sum()) if not features.empty else 0,
                "query_config": {"method": "pyrosm.get_data_by_custom_criteria", "filter": {"building": ["warehouse"], "office": ["logistics"], "industrial": ["logistics", "depot"]}},
                "notes_on_sparse_or_missing_layers": "",
            },
        ],
        notes=[f"pyrosm source PBF: {pbf_path.name}"],
    )

    manifest_path = OUTPUT_DIR / "spatial_manifest.json"
    existing_manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
    merged_manifest = _merge_manifest(existing_manifest, manifest)
    manifest_path.write_text(json.dumps(merged_manifest, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "market_slug": "richmond_va",
                "market_id": MARKET_ID,
                "bbox": bbox,
                "pbf_path": str(pbf_path),
                "line_rows": int(len(lines)),
                "polygon_rows": int(len(polygons)),
                "point_rows": int(len(points)),
                "output_dir": str(OUTPUT_DIR),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
