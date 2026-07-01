"""Phase 7 Tract KPI EDA — interactive Streamlit explorer.

Run from repo root:
    streamlit run exploration/intelligence_framework/phase_7_zone_methodology/app/app.py
"""

from __future__ import annotations

import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from config import APP_TITLE, KPI_IDS, THEME_COLORS, TRACT_KPIS
from db import (
    compute_coverage,
    get_tract_frame,
    load_cbsa_options,
    load_cross_frame_clusters,
)

st.set_page_config(layout="wide", page_title=APP_TITLE)

# ---------------------------------------------------------------------------
# Sidebar — geography filter
# ---------------------------------------------------------------------------

def _render_sidebar() -> tuple[str | None, tuple[str, ...] | None]:
    with st.sidebar:
        st.title("Phase 7 EDA")
        st.markdown("**Geography**")

        cbsa_options = load_cbsa_options()
        cbsa_display = {code: name for code, name in cbsa_options}

        scope = st.radio("Scope", ["National (all CBSAs)", "Select CBSAs"], index=0)
        selected_codes: tuple[str, ...] | None = None

        if scope == "Select CBSAs":
            selected = st.multiselect(
                "CBSAs",
                options=[code for code, _ in cbsa_options],
                format_func=lambda code: cbsa_display.get(code, code),
                default=[],
            )
            if selected:
                selected_codes = tuple(selected)

        st.markdown("---")
        st.markdown("**KPI**")
        theme_filter = st.multiselect(
            "Theme filter",
            options=["Character", "Livability", "Opportunity"],
            default=["Character", "Livability", "Opportunity"],
        )
        available_kpis = [k for k in TRACT_KPIS if k["theme"] in theme_filter]
        selected_kpi_id = st.selectbox(
            "Selected KPI (tabs 2–4)",
            options=[k["kpi_id"] for k in available_kpis],
            format_func=lambda kpi_id: next(
                (k["display_name"] for k in TRACT_KPIS if k["kpi_id"] == kpi_id), kpi_id
            ),
        )

    return selected_kpi_id, selected_codes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _kpi_meta(kpi_id: str) -> dict:
    return next((k for k in TRACT_KPIS if k["kpi_id"] == kpi_id), {"display_name": kpi_id, "theme": "Unknown"})


def _theme_color(theme: str) -> str:
    return THEME_COLORS.get(theme, "#888888")


def _log_safe(series: pd.Series) -> pd.Series:
    """Log-transform a series, clipping non-positive values to a small positive floor."""
    floor = series[series > 0].min() * 0.01 if (series > 0).any() else 1e-6
    return np.log1p(series.clip(lower=floor))


def _cbsa_name_map() -> dict[str, str]:
    return {code: name for code, name in load_cbsa_options()}


def _format_cbsa_label(cbsa_code: str, cbsa_names: dict[str, str]) -> str:
    cbsa_name = cbsa_names.get(cbsa_code, cbsa_code)
    return f"{cbsa_name} ({cbsa_code})" if cbsa_name != cbsa_code else cbsa_code


# ---------------------------------------------------------------------------
# Tab 1 — Coverage & Missingness
# ---------------------------------------------------------------------------

def _render_coverage_tab(df: pd.DataFrame) -> None:
    st.subheader("Coverage & Missingness")
    coverage_df = compute_coverage(df)

    flag_threshold = st.slider("Flag threshold: % missing", 0, 50, 20, step=5)

    flagged = coverage_df[coverage_df["pct_missing"] > flag_threshold]
    if not flagged.empty:
        st.warning(
            f"{len(flagged)} KPI(s) exceed {flag_threshold}% missing: "
            + ", ".join(flagged["display_name"].tolist())
        )
    else:
        st.success(f"All KPIs are within the {flag_threshold}% missingness threshold.")

    fig = px.bar(
        coverage_df.sort_values("pct_missing", ascending=False),
        x="display_name",
        y="pct_missing",
        color="theme",
        color_discrete_map=THEME_COLORS,
        labels={"display_name": "KPI", "pct_missing": "% Missing"},
        title=f"Missingness by KPI  (n={len(df):,} tracts)",
        height=400,
    )
    fig.add_hline(y=flag_threshold, line_dash="dash", line_color="red",
                  annotation_text=f"{flag_threshold}% threshold")
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Full coverage table"):
        display_cols = ["display_name", "theme", "n_present", "n_missing", "pct_present", "pct_missing"]
        st.dataframe(
            coverage_df[display_cols].rename(columns={"display_name": "KPI"}).reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )


