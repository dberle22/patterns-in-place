# In this script we normalize annual BFS county business-application rows into
# the first-pass Silver contract for county, CBSA, and state rollups.
#
# 1. Read staged annual county BFS rows and the geography crosswalks.
# 2. Standardize county rows and derive CBSA/state annual sums from counties.
# 3. Join CBP all-sector establishments where the annual denominator exists.
# 4. Materialize one annual `silver.bfs` analytical table.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

check_unique_annual_grain <- function(df, table_name) {
  dupes <- df %>%
    count(.data$geo_level, .data$geo_id, .data$period, .data$series_code, name = "row_count") %>%
    filter(.data$row_count > 1)

  if (nrow(dupes) > 0) {
    stop(
      sprintf(
        "%s has duplicate geo_level + geo_id + period + series_code rows",
        table_name
      ),
      call. = FALSE
    )
  }
}

append_state_abbr <- function(name, state_abbr) {
  dplyr::if_else(
    !is.na(state_abbr) & state_abbr != "" & !stringr::str_detect(name, ","),
    paste0(name, ", ", state_abbr),
    name
  )
}

summarize_bfs <- function(df, group_cols) {
  df %>%
    group_by(across(all_of(group_cols))) %>%
    summarize(
      business_applications = sum(.data$business_applications, na.rm = TRUE),
      .groups = "drop"
    )
}

# 1. Read staging and reference data ----
bfs_stage <- DBI::dbGetQuery(con, "SELECT * FROM staging.bfs_county") %>%
  mutate(
    year = as.integer(.data$year),
    state_abbr = as.character(.data$state_abbr),
    county_name = as.character(.data$county_name),
    county_fips = as.character(.data$county_fips),
    state_fips = as.character(.data$state_fips),
    county_fips_3 = as.character(.data$county_fips_3),
    series_code = as.character(.data$series_code)
  )

cbsa_county_xwalk <- DBI::dbGetQuery(
  con,
  "SELECT county_geoid, cbsa_code, cbsa_name FROM silver.xwalk_cbsa_county"
) %>%
  transmute(
    county_geoid = as.character(.data$county_geoid),
    cbsa_code = as.character(.data$cbsa_code),
    cbsa_name = as.character(.data$cbsa_name)
  ) %>%
  distinct()

county_state_xwalk <- DBI::dbGetQuery(
  con,
  "SELECT state_fip, county_geoid, county_name_long, state_abbr FROM silver.xwalk_county_state"
) %>%
  transmute(
    state_fips = as.character(.data$state_fip),
    county_geoid = as.character(.data$county_geoid),
    county_name_long = as.character(.data$county_name_long),
    state_abbr = as.character(.data$state_abbr)
  ) %>%
  distinct()

state_ref <- county_state_xwalk %>%
  distinct(.data$state_fips, .data$state_abbr)

cbp_total_estabs <- DBI::dbGetQuery(
  con,
  "
  SELECT
    lower(geo_level) AS geo_level,
    geo_id,
    period AS year,
    establishments AS cbp_total_estabs
  FROM silver.cbp
  WHERE is_total_row = TRUE
  "
) %>%
  transmute(
    geo_level = as.character(.data$geo_level),
    geo_id = as.character(.data$geo_id),
    year = as.integer(.data$year),
    cbp_total_estabs = as.double(.data$cbp_total_estabs)
  )

# 2. Standardize county rows ----
bfs_county <- bfs_stage %>%
  left_join(
    county_state_xwalk,
    by = c("county_fips" = "county_geoid", "state_fips")
  ) %>%
  transmute(
    geo_level = "county",
    geo_id = .data$county_fips,
    geo_name = append_state_abbr(
      dplyr::coalesce(.data$county_name_long, .data$county_name),
      dplyr::coalesce(.data$state_abbr.y, .data$state_abbr.x)
    ),
    period_type = "annual",
    period = .data$year,
    year = .data$year,
    state_fips = .data$state_fips,
    state_abbr = dplyr::coalesce(.data$state_abbr.y, .data$state_abbr.x),
    series_code = .data$series_code,
    series_label = "Business Applications",
    value = as.double(.data$business_applications),
    business_applications = as.double(.data$business_applications),
    source = "Census BFS"
  )

# 3. Derive CBSA and state rows from counties ----
bfs_cbsa <- bfs_county %>%
  inner_join(
    cbsa_county_xwalk,
    by = c("geo_id" = "county_geoid")
  ) %>%
  summarize_bfs(
    group_cols = c("cbsa_code", "cbsa_name", "period", "year", "series_code", "series_label")
  ) %>%
  transmute(
    geo_level = "cbsa",
    geo_id = .data$cbsa_code,
    geo_name = .data$cbsa_name,
    period_type = "annual",
    period = .data$period,
    year = .data$year,
    state_fips = NA_character_,
    state_abbr = NA_character_,
    series_code = .data$series_code,
    series_label = .data$series_label,
    value = .data$business_applications,
    business_applications = .data$business_applications,
    source = "Census BFS"
  )

bfs_state <- bfs_county %>%
  summarize_bfs(
    group_cols = c("state_fips", "period", "year", "series_code", "series_label")
  ) %>%
  left_join(
    state_ref,
    by = "state_fips"
  ) %>%
  transmute(
    geo_level = "state",
    geo_id = .data$state_fips,
    geo_name = .data$state_abbr,
    period_type = "annual",
    period = .data$period,
    year = .data$year,
    state_fips = .data$state_fips,
    state_abbr = .data$state_abbr,
    series_code = .data$series_code,
    series_label = .data$series_label,
    value = .data$business_applications,
    business_applications = .data$business_applications,
    source = "Census BFS"
  )

# 4. Add YoY and CBP denominator fields ----
bfs_silver <- bind_rows(
  bfs_county,
  bfs_cbsa,
  bfs_state
) %>%
  arrange(.data$geo_level, .data$geo_id, .data$period) %>%
  group_by(.data$geo_level, .data$geo_id, .data$series_code) %>%
  mutate(
    business_applications_yoy_pct = dplyr::if_else(
      dplyr::lag(.data$business_applications) > 0,
      (.data$business_applications / dplyr::lag(.data$business_applications)) - 1,
      NA_real_
    )
  ) %>%
  ungroup() %>%
  left_join(
    cbp_total_estabs,
    by = c("geo_level", "geo_id", "year")
  ) %>%
  mutate(
    business_application_rate_per_1000_establishments = dplyr::if_else(
      !is.na(.data$cbp_total_estabs) & .data$cbp_total_estabs > 0,
      (.data$business_applications / .data$cbp_total_estabs) * 1000.0,
      NA_real_
    )
  ) %>%
  select(
    .data$geo_level,
    .data$geo_id,
    .data$geo_name,
    .data$period_type,
    .data$period,
    .data$year,
    .data$state_fips,
    .data$state_abbr,
    .data$series_code,
    .data$series_label,
    .data$value,
    .data$business_applications,
    .data$business_applications_yoy_pct,
    .data$cbp_total_estabs,
    .data$business_application_rate_per_1000_establishments,
    .data$source
  ) %>%
  arrange(.data$geo_level, .data$geo_id, .data$period)

check_unique_annual_grain(bfs_silver, "silver.bfs")

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "bfs"),
  bfs_silver,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
