import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # Read-only review surface: inspect validated artifacts without changing
    # mappings, geometries, or any downstream analysis method.
    import json
    from pathlib import Path

    import altair as alt
    import duckdb
    import marimo as mo
    import pandas as pd

    return Path, alt, duckdb, json, mo, pd


@app.cell
def _(Path, json):
    # A manifest is the source of truth for a completed run. This prevents the
    # notebook from presenting incomplete or filename-guessed artifacts.
    engine_dir = Path(__file__).resolve().parent
    run_inventory = []
    for validation_path in sorted((engine_dir / "outputs").glob("*/*/validated/osm_core_v1/validation_manifest.json")):
        run_dir = validation_path.parents[2]
        source_path = run_dir / "source_run_manifest.json"
        feature_path = validation_path.parent / "infrastructure_feature.parquet"
        rejected_path = validation_path.parent / "infrastructure_rejected_feature.parquet"
        qa_path = validation_path.parent / "qa_summary.json"
        if not all(path.exists() for path in (source_path, feature_path, rejected_path, qa_path)):
            continue
        source = json.loads(source_path.read_text(encoding="utf-8"))
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        run_inventory.append({
            "market": source["market_slug"], "market_id": source["market_id"],
            "source_run_id": source["source_run_id"],
            "boundary_role": source["boundary"]["geometry_role"],
            "analytical_crs": validation["analytical_crs"],
            "feature_path": feature_path, "rejected_path": rejected_path,
            "qa": json.loads(qa_path.read_text(encoding="utf-8")),
        })
    if not run_inventory:
        raise FileNotFoundError("Run acquisition, normalization, and validation before opening this notebook.")
    return (run_inventory,)


@app.cell
def _(mo):
    mo.md("""
    # Infrastructure Explorer

    A light, read-only review notebook for learning the shape of each market's
    validated infrastructure candidate before an analysis begins. It profiles
    classification, geometry QA, water complexity, source evidence, and a
    bounded map sample. It does **not** define access, barriers, routing,
    catchments, corridors, or mapping rules.

    The currently available CBSA boundary is `legacy_unclassified`, so these
    are serving candidates—not authoritative market-boundary analysis outputs.
    """)
    return


@app.cell
def _(run_inventory):
    market_options = {
        f"{run['market'].replace('_', ' ').title()} ({run['market_id']})": run["source_run_id"]
        for run in run_inventory
    }
    return (market_options,)


@app.cell
def _(market_options, mo):
    market_selector = mo.ui.dropdown(market_options, value=next(iter(market_options)), label="Market / validated run", searchable=True, full_width=True)
    market_selector
    return (market_selector,)


@app.cell
def _(market_selector, run_inventory):
    selected_run = next(run for run in run_inventory if run["source_run_id"] == market_selector.value)
    return (selected_run,)


@app.cell
def _(mo, pd, selected_run):
    validation_rows = selected_run["qa"]["geometry_validation"]
    retained = sum(row["features"] for row in validation_rows if row["record_status"] == "retained")
    rejected = sum(row["features"] for row in validation_rows if row["record_status"] == "rejected")
    run_status = pd.DataFrame([
        {"field": "source run", "value": selected_run["source_run_id"]},
        {"field": "boundary role", "value": selected_run["boundary_role"]},
        {"field": "analytical CRS", "value": selected_run["analytical_crs"]},
        {"field": "valid serving-candidate features", "value": f"{retained:,}"},
        {"field": "rejected audit features", "value": f"{rejected:,}"},
    ])
    mo.vstack([mo.md("## Run status and provenance"), mo.ui.table(run_status, selection=None)])
    return


@app.cell
def _(duckdb, selected_run):
    # WKB stays in Parquet; DuckDB Spatial derives inspection metrics only.
    def query(sql, parameters=None):
        with duckdb.connect() as con:
            con.execute("LOAD spatial")
            return con.execute(sql, parameters or []).fetchdf()

    return str(selected_run["feature_path"]), query, str(selected_run["rejected_path"])


@app.cell
def _(feature_path, query):
    composition = query("""
        SELECT feature_group, feature_type, feature_form, geometry_type,
          COUNT(*) AS features,
          ROUND(AVG(ST_NPoints(ST_GeomFromWKB(geometry))), 1) AS avg_vertices
        FROM read_parquet(?) GROUP BY 1,2,3,4
        ORDER BY feature_group, feature_type, feature_form, features DESC
    """, [feature_path])
    return (composition,)


