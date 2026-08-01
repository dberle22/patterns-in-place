"""Market-parameterized OSM and Overture ingestion for Industry D4.

This script is intentionally separate from `data_prep.py`. Its job is to
extract and cache spatial layers that the app can read later without live
network calls. The first pass keeps OSM as the infrastructure source and
Overture as the first-class place/POI source.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, UTC
import json
from pathlib import Path
import sys
from typing import Iterable
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import duckdb
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
SECTION_ROOT = Path(__file__).resolve().parent
OUTPUTS_ROOT = SECTION_ROOT / "outputs"
DB_PATH = REPO_ROOT / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
DEFAULT_MARKET_ID = "40060"
DEFAULT_OVERPASS_URL = "https://overpass-api.de/api/interpreter"

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


@dataclass(frozen=True)
class OSMQueryConfig:
    """Describe one OSM extraction layer and the tag filters behind it."""

    layer_group: str
    category: str
    subcategory: str
    selectors: tuple[str, ...]


OSM_QUERY_CONFIGS = (
    OSMQueryConfig(
        layer_group="highways",
        category="infrastructure",
        subcategory="highway",
        selectors=(
            'way["highway"~"motorway|motorway_link|trunk|trunk_link"]({bbox});',
        ),
    ),
    OSMQueryConfig(
        layer_group="major_roads",
        category="infrastructure",
        subcategory="major_road",
        selectors=(
            'way["highway"~"primary|primary_link|secondary|secondary_link|tertiary|tertiary_link"]({bbox});',
        ),
    ),
    OSMQueryConfig(
        layer_group="rail",
        category="infrastructure",
        subcategory="rail",
        selectors=(
            'way["railway"~"rail|light_rail|subway"]({bbox});',
        ),
    ),
    OSMQueryConfig(
        layer_group="airports",
        category="infrastructure",
        subcategory="airport",
        selectors=(
            'nwr["aeroway"~"aerodrome|terminal|runway|helipad"]({bbox});',
        ),
    ),
    OSMQueryConfig(
        layer_group="ports",
        category="infrastructure",
        subcategory="port",
        selectors=(
            'nwr["harbour"]({bbox});',
            'nwr["landuse"="port"]({bbox});',
            'nwr["industrial"="port"]({bbox});',
            'nwr["amenity"="ferry_terminal"]({bbox});',
        ),
    ),
    OSMQueryConfig(
        layer_group="warehouses_logistics",
        category="infrastructure",
        subcategory="warehouse_logistics",
        selectors=(
            'nwr["building"="warehouse"]({bbox});',
            'nwr["office"="logistics"]({bbox});',
            'nwr["industrial"~"logistics|depot"]({bbox});',
        ),
    ),
)


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open the shared repo DuckDB in read-only mode."""
    return duckdb.connect(str(DB_PATH), read_only=True)


def _load_spatial(con: duckdb.DuckDBPyConnection) -> None:
    """Load DuckDB spatial helpers for geometry export."""
    con.execute("LOAD spatial;")


def _iter_geometry_points(geometry: dict | list | None):
    """Yield lon/lat pairs from nested GeoJSON-like coordinates."""
    if geometry is None:
        return
    if isinstance(geometry, dict):
        yield from _iter_geometry_points(geometry.get("coordinates"))
        return
    if isinstance(geometry, list):
        if geometry and isinstance(geometry[0], (int, float)) and len(geometry) >= 2:
            yield float(geometry[0]), float(geometry[1])
            return
        for value in geometry:
            yield from _iter_geometry_points(value)


def _geometry_centroid(geometry: dict | None) -> tuple[float | None, float | None]:
    """Approximate a centroid by taking the midpoint of the geometry bounds."""
    lons: list[float] = []
    lats: list[float] = []
    for lon, lat in _iter_geometry_points(geometry):
        lons.append(lon)
        lats.append(lat)
    if not lons or not lats:
        return None, None
    return (min(lons) + max(lons)) / 2, (min(lats) + max(lats)) / 2


