# This script is a parallel staging prototype for EPA Smart Location Database
# ingestion through the ArcGIS REST service. It intentionally does not replace
# the current CSV-backed staging job yet. The goal is to let us validate whether
# REST-delivered identifiers repair the tract backbone before we merge this path
# into the main pipeline.

getwd()

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "transportation", "raw", "epa", "sld", "rest")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Define the current EPA REST source ----
sld_vintage_year <- 2021L
sld_service_url <- "https://geodata.epa.gov/arcgis/rest/services/OA/SmartLocationDatabase/MapServer/1/query"
sld_chunk_size <- 1000L

sld_keep_fields <- c(
  "OBJECTID",
  "GEOID10",
  "GEOID20",
  "STATEFP",
  "COUNTYFP",
  "TRACTCE",
  "BLKGRPCE",
  "CBSA",
  "CBSA_Name",
  "TotPop",
  "TotEmp",
  "CountHU",
  "HH",
  "Ac_Unpr",
  "NatWalkInd",
  "D2A_EPHHM",
  "D2B_E8MIXA",
  "D3B",
  "D3AAO",
  "D4B025",
  "D4D",
  "D4E",
  "D5AR",
  "D5AE",
  "D5BR",
  "D5BE",
  "D1C",
  "D1B",
  "D1A"
)

fetch_epa_sld_object_ids <- function(service_url) {
  # We first fetch only the object ids so the data pull can be chunked in a
  # deterministic way without relying on pagination behavior from the service.
  resp <- httr::GET(
    service_url,
    query = list(
      where = "1=1",
      returnIdsOnly = "true",
      f = "pjson"
    ),
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)

  payload <- jsonlite::fromJSON(
    httr::content(resp, as = "text", encoding = "UTF-8"),
    simplifyDataFrame = TRUE
  )

  object_ids <- payload$objectIds

  if (is.null(object_ids) || length(object_ids) == 0) {
    stop("EPA SLD REST query returned no object ids.", call. = FALSE)
  }

  as.integer(object_ids)
}

fetch_epa_sld_chunk <- function(service_url, object_ids, keep_fields) {
  # The REST service already exposes clean string identifiers, so we request
  # only the governed compact field set plus the geography helpers we need for
  # QA and tract recovery.
  resp <- httr::GET(
    service_url,
    query = list(
      objectIds = paste(object_ids, collapse = ","),
      returnGeometry = "false",
      outFields = paste(keep_fields, collapse = ","),
      f = "pjson"
    ),
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)

  payload <- jsonlite::fromJSON(
    httr::content(resp, as = "text", encoding = "UTF-8"),
    simplifyDataFrame = TRUE
  )

  attrs <- payload$features$attributes

  if (is.null(attrs) || nrow(attrs) == 0) {
    return(tibble::tibble())
  }

  tibble::as_tibble(attrs) %>%
    janitor::clean_names()
}

download_epa_sld_rest <- function(service_url, keep_fields, chunk_size) {
  object_ids <- fetch_epa_sld_object_ids(service_url)

  chunks <- split(
    object_ids,
    ceiling(seq_along(object_ids) / chunk_size)
  )

  purrr::map_dfr(seq_along(chunks), function(i) {
    message(glue("Fetching EPA SLD REST chunk {i} of {length(chunks)}"))
    fetch_epa_sld_chunk(service_url, chunks[[i]], keep_fields)
  })
}

