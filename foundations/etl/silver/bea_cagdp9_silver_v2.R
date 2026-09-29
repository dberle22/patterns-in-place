# Build county-first CBSA real GDP, BEA-method v2 ----------------------------
#
# This replaces neither the original v1 script nor its outputs until all
# acceptance gates pass. It implements BEA's published pseudo-leaf approach:
# a county uses detailed child industries only when every child is available in
# both adjacent years; otherwise it uses the available parent industry. Fisher
# terms are then calculated at those selected county-industry cells before
# aggregating to the CBSA.

source(here::here("foundations", "etl", "utils.R"))
if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")
con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# The tree matches the published CAGDP2 aggregate hierarchy. Leaves are the
# lowest public industry cells with national value-added price indexes.
children <- list(
  "1" = c("2", "83"), "2" = c("91", "92"), "12" = c("13", "25"),
  "50" = c("51", "56"), "59" = c("60", "64", "65"),
  "68" = c("69", "70"), "75" = c("76", "79"),
  "87" = c("3", "6"), "88" = c("34", "35"), "89" = c("10", "36"),
  "90" = c("12", "45"), "91" = c("3", "6", "11", "12"),
  "92" = c("10", "34", "35", "36", "45", "50", "59", "68", "75", "82")
)
price_industry <- c(
  # Table 11 includes both detailed industries and the aggregate fallbacks.
  # A suppressed detail must therefore retain the appropriate parent deflator.
  "1" = "GDP", "2" = "PVT", "3" = "11", "6" = "21", "10" = "22", "11" = "23",
  "12" = "31G", "13" = "33DG", "25" = "31ND", "34" = "42", "35" = "44RT",
  "36" = "48TW", "45" = "51", "50" = "FIRE", "51" = "52", "56" = "53",
  "59" = "PROF", "60" = "54", "64" = "55", "65" = "56", "68" = "6",
  "69" = "61", "70" = "62", "75" = "7", "76" = "71", "79" = "72",
  "82" = "81", "83" = "G", "87" = "ORE", "88" = "4A0", "89" = "ICT",
  "90" = "HS", "91" = "PGOOD", "92" = "PSERV"
)

nominal <- DBI::dbGetQuery(con, "SELECT geo_id AS county_geoid, period, line_code, value FROM staging.bea_regional_county_cagdp2") %>%
  dplyr::mutate(county_geoid = as.character(.data$county_geoid), line_code = as.character(.data$line_code))
xwalk <- get_cbsa_rollup_xwalk(con) %>% dplyr::select(county_geoid, cbsa_code, cbsa_name)
prices <- DBI::dbGetQuery(con, "SELECT period, industry, price_index FROM staging.bea_gdp_industry_price_index") %>%
  dplyr::mutate(industry = as.character(.data$industry))
line_ref <- DBI::dbGetQuery(con, "SELECT * FROM silver.bea_regional_metrics_ref WHERE \"table\" = 'CAGDP9'") %>%
  dplyr::mutate(line_code = as.character(.data$line_code))

# Return the deepest usable public cells for a target node and county-year.
# A child branch may itself fall back to an aggregate cell, so validate the
# final selected cells rather than only the immediate children.
choose_cells <- function(target, values_now, values_prior) {
  child_nodes <- children[[target]]
  if (is.null(child_nodes)) return(target)
  cells <- unlist(lapply(child_nodes, choose_cells,
                         values_now = values_now, values_prior = values_prior),
                  use.names = FALSE)
  cells_ok <- all(vapply(cells, function(node) {
    # Named vector indexing returns NA for an absent historical cell, whereas
    # [[ would throw for the first available year in a county series.
    !is.na(values_now[node][[1]]) && !is.na(values_prior[node][[1]])
  }, logical(1)))
  if (cells_ok) cells else target
}

base <- nominal %>%
  dplyr::inner_join(xwalk, by = "county_geoid") %>%
  dplyr::filter(.data$line_code %in% names(price_industry)) %>%
  dplyr::arrange(.data$county_geoid, .data$period, .data$line_code)

targets <- names(price_industry)

