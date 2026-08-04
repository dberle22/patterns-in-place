"""Normalize Jacksonville osmextract outputs into the standard spatial cache contract.

This keeps the provider-backed Jacksonville OSM run but reshapes it into the
same `osm_infrastructure_*` parquet layout that the app-facing prep code can
consume directly.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import duckdb
import geopandas as gpd
import pandas as pd


SECTION_ROOT = Path(__file__).resolve().parent
SOURCE_GPKG = SECTION_ROOT / "outputs" / "jacksonville_fl" / "raw" / "openstreetmap_fr_northeast-latest.gpkg"
TARGET_DIR = SECTION_ROOT / "outputs" / "jacksonville_fl"
MANIFEST_PATH = TARGET_DIR / "spatial_manifest.json"
MARKET_ID = "27260"
MARKET_SLUG = "jacksonville_fl"
SOURCE_PROVIDER = "openstreetmap_fr"

COMMON_COLUMNS = [
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

LINE_QUERY = (
    "SELECT * FROM lines "
    "WHERE highway IN ('motorway','motorway_link','trunk','trunk_link','primary','primary_link',"
    "'secondary','secondary_link','tertiary','tertiary_link') "
    "OR railway IN ('rail','light_rail','subway') "
    "OR waterway IN ('river','canal')"
)
POINT_QUERY = (
    "SELECT * FROM points "
    "WHERE aeroway IN ('aerodrome','terminal','helipad') "
    "OR harbour IS NOT NULL "
    "OR amenity = 'ferry_terminal' "
    "OR building = 'warehouse' "
    "OR office = 'logistics' "
    "OR industrial IN ('logistics','depot','port')"
)
POLYGON_QUERY = (
    "SELECT * FROM multipolygons "
    "WHERE aeroway IN ('aerodrome','terminal','runway','helipad') "
    "OR harbour IS NOT NULL "
    "OR landuse = 'port' "
    "OR natural = 'water' "
    "OR water IN ('river','canal','reservoir','lake') "
    "OR waterway = 'riverbank' "
    "OR industrial IN ('port','logistics','depot') "
    "OR amenity = 'ferry_terminal' "
    "OR building = 'warehouse' "
    "OR office = 'logistics'"
)


def _write_parquet(frame: pd.DataFrame, path: Path) -> None:
    """Write one normalized frame via DuckDB without adding a pyarrow dependency."""

    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    try:
        con.register("frame", frame)
        escaped_path = str(path).replace("'", "''")
        con.execute(f"COPY frame TO '{escaped_path}' (FORMAT PARQUET)")
    finally:
        con.close()


def _read_layer(query: str) -> gpd.GeoDataFrame:
    """Read one geometry family from the cached Jacksonville GeoPackage."""

    if not SOURCE_GPKG.exists():
        raise FileNotFoundError(f"Missing Jacksonville osmextract source: {SOURCE_GPKG}")
    return gpd.read_file(SOURCE_GPKG, sql=query)


def _classify_layer_group(row: pd.Series) -> str:
    """Map raw OSM tags into the D3 infrastructure families."""

    highway = row.get("highway")
    railway = row.get("railway")
    aeroway = row.get("aeroway")
    harbour = row.get("harbour")
    landuse = row.get("landuse")
    industrial = row.get("industrial")
    amenity = row.get("amenity")
    building = row.get("building")
    office = row.get("office")
    waterway = row.get("waterway")
    natural = row.get("natural")
    water = row.get("water")

    if highway in {"motorway", "motorway_link", "trunk", "trunk_link"}:
        return "highways"
    if highway in {"primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link"}:
        return "major_roads"
    if railway in {"rail", "light_rail", "subway"}:
        return "rail"
    if waterway in {"river", "canal"} or natural == "water" or water in {"river", "canal", "reservoir", "lake"}:
        return "water"
    if pd.notna(aeroway):
        return "airports"
    if pd.notna(harbour) or landuse == "port" or industrial == "port" or amenity == "ferry_terminal":
        return "ports"
    if building == "warehouse" or office == "logistics" or industrial in {"logistics", "depot"}:
        return "warehouses_logistics"
    return "other_infrastructure"


def _classify_subcategory(layer_group: str) -> str:
    """Keep the standard cache subcategory labels stable across geometry families."""

    return {
        "highways": "highway",
        "major_roads": "major_road",
        "rail": "rail",
        "water": "water",
        "airports": "airport",
        "ports": "port",
        "warehouses_logistics": "warehouse_logistics",
    }.get(layer_group, "infrastructure")


def _normalize_frame(frame: gpd.GeoDataFrame) -> pd.DataFrame:
    """Align one queried OSM layer to the standard cache schema."""

    if frame.empty:
        return pd.DataFrame(columns=COMMON_COLUMNS)

    frame = frame.to_crs(4326).copy()
    frame["layer_group"] = frame.apply(_classify_layer_group, axis=1)
    frame["subcategory"] = frame["layer_group"].map(_classify_subcategory)
    centroids = frame.geometry.centroid

    attribute_columns = [
        column
        for column in frame.columns
        if column not in {"geometry", "osm_id", "name", "layer_group", "subcategory"}
    ]
    attributes_json = []
    for _, row in frame[attribute_columns].iterrows():
        row_dict = {
            key: value
            for key, value in row.to_dict().items()
            if pd.notna(value) and value != ""
        }
        attributes_json.append(json.dumps(row_dict, sort_keys=True, default=str))

    normalized = pd.DataFrame(
        {
            "market_id": MARKET_ID,
            "source_system": "osm",
            "source_id": frame["osm_id"].astype(str),
            "feature_name": frame.get("name", "").fillna(""),
            "layer_group": frame["layer_group"],
            "category": "infrastructure",
            "subcategory": frame["subcategory"],
            "geometry_type": frame.geometry.geom_type,
            "geometry": frame.geometry.apply(lambda geom: json.dumps(geom.__geo_interface__)),
            "centroid_lat": centroids.y,
            "centroid_lon": centroids.x,
            "attributes_json": attributes_json,
            "extract_date": datetime.now(UTC).isoformat(timespec="seconds"),
        }
    )
    return normalized[COMMON_COLUMNS].copy()


def _merge_manifest(osm_layers: list[dict[str, object]], notes: list[str]) -> dict[str, object]:
    """Merge normalized OSM layers into the existing Jacksonville spatial manifest."""

    existing = {}
    if MANIFEST_PATH.exists():
        existing = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    kept_layers = [layer for layer in existing.get("layers", []) if layer.get("source") != "osm"]
    kept_notes = [note for note in existing.get("notes", []) if "OSM" not in str(note)]

    return {
        "market_id": existing.get("market_id", MARKET_ID),
        "bbox": existing.get("bbox"),
        "extract_date": datetime.now(UTC).isoformat(timespec="seconds"),
        "layers": kept_layers + osm_layers,
        "notes": kept_notes + notes,
    }


def _build_layer_manifest(frame: pd.DataFrame, geometry_type: str) -> list[dict[str, object]]:
    """Summarize one normalized OSM geometry family for the shared manifest."""

    if frame.empty:
        return []
    counts = (
        frame.groupby("layer_group", dropna=False)
        .size()
        .reset_index(name="row_count")
        .sort_values("row_count", ascending=False, kind="mergesort")
    )
    layers: list[dict[str, object]] = []
    for _, row in counts.iterrows():
        layers.append(
            {
                "source": "osm",
                "layer_name": row["layer_group"] or "unclassified",
                "geometry_type": geometry_type,
                "row_count": int(row["row_count"]),
                "query_config": {"method": "osmextract", "provider": SOURCE_PROVIDER},
                "notes_on_sparse_or_missing_layers": "",
            }
        )
    return layers


def main() -> int:
    """Read the cached Jacksonville GeoPackage and materialize standard OSM cache outputs."""

    lines = _normalize_frame(_read_layer(LINE_QUERY))
    points = _normalize_frame(_read_layer(POINT_QUERY))
    polygons = _normalize_frame(_read_layer(POLYGON_QUERY))

    _write_parquet(lines, TARGET_DIR / "osm_infrastructure_lines.parquet")
    _write_parquet(points, TARGET_DIR / "osm_infrastructure_points.parquet")
    _write_parquet(polygons, TARGET_DIR / "osm_infrastructure_polygons.parquet")

    notes = [
        "OSM infrastructure normalized from the Jacksonville osmextract GeoPackage.",
        f"OSM source path: {SOURCE_GPKG}",
        "Source footprint matched the Northeast Florida provider extract; review remains scoped to Jacksonville rings at analysis time.",
    ]
    manifest = _merge_manifest(
        _build_layer_manifest(lines, "line")
        + _build_layer_manifest(points, "point")
        + _build_layer_manifest(polygons, "polygon"),
        notes,
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "market_slug": MARKET_SLUG,
                "market_id": MARKET_ID,
                "line_rows": int(len(lines)),
                "point_rows": int(len(points)),
                "polygon_rows": int(len(polygons)),
                "target_dir": str(TARGET_DIR),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
