"""Jacksonville-first Overture POI ingestion for Place Intelligence D3."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import sys

import duckdb


SECTION_ROOT = Path(__file__).resolve().parent
INDUSTRY_ROOT = SECTION_ROOT.parent / "industry"
if str(INDUSTRY_ROOT) not in sys.path:
    sys.path.insert(0, str(INDUSTRY_ROOT))

from ingest_spatial import build_manifest, fetch_overture_pois, get_market_bbox


OUTPUT_DIR = SECTION_ROOT / "outputs" / "jacksonville_fl"
MARKET_ID = "27260"
MARKET_SLUG = "jacksonville_fl"
DEFAULT_OVERTURE_RELEASE = "2026-06-17.0"
DEFAULT_OVERTURE_S3_PATH = (
    "s3://overturemaps-us-west-2/"
    f"release/{DEFAULT_OVERTURE_RELEASE}/theme=places/*/*"
)


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
    """Merge Overture results into an existing combined Jacksonville manifest if present."""

    if not existing:
        return new_manifest

    kept_layers = [layer for layer in existing.get("layers", []) if layer.get("source") != "overture"]
    kept_notes = [note for note in existing.get("notes", []) if "Overture" not in str(note)]
    return {
        "market_id": new_manifest["market_id"],
        "bbox": new_manifest["bbox"],
        "extract_date": new_manifest["extract_date"],
        "layers": kept_layers + new_manifest.get("layers", []),
        "notes": kept_notes + new_manifest.get("notes", []),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI args for the Jacksonville Overture run."""

    parser = argparse.ArgumentParser(description="Extract Jacksonville Overture POIs for Place Intelligence.")
    parser.add_argument(
        "--bbox",
        help="Optional west,south,east,north override. If omitted, derive from Jacksonville tract geometry.",
    )
    parser.add_argument(
        "--overture-path",
        default=DEFAULT_OVERTURE_S3_PATH,
        help="Cloud or local parquet/glob path for Overture Places.",
    )
    return parser.parse_args(argv)


def _parse_bbox_arg(bbox_text: str) -> tuple[float, float, float, float]:
    """Parse west,south,east,north bbox text."""

    parts = [float(value.strip()) for value in bbox_text.split(",")]
    if len(parts) != 4:
        raise ValueError("Expected bbox as west,south,east,north.")
    return parts[0], parts[1], parts[2], parts[3]


def main(argv: list[str] | None = None) -> int:
    """Run the Jacksonville Overture extraction and update the combined manifest."""

    args = parse_args(argv)
    extract_date = datetime.now(UTC).isoformat(timespec="seconds")
    bbox = _parse_bbox_arg(args.bbox) if args.bbox else get_market_bbox(MARKET_ID)

    overture_frame, overture_layers, overture_notes = fetch_overture_pois(
        market_id=MARKET_ID,
        bbox=bbox,
        extract_date=extract_date,
        overture_path=args.overture_path,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_parquet(overture_frame, OUTPUT_DIR / "overture_pois.parquet")

    new_manifest = build_manifest(
        market_id=MARKET_ID,
        bbox=bbox,
        extract_date=extract_date,
        layers=overture_layers,
        notes=overture_notes,
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
                "market_slug": MARKET_SLUG,
                "market_id": MARKET_ID,
                "bbox": bbox,
                "overture_rows": int(len(overture_frame)),
                "overture_path": args.overture_path,
                "output_dir": str(OUTPUT_DIR),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
