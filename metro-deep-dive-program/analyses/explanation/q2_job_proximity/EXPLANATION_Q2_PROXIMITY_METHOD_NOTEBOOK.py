import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # Epic 2 deliberately stays read-only. This notebook makes candidate center
    # constructions visible for review; it does not materialize or select one.
    import json
    import os
    from pathlib import Path

    import duckdb
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    from shapely import wkb

    return Path, duckdb, json, mo, os, pd, px, wkb


@app.cell
def _(Path, os, pd):
    analysis_dir = Path(__file__).resolve().parent
    repo_root = analysis_dir.parents[3]
    query_dir = analysis_dir / "queries"

    def resolve_db_path() -> str:
        """Use DB_PATH when supplied, otherwise use the repository-local DB."""

        return os.environ.get("DB_PATH", "").strip() or str(
            repo_root / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
        )

    def read_market_query(con, name: str, market_id: str) -> pd.DataFrame:
        """Bind a validated CBSA token into a named, analysis-owned reader."""

        query = (query_dir / name).read_text().replace("__CBSA_CODE__", market_id)
        return con.sql(query).df()

    return read_market_query, resolve_db_path


@app.cell
def _(mo, os):
    market_selector = mo.ui.text(
        value=os.environ.get("Q2_CBSA_CODE", "40060").strip(),
        label="CBSA code",
        full_width=False,
    )
    mo.vstack([
        mo.md(
            "# Explanation Q2 — Proximity Method Exploration\n"
            "This notebook maps workplace-job geography before choosing a center "
            "rule. It measures neither travel time nor a 15-minute city."
        ),
        market_selector,
    ])
    return (market_selector,)


@app.cell
def _(duckdb, market_selector, read_market_query, resolve_db_path, wkb):
    market_id = market_selector.value.strip()
    if not market_id.isdigit() or len(market_id) != 5:
        raise ValueError("CBSA code must be five digits.")

    # The reader returns governed WKB rather than requiring a local DuckDB
    # Spatial extension. Centroids and adjacency are derived below in Python.
    with duckdb.connect(resolve_db_path(), read_only=True) as con:
        tract_jobs = read_market_query(con, "q2_proximity_method_tracts.sql", market_id)
        market_context = read_market_query(
            con, "q2_job_concentration_market_context.sql", market_id
        )

    if tract_jobs.empty:
        raise ValueError(f"No tract WAC rows are available for CBSA {market_id}.")
    tract_jobs["geometry"] = tract_jobs.geom_wkb.map(lambda value: wkb.loads(bytes(value)))
    tract_jobs["centroid_lon"] = tract_jobs.geometry.map(lambda geometry: geometry.centroid.x)
    tract_jobs["centroid_lat"] = tract_jobs.geometry.map(lambda geometry: geometry.centroid.y)
    return market_context, tract_jobs


@app.cell
def _(market_context, mo):
    context = market_context.iloc[0]
    mo.md(
        "## National job-concentration context\n"
        f"**{context.cbsa_name} ({context.cbsa_code})** has "
        f"{int(context.tract_count):,} WAC tracts and "
        f"{int(context.workplace_jobs):,} workplace jobs in the 2023 snapshot. "
        f"Its highest-job tracts reach 50% of workplace jobs at "
        f"{context.tract_share_to_50pct_jobs:.1%} of tract rows and 80% at "
        f"{context.tract_share_to_80pct_jobs:.1%}. Compare this selected-market "
        "context with the national concentration notebook before selecting a local rule."
    )
    return


@app.cell
def _(json, mo, tract_jobs):
    # Keep the raw tract geometry as GeoJSON so the market view supports normal
    # map interaction without a DuckDB Spatial extension or a separate service.
    market_geography = tract_jobs.assign(
        jobs_to_workers_ratio=tract_jobs.jobs_total / tract_jobs.workers_total.where(tract_jobs.workers_total > 0),
        # This is a within-market rescaling of job totals. It makes the same
        # tract pattern comparable across markets without becoming a new score.
        market_job_share=tract_jobs.jobs_total / tract_jobs.jobs_total.sum(),
    )
    market_geojson = json.loads(json.dumps({
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": row.tract_geoid,
                "properties": {},
                "geometry": row.geometry.__geo_interface__,
            }
            for row in market_geography.itertuples(index=False)
        ],
    }))
    map_minimum_jobs = mo.ui.slider(
        start=0,
        stop=int(market_geography.jobs_total.max()),
        step=500,
        value=0,
        label="Display tracts with at least this many jobs",
        full_width=False,
    )
    mo.vstack([
        mo.md(
            "## Market job geography\n"
            "Every polygon is a tract. Compare total workplace jobs, market job "
            "share, workplace-job density, and jobs to resident workers without "
            "collapsing them into a single score. Density is contextual because tract "
            "land area affects it. The control below is display-only, not a center rule."
        ),
        map_minimum_jobs,
    ])
    return map_minimum_jobs, market_geography, market_geojson