@app.cell
def _(alt, composition, mo):
    chart = alt.Chart(composition).mark_bar().encode(
        x=alt.X("features:Q", title="Features"),
        y=alt.Y("feature_type:N", sort="-x", title="Source-supported type"),
        color=alt.Color("feature_group:N", title="Group"),
        tooltip=["feature_group:N", "feature_type:N", "feature_form:N", "geometry_type:N", "features:Q", "avg_vertices:Q"],
    ).properties(height=330, title="Validated feature composition")
    mo.vstack([mo.md("## What is in the candidate layer"), chart])
    return


@app.cell
def _(mo, pd, selected_run):
    water_profile = pd.DataFrame(selected_run["qa"]["water_profile"])
    validation = pd.DataFrame(selected_run["qa"]["geometry_validation"])
    mappings = pd.DataFrame(selected_run["qa"]["mapping_counts"])
    mo.vstack([
        mo.md("## Water scale and validation QA\nNo size filter, simplification, or dissolve is applied by this notebook."),
        mo.ui.table(water_profile, selection=None),
        mo.ui.table(validation, selection=None),
        mo.ui.table(mappings, selection=None),
    ])
    return


@app.cell
def _(composition):
    group_options = {"All feature groups": "__all__", **{group.title(): group for group in sorted(composition.feature_group.unique())}}
    return (group_options,)


@app.cell
def _(group_options, mo):
    group_selector = mo.ui.dropdown(group_options, value="All feature groups", label="Map and source-evidence filter")
    group_selector
    return (group_selector,)


@app.cell
def _(feature_path, group_selector, json, query):
    # Map sample is deterministic and bounded at 500 source-key-ordered rows
    # per group. It supports visual review but is not a coverage measure.
    map_rows = query("""
        WITH sampled AS (
          SELECT *, ROW_NUMBER() OVER (PARTITION BY feature_group ORDER BY source_record_key) AS sample_rank
          FROM read_parquet(?) WHERE ? = '__all__' OR feature_group = ?
        )
        SELECT feature_group, feature_type,
          ST_AsGeoJSON(ST_SimplifyPreserveTopology(ST_GeomFromWKB(geometry), 0.00015)) AS geojson
        FROM sampled WHERE sample_rank <= 500
    """, [feature_path, group_selector.value, group_selector.value])
    features = [
        {"type": "Feature", "geometry": json.loads(row.geojson), "properties": {"feature_group": row.feature_group, "feature_type": row.feature_type}}
        for row in map_rows.itertuples(index=False)
    ]
    return (features,)


@app.cell
def _(alt, features, group_selector, mo):
    data = alt.Data(values={"type": "FeatureCollection", "features": features}, format=alt.DataFormat(property="features"))
    shape_map = alt.Chart(data).mark_geoshape(stroke="#ffffff", strokeWidth=0.2).encode(
        color=alt.Color("properties.feature_group:N", title="Feature group", scale=alt.Scale(domain=["road", "rail", "water_network"], range=["#777777", "#8b3a3a", "#2787b8"])),
        tooltip=[alt.Tooltip("properties.feature_group:N", title="Group"), alt.Tooltip("properties.feature_type:N", title="Type")],
    ).properties(width=760, height=480, title=f"Bounded geometry review: {group_selector.value}")
    mo.vstack([mo.md("## Shape review map\nAt most 500 source-key-ordered features per group; never an analytical or publication map."), shape_map])
    return


@app.cell
def _(feature_path, group_selector, query):
    examples = query("""
        SELECT source_record_key, source_name, feature_group, feature_type,
          feature_form, geometry_type, source_tags, was_clipped, was_repaired
        FROM read_parquet(?) WHERE ? = '__all__' OR feature_group = ?
        ORDER BY feature_group, feature_type, source_record_key LIMIT 100
    """, [feature_path, group_selector.value, group_selector.value])
    return (examples,)


@app.cell
def _(examples, mo):
    mo.vstack([mo.md("## Source evidence sample"), mo.ui.dataframe(examples, page_size=20)])
    return


@app.cell
def _(rejected_path, query):
    rejected_examples = query("""
        SELECT rejection_reason, feature_group, feature_type, feature_form,
          source_name, source_record_key, source_tags
        FROM read_parquet(?) ORDER BY rejection_reason, feature_group, feature_type, source_record_key LIMIT 100
    """, [rejected_path])
    return (rejected_examples,)


@app.cell
def _(mo, rejected_examples):
    mo.vstack([mo.md("## Rejected audit evidence"), mo.ui.dataframe(rejected_examples, page_size=20)])
    return


if __name__ == "__main__":
    app.run()
