# Build canonical HUD-USPS ZIP allocation tables and compatibility views for
# legacy callers that still use the historical, incorrect xwalk_zcta_* names.
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

library(DBI)
library(duckdb)

db_path <- get_env_path("DB_PATH")
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)
dbExecute(con, "CREATE SCHEMA IF NOT EXISTS silver")

# Each ratio is an address-count allocation from ZIP to the target geography.
# Keep the raw ratio names explicit instead of relabeling them as population or
# housing weights, which would misstate what HUD-USPS actually publishes.
build_zip_xwalk <- function(source_table, target_level, target_column, target_alias, target_width) {
  dbExecute(con, sprintf("
    CREATE OR REPLACE TABLE silver.xwalk_zip_%s AS
    SELECT
      lpad(cast(ZIP as varchar), 5, '0') AS zip_geoid,
      lpad(cast(%s as varchar), %d, '0') AS %s,
      cast(RES_RATIO as double) AS residential_address_ratio,
      cast(BUS_RATIO as double) AS business_address_ratio,
      cast(OTH_RATIO as double) AS other_address_ratio,
      cast(TOT_RATIO as double) AS total_address_ratio,
      cast(source_release_year as integer) AS source_release_year,
      cast(source_release as varchar) AS source_release,
      'HUD_USPS' AS source
    FROM staging.%s
    WHERE ZIP IS NOT NULL AND %s IS NOT NULL
  ", target_level, target_column, target_width, target_alias, source_table, target_column))
}

build_zip_xwalk("hud_usps_zip_county", "county", "COUNTY", "county_geoid", 5)
build_zip_xwalk("hud_usps_zip_cbsa", "cbsa", "CBSA", "cbsa_geoid", 5)
build_zip_xwalk("hud_usps_zip_tract", "tract", "TRACT", "tract_geoid", 11)

# Compatibility views expose the legacy column names so downstream migrations
# can be deliberate. They are ZIP data despite the historic ZCTA table names.
replace_legacy_object_with_view <- function(name, query) {
  object <- dbGetQuery(con, sprintf("
    SELECT table_type
    FROM information_schema.tables
    WHERE table_schema = 'silver' AND table_name = '%s'
  ", name))
  if (nrow(object) == 1) {
    dbExecute(con, sprintf("DROP %s silver.%s", ifelse(object$table_type == "VIEW", "VIEW", "TABLE"), name))
  }
  dbExecute(con, sprintf("CREATE VIEW silver.%s AS %s", name, query))
}

replace_legacy_object_with_view("xwalk_zcta_county", "
  SELECT zip_geoid, county_geoid, residential_address_ratio AS rel_weight_pop,
         business_address_ratio AS rel_weight_bus, total_address_ratio AS rel_weight_hu,
         source_release_year AS vintage, concat('HUD_ZIP_COUNTY_', source_release) AS source
  FROM silver.xwalk_zip_county
")
replace_legacy_object_with_view("xwalk_zcta_cbsa", "
  SELECT zip_geoid, cbsa_geoid, residential_address_ratio AS rel_weight_pop,
         business_address_ratio AS rel_weight_bus, total_address_ratio AS rel_weight_hu,
         source_release_year AS vintage, concat('HUD_ZIP_CBSA_', source_release) AS source
  FROM silver.xwalk_zip_cbsa
")
replace_legacy_object_with_view("xwalk_zcta_tract", "
  SELECT zip_geoid, tract_geoid, residential_address_ratio AS rel_weight_pop,
         business_address_ratio AS rel_weight_bus, total_address_ratio AS rel_weight_hu,
         source_release_year AS vintage, concat('HUD_ZIP_TRACT_', source_release) AS source
  FROM silver.xwalk_zip_tract
")

message("Built canonical ZIP crosswalks and legacy compatibility views.")