@app.cell
def _(map_minimum_jobs, market_geography, market_geojson, mo, px):
    map_rows = market_geography.loc[
        market_geography.jobs_total >= map_minimum_jobs.value
    ].drop(columns=["geom_wkb", "geometry"]).copy()
    def build_market_map(fill_column: str, fill_label: str):
        """Create one comparable interactive tract map without mixing metrics."""

        # Plotly's current MapLibre surface replaces the retired Mapbox helper,
        # keeping this interactive map compatible with newer Marimo environments.
        figure = px.choropleth_map(
            map_rows,
            geojson=market_geojson,
            locations="tract_geoid",
            featureidkey="id",
            color=fill_column,
            color_continuous_scale="YlOrRd",
            hover_name="tract_name",
            hover_data={
                "tract_geoid": True,
                "jobs_total": ":,.0f",
                "market_job_share": ".2%",
                "jobs_per_sqmi": ":,.0f",
                "workers_total": ":,.0f",
                "jobs_to_workers_ratio": ".2f",
                "centroid_lon": False,
                "centroid_lat": False,
            },
            center={
                "lat": map_rows.centroid_lat.median(),
                "lon": map_rows.centroid_lon.median(),
            },
            zoom=8.1,
            opacity=0.78,
            map_style="carto-positron",
            labels={fill_column: fill_label},
        )
        figure.update_layout(
            margin={"l": 0, "r": 0, "t": 42, "b": 0},
            title=f"{fill_label} by tract",
        )
        return mo.ui.plotly(figure)

    return (build_market_map,)


@app.cell
def _(build_market_map):
    # One full-width map per cell keeps the geographic context readable on a
    # laptop screen and avoids horizontal scrolling in the Marimo output pane.
    build_market_map("jobs_total", "2023 workplace jobs")
    return


@app.cell
def _(build_market_map):
    build_market_map("market_job_share", "Share of CBSA workplace jobs")
    return


@app.cell
def _(build_market_map):
    build_market_map("jobs_per_sqmi", "Workplace jobs per square mile")
    return


@app.cell
def _(build_market_map):
    build_market_map("jobs_to_workers_ratio", "Jobs per resident worker")
    return


@app.cell
def _(mo, tract_jobs):
    # Candidate controls are deliberately visible and editable. Their defaults
    # make comparison convenient; none represents a recommended center rule.
    max_jobs = int(tract_jobs.jobs_total.max())
    absolute_floor = mo.ui.slider(
        start=0,
        stop=max_jobs,
        step=500,
        value=min(2500, max_jobs),
        label="Absolute tract-job floor",
        full_width=False,
    )
    market_share_floor = mo.ui.slider(
        start=0.1,
        stop=5.0,
        step=0.1,
        value=1.0,
        label="Minimum share of CBSA workplace jobs (%)",
        full_width=False,
    )
    ratio_floor = mo.ui.slider(
        start=1.0,
        stop=5.0,
        step=0.1,
        value=1.5,
        label="Jobs-to-workers context floor",
        full_width=False,
    )
    mo.vstack([
        mo.md(
            "## Candidate controls\n"
            "Market job share and jobs-to-workers are the primary candidate signals. "
            "The absolute-job floor is a guardrail against small-count ratio artifacts, "
            "not an attempt to correct tract size: tracts are generally designed around "
            "roughly 4,000 residents even though their physical area and worker counts vary. "
            "Jobs per square mile remains a map-only geographic diagnostic; its percentile "
            "and the redundant within-market jobs percentile are not center gates."
        ),
        mo.hstack([absolute_floor, market_share_floor], justify="start"),
        ratio_floor,
    ])
    return absolute_floor, market_share_floor, ratio_floor


@app.cell
def _(mo):
    mo.md("""
    ## Recommended V0 construction: core seeds plus one-hop expansion
    "
        f"**Core seed:** at least {market_share_floor.value:.1f}% of CBSA jobs, "
        f"{ratio_floor.value:.1f} jobs per resident worker, and "
        f"{absolute_floor.value:,}+ jobs.

    "
        "**One-hop extension:** a tract that shares a boundary with a core seed and "
        "passes the jobs-to-workers and absolute-job guardrails, even if it narrowly "
        "misses market share. This captures a connected employment district without "
        "letting the extension recur indefinitely.

    "
        "The notebook also shows strict core-only and broader no-share candidates as "
        "sensitivities. None is selected until a reviewer records a decision.
    """)
    return


