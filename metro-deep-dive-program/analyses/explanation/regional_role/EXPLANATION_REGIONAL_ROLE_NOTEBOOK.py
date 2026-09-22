import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # The run workbench consumes the setup engine's persisted membership and
    # Benchmarking's metric surface. It does not create a Regional Role mart.
    import os
    from pathlib import Path

    import duckdb
    import geopandas as gpd
    import matplotlib.pyplot as plt
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    from shapely import wkb
    from shapely.geometry import mapping

    return Path, duckdb, gpd, mapping, mo, os, pd, plt, px, wkb


@app.cell
def _(Path, os):
    analysis_dir = Path(__file__).resolve().parent
    query_dir = analysis_dir / "queries"
    repo_root = analysis_dir.parents[3]

    def resolve_db_path():
        return os.environ.get("DB_PATH", "").strip() or str(
            repo_root / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
        )

    def read_query(con, name, replacements=None):
        sql = (query_dir / name).read_text()
        for token, value in (replacements or {}).items():
            sql = sql.replace(token, str(value))
        return con.execute(sql).fetchdf()

    return read_query, resolve_db_path


@app.cell
def _(duckdb, read_query, resolve_db_path):
    with duckdb.connect(resolve_db_path(), read_only=True) as _con:
        cbsa_options = read_query(_con, "regional_role_cbsa_options.sql")
        metric_options = _con.execute(
            """
            SELECT metric_id, metric_label, metric_family, unit
            FROM mart_benchmarking.benchmark_metric_catalog
            WHERE metric_id IN ('pop_total', 'pop_growth_5yr', 'lq_professional',
                                'lq_manufacturing', 'lq_information',
                                'qcew_private_avg_wkly_wage', 'irs_net_migration_rate')
            ORDER BY metric_family, metric_label
            """
        ).fetchdf()
    return cbsa_options, metric_options


@app.cell
def _(cbsa_options, mo, os):
    choices = dict(zip(cbsa_options.display_name, cbsa_options.cbsa_code))
    default_code = os.environ.get("REGIONAL_ROLE_CBSA_CODE", "40060").strip()
    _default_market_label = next((label for label, code in choices.items() if code == default_code), next(iter(choices)))
    market_selector = mo.ui.dropdown(choices, value=_default_market_label, label="Target metropolitan CBSA", searchable=True)
    mo.vstack([
        mo.md("# Regional Role — Run Workbench"),
        mo.md("National metro context is shown first; all active-lens details use the Geography-owned membership selected below."),
        market_selector,
    ])
    return (market_selector,)


@app.cell
def _(duckdb, market_selector, read_query, resolve_db_path):
    target_cbsa_code = market_selector.value
    with duckdb.connect(resolve_db_path(), read_only=True) as _con:
        membership = read_query(_con, "regional_role_setup_membership.sql", {"__CBSA_CODE__": target_cbsa_code})
    if membership.empty:
        raise ValueError(f"No governed Regional Role membership is available for CBSA {target_cbsa_code}.")
    target_cbsa_name = membership.target_cbsa_name.iloc[0]
    return membership, target_cbsa_code, target_cbsa_name


@app.cell
def _(membership, metric_options, mo):
    lens_choices = {}
    for row in membership[["lens_id", "parameter_value"]].drop_duplicates().itertuples(index=False):
        label = row.lens_id if row.parameter_value == "none" else f"{row.lens_id} ({row.parameter_value} miles)"
        lens_choices[label] = f"{row.lens_id}|{row.parameter_value}"
    default_lens = next(label for label, value in lens_choices.items() if value == "cbsa_centroid_250mi|250")
    metric_choices = {
        f"{row.metric_label} [{row.unit}]": row.metric_id
        for row in metric_options.itertuples(index=False)
    }
    active_lens_selector = mo.ui.dropdown(lens_choices, value=default_lens, label="Active lens")
    metric_selector = mo.ui.dropdown(metric_choices, value=next(label for label, value in metric_choices.items() if value == "pop_total"), label="Comparison KPI")
    mo.vstack([
        mo.md("## Comparison controls"),
        active_lens_selector,
        metric_selector,
    ])
    return active_lens_selector, metric_selector


@app.cell
def _(active_lens_selector):
    active_lens_id, active_parameter_value = active_lens_selector.value.split("|", 1)
    return active_lens_id, active_parameter_value


