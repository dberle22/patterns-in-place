import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This setup workbench only reads governed Geography results. It never
    # recomputes adjacency, centroids, or regional membership in notebook code.
    import os
    from pathlib import Path

    import duckdb
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    from shapely import wkb
    from shapely.geometry import mapping

    return Path, duckdb, mapping, mo, os, pd, px, wkb


@app.cell
def _(Path, os, pd):
    analysis_dir = Path(__file__).resolve().parent
    query_dir = analysis_dir / "queries"
    repo_root = analysis_dir.parents[3]

    def resolve_db_path():
        """Prefer DB_PATH while keeping the repository-local development default."""

        return os.environ.get("DB_PATH", "").strip() or str(
            repo_root / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
        )

    def read_query(con, name, replacements=None):
        """Read a named SQL surface after binding controlled dropdown values."""

        sql = (query_dir / name).read_text()
        for token, value in (replacements or {}).items():
            sql = sql.replace(token, str(value))
        return con.execute(sql).fetchdf()

    return read_query, resolve_db_path


@app.cell
def _(duckdb, read_query, resolve_db_path):
    with duckdb.connect(resolve_db_path(), read_only=True) as _con:
        cbsa_options = read_query(_con, "regional_role_cbsa_options.sql")
    return (cbsa_options,)


@app.cell
def _(cbsa_options, mo, os):
    choices = dict(zip(cbsa_options.display_name, cbsa_options.cbsa_code))
    default_code = os.environ.get("REGIONAL_ROLE_CBSA_CODE", "40060").strip()
    _default_market_label = next((label for label, code in choices.items() if code == default_code), next(iter(choices)))
    market_selector = mo.ui.dropdown(choices, value=_default_market_label, label="Target metropolitan CBSA", searchable=True)
    mo.vstack([
        mo.md("# Regional Role — Region Setup"),
        mo.md("Inspect the governed membership before interpreting a market's regional role. The radius is geographic proximity, not travel time."),
        market_selector,
    ])
    return (market_selector,)


@app.cell
def _(duckdb, market_selector, read_query, resolve_db_path):
    target_cbsa_code = market_selector.value
    with duckdb.connect(resolve_db_path(), read_only=True) as _con:
        membership = read_query(_con, "regional_role_setup_membership.sql", {"__CBSA_CODE__": target_cbsa_code})
        overlap = read_query(_con, "regional_role_setup_overlap.sql", {"__CBSA_CODE__": target_cbsa_code})
    if membership.empty:
        raise ValueError(f"No governed Regional Role membership is available for CBSA {target_cbsa_code}.")
    target_cbsa_name = membership.target_cbsa_name.iloc[0]
    return membership, overlap, target_cbsa_code, target_cbsa_name


@app.cell
def _(membership, mo):
    lens_options = {}
    for row in membership[["lens_id", "parameter_value"]].drop_duplicates().itertuples(index=False):
        label = row.lens_id if row.parameter_value == "none" else f"{row.lens_id} ({row.parameter_value} miles)"
        lens_options[label] = f"{row.lens_id}|{row.parameter_value}"
    _default_lens_label = next(label for label, value in lens_options.items() if value == "cbsa_centroid_250mi|250")
    lens_selector = mo.ui.dropdown(lens_options, value=_default_lens_label, label="Declared lens")
    mo.vstack([
        mo.md("## Lens and membership provenance"),
        mo.md("The 200-, 250-, and 300-mile entries are stored sensitivity memberships from the same declared centroid method."),
        lens_selector,
    ])
    return (lens_selector,)


@app.cell
def _(lens_selector):
    selected_lens_id, selected_parameter_value = lens_selector.value.split("|", 1)
    return selected_lens_id, selected_parameter_value


@app.cell
def _(duckdb, read_query, resolve_db_path, selected_lens_id, selected_parameter_value, target_cbsa_code):
    with duckdb.connect(resolve_db_path(), read_only=True) as _con:
        map_rows = read_query(
            _con,
            "regional_role_setup_map.sql",
            {
                "__CBSA_CODE__": target_cbsa_code,
                "__LENS_ID__": selected_lens_id,
                "__PARAMETER_VALUE__": selected_parameter_value,
            },
        )
    return (map_rows,)


@app.cell
def _(map_rows, mapping, mo, px, selected_lens_id, selected_parameter_value, target_cbsa_name, wkb):
    mapped = map_rows.copy()
    mapped["geometry"] = mapped.geom_wkb.map(lambda value: wkb.loads(bytes(value)))
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"cbsa_code": row.member_cbsa_code},
                "geometry": mapping(row.geometry),
            }
            for row in mapped.itertuples()
        ],
    }
    figure = px.choropleth(
        mapped,
        geojson=geojson,
        locations="member_cbsa_code",
        featureidkey="properties.cbsa_code",
        color="member_role",
        hover_name="member_cbsa_name",
        hover_data={"distance_miles": ":.1f"},
        color_discrete_map={"target": "#d94801", "comparison": "#4c78a8"},
        projection="mercator",
        title=f"{target_cbsa_name}: {selected_lens_id} membership",
    )
    figure.update_geos(fitbounds="locations", visible=False)
    figure.update_layout(margin={"r": 0, "t": 45, "l": 0, "b": 0})
    mo.vstack([
        mo.md("## Active-lens boundary map"),
        mo.md("Map geometry is display-only. Membership was created from the separate full-TIGER analytical geometry surface."),
        mo.ui.plotly(figure),
    ])
    return


@app.cell
def _(membership, mo, overlap, target_cbsa_name):
    counts = (
        membership.groupby(["lens_id", "parameter_value"], as_index=False)
        .agg(member_count=("member_cbsa_code", "size"), boundary_vintage=("boundary_vintage", "first"), method_version=("method_version", "first"))
        .sort_values(["lens_id", "parameter_value"])
    )
    overlap_matrix = overlap.pivot(index="left_lens", columns="right_lens", values="jaccard_overlap").round(3)
    provenance = membership[
        ["lens_id", "parameter_value", "membership_source", "boundary_vintage", "method_version"]
    ].drop_duplicates().sort_values(["lens_id", "parameter_value"])
    mo.vstack([
        mo.md(f"## {target_cbsa_name}: membership review"),
        mo.md("Counts, overlap, and source metadata remain visible so a surprising regional boundary can be corrected before downstream interpretation."),
        mo.ui.table(counts, page_size=10),
        mo.md("### Pairwise Jaccard overlap"),
        mo.ui.table(overlap_matrix.reset_index(), page_size=10),
        mo.md("### Provenance"),
        mo.ui.table(provenance, page_size=20),
    ])
    return


if __name__ == "__main__":
    app.run()
