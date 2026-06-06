"""Build the Stoop neighborhood character mart."""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd

from nyc_property_finder.pipelines.build_tract_to_nta import (
    EQUIVALENCY_COLUMN_ALIASES,
    _find_column,
    load_shapefile,
    read_tract_to_nta_equivalency,
)
from nyc_property_finder.services.config import PROJECT_ROOT, load_config
from nyc_property_finder.services.duckdb_service import DuckDBService
from nyc_property_finder.utils.geo import points_from_lon_lat, spatial_join_points_to_polygons


DEFAULT_TRACT_PATH = PROJECT_ROOT / "data" / "raw" / "geography" / "census_tracts.geojson"
DEFAULT_EQUIVALENCY_PATH = PROJECT_ROOT / "data" / "raw" / "geography" / "tract_to_nta_equivalency.csv"
DEFAULT_NTA_PATH = PROJECT_ROOT / "data" / "raw" / "boundaries" / "nta_2020.geojson"

SQL_DDL = PROJECT_ROOT / "sql" / "ddl" / "004_neighborhood_character_mart.sql"
SQL_BUILD_ORDER = [
    PROJECT_ROOT / "sql" / "marts" / "neighborhood_character" / "nta_curated_poi_counts.sql",
    PROJECT_ROOT / "sql" / "marts" / "neighborhood_character" / "nta_public_poi_counts.sql",
    PROJECT_ROOT / "sql" / "marts" / "neighborhood_character" / "nta_category_controls.sql",
    PROJECT_ROOT / "sql" / "marts" / "neighborhood_character" / "nta_category_density.sql",
    PROJECT_ROOT / "sql" / "marts" / "neighborhood_character" / "nta_character_profile.sql",
]

SUMMARY_QUERIES = {
    "table_row_counts": """
        select 'nta_boundaries' as table_name, count(*) as row_count
        from neighborhood_character_mart.nta_boundaries
        union all
        select 'nta_poi_assignments' as table_name, count(*) as row_count
        from neighborhood_character_mart.nta_poi_assignments
        order by table_name
    """,
    "category_threshold_summary": """
        select
            source,
            category,
            max(nyc_category_total) as nyc_category_total,
            bool_or(meets_evidence_threshold) as any_rows_meet_threshold
        from neighborhood_character_mart.nta_category_density
        group by source, category
        order by source, category
    """,
}


def _default_database_path() -> Path:
    settings = load_config()["settings"]
    return PROJECT_ROOT / settings["database_path"]


