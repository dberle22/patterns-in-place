# In this script we land the County Health Rankings annual analytic CSV as one
# wide, source-faithful staging table. We keep the full measure inventory so
# downstream Silver work can choose the approved subset without re-ingesting the
# provider file.

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

# 2. Resolve the current analytic CSV URL ----
release_year <- 2025L
chr_catalog_url <- "https://www.countyhealthrankings.org/health-data/methodology-and-sources/data-documentation"
chr_fallback_urls <- c(
  "https://www.countyhealthrankings.org/sites/default/files/media/document/analytic_data2025_v3.csv",
  "https://www.countyhealthrankings.org/sites/default/files/media/document/analytic_data2025.csv"
)
chr_local_file <- file.path(raw_dir, "analytic_data2025_v3.csv")

resolve_chr_analytic_url <- function(catalog_url, release_year) {
  page <- httr::GET(
    catalog_url,
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(page)

  html <- httr::content(page, as = "text", encoding = "UTF-8")
  doc <- xml2::read_html(html)
  links <- xml2::xml_find_all(doc, ".//a")

  link_text <- xml2::xml_text(links, trim = TRUE)
  link_href <- xml2::xml_attr(links, "href")

  target_text <- glue("{release_year} CHR CSV Analytic Data")
  match_idx <- which(link_text == target_text)[1]

  if (is.na(match_idx)) {
    return(NA_character_)
  }

  xml2::url_absolute(link_href[[match_idx]], catalog_url)
}

download_chr_file <- function(catalog_url, fallback_urls, dest_path, release_year) {
  if (file.exists(dest_path)) {
    return(dest_path)
  }

  candidate_urls <- c(
    resolve_chr_analytic_url(catalog_url, release_year),
    fallback_urls
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
      glue("HTTP {httr::status_code(resp)} for {url}")
    )
  }

  stop(
    glue(
      "CHR download failed for release year {release_year}. Tried: {paste(candidate_urls, collapse = ', ')}. Last error: {conditionMessage(last_error)}"
    ),
    call. = FALSE
  )
}

# 3. Download and normalize the analytic CSV ----
download_chr_file(
  catalog_url = chr_catalog_url,
  fallback_urls = chr_fallback_urls,
  dest_path = chr_local_file,
  release_year = release_year
)

chr_raw <- readr::read_csv(
  chr_local_file,
  col_types = readr::cols(
    statecode = readr::col_character(),
    countycode = readr::col_character(),
    fipscode = readr::col_character(),
    state = readr::col_character(),
    county = readr::col_character(),
    year = readr::col_integer(),
    county_clustered = readr::col_integer(),
    .default = readr::col_guess()
  ),
  guess_max = 5000,
  show_col_types = FALSE,
  progress = FALSE
) %>%
  janitor::clean_names()

chr_staging <- chr_raw %>%
  rename(
    state_fips = state_fips_code,
    county_fips = county_fips_code,
    fips5 = x5_digit_fips_code,
    state_abbr = state_abbreviation,
    county_name = name,
    county_clustered = county_clustered_yes_1_no_0
  ) %>%
  filter(.data$fips5 != "fipscode") %>%
  mutate(
    state_fips = stringr::str_pad(.data$state_fips, width = 2, side = "left", pad = "0"),
    county_fips = stringr::str_pad(.data$county_fips, width = 3, side = "left", pad = "0"),
    fips5 = stringr::str_pad(.data$fips5, width = 5, side = "left", pad = "0"),
    across(
      .cols = c(state_abbr, county_name),
      .fns = ~ iconv(.x, from = "", to = "UTF-8", sub = "")
    )
  )

# 4. Validate the staged county key contract ----
invalid_fips_rows <- chr_staging %>%
  filter(is.na(.data$fips5) | !stringr::str_detect(.data$fips5, "^\\d{5}$"))

if (nrow(invalid_fips_rows) > 0) {
  stop(
    glue("CHR staging contains {nrow(invalid_fips_rows)} rows with invalid five-digit county FIPS."),
    call. = FALSE
  )
}

duplicate_rows <- chr_staging %>%
  count(.data$fips5, .data$release_year, name = "n") %>%
  filter(.data$n > 1)

if (nrow(duplicate_rows) > 0) {
  stop(
    glue("CHR staging is not unique at fips5 + release_year. Duplicate keys found: {nrow(duplicate_rows)}"),
    call. = FALSE
  )
}

# 5. Materialize the wide staging table ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "chr_health_rankings"),
  chr_staging,
  overwrite = TRUE
)
