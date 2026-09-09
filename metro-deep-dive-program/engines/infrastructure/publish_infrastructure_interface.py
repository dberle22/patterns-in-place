#!/usr/bin/env python3
"""Resolve and verify the read-only Infrastructure Engine consumer handoff.

This does not copy data, write a managed table, or perform analysis. It checks
that the latest Epic 4 candidate has the fields promised by the versioned
consumer contract and prints its exact local artifact and promotion gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import duckdb
import yaml

from acquire_osm_infrastructure import ENGINE_DIR, REPO_ROOT, sql_literal
from normalize_osm_infrastructure import latest_source_run


DEFAULT_OUTPUT_ROOT = ENGINE_DIR / "outputs"
DEFAULT_INTERFACE = ENGINE_DIR / "consumers" / "infrastructure_consumer_interface_v1.yml"


def read_interface(path: Path) -> dict[str, Any]:
    """Load the small checked-in consumer contract and validate its essentials."""

    interface = yaml.safe_load(path.read_text(encoding="utf-8"))
    needed = {"interface_version", "artifact", "required_fields", "consumer_contracts", "adoptions"}
    if not interface or needed - set(interface):
        raise ValueError("Consumer interface declaration is incomplete.")
    return interface


def main() -> None:
    """Print a verified, machine-readable pointer to one market's candidate."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True)
    parser.add_argument("--source-run-dir", type=Path, help="Completed source run; defaults to the latest for --market.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--interface", type=Path, default=DEFAULT_INTERFACE)
    args = parser.parse_args()

    interface = read_interface(args.interface)
    source_dir = args.source_run_dir or latest_source_run(args.output_root, args.market)
    source_manifest = json.loads((source_dir / "source_run_manifest.json").read_text(encoding="utf-8"))
    validation_manifest = json.loads((source_dir / "validated" / "osm_core_v1" / "validation_manifest.json").read_text(encoding="utf-8"))
    artifact = source_dir / interface["artifact"]
    if not artifact.exists():
        raise FileNotFoundError(f"Validated consumer artifact is missing: {artifact}")
    with duckdb.connect() as con:
        fields = {row[0] for row in con.execute(f"DESCRIBE SELECT * FROM read_parquet({sql_literal(str(artifact))})").fetchall()}
    missing = sorted(set(interface["required_fields"]) - fields)
    if missing:
        raise RuntimeError(f"Consumer artifact is missing required fields: {', '.join(missing)}")

    geometry_role = source_manifest["boundary"]["geometry_role"]
    print(json.dumps({
        "interface_version": interface["interface_version"],
        "market": args.market,
        "market_id": source_manifest["market_id"],
        "source_run_id": source_manifest["source_run_id"],
        "artifact_uri": str(artifact.relative_to(REPO_ROOT)),
        "validation_manifest_uri": str((source_dir / "validated" / "osm_core_v1" / "validation_manifest.json").relative_to(REPO_ROOT)),
        "boundary_geometry_role": geometry_role,
        "promotion_status": "candidate_only" if geometry_role != "analytical" else "eligible_for_consumer_promotion",
        "adoptions": interface["adoptions"],
    }, indent=2))


if __name__ == "__main__":
    main()
