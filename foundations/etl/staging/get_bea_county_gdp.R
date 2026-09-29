# Stage BEA county GDP and national price indexes for county-first CBSA GDP.
# The bulk CAGDP2 archive is used instead of hundreds of API calls so a run is
# reproducible from one versioned BEA release and captures the full 2024 county
# vintage. Direct CBSA CAGDP9 is deliberately not a production staging input.

source(here::here("foundations", "etl", "utils.R"))
if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")
bea_key <- get_env_path("BEA_KEY")
data_root <- get_env_path("DATA")
raw_dir <- file.path(data_root, "economics", "raw", "bea")
dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)

cagdp2_url <- "https://apps.bea.gov/regional/zip/CAGDP2.zip"
cagdp2_zip <- file.path(raw_dir, "CAGDP2_2026-02-05.zip")
retrieved_at <- format(Sys.time(), tz = "UTC", usetz = TRUE)
release_date <- as.Date("2026-02-05")
if (!file.exists(cagdp2_zip)) utils::download.file(cagdp2_url, cagdp2_zip, mode = "wb", quiet = TRUE)

# Keep only county GEOIDs. State and national summary rows are retained by the
# legacy staging path; production CBSA values below originate solely from this.
csv_name <- "CAGDP2__ALL_AREAS_2001_2024.csv"
raw <- readr::read_csv(unz(cagdp2_zip, csv_name), show_col_types = FALSE, name_repair = "minimal")
# BEA's bulk CSV includes a small number of legacy footnote bytes. Normalise
# them before DuckDB writes so an explanatory label cannot abort the refresh.
raw <- raw %>% dplyr::mutate(dplyr::across(where(is.character), ~ iconv(.x, from = "", to = "UTF-8", sub = "")))
year_cols <- names(raw)[stringr::str_detect(names(raw), "^[0-9]{4}$")]
county_stage <- raw %>%
  dplyr::mutate(
    geo_id = stringr::str_trim(stringr::str_remove_all(.data$GeoFIPS, '"')),
    line_code = as.character(.data$LineCode),
    geo_name = stringr::str_trim(.data$GeoName),
    line_desc_clean = stringr::str_squish(.data$Description)
  ) %>%
  dplyr::filter(stringr::str_detect(.data$geo_id, "^[0-9]{5}$"), .data$geo_id != "00000") %>%
  tidyr::pivot_longer(dplyr::all_of(year_cols), names_to = "period", values_to = "value_raw") %>%
  dplyr::transmute(
    code = paste0("CAGDP2-", .data$line_code), table = "CAGDP2", geo_level = "county",
    geo_id = .data$geo_id, geo_name = .data$geo_name, period = as.integer(.data$period),
    line_code = as.integer(.data$line_code), industry_classification = .data$IndustryClassification,
    line_desc_clean = .data$line_desc_clean, unit_raw = .data$Unit, unit_mult = 3L,
    value_raw = as.character(.data$value_raw),
    value = suppressWarnings(as.numeric(.data$value_raw)) * 1000,
    note_ref = dplyr::if_else(stringr::str_detect(.data$value_raw, "^\\("), .data$value_raw, NA_character_),
    source_url = cagdp2_url, provider_release_date = release_date, retrieved_at = retrieved_at
  )

# GDP-by-Industry table 11 is BEA's annual national chain-type value-added
# price index. jsonlite is used directly because bea.R currently drops this
# dataset's returned rows despite the API returning valid JSON.
price_url <- paste0("https://apps.bea.gov/api/data/?UserID=", bea_key,
                    "&method=GETDATA&datasetname=GDPbyIndustry&TableID=11&Frequency=A&Year=ALL&Industry=ALL&ResultFormat=JSON")
price_json <- jsonlite::fromJSON(price_url, simplifyDataFrame = TRUE)
# The API wraps Data in a one-row results data frame; extract that nested table
# rather than coercing the wrapper (which has an intentionally blank list name).
prices <- tibble::as_tibble(price_json$BEAAPI$Results$Data[[1]]) %>%
  dplyr::transmute(period = as.integer(.data$Year), industry = .data$Industry,
                   industry_description = stringr::str_squish(.data$IndustrYDescription),
                   price_index = as.numeric(.data$DataValue), source_url = price_url,
                   retrieved_at = retrieved_at)

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbWriteTable(con, DBI::Id(schema = "staging", table = "bea_regional_county_cagdp2"), county_stage, overwrite = TRUE)
DBI::dbWriteTable(con, DBI::Id(schema = "staging", table = "bea_gdp_industry_price_index"), prices, overwrite = TRUE)
DBI::dbExecute(con, "CHECKPOINT")
DBI::dbDisconnect(con, shutdown = TRUE)
