import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This notebook is read-only by design. It profiles source labels and
    # review queues; production rules change only after a human decision.
    from pathlib import Path

    import duckdb
    import marimo as mo
    import pandas as pd
    import yaml

    return Path, duckdb, mo, pd, yaml


@app.cell
def _(Path):
    engine_dir = Path(__file__).resolve().parents[1]
    output_root = engine_dir / "outputs"
    richmond_runs = sorted((output_root / "richmond_va").glob("*/classified/poi_classified_place.parquet"))
    if not richmond_runs:
        raise FileNotFoundError("Run POI acquisition, normalization, and classification for Richmond first.")
    classified_path = richmond_runs[-1]
    return (classified_path,)


@app.cell
def _(mo):
    mo.md("""
    # POI Taxonomy Exploration

    This is a review surface for expanding governed POI categories safely. It
    profiles Overture's preserved labels and names; it does not write mapping
    rules, change classified records, or define Q4's `daily_needs` basket.
    Promote a value only after inspecting its count and examples, then add an
    exact rule in a new versioned YAML registry.
    """)
    return


@app.cell
def _(Path, pd, yaml):
    # The registry is shown in the notebook so reviewers can see the current
    # governed taxonomy before proposing additions from the source profile.
    registry_path = Path(__file__).resolve().parent / "q4_overture_v2.yml"
    registry = yaml.safe_load(registry_path.read_text())
    current_taxonomy = pd.DataFrame(registry["rules"])[
        ["governed_category", "source_taxonomy_primary", "rule_id"]
    ].sort_values(["governed_category", "source_taxonomy_primary"])
    current_taxonomy
    return current_taxonomy, registry


@app.cell
def _(classified_path, duckdb):
    # One read-only connection keeps the source record, mapping result, and
    # taxonomy labels visible together without copying data into a notebook.
    def profile(sql):
        with duckdb.connect() as con:
            return con.execute(sql, [str(classified_path)]).fetchdf()

    return (profile,)


@app.cell
def _(profile):
    coverage = profile("""
        SELECT mapping_status, count(*) AS places
        FROM read_parquet(?) GROUP BY 1 ORDER BY places DESC
    """)
    coverage
    return (coverage,)


@app.cell
def _(profile):
    # This is the current taxonomy in use on the run, organized by Overture's
    # broad basic-category family and then the governed category it supports.
    current_taxonomy_coverage = profile("""
        SELECT source_category_basic, governed_category, count(*) AS places,
          count(DISTINCT source_taxonomy_primary) AS source_labels
        FROM read_parquet(?)
        WHERE mapping_status = 'mapped'
        GROUP BY 1, 2 ORDER BY source_category_basic, places DESC
    """)
    current_taxonomy_coverage
    return (current_taxonomy_coverage,)


@app.cell
def _(profile):
    # Start with high-volume unmapped values: these are the easiest candidates
    # for an exact, evidence-backed rule or an intentional exclusion decision.
    unmapped_categories = profile("""
        SELECT source_taxonomy_primary, source_category_basic, count(*) AS places,
          count(DISTINCT source_name) AS distinct_names
        FROM read_parquet(?)
        WHERE mapping_status = 'unmapped'
        GROUP BY 1, 2 ORDER BY places DESC LIMIT 100
    """)
    unmapped_categories
    return (unmapped_categories,)


@app.cell
def _(profile):
    # Basic categories are the review navigation layer: they group precise
    # taxonomy.primary values without weakening the exact production match.
    unmapped_basic_categories = profile("""
        SELECT source_category_basic, count(*) AS places,
          count(DISTINCT source_taxonomy_primary) AS taxonomy_labels
        FROM read_parquet(?)
        WHERE mapping_status = 'unmapped'
        GROUP BY 1 ORDER BY places DESC LIMIT 100
    """)
    unmapped_basic_categories
    return (unmapped_basic_categories,)


@app.cell
def _(mo, unmapped_categories):
    options = {f"{row.source_taxonomy_primary or '(missing taxonomy)'} — {row.places:,}": row.source_taxonomy_primary for row in unmapped_categories.itertuples(index=False)}
    category_selector = mo.ui.dropdown(options=options, label="Inspect an unmapped taxonomy.primary value", searchable=True, full_width=True)
    category_selector
    return (category_selector,)


@app.cell
def _(category_selector, classified_path, duckdb):
    selected = category_selector.value
    with duckdb.connect() as con:
        examples = con.execute("""
            SELECT source_name, source_address, source_postal_zip,
              source_category_primary, source_category_basic,
              source_taxonomy_primary, source_taxonomy_hierarchy
            FROM read_parquet(?)
            WHERE source_taxonomy_primary IS NOT DISTINCT FROM ?
            ORDER BY source_name LIMIT 50
        """, [str(classified_path), selected]).fetchdf()
    examples
    return examples, selected


@app.cell
def _(profile):
    # Basic-category rollups reveal whether a precise source label has a broad
    # family that warrants manual review before any many-to-one mapping choice.
    basic_rollups = profile("""
        SELECT source_category_basic, mapping_status, count(*) AS places
        FROM read_parquet(?) GROUP BY 1, 2 ORDER BY places DESC LIMIT 100
    """)
    basic_rollups
    return (basic_rollups,)


if __name__ == "__main__":
    app.run()
