# In this script we land the FEMA National Risk Index county and tract releases
# as wide, source-faithful staging tables. We intentionally keep the full field
# inventory for both files because FEMA's hazard matrix is expensive to
# re-research and Silver can prune it later without forcing a re-download.

getwd()

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "environment", "raw", "fema", "nri")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

# 2. Define the current FEMA releases ----
nri_release_version <- "v120"
nri_release_year <- 2025L
dictionary_name <- "NRIDataDictionary.csv"
hazard_info_name <- "NRI_HazardInfo.csv"
metadata_pdf_name <- "NRI_metadata_December2025.pdf"

county_zip_name <- "NRI_Table_Counties.zip"
county_csv_name <- "NRI_Table_Counties.csv"
tract_zip_name <- "NRI_Table_CensusTracts.zip"
tract_csv_name <- "NRI_Table_CensusTracts.csv"

county_zip_url <- glue(
  "https://www.fema.gov/about/reports-and-data/openfema/nri/{nri_release_version}/{county_zip_name}"
)
tract_zip_url <- glue(
  "https://www.fema.gov/about/reports-and-data/openfema/nri/{nri_release_version}/{tract_zip_name}"
)

county_zip_path <- file.path(raw_dir, county_zip_name)
tract_zip_path <- file.path(raw_dir, tract_zip_name)

download_fema_zip <- function(url, dest_path) {
  if (file.exists(dest_path)) {
    return(dest_path)
  }

  resp <- httr::GET(
    url,
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)

  writeBin(httr::content(resp, "raw"), dest_path)
  dest_path
}

extract_fema_members <- function(zip_path, member_names, exdir) {
  missing_members <- member_names[!file.exists(file.path(exdir, member_names))]

  if (length(missing_members) == 0) {
    return(invisible(file.path(exdir, member_names)))
  }

  utils::unzip(
    zipfile = zip_path,
    files = missing_members,
    exdir = exdir,
    overwrite = TRUE
  )

  invisible(file.path(exdir, member_names))
}

read_fema_csv <- function(csv_path, has_tract_fields = FALSE) {
  base_col_types <- list(
    NRI_ID = readr::col_character(),
    STATE = readr::col_character(),
    STATEABBRV = readr::col_character(),
    STATEFIPS = readr::col_character(),
    COUNTY = readr::col_character(),
    COUNTYTYPE = readr::col_character(),
    COUNTYFIPS = readr::col_character(),
    STCOFIPS = readr::col_character(),
    NRI_VER = readr::col_character()
  )

  if (has_tract_fields) {
    base_col_types$TRACT <- readr::col_character()
    base_col_types$TRACTFIPS <- readr::col_character()
  }

  readr::read_csv(
    csv_path,
    col_types = do.call(readr::cols, c(base_col_types, list(.default = readr::col_guess()))),
    guess_max = 5000,
    show_col_types = FALSE,
    progress = FALSE
  ) %>%
    janitor::clean_names()
}

normalize_fema_geography <- function(df, geo_level) {
  df %>%
    mutate(
      nri_release_year = nri_release_year,
      nri_geo_level = geo_level,
      stcofips = stringr::str_pad(.data$stcofips, width = 5, side = "left", pad = "0"),
      statefips = stringr::str_pad(.data$statefips, width = 2, side = "left", pad = "0"),
      countyfips = stringr::str_pad(.data$countyfips, width = 3, side = "left", pad = "0"),
      countytype = dplyr::na_if(.data$countytype, ""),
      across(
        .cols = c(state, stateabbrv, county, countytype, nri_ver),
        .fns = ~ iconv(.x, from = "", to = "UTF-8", sub = "")
      )
    ) %>%
    {
      if (identical(geo_level, "tract")) {
        mutate(
          .,
          tract = dplyr::na_if(.data$tract, ""),
          tractfips = stringr::str_pad(dplyr::na_if(.data$tractfips, ""), width = 11, side = "left", pad = "0")
        )
      } else {
        .
      }
    }
}

validate_county_staging <- function(df) {
  invalid_stcofips_rows <- df %>%
    filter(is.na(.data$stcofips) | !stringr::str_detect(.data$stcofips, "^\\d{5}$"))

  if (nrow(invalid_stcofips_rows) > 0) {
    stop(
      glue("FEMA NRI county staging contains {nrow(invalid_stcofips_rows)} rows with invalid county-equivalent GEOIDs in STCOFIPS."),
      call. = FALSE
    )
  }

  duplicate_rows <- df %>%
    count(.data$stcofips, name = "n") %>%
    filter(.data$n > 1)

  if (nrow(duplicate_rows) > 0) {
    stop(
      glue("FEMA NRI county staging is not unique at county-equivalent STCOFIPS. Duplicate keys found: {nrow(duplicate_rows)}"),
      call. = FALSE
    )
  }

  nri_id_mismatch_rows <- df %>%
    filter(!is.na(.data$nri_id) & .data$nri_id != paste0("C", .data$stcofips))

  if (nrow(nri_id_mismatch_rows) > 0) {
    stop(
      glue("FEMA NRI county staging contains {nrow(nri_id_mismatch_rows)} rows where NRI_ID does not match C + STCOFIPS."),
      call. = FALSE
    )
  }
}

