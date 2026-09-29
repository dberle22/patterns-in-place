# Stage the Census inputs needed to restate 2010 tract counts on 2020 tracts.
# Population and housing counts come from 2010 PL 94-171 blocks; Census block
# relationships supply the intersection-area proxy used to apportion a block
# when its 2010 boundary was split. No block geometry is stored.
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

library(DBI)
library(duckdb)
library(dplyr)
library(readr)
library(stringr)

db_path <- get_env_path("DB_PATH")
raw_root <- Sys.getenv("GEOGRAPHY_RAW_DIR", unset = file.path(get_env_path("DATA"), "geography", "raw"))
state_scope <- Sys.getenv("GEOGRAPHY_STATE_SCOPE", unset = "")

# Retain published directory names because the legacy 2010 PL archive is not
# mechanically derivable for every jurisdiction.
states <- tibble::tribble(
  ~state_fips, ~state_abbr, ~directory, ~file_stem,
  "01", "AL", "Alabama", "al", "02", "AK", "Alaska", "ak", "04", "AZ", "Arizona", "az",
  "05", "AR", "Arkansas", "ar", "06", "CA", "California", "ca", "08", "CO", "Colorado", "co",
  "09", "CT", "Connecticut", "ct", "10", "DE", "Delaware", "de", "11", "DC", "District_of_Columbia", "dc",
  "12", "FL", "Florida", "fl", "13", "GA", "Georgia", "ga", "15", "HI", "Hawaii", "hi",
  "16", "ID", "Idaho", "id", "17", "IL", "Illinois", "il", "18", "IN", "Indiana", "in",
  "19", "IA", "Iowa", "ia", "20", "KS", "Kansas", "ks", "21", "KY", "Kentucky", "ky",
  "22", "LA", "Louisiana", "la", "23", "ME", "Maine", "me", "24", "MD", "Maryland", "md",
  "25", "MA", "Massachusetts", "ma", "26", "MI", "Michigan", "mi", "27", "MN", "Minnesota", "mn",
  "28", "MS", "Mississippi", "ms", "29", "MO", "Missouri", "mo", "30", "MT", "Montana", "mt",
  "31", "NE", "Nebraska", "ne", "32", "NV", "Nevada", "nv", "33", "NH", "New_Hampshire", "nh",
  "34", "NJ", "New_Jersey", "nj", "35", "NM", "New_Mexico", "nm", "36", "NY", "New_York", "ny",
  "37", "NC", "North_Carolina", "nc", "38", "ND", "North_Dakota", "nd", "39", "OH", "Ohio", "oh",
  "40", "OK", "Oklahoma", "ok", "41", "OR", "Oregon", "or", "42", "PA", "Pennsylvania", "pa",
  "44", "RI", "Rhode_Island", "ri", "45", "SC", "South_Carolina", "sc", "46", "SD", "South_Dakota", "sd",
  "47", "TN", "Tennessee", "tn", "48", "TX", "Texas", "tx", "49", "UT", "Utah", "ut",
  "50", "VT", "Vermont", "vt", "51", "VA", "Virginia", "va", "53", "WA", "Washington", "wa",
  "54", "WV", "West_Virginia", "wv", "55", "WI", "Wisconsin", "wi", "56", "WY", "Wyoming", "wy"
)

if (nzchar(state_scope)) {
  requested <- str_split(state_scope, ",", simplify = TRUE) |> str_trim() |> toupper()
  unknown <- setdiff(requested, states$state_abbr)
  if (length(unknown) > 0) stop("Unknown GEOGRAPHY_STATE_SCOPE values: ", paste(unknown, collapse = ", "))
  states <- filter(states, state_abbr %in% requested)
}

download_cached <- function(url, destination) {
  if (!file.exists(destination)) download.file(url, destination, mode = "wb", quiet = FALSE)
  destination
}

