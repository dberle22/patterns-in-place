# In this script we normalize IRS migration data into our Silver layer

# 1. Set up our environment
# 2. Read staging and crosswalk tables
# 3. Build detailed county and state origin-destination flow tables
# 4. Roll those detailed flows up into county, CBSA, and state summaries
# 5. Materialize to Silver

# 1. Set up our environment ----
getwd()

# Read our shared libraries and helper functions.
source(here::here("foundations", "etl", "utils.R"))

# Make sure project-level environment variables are available.
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Point to the shared DuckDB used by the pipeline.
db_path <- get_env_path("DB_PATH")

# Connect with write access because this script overwrites Silver tables.
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# 2. Read in our staging and reference tables ----
# IRS staging currently gives us:
# - county-level inflow detail (origin county -> destination county)
# - state-level inflow summaries (origin state -> destination state)
county_inflow_raw <- dbGetQuery(con, "SELECT * FROM staging.irs_inflow_migration_county")
state_inflow_raw <- dbGetQuery(con, "SELECT * FROM staging.irs_inflow_migration_state")

# Crosswalks are used only to add readable names and to rebase county flows to CBSA.
cbsa_county_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county")
county_state_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state")

# Helper functions ----
sum_or_na <- function(x) {
  # If every value in a group is suppressed / missing, keep the result missing.
  # This avoids silently converting "unknown" into 0 during aggregation.
  if (all(is.na(x))) {
    return(NA_real_)
  }

  sum(x, na.rm = TRUE)
}

aggregate_inflows <- function(df, group_cols) {
  df %>%
    # Group the detailed OD rows to the requested geography + year grain,
    # then total up the IRS measures for the "inflow" side.
    group_by(across(all_of(c(group_cols, "year")))) %>%
    summarize(
      across(
        c(n_returns, n_exemptions, agi_thousands, agi),
        sum_or_na
      ),
      .groups = "drop"
    ) %>%
    mutate(has_inflow = TRUE) %>%
    rename(
      inflow_returns = n_returns,
      inflow_exemptions = n_exemptions,
      inflow_agi_thousands = agi_thousands,
      inflow_agi = agi
    )
}

aggregate_outflows <- function(df, group_cols) {
  df %>%
    # Same idea as inflows, but these totals will represent the "outflow" side
    # so that we can compute net migration metrics later.
    group_by(across(all_of(c(group_cols, "year")))) %>%
    summarize(
      across(
        c(n_returns, n_exemptions, agi_thousands, agi),
        sum_or_na
      ),
      .groups = "drop"
    ) %>%
    mutate(has_outflow = TRUE) %>%
    rename(
      outflow_returns = n_returns,
      outflow_exemptions = n_exemptions,
      outflow_agi_thousands = agi_thousands,
      outflow_agi = agi
    )
}

build_summary <- function(inflow_df, outflow_df, key_cols) {
  full_join(
    inflow_df,
    outflow_df,
    by = c(key_cols, "year")
  ) %>%
    mutate(
      # If a geography shows up only on one side of the join, that usually means
      # "no inflow rows" or "no outflow rows" rather than a broken value.
      # We treat the missing side as zero before computing net measures.
      inflow_returns = if_else(is.na(has_inflow), 0, inflow_returns),
      inflow_exemptions = if_else(is.na(has_inflow), 0, inflow_exemptions),
      inflow_agi_thousands = if_else(is.na(has_inflow), 0, inflow_agi_thousands),
      inflow_agi = if_else(is.na(has_inflow), 0, inflow_agi),
      outflow_returns = if_else(is.na(has_outflow), 0, outflow_returns),
      outflow_exemptions = if_else(is.na(has_outflow), 0, outflow_exemptions),
      outflow_agi_thousands = if_else(is.na(has_outflow), 0, outflow_agi_thousands),
      outflow_agi = if_else(is.na(has_outflow), 0, outflow_agi),
      net_returns = inflow_returns - outflow_returns,
      net_exemptions = inflow_exemptions - outflow_exemptions,
      net_agi_thousands = inflow_agi_thousands - outflow_agi_thousands,
      net_agi = inflow_agi - outflow_agi
    ) %>%
    select(-has_inflow, -has_outflow)
}

