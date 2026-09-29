import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This is a read-only review surface. The builder owns artifact creation so
    # exploring a basket or market cannot silently change a POI classification.
    from pathlib import Path

    import duckdb
    import json
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from pyproj import Transformer
    from shapely import wkb
    from shapely.ops import transform

    return Path, Transformer, duckdb, go, json, mo, pd, px, transform, wkb


@app.cell
def _(Path):
    analysis_dir = Path(__file__).resolve().parent
    output_dir = analysis_dir / "outputs" / "q4_poi_workbench_v1"
    hub_dir = analysis_dir / "outputs" / "q4_amenity_hub_basket_matrix_v1"
    profile_dir = analysis_dir / "outputs" / "q4_epic4_profiles_v1"
    required = ["q4_poi_workbench.parquet", "q4_poi_basket_catalog.parquet", "q4_poi_coverage.parquet", "q4_map_context.json", str(hub_dir / "q4_amenity_hub_inventory.parquet"), str(profile_dir / "q4_hub_typology_profile.parquet")]
    missing = [name for name in required if not (output_dir / name).exists()]
    if missing:
        raise FileNotFoundError("Run build_q4_poi_workbench.py first: " + ", ".join(missing))
    return hub_dir, output_dir, profile_dir


@app.cell
def _(duckdb, hub_dir, json, output_dir, profile_dir):
    with duckdb.connect() as con:
        catalog = con.execute("select * from read_parquet(?) order by basket_id", [str(output_dir / "q4_poi_basket_catalog.parquet")]).fetchdf()
        coverage = con.execute("select * from read_parquet(?) order by market_slug, mapping_status", [str(output_dir / "q4_poi_coverage.parquet")]).fetchdf()
        workbench = con.execute("select * from read_parquet(?)", [str(output_dir / "q4_poi_workbench.parquet")]).fetchdf()
        hub_inventory = con.execute("select * from read_parquet(?)", [str(hub_dir / "q4_amenity_hub_inventory.parquet")]).fetchdf()
        hub_membership = con.execute("select * from read_parquet(?)", [str(hub_dir / "q4_amenity_hub_membership.parquet")]).fetchdf()
        hub_profiles = con.execute("select * from read_parquet(?)", [str(profile_dir / "q4_hub_typology_profile.parquet")]).fetchdf()
        hub_tract_context = con.execute("select * from read_parquet(?)", [str(profile_dir / "q4_hub_tract_context.parquet")]).fetchdf()
    map_context = json.loads((output_dir / "q4_map_context.json").read_text(encoding="utf-8"))
    return catalog, coverage, hub_inventory, hub_membership, hub_profiles, hub_tract_context, map_context, workbench


@app.cell
def _(catalog, mo):
    market = mo.ui.dropdown(options={"Richmond, VA (40060)": "40060", "Jacksonville, FL (27260)": "27260"}, value="Richmond, VA (40060)", label="Pilot market")
    basket = mo.ui.dropdown(options={row.label: row.basket_id for row in catalog.itertuples(index=False)}, value="Broad livability", label="Amenity basket")
    mo.vstack([
        mo.md("# Explanation Q4 — POI Livability Workbench\nThis review surface starts with governed POI points. It shows basket membership and coverage; it does not measure access, walkability, or amenity quality."),
        mo.hstack([market, basket], justify="start"),
    ])
    return basket, market


@app.cell
def _(basket, catalog, coverage, market, mo, workbench):
    selected_catalog = catalog.loc[catalog.basket_id == basket.value]
    selected = workbench.loc[workbench.cbsa_code == market.value].copy()
    flag = f"is_{basket.value}"
    selected["basket_status"] = selected[flag].map({True: "In selected basket", False: "Outside selected basket"})
    selected_coverage = coverage.loc[coverage.cbsa_code == market.value]
    mapped = int(selected_coverage.loc[selected_coverage.mapping_status == "mapped", "poi_count"].sum())
    unmapped = int(selected_coverage.loc[selected_coverage.mapping_status == "unmapped", "poi_count"].sum())
    mo.vstack([
        mo.md(f"## Coverage and basket contract\n**{mapped:,} mapped** and **{unmapped:,} unclassified** retained POIs are visible for this market. Unclassified is a coverage state, not a zero-amenity result."),
        mo.ui.table(selected_catalog, selection=None),
        mo.ui.table(selected_coverage, selection=None),
    ])
    return selected,


