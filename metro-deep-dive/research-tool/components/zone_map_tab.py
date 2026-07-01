"""Zone Map tab — tract-level zone cluster choropleth."""

from __future__ import annotations

import json

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from dd_db import get_zone_data, get_zone_geojson


ZONE_COLORS = px.colors.qualitative.Bold


def render_zone_map(cbsa_code: str, cbsa_name: str) -> None:
    st.subheader("Tract-Level Zone Map")

    zone_df = get_zone_data(cbsa_code)
    if zone_df.empty:
        st.warning("No zone data available for this metro.")
        return

    tract_count = len(zone_df)
    st.caption(f"{tract_count:,} tracts | Zone data from Phase 7")

    # Unified tract table — all zone types side by side
    st.subheader("Zone Summary — All Cluster Types")
    _render_unified_zone_table(zone_df)
    st.divider()

    # Zone type selector for choropleth
    zone_types = zone_df["zone_type"].dropna().unique().tolist() if "zone_type" in zone_df.columns else []
    if zone_types:
        selected_zone_type = st.selectbox("Zone type (for map view)", options=sorted(zone_types), index=0)
        display_df = zone_df[zone_df["zone_type"] == selected_zone_type].copy()
    else:
        display_df = zone_df.copy()

    cluster_col = "zone_kmeans_cluster"
    if cluster_col not in display_df.columns:
        st.warning("Zone cluster column not found.")
        return

    # Try to render choropleth using DuckDB spatial
    with st.spinner("Loading tract geometries…"):
        geojson = get_zone_geojson(cbsa_code)

    if geojson is None:
        st.info(
            "Tract geometry export requires the DuckDB spatial extension. "
            "Falling back to tabular zone summary."
        )
        _render_zone_table(display_df, cluster_col)
        return

    # Merge zone data into geojson properties
    zone_lookup = display_df.set_index("tract_geoid")[cluster_col].to_dict()
    score_lookup = display_df.set_index("tract_geoid")["national_composite_percentile"].to_dict() if "national_composite_percentile" in display_df.columns else {}
    oz_lookup = display_df.set_index("tract_geoid")["is_opportunity_zone"].to_dict() if "is_opportunity_zone" in display_df.columns else {}

    for feat in geojson["features"]:
        tid = feat["properties"]["tract_geoid"]
        feat["properties"]["zone_cluster"] = zone_lookup.get(tid)
        feat["properties"]["composite_pct"] = score_lookup.get(tid)
        feat["properties"]["is_oz"] = oz_lookup.get(tid, False)

    # Build choropleth
    plot_df = display_df[["tract_geoid", cluster_col]].copy()
    plot_df[cluster_col] = plot_df[cluster_col].astype(str)

    fig = px.choropleth_mapbox(
        plot_df,
        geojson=geojson,
        locations="tract_geoid",
        featureidkey="properties.tract_geoid",
        color=cluster_col,
        color_discrete_sequence=ZONE_COLORS,
        mapbox_style="carto-positron",
        zoom=9,
        center=_get_centroid(geojson),
        opacity=0.7,
        labels={cluster_col: "Zone Cluster"},
        title=f"{cbsa_name} — Zone Clusters ({selected_zone_type if zone_types else 'all'})",
    )
    fig.update_layout(height=600, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    _render_zone_summary(display_df, cluster_col)


def _get_centroid(geojson: dict) -> dict:
    lons, lats = [], []
    for feat in geojson["features"][:200]:
        geom = feat["geometry"]
        if geom["type"] == "Polygon":
            coords = geom["coordinates"][0]
        elif geom["type"] == "MultiPolygon":
            coords = geom["coordinates"][0][0]
        else:
            continue
        for lon, lat in coords[:5]:
            lons.append(lon)
            lats.append(lat)
    if lons:
        return {"lat": sum(lats) / len(lats), "lon": sum(lons) / len(lons)}
    return {"lat": 39.5, "lon": -98.35}


def _render_unified_zone_table(zone_df: pd.DataFrame) -> None:
    """One row per zone_kmeans_cluster per zone_type — tract count + avg national composite percentile."""
    if zone_df.empty or "zone_kmeans_cluster" not in zone_df.columns:
        st.caption("Zone cluster data not available.")
        return

    has_composite = "national_composite_percentile" in zone_df.columns
    has_oz = "is_opportunity_zone" in zone_df.columns

    agg = {"tract_geoid": "count"}
    rename = {"tract_geoid": "Tracts"}
    if has_composite:
        agg["national_composite_percentile"] = "mean"
        rename["national_composite_percentile"] = "Avg National Composite Pct"
    if has_oz:
        agg["is_opportunity_zone"] = "sum"
        rename["is_opportunity_zone"] = "OZ Tracts"

    group_cols = ["zone_type", "zone_kmeans_cluster"] if "zone_type" in zone_df.columns else ["zone_kmeans_cluster"]
    summary = (
        zone_df.groupby(group_cols)
        .agg(agg)
        .reset_index()
        .rename(columns=rename)
    )

    if has_composite:
        summary["Avg National Composite Pct"] = summary["Avg National Composite Pct"].map(
            lambda x: f"{x:.1f}" if pd.notna(x) else "—"
        )
    if has_oz:
        summary["OZ Tracts"] = summary["OZ Tracts"].map(lambda x: int(x) if pd.notna(x) else 0)

    if "zone_type" in summary.columns:
        summary = summary.rename(columns={"zone_type": "Zone Type", "zone_kmeans_cluster": "Cluster"})
    else:
        summary = summary.rename(columns={"zone_kmeans_cluster": "Cluster"})

    summary = summary.sort_values(["Zone Type", "Cluster"] if "Zone Type" in summary.columns else ["Cluster"])
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.caption(
        "**National Composite Pct** = tract's percentile rank nationally across all 78k tracts on a "
        "combined livability + opportunity + character score. Higher = stronger overall."
    )


def _render_zone_table(df: pd.DataFrame, cluster_col: str) -> None:
    summary = (
        df.groupby(cluster_col)
        .agg(
            tract_count=("tract_geoid", "count"),
            avg_composite_pct=("national_composite_percentile", "mean"),
            oz_tracts=("is_opportunity_zone", "sum"),
        )
        .reset_index()
        .rename(columns={
            cluster_col: "Zone Cluster",
            "tract_count": "Tracts",
            "avg_composite_pct": "Avg Composite Pct",
            "oz_tracts": "OZ Tracts",
        })
    )
    summary["Avg Composite Pct"] = summary["Avg Composite Pct"].map(
        lambda x: f"{x:.1f}" if pd.notna(x) else "—"
    )
    st.dataframe(summary, use_container_width=True, hide_index=True)


def _render_zone_summary(df: pd.DataFrame, cluster_col: str) -> None:
    st.subheader("Zone Cluster Summary")

    score_cols = [c for c in df.columns if "percentile" in c and "rank" not in c]
    summary_rows = []
    for cluster_id, group in df.groupby(cluster_col):
        row = {"Zone Cluster": int(cluster_id), "Tracts": len(group)}
        for sc in score_cols[:4]:
            col_label = sc.replace("_", " ").replace("percentile", "Pct").title()
            row[col_label] = f"{group[sc].mean():.1f}" if group[sc].notna().any() else "—"
        oz_col = "is_opportunity_zone"
        if oz_col in group.columns:
            row["OZ Tracts"] = int(group[oz_col].sum())
        summary_rows.append(row)

    if summary_rows:
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
