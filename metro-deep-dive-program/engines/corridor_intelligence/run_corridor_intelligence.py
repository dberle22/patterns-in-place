#!/usr/bin/env python3
"""Preflight one Corridor Intelligence market before grouping is implemented.

The final Epic 2 runner keeps this command and adds a grouping stage after the
same checks. It verifies the declared tract source directly, so the first
build can use the existing national tract geometry without mistaking its
legacy-vintage status for undocumented analytical metadata.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd
import yaml

from corridor_baseline import dbscan_products, evaluate_relationships, graph_products
from physical_refinement import refine_candidates


ENGINE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUTS = ENGINE_DIR / "inputs" / "corridor_inputs_v1.yml"
DEFAULT_OUTPUTS = ENGINE_DIR / "outputs" / "corridor_duckdb_contract_v1.yml"
DEFAULT_PROFILE = ENGINE_DIR / "inputs" / "baseline_graph_v1.yml"
DEFAULT_EVIDENCE_PROFILE = ENGINE_DIR / "inputs" / "physical_evidence_v1.yml"
DEFAULT_RUN_ROOT = ENGINE_DIR / "outputs" / "runs"


def read_yaml(path: Path) -> dict[str, Any]:
    """Load a versioned declaration rather than carrying input choices in code."""
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def check_market(con: duckdb.DuckDBPyConnection, inputs: dict[str, Any], market: str) -> dict[str, Any]:
    """Check the identity, Phase 7, and analytical-geometry gates for one market."""
    if market not in inputs["markets"]:
        raise ValueError(f"Unknown market {market!r}; use a declared market key.")

    market_config = inputs["markets"][market]
    phase7 = inputs["phase7"]
    relation = phase7["relation"]
    available_fields = {row[0] for row in con.execute(f"DESCRIBE {relation}").fetchall()}
    missing_fields = sorted(set(phase7["required_fields"]) - available_fields)
    cbsa_code = market_config["cbsa_code"]
    row_count, distinct_tract_count, names = con.execute(
        f"SELECT count(*), count(DISTINCT tract_geoid), list(DISTINCT cbsa_name) FROM {relation} WHERE cbsa_code = ?",
        [cbsa_code],
    ).fetchone()

    geometry = inputs["geometry"]
    geometry_relation = geometry["source_relation"]
    geometry_fields = {row[0] for row in con.execute(f"DESCRIBE {geometry_relation}").fetchall()}
    missing_geometry_fields = sorted(set(geometry["required_fields"]) - geometry_fields)
    geometry_coverage = None
    if not missing_geometry_fields:
        # Count directly against Phase 7 inputs. This catches missing, duplicate,
        # or null tract shapes without trying to infer a replacement table.
        geometry_coverage = con.execute(
            f"""
            SELECT
              count(*) FILTER (WHERE geometry_count = 1 AND valid_geometry_count = 1) AS covered_once,
              count(*) AS phase7_tracts
            FROM (
              SELECT
                z.tract_geoid,
                count(g.tract_geoid) AS geometry_count,
                count(g.tract_geoid) FILTER (WHERE g.geom IS NOT NULL) AS valid_geometry_count
              FROM {relation} z
              LEFT JOIN {geometry_relation} g ON z.tract_geoid = g.tract_geoid
              WHERE z.cbsa_code = ?
              GROUP BY z.tract_geoid
            )
            """,
            [cbsa_code],
        ).fetchone()
    geometry_ready = geometry_coverage is not None and geometry_coverage[0] == geometry_coverage[1]
    checks = {
        "phase7_required_fields": {"ok": not missing_fields, "missing": missing_fields},
        "phase7_market_coverage": {
            "ok": row_count == market_config["expected_phase7_tracts"] == distinct_tract_count and names == [market_config["cbsa_name"]],
            "expected_tracts": market_config["expected_phase7_tracts"],
            "rows": row_count,
            "distinct_tracts": distinct_tract_count,
            "cbsa_names": names,
        },
        "declared_tract_geometry": {
            "ok": geometry_ready,
            "source_relation": geometry_relation,
            "geometry_role": geometry["geometry_role"],
            "geometry_vintage_status": geometry["geometry_vintage_status"],
            "missing_fields": missing_geometry_fields,
            "coverage": None if geometry_coverage is None else dict(covered_once=geometry_coverage[0], phase7_tracts=geometry_coverage[1]),
            "blocking_reason": None if geometry_ready else "The declared tract geometry relation does not cover every Phase 7 tract exactly once.",
        },
    }
    return {"market": market, "cbsa_code": cbsa_code, "ready": all(check["ok"] for check in checks.values()), "checks": checks}


def load_tracts(con: duckdb.DuckDBPyConnection, inputs: dict[str, Any], market: str, profile: dict[str, Any]) -> pd.DataFrame:
    """Read only the declared Phase 7 fields and the declared tract geometry."""
    phase7 = inputs["phase7"]
    geometry = inputs["geometry"]
    fields = ["tract_geoid", "cbsa_code", "zone_type", *profile["similarity"]["fields"]]
    select_fields = ", ".join(f"z.{field}" for field in fields)
    tracts = con.execute(
        f"""
        SELECT {select_fields}, ST_AsWKB(g.geom) AS geometry_wkb
        FROM {phase7['relation']} z
        JOIN {geometry['source_relation']} g USING (tract_geoid)
        WHERE z.cbsa_code = ?
        ORDER BY z.tract_geoid
        """,
        [inputs["markets"][market]["cbsa_code"]],
    ).fetchdf()
    if tracts[profile["similarity"]["fields"]].isna().any().any():
        raise RuntimeError("Declared Phase 7 similarity fields contain nulls in the selected market.")
    return tracts


def load_physical_inputs(con: duckdb.DuckDBPyConnection, inputs: dict[str, Any], market: str, evidence: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load only the declared, versioned handoffs needed for Epic 3 refinement."""
    market_inputs = inputs["markets"][market]
    if "infrastructure" not in market_inputs or "poi" not in market_inputs:
        raise RuntimeError(f"{market} has no declared Infrastructure and POI handoffs for Epic 3.")
    infrastructure_input, poi_input = market_inputs["infrastructure"], market_inputs["poi"]
    infrastructure_path = ENGINE_DIR.parents[2] / infrastructure_input["feature_artifact"]
    classified_path = ENGINE_DIR.parents[2] / poi_input["classified_artifact"]
    assignment_path = ENGINE_DIR.parents[2] / poi_input["tract_assignment_artifact"]
    for path in (infrastructure_path, classified_path, assignment_path):
        if not path.exists():
            raise FileNotFoundError(f"Declared Epic 3 handoff is missing: {path.relative_to(ENGINE_DIR.parents[2])}")
    infrastructure = con.execute(
        """
        SELECT source_record_key, feature_type, geometry AS geometry_wkb
        FROM read_parquet(?)
        WHERE record_status = 'retained' AND mapping_status = 'mapped'
        """,
        [str(infrastructure_path)],
    ).fetchdf()
    allowed_types = set(evidence["infrastructure"]["spine_types"] + evidence["infrastructure"]["separator_types"])
    infrastructure = infrastructure[infrastructure.feature_type.isin(allowed_types)].copy()
    categories = evidence["poi"]["eligible_categories"]
    coverage = con.execute(
        """
        WITH eligible AS (
          SELECT source_record_key
          FROM read_parquet(?)
          WHERE record_status = 'retained' AND mapping_status = 'mapped'
            AND governed_category = ANY(?)
        ), assignments AS (
          SELECT source_record_key, geo_id AS tract_geoid
          FROM read_parquet(?)
          WHERE geo_level = 'tract' AND assignment_status = 'assigned'
        )
        SELECT count(*) AS eligible_places, count(assignments.tract_geoid) AS assigned_places
        FROM eligible LEFT JOIN assignments USING (source_record_key)
        """,
        [str(classified_path), categories, str(assignment_path)],
    ).fetchone()
    if coverage[0] != coverage[1]:
        raise RuntimeError(f"Eligible POI tract assignment is incomplete: {coverage[1]} of {coverage[0]} records assigned.")
    poi_counts = con.execute(
        """
        SELECT assignments.geo_id AS tract_geoid, classified.governed_category, count(*) AS place_count
        FROM read_parquet(?) classified
        JOIN read_parquet(?) assignments USING (source_record_key)
        WHERE classified.record_status = 'retained' AND classified.mapping_status = 'mapped'
          AND classified.governed_category = ANY(?)
          AND assignments.geo_level = 'tract' AND assignments.assignment_status = 'assigned'
        GROUP BY 1, 2 ORDER BY 1, 2
        """,
        [str(classified_path), str(assignment_path), categories],
    ).fetchdf()
    return infrastructure, poi_counts


