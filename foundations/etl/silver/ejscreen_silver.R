# In this script we normalize tract-level EJScreen staging rows into a curated
# Silver table. The script first audits tract GEOID coverage against canonical
# tract reference tables; if the archive looks too stale relative to current
# crosswalks, we stop before writing a misleading analytical table.

getwd()

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

# 2. Helpers ----
check_unique_annual_grain <- function(df, table_name) {
  dupes <- df %>%
    count(geo_level, geo_id, year, name = "row_count") %>%
    filter(row_count > 1)

  if (nrow(dupes) > 0) {
    stop(
      sprintf(
        "%s has duplicate geo_level + geo_id + year rows",
        table_name
      ),
      call. = FALSE
    )
  }
}

match_floor <- 0.99
unsupported_state_abbrevs <- c("AS", "GU", "MP", "PR", "VI")

# 3. Read staging and canonical tract references ----
ejscreen_stage <- DBI::dbGetQuery(con, "SELECT * FROM staging.ejscreen") %>%
  mutate(
    tract_geoid = as.character(tract_geoid),
    year = as.integer(year)
  )

tract_xwalk <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_tract_county") %>%
  transmute(
    tract_geoid = as.character(tract_geoid),
    tract_name_long = as.character(tract_name_long),
    county_name = as.character(county_name),
    state_abbr = as.character(state_abbr),
    state_name = as.character(state_name)
  ) %>%
  distinct()

tract_dim_geo <- DBI::dbGetQuery(
  con,
  "
  SELECT geo_id, geo_name
  FROM gold.dim_geo
  WHERE geo_level = 'tract'
  "
) %>%
  transmute(
    tract_geoid = as.character(geo_id),
    tract_geo_name = as.character(geo_name)
  ) %>%
  distinct()

# 4. Audit tract-key match quality before modeling ----
tract_match_audit <- ejscreen_stage %>%
  distinct(tract_geoid) %>%
  left_join(
    tract_xwalk %>% transmute(tract_geoid, in_xwalk = TRUE),
    by = "tract_geoid"
  ) %>%
  left_join(
    tract_dim_geo %>% transmute(tract_geoid, in_dim_geo = TRUE),
    by = "tract_geoid"
  ) %>%
  mutate(
    in_xwalk = dplyr::coalesce(in_xwalk, FALSE),
    in_dim_geo = dplyr::coalesce(in_dim_geo, FALSE)
  )

xwalk_match_rate <- mean(tract_match_audit$in_xwalk)
dim_geo_match_rate <- mean(tract_match_audit$in_dim_geo)
supported_tract_match_audit <- ejscreen_stage %>%
  distinct(tract_geoid, state_abbrev) %>%
  filter(!state_abbrev %in% unsupported_state_abbrevs) %>%
  left_join(
    tract_match_audit,
    by = "tract_geoid"
  )

supported_xwalk_match_rate <- mean(supported_tract_match_audit$in_xwalk)
supported_dim_geo_match_rate <- mean(supported_tract_match_audit$in_dim_geo)
unsupported_tract_count <- ejscreen_stage %>%
  distinct(tract_geoid, state_abbrev) %>%
  filter(state_abbrev %in% unsupported_state_abbrevs) %>%
  nrow()
supported_unmatched_count <- supported_tract_match_audit %>%
  filter(!in_xwalk | !in_dim_geo) %>%
  nrow()

if (supported_xwalk_match_rate < match_floor || supported_dim_geo_match_rate < match_floor) {
  stop(
    sprintf(
      paste(
        "EJScreen tract coverage audit failed after excluding archive geographies",
        "that are outside the current canonical tract backbone.",
        "Supported-state xwalk_tract_county match rate = %.4f, gold.dim_geo tract match rate = %.4f,",
        "both of which must be at least %.2f before Silver proceeds."
      ),
      supported_xwalk_match_rate,
      supported_dim_geo_match_rate,
      match_floor
    ),
    call. = FALSE
  )
}

message(
  sprintf(
    paste(
      "EJScreen tract audit summary:",
      "overall xwalk match = %.4f, overall dim_geo match = %.4f,",
      "unsupported archive tracts excluded from Silver = %s,",
      "supported unmatched tracts dropped = %s."
    ),
    xwalk_match_rate,
    dim_geo_match_rate,
    unsupported_tract_count,
    supported_unmatched_count
  )
)

# 5. Keep the agreed core tract-level environmental columns ----
ejscreen <- ejscreen_stage %>%
  left_join(
    tract_xwalk,
    by = "tract_geoid"
  ) %>%
  left_join(
    tract_dim_geo,
    by = "tract_geoid"
  ) %>%
  left_join(
    tract_match_audit,
    by = "tract_geoid"
  ) %>%
  filter(!state_abbrev %in% unsupported_state_abbrevs) %>%
  filter(in_xwalk, in_dim_geo) %>%
  transmute(
    geo_level = "tract",
    geo_id = tract_geoid,
    geo_name = dplyr::coalesce(tract_geo_name, tract_name_long, tract_geoid),
    year = year,
    total_population = as.double(acstotpop),
    pm25 = as.double(pm25),
    ozone = as.double(ozone),
    diesel_pm = as.double(dslpm),
    traffic_proximity = as.double(ptraf),
    superfund_proximity = as.double(pnpl),
    rmp_proximity = as.double(prmp),
    wastewater_discharge = as.double(pwdis),
    drinking_water_noncompliance = as.double(dwater),
    pctile_pm25_us = as.double(p_pm25),
    pctile_ozone_us = as.double(p_ozone),
    pctile_diesel_pm_us = as.double(p_dslpm),
    pctile_traffic_us = as.double(p_ptraf),
    pctile_superfund_us = as.double(p_pnpl),
    pctile_rmp_us = as.double(p_prmp),
    pctile_wastewater_us = as.double(p_pwdis),
    pctile_drinking_water_us = as.double(p_dwater),
    count_high_exposure_indicators = as.integer(exceed_count_80),
    count_high_exposure_supplemental = as.integer(exceed_count_80_sup)
  ) %>%
  filter(!is.na(.data$geo_id), !is.na(.data$year)) %>%
  distinct() %>%
  arrange(.data$geo_id, .data$year)

check_unique_annual_grain(ejscreen, "silver.ejscreen")

# 6. Materialize to Silver ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "ejscreen"),
  ejscreen,
  overwrite = TRUE
)

DBI::dbExecute(con, "CHECKPOINT")
