# In this script we convert the latest IRS EO BMF staging snapshot into one
# static Silver table for county and CBSA nonprofit density metrics.
#
# 1. Read the staged active-organization rows and geography helpers.
# 2. Allocate each organization ZIP5 to counties with HUD ZIP-county weights.
# 3. Aggregate estimated organization counts to county and county-derived CBSA.
# 4. Join the latest ACS population denominator and materialize the static
#    nonprofit density metrics for social-fabric analysis.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS silver;")

on.exit(DBI::dbDisconnect(con, shutdown = FALSE), add = TRUE)

check_unique_grain <- function(df, table_name) {
  dupes <- df %>%
    count(.data$geo_level, .data$geo_id, name = "row_count") %>%
    filter(.data$row_count > 1)

  if (nrow(dupes) > 0) {
    stop(
      sprintf("%s has duplicate geo_level + geo_id rows", table_name),
      call. = FALSE
    )
  }
}

safe_ratio <- function(num, den) {
  if (is.na(den) || den <= 0) {
    return(NA_real_)
  }

  num / den
}

nonreligious_keep_flag <- function(ntee_cd, filing_requirement_code) {
  !(
    (!is.na(ntee_cd) & stringr::str_detect(ntee_cd, "^X")) |
      filing_requirement_code %in% c("06", "13")
  )
}

# 1. Read staging and geography helpers ----
irs_bmf_stage <- DBI::dbGetQuery(con, "SELECT * FROM staging.irs_bmf") %>%
  mutate(
    ein = as.character(.data$ein),
    state = as.character(.data$state),
    zip5 = as.character(.data$zip5),
    ntee_cd = as.character(.data$ntee_cd),
    filing_requirement_code = as.character(.data$filing_requirement_code),
    snapshot_date = as.character(.data$snapshot_date)
  )

message(sprintf("Loaded %s staged IRS BMF rows.", scales::comma(nrow(irs_bmf_stage))))

snapshot_dates <- unique(irs_bmf_stage$snapshot_date)
if (length(snapshot_dates) != 1) {
  stop("staging.irs_bmf contains multiple snapshot dates.", call. = FALSE)
}

zcta_county_xwalk <- DBI::dbGetQuery(
  con,
  "SELECT zip_geoid, county_geoid, rel_weight_pop, rel_weight_bus, rel_weight_hu FROM silver.xwalk_zcta_county"
) %>%
  transmute(
    zip5 = as.character(.data$zip_geoid),
    county_geoid = as.character(.data$county_geoid),
    rel_weight_pop = as.double(.data$rel_weight_pop),
    rel_weight_bus = as.double(.data$rel_weight_bus),
    rel_weight_hu = as.double(.data$rel_weight_hu)
  ) %>%
  group_by(.data$zip5) %>%
  mutate(
    bus_weight_sum = sum(dplyr::coalesce(.data$rel_weight_bus, 0), na.rm = TRUE),
    hu_weight_sum = sum(dplyr::coalesce(.data$rel_weight_hu, 0), na.rm = TRUE),
    pop_weight_sum = sum(dplyr::coalesce(.data$rel_weight_pop, 0), na.rm = TRUE),
    allocation_method = dplyr::case_when(
      .data$bus_weight_sum > 0 ~ "zip5_bus_ratio",
      .data$hu_weight_sum > 0 ~ "zip5_hu_ratio_fallback",
      .data$pop_weight_sum > 0 ~ "zip5_pop_ratio_fallback",
      TRUE ~ "unweighted_missing"
    ),
    allocation_weight = dplyr::case_when(
      .data$bus_weight_sum > 0 ~ .data$rel_weight_bus / .data$bus_weight_sum,
      .data$hu_weight_sum > 0 ~ .data$rel_weight_hu / .data$hu_weight_sum,
      .data$pop_weight_sum > 0 ~ .data$rel_weight_pop / .data$pop_weight_sum,
      TRUE ~ NA_real_
    )
  ) %>%
  ungroup()

county_lookup <- DBI::dbGetQuery(
  con,
  "SELECT state_fip, county_geoid, county_name_long, state_abbr FROM silver.xwalk_county_state"
) %>%
  transmute(
    county_geoid = as.character(.data$county_geoid),
    county_name_long = as.character(.data$county_name_long),
    state_fips = as.character(.data$state_fip),
    state_abbr = as.character(.data$state_abbr)
  ) %>%
  distinct()

cbsa_lookup <- DBI::dbGetQuery(
  con,
  "SELECT county_geoid, cbsa_code, cbsa_name FROM silver.xwalk_cbsa_county"
) %>%
  transmute(
    county_geoid = as.character(.data$county_geoid),
    cbsa_code = as.character(.data$cbsa_code),
    cbsa_name = as.character(.data$cbsa_name)
  ) %>%
  distinct()