@app.cell
def _(absolute_floor, market_share_floor, ratio_floor, tract_jobs):
    def shared_edge_neighbors(rows):
        """Return tract pairs that share an edge rather than only a corner."""

        # Shared-edge adjacency produces legible districts and avoids joining
        # diagonal tracts that merely meet at one vertex. Direct comparisons are
        # adequate for the selected-market tract counts in this V0 workbench.
        neighbors = {tract_id: set() for tract_id in rows.tract_geoid}
        for left in rows.itertuples(index=False):
            for right in rows.itertuples(index=False):
                if left.tract_geoid >= right.tract_geoid:
                    continue
                shared_boundary = left.geometry.boundary.intersection(right.geometry.boundary)
                if shared_boundary.length > 0:
                    neighbors[left.tract_geoid].add(right.tract_geoid)
                    neighbors[right.tract_geoid].add(left.tract_geoid)
        return neighbors

    def connected_components(qualified_ids: set[str], neighbors: dict[str, set[str]]) -> dict[str, int]:
        """Label shared-edge components without treating a component as a center."""

        eligible_neighbors = {
            tract_id: neighbors[tract_id] & qualified_ids for tract_id in qualified_ids
        }

        component_by_tract = {}
        component_id = 0
        for tract_id in sorted(qualified_ids):
            if tract_id in component_by_tract:
                continue
            component_id += 1
            pending = [tract_id]
            while pending:
                current = pending.pop()
                if current in component_by_tract:
                    continue
                component_by_tract[current] = component_id
                pending.extend(eligible_neighbors[current] - component_by_tract.keys())
        return component_by_tract

    candidates = tract_jobs.copy()
    # Preserve the same within-market normalization used in the base map so
    # candidate-map hover details can compare each tract with its CBSA context.
    candidates["market_job_share"] = candidates.jobs_total / candidates.jobs_total.sum()
    candidates["jobs_to_workers_ratio"] = candidates.jobs_total / candidates.workers_total.where(candidates.workers_total > 0)
    candidates["absolute_floor_candidate"] = candidates.jobs_total >= absolute_floor.value
    candidates["market_share_candidate"] = (
        candidates.market_job_share >= market_share_floor.value / 100
    )
    candidates["ratio_context_candidate"] = candidates.jobs_to_workers_ratio >= ratio_floor.value
    # Strict cores are the high-confidence seeds. The broader sensitivity makes
    # visible which workplace-heavy tracts are excluded only by market share.
    candidates["core_seed_candidate"] = (
        candidates.absolute_floor_candidate
        & candidates.market_share_candidate
        & candidates.ratio_context_candidate
    )
    candidates["no_share_sensitivity_candidate"] = (
        candidates.absolute_floor_candidate & candidates.ratio_context_candidate
    )

    neighbors = shared_edge_neighbors(candidates)
    core_seed_ids = set(candidates.loc[candidates.core_seed_candidate, "tract_geoid"])
    adjacent_to_core_ids = {
        neighbor for tract_id in core_seed_ids for neighbor in neighbors[tract_id]
    }
    candidates["one_hop_extension_candidate"] = (
        candidates.tract_geoid.isin(adjacent_to_core_ids)
        & candidates.no_share_sensitivity_candidate
        & ~candidates.core_seed_candidate
    )
    candidates["recommended_candidate"] = (
        candidates.core_seed_candidate | candidates.one_hop_extension_candidate
    )

    qualifying_ids = set(candidates.loc[candidates.recommended_candidate, "tract_geoid"])
    cluster_by_tract = connected_components(qualifying_ids, neighbors)
    candidates["recommended_cluster_id"] = candidates.tract_geoid.map(cluster_by_tract).astype("Int64")

    cluster_inventory = (
        candidates.loc[candidates.recommended_cluster_id.notna()]
        .groupby("recommended_cluster_id", as_index=False)
        .agg(
            tract_count=("tract_geoid", "size"),
            core_seed_count=("core_seed_candidate", "sum"),
            extension_count=("one_hop_extension_candidate", "sum"),
            jobs_total=("jobs_total", "sum"),
        )
        .sort_values(["jobs_total", "tract_count"], ascending=False)
    )
    # A one-tract component remains visible on the cluster map but is not called
    # a contiguous candidate. This avoids relabeling every recommended tract.
    cluster_sizes = cluster_inventory.set_index("recommended_cluster_id")["tract_count"]
    candidates["contiguous_recommended_cluster_candidate"] = (
        candidates.recommended_cluster_id.map(cluster_sizes).fillna(0) >= 2
    )
    return candidates, cluster_inventory