validate_tract_staging <- function(df) {
  invalid_stcofips_rows <- df %>%
    filter(is.na(.data$stcofips) | !stringr::str_detect(.data$stcofips, "^\\d{5}$"))

  if (nrow(invalid_stcofips_rows) > 0) {
    stop(
      glue("FEMA NRI tract staging contains {nrow(invalid_stcofips_rows)} rows with invalid county-equivalent GEOIDs in STCOFIPS."),
      call. = FALSE
    )
  }

  invalid_tractfips_rows <- df %>%
    filter(is.na(.data$tractfips) | !stringr::str_detect(.data$tractfips, "^\\d{11}$"))

  if (nrow(invalid_tractfips_rows) > 0) {
    stop(
      glue("FEMA NRI tract staging contains {nrow(invalid_tractfips_rows)} rows with invalid tract GEOIDs in TRACTFIPS."),
      call. = FALSE
    )
  }

  duplicate_rows <- df %>%
    count(.data$tractfips, name = "n") %>%
    filter(.data$n > 1)

  if (nrow(duplicate_rows) > 0) {
    stop(
      glue("FEMA NRI tract staging is not unique at TRACTFIPS. Duplicate keys found: {nrow(duplicate_rows)}"),
      call. = FALSE
    )
  }

  nri_id_mismatch_rows <- df %>%
    filter(!is.na(.data$nri_id) & .data$nri_id != paste0("T", .data$tractfips))

  if (nrow(nri_id_mismatch_rows) > 0) {
    stop(
      glue("FEMA NRI tract staging contains {nrow(nri_id_mismatch_rows)} rows where NRI_ID does not match T + TRACTFIPS."),
      call. = FALSE
    )
  }
}

materialize_staging_table <- function(df, table_name) {
  drv <- duckdb::duckdb()
  con <- DBI::dbConnect(drv, dbdir = db_path, read_only = FALSE)
  DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

  tmp_name <- paste0(table_name, "_", as.integer(Sys.time()))
  registered_tmp <- FALSE

  tryCatch(
    {
      duckdb::duckdb_register(con, tmp_name, as.data.frame(df))
      registered_tmp <- TRUE

      DBI::dbExecute(con, sprintf("DROP TABLE IF EXISTS staging.%s", table_name))
      DBI::dbExecute(
        con,
        sprintf(
          "CREATE TABLE staging.%s AS SELECT * FROM %s",
          table_name,
          DBI::dbQuoteIdentifier(con, tmp_name)
        )
      )
    },
    finally = {
      if (registered_tmp && DBI::dbIsValid(con)) {
        duckdb::duckdb_unregister(con, tmp_name)
      }

      if (DBI::dbIsValid(con)) {
        DBI::dbDisconnect(con, shutdown = TRUE)
      }
    }
  )
}

# 3. Download and extract the county and tract releases ----
download_fema_zip(county_zip_url, county_zip_path)
download_fema_zip(tract_zip_url, tract_zip_path)

extract_fema_members(
  zip_path = county_zip_path,
  member_names = c(county_csv_name, dictionary_name, hazard_info_name, metadata_pdf_name),
  exdir = raw_dir
)

extract_fema_members(
  zip_path = tract_zip_path,
  member_names = c(tract_csv_name, dictionary_name, hazard_info_name, metadata_pdf_name),
  exdir = raw_dir
)

county_csv_path <- file.path(raw_dir, county_csv_name)
tract_csv_path <- file.path(raw_dir, tract_csv_name)

# 4. Read both CSVs source-faithfully ----
fema_county_raw <- read_fema_csv(
  csv_path = county_csv_path,
  has_tract_fields = FALSE
)

fema_tract_raw <- read_fema_csv(
  csv_path = tract_csv_path,
  has_tract_fields = TRUE
)

fema_nri_staging <- normalize_fema_geography(
  df = fema_county_raw,
  geo_level = "county"
)

fema_nri_tract_staging <- normalize_fema_geography(
  df = fema_tract_raw,
  geo_level = "tract"
)

# 5. Validate the county and tract contracts ----
validate_county_staging(fema_nri_staging)
validate_tract_staging(fema_nri_tract_staging)

countytype_profile <- fema_nri_staging %>%
  mutate(countytype = coalesce(.data$countytype, "<blank>")) %>%
  count(.data$countytype, sort = TRUE)

message("FEMA NRI county-equivalent COUNTYTYPES observed:")
purrr::walk2(
  countytype_profile$countytype,
  countytype_profile$n,
  ~ message(" - ", .x, ": ", scales::comma(.y))
)

# 6. Materialize the wide county and tract staging tables ----
materialize_staging_table(
  df = fema_nri_staging,
  table_name = "fema_nri"
)

materialize_staging_table(
  df = fema_nri_tract_staging,
  table_name = "fema_nri_tract"
)
