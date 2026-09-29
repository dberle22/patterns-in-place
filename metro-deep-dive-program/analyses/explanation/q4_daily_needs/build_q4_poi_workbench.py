#!/usr/bin/env python3
"""Build Q4's POI-first workbench and analysis-owned basket membership."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb
import pandas as pd
import yaml


MARKETS = {"richmond_va": "40060", "jacksonville_fl": "27260"}


def repo_root() -> Path:
    """Resolve the repository without persisting a machine-specific path."""
    return Path(__file__).resolve().parents[4]


def latest_run(root: Path, market: str) -> Path:
    """Use the newest declared POI run for the named pilot market."""
    runs = sorted(path for path in (root / market).iterdir() if path.is_dir())
    if not runs:
        raise FileNotFoundError(f"No POI run for {market}.")
    return runs[-1]


def write_parquet(frame: pd.DataFrame, path: Path) -> None:
    """Write local analysis artifacts without materializing a shared mart."""
    with duckdb.connect() as con:
        con.register("frame", frame)
        con.execute("COPY frame TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(path)])


def main() -> None:
    """Join classified points to tract assignment and expose basket membership."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "outputs" / "q4_poi_workbench_v1")
    args = parser.parse_args()
    analysis_dir = Path(__file__).resolve().parent
    config = yaml.safe_load((analysis_dir / "q4_amenity_baskets.yml").read_text())
    poi_root = repo_root() / "metro-deep-dive-program" / "engines" / "poi" / "outputs"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    point_frames, membership_frames, coverage_frames = [], [], []
    source_runs = {}

    for market, cbsa_code in MARKETS.items():
        run = latest_run(poi_root, market)
        source_runs[market] = run
        classified = run / "classified" / "poi_classified_place.parquet"
        assignment = run / "geography" / "poi_geography_assignment.parquet"
        with duckdb.connect() as con:
            points = con.execute("""
                SELECT p.source_record_key, p.source_run_id, p.mapping_version,
                       p.record_status, p.mapping_status, p.review_status,
                       p.category, p.sub_category, p.longitude, p.latitude,
                       a.geo_id AS tract_geoid, a.assignment_status AS tract_assignment_status
                FROM read_parquet(?) p
                LEFT JOIN read_parquet(?) a
                  ON p.source_record_key = a.source_record_key AND a.geo_level = 'tract'
                WHERE p.record_status = 'retained'
            """, [str(classified), str(assignment)]).fetchdf()
        if points.source_record_key.duplicated().any() or len(points) == 0:
            raise ValueError(f"Invalid POI workbench input for {market}.")
        points["cbsa_code"], points["market_slug"] = cbsa_code, market
        points["workbench_status"] = points.mapping_status.map({"mapped": "classified", "unmapped": "unclassified"}).fillna("unclassified")
        for basket_id, basket in config["baskets"].items():
            category_match = points.category.isin(basket.get("categories", []))
            subcategory_match = points.sub_category.isin(basket.get("sub_categories", []))
            points[f"is_{basket_id}"] = (category_match | subcategory_match) & (points.mapping_status == "mapped")
            members = points.loc[points[f"is_{basket_id}"], ["source_record_key", "cbsa_code", "market_slug", "category", "sub_category", "longitude", "latitude", "tract_geoid"]].copy()
            members["basket_version"], members["basket_id"] = config["version"], basket_id
            membership_frames.append(members)
        coverage = points.groupby(["cbsa_code", "market_slug", "mapping_status", "tract_assignment_status"], dropna=False).size().reset_index(name="poi_count")
        coverage_frames.append(coverage)
        point_frames.append(points)

    workbench = pd.concat(point_frames, ignore_index=True)
    memberships = pd.concat(membership_frames, ignore_index=True)
    coverage = pd.concat(coverage_frames, ignore_index=True)
    if memberships.duplicated(["basket_id", "source_record_key"]).any() or workbench.tract_geoid.isna().any():
        raise ValueError("Basket membership or tract assignment failed workbench QA.")
    composition = workbench.groupby(["cbsa_code", "market_slug", "workbench_status", "category", "sub_category"], dropna=False).size().reset_index(name="poi_count")
    write_parquet(workbench, args.output_dir / "q4_poi_workbench.parquet")
    write_parquet(memberships, args.output_dir / "q4_poi_basket_membership.parquet")
    write_parquet(coverage, args.output_dir / "q4_poi_coverage.parquet")
    write_parquet(composition, args.output_dir / "q4_poi_category_composition.parquet")
    catalog = pd.DataFrame([{"basket_version": config["version"], "basket_id": key, "label": value["label"], "description": value["description"], "categories": json.dumps(value.get("categories", [])), "sub_categories": json.dumps(value.get("sub_categories", []))} for key, value in config["baskets"].items()])
    write_parquet(catalog, args.output_dir / "q4_poi_basket_catalog.parquet")
    artifacts = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in args.output_dir.glob("q4_*.parquet")}
    manifest = {"basket_version": config["version"], "interface_status": "pilot_artifacts_direct_not_promoted", "source_runs": {market: str(run.relative_to(repo_root())) for market, run in source_runs.items()}, "artifacts": artifacts, "workbench_rows": len(workbench), "membership_rows": len(memberships)}
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