@app.cell
def _(mo, selected):
    categories = sorted(selected.loc[selected.basket_status == "In selected basket", "category"].unique())
    category_filter = mo.ui.multiselect(options=categories, value=categories, label="Map categories")
    mo.vstack([mo.md("## POI map controls\nFilter the inventory map without changing basket membership or the summaries below."), category_filter])
    return (category_filter,)


@app.cell
def _(category_filter, go, map_context, market, mo, pd, px, selected):
    basket_points = selected.loc[selected.basket_status == "In selected basket"]
    basket_points = basket_points.loc[basket_points.category.isin(category_filter.value)]
    max_map_points = 25_000

    # Keep the browser payload small enough for a responsive review map while
    # preserving every governed category in a deterministic proportional sample.
    # The full selected-basket count remains visible above and in composition.
    if len(basket_points) > max_map_points:
        category_counts = basket_points.groupby("category").size()
        category_limits = (category_counts / category_counts.sum() * max_map_points).round().astype(int).clip(lower=1)
        map_points = pd.concat([
            group.sort_values("source_record_key").head(category_limits.loc[category])
            for category, group in basket_points.groupby("category")
        ])
    else:
        map_points = basket_points

    def line_trace(feature_collection, color, width, name):
        """Convert simplified GeoJSON boundaries or lines to one map trace."""
        longitude, latitude = [], []
        def add_path(coordinates):
            longitude.extend(point[0] for point in coordinates)
            latitude.extend(point[1] for point in coordinates)
            longitude.append(None)
            latitude.append(None)
        for feature in feature_collection["features"]:
            geometry = feature["geometry"]
            if geometry["type"] == "LineString":
                add_path(geometry["coordinates"])
            elif geometry["type"] == "MultiLineString":
                for line in geometry["coordinates"]:
                    add_path(line)
            elif geometry["type"] == "Polygon":
                for ring in geometry["coordinates"]:
                    add_path(ring)
            elif geometry["type"] == "MultiPolygon":
                for polygon in geometry["coordinates"]:
                    for ring in polygon:
                        add_path(ring)
        return go.Scattermap(lon=longitude, lat=latitude, mode="lines", line={"color": color, "width": width}, name=name, hoverinfo="skip")

    map_figure = px.scatter_map(
        map_points,
        lat="latitude",
        lon="longitude",
        color="category",
        hover_name="sub_category",
        hover_data={"longitude": False, "latitude": False},
        center={"lat": map_points["latitude"].mean(), "lon": map_points["longitude"].mean()},
        zoom=7,
        height=620,
        opacity=0.55,
        map_style="carto-positron",
        title="Selected basket POIs — map is inventory context, not an access surface",
    )
    context = map_context[market.value]
    map_figure.add_trace(line_trace(context["tracts"], "rgba(85,85,85,0.18)", 1, "Census tract boundary"))
    map_figure.add_trace(line_trace(context["counties"], "rgba(35,35,35,0.45)", 2, "County boundary"))
    mo.vstack([
        mo.md(f"Showing **{len(map_points):,} of {len(basket_points):,}** selected POIs on the map. When a basket exceeds 25,000 points, this is a deterministic proportional display sample by governed category; it does not change the basket or its composition counts."),
        mo.ui.plotly(map_figure),
    ])
    return (line_trace,)


@app.cell
def _(mo, selected):
    focus_categories = sorted(selected.loc[selected.basket_status == "In selected basket", "category"].unique())
    focus_category = mo.ui.dropdown(options=focus_categories, value=focus_categories[0], label="Category to inspect")
    mo.vstack([mo.md("## Category detail map\nSelect one governed category; its dots are colored by subcategory."), focus_category])
    return (focus_category,)


