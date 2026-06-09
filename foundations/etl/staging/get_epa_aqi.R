# In this script we land EPA AirData annual AQI summaries as one source-faithful
# staging table that contains both county and CBSA rows. We keep the county
# name strings and CBSA identifiers exactly because Silver will own the county
# crosswalk and downstream standardization work.

getwd()

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "demographics", "raw", "epa", "aqi")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Define the annual ingest scope ----
aqi_years <- 2016:2025

download_epa_aqi_zip <- function(geo_level, year_value) {
  zip_name <- glue("annual_aqi_by_{geo_level}_{year_value}.zip")
  zip_path <- file.path(raw_dir, zip_name)

  if (!file.exists(zip_path)) {
    zip_url <- glue("https://aqs.epa.gov/aqsweb/airdata/{zip_name}")

    resp <- httr::GET(
      zip_url,
      httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
    )
    httr::stop_for_status(resp)

    writeBin(httr::content(resp, "raw"), zip_path)
  }

  zip_path
}

read_epa_aqi_zip <- function(zip_path, geo_level) {
  member_name <- stringr::str_replace(basename(zip_path), "\\.zip$", ".csv")

  readr::read_csv(
    unz(zip_path, member_name),
    col_types = readr::cols(.default = readr::col_guess()),
    show_col_types = FALSE,
    progress = FALSE
  ) %>%
    janitor::clean_names() %>%
    mutate(source_geo_level = geo_level)
}

normalize_epa_aqi <- function(df, geo_level) {
  if (identical(geo_level, "county")) {
    df %>%
      transmute(
        geo_level = "county",
        state_name = .data$state,
        county_name = .data$county,
        cbsa_name = NA_character_,
        cbsa_code = NA_character_,
        year = .data$year,
        days_with_aqi = suppressWarnings(as.integer(.data$days_with_aqi)),
        good_days = suppressWarnings(as.integer(.data$good_days)),
        moderate_days = suppressWarnings(as.integer(.data$moderate_days)),
        usg_days = suppressWarnings(as.integer(.data$unhealthy_for_sensitive_groups_days)),
        unhealthy_days = suppressWarnings(as.integer(.data$unhealthy_days)),
        very_unhealthy_days = suppressWarnings(as.integer(.data$very_unhealthy_days)),
        hazardous_days = suppressWarnings(as.integer(.data$hazardous_days)),
        max_aqi = suppressWarnings(as.integer(.data$max_aqi)),
        aqi_p90 = suppressWarnings(as.numeric(.data$x90th_percentile_aqi)),
        aqi_median = suppressWarnings(as.numeric(.data$median_aqi)),
        days_co = suppressWarnings(as.integer(.data$days_co)),
        days_no2 = suppressWarnings(as.integer(.data$days_no2)),
        days_ozone = suppressWarnings(as.integer(.data$days_ozone)),
        days_pm25 = suppressWarnings(as.integer(.data$days_pm2_5)),
        days_pm10 = suppressWarnings(as.integer(.data$days_pm10))
      )
  } else if (identical(geo_level, "cbsa")) {
    df %>%
      transmute(
        geo_level = "cbsa",
        state_name = NA_character_,
        county_name = NA_character_,
        cbsa_name = .data$cbsa,
        cbsa_code = stringr::str_pad(.data$cbsa_code, width = 5, side = "left", pad = "0"),
        year = .data$year,
        days_with_aqi = suppressWarnings(as.integer(.data$days_with_aqi)),
        good_days = suppressWarnings(as.integer(.data$good_days)),
        moderate_days = suppressWarnings(as.integer(.data$moderate_days)),
        usg_days = suppressWarnings(as.integer(.data$unhealthy_for_sensitive_groups_days)),
        unhealthy_days = suppressWarnings(as.integer(.data$unhealthy_days)),
        very_unhealthy_days = suppressWarnings(as.integer(.data$very_unhealthy_days)),
        hazardous_days = suppressWarnings(as.integer(.data$hazardous_days)),
        max_aqi = suppressWarnings(as.integer(.data$max_aqi)),
        aqi_p90 = suppressWarnings(as.numeric(.data$x90th_percentile_aqi)),
        aqi_median = suppressWarnings(as.numeric(.data$median_aqi)),
        days_co = suppressWarnings(as.integer(.data$days_co)),
        days_no2 = suppressWarnings(as.integer(.data$days_no2)),
        days_ozone = suppressWarnings(as.integer(.data$days_ozone)),
        days_pm25 = suppressWarnings(as.integer(.data$days_pm2_5)),
        days_pm10 = suppressWarnings(as.integer(.data$days_pm10))
      )
  } else {
    stop(glue("Unsupported EPA AQI geography: {geo_level}"), call. = FALSE)
  }
}

