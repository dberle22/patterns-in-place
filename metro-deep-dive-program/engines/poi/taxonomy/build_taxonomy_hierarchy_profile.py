#!/usr/bin/env python3
"""Profile the Overture taxonomy hierarchy as a monitored three-level workbook.

Read-only. Makes no mapping decision. Emits the evidence needed to review,
seed, and monitor the governed taxonomy described in TAXONOMY.md:

  layer_invariant   the two structural checks the rule depends on
  category_root     hierarchy[1] -> Category seed candidate (13 rows)
  subcategory       hierarchy[2] -> Sub Category seed candidate (~112 rows)
  split_candidate   depth-2 nodes whose leaves cross a governed boundary
  detail_coverage   where the leaf adds nothing beyond the browsable node
  null_state        the three distinct null states, kept separate
  hierarchy_tag     the original tag x depth profile, retained
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import duckdb

ENGINE_DIR = Path(__file__).resolve().parents[1]
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from normalize_overture_places import latest_source_run
from acquire_overture_places import ENGINE_DIR, sql_literal

# Depth-2 nodes known to span more than one governed Category. Their leaves
# decide, so they are reported leaf-by-leaf for review rather than rolled up.
# Growth in this list is a signal that a Category boundary is drawn wrong.
SPLIT_NODES = (
    "financial_service",
    "animal_or_pet_service",
    "shipping_or_delivery_service",
    "family_service",
    "research_institute",
    "sport_or_fitness_facility",
)


def profile_queries(classified: str) -> dict[str, str]:
    """Build one read-only query per workbook surface."""

    source = f"read_parquet({sql_literal(classified)})"
    split_list = ", ".join(sql_literal(node) for node in SPLIT_NODES)

    return {
        # The mechanism in TAXONOMY.md holds only while both of these
        # are true for every non-null row. A false row is a hard stop.
        "layer_invariant": f"""
            SELECT
                list_contains(source_taxonomy_hierarchy, source_category_basic) AS basic_on_path,
                source_taxonomy_hierarchy[-1] = source_taxonomy_primary AS leaf_is_taxonomy_primary,
                count(*) AS place_count
            FROM {source}
            WHERE source_taxonomy_hierarchy IS NOT NULL
            GROUP BY ALL
            ORDER BY place_count DESC
        """,
        # Category seed candidate. A new root is a decision, not a default.
        "category_root": f"""
            SELECT
                source_taxonomy_hierarchy[1] AS hierarchy_root,
                count(*) AS place_count,
                count(DISTINCT source_taxonomy_hierarchy[2]) AS subcategory_count,
                count(DISTINCT source_category_basic) AS basic_count,
                count(DISTINCT source_taxonomy_primary) AS leaf_count
            FROM {source}
            WHERE source_taxonomy_hierarchy IS NOT NULL
            GROUP BY ALL
            ORDER BY place_count DESC
        """,
        # Sub Category seed candidate, carried with its root for review.
        "subcategory": f"""
            SELECT
                source_taxonomy_hierarchy[1] AS hierarchy_root,
                source_taxonomy_hierarchy[2] AS hierarchy_level_2,
                count(*) AS place_count,
                count(DISTINCT source_taxonomy_primary) AS leaf_count
            FROM {source}
            WHERE len(source_taxonomy_hierarchy) >= 2
            GROUP BY ALL
            ORDER BY hierarchy_root, place_count DESC
        """,
        # Leaf detail for the nodes that cross a governed Category boundary.
        "split_candidate": f"""
            SELECT
                source_taxonomy_hierarchy[2] AS hierarchy_level_2,
                source_taxonomy_primary AS leaf,
                count(*) AS place_count
            FROM {source}
            WHERE len(source_taxonomy_hierarchy) >= 2
              AND source_taxonomy_hierarchy[2] IN ({split_list})
            GROUP BY ALL
            ORDER BY hierarchy_level_2, place_count DESC
        """,
        # Where the leaf equals the browsable node, no Detailed Category
        # exists. This is a coverage metric, not a defect.
        "detail_coverage": f"""
            SELECT
                source_category_basic,
                count(*) AS place_count
            FROM {source}
            WHERE source_category_basic = source_taxonomy_primary
            GROUP BY ALL
            ORDER BY place_count DESC
        """,
        # Three states the review CSV collapsed into one. Keep them apart:
        # no signal, partial signal, and full signal are different problems.
        "null_state": f"""
            SELECT
                CASE
                    WHEN source_category_basic IS NULL AND source_taxonomy_primary IS NULL
                        THEN 'no_source_signal'
                    WHEN source_taxonomy_primary IS NULL
                        THEN 'basic_only'
                    ELSE 'full_signal'
                END AS null_state,
                source_category_basic,
                count(*) AS place_count
            FROM {source}
            GROUP BY ALL
            ORDER BY null_state, place_count DESC
        """,
        # The original surface, unchanged: every tag with its depth.
        "hierarchy_tag": f"""
            WITH tagged AS (
                SELECT
                    source_category_basic,
                    source_taxonomy_primary,
                    category,
                    sub_category,
                    mapping_status,
                    tag_index AS hierarchy_depth,
                    hierarchy_tag,
                    source_record_key
                FROM {source},
                UNNEST(source_taxonomy_hierarchy) WITH ORDINALITY AS tags(hierarchy_tag, tag_index)
                WHERE hierarchy_tag IS NOT NULL AND trim(hierarchy_tag) <> ''
            )
            SELECT
                source_category_basic,
                source_taxonomy_primary,
                category,
                sub_category,
                mapping_status,
                hierarchy_depth,
                hierarchy_tag,
                count(*) AS place_count,
                count(DISTINCT source_record_key) AS distinct_place_count
            FROM tagged
            GROUP BY ALL
            ORDER BY place_count DESC, hierarchy_tag
        """,
    }


def reconcile(con: duckdb.DuckDBPyConnection, classified: str, baseline: str) -> dict:
    """Compare this run's vocabulary to a prior run at each hierarchy level.

    A new root blocks publication; a new depth-2 value needs a seed entry; a
    new leaf alone is safe. This is the quarterly Overture release check.
    """

    current = f"read_parquet({sql_literal(classified)})"
    prior = f"read_parquet({sql_literal(baseline)})"
    levels = {
        "root": "source_taxonomy_hierarchy[1]",
        "level_2": "source_taxonomy_hierarchy[2]",
        "leaf": "source_taxonomy_primary",
    }

    drift: dict[str, dict] = {}
    for level, expression in levels.items():
        added = con.execute(f"""
            SELECT DISTINCT {expression} AS value FROM {current}
            WHERE {expression} IS NOT NULL
              AND {expression} NOT IN (
                SELECT {expression} FROM {prior} WHERE {expression} IS NOT NULL
              )
            ORDER BY value
        """).fetchall()
        removed = con.execute(f"""
            SELECT DISTINCT {expression} AS value FROM {prior}
            WHERE {expression} IS NOT NULL
              AND {expression} NOT IN (
                SELECT {expression} FROM {current} WHERE {expression} IS NOT NULL
              )
            ORDER BY value
        """).fetchall()
        drift[level] = {
            "added": [row[0] for row in added],
            "removed": [row[0] for row in removed],
        }
    return drift


def main() -> None:
    """Emit the taxonomy workbook surfaces for one classified run."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True)
    parser.add_argument("--source-run-dir", type=Path)
    parser.add_argument("--output-root", type=Path, default=ENGINE_DIR / "outputs")
    parser.add_argument(
        "--baseline-run-dir",
        type=Path,
        help="Prior classified run to reconcile vocabulary against.",
    )
    args = parser.parse_args()

    source_dir = args.source_run_dir or latest_source_run(args.output_root, args.market)
    classified = source_dir / "classified" / "poi_classified_place.parquet"
    if not classified.exists():
        raise FileNotFoundError("Run classification before profiling hierarchy tags.")
    output_dir = source_dir / "classified" / "taxonomy_profile"
    output_dir.mkdir(exist_ok=True)

    queries = profile_queries(str(classified))
    summary: dict[str, object] = {"market": args.market, "run": source_dir.name}

    with duckdb.connect() as con:
        for name, query in queries.items():
            destination = output_dir / f"poi_taxonomy_{name}.parquet"
            con.execute(
                f"COPY ({query}) TO {sql_literal(str(destination))} "
                "(FORMAT PARQUET, COMPRESSION ZSTD)"
            )
            summary[f"{name}_rows"] = con.execute(
                f"SELECT count(*) FROM ({query})"
            ).fetchone()[0]

        # The invariant gate. Anything other than a single all-true group means
        # the hierarchy is no longer a strict rollup path and the rule in
        # TAXONOMY.md does not hold for this release.
        invariant = con.execute(f"""
            SELECT
                coalesce(sum(CASE WHEN basic_on_path AND leaf_is_taxonomy_primary
                    THEN place_count ELSE 0 END), 0) AS holds,
                coalesce(sum(CASE WHEN basic_on_path AND leaf_is_taxonomy_primary
                    THEN 0 ELSE place_count END), 0) AS violates
            FROM ({queries['layer_invariant']})
        """).fetchone()
        summary["invariant_holds"] = invariant[0]
        summary["invariant_violations"] = invariant[1]

        detail_missing = con.execute(
            f"SELECT coalesce(sum(place_count), 0) FROM ({queries['detail_coverage']})"
        ).fetchone()[0]
        total = con.execute(
            f"SELECT count(*) FROM read_parquet({sql_literal(str(classified))})"
        ).fetchone()[0]
        summary["places"] = total
        summary["places_without_detail"] = detail_missing
        summary["detail_coverage_pct"] = round(100 * (total - detail_missing) / total, 1)

        if args.baseline_run_dir:
            baseline = args.baseline_run_dir / "classified" / "poi_classified_place.parquet"
            if not baseline.exists():
                raise FileNotFoundError(f"Missing baseline classified run: {baseline}")
            summary["vocabulary_drift"] = reconcile(con, str(classified), str(baseline))

    (output_dir / "taxonomy_profile_manifest.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Places: {total:,}  Detailed-category coverage: {summary['detail_coverage_pct']}%")
    if summary["invariant_violations"]:
        print(
            f"INVARIANT VIOLATED on {summary['invariant_violations']:,} places. "
            "The hierarchy is not a strict rollup path for this release. "
            "Do not seed or publish from it."
        )
    else:
        print(f"Invariants hold on {summary['invariant_holds']:,} places.")

    drift = summary.get("vocabulary_drift")
    if drift:
        for level in ("root", "level_2", "leaf"):
            added, removed = drift[level]["added"], drift[level]["removed"]
            print(f"{level}: +{len(added)} new, -{len(removed)} retired")
        if drift["root"]["added"]:
            print(f"NEW ROOT: {', '.join(drift['root']['added'])} — Category decision required.")
        if drift["level_2"]["added"]:
            print(f"New sub-category values need a seed entry: {len(drift['level_2']['added'])}.")


if __name__ == "__main__":
    main()
