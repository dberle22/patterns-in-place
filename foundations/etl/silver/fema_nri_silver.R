# In this script we normalize FEMA National Risk Index county-equivalent staging
# rows into a compact analytical Silver table. We keep county rows directly and
# derive CBSA rows from county-equivalent staging using population-weighted
# averages across the selected composite and hazard metrics.

getwd()

# 1. Set up our environment ----
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

drv <- duckdb::duckdb()
con <- DBI::dbConnect(drv, dbdir = db_path, read_only = FALSE)

# 2. Helpers ----
safe_weighted_mean <- function(values, weights) {
  valid <- !is.na(values) & !is.na(weights) & weights > 0

  if (!any(valid)) {
    return(NA_real_)
  }

  stats::weighted.mean(values[valid], weights[valid])
}

append_state_abbr <- function(name, state_abbr) {
  dplyr::if_else(
    !is.na(state_abbr) & state_abbr != "" & !stringr::str_detect(name, ","),
    paste0(name, ", ", state_abbr),
    name
  )
}

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

build_metric_exprs <- function(mapping) {
  purrr::imap(
    mapping,
    ~ rlang::expr(as.double(.data[[!!.x]]))
  ) %>%
    rlang::set_names(names(mapping))
}

hazard_prefix_map <- c(
  avalanche = "avln",
  coastal_flooding = "cfld",
  cold_wave = "cwav",
  drought = "drgt",
  earthquake = "erqk",
  hail = "hail",
  heat_wave = "hwav",
  hurricane = "hrcn",
  ice_storm = "istm",
  inland_flooding = "ifld",
  landslide = "lnds",
  lightning = "ltng",
  strong_wind = "swnd",
  tornado = "trnd",
  tsunami = "tsun",
  volcanic_activity = "vlcn",
  wildfire = "wfir",
  winter_weather = "wntw"
)

base_metric_map <- c(
  risk_score = "risk_score",
  eal_score = "eal_score",
  alr_national_pctile = "alr_npctl",
  alr_vra_national_pctile = "alr_vra_npctl",
  social_vulnerability_score = "sovi_score",
  community_resilience_score = "resl_score"
)

hazard_risk_score_map <- setNames(
  paste0(hazard_prefix_map, "_risks"),
  paste0(names(hazard_prefix_map), "_risk_score")
)

hazard_eal_score_map <- setNames(
  paste0(hazard_prefix_map, "_eals"),
  paste0(names(hazard_prefix_map), "_expected_annual_loss_score")
)

hazard_frequency_map <- setNames(
  paste0(hazard_prefix_map, "_afreq"),
  paste0(names(hazard_prefix_map), "_annualized_frequency")
)

selected_metric_map <- c(
  base_metric_map,
  hazard_risk_score_map,
  hazard_eal_score_map,
  hazard_frequency_map
)

selected_metric_names <- names(selected_metric_map)

# 3. Read staging and crosswalks ----
fema_nri_stage <- DBI::dbGetQuery(con, "SELECT * FROM staging.fema_nri")

cbsa_county_xwalk <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county") %>%
  transmute(
    county_geoid = as.character(county_geoid),
    cbsa_code = as.character(cbsa_code),
    cbsa_name = as.character(cbsa_name)
  ) %>%
  distinct()

county_state_xwalk <- DBI::dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state") %>%
  transmute(
    county_geoid = as.character(county_geoid),
    county_name_long = as.character(county_name_long),
    state_abbr = as.character(state_abbr)
  ) %>%
  distinct()

# 4. Standardize county rows ----
# FEMA's county release is actually a county-equivalent layer. We keep every
# published county-equivalent row at county grain in Silver and only use the
# OMB crosswalk to derive CBSA rollups for counties that participate in a CBSA.
fema_nri_county <- fema_nri_stage %>%
  mutate(
    stcofips = as.character(stcofips),
    stateabbrv = as.character(stateabbrv),
    county = as.character(county),
    countytype = as.character(countytype),
    nri_release_year = as.integer(nri_release_year),
    population_weight = as.double(population)
  ) %>%
  left_join(
    county_state_xwalk,
    by = c("stcofips" = "county_geoid")
  ) %>%
  transmute(
    geo_level = "county",
    geo_id = stcofips,
    geo_name = append_state_abbr(
      dplyr::coalesce(
        county_name_long,
        dplyr::if_else(
          !is.na(countytype) & countytype != "",
          paste(county, countytype),
          county
        ),
        stcofips
      ),
      dplyr::coalesce(state_abbr, stateabbrv)
    ),
    year = nri_release_year,
    population_weight = population_weight,
    !!!build_metric_exprs(selected_metric_map)
  ) %>%
  filter(!is.na(geo_id), !is.na(year)) %>%
  distinct()

# 5. Rebase county rows to CBSA using staged population weights ----
# The FEMA NRI provider file has no native CBSA geometry, so we derive metro rows
# by joining county-equivalent rows to the current county->CBSA crosswalk. The
# selected risk and hazard metrics are treated as score-like fields and rolled
# with population-weighted means for the first pass.
fema_nri_cbsa <- fema_nri_county %>%
  left_join(
    cbsa_county_xwalk,
    by = c("geo_id" = "county_geoid")
  ) %>%
  filter(!is.na(cbsa_code), cbsa_code != "") %>%
  group_by(cbsa_code, cbsa_name, year) %>%
  summarize(
    across(
      dplyr::all_of(selected_metric_names),
      ~ safe_weighted_mean(.x, population_weight)
    ),
    .groups = "drop"
  ) %>%
  transmute(
    geo_level = "cbsa",
    geo_id = cbsa_code,
    geo_name = cbsa_name,
    year = as.integer(year),
    dplyr::across(dplyr::all_of(selected_metric_names))
  )

# 6. Materialize Silver ----
fema_nri <- bind_rows(
  fema_nri_county %>%
    select(-population_weight),
  fema_nri_cbsa
) %>%
  arrange(geo_level, geo_id, year)

check_unique_annual_grain(fema_nri, "silver.fema_nri")

tryCatch(
  {
    DBI::dbWriteTable(
      con,
      DBI::Id(schema = "silver", table = "fema_nri"),
      fema_nri,
      overwrite = TRUE
    )

    DBI::dbExecute(con, "CHECKPOINT")
  },
  finally = {
    if (DBI::dbIsValid(con)) {
      DBI::dbDisconnect(con, shutdown = TRUE)
    }
  }
)
