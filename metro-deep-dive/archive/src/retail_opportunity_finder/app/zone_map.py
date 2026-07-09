"""Zone Explorer helper functions: data loading, color ramp, and PyDeck layers."""

from __future__ import annotations

from collections import OrderedDict

import pandas as pd
import pydeck as pdk

from retail_opportunity_finder.utils.geo import add_polygon_coords

_NULL_COLOR = [160, 160, 160, 80]
_LO_COLOR = [239, 243, 255, 200]
_HI_COLOR = [8, 48, 107, 220]
_GATE_PASS_COLOR = [40, 167, 69, 200]
_GATE_FAIL_COLOR = [220, 53, 69, 200]

_GATE_COLS = frozenset({"gate_pop", "gate_price", "gate_density", "eligible_v1"})
_INVERTED_COLS = frozenset({"pov_rate"})


def load_tract_data(con, cbsa_code: str) -> pd.DataFrame:
    """Returns tract geometry joined with features, scores, and retail intensity."""
    return con.execute(
        """
        SELECT
            tg.tract_geoid,
            tg.geom_wkt,
            tf.county_geoid,
            tf.pop_total,
            tf.pop_growth_3yr,
            tf.median_hh_income,
            tf.per_capita_income,
            tf.pov_rate,
            tf.median_gross_rent,
            tf.median_home_value,
            tf.pop_density,
            tf.units_per_1k_3yr,
            ts.tract_score,
            ts.eligible_v1,
            ts.gate_pop,
            ts.gate_price,
            ts.gate_density,
            ri.retail_parcel_count,
            ri.retail_area_density,
            ri.local_retail_context_score
        FROM rof_gold.tract_geometry tg
        LEFT JOIN rof_gold.tract_features tf
            ON tg.cbsa_code = tf.cbsa_code AND tg.tract_geoid = tf.tract_geoid
        LEFT JOIN rof_gold.tract_scores ts
            ON tg.cbsa_code = ts.cbsa_code AND tg.tract_geoid = ts.tract_geoid
        LEFT JOIN rof_gold.retail_intensity_by_tract ri
            ON tg.cbsa_code = ri.cbsa_code AND tg.tract_geoid = ri.tract_geoid
        WHERE tg.cbsa_code = ?
        """,
        [cbsa_code],
    ).df()


def load_zone_data(con, market_key: str, zone_system: str) -> pd.DataFrame:
    """Returns zone geometry joined with summary stats for the given zone system."""
    if zone_system == "cluster":
        return con.execute(
            """
            SELECT
                czg.cluster_id      AS zone_id,
                czg.cluster_label   AS zone_label,
                czg.cluster_order   AS zone_order,
                czg.label_lon,
                czg.label_lat,
                czg.geom_wkt,
                czs.tracts,
                czs.total_population,
                czs.pop_growth_3yr_wtd,
                czs.pop_density_median,
                czs.units_per_1k_3yr_wtd,
                czs.price_proxy_pctl_median,
                czs.mean_tract_score
            FROM rof_gold.cluster_zone_geometries czg
            LEFT JOIN rof_gold.cluster_zone_summary czs
                ON czg.market_key = czs.market_key AND czg.cluster_id = czs.cluster_id
            WHERE czg.market_key = ?
            ORDER BY czg.cluster_order
            """,
            [market_key],
        ).df()
    else:
        return con.execute(
            """
            SELECT
                czg.zone_id,
                czg.zone_label,
                czg.zone_order,
                czg.label_lon,
                czg.label_lat,
                czg.geom_wkt,
                czs.tracts,
                czs.total_population,
                czs.pop_growth_3yr_wtd,
                czs.pop_density_median,
                czs.units_per_1k_3yr_wtd,
                czs.price_proxy_pctl_median,
                czs.mean_tract_score
            FROM rof_gold.contiguity_zone_geometries czg
            LEFT JOIN rof_gold.contiguity_zone_summary czs
                ON czg.market_key = czs.market_key AND czg.zone_id = czs.zone_id
            WHERE czg.market_key = ?
            ORDER BY czg.zone_order
            """,
            [market_key],
        ).df()


def load_cluster_tract_data(con, market_key: str) -> pd.DataFrame:
    """Returns tract metrics joined to their cluster assignment for a market."""
    return con.execute(
        """
        SELECT
            ca.cluster_id    AS zone_id,
            ca.cluster_label AS zone_label,
            ca.cluster_order AS zone_order,
            ca.tract_geoid,
            tf.county_geoid,
            tf.pop_total,
            tf.pop_growth_3yr,
            tf.median_hh_income,
            tf.per_capita_income,
            tf.pov_rate,
            tf.median_gross_rent,
            tf.median_home_value,
            tf.pop_density,
            tf.units_per_1k_3yr,
            ts.tract_score,
            ts.eligible_v1,
            ts.gate_pop,
            ts.gate_price,
            ts.gate_density,
            ri.retail_parcel_count,
            ri.retail_area_density,
            ri.local_retail_context_score
        FROM rof_gold.cluster_assignments ca
        LEFT JOIN rof_gold.tract_features tf
            ON ca.cbsa_code = tf.cbsa_code AND ca.tract_geoid = tf.tract_geoid
        LEFT JOIN rof_gold.tract_scores ts
            ON ca.cbsa_code = ts.cbsa_code AND ca.tract_geoid = ts.tract_geoid
        LEFT JOIN rof_gold.retail_intensity_by_tract ri
            ON ca.cbsa_code = ri.cbsa_code AND ca.tract_geoid = ri.tract_geoid
        WHERE ca.market_key = ?
        ORDER BY ca.cluster_order, ca.tract_geoid
        """,
        [market_key],
    ).df()


