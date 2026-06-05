# In this script we normalize BPS data into our Silver layer

# 1. Set up our Environment
# 2. Read in our Staging Data to R Data Frames
# 3. Build Final Tables
# 3.1. Add XWalks for CBSA
# 3.2. Select metrics
# 3.3. Build simple KPIs
# 4. Materialize to Silver

# Find our current directory 
getwd()

# 1. Set up our environment ----
# Read our common libraries & set other packages
source(here::here("foundations", "etl", "utils.R"))


# Set paths for our environments
# Make sure we're reading from the project Renviron
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Set our Paths - Pointing to our Bronze folder in Data
db_path <- get_env_path("DB_PATH")

## Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

### List the tables available in the DB
tables <- dbListTables(con)
print(tables)

# 2. Read in our Staging Data to R Data Frames ----

## Metric Tables ----
bps_region <- dbGetQuery(con, "SELECT * FROM staging.bps_region")
bps_division <- dbGetQuery(con, "SELECT * FROM staging.bps_division")
bps_state <- dbGetQuery(con, "SELECT * FROM staging.bps_state")
bps_county <- dbGetQuery(con, "SELECT * FROM staging.bps_county")
bps_place <- dbGetQuery(con, "SELECT * FROM staging.bps_place")


## CBSA <> County Xwalk ----
cbsa_county_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county")
county_state_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state")

# 3. Build Final Tables ----
## Region ----
### Select Metrics & Vars ----
bps_region_clean <- bps_region %>% 
  clean_names() %>%
  mutate(period = as.integer(year),
         geo_level = "Region",
         geo_id = as.character(region_code)) %>%
  select(geo_level, geo_id, geo_name = region_name, period, 
         total_bldgs, total_units, total_value,
         bldgs_1_unit, bldgs_2_units, bldgs_3_4_units, bldgs_5_units,
         units_1_unit, units_2_units, units_3_4_units, units_5_units,
         value_1_unit, value_2_units, value_3_4_units, value_5_units) %>%
  mutate(
    # Multifamily groupings
    units_multifam  = units_2_units + units_3_4_units + units_5_units,
    bldgs_multifam  = bldgs_2_units + bldgs_3_4_units + bldgs_5_units,
    value_multifam  = value_2_units + value_3_4_units + value_5_units,
    
    # Averages
    avg_units_per_bldg = if_else(
      total_bldgs > 0,
      total_units / total_bldgs,
      NA_real_
    ),
    avg_units_per_mf_bldg = if_else(
      bldgs_multifam > 0,
      units_multifam / bldgs_multifam,
      NA_real_
    ),
    
    # Shares
    share_multifam_units = if_else(
      total_units > 0,
      units_multifam / total_units,
      NA_real_
    ),
    share_units_5_plus = if_else(
      total_units > 0,
      units_5_units / total_units,
      NA_real_
    ),
    share_units_1_unit = if_else(
      total_units > 0,
      units_1_unit / total_units,
      NA_real_
    ),
    
    # Simple mix label (optional, tweak thresholds if you like)
    structure_mix = case_when(
      !is.na(share_units_5_plus)   & share_units_5_plus   >= 0.50 ~ "mostly_large_multifam",
      !is.na(share_multifam_units) & share_multifam_units >= 0.50 ~ "mostly_multifam",
      TRUE ~ "mostly_single_family"
    )
  )
  
## Division ----
### Select Metrics & Vars ----
bps_division_clean <- bps_division %>% 
  clean_names() %>%
  mutate(period = as.integer(year),
         geo_level = "Division",
         geo_id = as.character(division_code)) %>%
  select(geo_level, geo_id, geo_name = division_name, period, 
         total_bldgs, total_units, total_value,
         bldgs_1_unit, bldgs_2_units, bldgs_3_4_units, bldgs_5_units,
         units_1_unit, units_2_units, units_3_4_units, units_5_units,
         value_1_unit, value_2_units, value_3_4_units, value_5_units) %>%
  mutate(
    # Multifamily groupings
    units_multifam  = units_2_units + units_3_4_units + units_5_units,
    bldgs_multifam  = bldgs_2_units + bldgs_3_4_units + bldgs_5_units,
    value_multifam  = value_2_units + value_3_4_units + value_5_units,
    
    # Averages
    avg_units_per_bldg = if_else(
      total_bldgs > 0,
      total_units / total_bldgs,
      NA_real_
    ),
    avg_units_per_mf_bldg = if_else(
      bldgs_multifam > 0,
      units_multifam / bldgs_multifam,
      NA_real_
    ),
    
    # Shares
    share_multifam_units = if_else(
      total_units > 0,
      units_multifam / total_units,
      NA_real_
    ),
    share_units_5_plus = if_else(
      total_units > 0,
      units_5_units / total_units,
      NA_real_
    ),
    share_units_1_unit = if_else(
      total_units > 0,
      units_1_unit / total_units,
      NA_real_
    ),
    
    # Simple mix label (optional, tweak thresholds if you like)
    structure_mix = case_when(
      !is.na(share_units_5_plus)   & share_units_5_plus   >= 0.50 ~ "mostly_large_multifam",
      !is.na(share_multifam_units) & share_multifam_units >= 0.50 ~ "mostly_multifam",
      TRUE ~ "mostly_single_family"
    )
  )

