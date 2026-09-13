#!/usr/bin/env python3
"""Apply the approved governed taxonomy to one normalized source run.

Assignment is keyed on `source_category_basic`, the current Overture property,
as the v1 category and sub-category documents specify. Rules the documents mark
[T] carry a split keyed on `source_taxonomy_primary`; a split wins over its row
default. Level 3 (`taxonomy_detail`) is a passthrough of the source leaf and is
null where the leaf adds nothing beyond the browsable node.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb
import yaml

from normalize_overture_places import latest_source_run
from acquire_overture_places import ENGINE_DIR, sql_literal


def rule_tables(seed: dict) -> tuple[str, str]:
    """Expand the seed into base and split VALUES lists."""

    base: list[tuple[str, str, str, str]] = []
    split: list[tuple[str, str, str, str, str]] = []

    for rule in seed["rules"]:
        basic = rule["basic"]
        rule_id = f"basic_{basic}"
        base.append((basic, rule_id, rule["category"], rule["sub_category"]))
        for leaf, target in (rule.get("split") or {}).items():
            split.append((
                basic,
                leaf,
                f"basic_{basic}__leaf_{leaf}",
                target.get("category", rule["category"]),
                target.get("sub_category", rule["sub_category"]),
            ))

    base_values = ", ".join(
        "(" + ", ".join(sql_literal(v) for v in row) + ")" for row in base
    )
    split_values = ", ".join(
        "(" + ", ".join(sql_literal(v) for v in row) + ")" for row in split
    ) or "(NULL, NULL, NULL, NULL, NULL)"
    return base_values, split_values


def classify_sql(normalized: Path, seed: dict) -> str:
    """Build the governed classification query for one normalized run."""

    base_values, split_values = rule_tables(seed)
    version = sql_literal(seed["mapping_version"])
    unclassified = sql_literal(
        seed.get("defaults", {}).get("unclassified_category", "Unclassified")
    )

    return f"""
    WITH base(basic, rule_id, category, sub_category) AS (VALUES {base_values}),
    split(basic, leaf, rule_id, category, sub_category) AS (VALUES {split_values})
    SELECT
        p.*,
        {version} AS mapping_version,
        CASE
            WHEN p.source_category_basic IS NULL THEN 'unmapped'
            WHEN b.basic IS NULL THEN 'unmapped'
            ELSE 'mapped'
        END AS mapping_status,
        coalesce(s.rule_id, b.rule_id) AS mapping_rule_id,
        -- Level 1 and 2 are governed. A split rule wins over its row default.
        coalesce(s.category, b.category,
            CASE WHEN p.source_category_basic IS NULL THEN {unclassified} END
        ) AS category,
        coalesce(s.sub_category, b.sub_category) AS sub_category,
        -- Level 3 is an optional passthrough for specific analyses. It is null
        -- where the source leaf is the browsable node, meaning no finer detail
        -- exists, and null where the source supplied no taxonomy at all.
        CASE
            WHEN p.source_taxonomy_primary IS NULL THEN NULL
            WHEN p.source_taxonomy_primary = p.source_category_basic THEN NULL
            ELSE p.source_taxonomy_primary
        END AS taxonomy_detail,
        CASE
            WHEN s.rule_id IS NOT NULL
                THEN concat('basic = ', p.source_category_basic,
                            ' split on taxonomy.primary = ', p.source_taxonomy_primary)
            WHEN b.rule_id IS NOT NULL
                THEN concat('basic = ', p.source_category_basic)
            WHEN p.source_category_basic IS NULL
                THEN 'no source category'
            ELSE concat('no rule for basic = ', p.source_category_basic)
        END AS mapping_evidence,
        CASE WHEN b.basic IS NULL THEN 'needs_review' ELSE 'approved_rule' END AS review_status
    FROM read_parquet({sql_literal(str(normalized))}) p
    LEFT JOIN base b ON p.source_category_basic = b.basic
    LEFT JOIN split s
        ON p.source_category_basic = s.basic
       AND p.source_taxonomy_primary = s.leaf
    """


def main() -> None:
    """Classify one normalized run and write its review artifacts."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True)
    parser.add_argument("--source-run-dir", type=Path)
    parser.add_argument("--output-root", type=Path, default=ENGINE_DIR / "outputs")
    parser.add_argument(
        "--rules", type=Path, default=ENGINE_DIR / "taxonomy" / "overture_taxonomy.yml"
    )
    args = parser.parse_args()

    source_dir = args.source_run_dir or latest_source_run(args.output_root, args.market)
    normalized = source_dir / "normalized" / "poi_source_place.parquet"
    if not normalized.exists():
        raise FileNotFoundError(f"Missing normalized run: {normalized}")

    seed = yaml.safe_load(args.rules.read_text(encoding="utf-8"))
    seen: set[str] = set()
    for rule in seed["rules"]:
        if rule["basic"] in seen:
            raise ValueError(
                f"Duplicate rule for basic '{rule['basic']}' — the seed must be a function."
            )
        seen.add(rule["basic"])

    query = classify_sql(normalized, seed)
    out = source_dir / "classified"
    out.mkdir(exist_ok=True)

    with duckdb.connect() as con:
        con.execute(
            f"COPY ({query}) TO {sql_literal(str(out / 'poi_classified_place.parquet'))} "
            "(FORMAT PARQUET, COMPRESSION ZSTD)"
        )
        # Unmapped places are retained, never dropped. A row here is either a
        # null source category or a basic value with no rule.
        con.execute(
            f"COPY (SELECT * FROM ({query}) WHERE mapping_status = 'unmapped') "
            f"TO {sql_literal(str(out / 'poi_unmapped_review.parquet'))} "
            "(FORMAT PARQUET, COMPRESSION ZSTD)"
        )
        # One basic resolves to exactly one rule, so an automated ambiguous
        # match cannot occur. The artifact stays for future mapping versions.
        con.execute(
            f"COPY (SELECT * FROM ({query}) WHERE FALSE) "
            f"TO {sql_literal(str(out / 'poi_ambiguous_review.parquet'))} "
            "(FORMAT PARQUET, COMPRESSION ZSTD)"
        )
        counts = dict(con.execute(
            f"SELECT mapping_status, count(*) FROM ({query}) GROUP BY 1"
        ).fetchall())
        levels = con.execute(f"""
            SELECT
                count(DISTINCT category) AS categories,
                count(DISTINCT sub_category) AS sub_categories,
                count(taxonomy_detail) AS places_with_detail,
                count(*) AS places
            FROM ({query})
        """).fetchone()

    manifest = {
        "mapping_version": seed["mapping_version"],
        "taxonomy_version": seed.get("taxonomy_version"),
        "source_release": seed.get("source_release"),
        "rules": len(seed["rules"]),
        "counts": counts,
        "categories": levels[0],
        "sub_categories": levels[1],
        "places_with_taxonomy_detail": levels[2],
        "detail_coverage_pct": round(100 * levels[2] / levels[3], 1),
        "note": "Levels 1-2 governed from source_category_basic; level 3 is an optional source passthrough.",
    }
    (out / "classification_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
