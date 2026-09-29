# Publish the validated county OD pilot. The fact table contains observed flows;
# the companion coverage table tells consumers when an absent flow is unknown
# because a provider asset was unavailable rather than a genuine zero.

source(here::here("foundations", "etl", "utils.R"))
if (file.exists(".Renviron")) readRenviron(".Renviron")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = get_env_path("DB_PATH"), read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS silver;")
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

county_ref <- DBI::dbGetQuery(
  con,
  "SELECT DISTINCT state_fip, county_fip, county_name FROM silver.xwalk_tract_county"
) %>% dplyr::transmute(
  county_geoid = stringr::str_c(as.character(.data$state_fip), as.character(.data$county_fip)),
  county_name = .data$county_name
)

od <- DBI::dbGetQuery(con, "SELECT * FROM staging.lehd_lodes_od_county") %>%
  dplyr::mutate(home_county_geoid = as.character(.data$home_county_geoid), work_county_geoid = as.character(.data$work_county_geoid)) %>%
  dplyr::left_join(county_ref %>% dplyr::rename(home_county_geoid = .data$county_geoid, home_county_name = .data$county_name), by = "home_county_geoid") %>%
  dplyr::left_join(county_ref %>% dplyr::rename(work_county_geoid = .data$county_geoid, work_county_name = .data$county_name), by = "work_county_geoid") %>%
  dplyr::mutate(
    home_county_geography_status = dplyr::if_else(is.na(.data$home_county_name), "unmapped_provider_county", "matched"),
    work_county_geography_status = dplyr::if_else(is.na(.data$work_county_name), "unmapped_provider_county", "matched")
  )

if (any(od$work_county_geography_status != "matched")) stop("OD staging contains workplaces outside the managed geography backbone.", call. = FALSE)
if (anyDuplicated(od[c("home_county_geoid", "work_county_geoid", "year", "source_state", "source_part")]) > 0) stop("OD Silver grain is not unique.", call. = FALSE)
if (any(od$jobs_all < 0, na.rm = TRUE) || any(od$jobs_private < 0, na.rm = TRUE)) stop("OD Silver contains negative job counts.", call. = FALSE)

coverage <- DBI::dbGetQuery(con, "SELECT * FROM staging.lehd_lodes_od_coverage")
if (any(coverage$coverage_status == "available_validated" & !coverage$reconciliation_passed)) stop("OD coverage has an unresolved available source asset.", call. = FALSE)

DBI::dbWriteTable(con, DBI::Id(schema = "silver", table = "lehd_lodes_od_county"), od, overwrite = TRUE)
DBI::dbWriteTable(con, DBI::Id(schema = "silver", table = "lehd_lodes_od_coverage"), coverage, overwrite = TRUE)
DBI::dbExecute(con, "CHECKPOINT")
