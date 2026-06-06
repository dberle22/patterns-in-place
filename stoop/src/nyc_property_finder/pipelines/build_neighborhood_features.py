"""Build starter neighborhood feature tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from nyc_property_finder.services.duckdb_service import DuckDBService


TRACT_FEATURE_COLUMNS = [
    "tract_id",
    "median_income",
    "median_rent",
    "median_home_value",
    "pct_bachelors_plus",
    "median_age",
    "crime_rate_proxy",
]
NTA_FEATURE_COLUMNS = [
    "nta_id",
    "nta_name",
    "borough",
    "tract_count",
    "median_income",
    "median_rent",
    "median_home_value",
    "pct_bachelors_plus",
    "median_age",
    "crime_rate_proxy",
]
NYC_CORE_COUNTY_GEOIDS = ("36047", "36061")


def build_acs_features(acs_dataframe: pd.DataFrame | None = None) -> pd.DataFrame:
    """Create tract-level ACS features.

    TODO: Replace placeholder column mapping with Census API/table-specific
    transforms after source fields are finalized.
    """

    if acs_dataframe is None or acs_dataframe.empty:
        return pd.DataFrame(columns=TRACT_FEATURE_COLUMNS)

    output = acs_dataframe.copy()
    for column in TRACT_FEATURE_COLUMNS:
        if column not in output.columns:
            output[column] = pd.NA
    return output[TRACT_FEATURE_COLUMNS]


def add_crime_proxy(features: pd.DataFrame, crime_dataframe: pd.DataFrame | None = None) -> pd.DataFrame:
    """Add a simple crime proxy to tract features."""

    output = features.copy()
    if crime_dataframe is None or crime_dataframe.empty:
        output["crime_rate_proxy"] = output["crime_rate_proxy"].fillna(0)
        return output

    # TODO: Spatially join incidents to tracts and normalize by population.
    crime_counts = crime_dataframe.groupby("tract_id").size().reset_index(name="crime_rate_proxy")
    output = output.drop(columns=["crime_rate_proxy"], errors="ignore").merge(crime_counts, on="tract_id", how="left")
    output["crime_rate_proxy"] = output["crime_rate_proxy"].fillna(0)
    return output[TRACT_FEATURE_COLUMNS]


def build_neighborhood_features(
    acs_dataframe: pd.DataFrame | None = None,
    crime_dataframe: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build tract-level neighborhood features from ACS and crime inputs."""

    features = build_acs_features(acs_dataframe)
    return add_crime_proxy(features, crime_dataframe)


def read_metro_deep_dive_tract_features(
    source_database_path: str | Path,
    county_geoids: tuple[str, ...] = NYC_CORE_COUNTY_GEOIDS,
) -> pd.DataFrame:
    """Read MVP tract features from the local Metro Deep Dive DuckDB."""

    import duckdb

    county_filter = ", ".join(f"'{county_geoid}'" for county_geoid in county_geoids)
    rof_query = f"""
        WITH latest_rof_tract_year AS (
            SELECT MAX(year) AS year
            FROM rof_features.tract_features
            WHERE county_geoid IN ({county_filter})
        )
        SELECT
            r.tract_geoid AS tract_id,
            r.median_hh_income AS median_income,
            r.median_gross_rent AS median_rent,
            r.median_home_value,
            p.pct_ba_plus AS pct_bachelors_plus,
            p.median_age,
            CAST(NULL AS DOUBLE) AS crime_rate_proxy
        FROM rof_features.tract_features r
        INNER JOIN latest_rof_tract_year latest
            ON r.year = latest.year
        LEFT JOIN gold.population_demographics p
            ON p.geo_level = 'tract'
           AND r.tract_geoid = p.geo_id
           AND r.year = p.year
        WHERE r.county_geoid IN ({county_filter})
    """
    foundation_query = f"""
        WITH latest_foundation_tract_year AS (
            SELECT MAX(year) AS year
            FROM foundation.tract_features
            WHERE county_geoid IN ({county_filter})
        )
        SELECT
            f.tract_geoid AS tract_id,
            f.median_hh_income AS median_income,
            f.median_gross_rent AS median_rent,
            f.median_home_value,
            p.pct_ba_plus AS pct_bachelors_plus,
            p.median_age,
            CAST(NULL AS DOUBLE) AS crime_rate_proxy
        FROM foundation.tract_features f
        INNER JOIN latest_foundation_tract_year latest
            ON f.year = latest.year
        LEFT JOIN gold.population_demographics p
            ON p.geo_level = 'tract'
           AND f.tract_geoid = p.geo_id
           AND f.year = p.year
        WHERE f.county_geoid IN ({county_filter})
    """
    gold_query = f"""
        SELECT
            h.geo_id AS tract_id,
            h.median_hh_income AS median_income,
            h.median_gross_rent AS median_rent,
            h.median_home_value,
            p.pct_ba_plus AS pct_bachelors_plus,
            p.median_age,
            CAST(NULL AS DOUBLE) AS crime_rate_proxy
        FROM gold.housing_core_wide h
        LEFT JOIN gold.population_demographics p
            ON h.geo_level = p.geo_level
           AND h.geo_id = p.geo_id
           AND h.year = p.year
        WHERE h.geo_level = 'tract'
          AND h.year = (SELECT MAX(year) FROM gold.housing_core_wide WHERE geo_level = 'tract')
          AND ({' OR '.join(f"h.geo_id LIKE '{county_geoid}%'" for county_geoid in county_geoids)})
    """
    with duckdb.connect(str(source_database_path), read_only=True) as connection:
        rof_features = connection.execute(rof_query).fetchdf()
        foundation_features = connection.execute(foundation_query).fetchdf()
        gold_features = connection.execute(gold_query).fetchdf()

    features = rof_features
    for fallback_features in [foundation_features, gold_features]:
        if fallback_features.empty:
            continue
        if features.empty:
            features = fallback_features
            continue
        existing_tract_ids = set(features["tract_id"].dropna().astype(str))
        missing_features = fallback_features[
            ~fallback_features["tract_id"].astype(str).isin(existing_tract_ids)
        ]
        if not missing_features.empty:
            features = pd.concat([features, missing_features], ignore_index=True)
    return features[TRACT_FEATURE_COLUMNS].reset_index(drop=True)