@app.cell
def _(duckdb, metric_selector, read_query, resolve_db_path, target_cbsa_code):
    _replacements = {"__CBSA_CODE__": target_cbsa_code, "__METRIC_ID__": metric_selector.value}
    with duckdb.connect(resolve_db_path(), read_only=True) as _con:
        national_baseline = read_query(_con, "regional_role_national_baseline.sql", _replacements)
        lens_panel = read_query(_con, "regional_role_lens_panel.sql", _replacements)
    return lens_panel, national_baseline


@app.cell
def _(lens_panel, mo, national_baseline, px, target_cbsa_name):
    baseline = national_baseline.iloc[0]
    panel_figure = px.bar(
        lens_panel,
        x="lens_id",
        y="member_median",
        error_y=(lens_panel.member_p75 - lens_panel.member_median),
        title=f"{target_cbsa_name}: target versus each lens median",
        labels={"lens_id": "Lens", "member_median": baseline.metric_label},
    )
    panel_figure.add_hline(y=baseline.target_value, line_color="#d94801", annotation_text="Target value")
    mo.vstack([
        mo.md("## National metropolitan baseline"),
        mo.md(
            f"**{baseline.metric_label}** ({baseline.year}; {baseline.unit}): target **{baseline.target_value:,.3g}**; "
            f"national metro median **{baseline.comparison_median:,.3g}**; percentile **{baseline.target_percentile:.1%}** "
            f"across {int(baseline.comparison_n):,} comparable metros."
        ),
        mo.md("## Persistent four-lens comparison panel"),
        mo.md("The target line is repeated across lenses; metric coverage remains visible in the table."),
        panel_figure,
        mo.ui.table(lens_panel, page_size=10),
    ])
    return


@app.cell
def _(active_lens_id, active_parameter_value, duckdb, metric_selector, read_query, resolve_db_path, target_cbsa_code):
    _replacements = {
        "__CBSA_CODE__": target_cbsa_code,
        "__METRIC_ID__": metric_selector.value,
        "__LENS_ID__": active_lens_id,
        "__PARAMETER_VALUE__": active_parameter_value,
    }
    with duckdb.connect(resolve_db_path(), read_only=True) as _con:
        active_comparison = read_query(_con, "regional_role_active_comparison.sql", _replacements)
        map_rows = read_query(_con, "regional_role_setup_map.sql", _replacements)
    return active_comparison, map_rows


@app.cell
def _(active_comparison, active_lens_id, active_parameter_value, map_rows, mapping, mo, px, target_cbsa_name, wkb):
    mapped = map_rows.merge(
        active_comparison[["member_cbsa_code", "value", "member_role"]],
        on=["member_cbsa_code", "member_role"],
        how="left",
    )
    mapped["geometry"] = mapped.geom_wkb.map(lambda value: wkb.loads(bytes(value)))
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"cbsa_code": row.member_cbsa_code}, "geometry": mapping(row.geometry)}
            for row in mapped.itertuples()
        ],
    }
    map_figure = px.choropleth(
        mapped,
        geojson=geojson,
        locations="member_cbsa_code",
        featureidkey="properties.cbsa_code",
        color="value",
        hover_name="member_cbsa_name",
        hover_data={"member_role": True, "distance_miles": ":.1f"},
        color_continuous_scale="Viridis",
        projection="mercator",
        title=f"{target_cbsa_name}: active-lens KPI map",
    )
    map_figure.update_geos(fitbounds="locations", visible=False)
    map_figure.update_layout(margin={"r": 0, "t": 45, "l": 0, "b": 0})
    mo.vstack([
        mo.md(f"## Active comparison — {active_lens_id} ({active_parameter_value})"),
        mo.md("The table is CBSA-to-CBSA only. A centroid distance is geographic proximity, not travel behavior."),
        mo.ui.plotly(map_figure),
        mo.ui.table(active_comparison, page_size=25),
    ])
    return

@app.cell
def _(active_lens_id, active_parameter_value, duckdb, read_query, resolve_db_path, target_cbsa_code):
    _replacements = {"__CBSA_CODE__": target_cbsa_code, "__LENS_ID__": active_lens_id, "__PARAMETER_VALUE__": active_parameter_value, "__MIGRATION_YEAR__": "2022"}
    with duckdb.connect(resolve_db_path(), read_only=True) as _con:
        industry_role = read_query(_con, "regional_role_industry_role.sql", _replacements)
        jobs_workers = read_query(_con, "regional_role_jobs_workers.sql", _replacements)
        migration_exchange = read_query(_con, "regional_role_irs_partner_exchange.sql", _replacements)
    return industry_role, jobs_workers, migration_exchange


