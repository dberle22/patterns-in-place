# Correct Census ZCTA membership with the dedicated national relationship file.
# The PL geographic header is not a complete block-to-ZCTA assignment source.
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

library(DBI)
library(duckdb)

db_path <- get_env_path("DB_PATH")
raw_root <- Sys.getenv("GEOGRAPHY_RAW_DIR", unset = file.path(get_env_path("DATA"), "geography", "raw"))
relationship_dir <- file.path(raw_root, "census_2020", "relationships")
relationship_file <- file.path(relationship_dir, "tab20_zcta520_tabblock20_natl.txt")
relationship_url <- "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_tabblock20_natl.txt"

dir.create(relationship_dir, recursive = TRUE, showWarnings = FALSE)
if (!file.exists(relationship_file)) {
  download.file(relationship_url, relationship_file, mode = "wb", quiet = FALSE)
}

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

# DuckDB scans the 1 GB relationship file directly and retains only the two
# identifiers needed by the block registry. Blocks outside a ZCTA stay null.
relationship_path_sql <- gsub("'", "''", normalizePath(relationship_file, winslash = "/"))
dbExecute(con, sprintf("
  CREATE OR REPLACE TABLE staging.census_zcta_block_2020 AS
  SELECT DISTINCT
    GEOID_TABBLOCK_20 AS block_geoid,
    GEOID_ZCTA5_20 AS zcta_geoid
  FROM read_csv('%s', delim = '|', header = TRUE, all_varchar = TRUE, ignore_errors = FALSE)
  WHERE GEOID_ZCTA5_20 IS NOT NULL AND GEOID_ZCTA5_20 <> ''
", relationship_path_sql))

## Clear the incomplete PL-header values first. The relationship file is the
## authority, and its unmatched blocks must remain null rather than retaining a
## plausible-looking but invalid ZCTA code from the geographic header.
dbExecute(con, "UPDATE staging.census_pl2020_blocks SET zcta_geoid = NULL")

dbExecute(con, "
  UPDATE staging.census_pl2020_blocks AS blocks
  SET zcta_geoid = relationship.zcta_geoid
  FROM staging.census_zcta_block_2020 AS relationship
  WHERE blocks.block_geoid = relationship.block_geoid
")

message("Updated Census block staging with dedicated ZCTA-to-block assignments.")
