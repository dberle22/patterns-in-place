# Section 02 build script
# Purpose: data prep and core transformations for section 02_market_overview.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()
source("notebooks/retail_opportunity_finder/sections/02_market_overview/section_02_inputs.R")

message("Running section 02 build: 02_market_overview")

con <- connect_project_duckdb(read_only = TRUE)
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

market_profile <- get_market_profile()
market_context <- get_market_context()
market_profile_check <- validate_market_profile(market_profile)
if (!isTRUE(market_profile_check$pass)) {
  stop("Active market profile failed validation.", call. = FALSE)
}
section_output_dir <- resolve_market_output_dir("02_market_overview")

target_year <- TARGET_YEAR
target_cbsa_code <- TARGET_CBSA
target_cbsa_label <- market_label("cbsa_name", market_profile)
target_market_label <- market_label("market_name", market_profile)
target_flag_label <- market_label("target_flag", market_profile)
benchmark_region_type <- market_profile$benchmark_region_type
benchmark_region_value <- market_profile$benchmark_region_value
benchmark_region_label <- market_profile$benchmark_region_label
us_label <- market_label("us_label", market_profile)

section_inputs <- load_section_02_inputs(con, market_profile)
cbsa_features <- section_inputs$cbsa_features
assert_required_columns(cbsa_features, REQUIRED_COLUMNS$cbsa_features, "cbsa_features")

format_kpi_value <- function(x, type = c("num", "pct", "usd", "units", "mins")) {
  type <- match.arg(type)
  if (length(x) == 0 || all(is.na(x))) return(NA_character_)
  v <- x[1]
  if (type == "pct" && !is.na(v) && abs(v) > 1) v <- v / 100
  dplyr::case_when(
    type == "num" ~ scales::comma(v, accuracy = 1),
    type == "pct" ~ scales::percent(v, accuracy = 0.1),
    type == "usd" ~ scales::dollar(v, accuracy = 1),
    type == "units" ~ scales::number(v, accuracy = 0.1),
    type == "mins" ~ scales::number(v, accuracy = 0.1),
    TRUE ~ as.character(v)
  )
}

target_row <- cbsa_features %>%
  filter(cbsa_code == target_cbsa_code, year == target_year) %>%
  slice(1)

if (nrow(target_row) != 1) {
  stop(glue("Expected one target market row in cbsa_features for cbsa_code={target_cbsa_code}, year={target_year}."), call. = FALSE)
}

kpi_tiles <- target_row %>%
  transmute(
    cbsa_code,
    year,
    population = pop_total,
    pop_growth_5yr = pop_growth_5yr,
    units_per_1k_3yr = bps_units_per_1k_3yr_avg,
    median_rent = median_gross_rent,
    median_home_value = median_home_value,
    mean_commute_min = mean_travel_time
  ) %>%
  mutate(
    population_fmt = format_kpi_value(population, "num"),
    pop_growth_5yr_fmt = format_kpi_value(pop_growth_5yr, "pct"),
    units_per_1k_3yr_fmt = format_kpi_value(units_per_1k_3yr, "units"),
    median_rent_fmt = format_kpi_value(median_rent, "usd"),
    median_home_value_fmt = format_kpi_value(median_home_value, "usd"),
    mean_commute_min_fmt = paste0(format_kpi_value(mean_commute_min, "mins"), " min")
  )

peer_cbsa_codes <- market_profile$peers

peer_table <- cbsa_features %>%
  filter(cbsa_code %in% peer_cbsa_codes, year == target_year) %>%
  transmute(
    cbsa_code,
    metro_name = cbsa_name,
    pop_growth_5yr,
    pop_growth_rank = region_pop_growth_5yr_rank,
    units_per_1k_3yr = bps_units_per_1k_3yr_avg,
    units_per_1k_rank = region_units_1k_avg_rank,
    median_rent = median_gross_rent,
    median_rent_rank = region_gross_rent_rank,
    median_home_value,
    home_value_rank = region_home_value_rank,
    mean_travel_time = round(mean_travel_time, 2),
    mean_travel_time_rank = region_travel_time_rank,
    is_target_market = cbsa_code == target_cbsa_code
  )