read_segment_counts <- function(path, count_name) {
  readr::read_csv(
    path, col_names = FALSE, col_select = c(X5, X6),
    col_types = cols(X5 = col_character(), X6 = col_integer()), progress = FALSE
  ) |>
    setNames(c("logrecno", count_name))
}

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)
dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging")
dbExecute(con, "
  CREATE TABLE IF NOT EXISTS staging.census_pl2010_blocks (
    block_geoid VARCHAR, tract_geoid VARCHAR, population_2010 INTEGER,
    housing_units_2010 INTEGER, source_release_year INTEGER, source VARCHAR
  )
")
dbExecute(con, "
  CREATE TABLE IF NOT EXISTS staging.census_block_relationship_2010_2020 (
    from_block_geoid VARCHAR, to_block_geoid VARCHAR, intersection_land_area_sqm DOUBLE,
    source VARCHAR
  )
")

pl_root <- "https://www2.census.gov/census_2010/01-Redistricting_File--PL_94-171"
relationship_root <- "https://www2.census.gov/geo/docs/maps-data/data/rel2020/t10t20"

for (state in split(states, seq_len(nrow(states)))) {
  state <- state[1, ]
  message("Staging 2010-to-2020 temporal inputs for ", state$state_abbr)
  state_dir <- file.path(raw_root, "census_2010_2020", state$state_abbr)
  dir.create(state_dir, recursive = TRUE, showWarnings = FALSE)

  pl_zip <- download_cached(
    paste0(pl_root, "/", state$directory, "/", state$file_stem, "2010.pl.zip"),
    file.path(state_dir, paste0(state$file_stem, "2010.pl.zip"))
  )
  relationship_zip <- download_cached(
    paste0(relationship_root, "/TAB2010_TAB2020_ST", state$state_fips, ".zip"),
    file.path(state_dir, paste0("TAB2010_TAB2020_ST", state$state_fips, ".zip"))
  )

  # Legacy PL files have a fixed-width geographic header and comma-delimited
  # segments. Extract only for this state and clean up the temporary copy after
  # the normalized rows are written; the original published archives stay cached.
  extract_dir <- tempfile(pattern = paste0("census_", state$state_abbr, "_"))
  dir.create(extract_dir)
  unzip(pl_zip, exdir = extract_dir)
  unzip(relationship_zip, exdir = extract_dir)

  geo <- readr::read_fwf(
    file.path(extract_dir, paste0(state$file_stem, "geo2010.pl")),
    readr::fwf_positions(
      start = c(9, 19, 28, 30, 55, 62), end = c(11, 25, 29, 32, 60, 65),
      col_names = c("sumlev", "logrecno", "state_fips", "county_fips", "tract_code", "block_code")
    ), col_types = cols(.default = col_character()), progress = FALSE
  ) |>
    filter(sumlev == "750") |>
    transmute(
      logrecno, block_geoid = paste0(state_fips, county_fips, tract_code, block_code),
      tract_geoid = paste0(state_fips, county_fips, tract_code)
    )
  population <- read_segment_counts(file.path(extract_dir, paste0(state$file_stem, "000012010.pl")), "population_2010")
  housing <- read_segment_counts(file.path(extract_dir, paste0(state$file_stem, "000022010.pl")), "housing_units_2010")
  blocks <- geo |>
    left_join(population, by = "logrecno") |>
    left_join(housing, by = "logrecno") |>
    transmute(block_geoid, tract_geoid, population_2010, housing_units_2010,
              source_release_year = 2011L, source = "CENSUS_2010_PL94_171")

  relationship_file <- list.files(extract_dir, pattern = "^tab2010_tab2020.*\\.txt$", full.names = TRUE, ignore.case = TRUE)
  relationship <- readr::read_delim(
    relationship_file, delim = "|",
    col_select = c(STATE_2010, COUNTY_2010, TRACT_2010, BLK_2010,
                   STATE_2020, COUNTY_2020, TRACT_2020, BLK_2020, AREALAND_INT),
    col_types = cols(.default = col_character(), AREALAND_INT = col_double()), progress = FALSE
  ) |>
    transmute(
      from_block_geoid = paste0(STATE_2010, COUNTY_2010, TRACT_2010, BLK_2010),
      to_block_geoid = paste0(STATE_2020, COUNTY_2020, TRACT_2020, BLK_2020),
      intersection_land_area_sqm = AREALAND_INT,
      source = "CENSUS_2020_BLOCK_RELATIONSHIP"
    )

  # State-level replacement makes national work resumable without duplicate
  # rows. A state FIPS prefix identifies both source and target block records.
  dbExecute(con, sprintf("DELETE FROM staging.census_pl2010_blocks WHERE left(block_geoid, 2) = '%s'", state$state_fips))
  dbExecute(con, sprintf("DELETE FROM staging.census_block_relationship_2010_2020 WHERE left(from_block_geoid, 2) = '%s'", state$state_fips))
  dbWriteTable(con, Id(schema = "staging", table = "census_pl2010_blocks"), blocks, append = TRUE)
  dbWriteTable(con, Id(schema = "staging", table = "census_block_relationship_2010_2020"), relationship, append = TRUE)
  unlink(extract_dir, recursive = TRUE, force = TRUE)
}

# The national tract relationship is the direct, smaller authority for land
# basis. It avoids recreating tract land overlap from lower-level edges.
tract_file <- file.path(raw_root, "census_2010_2020", "tab20_tract20_tract10_natl.txt")
dir.create(dirname(tract_file), recursive = TRUE, showWarnings = FALSE)
download_cached(
  "https://www2.census.gov/geo/docs/maps-data/data/rel2020/tract/tab20_tract20_tract10_natl.txt",
  tract_file
)
tract_file_sql <- gsub("'", "''", normalizePath(tract_file, winslash = "/"))
dbExecute(con, sprintf("
  CREATE OR REPLACE TABLE staging.census_tract_relationship_2010_2020 AS
  SELECT GEOID_TRACT_10 AS from_tract_geoid, GEOID_TRACT_20 AS to_tract_geoid,
         cast(AREALAND_PART AS DOUBLE) AS intersection_land_area_sqm,
         cast(AREALAND_TRACT_10 AS DOUBLE) AS from_land_area_sqm,
         'CENSUS_2020_TRACT_RELATIONSHIP' AS source
  FROM read_csv('%s', delim = '|', header = TRUE, all_varchar = TRUE)
  WHERE GEOID_TRACT_10 IS NOT NULL AND GEOID_TRACT_20 IS NOT NULL
", tract_file_sql))

message("Staged 2010 block counts and 2010-to-2020 Census relationships.")
