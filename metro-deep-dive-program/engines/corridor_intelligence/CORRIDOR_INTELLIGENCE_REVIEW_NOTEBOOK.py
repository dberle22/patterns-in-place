import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This is a read-only method-review surface. It reads versioned artifacts
    # and imports the engine's ID helper for QA; it never groups or edits tracts.
    import json
    import os
    import sys
    from pathlib import Path

    import altair as alt
    import duckdb
    import geopandas as gpd
    import marimo as mo
    import pandas as pd

    return Path, alt, duckdb, gpd, json, mo, os, pd, sys


@app.cell
def _(Path, sys):
    corridor_notebook_dir = Path(__file__).resolve().parent
    corridor_repo_root = corridor_notebook_dir.parents[2]
    if str(corridor_notebook_dir) not in sys.path:
        sys.path.insert(0, str(corridor_notebook_dir))
    from corridor_baseline import candidate_id

    return candidate_id, corridor_notebook_dir, corridor_repo_root


@app.cell
def _(corridor_notebook_dir, json):
    # A run manifest is the discovery surface. A notebook never assumes a
    # current run from a filename or constructs a replacement artifact path.
    corridor_run_inventory = []
    for manifest_path in sorted((corridor_notebook_dir / "outputs" / "runs").glob("*/run_manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        run_dir = manifest_path.parent
        required = [run_dir / f"{name}.parquet" for name in ("structural_membership", "structural_candidate", "structural_edge_evidence")]
        if all(path.exists() for path in required):
            corridor_run_inventory.append({**manifest, "run_dir": run_dir})
    if not corridor_run_inventory:
        raise FileNotFoundError("Run Corridor Intelligence before opening the review notebook.")
    return (corridor_run_inventory,)


@app.cell
def _(mo):
    mo.md("""
    # Corridor Intelligence — method review

    This notebook reviews stored Corridor Intelligence runs. It does not
    regroup tracts, override membership, rename candidates, or write DuckDB.
    Use it to trace a candidate from Phase 7 inputs through the same-zone
    baseline, physical and aggregate-POI refinement, bridge decisions, and
    diagnostic form classification.
    """)
    return


@app.cell
def _(corridor_run_inventory):
    market_options = {}
    for run in corridor_run_inventory:
        label = f"{run['market']} ({run['cbsa_code']})"
        market_options[label] = run["cbsa_code"]
    return (market_options,)


@app.cell
def _(market_options, mo):
    default_market = next((label for label, code in market_options.items() if code == "27260"), next(iter(market_options)))
    market_selector = mo.ui.dropdown(market_options, value=default_market, label="Market", searchable=True, full_width=True)
    market_selector
    return (market_selector,)


@app.cell
def _(corridor_run_inventory, market_selector):
    selected_market_runs = [run for run in corridor_run_inventory if run["cbsa_code"] == market_selector.value]
    run_options = {f"{run['parameter_profile']} · {run['run_id']}": run["run_id"] for run in selected_market_runs}
    return run_options, selected_market_runs


@app.cell
def _(mo, run_options):
    default_run = next(
        (
            label
            for label in run_options
            if label.startswith("physical_evidence_v1__baseline_graph_v1 ·")
        ),
        next((label for label in run_options if label.startswith("physical_evidence_v1")), next(iter(run_options))),
    )
    run_selector = mo.ui.dropdown(run_options, value=default_run, label="Method / parameter profile", searchable=True, full_width=True)
    run_selector
    return (run_selector,)


@app.cell
def _(run_selector, selected_market_runs):
    selected_run = next(run for run in selected_market_runs if run["run_id"] == run_selector.value)
    return (selected_run,)


@app.cell
def _(mo, pd, selected_run):
    # Provenance appears before results so a reviewer sees exactly which input
    # releases and method profile were responsible for a displayed candidate.
    provenance_rows = [
        {"field": "run_id", "value": selected_run["run_id"]},
        {"field": "method_version", "value": selected_run["method_version"]},
        {"field": "parameter_profile", "value": selected_run["parameter_profile"]},
        {"field": "Phase 7 build", "value": selected_run["phase7_build_id"]},
        {"field": "tract geometry", "value": f"{selected_run['geometry_role']} ({selected_run['geometry_vintage_status']})"},
        {"field": "Infrastructure source run", "value": selected_run.get("infrastructure_source_run_id") or "not used"},
        {"field": "POI source run", "value": selected_run.get("poi_source_run_id") or "not used"},
        {"field": "publication status", "value": selected_run["publication_status"]},
    ]
    mo.vstack([mo.md("## Input coverage and provenance"), mo.ui.table(pd.DataFrame(provenance_rows), selection=None)])
    return


@app.cell
def _(duckdb, selected_run):
    with duckdb.connect() as _artifact_con:
        membership_all = _artifact_con.execute("SELECT * FROM read_parquet(?)", [str(selected_run["run_dir"] / "structural_membership.parquet")]).fetchdf()
        candidate_all = _artifact_con.execute("SELECT * FROM read_parquet(?)", [str(selected_run["run_dir"] / "structural_candidate.parquet")]).fetchdf()
        edge_all = _artifact_con.execute("SELECT * FROM read_parquet(?)", [str(selected_run["run_dir"] / "structural_edge_evidence.parquet")]).fetchdf()
    return candidate_all, edge_all, membership_all


@app.cell
def _(candidate_all, membership_all):
    method_variant_options = {value.replace("_", " ").title(): value for value in sorted(membership_all.method_variant.unique())}
    zone_options = {"All zone types": "__all__", **{value: value for value in sorted(membership_all.original_zone_type.unique())}}
    form_options = {"All forms": "__all__", **{value.title(): value for value in sorted(candidate_all.candidate_form.dropna().unique())}}
    return form_options, method_variant_options, zone_options


@app.cell
def _(form_options, method_variant_options, mo, zone_options):
    method_selector = mo.ui.dropdown(method_variant_options, value=next((label for label, value in method_variant_options.items() if value == "physical_evidence"), next(iter(method_variant_options))), label="Method stage")
    zone_selector = mo.ui.dropdown(zone_options, value="All zone types", label="Primary / original zone type", searchable=True)
    form_selector = mo.ui.dropdown(form_options, value="All forms", label="Candidate form")
    mo.hstack([method_selector, zone_selector, form_selector], justify="start")
    return form_selector, method_selector, zone_selector


@app.cell
def _(candidate_all, form_selector, method_selector, zone_selector):
    visible_candidates = candidate_all.loc[candidate_all.method_variant.eq(method_selector.value)].copy()
    if zone_selector.value != "__all__":
        visible_candidates = visible_candidates.loc[visible_candidates.primary_zone_type.eq(zone_selector.value)]
    if form_selector.value != "__all__":
        visible_candidates = visible_candidates.loc[visible_candidates.candidate_form.eq(form_selector.value)]
    visible_candidates = visible_candidates.sort_values(["candidate_form", "total_tract_count", "candidate_id"], ascending=[True, False, True])
    candidate_options = {f"{row.candidate_form} · {row.primary_zone_type} · {row.total_tract_count} tracts · {row.candidate_id}": row.candidate_id for row in visible_candidates.itertuples(index=False)}
    return candidate_options, visible_candidates


@app.cell
def _(candidate_options, mo):
    candidate_selector = mo.ui.dropdown(candidate_options, value=next(iter(candidate_options), None), label="Candidate", searchable=True, full_width=True)
    candidate_selector
    return (candidate_selector,)


@app.cell
def _(mo, visible_candidates):
    columns = [column for column in ["candidate_id", "primary_zone_type", "candidate_form", "core_tract_count", "bridge_tract_count", "total_tract_count", "aspect_ratio", "spine_edge_count", "coherence_status"] if column in visible_candidates]
    mo.vstack([mo.md("## Candidate inventory"), mo.ui.dataframe(visible_candidates[columns], page_size=25)])
    return


@app.cell
def _(candidate_selector, membership_all, method_selector):
    selected_candidate_membership = membership_all.loc[(membership_all.method_variant.eq(method_selector.value)) & (membership_all.candidate_id.eq(candidate_selector.value))].copy()
    return (selected_candidate_membership,)


@app.cell
def _(corridor_repo_root, duckdb, gpd, market_selector, membership_all, method_selector, os):
    # Maps use governed geometry only for display. Membership comes wholly from
    # the selected run artifact; this cell performs no spatial grouping.
    db_path = None
    env_path = os.environ.get("DB_PATH", "").strip()
    if env_path:
        db_path = env_path
    else:
        for raw_line in (corridor_repo_root / ".Renviron").read_text(encoding="utf-8").splitlines():
            if raw_line.startswith("DB_PATH="):
                db_path = raw_line.split("=", 1)[1].strip()
                break
    with duckdb.connect(db_path, read_only=True) as _geometry_con:
        map_rows = _geometry_con.execute("""
            SELECT z.tract_geoid, ST_AsWKB(g.geom) AS geometry_wkb
            FROM mart_intelligence.intelligence_zones z
            JOIN geo.tracts_all_us g USING (tract_geoid)
            WHERE z.cbsa_code = ?
        """, [market_selector.value]).fetchdf()
    # DuckDB exposes BLOB values as bytearrays through pandas, while GeoPandas
    # expects immutable WKB bytes when constructing the display geometry.
    map_rows["geometry"] = gpd.GeoSeries.from_wkb(map_rows.pop("geometry_wkb").map(bytes), crs="EPSG:4326")
    tract_map = gpd.GeoDataFrame(map_rows, geometry="geometry", crs="EPSG:4326").merge(membership_all.loc[membership_all.method_variant.eq(method_selector.value)], on="tract_geoid", how="left", validate="one_to_one")
    return (tract_map,)


@app.cell
def _(alt, candidate_selector, mo, tract_map):
    tract_map["selected_candidate"] = tract_map.candidate_id.eq(candidate_selector.value)
    # The initial review view shows the selected candidate's actual tract
    # footprint. Membership roles remain available in the trace below, where
    # they explain a questionable boundary rather than define the review task.
    review_map = alt.Chart(tract_map, title="Selected candidate footprint").mark_geoshape(stroke="#ffffff", strokeWidth=0.35).encode(
        color=alt.condition("datum.selected_candidate", alt.value("#2a6f97"), alt.value("#e6e6e6")),
        opacity=alt.condition("datum.selected_candidate", alt.value(1), alt.value(0.35)),
        tooltip=["tract_geoid:N", "original_zone_type:N", "candidate_id:N"],
    ).properties(width=760, height=500)
    mo.vstack([mo.md("## Candidate map\nSelect a candidate to see its tract footprint and overall spatial form. Switch **Method stage** to compare the form created by strict adjacency, bounded-nearby, DBSCAN, or physical/POI refinement."), review_map])
    return (review_map,)


@app.cell
def _(candidate_selector, edge_all, method_selector, selected_candidate_membership):
    selected_candidate_edges = edge_all.loc[(edge_all.method_variant.eq(method_selector.value)) & ((edge_all.tract_geoid_low.isin(selected_candidate_membership.tract_geoid)) | (edge_all.tract_geoid_high.isin(selected_candidate_membership.tract_geoid)))].copy()
    return (selected_candidate_edges,)


@app.cell
def _(mo, selected_candidate_edges, selected_candidate_membership):
    membership_columns = ["tract_geoid", "original_zone_type", "membership_status", "membership_stage", "evidence_summary"]
    edge_columns = [column for column in ["tract_geoid_low", "tract_geoid_high", "geographic_relation", "phase7_similarity", "spine_feature_count", "separator_overlap_m", "poi_composition_similarity", "poi_combined_places", "decision_stage", "final_decision"] if column in selected_candidate_edges]
    mo.vstack([mo.md("## Candidate diagnostic trace\nUse this only when the candidate footprint raises a question. Core and bridge are membership explanations; unassigned tracts are nearby tracts that did not qualify for any candidate."), mo.ui.table(selected_candidate_membership[membership_columns], selection=None), mo.ui.dataframe(selected_candidate_edges[edge_columns], page_size=25)])
    return


@app.cell
def _(alt, candidate_all, mo, pd):
    comparison = candidate_all.groupby(["method_variant", "candidate_form"], dropna=False).size().reset_index(name="candidates")
    comparison_chart = alt.Chart(comparison, title="Method comparison by candidate form").mark_bar().encode(
        x=alt.X("method_variant:N", title="Stored method stage"), y=alt.Y("candidates:Q", title="Candidates"), color=alt.Color("candidate_form:N", title="Candidate form"), tooltip=["method_variant:N", "candidate_form:N", "candidates:Q"]
    )
    mo.vstack([mo.md("## Method and sensitivity comparison\nCompare how many candidate zones and forms each stage produces. The strict/bounded graph variants are the no-POI baseline; DBSCAN remains a challenger; physical evidence is the final refinement."), comparison_chart, mo.ui.table(comparison, selection=None)])
    return comparison, comparison_chart


@app.cell
def _(corridor_run_inventory, duckdb, pd, selected_run):
    # Compare only like-for-like parameter profiles across markets. This reads
    # artifacts already produced by the shared runner; it performs no rerun or
    # cross-market parameter adjustment in the notebook.
    cross_market_rows = []
    comparable_runs = [run for run in corridor_run_inventory if run["parameter_profile"] == selected_run["parameter_profile"]]
    with duckdb.connect() as _comparison_con:
        for _run in comparable_runs:
            _membership = _comparison_con.execute("SELECT * FROM read_parquet(?) WHERE method_variant = 'physical_evidence'", [str(_run["run_dir"] / "structural_membership.parquet")]).fetchdf()
            _candidates = _comparison_con.execute("SELECT * FROM read_parquet(?) WHERE method_variant = 'physical_evidence'", [str(_run["run_dir"] / "structural_candidate.parquet")]).fetchdf()
            cross_market_rows.append({"market": _run["market"], "cbsa_code": _run["cbsa_code"], "parameter_profile": _run["parameter_profile"], "tracts": len(_membership), "core_tracts": int(_membership.membership_status.eq("core").sum()), "bridge_tracts": int(_membership.membership_status.eq("bridge").sum()), "unassigned_tracts": int(_membership.membership_status.eq("unassigned").sum()), "candidates": len(_candidates), "corridors": int(_candidates.candidate_form.eq("corridor").sum()), "districts": int(_candidates.candidate_form.eq("district").sum()), "unclassified": int(_candidates.candidate_form.eq("unclassified").sum())})
    cross_market_comparison = pd.DataFrame(cross_market_rows)
    return (cross_market_comparison,)


@app.cell
def _(alt, cross_market_comparison, mo):
    cross_market_chart = alt.Chart(cross_market_comparison, title="Like-for-like market comparison").transform_fold(
        ["candidates", "corridors", "districts", "unclassified"], as_=["candidate_measure", "count"]
    ).mark_bar().encode(
        x=alt.X("market:N", title="Market"), y=alt.Y("count:Q", title="Candidate count"), color=alt.Color("candidate_measure:N", title="Candidate measure"), tooltip=["market:N", "candidate_measure:N", "count:Q", "parameter_profile:N"]
    )
    mo.vstack([mo.md("## Jacksonville–Richmond comparison\nThis compares the candidate zones and their forms when both markets use the selected identical parameter profile. Membership counts remain in the table as diagnostics, not the headline result."), cross_market_chart, mo.ui.table(cross_market_comparison, selection=None)])
    return (cross_market_chart,)


@app.cell
def _(candidate_all, candidate_id, membership_all, mo, pd, selected_run, tract_map):
    physical_membership = membership_all.loc[membership_all.method_variant.eq("physical_evidence")].copy()
    physical_candidates = candidate_all.loc[candidate_all.method_variant.eq("physical_evidence")].copy()
    expected_ids = []
    for candidate in physical_candidates.itertuples(index=False):
        members = physical_membership.loc[physical_membership.candidate_id.eq(candidate.candidate_id), "tract_geoid"].tolist()
        expected_ids.append(candidate_id(str(candidate.cbsa_code), candidate.primary_zone_type, members) == candidate.candidate_id)
    qa = pd.DataFrame([
        {"check": "One membership row per tract and selected method", "result": not physical_membership.duplicated("tract_geoid").any(), "detail": len(physical_membership)},
        {"check": "Tract geometry coverage", "result": tract_map.geometry.notna().all(), "detail": int(tract_map.geometry.notna().sum())},
        {"check": "Candidate IDs reproduce from stored membership", "result": all(expected_ids), "detail": len(expected_ids)},
        {"check": "Bridge records retain a different original zone", "result": (physical_membership.loc[physical_membership.membership_status.eq("bridge"), "original_zone_type"] != physical_membership.loc[physical_membership.membership_status.eq("bridge"), "candidate_id"].map(physical_candidates.set_index("candidate_id").primary_zone_type)).all(), "detail": int(physical_membership.membership_status.eq("bridge").sum())},
        {"check": "Run remains a review artifact", "result": selected_run["publication_status"].endswith("not_duckdb_published"), "detail": selected_run["publication_status"]},
    ])
    fragmentation = physical_candidates.groupby("primary_zone_type").agg(candidates=("candidate_id", "count"), tracts=("total_tract_count", "sum"), bridges=("bridge_tract_count", "sum")).reset_index()
    mo.vstack([mo.md("## QA and fragmentation"), mo.ui.table(qa, selection=None), mo.ui.table(fragmentation, selection=None)])
    return fragmentation, qa


@app.cell
def _(candidate_selector, mo, selected_candidate_edges, selected_candidate_membership, selected_run):
    # The export is generated in memory and carries run lineage. It does not
    # mutate canonical artifacts or create an editable membership workflow.
    export_rows = selected_candidate_membership.assign(run_id=selected_run["run_id"], parameter_profile=selected_run["parameter_profile"])
    export_csv = export_rows.to_csv(index=False).encode("utf-8")
    mo.vstack([mo.md("## Optional review export"), mo.download(export_csv, filename=f"{selected_run['run_id']}_{candidate_selector.value}_membership.csv", mimetype="text/csv", label="Download selected-candidate membership with lineage"), mo.download(selected_candidate_edges.to_csv(index=False).encode("utf-8"), filename=f"{selected_run['run_id']}_{candidate_selector.value}_edge_evidence.csv", mimetype="text/csv", label="Download selected-candidate edge evidence")])
    return


if __name__ == "__main__":
    app.run()
