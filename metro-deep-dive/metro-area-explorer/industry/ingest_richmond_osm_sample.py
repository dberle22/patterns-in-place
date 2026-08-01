"""Small-bbox Richmond OSM infrastructure sample for fast layer inspection.

This script is the lightweight review path after the Virginia-scale `pyrosm`
download proved too heavy for quick iteration. It uses a compact Richmond bbox
and the existing Overpass-based infrastructure selectors so we can inspect
available tags, geometry mix, and sample coverage before locking a broader
metro-scale ingest strategy.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path

import duckdb

from ingest_spatial import (
    DEFAULT_OVERPASS_URL,
    OSM_QUERY_CONFIGS,
    build_manifest,
    fetch_osm_infrastructure,
)


SECTION_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = SECTION_ROOT / "outputs" / "richmond_va_sample"

SAMPLE_BBOXES = {
    "downtown_pilot": (-77.5000, 37.5000, -77.3900, 37.5900),
    "richmond_core": (-77.6200, 37.4300, -77.2200, 37.6700),
    "airport_corridor": (-77.5000, 37.4300, -77.1400, 37.6200),
}
LAYER_CHOICES = tuple(config.layer_group for config in OSM_QUERY_CONFIGS)


def _write_parquet(frame, path: Path) -> None:
    """Write one frame to parquet via DuckDB without adding a direct pyarrow dependency."""
    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    try:
        con.register("frame", frame)
        escaped_path = str(path).replace("'", "''")
        con.execute(f"COPY frame TO '{escaped_path}' (FORMAT PARQUET)")
    finally:
        con.close()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI args for the Richmond sample run."""
    parser = argparse.ArgumentParser(description="Extract a small Richmond OSM infrastructure sample.")
    parser.add_argument(
        "--sample-name",
        choices=sorted(SAMPLE_BBOXES),
        default="richmond_core",
        help="Named Richmond sample bbox to use.",
    )
    parser.add_argument(
        "--bbox",
        help="Optional west,south,east,north override for a custom Richmond sample bbox.",
    )
    parser.add_argument(
        "--overpass-url",
        default=DEFAULT_OVERPASS_URL,
        help="Overpass endpoint URL.",
    )
    parser.add_argument(
        "--layer",
        choices=LAYER_CHOICES,
        action="append",
        help="Optional one-or-more layer filters for a tighter sample run.",
    )
    return parser.parse_args(argv)


def _parse_bbox_arg(bbox_text: str) -> tuple[float, float, float, float]:
    """Parse west,south,east,north bbox text."""
    parts = [float(value.strip()) for value in bbox_text.split(",")]
    if len(parts) != 4:
        raise ValueError("Expected bbox as west,south,east,north.")
    return parts[0], parts[1], parts[2], parts[3]


def main(argv: list[str] | None = None) -> int:
    """Run the Richmond sample extraction and write review-friendly outputs."""
    args = parse_args(argv)
    extract_date = datetime.now(UTC).isoformat(timespec="seconds")
    bbox = _parse_bbox_arg(args.bbox) if args.bbox else SAMPLE_BBOXES[args.sample_name]
    selected_layers = tuple(args.layer) if args.layer else LAYER_CHOICES
    selected_configs = tuple(
        config for config in OSM_QUERY_CONFIGS if config.layer_group in selected_layers
    )
    layer_slug = "__".join(selected_layers)
    sample_dir = OUTPUT_DIR / args.sample_name / layer_slug

    osm_frames, osm_layers, osm_notes = fetch_osm_infrastructure(
        market_id=f"richmond_sample_{args.sample_name}",
        bbox=bbox,
        extract_date=extract_date,
        overpass_url=args.overpass_url,
        query_configs=selected_configs,
    )

    sample_dir.mkdir(parents=True, exist_ok=True)
    _write_parquet(osm_frames["lines"], sample_dir / "osm_infrastructure_lines.parquet")
    _write_parquet(osm_frames["polygons"], sample_dir / "osm_infrastructure_polygons.parquet")
    _write_parquet(osm_frames["points"], sample_dir / "osm_infrastructure_points.parquet")

    summary = {
        "sample_name": args.sample_name,
        "layers_requested": list(selected_layers),
        "bbox": {
            "west": bbox[0],
            "south": bbox[1],
            "east": bbox[2],
            "north": bbox[3],
        },
        "extract_date": extract_date,
        "line_rows": int(len(osm_frames["lines"])),
        "polygon_rows": int(len(osm_frames["polygons"])),
        "point_rows": int(len(osm_frames["points"])),
        "line_layer_counts": osm_frames["lines"]["layer_group"].value_counts().to_dict()
        if not osm_frames["lines"].empty
        else {},
        "polygon_layer_counts": osm_frames["polygons"]["layer_group"].value_counts().to_dict()
        if not osm_frames["polygons"].empty
        else {},
        "point_layer_counts": osm_frames["points"]["layer_group"].value_counts().to_dict()
        if not osm_frames["points"].empty
        else {},
    }

    manifest = build_manifest(
        market_id=f"richmond_sample_{args.sample_name}",
        bbox=bbox,
        extract_date=extract_date,
        layers=osm_layers,
        notes=osm_notes,
    )

    (sample_dir / "spatial_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (sample_dir / "sample_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps({"output_dir": str(sample_dir), **summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