population_year <- DBI::dbGetQuery(
  con,
  "SELECT MAX(year) AS max_year FROM silver.age_kpi WHERE geo_level IN ('county', 'cbsa')"
)$max_year[[1]]

population_lookup <- DBI::dbGetQuery(
  con,
  sprintf(
    "
    SELECT
      geo_level,
      geo_id,
      geo_name,
      year,
      pop_total
    FROM silver.age_kpi
    WHERE geo_level IN ('county', 'cbsa')
      AND year = %s
    ",
    population_year
  )
) %>%
  transmute(
    geo_level = as.character(.data$geo_level),
    geo_id = as.character(.data$geo_id),
    population_year = as.integer(.data$year),
    population_total = as.double(.data$pop_total)
  )

message(sprintf("Using ACS population year %s for county and CBSA denominators.", population_year))

# 2. Summarize organizations at ZIP5 before county allocation ----
irs_bmf_zip <- irs_bmf_stage %>%
  mutate(
    nonreligious_keep = nonreligious_keep_flag(.data$ntee_cd, .data$filing_requirement_code)
  ) %>%
  filter(!is.na(.data$zip5)) %>%
  group_by(.data$zip5, .data$snapshot_date) %>%
  summarise(
    nonprofit_org_count = dplyr::n(),
    nonprofit_org_count_nonreligious = sum(dplyr::if_else(.data$nonreligious_keep, 1, 0), na.rm = TRUE),
    .groups = "drop"
  )

message(sprintf("Summarized IRS BMF rows to %s ZIP5 groups.", scales::comma(nrow(irs_bmf_zip))))

zip_coverage_audit <- irs_bmf_stage %>%
  distinct(.data$zip5) %>%
  filter(!is.na(.data$zip5)) %>%
  left_join(
    zcta_county_xwalk %>%
      distinct(.data$zip5) %>%
      mutate(in_xwalk = TRUE),
    by = "zip5"
  ) %>%
  mutate(in_xwalk = dplyr::coalesce(.data$in_xwalk, FALSE))

org_zip_unmatched <- zip_coverage_audit %>%
  filter(!.data$in_xwalk)

if ((nrow(org_zip_unmatched) / nrow(zip_coverage_audit)) > 0.05) {
  stop(
    sprintf(
      "IRS BMF ZIP5-to-county coverage is too low for Silver promotion: %s of %s distinct ZIP5s are unmatched.",
      nrow(org_zip_unmatched),
      nrow(zip_coverage_audit)
    ),
    call. = FALSE
  )
}

zip_weight_audit <- zcta_county_xwalk %>%
  filter(!is.na(.data$allocation_weight), .data$allocation_weight > 0) %>%
  group_by(.data$zip5) %>%
  summarise(weight_sum = sum(.data$allocation_weight, na.rm = TRUE), .groups = "drop") %>%
  filter(abs(.data$weight_sum - 1) > 1e-6)

if (nrow(zip_weight_audit) > 0) {
  stop(
    sprintf(
      "IRS BMF ZIP5 allocation weights do not sum to 1 for %s ZIPs.",
      nrow(zip_weight_audit)
    ),
    call. = FALSE
  )
}

# 3. Allocate ZIP summaries to counties, then aggregate county and CBSA counts ----
irs_bmf_zip_allocated <- irs_bmf_zip %>%
  inner_join(
    zcta_county_xwalk %>%
      filter(!is.na(.data$allocation_weight), .data$allocation_weight > 0) %>%
      select("zip5", "county_geoid", "allocation_method", "allocation_weight"),
    by = "zip5"
  ) %>%
  mutate(
    nonprofit_org_count_est = .data$nonprofit_org_count * .data$allocation_weight,
    nonprofit_org_count_nonreligious_est = .data$nonprofit_org_count_nonreligious * .data$allocation_weight
  )

message(sprintf("Expanded ZIP summaries to %s ZIP-county allocation rows.", scales::comma(nrow(irs_bmf_zip_allocated))))