## State ----
### Select Metrics & Vars ----
bps_state_clean <- bps_state %>% 
  clean_names() %>%
  mutate(period = as.integer(year),
         geo_level = "State",
         geo_id = as.character(state_code)) %>%
  select(geo_level, geo_id, geo_name = state_name, period, 
         total_bldgs, total_units, total_value,
         bldgs_1_unit, bldgs_2_units, bldgs_3_4_units, bldgs_5_units,
         units_1_unit, units_2_units, units_3_4_units, units_5_units,
         value_1_unit, value_2_units, value_3_4_units, value_5_units) %>%
  mutate(
    # Multifamily groupings
    units_multifam  = units_2_units + units_3_4_units + units_5_units,
    bldgs_multifam  = bldgs_2_units + bldgs_3_4_units + bldgs_5_units,
    value_multifam  = value_2_units + value_3_4_units + value_5_units,
    
    # Averages
    avg_units_per_bldg = if_else(
      total_bldgs > 0,
      total_units / total_bldgs,
      NA_real_
    ),
    avg_units_per_mf_bldg = if_else(
      bldgs_multifam > 0,
      units_multifam / bldgs_multifam,
      NA_real_
    ),
    
    # Shares
    share_multifam_units = if_else(
      total_units > 0,
      units_multifam / total_units,
      NA_real_
    ),
    share_units_5_plus = if_else(
      total_units > 0,
      units_5_units / total_units,
      NA_real_
    ),
    share_units_1_unit = if_else(
      total_units > 0,
      units_1_unit / total_units,
      NA_real_
    ),
    
    # Simple mix label (optional, tweak thresholds if you like)
    structure_mix = case_when(
      !is.na(share_units_5_plus)   & share_units_5_plus   >= 0.50 ~ "mostly_large_multifam",
      !is.na(share_multifam_units) & share_multifam_units >= 0.50 ~ "mostly_multifam",
      TRUE ~ "mostly_single_family"
    )
  )


## County ----
### Select Metrics & Vars ----
bps_county_clean <- bps_county %>% 
  clean_names() %>%
  mutate(period = as.integer(year),
         geo_level = "County",
         geo_id = fips_county_5_digits) %>%
  select(geo_level, geo_id, geo_name = county_name, period, 
         total_bldgs, total_units, total_value,
         bldgs_1_unit, bldgs_2_units, bldgs_3_4_units, bldgs_5_units,
         units_1_unit, units_2_units, units_3_4_units, units_5_units,
         value_1_unit, value_2_units, value_3_4_units, value_5_units) %>%
  mutate(
    # Multifamily groupings
    units_multifam  = units_2_units + units_3_4_units + units_5_units,
    bldgs_multifam  = bldgs_2_units + bldgs_3_4_units + bldgs_5_units,
    value_multifam  = value_2_units + value_3_4_units + value_5_units,
    
    # Averages
    avg_units_per_bldg = if_else(
      total_bldgs > 0,
      total_units / total_bldgs,
      NA_real_
    ),
    avg_units_per_mf_bldg = if_else(
      bldgs_multifam > 0,
      units_multifam / bldgs_multifam,
      NA_real_
    ),
    
    # Shares
    share_multifam_units = if_else(
      total_units > 0,
      units_multifam / total_units,
      NA_real_
    ),
    share_units_5_plus = if_else(
      total_units > 0,
      units_5_units / total_units,
      NA_real_
    ),
    share_units_1_unit = if_else(
      total_units > 0,
      units_1_unit / total_units,
      NA_real_
    ),
    
    # Simple mix label (optional, tweak thresholds if you like)
    structure_mix = case_when(
      !is.na(share_units_5_plus)   & share_units_5_plus   >= 0.50 ~ "mostly_large_multifam",
      !is.na(share_multifam_units) & share_multifam_units >= 0.50 ~ "mostly_multifam",
      TRUE ~ "mostly_single_family"
    )
  )