# Keep all years for one county together. This avoids repeatedly scanning the
# full 2.6m-row source for each county/year, while preserving the BEA rule.
county_panels <- split(base, base$county_geoid, drop = TRUE)
selected <- tibble::as_tibble(data.table::rbindlist(lapply(county_panels, function(county_rows) {
  years <- split(county_rows, county_rows$period, drop = TRUE)
  data.table::rbindlist(lapply(names(years), function(year_key) {
    year <- as.integer(year_key)
    now <- years[[year_key]]
    prior <- years[[as.character(year - 1L)]]
    now_values <- stats::setNames(now$value, now$line_code)
    prior_values <- if (is.null(prior)) numeric() else stats::setNames(prior$value, prior$line_code)
    chosen_cells <- lapply(targets, choose_cells, values_now = now_values, values_prior = prior_values)
    lengths <- lengths(chosen_cells)
    # Construct one compact block per county-year; rbindlist avoids millions
    # of tiny tibble allocations in this 1.5m-cell selection step.
    data.table::data.table(
      county_geoid = rep(now$county_geoid[[1]], sum(lengths)),
      period = rep(year, sum(lengths)),
      target_line = rep(targets, lengths),
      source_line = unlist(chosen_cells, use.names = FALSE)
    )
  }))
}), fill = TRUE))

# `selected` is already pair-specific: its cells were chosen using both year t
# and t-1. Join those two years directly, rather than lagging a line that may
# legitimately change from a detailed industry to its published fallback.
current_values <- base %>%
  dplyr::select(county_geoid, period, cbsa_code, cbsa_name, line_code, value_now = value)
prior_values <- base %>%
  dplyr::transmute(county_geoid, period = .data$period + 1L, line_code, value_prior = .data$value)
current_prices <- prices %>% dplyr::rename(price_now = price_index)
prior_prices <- prices %>%
  dplyr::transmute(period = .data$period + 1L, industry, price_prior = .data$price_index)

cells <- selected %>%
  dplyr::left_join(current_values,
                    by = c("county_geoid", "period", "source_line" = "line_code")) %>%
  dplyr::left_join(prior_values,
                    by = c("county_geoid", "period", "source_line" = "line_code")) %>%
  dplyr::mutate(industry = unname(price_industry[.data$source_line])) %>%
  dplyr::left_join(current_prices, by = c("period", "industry")) %>%
  dplyr::left_join(prior_prices, by = c("period", "industry")) %>%
  dplyr::mutate(
    # All four Fisher components use precisely the cells selected for this
    # adjacent-year comparison; no cross-period line identity is assumed.
    p1q1 = .data$value_now,
    p1q0 = .data$price_now * (.data$value_prior / .data$price_prior),
    p0q1 = .data$price_prior * (.data$value_now / .data$price_now),
    p0q0 = .data$value_prior
  )

aggregate_terms <- cells %>%
  dplyr::group_by(.data$cbsa_code, .data$cbsa_name, .data$target_line, .data$period) %>%
  dplyr::summarise(
    nominal_gdp = if (all(!is.na(.data$value_now))) sum(.data$value_now) else NA_real_,
    p1q1 = if (all(!is.na(.data$p1q1))) sum(.data$p1q1) else NA_real_,
    p1q0 = if (all(!is.na(.data$p1q0))) sum(.data$p1q0) else NA_real_,
    p0q1 = if (all(!is.na(.data$p0q1))) sum(.data$p0q1) else NA_real_,
    p0q0 = if (all(!is.na(.data$p0q0))) sum(.data$p0q0) else NA_real_,
    missing_county_inputs = sum(is.na(.data$value_now) | is.na(.data$value_prior)),
    .groups = "drop"
  ) %>%
  dplyr::mutate(fisher_relative = sqrt((.data$p1q1 / .data$p1q0) * (.data$p0q1 / .data$p0q0)))

chain_one <- function(df, reference_year = 2017L) {
  df <- dplyr::arrange(df, .data$period)
  reference <- which(df$period == reference_year)
  df$quantity_index <- NA_real_
  if (length(reference) != 1L || is.na(df$nominal_gdp[reference]) || df$nominal_gdp[reference] <= 0) return(df)
  df$quantity_index[reference] <- 100
  if (reference < nrow(df)) for (i in seq.int(reference + 1L, nrow(df))) df$quantity_index[i] <- df$quantity_index[i - 1L] * df$fisher_relative[i]
  if (reference > 1L) for (i in seq.int(reference - 1L, 1L)) df$quantity_index[i] <- df$quantity_index[i + 1L] / df$fisher_relative[i + 1L]
  df$real_gdp <- df$quantity_index / 100 * df$nominal_gdp[reference]
  df
}