# 3. Read and row-bind the annual county and CBSA files ----
county_staging <- purrr::map_dfr(
  aqi_years,
  function(year_value) {
    message("Processing EPA AQI county file for year: ", year_value)

    zip_path <- download_epa_aqi_zip("county", year_value)

    read_epa_aqi_zip(zip_path, "county") %>%
      normalize_epa_aqi("county")
  }
)

cbsa_staging <- purrr::map_dfr(
  aqi_years,
  function(year_value) {
    message("Processing EPA AQI CBSA file for year: ", year_value)

    zip_path <- download_epa_aqi_zip("cbsa", year_value)

    read_epa_aqi_zip(zip_path, "cbsa") %>%
      normalize_epa_aqi("cbsa")
  }
)

# 4. Final staging shape and contract checks ----
epa_aqi_staging <- bind_rows(county_staging, cbsa_staging) %>%
  mutate(
    across(
      .cols = c(state_name, county_name, cbsa_name),
      .fns = ~ dplyr::if_else(is.na(.x), .x, stringr::str_squish(iconv(.x, from = "", to = "UTF-8", sub = "")))
    ),
    cbsa_code = dplyr::if_else(
      is.na(.data$cbsa_code) | .data$cbsa_code == "",
      NA_character_,
      stringr::str_pad(.data$cbsa_code, width = 5, side = "left", pad = "0")
    )
  )

invalid_geo_rows <- epa_aqi_staging %>%
  filter(
    (.data$geo_level == "county" & (is.na(.data$state_name) | is.na(.data$county_name))) |
      (.data$geo_level == "cbsa" & (is.na(.data$cbsa_name) | is.na(.data$cbsa_code)))
  )

if (nrow(invalid_geo_rows) > 0) {
  stop(
    glue("EPA AQI staging contains {nrow(invalid_geo_rows)} rows missing required source-native geography fields."),
    call. = FALSE
  )
}

invalid_day_rows <- epa_aqi_staging %>%
  filter(
    !is.na(.data$days_with_aqi) &
      (
        coalesce(.data$good_days, 0L) +
          coalesce(.data$moderate_days, 0L) +
          coalesce(.data$usg_days, 0L) +
          coalesce(.data$unhealthy_days, 0L) +
          coalesce(.data$very_unhealthy_days, 0L) +
          coalesce(.data$hazardous_days, 0L)
      ) != .data$days_with_aqi
  )

if (nrow(invalid_day_rows) > 0) {
  stop(
    glue("EPA AQI staging contains {nrow(invalid_day_rows)} rows where AQI bucket days do not sum to days_with_aqi."),
    call. = FALSE
  )
}

duplicate_rows <- epa_aqi_staging %>%
  mutate(
    geo_key = dplyr::case_when(
      .data$geo_level == "county" ~ paste(.data$state_name, .data$county_name, sep = " | "),
      .data$geo_level == "cbsa" ~ .data$cbsa_code,
      TRUE ~ NA_character_
    )
  ) %>%
  count(.data$geo_level, .data$geo_key, .data$year, name = "n") %>%
  filter(.data$n > 1)

if (nrow(duplicate_rows) > 0) {
  stop(
    glue("EPA AQI staging is not unique at geo_level + source geography key + year. Duplicate keys found: {nrow(duplicate_rows)}"),
    call. = FALSE
  )
}

# 5. Load the unified AQI staging table ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "epa_aqi"),
  epa_aqi_staging,
  overwrite = TRUE
)
