# In this script we normalize HUD CHAS burden data into our Silver layer

# 1. Set up our environment
# 2. Read staged county and place CHAS tables plus crosswalks
# 3. Standardize the CHAS segment labels we want to preserve in Silver
# 4. Pivot burden buckets into one analytical row per geography + tenure + income band
# 5. Rebase county CHAS rows to CBSA by summing household counts
# 6. Materialize to Silver

# 1. Set up our environment ----
getwd()

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# Helpers ----
check_unique_chas_grain <- function(df) {
  dupes <- df %>%
    count(geo_level, geo_id, year, tenure, income_band, name = "row_count") %>%
    filter(row_count > 1)

  if (nrow(dupes) > 0) {
    stop(
      "silver.hud_chas_burden has duplicate geo_level + geo_id + year + tenure + income_band rows",
      call. = FALSE
    )
  }
}

safe_sum <- function(x) {
  if (all(is.na(x))) {
    return(NA_real_)
  }

  sum(x, na.rm = TRUE)
}

clean_tenure <- function(x) {
  case_when(
    x == "Total: Occupied housing units" ~ "all",
    x == "Owner occupied" ~ "owner",
    x == "Renter occupied" ~ "renter",
    TRUE ~ NA_character_
  )
}

clean_income_band <- function(x) {
  case_when(
    x == "All" ~ "all",
    x == "household income is less than or equal to 30% of HAMFI" ~ "le_30_hamfi",
    x == "household income is greater than 30% but less than or equal to 50% of HAMFI" ~ "gt_30_to_50_hamfi",
    x == "household income is greater than 50% but less than or equal to 80% of HAMFI" ~ "gt_50_to_80_hamfi",
    x == "household income is greater than 80% but less than or equal to 100% of HAMFI" ~ "gt_80_to_100_hamfi",
    x == "household income is greater than 100% of HAMFI" ~ "gt_100_hamfi",
    TRUE ~ NA_character_
  )
}

clean_burden_band <- function(x) {
  case_when(
    x == "All" ~ "all",
    x == "housing cost burden is less than or equal to 30%" ~ "le_30_pct",
    x == "housing cost burden is greater than 30% but less than or equal to 50%" ~ "gt_30_to_50_pct",
    x == "housing cost burden is greater than 50%" ~ "gt_50_pct",
    TRUE ~ NA_character_
  )
}

standardize_chas <- function(df, geo_level_value, geo_id_col, state_lookup) {
  df %>%
    transmute(
      source = as.character(source),
      geo_level = geo_level_value,
      geo_id = as.character(.data[[geo_id_col]]),
      geo_name = as.character(name),
      state_fips = stringr::str_pad(as.character(st), width = 2, side = "left", pad = "0"),
      estimate = as.double(estimate),
      chas_period = as.character(chas_period),
      year = as.integer(year),
      household_type = as.character(household_type),
      tenure = clean_tenure(as.character(tenure)),
      income_band = clean_income_band(as.character(household_income)),
      burden_band = clean_burden_band(as.character(cost_burden))
    ) %>%
    left_join(state_lookup, by = "state_fips") %>%
    mutate(
      geo_name = dplyr::if_else(
        !is.na(state_abbr) & state_abbr != "" & !stringr::str_detect(geo_name, ","),
        paste0(geo_name, ", ", state_abbr),
        geo_name
      )
    ) %>%
    filter(
      !is.na(tenure),
      !is.na(income_band),
      !is.na(burden_band)
    ) %>%
    select(
      source, geo_level, geo_id, geo_name, state_fips, state_abbr,
      chas_period, year, household_type, tenure, income_band, burden_band, estimate
    ) %>%
    distinct()
}

# 2. Read staged CHAS and reference tables ----
county_chas_stage <- dbGetQuery(con, "SELECT * FROM staging.hud_chas_county")
place_chas_stage <- dbGetQuery(con, "SELECT * FROM staging.hud_chas_place")
county_state_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state")
cbsa_county_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county")