# ---------------------------------------------------------------------------
# Tab 2 — Distribution
# ---------------------------------------------------------------------------

def _render_distribution_tab(df: pd.DataFrame, kpi_id: str) -> None:
    meta = _kpi_meta(kpi_id)
    cbsa_names = _cbsa_name_map()
    st.subheader(f"Distribution — {meta['display_name']}")

    col1, col2, col3 = st.columns(3)
    log_transform = col1.checkbox("Log transform", value=False)
    n_bins = col2.slider("Bins", 20, 100, 40, step=10)
    cbsa_overlay = col3.selectbox(
        "Overlay single CBSA",
        options=["(none)"] + sorted(df["cbsa_code"].unique().tolist()),
        format_func=lambda code: "(none)" if code == "(none)" else _format_cbsa_label(code, cbsa_names),
    )

    series = df[kpi_id].dropna()
    if series.empty:
        st.warning(f"No data available for {kpi_id}.")
        return

    plot_series = _log_safe(series) if log_transform else series
    label = f"log({meta['display_name']})" if log_transform else meta["display_name"]

    skewness = float(series.skew())
    kurtosis = float(series.kurtosis())
    median_val = float(series.median())
    p10 = float(series.quantile(0.10))
    p90 = float(series.quantile(0.90))

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Median", f"{median_val:,.2f}")
    m2.metric("P10", f"{p10:,.2f}")
    m3.metric("P90", f"{p90:,.2f}")
    m4.metric("Skewness", f"{skewness:.2f}")
    m5.metric("Excess Kurtosis", f"{kurtosis:.2f}")
    st.caption(
        "Skewness shows whether the distribution leans left or right. "
        "Excess kurtosis shows whether the tails are unusually heavy and outlier-prone."
    )

    if abs(skewness) > 1.5 and not log_transform:
        st.info("High skewness detected — consider enabling log transform.")

    plot_df = pd.DataFrame({"value": plot_series, "group": "National"})

    if cbsa_overlay != "(none)":
        cbsa_series = df[df["cbsa_code"] == cbsa_overlay][kpi_id].dropna()
        if not cbsa_series.empty:
            cbsa_plot = _log_safe(cbsa_series) if log_transform else cbsa_series
            overlay_label = _format_cbsa_label(cbsa_overlay, cbsa_names)
            overlay_df = pd.DataFrame({"value": cbsa_plot, "group": overlay_label})
            plot_df = pd.concat([plot_df, overlay_df], ignore_index=True)
            st.caption(
                f"Overlaying {overlay_label} with {len(cbsa_series):,} non-null tracts "
                f"out of {int((df['cbsa_code'] == cbsa_overlay).sum()):,} tracts in scope."
            )

    fig = px.histogram(
        plot_df,
        x="value",
        color="group",
        nbins=n_bins,
        barmode="overlay",
        opacity=0.7,
        color_discrete_sequence=[_theme_color(meta["theme"]), "#d94801"],
        labels={"value": label},
        title=f"{label}  (n={len(series):,} non-null tracts)",
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Tab 3 — Correlation Matrix
# ---------------------------------------------------------------------------

def _render_correlation_tab(df: pd.DataFrame) -> None:
    st.subheader("KPI × KPI Correlation Matrix")

    r_threshold = st.slider("Highlight |r| ≥", 0.0, 1.0, 0.75, step=0.05)
    corr_method = st.radio("Method", ["Pearson", "Spearman"], horizontal=True)
    st.caption(
        "Pearson measures straight-line correlation. Spearman measures whether KPI rankings move "
        "together even when the pattern is curved or nonlinear."
    )

    available_kpis = [k for k in KPI_IDS if k in df.columns and df[k].notna().sum() > 30]
    corr_df = df[available_kpis].copy()

    if corr_method == "Spearman":
        corr_matrix = corr_df.rank().corr()
    else:
        corr_matrix = corr_df.corr()

    labels = [
        next((k["display_name"] for k in TRACT_KPIS if k["kpi_id"] == kid), kid)
        for kid in available_kpis
    ]

    fig = px.imshow(
        corr_matrix.values,
        x=labels,
        y=labels,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title=f"{corr_method} Correlation — {len(available_kpis)} KPIs",
        height=620,
        aspect="auto",
    )
    fig.update_layout(coloraxis_colorbar=dict(title="r"))
    st.plotly_chart(fig, use_container_width=True)

    # High-correlation pairs table
    st.markdown(f"**Pairs with |r| ≥ {r_threshold}**")
    pairs = []
    vals = corr_matrix.values
    for i in range(len(available_kpis)):
        for j in range(i + 1, len(available_kpis)):
            r = vals[i][j]
            if abs(r) >= r_threshold:
                pairs.append({
                    "KPI A": labels[i],
                    "KPI B": labels[j],
                    "r": round(float(r), 3),
                    "|r|": round(abs(float(r)), 3),
                })
    if pairs:
        pairs_df = pd.DataFrame(pairs).sort_values("|r|", ascending=False)
        st.dataframe(pairs_df.drop(columns=["|r|"]), use_container_width=True, hide_index=True)
    else:
        st.info(f"No pairs exceed |r| = {r_threshold}.")


# ---------------------------------------------------------------------------
# Tab 4 — Bivariate Scatter
# ---------------------------------------------------------------------------

def _render_scatter_tab(df: pd.DataFrame, default_kpi_id: str) -> None:
    st.subheader("Bivariate Scatter")
    cbsa_names = _cbsa_name_map()

    available_kpis = [k for k in TRACT_KPIS if k["kpi_id"] in df.columns]
    kpi_ids = [k["kpi_id"] for k in available_kpis]

    def _idx(kpi_id: str) -> int:
        return kpi_ids.index(kpi_id) if kpi_id in kpi_ids else 0

    col1, col2, col3 = st.columns(3)
    x_kpi = col1.selectbox("X Axis", kpi_ids, index=_idx(default_kpi_id),
                            format_func=lambda k: next((x["display_name"] for x in TRACT_KPIS if x["kpi_id"] == k), k))
    y_kpi = col2.selectbox("Y Axis", kpi_ids, index=_idx("median_hh_income") if "median_hh_income" in kpi_ids else 0,
                            format_func=lambda k: next((x["display_name"] for x in TRACT_KPIS if x["kpi_id"] == k), k))
    color_by = col3.selectbox("Color by", ["CBSA Cross-Frame Cluster", "CBSA", "None"])

    log_x = st.checkbox("Log X", value=False)
    log_y = st.checkbox("Log Y", value=False)

    scatter_df = df[["tract_geoid", "cbsa_code", x_kpi, y_kpi]].dropna().copy()
    if scatter_df.empty:
        st.warning("No rows with data on both selected KPIs.")
        return

    scatter_df["cbsa_label"] = scatter_df["cbsa_code"].map(
        lambda code: _format_cbsa_label(code, cbsa_names)
    )

    cluster_warning = None
    if color_by == "CBSA Cross-Frame Cluster":
        try:
            cluster_df = load_cross_frame_clusters()
            scatter_df = scatter_df.merge(cluster_df, on="cbsa_code", how="left")
            scatter_df["combined_cluster"] = scatter_df["combined_cluster"].fillna("Cluster unavailable")
        except FileNotFoundError:
            scatter_df["combined_cluster"] = "Cluster unavailable"
            cluster_warning = (
                "Cross-frame cluster labels are not available in the current environment, "
                "so points fall back to 'Cluster unavailable'."
            )

    x_label = next((k["display_name"] for k in TRACT_KPIS if k["kpi_id"] == x_kpi), x_kpi)
    y_label = next((k["display_name"] for k in TRACT_KPIS if k["kpi_id"] == y_kpi), y_kpi)

    plot_df = scatter_df.copy()
    if log_x:
        plot_df[x_kpi] = _log_safe(plot_df[x_kpi])
        x_label = f"log({x_label})"
    if log_y:
        plot_df[y_kpi] = _log_safe(plot_df[y_kpi])
        y_label = f"log({y_label})"

    # Sample to keep Plotly responsive at tract scale
    MAX_POINTS = 15_000
    if len(plot_df) > MAX_POINTS:
        plot_df = plot_df.sample(MAX_POINTS, random_state=42)
        st.caption(f"Showing a random sample of {MAX_POINTS:,} tracts for performance.")

    color_col = None
    color_map = None
    if color_by == "CBSA Cross-Frame Cluster":
        color_col = "combined_cluster"
    elif color_by == "CBSA":
        color_col = "cbsa_label"

    hover_data = {
        "tract_geoid": True,
        "cbsa_label": True,
        "cbsa_code": False,
    }
    if "combined_cluster" in plot_df.columns:
        hover_data["combined_cluster"] = True

    fig = px.scatter(
        plot_df,
        x=x_kpi,
        y=y_kpi,
        color=color_col,
        color_discrete_map=color_map,
        hover_data=hover_data,
        labels={x_kpi: x_label, y_kpi: y_label},
        opacity=0.5,
        title=f"{x_label} vs {y_label}  (n={len(plot_df):,} tracts)",
        height=500,
    )
    fig.update_traces(marker=dict(size=4))
    st.plotly_chart(fig, use_container_width=True)
    if cluster_warning:
        st.info(cluster_warning)
    elif color_by == "CBSA Cross-Frame Cluster":
        st.caption(
            "Points are colored by the tract's home CBSA cross-frame cluster, "
            "so the scatter can be read through the metro lens we already know."
        )

    # Inline correlation
    r = float(scatter_df[x_kpi].corr(scatter_df[y_kpi]))
    rho = float(scatter_df[x_kpi].rank().corr(scatter_df[y_kpi].rank()))
    st.caption(f"Pearson r = **{r:.3f}**  |  Spearman ρ = **{rho:.3f}**  (full non-null sample, n={len(scatter_df):,})")


# ---------------------------------------------------------------------------
# Tab 5 — Within-CBSA Variance
# ---------------------------------------------------------------------------

def _render_within_cbsa_tab(df: pd.DataFrame, kpi_id: str) -> None:
    meta = _kpi_meta(kpi_id)
    cbsa_names = _cbsa_name_map()
    st.subheader(f"Within-CBSA Variance — {meta['display_name']}")

    st.markdown(
        "Box plots show the distribution of this KPI **across tracts within each CBSA**. "
        "KPIs with wide boxes are doing meaningful work at zone grain. "
        "Narrow boxes mean the KPI differentiates CBSAs but not neighborhoods."
    )
    with st.expander("How to read this chart"):
        st.markdown(
            "- Each box is one CBSA.\n"
            "- The center line is the median tract value in that CBSA.\n"
            "- Taller boxes mean more tract-to-tract variation inside that metro.\n"
            "- Short boxes mean the KPI changes more between metros than within them.\n"
            "- The ratio below compares average within-metro spread to national spread."
        )

    min_tracts = st.slider("Min tracts per CBSA to show", 5, 50, 20, step=5)
    n_cbsas = st.slider("Max CBSAs to display", 10, 60, 30, step=5)
    sort_by = st.radio("Sort CBSAs by", ["Median", "IQR (spread)"], horizontal=True)

    col_data = df[["cbsa_code", kpi_id]].dropna()
    cbsa_counts = col_data.groupby("cbsa_code")[kpi_id].count()
    valid_cbsas = cbsa_counts[cbsa_counts >= min_tracts].index.tolist()
    col_data = col_data[col_data["cbsa_code"].isin(valid_cbsas)]

    if col_data.empty:
        st.warning(f"No CBSAs have ≥{min_tracts} tracts with data for {kpi_id}.")
        return

    cbsa_stats = col_data.groupby("cbsa_code")[kpi_id].agg(
        median="median",
        q25=lambda x: x.quantile(0.25),
        q75=lambda x: x.quantile(0.75),
    ).reset_index()
    cbsa_stats["iqr"] = cbsa_stats["q75"] - cbsa_stats["q25"]

    sort_col = "median" if sort_by == "Median" else "iqr"
    top_cbsas = (
        cbsa_stats.sort_values(sort_col, ascending=False)
        .head(n_cbsas)["cbsa_code"]
        .tolist()
    )
    plot_df = col_data[col_data["cbsa_code"].isin(top_cbsas)].copy()
    plot_df["cbsa_label"] = plot_df["cbsa_code"].map(
        lambda code: _format_cbsa_label(code, cbsa_names)
    )
    top_cbsa_labels = [_format_cbsa_label(code, cbsa_names) for code in top_cbsas]
    st.caption(
        f"Showing {len(top_cbsas):,} CBSAs from the current scope with at least {min_tracts} non-null tracts."
    )

    fig = px.box(
        plot_df,
        x="cbsa_label",
        y=kpi_id,
        color_discrete_sequence=[_theme_color(meta["theme"])],
        labels={"cbsa_label": "CBSA", kpi_id: meta["display_name"]},
        hover_data={"cbsa_code": True},
        title=f"Within-CBSA tract distribution — {meta['display_name']}",
        height=500,
    )
    fig.update_xaxes(tickangle=45, categoryorder="array", categoryarray=top_cbsa_labels)
    st.plotly_chart(fig, use_container_width=True)

    # National IQR summary
    national_iqr = float(df[kpi_id].quantile(0.75) - df[kpi_id].quantile(0.25))
    avg_within_cbsa_iqr = float(cbsa_stats["iqr"].mean())
    ratio = avg_within_cbsa_iqr / national_iqr if national_iqr > 0 else float("nan")

    m1, m2, m3 = st.columns(3)
    m1.metric("National IQR", f"{national_iqr:,.2f}")
    m2.metric("Avg Within-CBSA IQR", f"{avg_within_cbsa_iqr:,.2f}")
    m3.metric("Within/National ratio", f"{ratio:.2f}" if not math.isnan(ratio) else "—")
    st.caption(
        "A ratio close to 1 means this KPI varies as much within CBSAs as it does nationally — "
        "high zone-clustering value. A ratio near 0 means it mostly separates CBSAs, not neighborhoods."
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    st.title(APP_TITLE)
    st.caption(
        "EDA tool for the Phase 7 zone clustering input set. "
        "Reads Gold tract tables from DuckDB. Data is cached for 1 hour."
    )

    selected_kpi_id, selected_cbsa_codes = _render_sidebar()

    with st.spinner("Loading tract frame…"):
        df = get_tract_frame(cbsa_codes=selected_cbsa_codes)

    if df.empty:
        st.error("No tract data found. Check that Gold tract rows exist in DuckDB.")
        return

    scope_label = (
        f"{len(selected_cbsa_codes)} CBSA(s)" if selected_cbsa_codes else "National"
    )
    st.caption(f"**Scope:** {scope_label}  |  **Tracts loaded:** {len(df):,}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Coverage",
        "Distribution",
        "Correlations",
        "Scatter",
        "Within-CBSA Variance",
    ])

    with tab1:
        _render_coverage_tab(df)

    with tab2:
        _render_distribution_tab(df, selected_kpi_id)

    with tab3:
        _render_correlation_tab(df)

    with tab4:
        _render_scatter_tab(df, selected_kpi_id)

    with tab5:
        _render_within_cbsa_tab(df, selected_kpi_id)


if __name__ == "__main__":
    main()