@app.cell
def _(focus_category, line_trace, map_context, market, mo, px, selected):
    focus_points = selected.loc[
        (selected.basket_status == "In selected basket") & (selected.category == focus_category.value)
    ].sort_values("source_record_key")
    focus_display = focus_points.head(25_000)
    focus_figure = px.scatter_map(
        focus_display,
        lat="latitude",
        lon="longitude",
        color="sub_category",
        hover_name="sub_category",
        hover_data={"longitude": False, "latitude": False},
        center={"lat": focus_display["latitude"].mean(), "lon": focus_display["longitude"].mean()},
        zoom=7,
        height=620,
        opacity=0.65,
        map_style="carto-positron",
        title=f"{focus_category.value} POIs by governed subcategory",
    )
    focus_context = map_context[market.value]
    focus_figure.add_trace(line_trace(focus_context["tracts"], "rgba(85,85,85,0.18)", 1, "Census tract boundary"))
    focus_figure.add_trace(line_trace(focus_context["counties"], "rgba(35,35,35,0.45)", 2, "County boundary"))
    mo.vstack([
        mo.md(f"Showing **{len(focus_display):,} of {len(focus_points):,}** `{focus_category.value}` POIs. A limit only applies when a category exceeds 25,000 points."),
        mo.ui.plotly(focus_figure),
    ])
    return


@app.cell
def _(go, line_trace, map_context, market, mo, selected):
    infrastructure_figure = go.Figure()
    infrastructure = map_context[market.value]["infrastructure"]
    colors = {"road": "#6b7280", "rail": "#9a3412", "water_network": "#0284c7"}
    for group, color in colors.items():
        features = [feature for feature in infrastructure["features"] if feature["properties"]["feature_group"] == group]
        infrastructure_figure.add_trace(line_trace({"features": features}, color, 1.5, group.replace("_", " ").title()))
    points = selected.loc[selected.basket_status == "In selected basket"]
    infrastructure_figure.update_layout(
        map={"style": "carto-positron", "center": {"lat": points.latitude.mean(), "lon": points.longitude.mean()}, "zoom": 7},
        height=620,
        title="Infrastructure review sample — display context only",
        legend_title="Validated OSM feature group",
    )
    mo.vstack([
        mo.md("## Infrastructure review map\nThis separate map shows validated OSM rail and water networks plus major roads (motorway, trunk, and primary). It supports visual review only; it does not identify barriers, routing, travel time, or access."),
        mo.ui.plotly(infrastructure_figure),
    ])
    return


@app.cell
def _(hub_inventory, market, mo):
    hub_basket = mo.ui.dropdown(
        options={"Proximity amenities": "proximity_amenities", "Errands and essentials": "errands_essentials", "Employment places": "employment_places"},
        value="Proximity amenities",
        label="Hub basket",
    )
    mo.vstack([mo.md("# Hub review\nReview candidates constructed from governed basket POIs. These are spatial concentration candidates, not access, walkability, service-area, or tract-ranking results."), hub_basket])
    return (hub_basket,)


@app.cell
def _(hub_basket, hub_inventory, market, mo):
    candidate_options = sorted(hub_inventory.loc[(hub_inventory.cbsa_code == market.value) & (hub_inventory.basket_id == hub_basket.value), "candidate_version"].unique())
    hub_candidate = mo.ui.dropdown(options=candidate_options, value=candidate_options[0], label="Density candidate")
    mo.vstack([mo.md("Candidate controls"), hub_candidate])
    return (hub_candidate,)


@app.cell
def _(hub_basket, hub_candidate, hub_inventory, market, mo):
    review_hubs = hub_inventory.loc[(hub_inventory.cbsa_code == market.value) & (hub_inventory.basket_id == hub_basket.value) & (hub_inventory.candidate_version == hub_candidate.value)].copy()
    hub_options = {f"{row.amenity_hub_id} — {row.poi_count:,} POIs": row.amenity_hub_id for row in review_hubs.sort_values("poi_count", ascending=False).itertuples(index=False)}
    selected_hub = mo.ui.dropdown(options=hub_options, value=next(iter(hub_options)), label="Hub detail")
    mo.vstack([mo.md(f"**{len(review_hubs):,} hubs** in this basket/candidate selection."), selected_hub])
    return review_hubs, selected_hub


