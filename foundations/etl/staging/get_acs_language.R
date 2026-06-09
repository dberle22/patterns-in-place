# In this script we get our ACS language raw data

# Find our current directory
getwd()

# Set up our environment ----
here::i_am("foundations/etl/staging/get_acs_language.R")
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

bronze_acs <- get_env_path("DATA_DEMO_RAW")
db_path <- get_env_path("DB_PATH")

# Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# Load ACS Vars ----
acs_v24 <- load_variables(year = "2024", dataset = "acs5", cache = TRUE)

# Language spoken at home by ability to speak English (B16001) ----
# The full B16001 layout reaches its current 128-column shape in ACS 2016.
language_vars <- acs_v24 %>%
  dplyr::filter(stringr::str_detect(name, "^B16001_")) %>%
  dplyr::mutate(
    label_core = label %>%
      stringr::str_remove("^Estimate!!Total:") %>%
      stringr::str_remove("^!!"),
    label_core = dplyr::if_else(label_core == "", "Total", label_core),
    label_core = stringr::str_replace_all(label_core, "less than \"very well\"", "less than very well"),
    label_core = iconv(label_core, from = "", to = "ASCII//TRANSLIT"),
    clean_name = paste0("language_", janitor::make_clean_names(stringr::str_replace_all(label_core, "!!", "_")))
  )

vars <- stats::setNames(language_vars$name, language_vars$clean_name)

tract_states <- resolve_tract_state_scope()

write_geo_slice <- function(geography, table_name, years, state = NULL) {
  acs_raw <- acs_ingest(
    geography = geography,
    state = state,
    years = years,
    variables = vars,
    survey = "acs5",
    output = "wide"
  )

  dbWriteTable(
    con,
    DBI::Id(schema = "staging", table = table_name),
    acs_raw,
    overwrite = TRUE
  )
}

# Ingest Data ----
## US
write_geo_slice("us", "acs_language_us", 2016:2024)
## Region
write_geo_slice("region", "acs_language_region", 2016:2024)
## Division
write_geo_slice("division", "acs_language_division", 2016:2024)
## State
write_geo_slice("state", "acs_language_state", 2016:2024)
## County
write_geo_slice("county", "acs_language_county", 2016:2024)
## ZCTA
write_geo_slice("zcta", "acs_language_zcta", 2016:2024)
## Place
write_geo_slice("place", "acs_language_place", 2016:2024)
## Tract
write_geo_slice("tract", "acs_language_tract", 2016:2024, state = tract_states)

# Legacy: preserve existing state-level tract ingest tables for compatibility
# write_geo_slice("tract", "acs_language_tract_fl", 2016:2024, state = "FL")
# write_geo_slice("tract", "acs_language_tract_nc", 2016:2024, state = "NC")
# write_geo_slice("tract", "acs_language_tract_ga", 2016:2024, state = "GA")
# write_geo_slice("tract", "acs_language_tract_sc", 2016:2024, state = "SC")

dbDisconnect(con, shutdown = TRUE)