def build_metric_options() -> OrderedDict[str, str]:
    """Returns an ordered dict of {display label: column name} for the metric selector."""
    return OrderedDict([
        # Demographics
        ("Population", "pop_total"),
        ("Pop Growth (3yr)", "pop_growth_3yr"),
        ("Median HH Income", "median_hh_income"),
        ("Per Capita Income", "per_capita_income"),
        ("Poverty Rate", "pov_rate"),
        # Housing
        ("Median Gross Rent", "median_gross_rent"),
        ("Median Home Value", "median_home_value"),
        # Activity
        ("Population Density", "pop_density"),
        ("Building Permits / 1k", "units_per_1k_3yr"),
        # Scores
        ("Tract Score", "tract_score"),
        ("Gate: Population", "gate_pop"),
        ("Gate: Price Proxy", "gate_price"),
        ("Gate: Density", "gate_density"),
        # Retail context
        ("Retail Parcel Count", "retail_parcel_count"),
        ("Retail Area Density", "retail_area_density"),
        ("Local Retail Context Score", "local_retail_context_score"),
    ])


def apply_color_ramp(df: pd.DataFrame, metric_col: str) -> pd.DataFrame:
    """Adds fill_color column ([R, G, B, A] lists) based on metric_col. Null-safe."""
    df = df.copy().reset_index(drop=True)

    def _lerp(t: float) -> list[int]:
        return [int(_LO_COLOR[c] + t * (_HI_COLOR[c] - _LO_COLOR[c])) for c in range(4)]

    colors: list[list[int]] = [_NULL_COLOR] * len(df)

    if metric_col in _GATE_COLS:
        for i, v in enumerate(df[metric_col]):
            if pd.notna(v):
                colors[i] = _GATE_PASS_COLOR if int(v) == 1 else _GATE_FAIL_COLOR
    else:
        valid_mask = pd.notna(df[metric_col])
        if valid_mask.any():
            pcts = df.loc[valid_mask, metric_col].rank(pct=True)
            if metric_col in _INVERTED_COLS:
                pcts = 1.0 - pcts
            for i, t in pcts.items():
                colors[i] = _lerp(t)

    df["fill_color"] = colors
    return df


def build_tract_layer(df: pd.DataFrame, pickable: bool = True) -> pdk.Layer:
    """Builds a PyDeck PolygonLayer for census tracts colored by fill_color."""
    df = add_polygon_coords(df)
    df = df[df["polygon_coords"].notna()].copy()
    return pdk.Layer(
        "PolygonLayer",
        df,
        id="tracts",
        get_polygon="polygon_coords",
        get_fill_color="fill_color",
        get_line_color=[100, 100, 100, 100],
        line_width_min_pixels=0.5,
        pickable=pickable,
        auto_highlight=True,
        opacity=1.0,
    )


def build_zone_layer(df: pd.DataFrame, pickable: bool = True) -> pdk.Layer:
    """Builds a PyDeck PolygonLayer for zone boundaries (outline only)."""
    df = add_polygon_coords(df)
    df = df[df["polygon_coords"].notna()].copy()
    return pdk.Layer(
        "PolygonLayer",
        df,
        id="zones",
        get_polygon="polygon_coords",
        get_fill_color=[0, 0, 0, 0],
        get_line_color=[220, 80, 0, 230],
        line_width_min_pixels=2,
        pickable=pickable,
        stroked=True,
        filled=False,
    )


def build_label_layer(df: pd.DataFrame) -> pdk.Layer:
    """Builds a PyDeck TextLayer for zone labels at centroid positions."""
    df = df[df["label_lat"].notna() & df["label_lon"].notna()].copy()
    return pdk.Layer(
        "TextLayer",
        df,
        id="zone_labels",
        get_position=["label_lon", "label_lat"],
        get_text="zone_label",
        get_size=14,
        get_color=[30, 30, 30, 255],
        pickable=False,
    )


def build_tooltip(layer_type: str) -> dict:
    """Returns a PyDeck tooltip config dict for 'tract' or 'zone' layer types."""
    if layer_type == "tract":
        return {
            "html": (
                "<b>Tract {tract_geoid}</b><br/>"
                "Population: {pop_total}<br/>"
                "Pop Growth 3yr: {pop_growth_3yr}<br/>"
                "Median HH Income: {median_hh_income}<br/>"
                "Tract Score: {tract_score}<br/>"
                "<hr style='margin:4px 0'/>"
                "Gates &mdash; "
                "Pop: {gate_pop} &nbsp;"
                "Price: {gate_price} &nbsp;"
                "Density: {gate_density} &nbsp;"
                "&rarr; Eligible: {eligible_v1}"
            ),
            "style": {"backgroundColor": "white", "color": "#333", "padding": "8px"},
        }
    if layer_type == "zone":
        return {
            "html": (
                "<b>{zone_label}</b><br/>"
                "Tracts: {tracts}<br/>"
                "Population: {total_population}<br/>"
                "Pop Growth 3yr: {pop_growth_3yr_wtd}<br/>"
                "Mean Tract Score: {mean_tract_score}"
            ),
            "style": {"backgroundColor": "white", "color": "#333", "padding": "8px"},
        }
    return {}