def _normalize_tract_id(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(11)


def _load_tract_geometries(path: str | Path) -> gpd.GeoDataFrame:
    tracts = load_shapefile(path).to_crs("EPSG:4326")
    tract_id_col = _find_column(tracts, EQUIVALENCY_COLUMN_ALIASES["tract_id"])
    if tract_id_col is None:
        raise ValueError("Unable to find tract id column in tract geometry file.")
    tracts = tracts.rename(columns={tract_id_col: "tract_id"})
    tracts["tract_id"] = _normalize_tract_id(tracts["tract_id"])
    return tracts


def _combine_boroughs(values: pd.Series) -> str | None:
    unique = sorted({str(value).strip() for value in values if pd.notna(value) and str(value).strip()})
    if not unique:
        return None
    return " / ".join(unique)


def _nta_boundaries_from_tracts(
    tract_path: str | Path,
    equivalency_path: str | Path,
) -> gpd.GeoDataFrame:
    tracts = _load_tract_geometries(tract_path)
    mapping = read_tract_to_nta_equivalency(equivalency_path)
    merged = tracts.merge(mapping[["tract_id", "nta_id", "nta_name", "borough"]], on="tract_id", how="left")
    merged = merged[merged["nta_id"].notna() & (merged["nta_id"].astype(str).str.strip() != "")]
    dissolved = (
        merged[["nta_id", "nta_name", "borough", "geometry"]]
        .dissolve(
            by="nta_id",
            aggfunc={
                "nta_name": "first",
                "borough": _combine_boroughs,
            },
        )
        .reset_index()
    )
    return dissolved


def _load_nta_boundaries(
    tract_path: str | Path,
    equivalency_path: str | Path,
    nta_path: str | Path | None = None,
) -> gpd.GeoDataFrame:
    if nta_path is not None and Path(nta_path).exists():
        ntas = load_shapefile(nta_path).to_crs("EPSG:4326")
        nta_id_col = _find_column(ntas, EQUIVALENCY_COLUMN_ALIASES["nta_id"])
        nta_name_col = _find_column(ntas, EQUIVALENCY_COLUMN_ALIASES["nta_name"])
        borough_col = _find_column(ntas, EQUIVALENCY_COLUMN_ALIASES["borough"])
        if nta_id_col is None or nta_name_col is None:
            raise ValueError("NTA geometry file must include identifiable nta_id and nta_name columns.")
        rename_map = {nta_id_col: "nta_id", nta_name_col: "nta_name"}
        if borough_col is not None:
            rename_map[borough_col] = "borough"
        ntas = ntas.rename(columns=rename_map)
        if "borough" not in ntas.columns:
            ntas["borough"] = pd.NA
        return ntas[["nta_id", "nta_name", "borough", "geometry"]]
    return _nta_boundaries_from_tracts(tract_path=tract_path, equivalency_path=equivalency_path)


def build_nta_boundaries(
    tract_path: str | Path,
    equivalency_path: str | Path,
    nta_path: str | Path | None = None,
) -> gpd.GeoDataFrame:
    ntas = _load_nta_boundaries(tract_path=tract_path, equivalency_path=equivalency_path, nta_path=nta_path).copy()
    projected = ntas.to_crs("EPSG:2263")
    ntas["area_sqkm"] = projected.geometry.area * 0.09290304 / 1_000_000
    centroids = projected.geometry.centroid.to_crs("EPSG:4326")
    ntas["centroid_lat"] = centroids.y
    ntas["centroid_lon"] = centroids.x
    ntas["geometry_wkt"] = ntas.geometry.to_wkt()
    return ntas[["nta_id", "nta_name", "borough", "area_sqkm", "centroid_lat", "centroid_lon", "geometry", "geometry_wkt"]]


def _read_curated_poi(duckdb_service: DuckDBService) -> pd.DataFrame:
    curated_table = "property_explorer_gold.dim_user_poi_v3"
    table_count = duckdb_service.query_df(
        """
        select count(*) as table_count
        from information_schema.tables
        where table_schema = 'property_explorer_gold'
          and table_name = 'dim_user_poi_v3'
        """
    )["table_count"].iloc[0]
    row_count = 0
    if int(table_count) > 0:
        row_count = int(
            duckdb_service.query_df(
                "select count(*) as row_count from property_explorer_gold.dim_user_poi_v3"
            )["row_count"].iloc[0]
        )
    if int(table_count) == 0 or row_count == 0:
        curated_table = "property_explorer_gold.dim_user_poi_v2"

    return duckdb_service.query_df(
        f"""
        select
            poi_id,
            coalesce(nullif(primary_category, ''), nullif(category, '')) as category,
            coalesce(nullif(primary_subcategory, ''), nullif(subcategory, '')) as subcategory,
            lat,
            lon
        from {curated_table}
        """
    )


def _read_public_poi(duckdb_service: DuckDBService) -> pd.DataFrame:
    return duckdb_service.query_df(
        """
        select
            poi_id,
            category,
            subcategory,
            lat,
            lon
        from property_explorer_gold.dim_public_poi
        """
    )


def assign_poi_to_ntas(
    poi: pd.DataFrame,
    nta_boundaries: gpd.GeoDataFrame,
    poi_source: str,
) -> pd.DataFrame:
    if poi.empty:
        return pd.DataFrame(columns=["poi_id", "poi_source", "nta_id", "category", "subcategory", "lat", "lon"])

    valid = poi.copy()
    valid = valid[valid["lat"].notna() & valid["lon"].notna()]
    if valid.empty:
        return pd.DataFrame(columns=["poi_id", "poi_source", "nta_id", "category", "subcategory", "lat", "lon"])

    points = points_from_lon_lat(valid)
    joined = spatial_join_points_to_polygons(
        points=points,
        polygons=nta_boundaries[["nta_id", "geometry"]],
        point_columns=["poi_id", "category", "subcategory", "lat", "lon"],
        polygon_columns=["nta_id"],
    )
    joined["poi_source"] = poi_source
    output = joined[["poi_id", "poi_source", "nta_id", "category", "subcategory", "lat", "lon"]].copy()
    output = output[output["nta_id"].notna()].reset_index(drop=True)
    return output


def _write_nta_boundaries(nta_boundaries: gpd.GeoDataFrame, duckdb_service: DuckDBService) -> None:
    output = nta_boundaries.drop(columns="geometry").copy()
    duckdb_service.write_dataframe(output, table_name="nta_boundaries", schema="neighborhood_character_mart", if_exists="replace")


def _write_assignments(assignments: pd.DataFrame, duckdb_service: DuckDBService) -> None:
    duckdb_service.write_dataframe(
        assignments,
        table_name="nta_poi_assignments",
        schema="neighborhood_character_mart",
        if_exists="replace",
    )


def _print_summary(duckdb_service: DuckDBService) -> None:
    for title, query in SUMMARY_QUERIES.items():
        rows = duckdb_service.query_df(query)
        print(f"\n[{title}]")
        if rows.empty:
            print("(no rows)")
        else:
            print(rows.to_string(index=False))


def run(
    database_path: str | Path | None = None,
    tract_path: str | Path = DEFAULT_TRACT_PATH,
    equivalency_path: str | Path = DEFAULT_EQUIVALENCY_PATH,
    nta_path: str | Path | None = DEFAULT_NTA_PATH,
) -> None:
    resolved_database_path = Path(database_path) if database_path is not None else _default_database_path()
    with DuckDBService(resolved_database_path) as duckdb_service:
        duckdb_service.execute(SQL_DDL.read_text(encoding="utf-8"))

        nta_boundaries = build_nta_boundaries(
            tract_path=tract_path,
            equivalency_path=equivalency_path,
            nta_path=nta_path,
        )
        _write_nta_boundaries(nta_boundaries, duckdb_service)

        curated_assignments = assign_poi_to_ntas(_read_curated_poi(duckdb_service), nta_boundaries, "curated")
        public_assignments = assign_poi_to_ntas(_read_public_poi(duckdb_service), nta_boundaries, "public")
        assignments = pd.concat([curated_assignments, public_assignments], ignore_index=True)
        _write_assignments(assignments, duckdb_service)

        for sql_path in SQL_BUILD_ORDER:
            duckdb_service.execute(sql_path.read_text(encoding="utf-8"))
            print(f"Executed: {sql_path.relative_to(PROJECT_ROOT)}")

        _print_summary(duckdb_service)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Stoop neighborhood character mart.")
    parser.add_argument("--database", type=Path, default=None, help="Optional DuckDB path.")
    parser.add_argument(
        "--tract-path",
        type=Path,
        default=DEFAULT_TRACT_PATH,
        help="Path to tract geometry GeoJSON.",
    )
    parser.add_argument(
        "--equivalency-path",
        type=Path,
        default=DEFAULT_EQUIVALENCY_PATH,
        help="Path to tract-to-NTA equivalency CSV.",
    )
    parser.add_argument(
        "--nta-path",
        type=Path,
        default=DEFAULT_NTA_PATH,
        help="Optional path to NTA boundary GeoJSON.",
    )
    args = parser.parse_args()
    run(
        database_path=args.database,
        tract_path=args.tract_path,
        equivalency_path=args.equivalency_path,
        nta_path=args.nta_path,
    )


if __name__ == "__main__":
    main()
