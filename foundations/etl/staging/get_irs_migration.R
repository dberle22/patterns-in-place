# In this script we get IRS Migration Data scraped directly from their website

# Set up our environment
# Create a single ingestion test
# Build our staging file
# Loop over all years

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
raw_dir <- file.path(data, "demographics", "raw", "irs")
db_path <- get_env_path("DB_PATH")

## Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# Year range for IRS (can adjust later)
irs_years <- 2011:2022

## Download a single IRS Year to test ----
library(httr)

# Test destination year (e.g. 2022 for 2021–2022 migration)
test_year <- 2022L

prev_year <- test_year - 1L

# Build 4-digit code: YY(Prev) + YY(Current) → "2122"
code_prev <- substr(prev_year, 3, 4)  # "21"
code_curr <- substr(test_year,  3, 4) # "22"
code      <- paste0(code_prev, code_curr)


outflow_county_url  <- glue("https://www.irs.gov/pub/irs-soi/countyoutflow{code}.csv")
outflow_county_file <- file.path(raw_dir, glue("outflow{code}.csv"))


inflow_county_url <- glue("https://www.irs.gov/pub/irs-soi/countyinflow{code}.csv")
inflow_county_file <- file.path(raw_dir, glue("inflow{code}.csv"))

# Ingest inflow test
if (!file.exists(inflow_county_file)) {
  resp <- httr::GET(
    inflow_county_url,
    user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)  # will error with a clear message if bad
  
  writeBin(content(resp, "raw"), inflow_county_file)
}

irs_inflow_raw <- read_csv(inflow_county_file) %>%
  clean_names()


flow_test <- irs_inflow_raw %>%
  filter(str_detect(y1_countyname, "Autauga County"))

# Ingest outflow test
if (!file.exists(outflow_county_file)) {
  resp <- httr::GET(
    outflow_county_url,
    user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
  )
  httr::stop_for_status(resp)  # will error with a clear message if bad
  
  writeBin(content(resp, "raw"), outflow_county_file)
}

irs_outflow_raw <- read_csv(outflow_county_file) %>%
  clean_names()

# Test Inflows vs Outflows
## Read in XWalk
county_state_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state")

# LA County - "06037"
test_inflow <- irs_inflow_raw %>%
  transmute(
    y2_state_fips  = str_pad(as.character(y2_statefips), 2, pad = "0"),
    y2_county_fips = str_pad(as.character(y2_countyfips), 3, pad = "0"),
    y2_geoid = paste0(y2_state_fips, y2_county_fips),
    y2_state,
    y2_countyname,
    y1_state_fips    = str_pad(as.character(y1_statefips), 2, pad = "0"),
    y1_county_fips   = str_pad(as.character(y1_countyfips), 3, pad = "0"),
    y1_geoid   = paste0(y1_state_fips,   y1_county_fips),
    n1 = n1,
    n2 = n2
  ) %>%
  left_join(county_state_xwalk %>% 
              select(county_geoid, y1_county_name_long = county_name_long, y1_state_abbr = state_abbr),
            by = c("y1_geoid" = "county_geoid")) %>%
  left_join(county_state_xwalk %>% 
              select(county_geoid, y2_county_name_long = county_name_long, y2_state_abbr = state_abbr),
            by = c("y2_geoid" = "county_geoid")) %>%
  select(y2_geoid, y2_countyname, y2_state, y2_county_name_long, y2_state_abbr,
         y1_geoid, y1_county_name_long, y1_state_abbr,
         n1, n2) %>%
  filter(y2_geoid == "06037" | y1_geoid == "06037")


## Create our Staging data ----
## Split into two tables: county <> county flows, rolled up flows
## Fix FIPs codes, rename columns 
## Create Flow ID