@app.cell
def _(candidates, cluster_inventory, market_share_floor, mo, pd, ratio_floor):
    candidate_columns = [
        "absolute_floor_candidate",
        "market_share_candidate",
        "ratio_context_candidate",
        "core_seed_candidate",
        "one_hop_extension_candidate",
        "recommended_candidate",
        "no_share_sensitivity_candidate",
        "contiguous_recommended_cluster_candidate",
    ]
    candidate_labels = {
        "absolute_floor_candidate": "Absolute tract-job floor",
        "market_share_candidate": "Share of CBSA workplace jobs",
        "ratio_context_candidate": "Jobs-to-workers",
        "core_seed_candidate": "Strict core seed",
        "one_hop_extension_candidate": "One-hop qualified extension",
        "recommended_candidate": "Recommended center set",
        "no_share_sensitivity_candidate": "Broader no-share sensitivity",
        "contiguous_recommended_cluster_candidate": "Contiguous recommended clusters (2+)",
    }
    parameters = {
        "absolute_floor_candidate": "See visible absolute-floor control",
        "market_share_candidate": f">= {market_share_floor.value:.1f}% of CBSA jobs",
        "ratio_context_candidate": f">= {ratio_floor.value:.1f} jobs per resident worker",
        "core_seed_candidate": "All three primary gates",
        "one_hop_extension_candidate": "Shared-edge neighbor; passes job floor and ratio",
        "recommended_candidate": "Core seeds plus one-hop qualified extensions",
        "no_share_sensitivity_candidate": "Passes job floor and ratio; ignores market share",
        "contiguous_recommended_cluster_candidate": "Component of 2+ shared-edge recommended tracts",
    }
    candidate_inventory = pd.DataFrame([
        {
            "candidate": candidate_labels[column],
            "parameters": parameters[column],
            "tracts_selected": int(candidates[column].sum()),
            "workplace_jobs_selected": int(candidates.loc[candidates[column], "jobs_total"].sum()),
        }
        for column in candidate_columns
    ])
    method_options = pd.DataFrame([
        {
            "method_option": "Strict core only",
            "construction": "All three primary gates",
            "recommended_use": "High-confidence seed sensitivity",
        },
        {
            "method_option": "Core plus one-hop extension",
            "construction": "Core seeds plus shared-edge neighbors that pass the job floor and ratio",
            "recommended_use": "Recommended V0 review construction",
        },
        {
            "method_option": "No-share sensitivity",
            "construction": "Job floor plus jobs-to-workers; market share ignored",
            "recommended_use": "Check for plausible smaller or outlying centers",
        },
    ])

    overlap_rows = []
    for left in candidate_columns:
        for right in candidate_columns:
            union_count = int((candidates[left] | candidates[right]).sum())
            overlap_rows.append({
                "candidate": candidate_labels[left],
                "comparison": candidate_labels[right],
                "shared_tracts": int((candidates[left] & candidates[right]).sum()),
                "jaccard_share": (candidates[left] & candidates[right]).sum() / union_count if union_count else None,
            })
    overlap = pd.DataFrame(overlap_rows)

    # This sequential table makes the impact of each primary gate inspectable
    # while sliders change. It reports both selected tract counts and the job
    # mass retained, so a narrow screen is not mistaken for a weak center set.
    gate_steps = [
        ("All market tracts", candidates.index == candidates.index),
        ("Pass absolute-job guardrail", candidates.absolute_floor_candidate),
        (
            "Also pass market-job-share gate",
            candidates.absolute_floor_candidate & candidates.market_share_candidate,
        ),
        (
            "Also pass jobs-to-workers gate",
            candidates.core_seed_candidate,
        ),
    ]
    gate_summary = pd.DataFrame([
        {
            "sequential_gate": label,
            "tracts_remaining": int(mask.sum()),
            "workplace_jobs_remaining": int(candidates.loc[mask, "jobs_total"].sum()),
            "share_of_market_jobs": candidates.loc[mask, "market_job_share"].sum(),
        }
        for label, mask in gate_steps
    ])

    mo.vstack([
        mo.md("## Candidate inventories, gates, and overlap\nThe first table is a live, sequential gate count: adjust the three primary controls and inspect both tracts retained and their market job mass. The recommended set combines strict core seeds with one-hop, shared-edge extensions that pass the job-floor and jobs-to-workers guardrails. It remains a review candidate, not an automatic center decision."),
        mo.ui.table(gate_summary, page_size=10),
        mo.ui.table(method_options, page_size=5),
        mo.ui.table(candidate_inventory, page_size=10),
        mo.ui.table(cluster_inventory, page_size=20),
        mo.ui.table(overlap, page_size=30),
    ])
    return


