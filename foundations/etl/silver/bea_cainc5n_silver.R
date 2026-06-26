# In this script we turn staged BEA CAINC5N rows into a curated Silver table
# that matches what the source actually publishes.
#
# Key modeling choice:
# - BEA publishes broad industry detail as earnings rows.
# - BEA publishes wages, salaries, and supplements as all-industries totals.
# - We therefore keep one row per geography-year-industry bucket, with
#   `earnings_total` for the broad industry rows and the compensation
#   components populated only on the `all_industries` row.

getwd()

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")
db_path_override <- get_env_path("DB_PATH_OVERRIDE")

if (!is.na(db_path_override)) {
  db_path <- db_path_override
}

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
dbExecute(con, "CREATE SCHEMA IF NOT EXISTS silver;")

safe_sum <- function(x) {
  if (all(is.na(x))) return(NA_real_)
  sum(x, na.rm = TRUE)
}

safe_note_collapse <- function(x) {
  notes <- sort(unique(stats::na.omit(x)))
  if (length(notes) == 0) return(NA_character_)
  paste(notes, collapse = "; ")
}

industry_contract <- tibble::tribble(
  ~industry_key, ~industry_label, ~industry_rollup_family, ~industry_rollup_level, ~naics_raw, ~line_code, ~metric_slot,
  "all_industries", "All industries", "all_industries", "total", NA_character_, 35L, "earnings_total",
  "all_industries", "All industries", "all_industries", "total", NA_character_, 50L, "wages_salaries",
  "all_industries", "All industries", "all_industries", "total", NA_character_, 60L, "supplements",
  "all_industries", "All industries", "all_industries", "total", NA_character_, 61L, "pension_insurance_supplements",
  "all_industries", "All industries", "all_industries", "total", NA_character_, 62L, "govt_social_insurance_supplements",
  "all_industries", "All industries", "all_industries", "total", NA_character_, 70L, "proprietors_income",
  "private_nonfarm", "Private nonfarm", "private_nonfarm", "published_total", "113-814", 90L, "earnings_total",
  "ag_mining", "Agriculture, forestry, fishing, and mining", "ag_mining", "broad_family", "111-115,21", 81L, "earnings_total",
  "ag_mining", "Agriculture, forestry, fishing, and mining", "ag_mining", "broad_family", "111-115,21", 100L, "earnings_total",
  "ag_mining", "Agriculture, forestry, fishing, and mining", "ag_mining", "broad_family", "111-115,21", 200L, "earnings_total",
  "construction", "Construction", "construction", "broad_family", "23", 400L, "earnings_total",
  "manufacturing", "Manufacturing", "manufacturing", "broad_family", "31-33", 500L, "earnings_total",
  "wholesale", "Wholesale trade", "wholesale", "broad_family", "42", 600L, "earnings_total",
  "retail", "Retail trade", "retail", "broad_family", "44-45", 700L, "earnings_total",
  "transport_util", "Transportation, warehousing, and utilities", "transport_util", "broad_family", "22,48-49", 300L, "earnings_total",
  "transport_util", "Transportation, warehousing, and utilities", "transport_util", "broad_family", "22,48-49", 800L, "earnings_total",
  "information", "Information", "information", "broad_family", "51", 900L, "earnings_total",
  "finance_real", "Finance, insurance, and real estate", "finance_real", "broad_family", "52-53", 1000L, "earnings_total",
  "finance_real", "Finance, insurance, and real estate", "finance_real", "broad_family", "52-53", 1100L, "earnings_total",
  "professional", "Professional and business services", "professional", "broad_family", "54-56", 1200L, "earnings_total",
  "professional", "Professional and business services", "professional", "broad_family", "54-56", 1300L, "earnings_total",
  "professional", "Professional and business services", "professional", "broad_family", "54-56", 1400L, "earnings_total",
  "educ_health", "Education and health services", "educ_health", "broad_family", "61-62", 1500L, "earnings_total",
  "educ_health", "Education and health services", "educ_health", "broad_family", "61-62", 1600L, "earnings_total",
  "arts_accomm_food", "Arts, accommodation, and food services", "arts_accomm_food", "broad_family", "71-72", 1700L, "earnings_total",
  "arts_accomm_food", "Arts, accommodation, and food services", "arts_accomm_food", "broad_family", "71-72", 1800L, "earnings_total",
  "other_services", "Other services", "other_services", "broad_family", "81", 1900L, "earnings_total",
  "public_admin", "Government and government enterprises", "public_admin", "broad_family", NA_character_, 2000L, "earnings_total"
)

