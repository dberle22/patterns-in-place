# In this script we keep the current CHR staging split in two:
#   * a source-faithful wide 2025 analytic table for full provider provenance
#   * a curated historical annual panel for 2016-2025 that keeps only the
#     county-level CHR fields we actually plan to model downstream

getwd()

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "demographics", "raw", "chr")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Catalogs and helpers ----
current_release_year <- 2025L
historical_release_years <- 2016:2025

chr_catalog_urls <- c(
  "https://www.countyhealthrankings.org/health-data/methodology-and-sources/data-documentation",
  "https://www.countyhealthrankings.org/health-data/methodology-and-sources/data-documentation/national-data-documentation-2010-2023"
)

wide_release_local_file <- file.path(raw_dir, "analytic_data2025_v3.csv")

history_measure_map <- c(
  life_expectancy = "life_expectancy_raw_value",
  premature_death_rate = "premature_death_raw_value",
  premature_age_adjusted_mortality = "premature_age_adjusted_mortality_raw_value",
  child_mortality_rate = "child_mortality_raw_value",
  infant_mortality_rate = "infant_mortality_raw_value",
  drug_overdose_death_rate = "drug_overdose_deaths_raw_value",
  poor_mental_health_days = "poor_mental_health_days_raw_value",
  adult_obesity = "adult_obesity_raw_value",
  physical_inactivity = "physical_inactivity_raw_value",
  pct_uninsured_adults = "uninsured_adults_raw_value",
  primary_care_ratio = "ratio_of_population_to_primary_care_physicians",
  mental_health_provider_ratio = "ratio_of_population_to_mental_health_providers",
  preventable_hospital_stay_rate = "preventable_hospital_stays_raw_value",
  food_insecurity_rate = "food_insecurity_raw_value",
  social_associations_per_10k = "social_associations_raw_value",
  child_care_cost_burden_rate = "child_care_cost_burden_raw_value",
  hs_graduation_rate = "high_school_graduation_raw_value",
  air_pollution_pm25 = "air_pollution_particulate_matter_raw_value",
  adverse_climate_events = "adverse_climate_events_raw_value",
  pct_access_to_parks = "access_to_parks_raw_value",
  homicide_rate = "homicides_raw_value",
  firearm_fatality_rate = "firearm_fatalities_raw_value",
  motor_vehicle_crash_rate = "motor_vehicle_crash_deaths_raw_value",
  reading_score_index = "reading_scores_raw_value",
  math_score_index = "math_scores_raw_value"
)