### County <> County ----
irs_county_inflow <- irs_inflow_raw %>%
  # Must have FIPS on both sides
  filter(
    !is.na(y1_statefips),
    !is.na(y1_countyfips),
    !is.na(y2_statefips),
    !is.na(y2_countyfips)
  ) %>%
  # Valid state and county ranges (domestic counties)
  filter(
    dplyr::between(y1_statefips, 1, 56),
    dplyr::between(y2_statefips, 1, 56),
    dplyr::between(y1_countyfips, 1, 840),
    dplyr::between(y2_countyfips, 1, 840)
  ) %>%
  # Pad FIPS and build GEOIDs
  mutate(
    origin_state_fips  = str_pad(as.character(y2_statefips), 2, pad = "0"),
    origin_county_fips = str_pad(as.character(y2_countyfips), 3, pad = "0"),
    dest_state_fips    = str_pad(as.character(y1_statefips), 2, pad = "0"),
    dest_county_fips   = str_pad(as.character(y1_countyfips), 3, pad = "0"),
    
    origin_geoid = paste0(origin_state_fips, origin_county_fips),
    dest_geoid   = paste0(dest_state_fips,   dest_county_fips),
    dest_county_name = y1_countyname,
    dest_year = test_year,
    origin_year = prev_year
  ) %>%
  # Drop within-county non-migrants
  filter(origin_geoid != dest_geoid) %>%
  # Clean measures (IRS suppression: -1 → NA) and AGI in dollars
  mutate(
    n_returns      = if_else(n1  < 0, NA_real_, as.numeric(n1)),
    n_exemptions   = if_else(n2  < 0, NA_real_, as.numeric(n2)),
    agi_thousands  = if_else(agi < 0, NA_real_, as.numeric(agi)),
    agi            = agi_thousands * 1000
  ) %>%
  # Optional unique flow id
  mutate(
    flow_id = paste(dest_year, origin_geoid, dest_geoid, sep = "_")
  ) %>%
  # Select normalized columns only
  select(
    flow_id,
    origin_year, dest_year,
    dest_state_fips,   dest_county_fips,   dest_geoid, dest_county_name,
    origin_state_fips, origin_county_fips, origin_geoid, 
    n_returns, n_exemptions,
    agi_thousands, agi
  )

### County <> Summary ----

#### We will finalize this later 
irs_summary_inflow <- irs_inflow_raw %>%
  # We assume clean_names() already called upstream
  # Focus on rows that are "Total Migration-..." style for destination counties
  filter(
    !is.na(y1_statefips),
    !is.na(y1_countyfips),
    y1_countyfips != 0,                                   # real destination counties
    str_detect(y1_countyname, "Total Migration")
  ) %>%
  mutate(
    # Destination county (inflow file: Y1 is destination)
    dest_state_fips  = str_pad(as.character(y1_statefips), 2, pad = "0"),
    dest_county_fips = str_pad(as.character(y1_countyfips), 3, pad = "0"),
    dest_geoid       = paste0(dest_state_fips, dest_county_fips),
    origin_state_fips  = str_pad(as.character(y2_statefips), 2, pad = "0"),
    origin_county_fips = str_pad(as.character(y2_countyfips), 3, pad = "0"),
    
    # Classify which summary bucket this is for that destination county
    inflow_summary_type = case_when(
      str_detect(y1_countyname, "US and Foreign")       ~ "us_and_foreign_total",
      str_detect(y1_countyname, "Total Migration-US$")  ~ "us_total",
      str_detect(y1_countyname, "Same State")           ~ "same_state_total",
      str_detect(y1_countyname, "Different State")      ~ "different_state_total",
      str_detect(y1_countyname, "Foreign")              ~ "foreign_total",
      TRUE                                              ~ "other_summary"
    ),
    
    # Clean numeric measures
    n_returns     = if_else(n1  < 0, NA_real_, as.numeric(n1)),
    n_exemptions  = if_else(n2  < 0, NA_real_, as.numeric(n2)),
    agi_thousands = if_else(agi < 0, NA_real_, as.numeric(agi)),
    agi           = agi_thousands * 1000,
    
    dest_year   = test_year,
    origin_year = prev_year
  ) %>%
  select(
    origin_year, dest_year,
    dest_state_fips, dest_county_fips, dest_geoid,
    y1_countyname,
    origin_state_fips, origin_county_fips,
    inflow_summary_type,
    n_returns, n_exemptions,
    agi_thousands, agi
  )

# Create scaled County Inflow pipeline ----
## Create an ingestion loop ----
# Destination years you want (e.g., 2012–2022: 2011–12 up to 2021–22)
irs_dest_years <- 2012:2022

for (yy in irs_dest_years) {
  prev_year <- yy - 1L
  code_prev <- substr(prev_year, 3, 4)
  code_curr <- substr(yy,        3, 4)
  code      <- paste0(code_prev, code_curr)  # "1112", "2122", etc.
  
  inflow_url  <- glue("https://www.irs.gov/pub/irs-soi/countyinflow{code}.csv")
  inflow_file <- file.path(raw_dir, glue("countyinflow{code}.csv"))
  
  message("Downloading inflow ", prev_year, "-", yy, " as ", basename(inflow_file))
  
  if (!file.exists(inflow_file)) {
    resp <- httr::GET(
      inflow_url,
      user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
    )
    httr::stop_for_status(resp)
    writeBin(content(resp, "raw"), inflow_file)
  } else {
    message("  -> already exists, skipping")
  }
}