industry_ref <- industry_contract |>
  dplyr::group_by(
    .data$industry_key,
    .data$industry_label,
    .data$industry_rollup_family,
    .data$industry_rollup_level,
    .data$naics_raw
  ) |>
  dplyr::summarise(
    source_line_codes = paste(sort(unique(.data$line_code)), collapse = ","),
    .groups = "drop"
  )

# 2. Read staged inputs ----
stage_cainc5n <- DBI::dbGetQuery(con, "SELECT * FROM staging.bea_cainc5n") |>
  dplyr::mutate(
    dplyr::across(c("code", "table", "geo_level", "geo_id", "geo_name", "unit_raw", "data_value_text", "note_ref"), as.character),
    line_code = as.integer(.data$line_code),
    period = as.integer(.data$period),
    unit_mult = as.integer(.data$unit_mult),
    value_raw = as.numeric(.data$value_raw),
    value = as.numeric(.data$value),
    is_value_suppressed = as.logical(.data$is_value_suppressed)
  ) |>
  dplyr::mutate(
    geo_id = dplyr::case_when(
      .data$geo_level == "state" & nchar(.data$geo_id) == 5 ~ substr(.data$geo_id, 1, 2),
      .data$geo_level == "us" ~ "1",
      TRUE ~ .data$geo_id
    )
  )

cbsa_county_xwalk <- get_cbsa_rollup_xwalk(con) |>
  dplyr::select("county_geoid", "cbsa_code", "cbsa_name")

# 3. Build a source-true county/state/us industry table ----
curated_base <- stage_cainc5n |>
  dplyr::inner_join(industry_contract, by = "line_code") |>
  dplyr::group_by(
    .data$geo_level,
    .data$geo_id,
    .data$geo_name,
    .data$period,
    .data$table,
    .data$industry_key,
    .data$industry_label,
    .data$industry_rollup_family,
    .data$industry_rollup_level,
    .data$naics_raw,
    .data$metric_slot
  ) |>
  dplyr::summarise(
    value = safe_sum(.data$value),
    has_source_suppression = any(.data$is_value_suppressed, na.rm = TRUE),
    note_ref = safe_note_collapse(.data$note_ref),
    .groups = "drop"
  )

curated_wide <- curated_base |>
  tidyr::pivot_wider(
    names_from = "metric_slot",
    values_from = c("value", "has_source_suppression", "note_ref"),
    names_glue = "{metric_slot}__{.value}"
  ) |>
  dplyr::rename_with(
    ~ stringr::str_replace(.x, "__value$", ""),
    tidyselect::ends_with("__value")
  ) |>
  dplyr::rename_with(
    ~ paste0(stringr::str_replace(.x, "__has_source_suppression$", ""), "_suppressed"),
    tidyselect::ends_with("__has_source_suppression")
  ) |>
  dplyr::rename_with(
    ~ paste0(stringr::str_replace(.x, "__note_ref$", ""), "_note_ref"),
    tidyselect::ends_with("__note_ref")
  ) |>
  dplyr::left_join(industry_ref, by = c("industry_key", "industry_label", "industry_rollup_family", "industry_rollup_level", "naics_raw")) |>
  dplyr::mutate(
    compensation_total = dplyr::if_else(
      !is.na(.data$wages_salaries) | !is.na(.data$supplements),
      dplyr::coalesce(.data$wages_salaries, 0) + dplyr::coalesce(.data$supplements, 0),
      NA_real_
    ),
    has_source_suppression = dplyr::if_else(
      dplyr::coalesce(.data$earnings_total_suppressed, FALSE) |
        dplyr::coalesce(.data$wages_salaries_suppressed, FALSE) |
        dplyr::coalesce(.data$supplements_suppressed, FALSE) |
        dplyr::coalesce(.data$pension_insurance_supplements_suppressed, FALSE) |
        dplyr::coalesce(.data$govt_social_insurance_supplements_suppressed, FALSE) |
        dplyr::coalesce(.data$proprietors_income_suppressed, FALSE),
      TRUE,
      FALSE
    )
  ) |>
  dplyr::select(
    "geo_level", "geo_id", "geo_name", "period", "table",
    "industry_key", "industry_label", "industry_rollup_family", "industry_rollup_level",
    "naics_raw", "source_line_codes",
    "earnings_total", "compensation_total", "wages_salaries", "supplements",
    "pension_insurance_supplements", "govt_social_insurance_supplements",
    "proprietors_income", "has_source_suppression",
    "earnings_total_note_ref", "wages_salaries_note_ref", "supplements_note_ref",
    "pension_insurance_supplements_note_ref", "govt_social_insurance_supplements_note_ref",
    "proprietors_income_note_ref"
  )

