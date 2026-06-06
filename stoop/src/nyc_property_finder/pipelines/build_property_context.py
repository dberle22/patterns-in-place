"""Build property context and scoring table."""

from __future__ import annotations

import json
import re
from argparse import ArgumentParser
from pathlib import Path

import geopandas as gpd
import pandas as pd

from nyc_property_finder.services.config import PROJECT_ROOT, load_config
from nyc_property_finder.services.duckdb_service import DuckDBService
from nyc_property_finder.transforms.scoring import (
    is_missing,
    mobility_score,
    neighborhood_score,
    neighborhood_score_status,
    personal_fit_score,
    property_fit_score,
    property_fit_score_status,
)
from nyc_property_finder.utils.geo import (
    count_points_within_radius,
    nearest_neighbor,
    points_from_lon_lat,
    spatial_join_points_to_polygons,
)


PROPERTY_CONTEXT_COLUMNS = [
    "property_id",
    "source",
    "source_listing_id",
    "address",
    "lat",
    "lon",
    "price",
    "beds",
    "baths",
    "listing_type",
    "active",
    "url",
    "ingest_timestamp",
    "tract_id",
    "nta_id",
    "nta_name",
    "nearest_subway_stop",
    "nearest_subway_distance_miles",
    "subway_lines_count",
    "poi_data_available",
    "poi_count_nearby",
    "poi_count_10min",
    "poi_category_counts",
    "neighborhood_score",
    "neighborhood_score_status",
    "mobility_score",
    "personal_fit_score",
    "personal_fit_score_status",
    "property_fit_score",
    "property_fit_score_status",
]

NEIGHBORHOOD_FEATURE_COLUMNS = [
    "median_income",
    "median_rent",
    "median_home_value",
    "pct_bachelors_plus",
    "median_age",
]


def attach_geography(
    properties: pd.DataFrame,
    tracts,
    tract_id_col: str = "tract_id",
    nta_id_col: str = "nta_id",
) -> pd.DataFrame:
    """Join property points to tract and NTA attributes."""

    if properties.empty:
        output = properties.copy()
        output[tract_id_col] = pd.Series(dtype="object")
        output[nta_id_col] = pd.Series(dtype="object")
        output["nta_name"] = pd.Series(dtype="object")
        return output

    property_points = points_from_lon_lat(properties)
    polygon_columns = [tract_id_col, nta_id_col]
    if "nta_name" in tracts.columns:
        polygon_columns.append("nta_name")
    joined = spatial_join_points_to_polygons(
        points=property_points,
        polygons=tracts,
        point_columns=[column for column in properties.columns if column != "geometry"],
        polygon_columns=polygon_columns,
    )
    return pd.DataFrame(joined.drop(columns="geometry"))


def count_subway_lines(lines: object) -> int:
    """Count unique subway lines from common delimiter formats."""

    if is_missing(lines):
        return 0
    tokens = [token.strip() for token in re.split(r"[\s,;/|]+", str(lines)) if token.strip()]
    return len(set(tokens))


def add_transit_context(properties: pd.DataFrame, subway_stops: pd.DataFrame | None) -> pd.DataFrame:
    """Compute nearest subway stop and simple line-count context."""

    if subway_stops is None or subway_stops.empty or properties.empty:
        output = properties.copy()
        output["nearest_subway_stop"] = pd.NA
        output["nearest_subway_distance_miles"] = pd.NA
        output["subway_lines_count"] = 0
        return output

    property_points = points_from_lon_lat(properties)
    subway_points = points_from_lon_lat(subway_stops)
    nearest = nearest_neighbor(
        origins=property_points,
        destinations=subway_points,
        origin_id_col="property_id",
        destination_id_col="subway_stop_id",
        destination_name_col="stop_name",
    )
    nearest = nearest.rename(
        columns={
            "stop_name": "nearest_subway_stop",
            "distance_miles": "nearest_subway_distance_miles",
        }
    )
    line_counts = subway_stops[["subway_stop_id", "lines"]].copy()
    line_counts["subway_lines_count"] = line_counts["lines"].apply(count_subway_lines)
    nearest = nearest.merge(line_counts[["subway_stop_id", "subway_lines_count"]], on="subway_stop_id", how="left")
    return properties.merge(nearest, on="property_id", how="left")