## CBSA ----
bps_cbsa_clean <- bps_county %>% 
  clean_names() %>%
  mutate(period = as.integer(year),
         geo_id = fips_county_5_digits) %>%
  select(geo_id, geo_name = county_name, period, 
         total_bldgs, total_units, total_value,
         bldgs_1_unit, bldgs_2_units, bldgs_3_4_units, bldgs_5_units,
         units_1_unit, units_2_units, units_3_4_units, units_5_units,
         value_1_unit, value_2_units, value_3_4_units, value_5_units) %>%
  left_join(cbsa_county_xwalk %>% select(cbsa_code, cbsa_name, county_geoid),
            by = c("geo_id" = "county_geoid")) %>%
  group_by(cbsa_code, cbsa_name, period) %>%
  summarize(total_bldgs = sum(total_bldgs, na.rm = TRUE),
            total_units = sum(total_units, na.rm = TRUE),
            total_value = sum(total_value, na.rm = TRUE),
            
            bldgs_1_unit    = sum(bldgs_1_unit,    na.rm = TRUE),
            bldgs_2_units   = sum(bldgs_2_units,   na.rm = TRUE),
            bldgs_3_4_units = sum(bldgs_3_4_units, na.rm = TRUE),
            bldgs_5_units   = sum(bldgs_5_units,   na.rm = TRUE),
            
            units_1_unit    = sum(units_1_unit,    na.rm = TRUE),
            units_2_units   = sum(units_2_units,   na.rm = TRUE),
            units_3_4_units = sum(units_3_4_units, na.rm = TRUE),
            units_5_units   = sum(units_5_units,   na.rm = TRUE),
            
            value_1_unit    = sum(value_1_unit,    na.rm = TRUE),
            value_2_units   = sum(value_2_units,   na.rm = TRUE),
            value_3_4_units = sum(value_3_4_units, na.rm = TRUE),
            value_5_units   = sum(value_5_units,   na.rm = TRUE)
            ) %>%
  ungroup() %>%
  mutate(geo_level = "CBSA",
         # Multifamily groupings
         units_multifam  = units_2_units + units_3_4_units + units_5_units,
         bldgs_multifam  = bldgs_2_units + bldgs_3_4_units + bldgs_5_units,
         value_multifam  = value_2_units + value_3_4_units + value_5_units,
         
         # Averages
         avg_units_per_bldg = if_else(
           total_bldgs > 0,
           total_units / total_bldgs,
           NA_real_
         ),
         avg_units_per_mf_bldg = if_else(
           bldgs_multifam > 0,
           units_multifam / bldgs_multifam,
           NA_real_
         ),
         
         # Shares
         share_multifam_units = if_else(
           total_units > 0,
           units_multifam / total_units,
           NA_real_
         ),
         share_units_5_plus = if_else(
           total_units > 0,
           units_5_units / total_units,
           NA_real_
         ),
         share_units_1_unit = if_else(
           total_units > 0,
           units_1_unit / total_units,
           NA_real_
         ),
         
         # Simple mix label (optional, tweak thresholds if you like)
         structure_mix = case_when(
           !is.na(share_units_5_plus)   & share_units_5_plus   >= 0.50 ~ "mostly_large_multifam",
           !is.na(share_multifam_units) & share_multifam_units >= 0.50 ~ "mostly_multifam",
           TRUE ~ "mostly_single_family"
         )
         ) %>%
  select(geo_level, geo_id = cbsa_code, geo_name = cbsa_name, period:value_5_units,
         units_multifam:structure_mix)


## Place ----
### Select Metrics & Vars ----
bps_place_clean <- bps_place %>% 
  clean_names() %>%
  mutate(period = as.integer(year),
         geo_level = "Place",
         geo_id = paste0(state_code, fips_place_code)) %>%
  select(geo_level, geo_id, geo_name = place_name, period, 
         total_bldgs, total_units, total_value,
         bldgs_1_unit, bldgs_2_units, bldgs_3_4_units, bldgs_5_units,
         units_1_unit, units_2_units, units_3_4_units, units_5_units,
         value_1_unit, value_2_units, value_3_4_units, value_5_units) %>%
  mutate(
    # Multifamily groupings
    units_multifam  = units_2_units + units_3_4_units + units_5_units,
    bldgs_multifam  = bldgs_2_units + bldgs_3_4_units + bldgs_5_units,
    value_multifam  = value_2_units + value_3_4_units + value_5_units,
    
    # Averages
    avg_units_per_bldg = if_else(
      total_bldgs > 0,
      total_units / total_bldgs,
      NA_real_
    ),
    avg_units_per_mf_bldg = if_else(
      bldgs_multifam > 0,
      units_multifam / bldgs_multifam,
      NA_real_
    ),
    
    # Shares
    share_multifam_units = if_else(
      total_units > 0,
      units_multifam / total_units,
      NA_real_
    ),
    share_units_5_plus = if_else(
      total_units > 0,
      units_5_units / total_units,
      NA_real_
    ),
    share_units_1_unit = if_else(
      total_units > 0,
      units_1_unit / total_units,
      NA_real_
    ),
    
    # Simple mix label (optional, tweak thresholds if you like)
    structure_mix = case_when(
      !is.na(share_units_5_plus)   & share_units_5_plus   >= 0.50 ~ "mostly_large_multifam",
      !is.na(share_multifam_units) & share_multifam_units >= 0.50 ~ "mostly_multifam",
      TRUE ~ "mostly_single_family"
    )
  )

## Bind data together ----
bps_silver <- rbind(
  bps_region_clean,
  bps_division_clean,
  bps_state_clean,
  bps_cbsa_clean,
  bps_county_clean,
  bps_place_clean
)

## Write to Silver
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bps_wide"),
                  bps_silver, overwrite = TRUE)

# Shutdown ----
dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)