# 3. Build our lookup tables ----
# County names are mostly sourced from the county/state crosswalk.
county_lookup <- county_state_xwalk %>%
  distinct(
    county_geoid,
    county_name_long
  )

# State names are built from base R state vectors plus DC, then matched back
# to the state FIPS codes used in our county/state crosswalk.
state_lookup <- tibble(
  state_abbr = c(state.abb, "DC"),
  state_name = c(state.name, "District of Columbia")
) %>%
  left_join(
    county_state_xwalk %>%
      distinct(state_fip, state_abbr),
    by = "state_abbr"
  ) %>%
  distinct(state_fip, state_abbr, state_name)

# County FIPS can change over time, so we build a "best available" county name
# reference from both the current crosswalk and the staged IRS destination names.
county_name_ref <- bind_rows(
  # Current county crosswalk names are the preferred modern labels.
  county_lookup %>%
    transmute(
      county_geoid,
      county_name = county_name_long
    ),
  # The staged IRS names help cover older county identifiers that may not map
  # cleanly to the current crosswalk naming.
  county_inflow_raw %>%
    transmute(
      county_geoid = dest_geoid,
      county_name = dest_county_name
    )
) %>%
  filter(!is.na(county_name), county_name != "") %>%
  distinct(county_geoid, county_name) %>%
  group_by(county_geoid) %>%
  summarize(county_name = first(county_name), .groups = "drop")

cbsa_lookup <- cbsa_county_xwalk %>%
  distinct(county_geoid, cbsa_code, cbsa_name)

# 3.1 Build detailed county flow table ----
# Start from the staged county inflow rows, add readable origin/destination
# names, and align everything to one consistent Silver schema.
county_flows <- county_inflow_raw %>%
  # Attach readable county/state labels while preserving the staged IDs.
  left_join(
    county_name_ref %>%
      select(
        county_geoid,
        origin_geo_name = county_name
      ),
    by = c("origin_geoid" = "county_geoid")
  ) %>%
  left_join(
    county_name_ref %>%
      select(
        county_geoid,
        dest_geo_name = county_name
      ),
    by = c("dest_geoid" = "county_geoid")
  ) %>%
  left_join(
    state_lookup %>%
      select(state_fip, origin_state_abbr = state_abbr),
    by = c("origin_state_fips" = "state_fip")
  ) %>%
  left_join(
    state_lookup %>%
      select(state_fip, dest_state_abbr = state_abbr),
    by = c("dest_state_fips" = "state_fip")
  ) %>%
  transmute(
    # geo_level tells downstream users that both origin and destination IDs
    # in this row are county-level identifiers.
    geo_level = "county",
    flow_id,
    year,
    origin_year,
    dest_year,
    origin_geo_id = origin_geoid,
    origin_geo_name = coalesce(origin_geo_name, origin_geoid),
    origin_state_fips,
    origin_state_abbr,
    origin_county_fips,
    dest_geo_id = dest_geoid,
    dest_geo_name = coalesce(dest_geo_name, dest_county_name),
    dest_state_fips,
    dest_state_abbr,
    dest_county_fips,
    n_returns = as.double(n_returns),
    n_exemptions = as.double(n_exemptions),
    agi_thousands = as.double(agi_thousands),
    agi = as.double(agi)
  ) %>%
  # Some staged county records are exact repeats, so dedupe before we treat
  # this as a stable analytical contract.
  distinct()

