import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def imports():
    import os
    from pathlib import Path

    import duckdb
    import marimo as mo
    return Path, duckdb, mo, os


@app.cell
def resolve_database(Path, os):
    # The notebook consumes managed DuckDB serving tables, not local artifacts.
    root = Path(__file__).resolve().parents[4]
    configured = os.environ.get("DB_PATH", "").strip()
    if configured:
        db_path = configured
    else:
        db_path = next(
            line.split("=", 1)[1].strip().strip('"')
            for line in (root / ".Renviron").read_text().splitlines()
            if line.startswith("DB_PATH=")
        )
    return (db_path,)


@app.cell
def intro(mo):
    mo.md("""
    # POI Taxonomy Review

    Two tables. **Rules** is the taxonomy as written in `overture_taxonomy.yml`,
    which encodes the v1 category and sub-category documents and is read here
    straight from that file — the same file the classifier applies, so the two
    cannot drift. **Counts** is what those rules assign in the published market.

    A rule with zero places in this market is not a problem: the market may
    genuinely lack that tag. A rule with zero places in *every* market is a
    mistake, and the validator reports it separately.
    """)
    return


@app.cell
def load_rules(Path):
    # The YAML seed is the contract. It is read directly here rather than from a
    # published copy, so the notebook can never show rules that have drifted
    # from what the classifier actually applies.
    import pandas as pd
    import yaml

    seed_path = Path(__file__).parent / "overture_taxonomy.yml"
    seed = yaml.safe_load(seed_path.read_text(encoding="utf-8"))

    rows = []
    for rule in seed["rules"]:
        rows.append({
            "category": rule["category"],
            "sub_category": rule["sub_category"],
            "source_category_basic": rule["basic"],
            "split_leaf": None,
            "review": rule.get("review"),
        })
        for leaf, target in (rule.get("split") or {}).items():
            rows.append({
                "category": target.get("category", rule["category"]),
                "sub_category": target.get("sub_category", rule["sub_category"]),
                "source_category_basic": rule["basic"],
                "split_leaf": leaf,
                "review": "split",
            })
    rules = pd.DataFrame(rows).sort_values(
        ["category", "sub_category", "source_category_basic", "split_leaf"],
        na_position="first",
    ).reset_index(drop=True)
    return rules, seed


@app.cell
def load_counts(db_path, duckdb):
    with duckdb.connect(db_path, read_only=True) as con:
        counts = con.execute("""
            SELECT category, sub_category,
                   count(*) AS places,
                   count(taxonomy_detail) AS with_detail
            FROM mart_poi.poi_classified_place
            WHERE mapping_status = 'mapped'
            GROUP BY ALL
            ORDER BY category, places DESC
        """).fetchdf()
        by_category = con.execute("""
            SELECT category,
                   count(DISTINCT sub_category) AS sub_categories,
                   count(*) AS places,
                   round(100.0 * count(taxonomy_detail) / count(*), 1) AS detail_pct
            FROM mart_poi.poi_classified_place
            WHERE mapping_status = 'mapped'
            GROUP BY ALL
            ORDER BY places DESC
        """).fetchdf()
        unassigned = con.execute("""
            SELECT mapping_evidence, count(*) AS places
            FROM mart_poi.poi_classified_place
            WHERE mapping_status = 'unmapped'
            GROUP BY ALL
            ORDER BY places DESC
        """).fetchdf()
    return by_category, counts, unassigned


@app.cell
def show_rules(mo, rules):
    mo.vstack([
        mo.md(f"## Rules — {len(rules):,} rows"),
        mo.md(
            "One row per rule. `split_leaf` is set only where the v1 docs marked "
            "a row `[T]`, meaning the sub-category is decided by "
            "`taxonomy.primary` rather than by `basic_category` alone. `review` "
            "flags a rule not covered by either v1 document."
        ),
        mo.ui.table(rules, pagination=True, page_size=25),
    ])
    return


@app.cell
def show_counts(by_category, counts, mo, unassigned):
    mo.vstack([
        mo.md("## Counts — places assigned in this market"),
        mo.md(
            "`detail_pct` is level 3 coverage: the share of places whose source "
            "leaf adds something beyond the browsable node. Level 3 is optional "
            "and analysis-specific, so a low share here is a fact about the "
            "source, not a defect."
        ),
        mo.md("### By category"),
        mo.ui.table(by_category, pagination=True, page_size=25),
        mo.md("### By sub-category"),
        mo.ui.table(counts, pagination=True, page_size=25),
        mo.md("### Unmapped"),
        mo.ui.table(unassigned),
    ])
    return


if __name__ == "__main__":
    app.run()
