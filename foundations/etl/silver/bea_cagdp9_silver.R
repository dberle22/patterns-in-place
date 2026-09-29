# Build real county-first CBSA GDP -------------------------------------------
# CBSA CAGDP9 rows are not summed from county chained dollars. They are derived
# from county CAGDP2 plus BEA national industry prices using Fisher chaining.

source(here::here("foundations", "etl", "utils.R"))
source(here::here("foundations", "etl", "R", "bea_county_gdp.R"))
if (file.exists(".Renviron")) readRenviron(".Renviron")
con <- DBI::dbConnect(duckdb::duckdb(), dbdir = get_env_path("DB_PATH"), read_only = FALSE)

county_nominal <- DBI::dbGetQuery(con, "SELECT * FROM staging.bea_regional_county_cagdp2") %>%
  dplyr::mutate(geo_id = as.character(.data$geo_id), line_code = as.integer(.data$line_code))
prices <- DBI::dbGetQuery(con, "SELECT * FROM staging.bea_gdp_industry_price_index")
xwalk <- get_cbsa_rollup_xwalk(con) %>%
  dplyr::select(county_geoid, cbsa_code, cbsa_name)
line_ref <- DBI::dbGetQuery(con, "SELECT * FROM silver.bea_regional_metrics_ref WHERE \"table\" = 'CAGDP9'")

# CAGDP2's published classifications are coarser than the national price-table
# identifiers in a few industries. This is BEA's public industry mapping.
price_crosswalk <- tibble::tribble(
  ~line_code, ~industry,
  3L, "11", 6L, "21", 10L, "22", 11L, "23", 12L, "31G", 13L, "33DG",
  25L, "31ND", 34L, "42", 35L, "44RT", 36L, "48TW", 45L, "51", 51L, "52",
  56L, "53", 60L, "54", 64L, "55", 65L, "56", 69L, "61", 70L, "62",
  76L, "71", 79L, "72", 82L, "81", 83L, "92"
)

cbsa_cells <- county_nominal %>%
  dplyr::inner_join(xwalk, by = c("geo_id" = "county_geoid")) %>%
  dplyr::inner_join(price_crosswalk, by = "line_code") %>%
  dplyr::left_join(prices %>% dplyr::select(period, industry, price_index), by = c("period", "industry")) %>%
  dplyr::transmute(
    county_geoid = .data$geo_id, cbsa_code = .data$cbsa_code, cbsa_name = .data$cbsa_name,
    period = .data$period, line_code = .data$line_code, nominal_gdp = .data$value,
    price_index = .data$price_index
  )

derived <- bea_fisher_chain(cbsa_cells) %>%
  dplyr::left_join(line_ref %>% dplyr::select(line_code, metric_key, line_desc_clean), by = "line_code") %>%
  dplyr::transmute(
    table = "CAGDP9", code = paste0("CAGDP9-", .data$line_code), geo_level = "cbsa",
    geo_id = .data$cbsa_code, geo_name = .data$cbsa_name, period = .data$period,
    line_desc_clean = .data$line_desc_clean, metric_key = .data$metric_key,
    value = .data$real_gdp, source_vintage = "BEA CAGDP2 2026-02-05 + GDPbyIndustry table 11",
    derivation_method = "county_current_dollars_fisher_chain", missing_county_inputs = .data$missing_county_inputs
  )

# Preserve direct county and state CAGDP9 only at their native geographies.
# They are not joined into the CBSA derivation above and remain a benchmark.
native <- DBI::dbGetQuery(con, "SELECT * FROM staging.bea_regional_county_cagdp9 UNION ALL SELECT * FROM staging.bea_regional_state_cagdp9") %>%
  dplyr::mutate(line_code = as.character(.data$line_code)) %>%
  dplyr::left_join(line_ref, by = c("table" = "table", "line_code" = "line_code")) %>%
  dplyr::transmute(
    table, code, geo_level, geo_id, geo_name, period, line_desc_clean, metric_key, value,
    source_vintage = "BEA native CAGDP9 historical/native geography", derivation_method = "native_bea",
    missing_county_inputs = NA_integer_
  )

long_df <- dplyr::bind_rows(native, derived)
wide_df <- long_df %>%
  dplyr::select(geo_level, geo_id, geo_name, period, table, metric_key, value) %>%
  tidyr::pivot_wider(names_from = metric_key, values_from = value)

if (anyDuplicated(derived[c("geo_id", "period", "metric_key")])) stop("Derived CBSA GDP has duplicate keys.")
if (max(derived$period, na.rm = TRUE) < 2024L) stop("County-first CBSA GDP did not reach 2024.")
DBI::dbWriteTable(con, DBI::Id(schema = "silver", table = "bea_regional_cagdp9_long"), long_df, overwrite = TRUE)
DBI::dbWriteTable(con, DBI::Id(schema = "silver", table = "bea_regional_cagdp9_wide"), wide_df, overwrite = TRUE)
DBI::dbExecute(con, "CHECKPOINT")
DBI::dbDisconnect(con, shutdown = TRUE)
