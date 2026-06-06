"""Build tract-to-NTA geography mapping."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd

from nyc_property_finder.services.duckdb_service import DuckDBService
from nyc_property_finder.utils.geo import spatial_join_centroids_to_polygons


EQUIVALENCY_COLUMN_ALIASES = {
    "tract_id": ["tract_id", "tract_geoid", "geoid", "geoid_tract", "censustract2020", "tract"],
    "nta_id": ["nta_id", "ntacode", "nta_code", "nta2020", "nta"],
    "nta_name": ["nta_name", "ntaname", "nta_name_2020", "ntaname2020"],
    "borough": ["borough", "boroname", "boro_name", "boroname2020"],
    "cdta_id": ["cdta_id", "cdtacode", "cdta_code", "cdta2020"],
    "cdta_name": ["cdta_name", "cdtaname", "cdta_name_2020", "cdtaname2020"],
}
EQUIVALENCY_COLUMNS = ["tract_id", "nta_id", "nta_name", "borough", "cdta_id", "cdta_name", "geometry_wkt"]


def load_shapefile(path: str | Path) -> gpd.GeoDataFrame:
    """Load a shapefile or any vector file supported by GeoPandas."""

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Geometry file does not exist: {path}")
    return gpd.read_file(path)


def _clean_column_name(column: str) -> str:
    return "".join(character for character in column.lower() if character.isalnum() or character == "_")


def _find_column(dataframe: pd.DataFrame, aliases: list[str]) -> str | None:
    cleaned = {_clean_column_name(column): column for column in dataframe.columns}
    for alias in aliases:
        cleaned_alias = _clean_column_name(alias)
        if cleaned_alias in cleaned:
            return cleaned[cleaned_alias]
    return None


def read_tract_to_nta_equivalency(path: str | Path) -> pd.DataFrame:
    """Read the NYC tract-to-NTA equivalency CSV into the project contract."""

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Tract/NTA equivalency file does not exist: {path}")

    raw = pd.read_csv(path, dtype=str)
    output = pd.DataFrame()
    missing_required: list[str] = []
    for target_column, aliases in EQUIVALENCY_COLUMN_ALIASES.items():
        source_column = _find_column(raw, aliases)
        if source_column is None:
            if target_column in {"tract_id", "nta_id", "nta_name"}:
                missing_required.append(target_column)
            output[target_column] = pd.NA
        else:
            output[target_column] = raw[source_column].fillna("").astype(str).str.strip()

    if missing_required:
        raise ValueError(f"Missing required tract/NTA equivalency columns: {missing_required}")

    output["tract_id"] = output["tract_id"].str.replace(r"\.0$", "", regex=True).str.zfill(11)
    output["geometry_wkt"] = pd.NA
    output = output[output["tract_id"] != ""]
    return output[EQUIVALENCY_COLUMNS].drop_duplicates("tract_id", keep="last").reset_index(drop=True)


def build_tract_to_nta(
    tract_path: str | Path,
    nta_path: str | Path,
    tract_id_col: str = "tract_id",
    nta_id_col: str = "nta_id",
    nta_name_col: str = "nta_name",
) -> gpd.GeoDataFrame:
    """Assign census tracts to NTAs using tract centroids."""

    tracts = load_shapefile(tract_path)
    ntas = load_shapefile(nta_path)

    required_tract_cols = {tract_id_col}
    required_nta_cols = {nta_id_col, nta_name_col}
    missing_tract_cols = required_tract_cols.difference(tracts.columns)
    missing_nta_cols = required_nta_cols.difference(ntas.columns)
    if missing_tract_cols:
        raise ValueError(f"Missing tract columns: {sorted(missing_tract_cols)}")
    if missing_nta_cols:
        raise ValueError(f"Missing NTA columns: {sorted(missing_nta_cols)}")

    mapping = spatial_join_centroids_to_polygons(
        source_polygons=tracts,
        target_polygons=ntas,
        source_id_col=tract_id_col,
        target_columns=[nta_id_col, nta_name_col],
    )
    return mapping.rename(
        columns={
            tract_id_col: "tract_id",
            nta_id_col: "nta_id",
            nta_name_col: "nta_name",
        }
    )[["tract_id", "nta_id", "nta_name", "geometry"]]


def write_tract_to_nta(
    mapping: gpd.GeoDataFrame | pd.DataFrame,
    duckdb_service: DuckDBService,
    table_name: str = "dim_tract_to_nta",
    schema: str = "property_explorer_gold",
) -> None:
    """Persist the mapping to DuckDB.

    DuckDB does not need to own geometry for the first starter version. We store
    WKT for portability and keep geospatial operations in GeoPandas.
    """

    output = mapping.copy()
    if isinstance(output, gpd.GeoDataFrame) and "geometry" in output.columns:
        output["geometry_wkt"] = output.geometry.to_wkt()
        output = output.drop(columns="geometry")
    elif "geometry_wkt" not in output.columns:
        output["geometry_wkt"] = pd.NA

    for column in EQUIVALENCY_COLUMNS:
        if column not in output.columns:
            output[column] = pd.NA
    duckdb_service.write_dataframe(
        dataframe=output[EQUIVALENCY_COLUMNS],
        table_name=table_name,
        schema=schema,
        if_exists="replace",
    )


def run_equivalency(
    equivalency_path: str | Path,
    database_path: str | Path,
) -> pd.DataFrame:
    """Load and store a source-provided tract-to-NTA equivalency table."""

    mapping = read_tract_to_nta_equivalency(equivalency_path)
    with DuckDBService(database_path) as duckdb_service:
        write_tract_to_nta(mapping, duckdb_service)
    return mapping


def run(
    tract_path: str | Path,
    nta_path: str | Path,
    database_path: str | Path,
) -> gpd.GeoDataFrame:
    """Build and store tract-to-NTA mapping."""

    mapping = build_tract_to_nta(tract_path=tract_path, nta_path=nta_path)
    with DuckDBService(database_path) as duckdb_service:
        write_tract_to_nta(mapping, duckdb_service)
    return mapping
