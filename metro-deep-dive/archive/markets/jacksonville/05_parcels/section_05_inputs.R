source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

platform_helpers_path <- "notebooks/retail_opportunity_finder/data_platform/shared/platform_helpers.R"
if (!file.exists(platform_helpers_path)) {
  stop("Missing data platform helper file.", call. = FALSE)
}
source(platform_helpers_path)

load_section_05_duckdb_inputs <- function(con, profile = get_market_profile()) {
  required_tables <- c(
    "parcel.parcels_canonical",
    "parcel.parcel_join_qa",
    "parcel.retail_parcels",
    "ref.land_use_mapping"
  )

  required_exists <- vapply(required_tables, function(table_name) {
    parts <- strsplit(table_name, ".", fixed = TRUE)[[1]]
    duckdb_table_exists(con, parts[[1]], parts[[2]])
  }, logical(1))

  if (!all(required_exists)) {
    return(NULL)
  }

  market_key_sql <- DBI::dbQuoteString(con, profile$market_key)

  optional_tables <- c(
    "serving.retail_parcel_tract_assignment",
    "serving.retail_intensity_by_tract",
    "serving.parcel_zone_overlay",
    "serving.parcel_shortlist",
    "serving.parcel_shortlist_summary",
    "qa.market_serving_validation_results"
  )

  optional_exists <- vapply(optional_tables, function(table_name) {
    parts <- strsplit(table_name, ".", fixed = TRUE)[[1]]
    duckdb_table_exists(con, parts[[1]], parts[[2]])
  }, logical(1))

  list(
    parcels_canonical = DBI::dbGetQuery(
      con,
      paste0("SELECT * FROM parcel.parcels_canonical WHERE market_key = ", market_key_sql, " ORDER BY county_geoid, parcel_uid")
    ),
    parcel_join_qa = DBI::dbGetQuery(
      con,
      paste0("SELECT * FROM parcel.parcel_join_qa WHERE market_key = ", market_key_sql, " ORDER BY county_geoid")
    ),
    retail_parcels = DBI::dbGetQuery(
      con,
      paste0("SELECT * FROM parcel.retail_parcels WHERE market_key = ", market_key_sql, " ORDER BY county_geoid, parcel_uid")
    ),
    retail_mapping = DBI::dbGetQuery(
      con,
      "SELECT * FROM ref.land_use_mapping ORDER BY land_use_code"
    ),
    retail_parcel_tract_assignment = if (optional_exists[["serving.retail_parcel_tract_assignment"]]) DBI::dbGetQuery(
      con,
      paste0("SELECT * FROM serving.retail_parcel_tract_assignment WHERE market_key = ", market_key_sql, " ORDER BY tract_geoid, parcel_uid")
    ) else tibble::tibble(),
    retail_intensity_by_tract = if (optional_exists[["serving.retail_intensity_by_tract"]]) DBI::dbGetQuery(
      con,
      paste0("SELECT * FROM serving.retail_intensity_by_tract WHERE market_key = ", market_key_sql, " ORDER BY tract_geoid")
    ) else tibble::tibble(),
    parcel_zone_overlay = if (optional_exists[["serving.parcel_zone_overlay"]]) DBI::dbGetQuery(
      con,
      paste0("SELECT * FROM serving.parcel_zone_overlay WHERE market_key = ", market_key_sql, " ORDER BY zone_system, zone_order")
    ) else tibble::tibble(),
    parcel_shortlist = if (optional_exists[["serving.parcel_shortlist"]]) DBI::dbGetQuery(
      con,
      paste0("SELECT * FROM serving.parcel_shortlist WHERE market_key = ", market_key_sql, " ORDER BY zone_system, shortlist_rank_system")
    ) else tibble::tibble(),
    parcel_shortlist_summary = if (optional_exists[["serving.parcel_shortlist_summary"]]) DBI::dbGetQuery(
      con,
      paste0("SELECT * FROM serving.parcel_shortlist_summary WHERE market_key = ", market_key_sql, " ORDER BY zone_system, zone_id")
    ) else tibble::tibble(),
    market_serving_validation_results = if (optional_exists[["qa.market_serving_validation_results"]]) DBI::dbGetQuery(
      con,
      "SELECT * FROM qa.market_serving_validation_results ORDER BY check_name"
    ) else tibble::tibble()
  )
}
