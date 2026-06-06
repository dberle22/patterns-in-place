# Shared configuration for Retail Opportunity Finder section modules

# Market selection
ACTIVE_MARKET_KEY <- Sys.getenv("ROF_MARKET_KEY", unset = "jacksonville_fl")
if (!ACTIVE_MARKET_KEY %in% names(MARKET_PROFILES)) {
  stop(
    paste0(
      "Unknown ROF_MARKET_KEY: ", ACTIVE_MARKET_KEY,
      ". Valid options: ", paste(names(MARKET_PROFILES), collapse = ", ")
    ),
    call. = FALSE
  )
}
TARGET_CBSA <- MARKET_PROFILES[[ACTIVE_MARKET_KEY]]$cbsa_code
TARGET_VINTAGE <- "2024_5yr"
BASELINE_VINTAGE <- "2019_5yr"
TARGET_YEAR <- 2024

# Model thresholds and weights (V1 locked defaults)
MODEL_PARAMS <- list(
  min_growth_percentile = 0.50,
  price_proxy_pctl_max = 0.70,
  max_density_percentile = 0.70,
  cluster_top_share = 0.25,
  top_n_tracts = 50,
  weights = c(
    growth = 0.30,
    units = 0.20,
    headroom = 0.15,
    price = 0.10,
    commute = 0.05,
    income = 0.20
  )
)

# Output root for section artifacts
SECTION_OUTPUT_ROOT <- "notebooks/retail_opportunity_finder/sections"
DATA_PLATFORM_ROOT <- "notebooks/retail_opportunity_finder/data_platform"
NOTEBOOK_BUILD_ROOT <- "notebooks/retail_opportunity_finder/notebook_build"

# Parcel foundation inputs for Section 05.
PARCEL_STANDARDIZATION_ROOT_DEFAULT <- file.path(
  SECTION_OUTPUT_ROOT,
  "05_parcels",
  "parcel_standardization",
  "outputs",
  "fl_all_v2"
)
PARCEL_STANDARDIZATION_ROOT <- Sys.getenv(
  "ROF_PARCEL_STANDARDIZED_ROOT",
  unset = PARCEL_STANDARDIZATION_ROOT_DEFAULT
)
PARCEL_DUCKDB_SCHEMA <- "rof_parcel"

# SQL registry for section query inputs
SQL_ROOT <- "notebooks/retail_opportunity_finder/sql"
SQL_PATHS <- list(
  features = list(
    cbsa_features = file.path(SQL_ROOT, "features", "cbsa_features.sql"),
    tract_features = file.path(SQL_ROOT, "features", "tract_features.sql"),
    tract_universe = file.path(SQL_ROOT, "features", "tract_universe.sql")
  ),
  qa = list(
    tract_features = file.path(SQL_ROOT, "qa", "tract_features_qa.sql")
  ),
  staging = list()
)

# Geometry source registry for the legacy section geometry adapter.
# County and CBSA boundary tables remain shared; tract geometry here is still
# state-scoped compatibility infrastructure. Managed ROF consumers should prefer
# foundation geometry tables, and upstream geography ETL is moving toward
# metro_deep_dive.geo.tracts_all_us as the national tract source.
GEOMETRY_SOURCE_REGISTRY <- list(
  cbsa_table = "metro_deep_dive.geo.cbsas",
  county_table = "metro_deep_dive.geo.counties",
  tract_tables = list(
    FL = "metro_deep_dive.geo.tracts_fl",
    GA = "metro_deep_dive.geo.tracts_ga",
    SC = "metro_deep_dive.geo.tracts_sc",
    NC = "metro_deep_dive.geo.tracts_nc"
  )
)

# Optional toggles
ENABLE_SENSITIVITY <- FALSE
ENABLE_MICRO_DEEP_DIVE <- FALSE

# KPI dictionary for model transparency and QA
KPI_DICTIONARY <- data.frame(
  kpi_key = c(
    "pop_growth_3yr",
    "units_per_1k_3yr",
    "pop_density",
    "price_proxy_pctl",
    "commute_intensity_b",
    "median_hh_income"
  ),
  label = c(
    "Population growth (3-year)",
    "Estimated units per 1,000 residents (3-year avg)",
    "Population density",
    "Housing price pressure proxy percentile",
    "Commute intensity",
    "Median household income"
  ),
  direction = c("higher_better", "higher_better", "lower_better", "lower_better", "higher_better", "higher_better"),
  source_table = c(
    "tract_features",
    "tract_features",
    "tract_features",
    "tract_features",
    "tract_features",
    "tract_features"
  ),
  stringsAsFactors = FALSE
)

# Minimum required columns for major inputs used by section modules
REQUIRED_COLUMNS <- list(
  tract_features = c(
    "cbsa_code", "county_geoid", "tract_geoid", "year",
    "pop_total", "pop_growth_3yr", "pop_growth_5yr", "pop_growth_pctl",
    "median_gross_rent", "median_home_value", "price_proxy_pctl",
    "mean_travel_time", "pct_commute_wfh", "commute_intensity_b",
    "median_hh_income",
    "total_units_3yr_avg", "units_per_1k_3yr",
    "land_area_sqmi", "pop_density", "density_pctl",
    "gate_pop", "gate_price", "gate_density", "eligible_v1"
  ),
  cbsa_features = c(
    "cbsa_code", "cbsa_name", "cbsa_type", "census_region", "census_division",
    "year", "pop_total", "pop_growth_5yr", "median_gross_rent", "median_home_value",
    "mean_travel_time", "pct_commute_wfh", "commute_intensity_b",
    "bps_units_per_1k_3yr_avg"
  ),
  tract_geom = c("tract_geoid", "county_geoid", "state_fips", "cbsa_code", "geom_wkb"),
  county_geom = c("county_geoid", "county_name", "state_fips", "cbsa_code", "geom_wkb"),
  cbsa_geom = c("cbsa_code", "cbsa_name", "geom_wkb")
)

# Geometry assumptions for QA checks
GEOMETRY_ASSUMPTIONS <- list(
  expected_crs_epsg = 4326,
  analysis_crs_epsg = 5070,
  min_rows = list(
    cbsa_geom = 1L,
    county_geom = 1L,
    tract_geom = 1L
  )
)
