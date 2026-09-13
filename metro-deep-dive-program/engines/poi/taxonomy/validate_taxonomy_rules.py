#!/usr/bin/env python3
"""Validate a taxonomy rule seed against a classified run.

Read-only. Makes no mapping decision and writes no governed output. It answers
one question: does this seed, as written, assign every place in the data to
exactly one Category and Sub Category, and does it say what the v1 documents
say?

Checks, in the order a reviewer cares about:

  coverage      every source_category_basic in the data has a rule
  orphan        every rule matches something in the data
  completeness  every place lands in a category (or an explicit null state)
  splits        every [T] split leaf exists; unsplit leaves land on the default
  integrity     sub_category names are unique across categories, as the docs require
  drift         basics and leaves present here but absent from a baseline run
  review        rules carrying a `review:` flag, surfaced rather than buried
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import duckdb
import yaml

ENGINE_DIR = Path(__file__).resolve().parents[1]
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from normalize_overture_places import latest_source_run
from acquire_overture_places import ENGINE_DIR, sql_literal


def load_rules(path: Path) -> dict:
    """Read the seed and expand it into flat lookup tables."""

    seed = yaml.safe_load(path.read_text(encoding="utf-8"))
    base: dict[str, dict] = {}
    splits: dict[tuple[str, str], dict] = {}

    for rule in seed["rules"]:
        basic = rule["basic"]
        if basic in base:
            raise ValueError(f"Duplicate rule for basic '{basic}' — the seed must be a function.")
        base[basic] = {
            "category": rule["category"],
            "sub_category": rule["sub_category"],
            "review": rule.get("review"),
        }
        for leaf, target in (rule.get("split") or {}).items():
            # A split may override category, sub_category, or both. Anything
            # it does not name falls back to the row default.
            splits[(basic, leaf)] = {
                "category": target.get("category", rule["category"]),
                "sub_category": target.get("sub_category", rule["sub_category"]),
            }
    return {"seed": seed, "base": base, "splits": splits}


def assignment_sql(classified: str, rules: dict) -> str:
    """Build the CASE expression that applies the seed to the data."""

    base_values = ", ".join(
        "(" + ", ".join(sql_literal(v) for v in (basic, r["category"], r["sub_category"])) + ")"
        for basic, r in rules["base"].items()
    )
    split_values = ", ".join(
        "(" + ", ".join(sql_literal(v) for v in (basic, leaf, t["category"], t["sub_category"])) + ")"
        for (basic, leaf), t in rules["splits"].items()
    ) or "(NULL, NULL, NULL, NULL)"

    return f"""
    WITH base(basic, category, sub_category) AS (VALUES {base_values}),
    split(basic, leaf, category, sub_category) AS (VALUES {split_values}),
    place AS (
        SELECT source_category_basic, source_taxonomy_primary,
               source_taxonomy_hierarchy
        FROM read_parquet({sql_literal(classified)})
    )
    SELECT
        p.source_category_basic,
        p.source_taxonomy_primary,
        -- Split wins over the row default; absent both, the place is unassigned.
        coalesce(s.category, b.category) AS category,
        coalesce(s.sub_category, b.sub_category) AS sub_category,
        CASE
            WHEN p.source_category_basic IS NULL THEN 'no_source_signal'
            WHEN b.basic IS NULL THEN 'no_rule'
            WHEN s.basic IS NOT NULL THEN 'split'
            ELSE 'base'
        END AS assignment_path
    FROM place p
    LEFT JOIN base b ON p.source_category_basic = b.basic
    LEFT JOIN split s
        ON p.source_category_basic = s.basic
       AND p.source_taxonomy_primary = s.leaf
    """


def main() -> None:
    """Validate the seed and report every failure mode separately."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True)
    parser.add_argument("--source-run-dir", type=Path)
    parser.add_argument("--output-root", type=Path, default=ENGINE_DIR / "outputs")
    parser.add_argument("--rules", type=Path, default=Path(__file__).parent / "overture_taxonomy.yml")
    parser.add_argument("--baseline-run-dir", type=Path)
    parser.add_argument("--write-profile", action="store_true",
                        help="Write the assignment result for notebook review.")
    args = parser.parse_args()

    source_dir = args.source_run_dir or latest_source_run(args.output_root, args.market)
    classified = source_dir / "classified" / "poi_classified_place.parquet"
    if not classified.exists():
        raise FileNotFoundError("Run classification before validating rules.")

    rules = load_rules(args.rules)
    query = assignment_sql(str(classified), rules)
    report: dict[str, object] = {
        "market": args.market,
        "run": source_dir.name,
        "mapping_version": rules["seed"]["mapping_version"],
        "rule_count": len(rules["base"]),
        "split_count": len(rules["splits"]),
    }
    failures: list[str] = []

    with duckdb.connect() as con:
        total = con.execute(
            f"SELECT count(*) FROM read_parquet({sql_literal(str(classified))})"
        ).fetchone()[0]
        report["places"] = total

        paths = dict(con.execute(
            f"SELECT assignment_path, count(*) FROM ({query}) GROUP BY 1"
        ).fetchall())
        report["assignment_paths"] = paths

        # Coverage: a basic in the data with no rule is an unassigned place.
        no_rule = con.execute(f"""
            SELECT source_category_basic, count(*) n FROM ({query})
            WHERE assignment_path = 'no_rule' GROUP BY 1 ORDER BY n DESC
        """).fetchall()
        report["basics_without_rule"] = [{"basic": b, "places": n} for b, n in no_rule]
        if no_rule:
            failures.append(
                f"{len(no_rule)} basic value(s) have no rule, "
                f"covering {sum(n for _, n in no_rule):,} places"
            )

        # Orphans: a rule matching nothing is dead weight or a typo.
        in_data = {
            row[0] for row in con.execute(
                f"SELECT DISTINCT source_category_basic "
                f"FROM read_parquet({sql_literal(str(classified))}) "
                "WHERE source_category_basic IS NOT NULL"
            ).fetchall()
        }
        orphans = sorted(set(rules["base"]) - in_data)
        report["rules_matching_nothing"] = orphans

        # Split leaves that do not occur: usually a misspelled leaf.
        leaves = {
            row[0] for row in con.execute(
                f"SELECT DISTINCT source_taxonomy_primary "
                f"FROM read_parquet({sql_literal(str(classified))}) "
                "WHERE source_taxonomy_primary IS NOT NULL"
            ).fetchall()
        }
        dead_splits = sorted(
            f"{basic}/{leaf}" for (basic, leaf) in rules["splits"] if leaf not in leaves
        )
        report["split_leaves_matching_nothing"] = dead_splits

        # Integrity: the docs require sub_category names unique across the
        # whole taxonomy, so a fully-qualified path is never needed. The
        # shared bucket names are the documented exception — cross-cutting
        # rule 1 gives every category its own Unspecified.
        shared_names = (
            rules["seed"].get("defaults", {}).get("unspecified_sub_category", "Unspecified"),
            "Other & Unspecified",
        )
        shared = ", ".join(sql_literal(name) for name in shared_names)
        collisions = con.execute(f"""
            SELECT sub_category, count(DISTINCT category) c,
                   string_agg(DISTINCT category, ' | ') cats
            FROM ({query})
            WHERE sub_category IS NOT NULL AND sub_category NOT IN ({shared})
            GROUP BY 1 HAVING count(DISTINCT category) > 1 ORDER BY c DESC
        """).fetchall()
        report["sub_category_collisions"] = [
            {"sub_category": s, "categories": cats} for s, _, cats in collisions
        ]
        if collisions:
            failures.append(
                f"{len(collisions)} sub_category name(s) appear under more than one "
                "category; the v1 docs require uniqueness"
            )

        # Placeholders the seed author could not resolve from the docs.
        unresolved = con.execute(f"""
            SELECT sub_category, count(*) n FROM ({query})
            WHERE sub_category LIKE 'UNRESOLVED%' GROUP BY 1 ORDER BY n DESC
        """).fetchall()
        report["unresolved"] = [{"sub_category": s, "places": n} for s, n in unresolved]

        # Rules flagged for review because the docs do not cover them.
        flagged = [
            {"basic": b, "category": r["category"], "sub_category": r["sub_category"],
             "reason": r["review"]}
            for b, r in rules["base"].items() if r["review"]
        ]
        report["flagged_for_review"] = flagged

        # The realized shape, for the notebook to render.
        report["categories"] = [
            {"category": c, "sub_categories": s, "places": n}
            for c, s, n in con.execute(f"""
                SELECT category, count(DISTINCT sub_category), count(*) n
                FROM ({query}) WHERE category IS NOT NULL
                GROUP BY 1 ORDER BY n DESC
            """).fetchall()
        ]

        if args.baseline_run_dir:
            baseline = args.baseline_run_dir / "classified" / "poi_classified_place.parquet"
            if not baseline.exists():
                raise FileNotFoundError(f"Missing baseline run: {baseline}")
            new_basics = con.execute(f"""
                SELECT DISTINCT source_category_basic FROM read_parquet({sql_literal(str(classified))})
                WHERE source_category_basic IS NOT NULL AND source_category_basic NOT IN (
                    SELECT source_category_basic FROM read_parquet({sql_literal(str(baseline))})
                    WHERE source_category_basic IS NOT NULL)
                ORDER BY 1
            """).fetchall()
            report["new_basics_vs_baseline"] = [row[0] for row in new_basics]
            unruled = [b for (b,) in new_basics if b not in rules["base"]]
            if unruled:
                failures.append(
                    f"{len(unruled)} basic value(s) new vs baseline have no rule: "
                    f"{', '.join(unruled)}"
                )

        if args.write_profile:
            out = source_dir / "classified" / "taxonomy_profile"
            out.mkdir(exist_ok=True)
            con.execute(
                f"COPY ({query}) TO {sql_literal(str(out / 'poi_taxonomy_assignment.parquet'))} "
                "(FORMAT PARQUET, COMPRESSION ZSTD)"
            )
            # The rules themselves are not written out. The YAML seed is the
            # single source of truth: the classifier reads it, the notebook
            # reads it, and a published copy could only drift from it.

    report["failures"] = failures
    report["status"] = "fail" if failures else "pass"

    out_dir = source_dir / "classified" / "taxonomy_profile"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "taxonomy_validation_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )

    assigned = total - paths.get("no_rule", 0) - paths.get("no_source_signal", 0)
    print(f"{rules['seed']['mapping_version']} on {args.market}: "
          f"{len(rules['base'])} rules, {len(rules['splits'])} splits")
    print(f"Assigned {assigned:,} of {total:,} places "
          f"({100 * assigned / total:.1f}%); "
          f"{paths.get('split', 0):,} via a split rule")
    for key, label in (
        ("basics_without_rule", "basics with no rule"),
        ("rules_matching_nothing", "rules matching nothing"),
        ("split_leaves_matching_nothing", "split leaves matching nothing"),
        ("sub_category_collisions", "sub_category name collisions"),
        ("unresolved", "unresolved placeholders"),
        ("flagged_for_review", "rules flagged for review"),
    ):
        value = report.get(key) or []
        if value:
            print(f"  {len(value)} {label}")
    print("STATUS:", report["status"].upper())
    for failure in failures:
        print("  FAIL:", failure)


if __name__ == "__main__":
    main()
