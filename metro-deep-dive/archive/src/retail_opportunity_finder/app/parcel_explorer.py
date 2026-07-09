"""Retail Parcel Explorer helper functions: data loading, filters, layers, and upsert."""

from __future__ import annotations

import pandas as pd
import pydeck as pdk

from retail_opportunity_finder.utils.geo import add_polygon_coords

SORT_OPTIONS = [
    "Best opportunity",
    "Strongest zone",
    "Best parcel characteristics",
    "Best retail context",
    "Largest site",
    "Newest sale",
    "Lowest assessed value",
]

SHORTLIST_STATUSES = ["active", "needs_review", "watchlist", "rejected"]

_SORT_MAP: dict[str, tuple[str, bool]] = {
    "Best opportunity":            ("shortlist_score", False),
    "Strongest zone":              ("zone_quality_score", False),
    "Best parcel characteristics": ("parcel_characteristics_score", False),
    "Best retail context":         ("local_retail_context_score", False),
    "Largest site":                ("parcel_area_sqmi", False),
    "Newest sale":                 ("last_sale_date", False),
    "Lowest assessed value":       ("just_value", True),
}

# Score ramp: light yellow (low) → steel blue (high)
_SCORE_LO = [255, 237, 160, 200]
_SCORE_HI = [44, 123, 182, 220]
_NULL_COLOR = [160, 160, 160, 100]

# One color per retail subtype — qualitatively distinct palette
SUBTYPE_COLORS: dict[str, list[int]] = {
    "commercial_vacant":           [70,  130, 180, 220],  # steel blue
    "store_single_story":          [255, 140,   0, 220],  # dark orange
    "auto_sales_service":          [205,  92,  92, 220],  # indian red
    "community_shopping_center":   [46,  139,  87, 220],  # sea green
    "parking_lot":                 [140, 140, 140, 180],  # gray
    "restaurant":                  [147, 112, 219, 220],  # medium purple
    "mixed_use":                   [0,   206, 209, 220],  # dark turquoise
    "drive_in_restaurant":         [218, 165,  32, 220],  # goldenrod
    "supermarket":                 [255,  99,  71, 220],  # tomato
    "service_station":             [60,  179, 113, 220],  # medium sea green
    "department_store":            [199,  21, 133, 220],  # medium violet red
    "regional_shopping_center":    [178,  34,  34, 220],  # firebrick
    "hotel_motel":                 [100, 149, 237, 220],  # cornflower blue
}
_DEFAULT_SUBTYPE_COLOR: list[int] = [180, 180, 180, 180]


def _subtype_color(subtype: str) -> list[int]:
    return SUBTYPE_COLORS.get(subtype, _DEFAULT_SUBTYPE_COLOR)


def load_shortlist(con, market_key: str, zone_system: str) -> pd.DataFrame:
    """
    Returns parcel shortlist joined to geometry, retail_parcels (land/impro value),
    and parcel_zone_overlay (zone context).
    Geometry join: parcel_id → join_key (NOT parcel_uid).
    """
    return con.execute(
        """
        SELECT
            ps.parcel_uid,
            ps.parcel_id,
            ps.zone_id,
            ps.zone_label,
            ps.county_name,
            ps.county_geoid,
            ps.tract_geoid,
            ps.retail_subtype,
            ps.land_use_code,
            ps.site_addr,
            ps.owner_name,
            ps.parcel_area_sqmi,
            ps.just_value,
            ps.last_sale_date,
            ps.last_sale_price,
            ps.shortlist_score,
            ps.shortlist_rank_system,
            ps.shortlist_rank_zone,
            ps.zone_quality_score,
            ps.parcel_characteristics_score,
            ps.local_retail_context_score,
            ps.mean_tract_score,
            rp.land_value,
            rp.impro_value,
            pg.geom_wkt,
            pg.centroid_lat,
            pg.centroid_lon,
            pzo.tracts           AS zone_tracts,
            pzo.total_population AS zone_population,
            pzo.mean_tract_score AS zone_mean_tract_score
        FROM rof_gold.parcel_shortlist ps
        LEFT JOIN rof_gold.retail_parcels rp
            ON ps.parcel_uid = rp.parcel_uid
        LEFT JOIN rof_gold.parcel_geometry pg
            ON ps.parcel_id = pg.join_key
        LEFT JOIN rof_gold.parcel_zone_overlay pzo
            ON ps.market_key = pzo.market_key
            AND ps.zone_system = pzo.zone_system
            AND ps.zone_id = pzo.zone_id
        WHERE ps.market_key = ? AND ps.zone_system = ?
        """,
        [market_key, zone_system],
    ).df()