def get_market_bbox(market_id: str, buffer_degrees: float = 0.05) -> tuple[float, float, float, float]:
    """Derive a market bounding box from tract geometry in the shared DuckDB."""
    con = get_connection()
    try:
        _load_spatial(con)
        rows = con.execute(
            """
            WITH market_counties AS (
                SELECT DISTINCT county_geoid
                FROM patterns_in_place.silver.xwalk_cbsa_county
                WHERE cbsa_code = ?
            )
            SELECT
                ST_AsGeoJSON(g.geom) AS geometry_json
            FROM patterns_in_place.geo.tracts_all_us g
            INNER JOIN market_counties c
                ON g.county_geoid = c.county_geoid
            """,
            [str(market_id)],
        ).fetchall()
    finally:
        con.close()

    lons: list[float] = []
    lats: list[float] = []
    for (geometry_json,) in rows:
        geometry = json.loads(geometry_json)
        for lon, lat in _iter_geometry_points(geometry):
            lons.append(lon)
            lats.append(lat)

    if not lons or not lats:
        raise ValueError(f"Could not derive a tract-based bounding box for market {market_id}.")

    return (
        min(lons) - buffer_degrees,
        min(lats) - buffer_degrees,
        max(lons) + buffer_degrees,
        max(lats) + buffer_degrees,
    )


def _bbox_string(bbox: tuple[float, float, float, float]) -> str:
    """Format bbox in the south,west,north,east order Overpass expects."""
    west, south, east, north = bbox
    return f"{south},{west},{north},{east}"


def _split_bbox(
    bbox: tuple[float, float, float, float],
    cols: int = 3,
    rows: int = 3,
) -> list[tuple[float, float, float, float]]:
    """Split a large metro bbox into smaller tiles for Overpass stability."""
    west, south, east, north = bbox
    lon_step = (east - west) / cols
    lat_step = (north - south) / rows
    tiles: list[tuple[float, float, float, float]] = []
    for row_idx in range(rows):
        for col_idx in range(cols):
            tile_west = west + col_idx * lon_step
            tile_east = east if col_idx == cols - 1 else west + (col_idx + 1) * lon_step
            tile_south = south + row_idx * lat_step
            tile_north = north if row_idx == rows - 1 else south + (row_idx + 1) * lat_step
            tiles.append((tile_west, tile_south, tile_east, tile_north))
    return tiles


def _geometry_from_osm_element(element: dict) -> tuple[str | None, dict | None]:
    """Normalize one Overpass element into a GeoJSON geometry."""
    element_type = element.get("type")
    if element_type == "node":
        lon = element.get("lon")
        lat = element.get("lat")
        if lon is None or lat is None:
            return None, None
        return "Point", {"type": "Point", "coordinates": [lon, lat]}

    geometry_points = element.get("geometry")
    if not geometry_points:
        return None, None

    coordinates = [[point["lon"], point["lat"]] for point in geometry_points]
    is_closed = len(coordinates) >= 4 and coordinates[0] == coordinates[-1]
    tags = element.get("tags", {})

    if element_type == "way":
        if is_closed and not tags.get("highway") and not tags.get("railway"):
            return "Polygon", {"type": "Polygon", "coordinates": [coordinates]}
        return "LineString", {"type": "LineString", "coordinates": coordinates}

    return "LineString", {"type": "LineString", "coordinates": coordinates}


def _request_overpass(query: str, overpass_url: str) -> dict:
    """POST one Overpass query and return the parsed JSON payload."""
    payload = urlencode({"data": query}).encode("utf-8")
    request = Request(
        overpass_url,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Accept": "application/json",
            "User-Agent": "patterns-in-place-codex/1.0 (Richmond D4 research)",
        },
        method="POST",
    )
    with urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def _build_osm_query(config: OSMQueryConfig, bbox: tuple[float, float, float, float]) -> str:
    """Render one Overpass QL query from the config and bbox."""
    bbox_text = _bbox_string(bbox)
    selector_text = "\n".join(selector.format(bbox=bbox_text) for selector in config.selectors)
    return f"""
[out:json][timeout:120];
(
{selector_text}
);
out body geom;
""".strip()