derived <- aggregate_terms %>%
  dplyr::group_by(.data$cbsa_code, .data$target_line) %>%
  dplyr::group_modify(~ chain_one(.x)) %>%
  dplyr::ungroup() %>%
  dplyr::left_join(line_ref %>% dplyr::select(line_code, metric_key, line_desc_clean), by = c("target_line" = "line_code")) %>%
  dplyr::transmute(
    table = "CAGDP9", code = paste0("CAGDP9-", .data$target_line), geo_level = "cbsa",
    geo_id = .data$cbsa_code, geo_name = .data$cbsa_name, period = .data$period,
    line_desc_clean = .data$line_desc_clean, metric_key = .data$metric_key, value = .data$real_gdp,
    source_vintage = "BEA CAGDP2 2026-02-05 + GDPbyIndustry table 11",
    derivation_method = "county_pseudo_leaf_fisher_chain_v2", missing_county_inputs = .data$missing_county_inputs
  )

# Direct CBSA CAGDP9 is available only through 2023. Use it as a historical
# benchmark, never as an input to the county-first calculation or its 2024+ run.
direct_cbsa <- DBI::dbGetQuery(con, "
  SELECT geo_id, period, value AS direct_value
  FROM staging.bea_regional_cbsa_cagdp9
  WHERE line_code = '1' AND period BETWEEN 2017 AND 2023
") %>%
  dplyr::mutate(geo_id = as.character(.data$geo_id))
backtest <- derived %>%
  dplyr::filter(.data$metric_key == "real_gdp_total", .data$period %in% 2017:2023) %>%
  dplyr::select(.data$geo_id, .data$period, derived_value = .data$value) %>%
  dplyr::inner_join(direct_cbsa, by = c("geo_id", "period")) %>%
  dplyr::mutate(abs_pct_error = abs(.data$derived_value / .data$direct_value - 1))
backtest_summary <- backtest %>%
  dplyr::group_by(.data$period) %>%
  dplyr::summarise(
    matched_cbsas = dplyr::n(),
    mean_abs_pct_error = mean(.data$abs_pct_error, na.rm = TRUE),
    median_abs_pct_error = stats::median(.data$abs_pct_error, na.rm = TRUE),
    .groups = "drop"
  )

# Hard gates make a failed/incomplete calculation incapable of replacing Silver.
if (anyDuplicated(derived[c("geo_id", "period", "metric_key")])) stop("v2 derived CBSA GDP has duplicate keys.")
if (max(derived$period, na.rm = TRUE) < 2024L) stop("v2 derived CBSA GDP does not reach 2024.")
if (!"real_gdp_total" %in% derived$metric_key) stop("v2 did not derive real_gdp_total.")
# BEA's county GDP release excludes Puerto Rico. The 15 Puerto Rico CBSAs in
# the national crosswalk are consequently unavailable, leaving 920 supported
# CBSAs; keep that source-boundary explicit rather than imputing a rollup.
if (dplyr::n_distinct(derived$geo_id[derived$period == 2024L]) != 920L) stop("v2 2024 CBSA universe is not the 920 BEA-supported CBSAs.")
# The retained direct-CBSA extract covers a 385-CBSA historical sample (378
# current-code matches), not the full national universe. Seven years should
# yield more than 2,500 matched observations before it is accepted as a check.
if (nrow(backtest) < 2500L) stop("v2 historical benchmark did not match enough direct-CBSA observations.")
# Diagnostic mode retains a failed comparison for investigation, but never
# changes production. Normal materializations remain blocked by this gate.
benchmark_failed <- any(backtest_summary$mean_abs_pct_error > 0.03)
if (benchmark_failed && Sys.getenv("BEA_V2_DIAGNOSTIC_MODE") != "true") {
  stop("v2 historical benchmark exceeds the 3% mean absolute percent-error gate.")
}

# Do not write production tables until this v2 output is benchmarked. The
# review table keeps the result inspectable without changing existing consumers.
DBI::dbWriteTable(con, DBI::Id(schema = "silver", table = "bea_regional_cagdp9_v2_review_long"), derived, overwrite = TRUE)
DBI::dbWriteTable(con, DBI::Id(schema = "silver", table = "bea_regional_cagdp9_v2_backtest"), backtest, overwrite = TRUE)
DBI::dbWriteTable(con, DBI::Id(schema = "silver", table = "bea_regional_cagdp9_v2_backtest_summary"), backtest_summary, overwrite = TRUE)
DBI::dbExecute(con, "CHECKPOINT")
DBI::dbDisconnect(con, shutdown = TRUE)
