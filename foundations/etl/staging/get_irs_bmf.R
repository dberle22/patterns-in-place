# In this script we land the latest IRS EO Business Master File snapshot as one
# national staging table. The first pass uses the four IRS regional CSVs as the
# raw surface, filters to active U.S. organization rows, preserves the key
# source classification fields, and derives `zip5` for downstream county
# allocation.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "social", "raw", "irs_bmf")
db_path <- get_env_path("DB_PATH")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS staging;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 1. Define the current IRS EO BMF assets ----
landing_page_url <- "https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf"
region_codes <- c("1", "2", "3", "4")
active_status_codes <- c("01", "02", "12", "25")
supported_states <- c(state.abb, "DC")

download_binary_asset <- function(url, dest_path) {
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

fetch_landing_page <- function(url) {
  resp <- httr::GET(
    url,
    httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)

  httr::content(resp, "text", encoding = "UTF-8")
}

extract_snapshot_metadata <- function(page_html) {
  date_match <- stringr::str_match(
    page_html,
    "Updated data posting date:\\s*<strong>([^<]+)</strong>"
  )

  count_match <- stringr::str_match(
    page_html,
    "Record Count:\\s*&nbsp;([0-9,]+)"
  )

  region_matches <- stringr::str_match_all(
    page_html,
    "/pub/irs-soi/(eo[1-4]\\.csv)"
  )[[1]]

  if (nrow(region_matches) == 0) {
    stop("Could not extract EO BMF regional CSV links from the IRS landing page.", call. = FALSE)
  }

  snapshot_date_raw <- date_match[, 2]
  snapshot_record_count_raw <- count_match[, 2]

  if (is.na(snapshot_date_raw) || !nzchar(snapshot_date_raw)) {
    stop("Could not extract the EO BMF snapshot posting date from the IRS landing page.", call. = FALSE)
  }

  snapshot_date <- format(as.Date(snapshot_date_raw, format = "%m/%d/%Y"), "%Y-%m-%d")

  if (is.na(snapshot_date)) {
    stop("EO BMF snapshot posting date could not be parsed into ISO format.", call. = FALSE)
  }

  tibble::tibble(
    snapshot_date = snapshot_date,
    snapshot_record_count = dplyr::if_else(
      !is.na(snapshot_record_count_raw) & nzchar(snapshot_record_count_raw),
      as.double(gsub(",", "", snapshot_record_count_raw)),
      NA_real_
    ),
    file_name = unique(region_matches[, 2])
  ) %>%
    mutate(
      region_code = stringr::str_extract(.data$file_name, "[1-4]"),
      source_url = paste0("https://www.irs.gov/pub/irs-soi/", .data$file_name)
    ) %>%
    arrange(.data$region_code)
}

read_irs_bmf_csv <- function(csv_path, snapshot_date, snapshot_record_count, region_code) {
  readr::read_csv(
    csv_path,
    col_types = readr::cols(
      .default = readr::col_character(),
      ASSET_AMT = readr::col_double(),
      INCOME_AMT = readr::col_double(),
      REVENUE_AMT = readr::col_double()
    ),
    show_col_types = FALSE,
    progress = FALSE
  ) %>%
    janitor::clean_names() %>%
    mutate(
      source_file = basename(csv_path),
      source_region = paste0("region_", region_code),
      snapshot_date = snapshot_date,
      snapshot_record_count = snapshot_record_count
    )
}

normalize_irs_bmf <- function(df) {
  df %>%
    transmute(
      ein = stringr::str_pad(as.character(.data$ein), width = 9, side = "left", pad = "0"),
      name = as.character(.data$name),
      ico = as.character(.data$ico),
      street = as.character(.data$street),
      city = as.character(.data$city),
      state = stringr::str_to_upper(as.character(.data$state)),
      zip_raw = as.character(.data$zip),
      zip5 = stringr::str_extract(as.character(.data$zip), "^\\d{5}"),
      group_exemption_number = as.character(.data$group),
      subsection_code = as.character(.data$subsection),
      affiliation_code = as.character(.data$affiliation),
      classification_codes = as.character(.data$classification),
      ruling_yyyymm = as.character(.data$ruling),
      ruling_year = suppressWarnings(as.integer(stringr::str_sub(as.character(.data$ruling), 1, 4))),
      deductibility_code = as.character(.data$deductibility),
      foundation_code = as.character(.data$foundation),
      activity_codes = as.character(.data$activity),
      organization_code = as.character(.data$organization),
      status_code = stringr::str_pad(as.character(.data$status), width = 2, side = "left", pad = "0"),
      tax_period_yyyymm = as.character(.data$tax_period),
      asset_code = as.character(.data$asset_cd),
      income_code = as.character(.data$income_cd),
      filing_requirement_code = stringr::str_pad(as.character(.data$filing_req_cd), width = 2, side = "left", pad = "0"),
      pf_filing_requirement_code = as.character(.data$pf_filing_req_cd),
      accounting_period_mm = stringr::str_pad(as.character(.data$acct_pd), width = 2, side = "left", pad = "0"),
      asset_amt = as.double(.data$asset_amt),
      income_amt = as.double(.data$income_amt),
      revenue_amt = as.double(.data$revenue_amt),
      ntee_cd = stringr::str_to_upper(as.character(.data$ntee_cd)),
      sort_name = as.character(.data$sort_name),
      source_region = as.character(.data$source_region),
      source_file = as.character(.data$source_file),
      snapshot_date = as.character(.data$snapshot_date),
      snapshot_record_count = as.double(.data$snapshot_record_count)
    ) %>%
    filter(
      .data$state %in% supported_states,
      .data$status_code %in% active_status_codes
    )
}

# 2. Download and normalize the current regional release ----
landing_page_html <- fetch_landing_page(landing_page_url)
snapshot_meta <- extract_snapshot_metadata(landing_page_html) %>%
  filter(.data$region_code %in% region_codes)

if (nrow(snapshot_meta) != length(region_codes)) {
  stop(
    sprintf(
      "Expected %s EO BMF regional files but extracted %s from the IRS landing page.",
      length(region_codes),
      nrow(snapshot_meta)
    ),
    call. = FALSE
  )
}

irs_bmf_staging <- purrr::pmap_dfr(
  list(snapshot_meta$source_url, snapshot_meta$file_name, snapshot_meta$snapshot_date, snapshot_meta$snapshot_record_count, snapshot_meta$region_code),
  function(source_url, file_name, snapshot_date, snapshot_record_count, region_code) {
    local_path <- file.path(raw_dir, file_name)

    download_binary_asset(source_url, local_path)

    read_irs_bmf_csv(
      csv_path = local_path,
      snapshot_date = snapshot_date,
      snapshot_record_count = snapshot_record_count,
      region_code = region_code
    ) %>%
      normalize_irs_bmf()
  }
)

# 3. Contract checks ----
invalid_state_rows <- irs_bmf_staging %>%
  filter(is.na(.data$state) | !.data$state %in% supported_states)

if (nrow(invalid_state_rows) > 0) {
  stop(
    glue("IRS BMF staging contains {nrow(invalid_state_rows)} rows outside the supported U.S. state/DC scope."),
    call. = FALSE
  )
}

invalid_status_rows <- irs_bmf_staging %>%
  filter(is.na(.data$status_code) | !.data$status_code %in% active_status_codes)

if (nrow(invalid_status_rows) > 0) {
  stop(
    glue("IRS BMF staging contains {nrow(invalid_status_rows)} rows outside the active-status keep set."),
    call. = FALSE
  )
}

invalid_zip_rows <- irs_bmf_staging %>%
  filter(!is.na(.data$zip_raw) & is.na(.data$zip5))

if (nrow(invalid_zip_rows) > 0) {
  stop(
    glue("IRS BMF staging contains {nrow(invalid_zip_rows)} rows with a raw ZIP value that does not yield a five-digit zip5."),
    call. = FALSE
  )
}

duplicate_eins <- irs_bmf_staging %>%
  count(.data$ein, name = "n") %>%
  filter(.data$n > 1)

if (nrow(duplicate_eins) > 0) {
  stop(
    glue("IRS BMF staging is not unique at EIN after regional row-bind. Duplicate EINs found: {nrow(duplicate_eins)}"),
    call. = FALSE
  )
}

snapshot_dates <- unique(irs_bmf_staging$snapshot_date)

if (length(snapshot_dates) != 1) {
  stop("IRS BMF staging landed multiple snapshot dates in one build.", call. = FALSE)
}

# 4. Load the normalized staging table ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "staging", table = "irs_bmf"),
  irs_bmf_staging,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
