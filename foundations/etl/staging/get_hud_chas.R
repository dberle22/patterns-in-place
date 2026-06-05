# In this script we get HUD CHAS Data scraped directly from their website

# Find our current directory 
getwd()

# Set up our environment ----
# Read our common libraries & set other packages
source(here::here("foundations", "etl", "utils.R"))


# Set paths for our environments
# Make sure we're reading from the project Renviron
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Set our Paths - Pointing to our Bronze folder in Data
data <- get_env_path("DATA")
raw_dir <- file.path(data, "demographics", "raw", "hud")
db_path <- get_env_path("DB_PATH")

## Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# Ingest files from Bronze ----
## Set file paths 
chas_state_file <- file.path(raw_dir, "HUD_CHAS/2017thru2021-040-csv/040/Table7.csv")
chas_county_file <- file.path(raw_dir, "HUD_CHAS/2017thru2021-050-csv/050/Table7.csv")
chas_place_file <- file.path(raw_dir, "HUD_CHAS/2017thru2021-160-csv/160/Table7.csv")
chas_tract_file <- file.path(raw_dir, "HUD_CHAS/2017thru2021-140-csv/140/Table7.csv")
chas_metadata_file <- file.path(raw_dir, "HUD_CHAS/2017thru2021-040-csv/CHAS data dictionary 17-21.xlsx")

## Read data 
chas_metadata <- read_excel(chas_metadata_file, sheet = "Table 7")
chas_state <- read_csv(chas_state_file)
chas_county <- read_csv(chas_county_file)
chas_place <- read_csv(chas_place_file)
chas_tract <- read_csv(chas_tract_file)

## Set CHAS year
chas_period <- "2017-2021"
chas_year <- 2021L

# Identify Vars to keep for Staging ----

# 1) Denominator variables are hard-coded
denom_vars <- c("T7_est1", "T7_est2", "T7_est108")

# 2) Detail variables: Tenure/Income/Burden combos you use

income_keep <- c(
  "household income is less than or equal to 30% of HAMFI",
  "household income is greater than 30% but less than or equal to 50% of HAMFI",
  "household income is greater than 50% but less than or equal to 80% of HAMFI",
  "household income is greater than 80% but less than or equal to 100% of HAMFI",
  "household income is greater than 100% of HAMFI"
)

burden_keep <- c(
  "housing cost burden is less than or equal to 30%",
  "housing cost burden is greater than 30% but less than or equal to 50%",
  "housing cost burden is greater than 50%"
)

tenure_keep <- c("Owner occupied", "Renter occupied")

# Create Vars list
detail_vars <- chas_metadata %>%
  filter(
    `Household income` %in% income_keep,
    `Cost burden` %in% burden_keep,
    Tenure %in% tenure_keep
  ) %>%
  pull(`Column Name`) %>%
  unique()

vars_needed <- unique(c(denom_vars, detail_vars))

# Create Long DFs and filter Vars ----
# Make our data set long, join to our metadata table to bring variable names
## County ----
chas_county_long <- chas_county %>%
  select(source:cnty, all_of(vars_needed)) %>%
  pivot_longer(
    cols = all_of(vars_needed),
    names_to = "variable",
    values_to = "estimate"
  ) %>%
  left_join(chas_metadata, by = c("variable" = "Column Name")) %>%
  mutate(
    chas_period = chas_period,
    year        = chas_year,
    geo_level   = "County",
    # Standardized GEOIDs (you can tweak if you prefer geoid from HUD)
    county_geoid = paste0(st, str_pad(cnty, 3, pad = "0"))
    # You can add tract_geoid / place_geoid later if needed
  ) %>%
  clean_names() %>%
  mutate(
    across(
      where(is.character),
      ~ iconv(.x, from = "", to = "UTF-8", sub = "")
    )
  )

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="hud_chas_county"),
                  chas_county_long, overwrite = TRUE)

## Place ----
chas_place_long <- chas_place %>%
  select(source:place, all_of(vars_needed)) %>%
  pivot_longer(
    cols = all_of(vars_needed),
    names_to = "variable",
    values_to = "estimate"
  ) %>%
  left_join(chas_metadata, by = c("variable" = "Column Name")) %>%
  mutate(
    chas_period = chas_period,
    year        = chas_year,
    geo_level   = "Place",
    # Standardized GEOIDs (you can tweak if you prefer geoid from HUD)
    place_geoid = paste0(st, str_pad(place, 5, pad = "0"))
    # You can add tract_geoid / place_geoid later if needed
  ) %>%
  clean_names() %>%
  mutate(
    across(
      where(is.character),
      ~ iconv(.x, from = "", to = "UTF-8", sub = "")
    )
  )

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="hud_chas_place"),
                  chas_place_long, overwrite = TRUE)

## State ----
chas_state_long <- chas_state %>%
  select(source:st, all_of(vars_needed)) %>%
  pivot_longer(
    cols = all_of(vars_needed),
    names_to = "variable",
    values_to = "estimate"
  ) %>%
  left_join(chas_metadata, by = c("variable" = "Column Name")) %>%
  mutate(
    chas_period = chas_period,
    year        = chas_year,
    geo_level   = "State",
    # Standardized GEOIDs (you can tweak if you prefer geoid from HUD)
    place_geoid = str_pad(st, 2, pad = "0")
    # You can add tract_geoid / place_geoid later if needed
  ) %>%
  clean_names()

DBI::dbWriteTable(con, DBI::Id(schema="staging", table="hud_chas_state"),
                  chas_state_long, overwrite = TRUE)

# Shutdown ----
dbDisconnect(con, shutdown = TRUE)