## Create list of files and inspect names ----

inflow_files <- list.files(
  raw_dir,
  pattern = "^countyinflow\\d{4}\\.csv$",
  full.names = TRUE
)


for (file_i in inflow_files) {
  fname <- basename(file_i)
  message("\n---- ", fname, " ----")
  
  df <- read_csv(file_i, show_col_types = FALSE) %>%
    clean_names()
  
  print(names(df))
}

## Read data and normalize ----
irs_county_inflow_list <- map(
  inflow_files,
  \(file_i) {
    fname <- basename(file_i)
    code  <- str_extract(fname, "\\d{4}")   # e.g. "1112"
    
    # YYYY: 11 12 -> 2011, 2012
    y1_short    <- as.integer(substr(code, 1, 2))
    y2_short    <- as.integer(substr(code, 3, 4))
    origin_year <- 2000L + y1_short
    dest_year   <- 2000L + y2_short
    
    message("Cleaning ", fname, " for migration ", origin_year, "-", dest_year)
    
    irs_raw <- read_csv(file_i, show_col_types = FALSE) %>%
      clean_names() %>%
      # Coerce FIPS columns to numeric to avoid type issues
      mutate(
        y1_statefips  = as.numeric(y1_statefips),
        y1_countyfips = as.numeric(y1_countyfips),
        y2_statefips  = as.numeric(y2_statefips),
        y2_countyfips = as.numeric(y2_countyfips)
      )
    
    # ---------- County <-> County inflow for this file ----------
    irs_county_inflow <- irs_raw %>%
      # Must have FIPS on both sides
      filter(
        !is.na(y1_statefips),
        !is.na(y1_countyfips),
        !is.na(y2_statefips),
        !is.na(y2_countyfips)
      ) %>%
      # Valid state and county ranges (domestic counties)
      filter(
        dplyr::between(y1_statefips, 1, 56),
        dplyr::between(y2_statefips, 1, 56),
        dplyr::between(y1_countyfips, 1, 840),
        dplyr::between(y2_countyfips, 1, 840)
      ) %>%
      # Map origin (Y1) and destination (Y2), pad FIPS and build GEOIDs
      mutate(
        origin_state_fips  = str_pad(as.character(y2_statefips), 2, pad = "0"),
        origin_county_fips = str_pad(as.character(y2_countyfips), 3, pad = "0"),
        dest_state_fips    = str_pad(as.character(y1_statefips), 2, pad = "0"),
        dest_county_fips   = str_pad(as.character(y1_countyfips), 3, pad = "0"),
        
        origin_geoid = paste0(origin_state_fips, origin_county_fips),
        dest_geoid   = paste0(dest_state_fips,   dest_county_fips),
        dest_county_name = y1_countyname,
        origin_year = origin_year,
        dest_year   = dest_year,
        year        = dest_year   # canonical analysis year
      ) %>%
      # Drop within-county non-migrants
      filter(origin_geoid != dest_geoid) %>%
      # Clean measures (IRS suppression: -1 → NA) and AGI in dollars
      mutate(
        n_returns      = if_else(n1  < 0, NA_real_, as.numeric(n1)),
        n_exemptions   = if_else(n2  < 0, NA_real_, as.numeric(n2)),
        agi_thousands  = if_else(agi < 0, NA_real_, as.numeric(agi)),
        agi            = agi_thousands * 1000
      ) %>%
      # Unique flow id: year_origin_dest
      mutate(
        flow_id = paste(year, origin_geoid, dest_geoid, sep = "_")
      ) %>%
      select(
        flow_id,
        year, origin_year, dest_year,
        dest_county_name, dest_state_fips,   dest_county_fips,   dest_geoid,
        origin_state_fips, origin_county_fips, origin_geoid,
        n_returns, n_exemptions,
        agi_thousands, agi
      )
    
    # Return just county flows for this file
    list(
      county = irs_county_inflow
    )
  }
)

# Bind all years into one staging data frame
irs_county_inflow_all <- map_dfr(irs_county_inflow_list, "county") %>%
  mutate(
    across(
      where(is.character),
      ~ iconv(.x, from = "", to = "UTF-8", sub = "")
    )
  )

# Quick sanity check
irs_county_inflow_all %>% count(year)

## Create Staging table
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="irs_inflow_migration_county"),
                  irs_county_inflow_all, overwrite = TRUE)