# 3.2 Build detailed state flow table ----
# State staging is already a rolled-up interstate slice. Here we just add names
# and reshape it to match the county flow contract.
state_flows <- state_inflow_raw %>%
  left_join(
    state_lookup %>%
      select(
        state_fip,
        origin_geo_name = state_name,
        origin_state_abbr = state_abbr
      ),
    by = c("origin_state_fips" = "state_fip")
  ) %>%
  left_join(
    state_lookup %>%
      select(
        state_fip,
        dest_geo_name = state_name,
        dest_state_abbr = state_abbr
      ),
    by = c("dest_state_fips" = "state_fip")
  ) %>%
  transmute(
    geo_level = "state",
    flow_id,
    year,
    origin_year,
    dest_year,
    origin_geo_id = origin_state_fips,
    origin_geo_name = coalesce(origin_geo_name, origin_state_fips),
    origin_state_fips,
    origin_state_abbr,
    origin_county_fips = NA_character_,
    dest_geo_id = dest_state_fips,
    dest_geo_name = coalesce(dest_geo_name, dest_state_fips),
    dest_state_fips,
    dest_state_abbr,
    dest_county_fips = NA_character_,
    n_returns = as.double(n_returns),
    n_exemptions = as.double(n_exemptions),
    agi_thousands = as.double(agi_thousands),
    agi = as.double(agi)
  ) %>%
  distinct()

# Final detailed Silver flow table:
# one table, two geo levels, same column contract for county and state rows.
irs_migration_flows <- bind_rows(
  county_flows,
  state_flows
)

# 4. Build county summary rows ----
# For county summaries, destination counties represent inflows...
county_inflow_summary <- county_flows %>%
  transmute(
    geo_level = "county",
    geo_id = dest_geo_id,
    state_fips = dest_state_fips,
    year,
    n_returns,
    n_exemptions,
    agi_thousands,
    agi
  ) %>%
  aggregate_inflows(
    group_cols = c("geo_level", "geo_id", "state_fips")
  )

# ...and origin counties represent outflows.
county_outflow_summary <- county_flows %>%
  transmute(
    geo_level = "county",
    geo_id = origin_geo_id,
    state_fips = origin_state_fips,
    year,
    n_returns,
    n_exemptions,
    agi_thousands,
    agi
  ) %>%
  aggregate_outflows(
    group_cols = c("geo_level", "geo_id", "state_fips")
  )

# Join the two sides, compute net metrics, then add readable county/state names.
county_summary <- build_summary(
  inflow_df = county_inflow_summary,
  outflow_df = county_outflow_summary,
  key_cols = c("geo_level", "geo_id", "state_fips")
) %>%
  left_join(
    county_name_ref %>%
      rename(geo_id = county_geoid, geo_name = county_name),
    by = "geo_id"
  ) %>%
  left_join(
    state_lookup %>%
      select(state_fip, state_abbr) %>%
      rename(state_fips = state_fip),
    by = "state_fips"
  ) %>%
  transmute(
    geo_level,
    geo_id,
    geo_name = coalesce(geo_name, geo_id),
    state_fips,
    state_abbr,
    year,
    inflow_returns,
    outflow_returns,
    net_returns,
    inflow_exemptions,
    outflow_exemptions,
    net_exemptions,
    inflow_agi_thousands,
    outflow_agi_thousands,
    net_agi_thousands,
    inflow_agi,
    outflow_agi,
    net_agi
  )

# 4.1 Rebase county flows to CBSA summaries ----
# Join CBSA codes onto both the origin county and destination county so that
# each county-to-county move can also be interpreted as a metro-to-metro move.
county_flows_cbsa <- county_flows %>%
  left_join(
    cbsa_lookup %>%
      rename(origin_geo_id = county_geoid) %>%
      rename(origin_cbsa_code = cbsa_code, origin_cbsa_name = cbsa_name),
    by = "origin_geo_id"
  ) %>%
  left_join(
    cbsa_lookup %>%
      rename(dest_geo_id = county_geoid) %>%
      rename(dest_cbsa_code = cbsa_code, dest_cbsa_name = cbsa_name),
    by = "dest_geo_id"
  )

# CBSA inflows are any county flows whose destination is in a CBSA.
# We exclude moves where origin and destination counties are in the same CBSA,
# because those are internal metro moves rather than metro-to-metro migration.
cbsa_inflow_summary <- county_flows_cbsa %>%
  filter(!is.na(dest_cbsa_code)) %>%
  filter(is.na(origin_cbsa_code) | origin_cbsa_code != dest_cbsa_code) %>%
  transmute(
    geo_level = "cbsa",
    geo_id = dest_cbsa_code,
    year,
    n_returns,
    n_exemptions,
    agi_thousands,
    agi
  ) %>%
  aggregate_inflows(group_cols = c("geo_level", "geo_id"))

