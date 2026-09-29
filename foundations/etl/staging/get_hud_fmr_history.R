# Stage HUD's historical county FMR file -------------------------------------
# HUD's all-bedroom history is a wide file indexed by a 10-digit state-county-
# county-subdivision code. The first five digits are the county GEOID used by
# Foundations. FMR is a fiscal-year schedule, so fiscal_year is preserved.

source(here::here("foundations", "etl", "utils.R"))
if (file.exists(".Renviron")) readRenviron(".Renviron")
db_path <- get_env_path("DB_PATH")
history_file <- file.path(get_env_path("DATA"), "demographics", "raw", "FMR_All_1983_2027.csv")
if (!file.exists(history_file)) stop("HUD FMR history file is required at: ", history_file)

history <- readr::read_csv(history_file, show_col_types = FALSE, col_types = readr::cols(.default = readr::col_character()))
years <- 2012:2027
fmr_columns <- unlist(lapply(years, function(year) paste0("fmr", substr(year, 3, 4), "_", 0:4)))
missing_columns <- setdiff(fmr_columns, names(history))
if (length(missing_columns) > 0) stop("HUD history is missing FMR columns: ", paste(missing_columns, collapse = ", "))

# The FY2023 landing table contains HUD's population field. Use it as the
# documented fixed population weight because the history file has no annual one.
con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
if (DBI::dbExistsTable(con, DBI::Id(schema = "staging", table = "hud_fmr_county"))) {
  pop_weights <- DBI::dbGetQuery(con, "SELECT county_geoid, max(pop_weight) AS pop_weight FROM staging.hud_fmr_county GROUP BY 1")
} else {
  # A failed replacement can leave the old staging table absent. Recover the
  # same 2020 HUD population weights directly from its cached FY2023 workbook.
  weight_file <- file.path(get_env_path("DATA"), "demographics", "raw", "hud", "fmr_county_2023.xlsx")
  if (!file.exists(weight_file)) stop("Need the cached FY2023 HUD county workbook for population weights: ", weight_file)
  pop_weights <- readxl::read_xlsx(weight_file) %>% janitor::clean_names() %>%
    dplyr::transmute(county_geoid = stringr::str_sub(as.character(.data$fips), 1, 5), pop_weight = as.numeric(.data$pop2020)) %>%
    dplyr::group_by(.data$county_geoid) %>% dplyr::summarise(pop_weight = max(.data$pop_weight, na.rm = TRUE), .groups = "drop")
}

county_fmr <- history %>%
  dplyr::mutate(
    county_geoid = stringr::str_sub(.data$fips2027, 1, 5),
    state_fips = stringr::str_sub(.data$county_geoid, 1, 2),
    county_name = .data$name,
    hud_area_name = .data$areaname27,
    hud_area_code = .data$msa27
  ) %>%
  dplyr::filter(stringr::str_detect(.data$county_geoid, "^[0-9]{5}$")) %>%
  dplyr::select(county_geoid, state_fips, county_name, hud_area_name, hud_area_code, dplyr::all_of(fmr_columns)) %>%
  tidyr::pivot_longer(dplyr::all_of(fmr_columns), names_to = c("year_code", "bedrooms"), names_pattern = "fmr(\\d{2})_(\\d)") %>%
  dplyr::mutate(fiscal_year = as.integer(paste0("20", .data$year_code)), bedrooms = as.integer(.data$bedrooms)) %>%
  dplyr::filter(.data$fiscal_year %in% years) %>%
  dplyr::mutate(value = suppressWarnings(as.numeric(.data$value))) %>%
  dplyr::select(-year_code) %>%
  tidyr::pivot_wider(names_from = bedrooms, values_from = value, names_prefix = "fmr_") %>%
  dplyr::rename(fmr_0br = fmr_0, fmr_1br = fmr_1, fmr_2br = fmr_2, fmr_3br = fmr_3, fmr_4br = fmr_4) %>%
  # HUD lists every county subdivision in several New England counties. Those
  # rows normally repeat the same county FMR; collapse only after retaining a
  # flag that makes any genuinely differing subdivision schedule fail loudly.
  dplyr::group_by(county_geoid, state_fips, fiscal_year) %>%
  dplyr::summarise(
    county_name = dplyr::first(.data$county_name), hud_area_name = dplyr::first(.data$hud_area_name),
    hud_area_code = dplyr::first(.data$hud_area_code),
    dplyr::across(dplyr::starts_with("fmr_"), ~ dplyr::first(.x)),
    conflicting_subdivision_values = max(vapply(dplyr::pick(dplyr::starts_with("fmr_")), dplyr::n_distinct, integer(1), na.rm = TRUE)),
    .groups = "drop"
  ) %>%
  { if (any(.$conflicting_subdivision_values > 1L)) stop("HUD history has conflicting FMR values within a county-year."); . } %>%
  dplyr::select(-conflicting_subdivision_values) %>%
  dplyr::left_join(pop_weights, by = "county_geoid") %>%
  dplyr::mutate(
    period = .data$fiscal_year, state_abbr = NA_character_, metro_flag = NA_integer_,
    source_url = "https://www.huduser.gov/portal/datasets/FMR/FMR_All_1983_2027.csv",
    source_vintage = "HUD FMR history file, downloaded 2026-09-24"
  ) %>%
  dplyr::select(county_geoid, state_fips, county_name, state_abbr, hud_area_name, hud_area_code,
                metro_flag, period, fiscal_year, fmr_0br, fmr_1br, fmr_2br, fmr_3br, fmr_4br,
                pop_weight, source_url, source_vintage)

if (anyDuplicated(county_fmr[c("county_geoid", "fiscal_year")])) stop("HUD FMR history has duplicate county-fiscal-year keys.")
# HUD's historical names include a few legacy bytes; normalize them before the
# DuckDB write so geographic labels cannot stop an otherwise valid refresh.
county_fmr <- county_fmr %>% dplyr::mutate(dplyr::across(where(is.character), ~ iconv(.x, from = "", to = "UTF-8", sub = "")))
DBI::dbWriteTable(con, DBI::Id(schema = "staging", table = "hud_fmr_county"), county_fmr, overwrite = TRUE)
DBI::dbExecute(con, "CHECKPOINT")
DBI::dbDisconnect(con, shutdown = TRUE)