# Create scaled State Inflow pipeline ----
## Create an ingestion loop ----
# Destination years you want (e.g., 2012–2022: 2011–12 up to 2021–22)
irs_dest_years <- 2012:2022


for (yy in irs_dest_years) {
  prev_year <- yy - 1L
  code_prev <- substr(prev_year, 3, 4)
  code_curr <- substr(yy,        3, 4)
  code      <- paste0(code_prev, code_curr)  # "1112", "2122", etc.
  
  inflow_url  <- glue("https://www.irs.gov/pub/irs-soi/stateinflow{code}.csv")
  inflow_file <- file.path(raw_dir, glue("stateinflow{code}.csv"))
  
  message("Downloading inflow ", prev_year, "-", yy, " as ", basename(inflow_file))
  
  if (!file.exists(inflow_file)) {
    resp <- httr::GET(
      inflow_url,
      user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
    )
    httr::stop_for_status(resp)
    writeBin(content(resp, "raw"), inflow_file)
  } else {
    message("  -> already exists, skipping")
  }
}

## Create list of files and inspect names ----

inflow_files <- list.files(
  raw_dir,
  pattern = "^stateinflow\\d{4}\\.csv$",
  full.names = TRUE
)


for (file_i in inflow_files) {
  fname <- basename(file_i)
  message("\n---- ", fname, " ----")
  
  df <- read_csv(file_i, show_col_types = FALSE) %>%
    clean_names()
  
  print(names(df))
}

## Read data and normalize ----
irs_inflow_list <- map(
  inflow_files,
  \(file_i) {
    fname <- basename(file_i)
    code  <- str_extract(fname, "\\d{4}")   # e.g. "1112"
    
    # YYYY: 11 12 -> 2011, 2012
    y1_short    <- as.integer(substr(code, 1, 2))
    y2_short    <- as.integer(substr(code, 3, 4))
    origin_year <- 2000L + y1_short
    dest_year   <- 2000L + y2_short
    
    message("Cleaning ", fname, " for migration ", origin_year, "-", dest_year)
    
    irs_raw <- read_csv(file_i, show_col_types = FALSE) %>%
      clean_names() %>%
      # Coerce FIPS columns to numeric to avoid type issues
      mutate(
        y1_statefips  = as.numeric(y1_statefips),
        y2_statefips  = as.numeric(y2_statefips)
      )
    
    # ---------- County <-> County inflow for this file ----------
    irs_state_inflow <- irs_raw %>%
      # Must have FIPS on both sides
      filter(
        !is.na(y1_statefips),
        !is.na(y2_statefips)
      ) %>%
      # Valid state and county ranges (domestic counties)
      filter(
        dplyr::between(y1_statefips, 1, 56),
        dplyr::between(y2_statefips, 1, 56)
      ) %>%
      # Map origin (Y1) and destination (Y2), pad FIPS and build GEOIDs
      mutate(
        origin_state_fips  = str_pad(as.character(y2_statefips), 2, pad = "0"),
        dest_state_fips    = str_pad(as.character(y1_statefips), 2, pad = "0"),
        
        dest_state_name = y1_state_name,
        origin_year = origin_year,
        dest_year   = dest_year,
        year        = dest_year   # canonical analysis year
      ) %>%
      # Drop within-county non-migrants
      filter(origin_state_fips != dest_state_fips) %>%
      # Clean measures (IRS suppression: -1 → NA) and AGI in dollars
      mutate(
        n_returns      = if_else(n1  < 0, NA_real_, as.numeric(n1)),
        n_exemptions   = if_else(n2  < 0, NA_real_, as.numeric(n2)),
        agi_thousands  = if_else(agi < 0, NA_real_, as.numeric(agi)),
        agi            = agi_thousands * 1000
      ) %>%
      # Unique flow id: year_origin_dest
      mutate(
        flow_id = paste(year, origin_state_fips, dest_state_fips, sep = "_")
      ) %>%
      select(
        flow_id,
        year, origin_year, dest_year,
        dest_state_name, dest_state_fips, 
        origin_state_fips, 
        n_returns, n_exemptions,
        agi_thousands, agi
      )
    
    # Return just county flows for this file
    list(
      state = irs_state_inflow
    )
  }
)

# Bind all years into one staging data frame
irs_state_inflow_all <- map_dfr(irs_inflow_list, "state")

# Quick sanity check
irs_state_inflow_all %>% count(year)

## Create Staging table ----
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="irs_inflow_migration_state"),
                  irs_state_inflow_all, overwrite = TRUE)

# Shutdown ----
dbDisconnect(con, shutdown = TRUE)