"""Fetch and cache FDOT AADT segments for Place Intelligence D4.

This is intentionally app-local v0 cache work. It clips the official FDOT
statewide AADT layer to a market bbox and writes a local parquet artifact the
Place Intelligence prep code can read without live network calls.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import duckdb
import pandas as pd


SECTION_ROOT = Path(__file__).resolve().parent
INDUSTRY_ROOT = SECTION_ROOT.parent / "industry"
if str(INDUSTRY_ROOT) not in sys.path:
    sys.path.insert(0, str(INDUSTRY_ROOT))

from ingest_spatial import build_manifest, get_market_bbox


FDOT_AADT_LAYER_URL = "https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/0/query"
FDOT_AADT_HISTORICAL_LAYER_URL = (
    "https://services1.arcgis.com/O1JpcwDW8sjYuddV/ArcGIS/rest/services/"
    "Annual_Average_Daily_Traffic_Historical_TDA/FeatureServer/0/query"
)
DEFAULT_STATE = "FL"
DEFAULT_MARKET_ID = "27260"
DEFAULT_OUTPUT_SLUG = "jacksonville_fl"
BATCH_SIZE = 1000
OUTPUT_COLUMNS = [
    "market_id",
    "state",
    "source_system",
    "source_id",
    "year",
    "roadway",
    "county",
    "aadt",
    "begin_post",
    "end_post",
    "desc_frm",
    "desc_to",
    "geometry_type",
    "geometry",
    "extract_date",
]


def _write_parquet(frame: pd.DataFrame, path: Path) -> None:
    """Write one frame to parquet via DuckDB without adding a pyarrow dependency."""

    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    try:
        con.register("frame", frame)
        escaped_path = str(path).replace("'", "''")
        con.execute(f"COPY frame TO '{escaped_path}' (FORMAT PARQUET)")
    finally:
        con.close()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI args for the FDOT AADT cache build."""

    parser = argparse.ArgumentParser(description="Extract FDOT AADT segments for Place Intelligence.")
    parser.add_argument("--market-id", default=DEFAULT_MARKET_ID, help="CBSA / market id used for bbox derivation.")
    parser.add_argument("--state", default=DEFAULT_STATE, help="Two-letter state code for provenance labeling.")
    parser.add_argument(
        "--bbox",
        help="Optional west,south,east,north override. If omitted, derive from market tract geometry.",
    )
    parser.add_argument(
        "--output-slug",
        default=DEFAULT_OUTPUT_SLUG,
        help="Output folder slug under place_intelligence/outputs/.",
    )
    return parser.parse_args(argv)


def _parse_bbox_arg(bbox_text: str) -> tuple[float, float, float, float]:
    """Parse west,south,east,north bbox text."""

    parts = [float(value.strip()) for value in bbox_text.split(",")]
    if len(parts) != 4:
        raise ValueError("Expected bbox as west,south,east,north.")
    return parts[0], parts[1], parts[2], parts[3]


def _request_geojson(service_url: str, params: dict[str, Any]) -> dict[str, Any]:
    """Query the FDOT ArcGIS layer and return parsed JSON."""

    request = Request(
        f"{service_url}?{urlencode(params)}",
        headers={"Accept": "application/json", "User-Agent": "patterns-in-place-codex/1.0"},
        method="GET",
    )
    with urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def _geometry_to_geojson(geometry: dict[str, Any] | None) -> dict[str, Any] | None:
    """Normalize ArcGIS JSON geometry into GeoJSON-like geometry when needed."""

    if geometry is None:
        return None
    if "type" in geometry:
        return geometry
    if "paths" in geometry:
        if len(geometry["paths"]) == 1:
            return {"type": "LineString", "coordinates": geometry["paths"][0]}
        return {"type": "MultiLineString", "coordinates": geometry["paths"]}
    if "x" in geometry and "y" in geometry:
        return {"type": "Point", "coordinates": [geometry["x"], geometry["y"]]}
    return None