def write_artifacts(run_dir: Path, frames: dict[str, pd.DataFrame], metadata: dict[str, Any]) -> None:
    """Write reviewable Epic 2 artifacts without publishing managed DuckDB tables yet."""
    run_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in frames.items():
        frame.to_parquet(run_dir / f"{name}.parquet", index=False)
    summary = {
        variant: {
            "input_tract_count": int(len(frame)),
            "core_tract_count": int((frame.membership_status == "core").sum()),
            "unassigned_tract_count": int((frame.membership_status == "unassigned").sum()),
        }
        for variant, frame in frames["structural_membership"].groupby("method_variant")
    }
    (run_dir / "run_manifest.json").write_text(json.dumps({**metadata, "tract_accounting": summary}, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    """Run the Epic 2 baseline only after the declared input checks pass."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True, help="Declared market key, for example jacksonville_fl.")
    parser.add_argument("--db-path", type=Path, required=True, help="DuckDB containing the governed input catalogs.")
    parser.add_argument("--inputs", type=Path, default=DEFAULT_INPUTS)
    parser.add_argument("--output-contract", type=Path, default=DEFAULT_OUTPUTS)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--evidence-profile", type=Path, help="Apply the declared Epic 3 physical/place refinement profile.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--preflight-only", action="store_true", help="Check inputs without writing baseline artifacts.")
    args = parser.parse_args()

    inputs = read_yaml(args.inputs)
    outputs = read_yaml(args.output_contract)
    profile = read_yaml(args.profile)
    evidence = read_yaml(args.evidence_profile) if args.evidence_profile else None
    with duckdb.connect(str(args.db_path), read_only=True) as con:
        result = check_market(con, inputs, args.market)
        if result["ready"] and not args.preflight_only:
            tracts = load_tracts(con, inputs, args.market, profile)
            if evidence:
                infrastructure, poi_counts = load_physical_inputs(con, inputs, args.market, evidence)
    result["input_interface_version"] = inputs["interface_version"]
    result["output_interface_version"] = outputs["interface_version"]
    if not result["ready"]:
        print(json.dumps(result, indent=2, sort_keys=True))
        raise SystemExit(2)
    if args.preflight_only:
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    relationships = evaluate_relationships(tracts, profile, args.market)
    # Refinement artifacts must retain the baseline profile in their identity:
    # otherwise a sensitivity run would silently overwrite the shared default.
    active_profile = f"{evidence['profile']}__{profile['profile']}" if evidence else profile["profile"]
    run_id = f"corridor-{result['cbsa_code']}-{active_profile}-{inputs['phase7']['build_id']}"
    membership, candidates, edge_evidence = graph_products(tracts, relationships, run_id)
    challenger_membership, challenger_candidates, challenger_edges = dbscan_products(tracts, relationships, run_id, profile)
    membership = pd.concat([membership, challenger_membership], ignore_index=True)
    candidates = pd.concat([candidates, challenger_candidates], ignore_index=True)
    edge_evidence = pd.concat([edge_evidence, challenger_edges], ignore_index=True)
    if evidence:
        physical_membership, physical_candidates, physical_edges = refine_candidates(tracts, relationships, infrastructure, poi_counts, profile, evidence, args.market, run_id)
        membership = pd.concat([membership, physical_membership], ignore_index=True)
        candidates = pd.concat([candidates, physical_candidates], ignore_index=True)
        edge_evidence = pd.concat([edge_evidence, physical_edges], ignore_index=True)
    run_dir = args.output_root / run_id
    write_artifacts(run_dir, {"structural_membership": membership, "structural_candidate": candidates, "structural_edge_evidence": edge_evidence}, {"run_id": run_id, "market": args.market, "cbsa_code": result["cbsa_code"], "method_version": evidence["method_version"] if evidence else profile["method_version"], "parameter_profile": active_profile, "phase7_build_id": inputs["phase7"]["build_id"], "geometry_role": inputs["geometry"]["geometry_role"], "geometry_vintage_status": inputs["geometry"]["geometry_vintage_status"], "infrastructure_source_run_id": inputs["markets"][args.market].get("infrastructure", {}).get("source_run_id"), "poi_source_run_id": inputs["markets"][args.market].get("poi", {}).get("source_run_id"), "publication_status": "epic_3_review_artifact_not_duckdb_published" if evidence else "epic_2_review_artifact_not_duckdb_published"})
    result["run_id"] = run_id
    result["artifact_directory"] = str(run_dir.relative_to(ENGINE_DIR.parents[2]))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
