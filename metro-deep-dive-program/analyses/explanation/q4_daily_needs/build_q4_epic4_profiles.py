#!/usr/bin/env python3
"""Create Q4 hub composition, typology, and member-tract context artifacts."""
from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd


def write(frame: pd.DataFrame, path: Path) -> None:
    """Write direct pilot artifacts without creating a shared mart."""
    with duckdb.connect() as con:
        con.register("frame", frame)
        con.execute("copy frame to ? (format parquet, compression zstd)", [str(path)])


def main() -> None:
    """Profile every candidate hub and attach descriptive member-tract context."""
    analysis = Path(__file__).parent
    matrix = analysis / "outputs" / "q4_amenity_hub_basket_matrix_v1"
    output = analysis / "outputs" / "q4_epic4_profiles_v1"
    output.mkdir(parents=True, exist_ok=True)
    workbench = analysis / "outputs" / "q4_poi_workbench_v1" / "q4_poi_workbench.parquet"
    with duckdb.connect() as con:
        hubs = con.execute("select * from read_parquet(?)", [str(matrix / "q4_amenity_hub_inventory.parquet")]).fetchdf()
        members = con.execute("select * from read_parquet(?)", [str(matrix / "q4_amenity_hub_membership.parquet")]).fetchdf()
        assignments = con.execute("select source_record_key, tract_geoid from read_parquet(?)", [str(workbench)]).fetchdf()
    keys = ["basket_id", "market_slug", "candidate_version", "amenity_hub_id"]
    members = members.merge(assignments, on="source_record_key", validate="many_to_one")
    tract = members.groupby(keys + ["tract_geoid"], as_index=False).agg(member_poi_count=("source_record_key", "size"))
    totals = members.groupby(keys, as_index=False).agg(hub_member_poi_count=("source_record_key", "size"))
    tract = tract.merge(totals, on=keys, validate="many_to_one")
    tract["member_poi_share"] = tract.member_poi_count / tract.hub_member_poi_count
    tract["association_rule"] = "tract contains one or more POIs assigned to the hub"

    mix = members.groupby(keys + ["category", "sub_category"], as_index=False).agg(poi_count=("source_record_key", "size"))
    category = members.groupby(keys + ["category"], as_index=False).agg(poi_count=("source_record_key", "size"))
    category = category.merge(totals, on=keys, validate="many_to_one")
    category["poi_share"] = category.poi_count / category.hub_member_poi_count
    ordered = category.sort_values(keys + ["poi_share", "category"], ascending=[True] * len(keys) + [False, True])
    signatures = ordered.groupby(keys).agg(
        dominant_category=("category", "first"),
        dominant_category_share=("poi_share", "first"),
        composition_signature=("category", lambda values: " + ".join(values.head(3))),
    ).reset_index()
    diversity = category.groupby(keys, as_index=False).agg(category_hhi=("poi_share", lambda values: float((values ** 2).sum())))
    profiles = hubs.merge(signatures, on=keys, validate="one_to_one").merge(diversity, on=keys, validate="one_to_one")
    profiles["typology"] = profiles.apply(lambda row: f"{row.dominant_category}-led" if row.dominant_category_share >= 0.35 else "mixed composition", axis=1)
    profiles["typology_method"] = "dominant governed category when share >= 35%; otherwise mixed composition"

    db = analysis.parents[3] / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
    with duckdb.connect(str(db), read_only=True) as con:
        con.register("tract", tract[["tract_geoid"]].drop_duplicates())
        context = con.execute("""
            select h.geo_id as tract_geoid, h.year as context_year, h.pop_total,
              g.land_area_sqmi, h.pop_total / nullif(g.land_area_sqmi, 0) as population_density_per_sqmi,
              h.median_gross_rent, h.median_home_value, h.median_hh_income,
              h.pct_rent_burden_30plus, h.pov_rate, h.vacancy_rate, h.renter_occ_rate,
              p.median_age, p.pct_age_under_18, p.pct_age_over_64, p.diversity_index
            from gold.housing_core_wide h
            join tract t on h.geo_id = t.tract_geoid
            join geo.tracts_all_us g on h.geo_id = g.tract_geoid
            left join gold.population_demographics p on h.geo_id = p.geo_id and h.year = p.year and p.geo_level = 'tract'
            where h.geo_level = 'tract'
              and h.year = (select max(year) from gold.housing_core_wide where geo_level = 'tract')
        """).fetchdf()
    tract_context = tract.merge(context, on="tract_geoid", how="left", validate="many_to_one")
    write(mix, output / "q4_hub_composition_profile.parquet")
    write(profiles, output / "q4_hub_typology_profile.parquet")
    write(tract, output / "q4_hub_tract_association.parquet")
    write(tract_context, output / "q4_hub_tract_context.parquet")
    (output / "README.md").write_text("""# Q4 Epic 4 pilot profiles

These are direct, unpromoted Q4 artifacts. A tract is associated only when it
contains one or more POIs assigned to a hub; `member_poi_share` reports its
share of that hub's POI membership. Context is descriptive only and does not
represent a service area, resident access, causation, routing, or barriers.

Typology is a transparent composition label: a hub is `<category>-led` if its
largest governed category is at least 35% of member POIs; otherwise it is
`mixed composition`. The full category/subcategory profile remains the evidence.
""")
    (output / "manifest.json").write_text(json.dumps({"status": "pilot_artifacts_direct_not_promoted", "association_rule": "member POI tract assignment", "typology_method": "dominant category >= 35% else mixed composition", "context_source": "gold.housing_core_wide latest tract year", "hub_profiles": len(profiles), "tract_associations": len(tract)}, indent=2) + "\n")


if __name__ == "__main__":
    main()
