"""Richmond-first OSM infrastructure ingestion for Industry D4 review.

This wrapper keeps the Richmond run explicit and writes outputs under
`outputs/richmond_va/` so the review artifacts can point at a stable location.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path

import duckdb

from ingest_spatial import (
    DEFAULT_OVERPASS_URL,
    build_manifest,
    fetch_osm_infrastructure,
    get_market_bbox,
)


SECTION_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = SECTION_ROOT / "outputs" / "richmond_va"
MARKET_ID = "40060"


def _write_parquet(frame, path: Path) -> None:
    """Write one frame to parquet via DuckDB without adding a pyarrow dependency."""
    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    try:
        con.register("frame", frame)
        escaped_path = str(path).replace("'", "''")
        con.execute(f"COPY frame TO '{escaped_path}' (FORMAT PARQUET)")
    finally:
        con.close()


def _merge_manifest(existing: dict | None, new_manifest: dict) -> dict:
    """Merge OSM layer results into an existing combined manifest if present."""
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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI args for the Richmond OSM run."""
    parser = argparse.ArgumentParser(description="Extract Richmond OSM infrastructure layers for D4 review.")
    parser.add_argument(
        "--bbox",
        help="Optional west,south,east,north override. If omitted, derive from Richmond tract geometry.",
    )
    parser.add_argument("--overpass-url", default=DEFAULT_OVERPASS_URL, help="Overpass endpoint URL.")
    return parser.parse_args(argv)


def _parse_bbox_arg(bbox_text: str) -> tuple[float, float, float, float]:
    """Parse west,south,east,north bbox text."""
    parts = [float(value.strip()) for value in bbox_text.split(",")]
    if len(parts) != 4:
        raise ValueError("Expected bbox as west,south,east,north.")
    return parts[0], parts[1], parts[2], parts[3]


def main(argv: list[str] | None = None) -> int:
    """Run the Richmond OSM extraction and update the combined manifest."""
    args = parse_args(argv)
    extract_date = datetime.now(UTC).isoformat(timespec="seconds")
    bbox = _parse_bbox_arg(args.bbox) if args.bbox else get_market_bbox(MARKET_ID)

    osm_frames, osm_layers, osm_notes = fetch_osm_infrastructure(
        market_id=MARKET_ID,
        bbox=bbox,
        extract_date=extract_date,
        overpass_url=args.overpass_url,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_parquet(osm_frames["lines"], OUTPUT_DIR / "osm_infrastructure_lines.parquet")
    _write_parquet(osm_frames["polygons"], OUTPUT_DIR / "osm_infrastructure_polygons.parquet")
    _write_parquet(osm_frames["points"], OUTPUT_DIR / "osm_infrastructure_points.parquet")

    new_manifest = build_manifest(
        market_id=MARKET_ID,
        bbox=bbox,
        extract_date=extract_date,
        layers=osm_layers,
        notes=osm_notes,
    )
    manifest_path = OUTPUT_DIR / "spatial_manifest.json"
    existing_manifest = None
    if manifest_path.exists():
        existing_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    merged_manifest = _merge_manifest(existing_manifest, new_manifest)
    manifest_path.write_text(json.dumps(merged_manifest, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "market_slug": "richmond_va",
                "market_id": MARKET_ID,
                "bbox": bbox,
                "line_rows": int(len(osm_frames["lines"])),
                "polygon_rows": int(len(osm_frames["polygons"])),
                "point_rows": int(len(osm_frames["points"])),
                "output_dir": str(OUTPUT_DIR),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