target_bench <- target_row %>%
  transmute(
    geo_level = "metro",
    geo_name = cbsa_name,
    year,
    population = pop_total,
    pop_growth_5yr,
    units_per_1k_3yr = bps_units_per_1k_3yr_avg,
    median_gross_rent,
    median_home_value,
    mean_travel_time
  )

region_bench <- cbsa_features %>%
  filter(year == target_year, .data[[benchmark_region_type]] == benchmark_region_value) %>%
  summarise(
    geo_level = "region",
    geo_name = benchmark_region_label,
    year = target_year,
    population = mean(pop_total, na.rm = TRUE),
    pop_growth_5yr = weighted.mean(pop_growth_5yr, pop_total, na.rm = TRUE),
    units_per_1k_3yr = weighted.mean(bps_units_per_1k_3yr_avg, pop_total, na.rm = TRUE),
    median_gross_rent = weighted.mean(median_gross_rent, pop_total, na.rm = TRUE),
    median_home_value = weighted.mean(median_home_value, pop_total, na.rm = TRUE),
    mean_travel_time = weighted.mean(mean_travel_time, pop_total, na.rm = TRUE)
  )

us_bench <- cbsa_features %>%
  filter(year == target_year) %>%
  summarise(
    geo_level = "us",
    geo_name = us_label,
    year = target_year,
    population = mean(pop_total, na.rm = TRUE),
    pop_growth_5yr = weighted.mean(pop_growth_5yr, pop_total, na.rm = TRUE),
    units_per_1k_3yr = weighted.mean(bps_units_per_1k_3yr_avg, pop_total, na.rm = TRUE),
    median_gross_rent = weighted.mean(median_gross_rent, pop_total, na.rm = TRUE),
    median_home_value = weighted.mean(median_home_value, pop_total, na.rm = TRUE),
    mean_travel_time = weighted.mean(mean_travel_time, pop_total, na.rm = TRUE)
  )

 benchmark_table <- bind_rows(target_bench, region_bench, us_bench) %>%
  mutate(order = dplyr::case_when(
    geo_level == "metro" ~ 1L,
    geo_level == "region" ~ 2L,
    geo_level == "us" ~ 3L,
    TRUE ~ 99L
  )) %>%
  arrange(order) %>%
  select(-order)

region_vals <- benchmark_table %>% filter(geo_level == "region") %>% slice(1)
us_vals <- benchmark_table %>% filter(geo_level == "us") %>% slice(1)

benchmark_table <- benchmark_table %>%
  mutate(
    mean_travel_time = round(mean_travel_time, 2),
    target_vs_region_pop = if_else(geo_level == "metro", population / region_vals$population, NA_real_),
    target_vs_us_pop = if_else(geo_level == "metro", population / us_vals$population, NA_real_),
    target_vs_region_rent = if_else(geo_level == "metro", median_gross_rent / region_vals$median_gross_rent, NA_real_),
    target_vs_us_rent = if_else(geo_level == "metro", median_gross_rent / us_vals$median_gross_rent, NA_real_)
  )

pop_trend <- bind_rows(
  cbsa_features %>%
    filter(cbsa_code == target_cbsa_code) %>%
    transmute(geo = target_flag_label, year, population = as.numeric(pop_total)),
  cbsa_features %>%
    filter(.data[[benchmark_region_type]] == benchmark_region_value) %>%
    group_by(year) %>%
    summarise(population = sum(as.numeric(pop_total), na.rm = TRUE), .groups = "drop") %>%
    mutate(geo = benchmark_region_label) %>%
    select(geo, year, population),
  cbsa_features %>%
    group_by(year) %>%
    summarise(population = sum(as.numeric(pop_total), na.rm = TRUE), .groups = "drop") %>%
    mutate(geo = us_label) %>%
    select(geo, year, population)
) %>%
  distinct(geo, year, .keep_all = TRUE)

baseline_year <- pop_trend %>%
  group_by(geo) %>%
  summarise(min_year = min(year, na.rm = TRUE), .groups = "drop") %>%
  summarise(baseline = max(min_year)) %>%
  pull(baseline)

pop_trend_indexed <- pop_trend %>%
  group_by(geo) %>%
  arrange(year) %>%
  mutate(
    base = population[year == baseline_year][1],
    pop_index = 100 * population / base
  ) %>%
  ungroup()