irs_bmf_county <- irs_bmf_zip_allocated %>%
  inner_join(county_lookup, by = "county_geoid") %>%
  group_by(.data$county_geoid, .data$county_name_long, .data$state_fips, .data$state_abbr) %>%
  summarise(
    geo_level = "county",
    geo_id = dplyr::first(.data$county_geoid),
    geo_name = dplyr::first(.data$county_name_long),
    snapshot_date = dplyr::first(.data$snapshot_date),
    nonprofit_org_count_est = sum(.data$nonprofit_org_count_est, na.rm = TRUE),
    nonprofit_org_count_nonreligious_est = sum(.data$nonprofit_org_count_nonreligious_est, na.rm = TRUE),
    source_zip5_count = n_distinct(.data$zip5),
    weight_method = dplyr::case_when(
      any(.data$allocation_method == "zip5_pop_ratio_fallback") ~ "zip5_bus_ratio_with_hu_pop_fallback",
      any(.data$allocation_method == "zip5_hu_ratio_fallback") ~ "zip5_bus_ratio_with_hu_fallback",
      TRUE ~ "zip5_bus_ratio"
    ),
    .groups = "drop"
  ) %>%
  left_join(
    population_lookup %>% filter(.data$geo_level == "county") %>% select(-.data$geo_level),
    by = c("geo_id")
  ) %>%
  mutate(
    nonprofits_per_100k = purrr::map2_dbl(.data$nonprofit_org_count_nonreligious_est, .data$population_total, \(n, p) safe_ratio(n * 100000, p)),
    nonprofits_total_per_100k = purrr::map2_dbl(.data$nonprofit_org_count_est, .data$population_total, \(n, p) safe_ratio(n * 100000, p))
  ) %>%
  select(
    .data$geo_level,
    .data$geo_id,
    .data$geo_name,
    .data$snapshot_date,
    .data$population_year,
    .data$population_total,
    .data$nonprofit_org_count_est,
    .data$nonprofit_org_count_nonreligious_est,
    .data$nonprofits_per_100k,
    .data$nonprofits_total_per_100k,
    .data$source_zip5_count,
    .data$weight_method
  )

message(sprintf("Aggregated nonprofit metrics to %s county rows.", scales::comma(nrow(irs_bmf_county))))

irs_bmf_cbsa <- irs_bmf_zip_allocated %>%
  inner_join(cbsa_lookup, by = "county_geoid") %>%
  group_by(.data$cbsa_code, .data$cbsa_name) %>%
  summarise(
    geo_level = "cbsa",
    geo_id = dplyr::first(.data$cbsa_code),
    geo_name = dplyr::first(.data$cbsa_name),
    snapshot_date = dplyr::first(.data$snapshot_date),
    nonprofit_org_count_est = sum(.data$nonprofit_org_count_est, na.rm = TRUE),
    nonprofit_org_count_nonreligious_est = sum(.data$nonprofit_org_count_nonreligious_est, na.rm = TRUE),
    source_zip5_count = n_distinct(.data$zip5),
    weight_method = dplyr::case_when(
      any(.data$allocation_method == "zip5_pop_ratio_fallback") ~ "zip5_bus_ratio_with_hu_pop_fallback",
      any(.data$allocation_method == "zip5_hu_ratio_fallback") ~ "zip5_bus_ratio_with_hu_fallback",
      TRUE ~ "zip5_bus_ratio"
    ),
    .groups = "drop"
  ) %>%
  left_join(
    population_lookup %>% filter(.data$geo_level == "cbsa") %>% select(-.data$geo_level),
    by = c("geo_id")
  ) %>%
  mutate(
    nonprofits_per_100k = purrr::map2_dbl(.data$nonprofit_org_count_nonreligious_est, .data$population_total, \(n, p) safe_ratio(n * 100000, p)),
    nonprofits_total_per_100k = purrr::map2_dbl(.data$nonprofit_org_count_est, .data$population_total, \(n, p) safe_ratio(n * 100000, p))
  ) %>%
  select(
    .data$geo_level,
    .data$geo_id,
    .data$geo_name,
    .data$snapshot_date,
    .data$population_year,
    .data$population_total,
    .data$nonprofit_org_count_est,
    .data$nonprofit_org_count_nonreligious_est,
    .data$nonprofits_per_100k,
    .data$nonprofits_total_per_100k,
    .data$source_zip5_count,
    .data$weight_method
  )

message(sprintf("Aggregated nonprofit metrics to %s CBSA rows.", scales::comma(nrow(irs_bmf_cbsa))))

# 4. Materialize the static Silver table ----
irs_bmf_silver <- bind_rows(
  irs_bmf_county,
  irs_bmf_cbsa
) %>%
  arrange(.data$geo_level, .data$geo_id)

check_unique_grain(irs_bmf_silver, "silver.irs_bmf")

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "irs_bmf"),
  irs_bmf_silver,
  overwrite = TRUE
)

message(sprintf("Wrote %s total rows to silver.irs_bmf.", scales::comma(nrow(irs_bmf_silver))))
