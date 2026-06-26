# Download the Census Bureau 2020-to-2010 block group relationship file and
# land it in staging. This crosswalk is the foundation for the SLD tract rollup:
# SLD carries 2010 BG identifiers, our tract backbone is 2020/2023 vintage, and
# this file maps each 2010 BG to its overlapping 2020 BG(s) with land-area
# overlap for weighting.
#
# Source: https://www2.census.gov/geo/docs/maps-data/data/rel2020/blkgrp/
# File:   tab20_blkgrp20_blkgrp10_natl.txt  (~46 MB, pipe-delimited)
# Key fields:
#   GEOID_BLKGRP_10  - 12-digit 2010 block group GEOID
#   GEOID_BLKGRP_20  - 12-digit 2020 block group GEOID
#   AREALAND_PART    - square meters of 2010 BG land that falls in this 2020 BG
#   AREALAND_BLKGRP_10 - total 2010 BG land area (denominator for weight)

getwd()

# 1. Environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data    <- get_env_path("DATA")
raw_dir <- file.path(data, "demographics", "raw", "crosswalks", "census_bg_xwalk")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Download ----
xwalk_url      <- "https://www2.census.gov/geo/docs/maps-data/data/rel2020/blkgrp/tab20_blkgrp20_blkgrp10_natl.txt"
xwalk_filename <- "tab20_blkgrp20_blkgrp10_natl.txt"
xwalk_path     <- file.path(raw_dir, xwalk_filename)

if (!file.exists(xwalk_path)) {
  message("Downloading Census BG relationship file (~46 MB)...")
  resp <- httr::GET(
    xwalk_url,
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)"),
    httr::write_disk(xwalk_path, overwrite = TRUE),
    httr::progress()
  )
  httr::stop_for_status(resp)
  message("Download complete.")
} else {
  message("Census BG crosswalk file already present, skipping download.")
}

# 3. Read and normalize ----
raw <- readr::read_delim(
  xwalk_path,
  delim = "|",
  col_types = readr::cols(
    OID_BLKGRP_20      = readr::col_skip(),
    GEOID_BLKGRP_20    = readr::col_character(),
    NAMELSAD_BLKGRP_20 = readr::col_skip(),
    AREALAND_BLKGRP_20 = readr::col_skip(),
    AREAWATER_BLKGRP_20 = readr::col_skip(),
    MTFCC_BLKGRP_20    = readr::col_skip(),
    FUNCSTAT_BLKGRP_20 = readr::col_skip(),
    OID_BLKGRP_10      = readr::col_skip(),
    GEOID_BLKGRP_10    = readr::col_character(),
    NAMELSAD_BLKGRP_10 = readr::col_skip(),
    AREALAND_BLKGRP_10 = readr::col_double(),
    AREAWATER_BLKGRP_10 = readr::col_skip(),
    MTFCC_BLKGRP_10    = readr::col_skip(),
    FUNCSTAT_BLKGRP_10 = readr::col_skip(),
    AREALAND_PART      = readr::col_double(),
    AREAWATER_PART     = readr::col_skip()
  ),
  show_col_types = FALSE,
  progress = FALSE
)

bg_xwalk <- raw %>%
  transmute(
    bg_geoid_2010      = stringr::str_pad(GEOID_BLKGRP_10, width = 12, side = "left", pad = "0"),
    bg_geoid_2020      = stringr::str_pad(GEOID_BLKGRP_20, width = 12, side = "left", pad = "0"),
    tract_geoid_2020   = stringr::str_sub(bg_geoid_2020, 1, 11),
    arealand_part_sqm  = AREALAND_PART,
    arealand_2010_sqm  = AREALAND_BLKGRP_10,
    # Land-area weight: share of 2010 BG land that lands in this 2020 BG.
    # Rows for a given bg_geoid_2010 sum to 1.0 (or very close — rounding noise
    # is expected for BGs that straddle 2010/2020 boundaries).
    land_area_weight   = dplyr::if_else(
      !is.na(AREALAND_BLKGRP_10) & AREALAND_BLKGRP_10 > 0,
      AREALAND_PART / AREALAND_BLKGRP_10,
      NA_real_
    )
  )

# 4. Contract checks ----
invalid_2010 <- bg_xwalk %>%
  filter(is.na(bg_geoid_2010) | !stringr::str_detect(bg_geoid_2010, "^\\d{12}$"))

if (nrow(invalid_2010) > 0) {
  stop(glue("{nrow(invalid_2010)} rows have invalid 12-digit bg_geoid_2010."), call. = FALSE)
}

invalid_2020 <- bg_xwalk %>%
  filter(is.na(bg_geoid_2020) | !stringr::str_detect(bg_geoid_2020, "^\\d{12}$"))

if (nrow(invalid_2020) > 0) {
  stop(glue("{nrow(invalid_2020)} rows have invalid 12-digit bg_geoid_2020."), call. = FALSE)
}

weight_sanity <- bg_xwalk %>%
  filter(!is.na(land_area_weight)) %>%
  group_by(bg_geoid_2010) %>%
  summarise(weight_sum = sum(land_area_weight), .groups = "drop") %>%
  filter(abs(weight_sum - 1) > 0.01)

if (nrow(weight_sanity) > 0) {
  message(glue(
    "Note: {nrow(weight_sanity)} 2010 BGs have land-area weights that sum ",
    "outside [0.99, 1.01]. This is expected for water-only or island-area BGs."
  ))
}

message(glue(
  "Crosswalk loaded: {nrow(bg_xwalk)} rows | ",
  "{dplyr::n_distinct(bg_xwalk$bg_geoid_2010)} unique 2010 BGs | ",
  "{dplyr::n_distinct(bg_xwalk$bg_geoid_2020)} unique 2020 BGs"
))

# 5. Write to staging ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "census_bg_xwalk_2010_2020"),
  bg_xwalk,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
message("staging.census_bg_xwalk_2010_2020 written.")