winsorize_vec <- function(x, probs = c(0.01, 0.99)) {
  qs <- stats::quantile(x, probs = probs, na.rm = TRUE, names = FALSE)
  pmin(pmax(x, qs[1]), qs[2])
}

do_winsorize <- FALSE
winsor_limits <- c(0.01, 0.99)

metro_2024 <- cbsa_features %>%
  filter(year == target_year, cbsa_type == "Metro Area") %>%
  transmute(
    cbsa_geoid = cbsa_code,
    metro_name = cbsa_name,
    pop_total,
    pop_growth_5yr,
    units_per_1k_3yr = bps_units_per_1k_3yr_avg,
    land_area_sq_mi,
    median_gross_rent,
    median_home_value,
    mean_travel_time,
    pct_commute_wfh,
    commute_intensity_b,
    pop_density = if_else(land_area_sq_mi > 0, as.numeric(pop_total) / as.numeric(land_area_sq_mi), NA_real_),
    is_target_market = cbsa_code == target_cbsa_code
  )

distribution_long <- metro_2024 %>%
  select(
    cbsa_geoid, metro_name, is_target_market,
    pop_growth_5yr,
    units_per_1k_3yr,
    pop_density,
    median_gross_rent,
    median_home_value
  ) %>%
  tidyr::pivot_longer(
    cols = -c(cbsa_geoid, metro_name, is_target_market),
    names_to = "metric",
    values_to = "value"
  ) %>%
  filter(!is.na(value))

growth_median <- distribution_long %>%
  filter(metric == "pop_growth_5yr") %>%
  summarise(m = median(value, na.rm = TRUE)) %>%
  pull(m)

if (!is.na(growth_median) && growth_median > 1) {
  distribution_long <- distribution_long %>%
    mutate(value = if_else(metric == "pop_growth_5yr", value / 100, value))
}

if (do_winsorize) {
  distribution_long <- distribution_long %>%
    group_by(metric) %>%
    mutate(value_plot = winsorize_vec(value, winsor_limits)) %>%
    ungroup()
} else {
  distribution_long <- distribution_long %>%
    mutate(value_plot = value)
}

metric_labels <- c(
  pop_growth_5yr = "Pop growth (5y)",
  units_per_1k_3yr = "Units per 1k (3y)",
  pop_density = "Density (per sq mi)",
  median_gross_rent = "Median rent",
  median_home_value = "Median home value"
)

metric_order <- c(
  "pop_growth_5yr",
  "units_per_1k_3yr",
  "pop_density",
  "median_gross_rent",
  "median_home_value"
)

distribution_long <- distribution_long %>%
  mutate(
    metric = factor(metric, levels = metric_order),
    metric_label = metric_labels[as.character(metric)]
  )

save_artifact(
  kpi_tiles,
  resolve_output_path("02_market_overview", "section_02_kpi_tiles")
)
save_artifact(
  peer_table,
  resolve_output_path("02_market_overview", "section_02_peer_table")
)
save_artifact(
  benchmark_table,
  resolve_output_path("02_market_overview", "section_02_benchmark_table")
)
save_artifact(
  pop_trend_indexed,
  resolve_output_path("02_market_overview", "section_02_pop_trend_indexed")
)
save_artifact(
  distribution_long,
  resolve_output_path("02_market_overview", "section_02_distribution_long")
)
save_artifact(
  cbsa_features,
  resolve_output_path("02_market_overview", "section_02_cbsa_features")
)
save_artifact(
  market_profile,
  resolve_output_path("02_market_overview", "section_02_market_profile")
)

# Market context map artifact: tract geometries for target CBSA with growth signal.
tract_features <- section_inputs$tract_features %>%
  filter(as.character(cbsa_code) == as.character(target_cbsa_code)) %>%
  select(tract_geoid, cbsa_code, county_geoid, pop_growth_3yr, pop_growth_5yr, pop_density, median_gross_rent, median_home_value)

market_tract_sf <- section_inputs$market_tract_sf

save_artifact(
  market_tract_sf,
  resolve_output_path("02_market_overview", "section_02_market_tract_sf")
)

# County context map artifact: county geometries within target CBSA.
market_county_sf <- section_inputs$market_county_sf

save_artifact(
  market_county_sf,
  resolve_output_path("02_market_overview", "section_02_market_county_sf")
)

message("Section 02 build complete.")