def empty_tract_features_from_mapping(
    tract_to_nta: pd.DataFrame,
    county_geoids: tuple[str, ...] = NYC_CORE_COUNTY_GEOIDS,
) -> pd.DataFrame:
    """Create null-valued tract feature rows when source metrics are unavailable."""

    tract_ids = tract_to_nta["tract_id"].fillna("").astype(str)
    features = pd.DataFrame({"tract_id": tract_ids[tract_ids.str.startswith(county_geoids)].drop_duplicates()})
    for column in TRACT_FEATURE_COLUMNS:
        if column not in features.columns:
            features[column] = pd.NA
    return features[TRACT_FEATURE_COLUMNS].reset_index(drop=True)


def add_missing_tract_feature_rows_from_mapping(
    tract_features: pd.DataFrame,
    tract_to_nta: pd.DataFrame,
    county_geoids: tuple[str, ...] = NYC_CORE_COUNTY_GEOIDS,
) -> pd.DataFrame:
    """Add null-valued rows for mapped target-county tracts missing from sources."""

    fallback_features = empty_tract_features_from_mapping(tract_to_nta, county_geoids=county_geoids)
    if tract_features.empty:
        return fallback_features

    existing_tract_ids = set(tract_features["tract_id"].dropna().astype(str))
    missing_features = fallback_features[
        ~fallback_features["tract_id"].astype(str).isin(existing_tract_ids)
    ]
    if missing_features.empty:
        return tract_features[TRACT_FEATURE_COLUMNS].reset_index(drop=True)
    return pd.concat(
        [tract_features[TRACT_FEATURE_COLUMNS], missing_features[TRACT_FEATURE_COLUMNS]],
        ignore_index=True,
    )


def build_nta_features(tract_features: pd.DataFrame, tract_to_nta: pd.DataFrame) -> pd.DataFrame:
    """Aggregate tract features into an NTA-native feature contract."""

    if tract_features.empty or tract_to_nta.empty:
        return pd.DataFrame(columns=NTA_FEATURE_COLUMNS)

    joined = tract_features.merge(
        tract_to_nta[["tract_id", "nta_id", "nta_name", "borough"]].drop_duplicates("tract_id"),
        on="tract_id",
        how="inner",
    )
    metrics = [
        "median_income",
        "median_rent",
        "median_home_value",
        "pct_bachelors_plus",
        "median_age",
        "crime_rate_proxy",
    ]
    for metric in metrics:
        joined[metric] = pd.to_numeric(joined[metric], errors="coerce")
    aggregated = (
        joined.groupby(["nta_id", "nta_name"], dropna=False)
        .agg(
            borough=("borough", _collapse_boroughs),
            tract_count=("tract_id", "nunique"),
            median_income=("median_income", "median"),
            median_rent=("median_rent", "median"),
            median_home_value=("median_home_value", "median"),
            pct_bachelors_plus=("pct_bachelors_plus", "median"),
            median_age=("median_age", "median"),
            crime_rate_proxy=("crime_rate_proxy", "median"),
        )
        .reset_index()
    )
    return aggregated[NTA_FEATURE_COLUMNS]


def _collapse_boroughs(values: pd.Series) -> str | pd.NA:
    """Return one stable borough label per NTA, joining cross-borough cases."""

    unique_values = sorted({str(value).strip() for value in values if str(value).strip()})
    if not unique_values:
        return pd.NA
    return " / ".join(unique_values)


def write_neighborhood_features(
    features: pd.DataFrame,
    duckdb_service: DuckDBService,
    table_name: str = "fct_tract_features",
    schema: str = "property_explorer_gold",
) -> None:
    """Persist tract feature table."""

    duckdb_service.write_dataframe(features, table_name=table_name, schema=schema, if_exists="replace")


def write_nta_features(
    features: pd.DataFrame,
    duckdb_service: DuckDBService,
    table_name: str = "fct_nta_features",
    schema: str = "property_explorer_gold",
) -> None:
    """Persist NTA feature table."""

    duckdb_service.write_dataframe(features, table_name=table_name, schema=schema, if_exists="replace")


def run(database_path: str | Path) -> pd.DataFrame:
    """Pipeline entry point using placeholder empty source data."""

    features = build_neighborhood_features()
    with DuckDBService(database_path) as duckdb_service:
        write_neighborhood_features(features, duckdb_service)
    return features


def run_metro_deep_dive(
    database_path: str | Path,
    source_database_path: str | Path,
    county_geoids: tuple[str, ...] = NYC_CORE_COUNTY_GEOIDS,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build tract and NTA feature tables from Metro Deep Dive tract features."""

    tract_features = read_metro_deep_dive_tract_features(source_database_path, county_geoids=county_geoids)
    with DuckDBService(database_path) as duckdb_service:
        tract_to_nta = duckdb_service.query_df("SELECT * FROM property_explorer_gold.dim_tract_to_nta")
        tract_features = add_missing_tract_feature_rows_from_mapping(
            tract_features,
            tract_to_nta,
            county_geoids=county_geoids,
        )
        nta_features = build_nta_features(tract_features, tract_to_nta)
        write_neighborhood_features(tract_features, duckdb_service)
        write_nta_features(nta_features, duckdb_service)
    return tract_features, nta_features