# Same exclusion rule on the outflow side.
cbsa_outflow_summary <- county_flows_cbsa %>%
  filter(!is.na(origin_cbsa_code)) %>%
  filter(is.na(dest_cbsa_code) | origin_cbsa_code != dest_cbsa_code) %>%
  transmute(
    geo_level = "cbsa",
    geo_id = origin_cbsa_code,
    year,
    n_returns,
    n_exemptions,
    agi_thousands,
    agi
  ) %>%
  aggregate_outflows(group_cols = c("geo_level", "geo_id"))

# Net CBSA inflows and outflows, then attach metro names.
cbsa_summary <- build_summary(
  inflow_df = cbsa_inflow_summary,
  outflow_df = cbsa_outflow_summary,
  key_cols = c("geo_level", "geo_id")
) %>%
  left_join(
    cbsa_lookup %>%
      distinct(cbsa_code, cbsa_name) %>%
      rename(geo_id = cbsa_code, geo_name = cbsa_name),
    by = "geo_id"
  ) %>%
  transmute(
    geo_level,
    geo_id,
    geo_name = coalesce(geo_name, geo_id),
    state_fips = NA_character_,
    state_abbr = NA_character_,
    year,
    inflow_returns,
    outflow_returns,
    net_returns,
    inflow_exemptions,
    outflow_exemptions,
    net_exemptions,
    inflow_agi_thousands,
    outflow_agi_thousands,
    net_agi_thousands,
    inflow_agi,
    outflow_agi,
    net_agi
  )

# 4.2 Build state summary rows ----
# State staging is already a state-to-state flow table, so we summarize directly
# from those rows rather than rebasing county flows.
state_inflow_summary <- state_flows %>%
  # Keep this guard so we do not accidentally count same-state rows if the
  # staging contract changes in the future.
  filter(origin_geo_id != dest_geo_id) %>%
  transmute(
    geo_level = "state",
    geo_id = dest_geo_id,
    year,
    n_returns,
    n_exemptions,
    agi_thousands,
    agi
  ) %>%
  aggregate_inflows(group_cols = c("geo_level", "geo_id"))

# Outflow side for state summaries.
state_outflow_summary <- state_flows %>%
  filter(origin_geo_id != dest_geo_id) %>%
  transmute(
    geo_level = "state",
    geo_id = origin_geo_id,
    year,
    n_returns,
    n_exemptions,
    agi_thousands,
    agi
  ) %>%
  aggregate_outflows(group_cols = c("geo_level", "geo_id"))

# Net state inflows and outflows, then restore readable state labels.
state_summary <- build_summary(
  inflow_df = state_inflow_summary,
  outflow_df = state_outflow_summary,
  key_cols = c("geo_level", "geo_id")
) %>%
  left_join(
    state_lookup %>%
      transmute(
        geo_id = state_fip,
        geo_name = state_name,
        state_fips = state_fip,
        state_abbr
      ),
    by = "geo_id"
  ) %>%
  transmute(
    geo_level,
    geo_id,
    geo_name = coalesce(geo_name, geo_id),
    state_fips,
    state_abbr,
    year,
    inflow_returns,
    outflow_returns,
    net_returns,
    inflow_exemptions,
    outflow_exemptions,
    net_exemptions,
    inflow_agi_thousands,
    outflow_agi_thousands,
    net_agi_thousands,
    inflow_agi,
    outflow_agi,
    net_agi
  )

# Final summary contract:
# - county rows: county inflow/outflow totals
# - cbsa rows: metro-to-metro movement totals
# - state rows: interstate movement totals
irs_migration_summary <- bind_rows(
  county_summary,
  cbsa_summary,
  state_summary
) %>%
  arrange(geo_level, geo_id, year)

# 5. Materialize to Silver ----
# Write both the detailed OD table and the rolled-up summary table.
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "irs_migration_flows"),
  irs_migration_flows,
  overwrite = TRUE
)

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "irs_migration_summary"),
  irs_migration_summary,
  overwrite = TRUE
)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)
