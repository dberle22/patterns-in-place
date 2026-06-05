# In this script we land the official CDFI Fund list of designated Qualified
# Opportunity Zones as a tract-level staging table. The source list is static,
# but we keep a download step so the pipeline can rebuild from source without a
# manual file drop.

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "demographics", "raw", "opportunity_zones")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Download the current tract layer from the official CDFI ArcGIS service ----
oz_query_url <- paste0(
  "https://cimsprodprep.cdfifund.gov/arcgis/rest/services/PN/CIMS3_PN_View/MapServer/43/query",
  "?where=OZoneDesignated%3D%27Yes%27",
  "&outFields=CensusTractFIPS%2CStateName%2CCountyName%2COZoneDesignated%2CDataSource%2CNMTCQualified",
  "&returnGeometry=false&f=pjson"
)
oz_local_file <- file.path(raw_dir, "designated-qozs.json")

download_oz_payload <- function(query_url, dest_path) {
  if (file.exists(dest_path)) {
    return(dest_path)
  }

  resp <- httr::GET(
    query_url,
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)"),
    httr::config(ssl_verifypeer = 0L, ssl_verifyhost = 0L)
  )
  httr::stop_for_status(resp)

  writeLines(httr::content(resp, as = "text", encoding = "UTF-8"), dest_path, useBytes = TRUE)
  dest_path
}

# 3. Download and normalize the designation list ----
download_oz_payload(
  query_url = oz_query_url,
  dest_path = oz_local_file
)

oz_payload <- jsonlite::fromJSON(
  oz_local_file,
  simplifyVector = FALSE
)

oz_raw <- purrr::map_dfr(
  oz_payload$features,
  ~ tibble::as_tibble(.x$attributes)
) %>%
  janitor::clean_names()

oz_staging <- oz_raw %>%
  transmute(
    state_name = .data$state_name,
    county_name = .data$county_name,
    tract_geoid = stringr::str_pad(.data$census_tract_fips, width = 11, side = "left", pad = "0"),
    nmtc_qualified = .data$nmtc_qualified == "Yes",
    data_source = .data$data_source,
    is_opportunity_zone = .data$o_zone_designated == "Yes"
  ) %>%
  distinct()

# 4. Materialize the staging table ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "opportunity_zones"),
  oz_staging,
  overwrite = TRUE
)
