# Stage the national 2020 Census block backbone sequentially. The registry keeps
# block attributes only; block polygons are deliberately outside this engine.
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

# Census' PL directory names and file stems are not mechanically identical for
# DC, so retain the published values rather than deriving URLs from display text.
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

read_pipe_columns <- function(path, columns, names) {
  readr::read_delim(
    path, delim = "|", col_names = FALSE,
    col_select = all_of(paste0("X", columns)),
    col_types = cols(.default = col_character()), progress = FALSE,
    name_repair = "minimal"
  ) |> setNames(names)
}

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)
dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging")
dbExecute(con, "
  CREATE TABLE IF NOT EXISTS staging.census_pl2020_blocks (
    block_geoid VARCHAR,
    state_fips VARCHAR,
    county_geoid VARCHAR,
    tract_geoid VARCHAR,
    place_geoid VARCHAR,
    zcta_geoid VARCHAR,
    population_2020 INTEGER,
    housing_units_2020 INTEGER,
    land_area_sqm DOUBLE,
    water_area_sqm DOUBLE,
    boundary_vintage INTEGER,
    source_release_year INTEGER,
    source VARCHAR
  )
")

pl_root <- "https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171"
baf_root <- "https://www2.census.gov/geo/docs/maps-data/data/baf2020"

for (state in split(states, seq_len(nrow(states)))) {
  state <- state[1, ]
  message("Staging 2020 Census blocks for ", state$state_abbr)
  state_dir <- file.path(raw_root, "census_2020", state$state_abbr)
  dir.create(state_dir, recursive = TRUE, showWarnings = FALSE)

  pl_zip <- download_cached(
    paste0(pl_root, "/", state$directory, "/", state$file_stem, "2020.pl.zip"),
    file.path(state_dir, paste0(state$file_stem, "2020.pl.zip"))
  )
  baf_zip <- download_cached(
    paste0(baf_root, "/BlockAssign_ST", state$state_fips, "_", state$state_abbr, ".zip"),
    file.path(state_dir, paste0("BlockAssign_ST", state$state_fips, "_", state$state_abbr, ".zip"))
  )

  extract_dir <- file.path(state_dir, "extracted")
  if (!dir.exists(extract_dir)) {
    dir.create(extract_dir)
    unzip(pl_zip, exdir = extract_dir)
    unzip(baf_zip, exdir = extract_dir)
  }

  geo <- read_pipe_columns(
    file.path(extract_dir, paste0(state$file_stem, "geo2020.pl")),
    c(3, 8, 10, 13, 15, 18, 19, 33, 35, 85, 86),
    c("sumlev", "logrecno", "block_geoid", "state_fips", "county_fips", "zcta_geoid", "zcta_type", "tract_code", "block_code", "land_area_sqm", "water_area_sqm")
  ) |>
    filter(sumlev == "750") |>
    transmute(
      logrecno,
      block_geoid,
      state_fips,
      county_geoid = paste0(state_fips, county_fips),
      tract_geoid = paste0(state_fips, county_fips, tract_code),
      zcta_geoid = if_else(zcta_type == "Z5", na_if(zcta_geoid, ""), NA_character_),
      land_area_sqm = as.double(land_area_sqm),
      water_area_sqm = as.double(water_area_sqm)
    )

  population <- read_pipe_columns(
    file.path(extract_dir, paste0(state$file_stem, "000012020.pl")), c(5, 6), c("logrecno", "population_2020")
  )
  housing <- read_pipe_columns(
    file.path(extract_dir, paste0(state$file_stem, "000022020.pl")), c(5, 6), c("logrecno", "housing_units_2020")
  )
  place_file <- file.path(extract_dir, paste0("BlockAssign_ST", state$state_fips, "_", state$state_abbr, "_INCPLACE_CDP.txt"))
  place <- readr::read_delim(place_file, delim = "|", col_types = cols(.default = col_character()), progress = FALSE) |>
    transmute(block_geoid = BLOCKID, place_geoid = na_if(PLACEFP, ""))

  staged <- geo |>
    left_join(population, by = "logrecno") |>
    left_join(housing, by = "logrecno") |>
    left_join(place, by = "block_geoid") |>
    transmute(
      block_geoid, state_fips, county_geoid, tract_geoid, place_geoid, zcta_geoid,
      population_2020 = as.integer(population_2020), housing_units_2020 = as.integer(housing_units_2020),
      land_area_sqm, water_area_sqm, boundary_vintage = 2020L,
      source_release_year = 2021L, source = "CENSUS_2020_PL94_171_BAF"
    )

  # Replacing only the state being processed makes a failed national run safe
  # to resume without duplicating earlier states or discarding their cache.
  dbExecute(con, sprintf("DELETE FROM staging.census_pl2020_blocks WHERE state_fips = '%s'", state$state_fips))
  dbWriteTable(con, Id(schema = "staging", table = "census_pl2020_blocks"), staged, append = TRUE)
}

message("Staged 2020 Census block registry inputs for ", nrow(states), " states.")