fetch_catalog_links <- function(catalog_url) {
  page <- httr::GET(
    catalog_url,
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(page)

  html <- httr::content(page, as = "text", encoding = "UTF-8")
  doc <- xml2::read_html(html)
  links <- xml2::xml_find_all(doc, ".//a")

  tibble::tibble(
    text = xml2::xml_text(links, trim = TRUE),
    href = xml2::xml_attr(links, "href")
  ) %>%
    filter(!is.na(.data$href), .data$href != "") %>%
    mutate(
      href = xml2::url_absolute(.data$href, catalog_url),
      catalog_url = catalog_url
    )
}

catalog_links <- purrr::map_dfr(chr_catalog_urls, fetch_catalog_links)

resolve_chr_analytic_url <- function(release_year, catalog_links) {
  target_text <- glue::glue("{release_year} CHR CSV Analytic Data")

  matched_url <- catalog_links %>%
    filter(.data$text == target_text) %>%
    pull(.data$href) %>%
    dplyr::first()

  if (!is.na(matched_url) && nzchar(matched_url)) {
    return(matched_url)
  }

  NA_character_
}

build_chr_fallback_urls <- function(release_year) {
  c(
    glue::glue("https://www.countyhealthrankings.org/sites/default/files/media/document/analytic_data{release_year}_v3.csv"),
    glue::glue("https://www.countyhealthrankings.org/sites/default/files/media/document/analytic_data{release_year}.csv"),
    glue::glue("https://www.countyhealthrankings.org/sites/default/files/media/document/analytic_data{release_year}_0.csv"),
    glue::glue("https://www.countyhealthrankings.org/sites/default/files/analytic_data{release_year}.csv"),
    glue::glue("https://www.countyhealthrankings.org/sites/default/files/analytic_data{release_year}_0.csv")
  ) %>%
    unique()
}

download_chr_file <- function(dest_path, release_year, catalog_links) {
  if (file.exists(dest_path)) {
    return(dest_path)
  }

  candidate_urls <- c(
    resolve_chr_analytic_url(release_year, catalog_links),
    build_chr_fallback_urls(release_year)
  ) %>%
    unique() %>%
    purrr::discard(~ is.na(.x) || !nzchar(.x))

  last_error <- NULL

  for (url in candidate_urls) {
    resp <- tryCatch(
      httr::GET(
        url,
        httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
      ),
      error = function(e) e
    )

    if (inherits(resp, "error")) {
      last_error <- resp
      next
    }

    if (httr::status_code(resp) == 200) {
      writeBin(httr::content(resp, "raw"), dest_path)
      return(dest_path)
    }

    last_error <- simpleError(
      glue::glue("HTTP {httr::status_code(resp)} for {url}")
    )
  }

  stop(
    glue::glue(
      "CHR download failed for release year {release_year}. Tried: {paste(candidate_urls, collapse = ', ')}. Last error: {conditionMessage(last_error)}"
    ),
    call. = FALSE
  )
}

read_chr_csv <- function(path) {
  readr::read_csv(
    path,
    guess_max = 5000,
    show_col_types = FALSE,
    progress = FALSE
  ) %>%
    janitor::clean_names()
}

pull_chr_column <- function(df, candidates, default = NA) {
  matched_name <- candidates[candidates %in% names(df)][1]

  if (is.na(matched_name)) {
    return(rep(default, nrow(df)))
  }

  df[[matched_name]]
}

normalize_chr_staging <- function(chr_raw) {
  chr_raw %>%
    mutate(
      state_fips = pull_chr_column(., c("state_fips_code")),
      county_fips = pull_chr_column(., c("county_fips_code")),
      fips5 = pull_chr_column(., c("x5_digit_fips_code")),
      state_abbr = pull_chr_column(., c("state_abbreviation")),
      county_name = pull_chr_column(., c("name")),
      release_year = suppressWarnings(
        as.integer(pull_chr_column(., c("release_year", "year")))
      ),
      county_clustered = suppressWarnings(
        as.integer(
          pull_chr_column(
            .,
            c("county_clustered_yes_1_no_0", "county_ranked_yes_1_no_0"),
            default = NA_integer_
          )
        )
      )
    ) %>%
    filter(.data$fips5 != "fipscode") %>%
    mutate(
      state_fips = stringr::str_pad(as.character(.data$state_fips), width = 2, side = "left", pad = "0"),
      county_fips = stringr::str_pad(as.character(.data$county_fips), width = 3, side = "left", pad = "0"),
      fips5 = stringr::str_pad(as.character(.data$fips5), width = 5, side = "left", pad = "0"),
      across(
        .cols = c(state_abbr, county_name),
        .fns = ~ iconv(.x, from = "", to = "UTF-8", sub = "")
      )
    )
}

check_chr_annual_key <- function(df, table_name) {
  invalid_fips_rows <- df %>%
    filter(is.na(.data$fips5) | !stringr::str_detect(.data$fips5, "^\\d{5}$"))

  if (nrow(invalid_fips_rows) > 0) {
    stop(
      glue::glue("{table_name} contains {nrow(invalid_fips_rows)} rows with invalid five-digit county FIPS."),
      call. = FALSE
    )
  }

  duplicate_rows <- df %>%
    count(.data$fips5, .data$release_year, name = "n") %>%
    filter(.data$n > 1)

  if (nrow(duplicate_rows) > 0) {
    stop(
      glue::glue("{table_name} is not unique at fips5 + release_year. Duplicate keys found: {nrow(duplicate_rows)}"),
      call. = FALSE
    )
  }
}

build_chr_history_slice <- function(chr_staging, release_year, measure_map) {
  available_source_columns <- intersect(unname(measure_map), names(chr_staging))
  chr_county <- chr_staging %>%
    filter(.data$county_fips != "000")

  history_slice <- chr_county %>%
    transmute(
      release_year = as.integer(.data$release_year),
      state_fips = as.character(.data$state_fips),
      county_fips = as.character(.data$county_fips),
      fips5 = as.character(.data$fips5),
      state_abbr = as.character(.data$state_abbr),
      county_name = as.character(.data$county_name),
      county_clustered = as.integer(.data$county_clustered)
    )

  for (target_name in names(measure_map)) {
    source_name <- measure_map[[target_name]]

    if (source_name %in% available_source_columns) {
      history_slice[[target_name]] <- as.double(chr_county[[source_name]])
    } else {
      history_slice[[target_name]] <- NA_real_
    }
  }

  history_slice %>%
    filter(dplyr::if_any(dplyr::all_of(names(measure_map)), ~ !is.na(.x))) %>%
    mutate(release_year = as.integer(release_year))
}

# 3. Download, normalize, and keep the wide 2025 release ----
download_chr_file(
  dest_path = wide_release_local_file,
  release_year = current_release_year,
  catalog_links = catalog_links
)

chr_wide_raw <- read_chr_csv(wide_release_local_file)
chr_wide_staging <- normalize_chr_staging(chr_wide_raw)

check_chr_annual_key(chr_wide_staging, "staging.chr_health_rankings")

# 4. Build the curated historical county panel ----
chr_history_staging <- purrr::map_dfr(
  historical_release_years,
  function(release_year) {
    local_file <- file.path(raw_dir, glue::glue("analytic_data{release_year}.csv"))

    download_chr_file(
      dest_path = local_file,
      release_year = release_year,
      catalog_links = catalog_links
    )

    chr_year_raw <- read_chr_csv(local_file)
    chr_year_staging <- normalize_chr_staging(chr_year_raw)

    check_chr_annual_key(chr_year_staging, glue::glue("staging.chr_health_rankings_history ({release_year})"))

    build_chr_history_slice(
      chr_staging = chr_year_staging,
      release_year = release_year,
      measure_map = history_measure_map
    )
  }
)

check_chr_annual_key(chr_history_staging, "staging.chr_health_rankings_history")

# 5. Materialize both staging tables ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "chr_health_rankings"),
  chr_wide_staging,
  overwrite = TRUE
)

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "chr_health_rankings_history"),
  chr_history_staging,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