def add_poi_context(properties: pd.DataFrame, poi: pd.DataFrame | None, radius_miles: float = 0.5) -> pd.DataFrame:
    """Count nearby user POIs."""

    if poi is None or poi.empty or properties.empty:
        output = properties.copy()
        output["poi_data_available"] = False
        output["poi_count_nearby"] = 0
        output["poi_count_10min"] = 0
        output["poi_category_counts"] = [{} for _ in range(len(output))]
        return output

    property_points = points_from_lon_lat(properties)
    poi_points = points_from_lon_lat(poi)
    counts = count_points_within_radius(
        origins=property_points,
        points=poi_points,
        origin_id_col="property_id",
        point_category_col="category",
        radius_miles=radius_miles,
    ).rename(columns={"poi_count": "poi_count_nearby"})
    counts["poi_count_10min"] = counts["poi_count_nearby"]
    counts["poi_data_available"] = True
    return properties.merge(counts, on="property_id", how="left")


def _merge_neighborhood_features(
    properties: pd.DataFrame,
    tract_features: pd.DataFrame | None = None,
    nta_features: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Attach tract features and use NTA features as a same-field fallback."""

    output = properties.copy()
    if tract_features is not None and not tract_features.empty and "tract_id" in output.columns:
        tract_cols = ["tract_id", *[col for col in NEIGHBORHOOD_FEATURE_COLUMNS if col in tract_features.columns]]
        output = output.merge(tract_features[tract_cols].drop_duplicates("tract_id"), on="tract_id", how="left")

    if nta_features is not None and not nta_features.empty and "nta_id" in output.columns:
        available_cols = [col for col in NEIGHBORHOOD_FEATURE_COLUMNS if col in nta_features.columns]
        nta_cols = ["nta_id", *available_cols]
        renamed = nta_features[nta_cols].drop_duplicates("nta_id").rename(
            columns={column: f"nta_{column}" for column in available_cols}
        )
        output = output.merge(renamed, on="nta_id", how="left")
        for column in available_cols:
            nta_column = f"nta_{column}"
            if column not in output.columns:
                output[column] = output[nta_column]
            else:
                output[column] = output[column].combine_first(output[nta_column])

    return output


def add_scores(
    properties: pd.DataFrame,
    tract_features: pd.DataFrame | None = None,
    nta_features: pd.DataFrame | None = None,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Add component and total property scores."""

    output = _merge_neighborhood_features(properties, tract_features, nta_features)
    if "poi_data_available" not in output.columns:
        output["poi_data_available"] = False
    if "poi_count_nearby" not in output.columns:
        output["poi_count_nearby"] = 0
    if "poi_category_counts" not in output.columns:
        output["poi_category_counts"] = [{} for _ in range(len(output))]

    output["neighborhood_score"] = output.apply(neighborhood_score, axis=1)
    output["neighborhood_score_status"] = output.apply(neighborhood_score_status, axis=1)
    output["mobility_score"] = output.apply(
        lambda row: mobility_score(row.get("nearest_subway_distance_miles"), row.get("subway_lines_count")),
        axis=1,
    )
    output["personal_fit_score"] = output.apply(
        lambda row: personal_fit_score(
            row.get("poi_count_nearby"),
            len(row.get("poi_category_counts") or {}),
            bool(row.get("poi_data_available")),
        ),
        axis=1,
    )
    output["personal_fit_score_status"] = output["poi_data_available"].apply(
        lambda available: "scored" if bool(available) else "unavailable"
    )
    output["property_fit_score"] = output.apply(
        lambda row: property_fit_score(
            row["neighborhood_score"],
            row["mobility_score"],
            row["personal_fit_score"],
            weights=weights,
        ),
        axis=1,
    )
    output["property_fit_score_status"] = output.apply(
        lambda row: property_fit_score_status(
            row["neighborhood_score"],
            row["mobility_score"],
            row["personal_fit_score"],
        ),
        axis=1,
    )
    return output


def build_property_context(
    properties: pd.DataFrame,
    tracts,
    subway_stops: pd.DataFrame | None = None,
    poi: pd.DataFrame | None = None,
    tract_features: pd.DataFrame | None = None,
    nta_features: pd.DataFrame | None = None,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Build the property context fact table."""

    with_geography = attach_geography(properties, tracts)
    with_transit = add_transit_context(with_geography, subway_stops)
    with_poi = add_poi_context(with_transit, poi)
    return add_scores(with_poi, tract_features=tract_features, nta_features=nta_features, weights=weights)


def prepare_property_context_for_duckdb(context: pd.DataFrame) -> pd.DataFrame:
    """Coerce context output to the persisted DuckDB table shape."""

    output = context.copy()
    if "poi_category_counts" in output.columns:
        output["poi_category_counts"] = output["poi_category_counts"].apply(_jsonify_category_counts)

    for column in PROPERTY_CONTEXT_COLUMNS:
        if column not in output.columns:
            output[column] = pd.NA

    return output[PROPERTY_CONTEXT_COLUMNS]


def _jsonify_category_counts(value: object) -> str:
    """Serialize category-count values as stable JSON object text."""

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return json.dumps({}, sort_keys=True)
        return json.dumps(parsed or {}, sort_keys=True)
    if is_missing(value):
        return json.dumps({}, sort_keys=True)
    return json.dumps(value or {}, sort_keys=True)


def write_property_context(
    context: pd.DataFrame,
    duckdb_service: DuckDBService,
    table_name: str = "fct_property_context",
    schema: str = "property_explorer_gold",
) -> None:
    """Persist the property context fact table."""

    duckdb_service.write_dataframe(
        prepare_property_context_for_duckdb(context),
        table_name=table_name,
        schema=schema,
        if_exists="replace",
    )


def _read_table_or_empty(duckdb_service: DuckDBService, table_name: str) -> pd.DataFrame:
    """Read a DuckDB table, returning an empty dataframe if it does not exist."""

    try:
        return duckdb_service.query_df(f"SELECT * FROM {table_name}")
    except Exception:
        return pd.DataFrame()


def load_context_inputs(database_path: str | Path) -> dict[str, pd.DataFrame]:
    """Load persisted inputs needed to build property context."""

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        return {
            "properties": _read_table_or_empty(
                duckdb_service,
                "property_explorer_gold.dim_property_listing",
            ),
            "mapping": _read_table_or_empty(
                duckdb_service,
                "property_explorer_gold.dim_tract_to_nta",
            ),
            "subway_stops": _read_table_or_empty(
                duckdb_service,
                "property_explorer_gold.dim_subway_stop",
            ),
            "poi": _read_table_or_empty(
                duckdb_service,
                "property_explorer_gold.dim_user_poi",
            ),
            "tract_features": _read_table_or_empty(
                duckdb_service,
                "property_explorer_gold.fct_tract_features",
            ),
            "nta_features": _read_table_or_empty(
                duckdb_service,
                "property_explorer_gold.fct_nta_features",
            ),
        }


def load_tract_geometries(
    tract_path: str | Path,
    mapping: pd.DataFrame,
    tract_id_col: str = "tract_id",
) -> gpd.GeoDataFrame:
    """Load tract polygons and attach NTA mapping attributes."""

    tracts = gpd.read_file(tract_path)
    if tract_id_col not in tracts.columns:
        raise ValueError(f"Missing tract id column in tract geometry file: {tract_id_col}")

    tracts = tracts.rename(columns={tract_id_col: "tract_id"})
    if not mapping.empty and {"tract_id", "nta_id"}.issubset(mapping.columns):
        mapping_cols = [column for column in ["tract_id", "nta_id", "nta_name"] if column in mapping.columns]
        tracts = tracts.merge(mapping[mapping_cols].drop_duplicates("tract_id"), on="tract_id", how="left")
    elif "nta_id" not in tracts.columns:
        tracts["nta_id"] = pd.NA
    if "nta_name" not in tracts.columns:
        tracts["nta_name"] = pd.NA
    return tracts


def build_context_quality_summary(context: pd.DataFrame) -> dict[str, object]:
    """Return high-signal QA metrics for the persisted context table."""

    row_count = int(len(context))
    active = context["active"].fillna(False).astype(bool) if "active" in context.columns else pd.Series(dtype=bool)
    assigned = context["tract_id"].notna() if "tract_id" in context.columns else pd.Series(dtype=bool)
    subway_distances = (
        pd.to_numeric(context["nearest_subway_distance_miles"], errors="coerce")
        if "nearest_subway_distance_miles" in context.columns
        else pd.Series(dtype=float)
    )
    score_columns = ["neighborhood_score", "mobility_score", "personal_fit_score", "property_fit_score"]
    invalid_score_counts = {}
    for column in score_columns:
        scores = pd.to_numeric(context[column], errors="coerce") if column in context.columns else pd.Series(dtype=float)
        invalid_score_counts[column] = int(((scores < 0) | (scores > 100)).sum())

    return {
        "row_count": row_count,
        "active_row_count": int(active.sum()) if not active.empty else 0,
        "tract_assigned_count": int(assigned.sum()) if not assigned.empty else 0,
        "tract_assignment_rate": float(assigned.mean()) if row_count else None,
        "missing_nta_name_count": int(context["nta_name"].isna().sum()) if "nta_name" in context.columns else None,
        "subway_distance_missing_count": int(subway_distances.isna().sum()) if row_count else 0,
        "subway_distance_over_2_miles_count": int((subway_distances > 2).sum()) if row_count else 0,
        "invalid_score_counts": invalid_score_counts,
    }


def run(
    database_path: str | Path | None = None,
    tract_path: str | Path | None = None,
    tract_id_col: str = "tract_id",
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Build and persist property context from DuckDB inputs and tract geometries."""

    if database_path is None or tract_path is None:
        config = load_config()
        if database_path is None:
            database_path = PROJECT_ROOT / config["settings"]["database_path"]
        if tract_path is None:
            tract_source = config["data_sources"]["sources"]["census_tracts"]
            tract_path = PROJECT_ROOT / tract_source["path"]
            tract_id_col = tract_source.get("id_column", tract_id_col)

    inputs = load_context_inputs(database_path)
    tracts = load_tract_geometries(
        tract_path=tract_path,
        mapping=inputs["mapping"],
        tract_id_col=tract_id_col,
    )
    context = build_property_context(
        properties=inputs["properties"],
        tracts=tracts,
        subway_stops=inputs["subway_stops"],
        poi=inputs["poi"],
        tract_features=inputs["tract_features"],
        nta_features=inputs["nta_features"],
        weights=weights,
    )

    with DuckDBService(database_path) as duckdb_service:
        write_property_context(context, duckdb_service)
    return prepare_property_context_for_duckdb(context)


def main() -> None:
    """CLI entry point for the Sprint 3 context build."""

    parser = ArgumentParser(description="Build property_explorer_gold.fct_property_context")
    parser.add_argument("--database-path", default=None)
    parser.add_argument("--tract-path", default=None)
    parser.add_argument("--tract-id-col", default="tract_id")
    args = parser.parse_args()

    context = run(
        database_path=args.database_path,
        tract_path=args.tract_path,
        tract_id_col=args.tract_id_col,
    )
    summary = build_context_quality_summary(context)
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