def load_out_of_shortlist(con, market_key: str, zone_system: str) -> pd.DataFrame:
    """Returns retail parcels (centroid only) NOT in the shortlist for this zone system."""
    return con.execute(
        """
        SELECT
            rp.parcel_uid,
            rp.retail_subtype,
            rp.site_addr,
            rp.county_name,
            rp.just_value,
            pg.centroid_lat,
            pg.centroid_lon
        FROM rof_gold.retail_parcels rp
        JOIN rof_gold.parcel_geometry pg ON rp.join_key = pg.join_key
        WHERE rp.market_key = ?
          AND pg.centroid_lat IS NOT NULL
          AND rp.parcel_uid NOT IN (
              SELECT parcel_uid FROM rof_gold.parcel_shortlist
              WHERE market_key = ? AND zone_system = ?
          )
        """,
        [market_key, market_key, zone_system],
    ).df()


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Applies sidebar filter selections to the parcel DataFrame."""
    if filters.get("counties"):
        df = df[df["county_name"].isin(filters["counties"])]
    if filters.get("zone_ids"):
        df = df[df["zone_id"].isin(filters["zone_ids"])]
    if filters.get("subtypes"):
        df = df[df["retail_subtype"].isin(filters["subtypes"])]

    val_min, val_max = filters.get("val_range", (None, None))
    if val_min is not None:
        df = df[df["just_value"].fillna(0) >= val_min]
    if val_max is not None:
        df = df[df["just_value"].fillna(0) <= val_max]

    area_min, area_max = filters.get("area_range", (None, None))
    if area_min is not None:
        df = df[df["parcel_area_sqmi"].fillna(0) >= area_min]
    if area_max is not None:
        df = df[df["parcel_area_sqmi"].fillna(0) <= area_max]

    for col, key in [
        ("shortlist_score", "min_shortlist_score"),
        ("zone_quality_score", "min_zone_quality_score"),
        ("parcel_characteristics_score", "min_parcel_chars_score"),
    ]:
        threshold = filters.get(key)
        if threshold is not None and threshold > 0:
            df = df[df[col].fillna(0) >= threshold]

    status = filters.get("status_filter", "All")
    if status == "Unreviewed":
        df = df[df["user_status"].isna()]
    elif status != "All":
        df = df[df["user_status"] == status.lower().replace(" ", "_")]

    return df.reset_index(drop=True)


def apply_sort(df: pd.DataFrame, sort_key: str) -> pd.DataFrame:
    """Sorts the parcel DataFrame by the selected sort option."""
    col, ascending = _SORT_MAP.get(sort_key, ("shortlist_score", False))
    if col not in df.columns:
        return df.reset_index(drop=True)
    return df.sort_values(col, ascending=ascending, na_position="last").reset_index(drop=True)


def score_status(value) -> str:
    """Returns 'scored', 'partial', or 'unavailable' for a score value."""
    if pd.isna(value):
        return "unavailable"
    if float(value) <= 0:
        return "partial"
    return "scored"


def build_parcel_layer(df: pd.DataFrame, color_by: str = "subtype") -> pdk.Layer:
    """
    Builds a PolygonLayer for shortlisted parcel footprints.
    color_by='subtype' uses retail subtype colors; color_by='score' uses shortlist_score ramp.
    """
    df = add_polygon_coords(df)
    df = df[df["polygon_coords"].notna()].copy().reset_index(drop=True)

    if color_by == "subtype":
        df["fill_color"] = df["retail_subtype"].apply(_subtype_color)
    else:
        colors: list[list[int]] = [_NULL_COLOR] * len(df)
        valid = df["shortlist_score"].notna()
        if valid.any():
            pcts = df.loc[valid, "shortlist_score"].rank(pct=True)
            for i, t in pcts.items():
                colors[i] = [int(_SCORE_LO[c] + t * (_SCORE_HI[c] - _SCORE_LO[c])) for c in range(4)]
        df["fill_color"] = colors

    return pdk.Layer(
        "PolygonLayer",
        df,
        id="parcels",
        get_polygon="polygon_coords",
        get_fill_color="fill_color",
        get_line_color=[60, 60, 60, 100],
        line_width_min_pixels=0.5,
        pickable=True,
        auto_highlight=True,
        opacity=0.9,
    )


def build_parcel_scatter_layer(df: pd.DataFrame) -> pdk.Layer:
    """
    Builds a ScatterplotLayer at parcel centroids colored by subtype.
    Visible at overview zoom levels where polygon footprints are sub-pixel.
    """
    df = df[df["centroid_lat"].notna() & df["centroid_lon"].notna()].copy()
    df["fill_color"] = df["retail_subtype"].apply(_subtype_color)
    return pdk.Layer(
        "ScatterplotLayer",
        df,
        id="parcel_dots",
        get_position=["centroid_lon", "centroid_lat"],
        get_fill_color="fill_color",
        get_line_color=[255, 255, 255, 80],
        stroked=True,
        line_width_min_pixels=0.5,
        radius_min_pixels=3,
        radius_max_pixels=10,
        pickable=True,
        auto_highlight=True,
    )


def build_out_of_zone_layer(df: pd.DataFrame, pickable: bool = True) -> pdk.Layer:
    """Builds a muted ScatterplotLayer for retail parcels outside the current zone system."""
    df = df[df["centroid_lat"].notna() & df["centroid_lon"].notna()].copy()
    df["fill_color"] = df["retail_subtype"].apply(
        lambda s: [*_subtype_color(s)[:3], 90]  # same hue, reduced alpha
    )
    return pdk.Layer(
        "ScatterplotLayer",
        df,
        id="out_of_zone",
        get_position=["centroid_lon", "centroid_lat"],
        get_fill_color="fill_color",
        get_line_color=[200, 200, 200, 60],
        stroked=True,
        line_width_min_pixels=0.3,
        radius_min_pixels=2,
        radius_max_pixels=6,
        pickable=pickable,
        auto_highlight=True,
    )


def build_selected_layer(row: pd.Series) -> pdk.Layer | None:
    """Builds a ScatterplotLayer highlighting the selected parcel's centroid."""
    if pd.isna(row.get("centroid_lat")) or pd.isna(row.get("centroid_lon")):
        return None
    return pdk.Layer(
        "ScatterplotLayer",
        [{"lat": row["centroid_lat"], "lon": row["centroid_lon"]}],
        id="selected",
        get_position=["lon", "lat"],
        get_fill_color=[255, 50, 50, 220],
        get_line_color=[255, 255, 255, 255],
        stroked=True,
        line_width_min_pixels=2,
        radius_min_pixels=10,
        radius_max_pixels=30,
        pickable=False,
    )


def upsert_shortlist(
    con, parcel_uid: str, market_key: str, user_id: str, status: str, notes: str
) -> None:
    """Inserts or updates a user_shortlist row."""
    con.execute(
        """
        INSERT INTO rof_gold.user_shortlist
            (parcel_uid, market_key, user_id, status, notes, updated_at)
        VALUES (?, ?, ?, ?, ?, now())
        ON CONFLICT (parcel_uid, market_key, user_id)
        DO UPDATE SET
            status     = excluded.status,
            notes      = excluded.notes,
            updated_at = now()
        """,
        [parcel_uid, market_key, user_id, status, notes],
    )