def fetch_osm_infrastructure(
    market_id: str,
    bbox: tuple[float, float, float, float],
    extract_date: str,
    overpass_url: str = DEFAULT_OVERPASS_URL,
    query_configs: Iterable[OSMQueryConfig] | None = None,
) -> tuple[dict[str, pd.DataFrame], list[dict[str, object]], list[str]]:
    """Extract OSM infrastructure layers and split them by geometry family.

    The default behavior runs every configured infrastructure layer. Callers can
    pass a smaller config subset for faster sample runs or one-layer debugging.
    """
    record_buckets = {"Point": [], "LineString": [], "Polygon": []}
    manifest_layers: list[dict[str, object]] = []
    notes: list[str] = []
    tiles = _split_bbox(bbox)
    active_configs = tuple(query_configs) if query_configs is not None else OSM_QUERY_CONFIGS

    for config in active_configs:
        layer_counts = {"Point": 0, "LineString": 0, "Polygon": 0}
        seen_ids: set[str] = set()
        tile_errors: list[str] = []
        for tile_idx, tile_bbox in enumerate(tiles, start=1):
            query = _build_osm_query(config, tile_bbox)
            try:
                payload = _request_overpass(query, overpass_url)
            except URLError as exc:
                tile_errors.append(f"tile {tile_idx}: {exc}")
                continue

            for element in payload.get("elements", []):
                source_id = f"osm:{element.get('type', 'element')}:{element.get('id')}"
                if source_id in seen_ids:
                    continue
                geometry_type, geometry = _geometry_from_osm_element(element)
                if geometry is None or geometry_type is None:
                    continue
                seen_ids.add(source_id)
                centroid_lon, centroid_lat = _geometry_centroid(geometry)
                record_buckets[geometry_type].append(
                    {
                        "market_id": str(market_id),
                        "source_system": "osm",
                        "source_id": source_id,
                        "feature_name": element.get("tags", {}).get("name", ""),
                        "layer_group": config.layer_group,
                        "category": config.category,
                        "subcategory": config.subcategory,
                        "geometry_type": geometry_type,
                        "geometry": json.dumps(geometry),
                        "centroid_lat": centroid_lat,
                        "centroid_lon": centroid_lon,
                        "attributes_json": json.dumps(element.get("tags", {}), sort_keys=True),
                        "extract_date": extract_date,
                    }
                )
                layer_counts[geometry_type] += 1

        for geometry_type, count in layer_counts.items():
            manifest_layers.append(
                {
                    "source": "osm",
                    "layer_name": config.layer_group,
                    "geometry_type": geometry_type.lower(),
                    "row_count": count,
                    "query_config": {"selectors": list(config.selectors), "tile_count": len(tiles)},
                    "notes_on_sparse_or_missing_layers": (
                        "; ".join(tile_errors)
                        if tile_errors
                        else ("" if count else "No matching OSM features returned.")
                    ),
                }
            )
        if tile_errors and not any(layer_counts.values()):
            notes.append(f"OSM layer {config.layer_group} failed across tiled requests: {'; '.join(tile_errors)}.")

    return (
        {
            "points": _normalize_output_frame(pd.DataFrame.from_records(record_buckets["Point"])),
            "lines": _normalize_output_frame(pd.DataFrame.from_records(record_buckets["LineString"])),
            "polygons": _normalize_output_frame(pd.DataFrame.from_records(record_buckets["Polygon"])),
        },
        manifest_layers,
        notes,
    )