county_rows <- curated_wide |>
  dplyr::filter(.data$geo_level == "county")

cbsa_rows <- county_rows |>
  dplyr::inner_join(cbsa_county_xwalk, by = c("geo_id" = "county_geoid")) |>
  dplyr::group_by(
    .data$period,
    .data$table,
    .data$industry_key,
    .data$industry_label,
    .data$industry_rollup_family,
    .data$industry_rollup_level,
    .data$naics_raw,
    .data$source_line_codes,
    .data$cbsa_code,
    .data$cbsa_name
  ) |>
  dplyr::summarise(
    earnings_total = safe_sum(.data$earnings_total),
    compensation_total = safe_sum(.data$compensation_total),
    wages_salaries = safe_sum(.data$wages_salaries),
    supplements = safe_sum(.data$supplements),
    pension_insurance_supplements = safe_sum(.data$pension_insurance_supplements),
    govt_social_insurance_supplements = safe_sum(.data$govt_social_insurance_supplements),
    proprietors_income = safe_sum(.data$proprietors_income),
    has_source_suppression = any(.data$has_source_suppression, na.rm = TRUE),
    .groups = "drop"
  ) |>
  dplyr::mutate(
    geo_level = "cbsa",
    geo_id = .data$cbsa_code,
    geo_name = .data$cbsa_name,
    earnings_total_note_ref = NA_character_,
    wages_salaries_note_ref = NA_character_,
    supplements_note_ref = NA_character_,
    pension_insurance_supplements_note_ref = NA_character_,
    govt_social_insurance_supplements_note_ref = NA_character_,
    proprietors_income_note_ref = NA_character_
  ) |>
  dplyr::select(
    "geo_level", "geo_id", "geo_name", "period", "table",
    "industry_key", "industry_label", "industry_rollup_family", "industry_rollup_level",
    "naics_raw", "source_line_codes",
    "earnings_total", "compensation_total", "wages_salaries", "supplements",
    "pension_insurance_supplements", "govt_social_insurance_supplements",
    "proprietors_income", "has_source_suppression",
    "earnings_total_note_ref", "wages_salaries_note_ref", "supplements_note_ref",
    "pension_insurance_supplements_note_ref", "govt_social_insurance_supplements_note_ref",
    "proprietors_income_note_ref"
  )

state_and_us_rows <- curated_wide |>
  dplyr::filter(.data$geo_level %in% c("state", "us"))

silver_cainc5n <- dplyr::bind_rows(
  county_rows,
  cbsa_rows,
  state_and_us_rows
) |>
  dplyr::arrange(.data$geo_level, .data$geo_id, .data$period, .data$industry_key)

duplicate_keys <- silver_cainc5n |>
  dplyr::count(.data$geo_level, .data$geo_id, .data$period, .data$industry_key, name = "row_count") |>
  dplyr::filter(.data$row_count > 1)

if (nrow(duplicate_keys) > 0) {
  stop("Duplicate geo_level + geo_id + period + industry_key rows found in silver.bea_cainc5n.", call. = FALSE)
}

# 4. Materialize to Silver ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "bea_cainc5n"),
  silver_cainc5n,
  overwrite = TRUE
)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)