@app.cell
def _(industry_role, jobs_workers, migration_exchange, mo, px, target_cbsa_name):
    _industry = industry_role.melt(id_vars=["sector", "comparison_cbsa_coverage"], value_vars=["target_sector_share", "rest_of_lens_sector_share"], var_name="comparison", value_name="employment_share")
    _industry_chart = px.bar(_industry, x="sector", y="employment_share", color="comparison", barmode="group", title=f"{target_cbsa_name}: industry share versus the rest of the active lens")
    _jobs_chart = px.scatter(jobs_workers, x="workers_total", y="jobs_total", color="member_role", hover_name="member_cbsa_name", title="2023 workplace jobs versus resident workers")
    _jobs_chart.add_shape(type="line", x0=0, y0=0, x1=jobs_workers.workers_total.max(), y1=jobs_workers.workers_total.max(), line={"dash": "dash", "color": "gray"})
    mo.vstack([
        mo.md("## Industry role"),
        mo.md("Sector shares compare covered private employment. LQ is target context; this evidence does not assign an automatic role label."),
        _industry_chart, mo.ui.table(industry_role, page_size=10),
        mo.md("## Jobs versus resident workers"),
        mo.md("LODES WAC/RAC measures jobs located and workers living in each CBSA. The difference is descriptive—not inflow, outflow, or commuting."),
        _jobs_chart, mo.ui.table(jobs_workers, page_size=25),
        mo.md("## IRS partner-CBSA migration exchange"),
        mo.md("2022 household tax-return migration flows are rolled from county endpoints. Non-CBSA county rows are retained, and outside-lens partners remain visible. This is not commuting."),
        mo.ui.table(migration_exchange, page_size=30),
    ])
    return


@app.cell
def _(Path, duckdb, target_cbsa_code):
    # Resolve only a validated, analytical-boundary infrastructure handoff.
    _repo_root = Path(__file__).resolve().parents[3]
    _artifacts = sorted((_repo_root / "metro-deep-dive-program" / "engines" / "infrastructure" / "outputs").glob(f"**/*-{target_cbsa_code}-*/validated/osm_core_v1/infrastructure_feature.parquet"))
    infrastructure_artifact = _artifacts[-1] if _artifacts else None
    if infrastructure_artifact is None:
        infrastructure_features = None
    else:
        _escaped = str(infrastructure_artifact).replace("'", "''")
        with duckdb.connect() as _con:
            infrastructure_features = _con.execute(f"SELECT feature_group, feature_type, geometry, source_run_id, market_boundary_vintage, geometry_status FROM read_parquet('{_escaped}') WHERE record_status = 'retained' AND mapping_status IN ('mapped', 'overridden') AND geometry_status = 'valid'").fetchdf()
    return infrastructure_artifact, infrastructure_features


@app.cell
def _(gpd, infrastructure_artifact, infrastructure_features, mo, plt):
    if infrastructure_features is None:
        _ = mo.md("## Infrastructure context: no validated analytical-boundary handoff is available for this market.")
    else:
        _features = gpd.GeoDataFrame(infrastructure_features.drop(columns="geometry"), geometry=gpd.GeoSeries.from_wkb(infrastructure_features.geometry.map(bytes), crs="EPSG:26918"), crs="EPSG:26918").to_crs("EPSG:4326")
        _figure, _axis = plt.subplots(figsize=(10, 8))
        _features.plot(ax=_axis, column="feature_group", categorical=True, linewidth=0.25, alpha=0.65, legend=True)
        _axis.set(title="Validated Infrastructure context: roads, rail, and water network", axis_off=True)
        _figure.tight_layout()
        _ = mo.vstack([mo.md("## Infrastructure context"), mo.md(f"Validated analytical-boundary artifact: {infrastructure_artifact.name}. It is orientation evidence only: it does not supply routing, barriers, travel time, or a role score."), _figure, mo.ui.table(_features.groupby(["feature_group", "feature_type"]).size().reset_index(name="feature_count"), page_size=25)])
    return


@app.cell
def _(mo):
    hypothesis_notes = mo.ui.text_area(value="", label="Analyst-authored role hypothesis and caveats", placeholder="State a tentative role hypothesis, cite the visible evidence, and record counter-evidence or data limitations.", full_width=True)
    mo.vstack([mo.md("## Manual role-hypothesis evidence"), mo.md("This field intentionally does not classify the market. Pair any conclusion with the industry, jobs/workers, migration, and Infrastructure evidence above."), hypothesis_notes])
    return (hypothesis_notes,)



if __name__ == "__main__":
    app.run()