@app.cell
def _(mo):
    candidate_map_selector = mo.ui.dropdown(
        {
            "Absolute tract-job floor": "absolute_floor_candidate",
            "Share of CBSA workplace jobs": "market_share_candidate",
            "Jobs-to-workers": "ratio_context_candidate",
            "Strict core seeds": "core_seed_candidate",
            "One-hop qualified extensions": "one_hop_extension_candidate",
            "Recommended center set": "recommended_candidate",
            "Broader no-share sensitivity": "no_share_sensitivity_candidate",
            "Contiguous recommended clusters (2+)": "contiguous_recommended_cluster_candidate",
        },
        value="Recommended center set",
        label="Candidate map view",
        full_width=False,
    )
    mo.vstack([
        mo.md(
            "## Candidate maps\n"
            "Choose one construction at a time and inspect it over the actual tract "
            "polygons. The cluster view shows only components of two or more touching "
            "recommended tracts sharing an edge; it is not a corridor or selected center rule."
        ),
        candidate_map_selector,
    ])
    return (candidate_map_selector,)


@app.cell
def _(candidate_map_selector, candidates, market_geojson, mo, px):
    candidate_map_rows = candidates.drop(columns=["geom_wkb", "geometry"]).copy()
    candidate_view = candidate_map_selector.value

    if candidate_view == "contiguous_recommended_cluster_candidate":
        candidate_map_rows["candidate_map_status"] = "Other tract"
        candidate_map_rows.loc[
            candidate_map_rows.contiguous_recommended_cluster_candidate,
            "candidate_map_status",
        ] = "Shared-edge candidate cluster"
        candidate_map_title = "Contiguous recommended candidate clusters"
        candidate_colors = {
            "Other tract": "#d9d9d9",
            "Shared-edge candidate cluster": "#b2182b",
        }
    else:
        candidate_map_rows["candidate_map_status"] = "Other tract"
        candidate_map_rows.loc[
            candidate_map_rows[candidate_view], "candidate_map_status"
        ] = "Candidate tract"
        candidate_map_title = candidate_map_selector.value
        candidate_colors = {"Other tract": "#d9d9d9", "Candidate tract": "#2166ac"}

    candidate_map_figure = px.choropleth_map(
        candidate_map_rows,
        geojson=market_geojson,
        locations="tract_geoid",
        featureidkey="id",
        color="candidate_map_status",
        color_discrete_map=candidate_colors,
        category_orders={"candidate_map_status": ["Other tract", "Candidate tract", "Shared-edge candidate cluster"]},
        hover_name="tract_name",
        hover_data={
            "tract_geoid": True,
            "jobs_total": ":,.0f",
            "market_job_share": ".2%",
            "jobs_per_sqmi": ":,.0f",
            "workers_total": ":,.0f",
            "jobs_to_workers_ratio": ".2f",
            "core_seed_candidate": True,
            "one_hop_extension_candidate": True,
            "recommended_cluster_id": True,
            "centroid_lon": False,
            "centroid_lat": False,
        },
        center={
            "lat": candidate_map_rows.centroid_lat.median(),
            "lon": candidate_map_rows.centroid_lon.median(),
        },
        zoom=8.1,
        opacity=0.78,
        map_style="carto-positron",
        labels={"candidate_map_status": "Candidate status"},
    )
    candidate_map_figure.update_layout(
        margin={"l": 0, "r": 0, "t": 42, "b": 0},
        title=f"{candidate_map_title} by tract",
        legend_title_text="",
    )
    mo.ui.plotly(candidate_map_figure)
    return


@app.cell
def _(mo):
    # This is intentionally a blank review record, not a control that silently
    # changes the analysis. The analytical outcomes notebook may proceed only
    # after the reviewer records a decision in the method configuration.
    mo.md("""
    ## Reviewer decision record — required before the outcomes notebook

    - **Recommended construction accepted, rejected, or revised:** _not yet reviewed_
    - **Core seed parameters and retained sensitivity cases:** _not yet reviewed_
    - **One-hop expansion treatment and shared-edge rule:** _not yet reviewed_
    - **Tract origin and multiple-center treatment:** _not yet reviewed_
    - **What the selected construction visibly misses or fragments:** _not yet reviewed_
    - **Reviewer / date:** _not yet reviewed_

    This notebook is complete when this evidence is reviewed, not when a default
    control happens to have a value.
    """)
    return


if __name__ == "__main__":
    app.run()