@app.cell
def _(Transformer, go, hub_basket, hub_candidate, hub_membership, hub_profiles, hub_tract_context, map_context, market, mo, px, review_hubs, selected_hub, transform, wkb):
    hub_points = hub_membership.loc[(hub_membership.cbsa_code == market.value) & (hub_membership.basket_id == hub_basket.value) & (hub_membership.candidate_version == hub_candidate.value)]
    hub_figure = px.scatter_map(hub_points, lat="latitude", lon="longitude", color="category", hover_name="sub_category", hover_data={"longitude": False, "latitude": False}, center={"lat": hub_points.latitude.mean(), "lon": hub_points.longitude.mean()}, zoom=7, height=650, opacity=0.45, map_style="carto-positron", title="Candidate hub members and qualifying-cell outlines")
    inverse = Transformer.from_crs("EPSG:26918" if market.value == "40060" else "EPSG:26917", "EPSG:4326", always_xy=True)
    longitude, latitude = [], []
    for row in review_hubs.itertuples(index=False):
        geometry = transform(inverse.transform, wkb.loads(bytes(row.geometry_wkb)))
        for polygon in (geometry.geoms if geometry.geom_type == "MultiPolygon" else [geometry]):
            longitude.extend(point[0] for point in polygon.exterior.coords); latitude.extend(point[1] for point in polygon.exterior.coords); longitude.append(None); latitude.append(None)
    hub_figure.add_trace(go.Scattermap(lon=longitude, lat=latitude, mode="lines", line={"color": "#e66101", "width": 2}, name="Hub geometry", hoverinfo="skip"))
    _hub_context = map_context[market.value]
    # Use the same light geographic orientation layer as the POI review maps.
    for collection, _outline_color, width, name in ((_hub_context["tracts"], "rgba(85,85,85,0.18)", 1, "Census tract boundary"), (_hub_context["counties"], "rgba(35,35,35,0.45)", 2, "County boundary")):
        lon, lat = [], []
        for feature in collection["features"]:
            geometry = feature["geometry"]
            polygons = geometry["coordinates"] if geometry["type"] == "Polygon" else [ring for polygon in geometry["coordinates"] for ring in polygon]
            for ring in polygons: lon.extend(point[0] for point in ring); lat.extend(point[1] for point in ring); lon.append(None); lat.append(None)
        hub_figure.add_trace(go.Scattermap(lon=lon, lat=lat, mode="lines", line={"color": _outline_color, "width": width}, name=name, hoverinfo="skip"))
    detail = hub_profiles.loc[(hub_profiles.basket_id == hub_basket.value) & (hub_profiles.candidate_version == hub_candidate.value) & (hub_profiles.amenity_hub_id == selected_hub.value)]
    tract_detail = hub_tract_context.loc[(hub_tract_context.basket_id == hub_basket.value) & (hub_tract_context.candidate_version == hub_candidate.value) & (hub_tract_context.amenity_hub_id == selected_hub.value)].sort_values("member_poi_share", ascending=False)
    mo.vstack([mo.ui.plotly(hub_figure), mo.md("## Selected hub profile"), mo.ui.table(detail, selection=None), mo.md("## Member-tract context\nA tract appears only because it contains a member POI; this is not a catchment or an access result."), mo.ui.table(tract_detail, selection=None)])
    return


@app.cell
def _(mo, px, selected):
    category_composition = (
        selected.loc[selected.basket_status == "In selected basket"]
        .groupby("category")
        .size()
        .reset_index(name="poi_count")
        .sort_values("poi_count", ascending=True)
    )
    category_composition["basket_share"] = category_composition["poi_count"] / category_composition["poi_count"].sum()
    category_figure = px.bar(
        category_composition,
        x="poi_count",
        y="category",
        orientation="h",
        hover_data={"basket_share": ":.1%"},
        title="Selected-basket POIs by governed category",
    )
    mo.vstack([
        mo.md("## Category summary\nThis chart and table use every POI in the selected basket, including POIs not shown when the map uses its display sample."),
        mo.ui.plotly(category_figure),
        mo.ui.table(category_composition.sort_values("poi_count", ascending=False), selection=None),
    ])
    return


@app.cell
def _(mo, selected):
    composition = selected.groupby(["basket_status", "category", "sub_category"], dropna=False).size().reset_index(name="poi_count").sort_values("poi_count", ascending=False)
    mo.vstack([
        mo.md("## Category and subcategory composition\nUse this table to inspect what actually enters the selected basket before interpreting any hub or tract pattern."),
        mo.ui.table(composition, pagination=True, page_size=25),
    ])
    return


if __name__ == "__main__":
    app.run()