def _normalize_output_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Align one extracted frame to the shared cache schema."""
    if frame.empty:
        return pd.DataFrame(columns=COMMON_COLUMNS)
    for column in COMMON_COLUMNS:
        if column not in frame.columns:
            frame[column] = None
    return frame[COMMON_COLUMNS].copy()


def _json_safe_value(value):
    """Normalize DuckDB/Pandas nested values into JSON-serializable Python values."""
    if value is None:
        return None
    if hasattr(value, "tolist"):
        return value.tolist()
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    return value


def _overture_sql(path_or_glob: str) -> str:
    """Return the DuckDB query used for Overture place extraction.

    The script keeps Overture first-class but does not hardcode a release. Pass
    a local or remote parquet/glob path that resolves to Overture Places.
    """
    return f"""
    SELECT
        id AS source_id,
        names.primary AS feature_name,
        categories.primary AS primary_category,
        basic_category,
        taxonomy.primary AS taxonomy_primary,
        taxonomy.hierarchy AS taxonomy_hierarchy,
        confidence,
        addresses[1].freeform AS address_freeform,
        ST_AsGeoJSON(geometry) AS geometry_json
    FROM read_parquet('{path_or_glob}', hive_partitioning = 1)
    WHERE bbox.xmin <= ?
      AND bbox.xmax >= ?
      AND bbox.ymin <= ?
      AND bbox.ymax >= ?
    """


def _categorize_overture_place(
    primary_category: str,
    basic_category: str,
    taxonomy_primary: str,
) -> tuple[str, str]:
    """Map Overture primary categories into the first-pass D4 taxonomy."""
    primary_value = (primary_category or "").lower()
    basic_value = (basic_category or "").lower()
    taxonomy_value = (taxonomy_primary or "").lower()
    category_values = " ".join([primary_value, basic_value, taxonomy_value])

    if any(token in category_values for token in ["airport", "aerodrome", "terminal"]):
        return "infrastructure", "airport"
    if any(token in category_values for token in ["port", "harbor", "ferry"]):
        return "infrastructure", "port"
    if any(token in category_values for token in ["warehouse", "distribution", "logistics", "industrial"]):
        return "infrastructure", "warehouse_logistics"
    if "hospital" in category_values:
        return "amenity", "hospital"
    grocery_values = {
        "farmers_market",
        "grocery_store",
        "health_food_store",
        "international_grocery_store",
        "specialty_grocery_store",
        "supermarket",
    }
    if primary_value in grocery_values or taxonomy_value in grocery_values:
        return "amenity", "grocery"
    if any(token in category_values for token in ["university", "college"]):
        return "amenity", "university"
    if "school" in category_values:
        return "amenity", "school"
    return "poi", (basic_category or taxonomy_primary or primary_category or "place")


def fetch_overture_pois(
    market_id: str,
    bbox: tuple[float, float, float, float],
    extract_date: str,
    overture_path: str | None,
) -> tuple[pd.DataFrame, list[dict[str, object]], list[str]]:
    """Extract Overture place records for the market bbox when a path is configured."""
    manifest_layers: list[dict[str, object]] = []
    notes: list[str] = []

    if not overture_path:
        notes.append("Skipping Overture: no parquet path or release glob was provided.")
        return pd.DataFrame(columns=COMMON_COLUMNS), manifest_layers, notes

    west, south, east, north = bbox
    con = duckdb.connect()
    try:
        try:
            con.execute("LOAD spatial;")
        except duckdb.Error:
            con.execute("INSTALL spatial;")
            con.execute("LOAD spatial;")
        if overture_path.startswith("http") or overture_path.startswith("s3://"):
            try:
                con.execute("LOAD httpfs;")
            except duckdb.Error:
                con.execute("INSTALL httpfs;")
                con.execute("LOAD httpfs;")
            if overture_path.startswith("http"):
                con.execute("SET allow_asterisks_in_http_paths = true;")
            if overture_path.startswith("s3://"):
                con.execute("SET s3_region = 'us-west-2';")

        rows = con.execute(
            _overture_sql(overture_path),
            [east, west, north, south],
        ).fetchdf()
    finally:
        con.close()

    if rows.empty:
        manifest_layers.append(
            {
                "source": "overture",
                "layer_name": "overture_pois",
                "geometry_type": "point_or_polygon",
                "row_count": 0,
                "query_config": {"path": overture_path},
                "notes_on_sparse_or_missing_layers": "No Overture places matched the bbox query.",
            }
        )
        return pd.DataFrame(columns=COMMON_COLUMNS), manifest_layers, notes

    records = []
    for _, row in rows.iterrows():
        geometry = json.loads(row["geometry_json"]) if row.get("geometry_json") else None
        centroid_lon, centroid_lat = _geometry_centroid(geometry)
        category, subcategory = _categorize_overture_place(
            row.get("primary_category"),
            row.get("basic_category"),
            row.get("taxonomy_primary"),
        )
        records.append(
            {
                "market_id": str(market_id),
                "source_system": "overture",
                "source_id": row.get("source_id", ""),
                "feature_name": row.get("feature_name", "") or "",
                "layer_group": "overture_pois",
                "category": category,
                "subcategory": subcategory,
                "geometry_type": geometry.get("type") if geometry else "",
                "geometry": json.dumps(geometry) if geometry else "",
                "centroid_lat": centroid_lat,
                "centroid_lon": centroid_lon,
                "attributes_json": json.dumps(
                    {
                        "primary_category": row.get("primary_category", ""),
                        "basic_category": row.get("basic_category", ""),
                        "taxonomy_primary": row.get("taxonomy_primary", ""),
                        "taxonomy_hierarchy": _json_safe_value(row.get("taxonomy_hierarchy", [])) or [],
                        "confidence": _json_safe_value(row.get("confidence")),
                        "address_freeform": row.get("address_freeform", ""),
                    },
                    sort_keys=True,
                ),
                "extract_date": extract_date,
            }
        )

    frame = _normalize_output_frame(pd.DataFrame.from_records(records))
    manifest_layers.append(
        {
            "source": "overture",
            "layer_name": "overture_pois",
            "geometry_type": "mixed",
            "row_count": int(len(frame)),
            "query_config": {"path": overture_path},
            "notes_on_sparse_or_missing_layers": "",
        }
    )
    return frame, manifest_layers, notes


def _write_parquet(frame: pd.DataFrame, path: Path) -> None:
    """Write one cached frame to parquet via DuckDB."""
    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    try:
        con.register("frame", frame)
        escaped_path = str(path).replace("'", "''")
        con.execute(f"COPY frame TO '{escaped_path}' (FORMAT PARQUET)")
    finally:
        con.close()


def write_cache_outputs(
    market_id: str,
    frames: dict[str, pd.DataFrame],
    manifest: dict[str, object],
) -> None:
    """Write the market cache outputs expected by the D4 app layer."""
    output_dir = OUTPUTS_ROOT / str(market_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_parquet(frames["osm_lines"], output_dir / "osm_infrastructure_lines.parquet")
    _write_parquet(frames["osm_polygons"], output_dir / "osm_infrastructure_polygons.parquet")
    _write_parquet(frames["osm_points"], output_dir / "osm_infrastructure_points.parquet")
    _write_parquet(frames["overture_pois"], output_dir / "overture_pois.parquet")

    manifest_path = output_dir / "spatial_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)


def _parse_bbox_arg(bbox_text: str) -> tuple[float, float, float, float]:
    """Parse a comma-separated west,south,east,north bbox string."""
    parts = [float(value.strip()) for value in bbox_text.split(",")]
    if len(parts) != 4:
        raise ValueError("Expected bbox as west,south,east,north.")
    return parts[0], parts[1], parts[2], parts[3]


def build_manifest(
    market_id: str,
    bbox: tuple[float, float, float, float],
    extract_date: str,
    layers: list[dict[str, object]],
    notes: Iterable[str],
) -> dict[str, object]:
    """Create the reproducible manifest written beside the cached outputs."""
    return {
        "market_id": str(market_id),
        "bbox": {
            "west": bbox[0],
            "south": bbox[1],
            "east": bbox[2],
            "north": bbox[3],
        },
        "extract_date": extract_date,
        "layers": layers,
        "notes": list(notes),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the CLI arguments for one market extraction run."""
    parser = argparse.ArgumentParser(description="Cache D4 OSM and Overture overlays for one market.")
    parser.add_argument("--market-id", default=DEFAULT_MARKET_ID, help="CBSA market id, default = Richmond (40060).")
    parser.add_argument(
        "--bbox",
        help="Optional west,south,east,north bbox override. If omitted, derive bbox from tract geometry.",
    )
    parser.add_argument(
        "--overture-path",
        help="Optional local or remote parquet/glob path for Overture Places. Required if Overture extraction should run.",
    )
    parser.add_argument("--overpass-url", default=DEFAULT_OVERPASS_URL, help="Overpass endpoint URL.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run one market extraction and write the app-local D4 cache outputs."""
    args = parse_args(argv)
    extract_date = datetime.now(UTC).isoformat(timespec="seconds")
    bbox = _parse_bbox_arg(args.bbox) if args.bbox else get_market_bbox(args.market_id)

    osm_frames, osm_layers, osm_notes = fetch_osm_infrastructure(
        market_id=args.market_id,
        bbox=bbox,
        extract_date=extract_date,
        overpass_url=args.overpass_url,
    )
    overture_frame, overture_layers, overture_notes = fetch_overture_pois(
        market_id=args.market_id,
        bbox=bbox,
        extract_date=extract_date,
        overture_path=args.overture_path,
    )

    manifest = build_manifest(
        market_id=args.market_id,
        bbox=bbox,
        extract_date=extract_date,
        layers=[*osm_layers, *overture_layers],
        notes=[*osm_notes, *overture_notes],
    )
    frames = {
        "osm_lines": osm_frames["lines"],
        "osm_polygons": osm_frames["polygons"],
        "osm_points": osm_frames["points"],
        "overture_pois": overture_frame,
    }
    write_cache_outputs(args.market_id, frames, manifest)
    print(json.dumps({"market_id": args.market_id, "output_dir": str(OUTPUTS_ROOT / str(args.market_id))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
