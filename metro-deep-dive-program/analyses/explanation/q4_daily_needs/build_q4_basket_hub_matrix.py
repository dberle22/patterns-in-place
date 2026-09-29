#!/usr/bin/env python3
"""Build the declared Q4 basket-by-threshold amenity-hub review matrix."""
from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd

from build_q4_amenity_hubs import CandidateVersion, MARKETS, build_candidate, write_geojson, write_parquet, write_review_maps


METHOD_VERSION = "q4_amenity_hub_basket_matrix_v1"
BASKETS = ("proximity_amenities", "errands_essentials", "employment_places")
CANDIDATES = (
    CandidateVersion("grid_250m_min_20", 250, 20, recommended_for_review=True),
    CandidateVersion("grid_250m_min_10", 250, 10),
    CandidateVersion("grid_500m_min_60", 500, 60),
)


def main() -> None:
    """Persist all nine basket/method combinations as unpromoted pilot evidence."""
    analysis_dir = Path(__file__).parent
    source = analysis_dir / "outputs" / "q4_poi_workbench_v1" / "q4_poi_workbench.parquet"
    output = analysis_dir / "outputs" / METHOD_VERSION
    output.mkdir(parents=True, exist_ok=True)
    hubs_all, members_all, mix_all = [], [], []
    with duckdb.connect() as con:
        workbench = con.execute("select * from read_parquet(?)", [str(source)]).fetchdf()
    for basket_id in BASKETS:
        for market, details in MARKETS.items():
            points = workbench.loc[(workbench.cbsa_code == details["cbsa_code"]) & workbench[f"is_{basket_id}"], ["source_record_key", "source_run_id", "mapping_version", "category", "sub_category", "longitude", "latitude"]]
            for candidate in CANDIDATES:
                hubs, members, mix = build_candidate(points, market, candidate)
                for frame in (hubs, members, mix):
                    if not frame.empty:
                        frame["basket_id"] = basket_id
                        frame["method_version"] = METHOD_VERSION
                hubs_all.append(hubs); members_all.append(members); mix_all.append(mix)
    hubs = pd.concat(hubs_all, ignore_index=True)
    members = pd.concat(members_all, ignore_index=True)
    mix = pd.concat(mix_all, ignore_index=True)
    if members.duplicated(["basket_id", "candidate_version", "source_record_key"]).any():
        raise ValueError("A POI has duplicate membership within a basket candidate.")
    write_parquet(hubs, output / "q4_amenity_hub_inventory.parquet")
    write_parquet(members, output / "q4_amenity_hub_membership.parquet")
    write_parquet(mix, output / "q4_amenity_hub_category_mix.parquet")
    write_geojson(hubs, output / "q4_amenity_hub_inventory.geojson")
    write_review_maps(hubs, members, output)
    summary = hubs.groupby(["basket_id", "market_slug", "candidate_version"], as_index=False).agg(hub_count=("amenity_hub_id", "size"), member_pois=("poi_count", "sum"))
    summary.to_csv(output / "q4_amenity_hub_matrix_summary.csv", index=False)
    (output / "manifest.json").write_text(json.dumps({"method_version": METHOD_VERSION, "status": "pilot_artifacts_direct_not_promoted", "baskets": BASKETS, "candidates": [candidate.name for candidate in CANDIDATES], "hub_count": len(hubs), "membership_count": len(members)}, indent=2) + "\n")


if __name__ == "__main__":
    main()
