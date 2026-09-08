# Build governed identity and exact-containment tables after national Census
# block staging. Allocation and temporal tables remain separate later builds.
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

library(DBI)
library(duckdb)

db_path <- get_env_path("DB_PATH")
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)
dbExecute(con, "CREATE SCHEMA IF NOT EXISTS silver")

# The block table is intentionally tabular. It is the authoritative atom for
# later allocation bases, while geometry remains in the geo schema by design.
dbExecute(con, "
  CREATE OR REPLACE TABLE silver.block_registry AS
  SELECT
    block_geoid, state_fips, county_geoid, tract_geoid, place_geoid, zcta_geoid,
    population_2020, housing_units_2020, land_area_sqm, water_area_sqm,
    boundary_vintage, source_release_year, source
  FROM staging.census_pl2020_blocks
")

# Preserve the legacy serving dimension's names and hierarchy where it already
# provides a governed current label, then add 2020 Place/ZCTA identities from
# the Census block backbone. ZCTA labels are intentionally descriptive because
# Census does not publish a separate local-name field for ZCTAs.
dbExecute(con, "
  CREATE OR REPLACE TABLE silver.dim_geo AS
  WITH current_identity AS (
    SELECT
      geo_level,
      geo_id,
      vintage AS boundary_vintage,
      geo_name,
      display_name,
      parent_geo_level AS containment_parent_level,
      parent_geo_id AS containment_parent_id,
      CASE geo_level
        WHEN 'us' THEN 'stable'
        WHEN 'region' THEN 'stable'
        WHEN 'division' THEN 'stable'
        WHEN 'state' THEN 'stable'
        WHEN 'cbsa' THEN 'periodic'
        WHEN 'county' THEN 'continuous'
        WHEN 'tract' THEN 'decennial'
      END AS stability_class,
      CAST(NULL AS DOUBLE) AS land_area_sqm,
      CAST(NULL AS DOUBLE) AS water_area_sqm,
      vintage AS source_release_year,
      source
    FROM gold.dim_geo
  ),
  census_2020_identity AS (
    SELECT
      level.geo_level,
      level.geo_id,
      2020 AS boundary_vintage,
      coalesce(current.geo_name, concat('Census ', level.geo_level, ' ', level.geo_id)) AS geo_name,
      coalesce(current.display_name, concat('Census ', level.geo_level, ' ', level.geo_id)) AS display_name,
      CAST(NULL AS VARCHAR) AS containment_parent_level,
      CAST(NULL AS VARCHAR) AS containment_parent_id,
      CASE level.geo_level
        WHEN 'state' THEN 'stable'
        WHEN 'county' THEN 'continuous'
        WHEN 'tract' THEN 'decennial'
      END AS stability_class,
      level.land_area_sqm,
      level.water_area_sqm,
      2021 AS source_release_year,
      'CENSUS_2020_PL94_171' AS source
    FROM (
      SELECT 'state' AS geo_level, state_fips AS geo_id, sum(land_area_sqm) AS land_area_sqm, sum(water_area_sqm) AS water_area_sqm
      FROM silver.block_registry GROUP BY 1, 2
      UNION ALL
      SELECT 'county', county_geoid, sum(land_area_sqm), sum(water_area_sqm)
      FROM silver.block_registry GROUP BY 1, 2
      UNION ALL
      SELECT 'tract', tract_geoid, sum(land_area_sqm), sum(water_area_sqm)
      FROM silver.block_registry GROUP BY 1, 2
    ) AS level
    LEFT JOIN current_identity AS current
      ON level.geo_level = current.geo_level
     AND level.geo_id = current.geo_id
  ),
  place_identity AS (
    SELECT
      'place' AS geo_level,
      concat(state_fips, place_geoid) AS geo_id,
      2020 AS boundary_vintage,
      concat('Census place ', state_fips, place_geoid) AS geo_name,
      concat('Census place ', state_fips, place_geoid) AS display_name,
      CAST(NULL AS VARCHAR) AS containment_parent_level,
      CAST(NULL AS VARCHAR) AS containment_parent_id,
      'continuous' AS stability_class,
      sum(land_area_sqm) AS land_area_sqm,
      sum(water_area_sqm) AS water_area_sqm,
      2021 AS source_release_year,
      'CENSUS_2020_PL94_171_BAF' AS source
    FROM silver.block_registry
    WHERE place_geoid IS NOT NULL
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 11, 12
  ),
  zcta_identity AS (
    SELECT
      'zcta' AS geo_level,
      zcta_geoid AS geo_id,
      2020 AS boundary_vintage,
      concat('ZCTA ', zcta_geoid) AS geo_name,
      concat('ZCTA ', zcta_geoid) AS display_name,
      CAST(NULL AS VARCHAR) AS containment_parent_level,
      CAST(NULL AS VARCHAR) AS containment_parent_id,
      'decennial' AS stability_class,
      sum(land_area_sqm) AS land_area_sqm,
      sum(water_area_sqm) AS water_area_sqm,
      2021 AS source_release_year,
      'CENSUS_2020_PL94_171' AS source
    FROM silver.block_registry
    WHERE zcta_geoid IS NOT NULL
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 11, 12
  ),
  tract_2010_identity AS (
    -- Temporal edges need both ends in the identity registry. Names remain
    -- descriptive until a 2010 label source is needed by a consumer.
    SELECT DISTINCT
      'tract' AS geo_level,
      from_tract_geoid AS geo_id,
      2010 AS boundary_vintage,
      concat('Census tract ', from_tract_geoid) AS geo_name,
      concat('Census tract ', from_tract_geoid) AS display_name,
      CAST(NULL AS VARCHAR) AS containment_parent_level,
      CAST(NULL AS VARCHAR) AS containment_parent_id,
      'decennial' AS stability_class,
      CAST(NULL AS DOUBLE) AS land_area_sqm,
      CAST(NULL AS DOUBLE) AS water_area_sqm,
      2011 AS source_release_year,
      'CENSUS_2020_TRACT_RELATIONSHIP' AS source
    FROM staging.census_tract_relationship_2010_2020
  )
  SELECT * FROM current_identity
  UNION ALL BY NAME
  SELECT * FROM census_2020_identity
  UNION ALL BY NAME
  SELECT * FROM place_identity
  UNION ALL BY NAME
  SELECT * FROM zcta_identity
  UNION ALL BY NAME
  SELECT * FROM tract_2010_identity
")

# These rows are the sole exact hierarchy interface. Allocation edges never
# enter this table, preventing accidental use of an overlap as containment.
dbExecute(con, "
  CREATE OR REPLACE TABLE silver.xwalk_containment AS
  SELECT DISTINCT
    tract_geoid AS child_geo_id,
    'tract' AS child_geo_level,
    concat(state_fip, county_fip) AS parent_geo_id,
    'county' AS parent_geo_level,
    vintage AS boundary_vintage,
    source,
    'exact' AS relationship_quality
  FROM silver.xwalk_tract_county
  UNION ALL
  SELECT DISTINCT
    tract_geoid,
    'tract',
    county_geoid,
    'county',
    2020,
    'CENSUS_2020_PL94_171',
    'exact'
  FROM silver.block_registry
  UNION ALL
  SELECT DISTINCT
    county_geoid,
    'county',
    state_fip,
    'state',
    vintage,
    source,
    'exact'
  FROM silver.xwalk_county_state
  UNION ALL
  SELECT DISTINCT
    county_geoid,
    'county',
    state_fips,
    'state',
    2020,
    'CENSUS_2020_PL94_171',
    'exact'
  FROM silver.block_registry
  UNION ALL
  SELECT DISTINCT
    state_fips,
    'state',
    CASE census_division
      WHEN 'New England' THEN '1' WHEN 'Middle Atlantic' THEN '2'
      WHEN 'East North Central' THEN '3' WHEN 'West North Central' THEN '4'
      WHEN 'South Atlantic' THEN '5' WHEN 'East South Central' THEN '6'
      WHEN 'West South Central' THEN '7' WHEN 'Mountain' THEN '8'
      WHEN 'Pacific' THEN '9'
    END,
    'division',
    2023,
    'silver.xwalk_state_region',
    'exact'
  FROM silver.xwalk_state_region
  UNION ALL
  SELECT DISTINCT
    state_fips,
    'state',
    CASE census_region
      WHEN 'Northeast' THEN '1' WHEN 'Midwest' THEN '2'
      WHEN 'South' THEN '3' WHEN 'West' THEN '4'
    END,
    'region',
    2023,
    'silver.xwalk_state_region',
    'exact'
  FROM silver.xwalk_state_region
  UNION ALL
  SELECT DISTINCT
    county_geoid,
    'county',
    cbsa_code,
    'cbsa',
    vintage,
    source,
    'exact'
  FROM silver.xwalk_cbsa_county
")

dbExecute(con, "
  CREATE OR REPLACE TABLE silver.geography_coverage_audit AS
  SELECT
    'block_registry' AS audit_name,
    boundary_vintage,
    count(*) AS row_count,
    count(DISTINCT block_geoid) AS distinct_key_count,
    count(*) - count(DISTINCT block_geoid) AS duplicate_key_count
  FROM silver.block_registry
  GROUP BY 1, 2
  UNION ALL
  SELECT
    'dim_geo',
    boundary_vintage,
    count(*),
    count(DISTINCT concat(geo_level, ':', geo_id)),
    count(*) - count(DISTINCT concat(geo_level, ':', geo_id))
  FROM silver.dim_geo
  GROUP BY 1, 2
")

message("Built silver.block_registry, silver.dim_geo, and exact containment.")