state_lookup <- county_state_xwalk %>%
  transmute(
    state_fips = as.character(state_fip),
    state_abbr = as.character(state_abbr)
  ) %>%
  distinct()

# 3. Standardize the geography slices we are documenting in Silver ----
# The approved CHAS contract keeps county and place source rows, then preserves
# tenure and income-band detail while intentionally collapsing household_type
# to "All". Household-type detail still exists upstream in staging if we need
# it later, but the documented Silver surface stays focused on burden analysis.
county_chas <- standardize_chas(
  df = county_chas_stage,
  geo_level_value = "county",
  geo_id_col = "county_geoid",
  state_lookup = state_lookup
)

place_chas <- standardize_chas(
  df = place_chas_stage,
  geo_level_value = "place",
  geo_id_col = "place_geoid",
  state_lookup = state_lookup
)

all_chas <- bind_rows(
  county_chas,
  place_chas
)

# 4. Build one row per geography + tenure + income band ----
# CHAS Table 7 ships one row per burden bucket. Silver pivots those source
# buckets into a compact analytical contract with:
# - the total household base for the segment
# - the <=30%, 30-50%, and >50% burden buckets
# - derived "cost burdened" (>30%) and "severely cost burdened" (>50%) rates
# We keep the >100% HAMFI band because it is already staged and useful for
# comparisons across the full affordability spectrum.
chas_overall_totals <- all_chas %>%
  filter(
    household_type == "All",
    burden_band == "all"
  ) %>%
  group_by(
    source, geo_level, geo_id, geo_name, state_fips, state_abbr,
    chas_period, year, tenure, income_band
  ) %>%
  summarize(total_households = safe_sum(estimate), .groups = "drop")

chas_detail_buckets <- all_chas %>%
  filter(
    burden_band != "all",
    income_band != "all"
  ) %>%
  group_by(
    source, geo_level, geo_id, geo_name, state_fips, state_abbr,
    chas_period, year, tenure, income_band, burden_band
  ) %>%
  summarize(households = safe_sum(estimate), .groups = "drop") %>%
  filter(tenure %in% c("owner", "renter"))

chas_aggregated_buckets <- bind_rows(
  chas_detail_buckets,
  # All-income owner and renter rows are built by summing the staged income bands.
  chas_detail_buckets %>%
    group_by(
      source, geo_level, geo_id, geo_name, state_fips, state_abbr,
      chas_period, year, tenure, burden_band
    ) %>%
    summarize(households = safe_sum(households), .groups = "drop") %>%
    mutate(income_band = "all"),
  # Tenure = all rows are built by summing owner and renter detail rows.
  chas_detail_buckets %>%
    group_by(
      source, geo_level, geo_id, geo_name, state_fips, state_abbr,
      chas_period, year, income_band, burden_band
    ) %>%
    summarize(households = safe_sum(households), .groups = "drop") %>%
    mutate(tenure = "all"),
  # This produces the fully rolled-up all-household, all-income burden counts.
  chas_detail_buckets %>%
    group_by(
      source, geo_level, geo_id, geo_name, state_fips, state_abbr,
      chas_period, year, burden_band
    ) %>%
    summarize(households = safe_sum(households), .groups = "drop") %>%
    mutate(
      tenure = "all",
      income_band = "all"
    )
) %>%
  group_by(
    source, geo_level, geo_id, geo_name, state_fips, state_abbr,
    chas_period, year, tenure, income_band, burden_band
  ) %>%
  summarize(households = safe_sum(households), .groups = "drop")

chas_buckets <- chas_aggregated_buckets %>%
  tidyr::pivot_wider(
    names_from = burden_band,
    values_from = households,
    values_fill = 0
  ) %>%
  rename(
    households_cost_burden_le_30 = le_30_pct,
    households_cost_burden_30_50 = gt_30_to_50_pct,
    households_cost_burden_50plus = gt_50_pct
  ) %>%
  mutate(
    total_households_from_buckets =
      households_cost_burden_le_30 +
      households_cost_burden_30_50 +
      households_cost_burden_50plus
  )