normalize_epa_sld_rest <- function(df) {
  # The prototype keeps the same staging contract shape as the CSV path so we
  # can compare outputs cleanly. We use GEOID20 as the canonical staged block-
  # group key because it lines up better with the governed tract backbone in our
  # diagnostics, while still preserving GEOID10 for explicit vintage QA.
  df %>%
    transmute(
      year = sld_vintage_year,
      state_fips = stringr::str_pad(as.character(.data$statefp), width = 2, side = "left", pad = "0"),
      county_fips = stringr::str_pad(as.character(.data$countyfp), width = 3, side = "left", pad = "0"),
      tract_code = stringr::str_pad(as.character(.data$tractce), width = 6, side = "left", pad = "0"),
      block_group_code = stringr::str_pad(as.character(.data$blkgrpce), width = 1, side = "left", pad = "0"),
      bg_geoid = dplyr::if_else(
        is.na(.data$geoid20) | .data$geoid20 == "",
        NA_character_,
        stringr::str_pad(as.character(.data$geoid20), width = 12, side = "left", pad = "0")
      ),
      bg_geoid_2010 = dplyr::if_else(
        is.na(.data$geoid10) | .data$geoid10 == "",
        NA_character_,
        stringr::str_pad(as.character(.data$geoid10), width = 12, side = "left", pad = "0")
      ),
      bg_geoid_2020 = dplyr::if_else(
        is.na(.data$geoid20) | .data$geoid20 == "",
        NA_character_,
        stringr::str_pad(as.character(.data$geoid20), width = 12, side = "left", pad = "0")
      ),
      source_geoid10_raw = as.character(.data$geoid10),
      source_geoid20_raw = as.character(.data$geoid20),
      cbsa_code = dplyr::if_else(
        is.na(.data$cbsa) | .data$cbsa == "",
        NA_character_,
        stringr::str_pad(as.character(.data$cbsa), width = 5, side = "left", pad = "0")
      ),
      cbsa_name = dplyr::if_else(
        is.na(.data$cbsa_name) | .data$cbsa_name == "",
        NA_character_,
        stringr::str_squish(iconv(as.character(.data$cbsa_name), from = "", to = "UTF-8", sub = ""))
      ),
      total_population = as.numeric(.data$tot_pop),
      total_employment = as.numeric(.data$tot_emp),
      housing_units = as.numeric(.data$count_hu),
      households = as.numeric(.data$hh),
      land_acres_unprotected = as.numeric(.data$ac_unpr),
      walkability_index = as.numeric(.data$nat_walk_ind),
      employment_housing_mix = as.numeric(.data$d2a_ephhm),
      employment_mix = as.numeric(.data$d2b_e8mixa),
      street_intersection_density = as.numeric(.data$d3b),
      auto_oriented_intersection_share = as.numeric(.data$d3aao),
      transit_service_density = as.numeric(.data$d4b025),
      transit_frequency_peak = as.numeric(.data$d4d),
      distance_to_transit = as.numeric(.data$d4e),
      jobs_access_45min_transit = as.numeric(.data$d5ar),
      workers_access_45min_transit = as.numeric(.data$d5ae),
      jobs_access_45min_auto = as.numeric(.data$d5br),
      workers_access_45min_auto = as.numeric(.data$d5be),
      employment_density_gross = as.numeric(.data$d1c),
      population_density_gross = as.numeric(.data$d1b),
      housing_density_gross = as.numeric(.data$d1a)
    )
}

# 3. Download and normalize the current EPA REST release ----
epa_sld_rest_staging <- download_epa_sld_rest(
  service_url = sld_service_url,
  keep_fields = sld_keep_fields,
  chunk_size = sld_chunk_size
) %>%
  normalize_epa_sld_rest()

# 4. Contract checks ----
invalid_bg_rows <- epa_sld_rest_staging %>%
  filter(is.na(.data$bg_geoid) | !stringr::str_detect(.data$bg_geoid, "^\\d{12}$"))

if (nrow(invalid_bg_rows) > 0) {
  stop(
    glue("EPA SLD REST staging contains {nrow(invalid_bg_rows)} rows with invalid 12-digit block-group GEOIDs."),
    call. = FALSE
  )
}

invalid_state_rows <- epa_sld_rest_staging %>%
  filter(is.na(.data$state_fips) | !stringr::str_detect(.data$state_fips, "^\\d{2}$"))

if (nrow(invalid_state_rows) > 0) {
  stop(
    glue("EPA SLD REST staging contains {nrow(invalid_state_rows)} rows with invalid state FIPS values."),
    call. = FALSE
  )
}

invalid_county_rows <- epa_sld_rest_staging %>%
  filter(is.na(.data$county_fips) | !stringr::str_detect(.data$county_fips, "^\\d{3}$"))

if (nrow(invalid_county_rows) > 0) {
  stop(
    glue("EPA SLD REST staging contains {nrow(invalid_county_rows)} rows with invalid county FIPS values."),
    call. = FALSE
  )
}

invalid_tract_rows <- epa_sld_rest_staging %>%
  filter(is.na(.data$tract_code) | !stringr::str_detect(.data$tract_code, "^\\d{6}$"))

if (nrow(invalid_tract_rows) > 0) {
  stop(
    glue("EPA SLD REST staging contains {nrow(invalid_tract_rows)} rows with invalid tract codes."),
    call. = FALSE
  )
}

duplicate_rows <- epa_sld_rest_staging %>%
  count(.data$bg_geoid, name = "n") %>%
  filter(.data$n > 1)

if (nrow(duplicate_rows) > 0) {
  stop(
    glue("EPA SLD REST staging is not unique at bg_geoid. Duplicate keys found: {nrow(duplicate_rows)}"),
    call. = FALSE
  )
}

# 5. Load the prototype staging table ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "epa_sld_rest"),
  epa_sld_rest_staging,
  overwrite = TRUE
)