def fetch_fdot_aadt_segments(
    bbox: tuple[float, float, float, float],
    service_url: str = FDOT_AADT_LAYER_URL,
    source_id_field: str = "OBJECTID",
) -> pd.DataFrame:
    """Fetch all FDOT AADT line features intersecting one bbox."""

    base_params = {
        "geometry": ",".join(str(value) for value in bbox),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": f"{source_id_field},YEAR_,ROADWAY,COUNTY,AADT,BEGIN_POST,END_POST,DESC_FRM,DESC_TO",
        "outSR": "4326",
        "returnGeometry": "true",
        "f": "json",
        "where": "1=1",
    }

    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        payload = _request_geojson(
            service_url,
            {
                **base_params,
                "resultOffset": offset,
                "resultRecordCount": BATCH_SIZE,
            }
        )
        if payload.get("error"):
            raise ValueError(f"FDOT query failed: {payload['error']}")
        features = payload.get("features", [])
        for feature in features:
            properties = feature.get("properties") or feature.get("attributes") or {}
            geometry = _geometry_to_geojson(feature.get("geometry"))
            source_id = properties.get("OBJECTID", properties.get("FID"))
            rows.append(
                {
                    "source_id": str(source_id) if source_id is not None else None,
                    "year": properties.get("YEAR_"),
                    "roadway": properties.get("ROADWAY"),
                    "county": properties.get("COUNTY"),
                    "aadt": properties.get("AADT"),
                    "begin_post": properties.get("BEGIN_POST"),
                    "end_post": properties.get("END_POST"),
                    "desc_frm": properties.get("DESC_FRM"),
                    "desc_to": properties.get("DESC_TO"),
                    "geometry_type": geometry.get("type") if isinstance(geometry, dict) else None,
                    "geometry": json.dumps(geometry) if geometry else None,
                }
            )

        if not payload.get("properties", {}).get("exceededTransferLimit") and not payload.get("exceededTransferLimit"):
            break
        offset += BATCH_SIZE

    return pd.DataFrame(rows)


def main(argv: list[str] | None = None) -> int:
    """Run the FDOT AADT extraction and write the market-local cache."""

    args = parse_args(argv)
    extract_date = datetime.now(timezone.utc).isoformat(timespec="seconds")
    bbox = _parse_bbox_arg(args.bbox) if args.bbox else get_market_bbox(args.market_id)
    frame = fetch_fdot_aadt_segments(bbox, service_url=FDOT_AADT_LAYER_URL, source_id_field="OBJECTID").copy()
    historical = fetch_fdot_aadt_segments(
        bbox,
        service_url=FDOT_AADT_HISTORICAL_LAYER_URL,
        source_id_field="FID",
    ).copy()
    for output_frame in (frame, historical):
        output_frame["market_id"] = str(args.market_id)
        output_frame["state"] = str(args.state).upper()
        output_frame["source_system"] = "fdot"
        output_frame["extract_date"] = extract_date
    frame = frame[OUTPUT_COLUMNS].copy()
    historical = historical[OUTPUT_COLUMNS].copy()

    output_dir = SECTION_ROOT / "outputs" / args.output_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_parquet(frame, output_dir / "fdot_aadt_segments.parquet")
    _write_parquet(historical, output_dir / "fdot_aadt_historical_segments.parquet")

    manifest = build_manifest(
        market_id=str(args.market_id),
        bbox=bbox,
        extract_date=extract_date,
        layers=[
            {
                "source": "fdot",
                "layer_name": "aadt_segments",
                "geometry_type": "line",
                "row_count": int(len(frame)),
                "query_config": {
                    "state": str(args.state).upper(),
                    "service_url": FDOT_AADT_LAYER_URL,
                    "bbox": bbox,
                },
                "notes_on_sparse_or_missing_layers": "",
            },
            {
                "source": "fdot",
                "layer_name": "aadt_historical_segments",
                "geometry_type": "line",
                "row_count": int(len(historical)),
                "query_config": {
                    "state": str(args.state).upper(),
                    "service_url": FDOT_AADT_HISTORICAL_LAYER_URL,
                    "bbox": bbox,
                },
                "notes_on_sparse_or_missing_layers": "",
            }
        ],
        notes=[
            "FDOT statewide AADT segments clipped to the requested market bbox.",
            "FDOT historical AADT segments clipped to the requested market bbox.",
            "AADT is an annual average daily traffic statistic, not a peak-hour observed count.",
            "Source: official FDOT AADT FeatureServer layer 0.",
        ],
    )
    manifest_path = output_dir / "traffic_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "market_id": str(args.market_id),
                "state": str(args.state).upper(),
                "bbox": bbox,
                "rows": int(len(frame)),
                "historical_rows": int(len(historical)),
                "output_dir": str(output_dir),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