hud_chas_burden <- chas_buckets %>%
  left_join(
    chas_overall_totals,
    by = c(
      "source", "geo_level", "geo_id", "geo_name", "state_fips", "state_abbr",
      "chas_period", "year", "tenure", "income_band"
    )
  ) %>%
  mutate(
    total_households = coalesce(total_households, total_households_from_buckets),
    households_cost_burdened = households_cost_burden_30_50 + households_cost_burden_50plus,
    households_severely_cost_burdened = households_cost_burden_50plus,
    pct_cost_burdened = dplyr::if_else(
      total_households > 0,
      households_cost_burdened / total_households,
      NA_real_
    ),
    pct_severely_cost_burdened = dplyr::if_else(
      total_households > 0,
      households_severely_cost_burdened / total_households,
      NA_real_
    )
  ) %>%
  select(
    source, geo_level, geo_id, geo_name, state_fips, state_abbr,
    chas_period, year, tenure, income_band,
    total_households,
    households_cost_burden_le_30,
    households_cost_burden_30_50,
    households_cost_burden_50plus,
    households_cost_burdened,
    households_severely_cost_burdened,
    pct_cost_burdened,
    pct_severely_cost_burdened
  ) %>%
  arrange(geo_level, geo_id, year, tenure, income_band)

# 5. Rebase county CHAS rows to CBSA ----
# CHAS does not ship a clean metro table in the current staging contract, so we
# roll county CHAS counts into CBSAs using the county->CBSA crosswalk. We sum
# the household counts for each burden bucket and then recompute the rates from
# those summed counts rather than averaging already-derived county percentages.
cbsa_chas_burden <- hud_chas_burden %>%
  filter(geo_level == "county") %>%
  mutate(geo_id = as.character(geo_id)) %>%
  left_join(
    cbsa_county_xwalk %>%
      transmute(
        county_geoid = as.character(county_geoid),
        cbsa_code = as.character(cbsa_code),
        cbsa_name = as.character(cbsa_name)
      ) %>%
      distinct(),
    by = c("geo_id" = "county_geoid")
  ) %>%
  filter(!is.na(cbsa_code), cbsa_code != "") %>%
  group_by(source, cbsa_code, cbsa_name, chas_period, year, tenure, income_band) %>%
  summarize(
    total_households = safe_sum(total_households),
    households_cost_burden_le_30 = safe_sum(households_cost_burden_le_30),
    households_cost_burden_30_50 = safe_sum(households_cost_burden_30_50),
    households_cost_burden_50plus = safe_sum(households_cost_burden_50plus),
    households_cost_burdened = safe_sum(households_cost_burdened),
    households_severely_cost_burdened = safe_sum(households_severely_cost_burdened),
    .groups = "drop"
  ) %>%
  transmute(
    source,
    geo_level = "cbsa",
    geo_id = cbsa_code,
    geo_name = cbsa_name,
    state_fips = NA_character_,
    state_abbr = NA_character_,
    chas_period,
    year,
    tenure,
    income_band,
    total_households,
    households_cost_burden_le_30,
    households_cost_burden_30_50,
    households_cost_burden_50plus,
    households_cost_burdened,
    households_severely_cost_burdened,
    pct_cost_burdened = dplyr::if_else(
      total_households > 0,
      households_cost_burdened / total_households,
      NA_real_
    ),
    pct_severely_cost_burdened = dplyr::if_else(
      total_households > 0,
      households_severely_cost_burdened / total_households,
      NA_real_
    )
  )

hud_chas_burden <- bind_rows(
  hud_chas_burden,
  cbsa_chas_burden
) %>%
  arrange(geo_level, geo_id, year, tenure, income_band)

check_unique_chas_grain(hud_chas_burden)

# 6. Materialize to Silver ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "hud_chas_burden"),
  hud_chas_burden,
  overwrite = TRUE
)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)
