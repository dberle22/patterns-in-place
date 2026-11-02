#!/usr/bin/env python3
"""Build POI run artifacts for many markets, stopping before the warehouse.

Usage:
    python metro-deep-dive-program/engines/poi/run_poi_markets.py --series ny_state
    python metro-deep-dive-program/engines/poi/run_poi_markets.py --markets hudson_ny ny_non_cbsa

Each market resumes at its first unfinished step on the declared release, so a
rerun skips finished work. Any step failure stops the batch. Publishing is a
separate reviewed step; this runner never writes to DuckDB.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from acquire_overture_places import DEFAULT_CONFIG, ENGINE_DIR, read_config
from normalize_overture_places import latest_source_run


OUTPUT_ROOT = ENGINE_DIR / "outputs"
BASELINE_MARKET = "albany_ny"
PROFILE_MANIFEST = "classified/taxonomy_profile/taxonomy_profile_manifest.json"
# Step name, script, completion marker in the run folder, and optional inputs.
STEPS = (
    ("normalize", "normalize_overture_places.py", "normalized/normalization_manifest.json", {"db"}),
    ("classify", "classify_overture_places.py", "classified/classification_manifest.json", set()),
    ("profile", "taxonomy/build_taxonomy_hierarchy_profile.py", PROFILE_MANIFEST, {"baseline"}),
    ("validate", "taxonomy/validate_taxonomy_rules.py", "classified/taxonomy_profile/taxonomy_validation_report.json", {"baseline"}),
    ("assign", "assign_poi_geography.py", "geography/assignment_manifest.json", {"db"}),
)


def selected_markets(config: dict, series: str | None, markets: list[str] | None) -> list[str]:
    """Resolve the requested markets in their declared order."""

    declared = config["markets"]
    if markets:
        unknown = sorted(set(markets) - set(declared))
        if unknown:
            raise ValueError(f"Undeclared markets: {', '.join(unknown)}.")
        return markets
    chosen = [name for name, market in declared.items() if market.get("series") == series]
    if not chosen:
        raise ValueError(f"No markets declared for series {series!r}.")
    return chosen


def current_run(market: str, release: str) -> Path | None:
    """Return the newest run on the declared release, if the market has one."""

    try:
        run = latest_source_run(OUTPUT_ROOT, market)
    except FileNotFoundError:
        return None
    manifest = json.loads((run / "source_run_manifest.json").read_text(encoding="utf-8"))
    return run if manifest["source_release"] == release else None


def run_step(market: str, name: str, command: list[str]) -> None:
    """Run one pipeline script, keeping its normal output in the batch log."""

    started = time.time()
    print(f"[{market}] {name} start", flush=True)
    subprocess.run(command, check=True)
    print(f"[{market}] {name} done in {time.time() - started:.0f}s", flush=True)


def build_market(market: str, release: str, baseline: Path, db_args: list[str]) -> Path:
    """Run a market's unfinished steps and apply the taxonomy hard stop."""

    run = current_run(market, release)
    if run is None:
        run_step(market, "acquire", [sys.executable, str(ENGINE_DIR / "acquire_overture_places.py"), "--market", market, *db_args])
        run = current_run(market, release)
        if run is None:
            raise RuntimeError(f"Acquisition finished without a {release} run for {market}.")
    for name, script, marker, inputs in STEPS:
        if (run / marker).exists():
            print(f"[{market}] {name} already complete", flush=True)
            continue
        command = [sys.executable, str(ENGINE_DIR / script), "--market", market, "--source-run-dir", str(run)]
        if "db" in inputs:
            command += db_args
        if "baseline" in inputs:
            command += ["--baseline-run-dir", str(baseline)]
        run_step(market, name, command)
        if name == "profile":
            profile = json.loads((run / PROFILE_MANIFEST).read_text(encoding="utf-8"))
            if profile["invariant_violations"]:
                raise RuntimeError(f"{market}: taxonomy invariant violated on {profile['invariant_violations']:,} places.")
    return run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--series", help="Run every market declared with this series.")
    group.add_argument("--markets", nargs="+", help="Run these declared markets.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--db-path", type=Path)
    args = parser.parse_args()

    config = read_config(args.config)
    db_args = ["--db-path", str(args.db_path)] if args.db_path else []
    baseline = latest_source_run(OUTPUT_ROOT, BASELINE_MARKET)
    started = time.time()
    for market in selected_markets(config, args.series, args.markets):
        build_market(market, config["source_release"], baseline, db_args)
    print(f"Batch complete in {time.time() - started:.0f}s. Nothing was published.", flush=True)


if __name__ == "__main__":
    main()
