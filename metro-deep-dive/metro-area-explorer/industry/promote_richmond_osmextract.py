"""Promote Richmond osmextract outputs into the standard D4 cache contract.

The R-based osmextract prototype proved to be the first reliable OSM geometry
path for Richmond, but its raw outputs do not match the exact cache schema that
the D4 app already reads. This bridge keeps the stable Richmond extract and
normalizes it into the standard `osm_infrastructure_*` parquet files plus the
shared `spatial_manifest.json`.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import duckdb
import pandas as pd
from shapely import wkt


SECTION_ROOT = Path(__file__).resolve().parent
SOURCE_DIR = SECTION_ROOT / "outputs" / "richmond_va_osmextract"
TARGET_DIR = SECTION_ROOT / "outputs" / "richmond_va"
MANIFEST_PATH = TARGET_DIR / "spatial_manifest.json"

SOURCE_FILES = {
    "osm_lines": SOURCE_DIR / "osmextract_infrastructure_lines.parquet",
    "osm_points": SOURCE_DIR / "osmextract_infrastructure_points.parquet",
    "osm_polygons": SOURCE_DIR / "osmextract_infrastructure_polygons.parquet",
}
TARGET_FILES = {
    "osm_lines": TARGET_DIR / "osm_infrastructure_lines.parquet",
    "osm_points": TARGET_DIR / "osm_infrastructure_points.parquet",
    "osm_polygons": TARGET_DIR / "osm_infrastructure_polygons.parquet",
}


def _read_parquet(path: Path) -> pd.DataFrame:
    """Read one parquet file via DuckDB so we do not depend on pyarrow directly."""
    if not path.exists():
        return pd.DataFrame()
    con = duckdb.connect()
    try:
        return con.execute("SELECT * FROM read_parquet(?)", [str(path)]).fetchdf()
    finally:
        con.close()


def _write_parquet(frame: pd.DataFrame, path: Path) -> None:
    """Write one normalized parquet file via DuckDB."""
    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    try:
        con.register("frame", frame)
        escaped_path = str(path).replace("'", "''")
        con.execute(f"COPY frame TO '{escaped_path}' (FORMAT PARQUET)")
    finally:
        con.close()


def _geometry_to_geojson(geometry_wkt: str) -> str:
    """Convert one WKT geometry string into the cached GeoJSON-string format."""
    if not geometry_wkt:
        return ""
    geometry = wkt.loads(geometry_wkt)
    return json.dumps(geometry.__geo_interface__)


def _normalize_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Align one osmextract parquet to the standard D4 cache schema."""
    if frame.empty:
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

    normalized = frame.copy()
    if "geometry" not in normalized.columns and "geometry_wkt" in normalized.columns:
        normalized["geometry"] = normalized["geometry_wkt"].apply(_geometry_to_geojson)

    keep_columns = [
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
    for column in keep_columns:
        if column not in normalized.columns:
            normalized[column] = None
    return normalized[keep_columns].copy()


def _build_layers(frames: dict[str, pd.DataFrame]) -> list[dict[str, object]]:
    """Summarize the normalized OSM frames for the shared manifest."""
    layers: list[dict[str, object]] = []
    for frame_key, geometry_type in [
        ("osm_lines", "line"),
        ("osm_points", "point"),
        ("osm_polygons", "polygon"),
    ]:
        frame = frames[frame_key]
        if frame.empty:
            continue
        counts = (
            frame.groupby("layer_group", dropna=False)
            .size()
            .reset_index(name="row_count")
            .sort_values("row_count", ascending=False, kind="mergesort")
        )
        for _, row in counts.iterrows():
            layers.append(
                {
                    "source": "osm",
                    "layer_name": row["layer_group"] or "unclassified",
                    "geometry_type": geometry_type,
                    "row_count": int(row["row_count"]),
                    "query_config": {"method": "osmextract", "provider": "openstreetmap_fr"},
                    "notes_on_sparse_or_missing_layers": "",
                }
            )
    return layers


def _merge_manifest(new_layers: list[dict[str, object]], new_notes: list[str]) -> dict[str, object]:
    """Merge promoted osmextract layers into the existing Richmond manifest."""
    existing = {}
    if MANIFEST_PATH.exists():
        existing = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    kept_layers = [layer for layer in existing.get("layers", []) if layer.get("source") != "osm"]
    kept_notes = [note for note in existing.get("notes", []) if "osmextract" not in str(note) and "OSM layer " not in str(note)]

    return {
        "market_id": existing.get("market_id", "40060"),
        "bbox": existing.get(
            "bbox",
            {
                "west": None,
                "south": None,
                "east": None,
                "north": None,
            },
        ),
        "extract_date": datetime.now(UTC).isoformat(timespec="seconds"),
        "layers": kept_layers + new_layers,
        "notes": kept_notes + new_notes,
    }


def main() -> int:
    """Normalize and promote the successful Richmond osmextract run."""
    frames = {
        frame_key: _normalize_frame(_read_parquet(source_path))
        for frame_key, source_path in SOURCE_FILES.items()
    }
    for frame_key, target_path in TARGET_FILES.items():
        _write_parquet(frames[frame_key], target_path)

    notes = [
        "OSM infrastructure promoted from the Richmond osmextract run.",
        "OSM source path: openstreetmap_fr Richmond provider extract.",
        f"Promoted from: {SOURCE_DIR}",
    ]
    manifest = _merge_manifest(_build_layers(frames), notes)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "target_dir": str(TARGET_DIR),
                "line_rows": int(len(frames["osm_lines"])),
                "point_rows": int(len(frames["osm_points"])),
                "polygon_rows": int(len(frames["osm_polygons"])),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
