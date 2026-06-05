# In this script we get BEA Data from their API

# Find our current directory 
getwd()

# Set up our environment ----
# Read our common libraries & set other packages
source(here::here("foundations", "etl", "utils.R"))


# Set paths for our environments
# Make sure we're reading from the project Renviron
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Set our Paths - Pointing to our Bronze folder in Data
bea_key <- get_env_path("BEA_KEY")
db_path <- get_env_path("DB_PATH")

## Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)


# Table Metadata ---- 
## Helper Functions ----

`%||%` <- function(x, y) if (is.null(x)) y else x

# Create a function that takes Param Values and turns them into a Tibble
to_param_tbl <- function(param_vals_list) {
  # Flatten beaParamVals(...) list into a tibble
  purrr::map_dfr(param_vals_list, ~tibble::tibble(
    param_value = .x$ParamValue %||% NA_character_,
    key         = .x$Key        %||% NA_character_,
    desc        = .x$Desc       %||% NA_character_
  )) %>% janitor::clean_names()
}

# Discover which Params exist for a dataset (Regional/NIPA)
bea_params_list <- function(api_key, dataset = c("Regional","NIPA")) {
  dataset <- match.arg(dataset)
  beaParams(api_key, dataset)
}

# Get valid values for a parameter and return a tibble
bea_param_values <- function(api_key, dataset = c("Regional","NIPA"), parameter) {
  dataset <- match.arg(dataset)
  vals <- beaParamVals(api_key, dataset, parameter)
  to_param_tbl(vals)
}

## Get Regional Params and Values ----
### 1) See parameters - Regional ----
rp <- bea_params_list(bea_key, "Regional")

### 2) Create values tables for Tables, Lines, Geos ----
tbl_tables  <- bea_param_values(bea_key, "Regional", "TableName") %>%
  transmute(param_value = param_value,
            table_key = key,
            table_desc = desc) %>%
  mutate(dataset = "Regional") %>%
  unique()

tbl_geos    <- bea_param_values(bea_key, "Regional", "GeoFips") %>%
  transmute(geoid = key,
            geoid_name = desc) %>%
  mutate(dataset = "Regional") %>%
  unique()

tbl_lines   <- bea_param_values(bea_key, "Regional", "LineCode") %>%
  transmute(param_value = param_value,
            line_code = key,
            line_desc = desc) %>%
  mutate(    
    table_name_ref = str_extract(line_desc, "\\[.*?\\]") |> str_remove_all("\\[|\\]"),
    line_desc_clean = str_trim(str_remove(line_desc, "\\[.*?\\]")),
    dataset = "Regional") %>%
  unique()

## Write tables to our Database ----
DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_tables"),
                  tbl_tables, overwrite = TRUE)

DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_line_codes"),
                  tbl_lines, overwrite = TRUE)

# Ingest Data ----
## Helper Functions ----
# Create a function that builds Specs based on our inputs
build_bea_spec <- function(api_key,
                           dataset    = c("Regional","NIPA"),
                           table_name,
                           geo_fips,                 # token or vector
                           line_code = NULL,         # MUST be a single value
                           years      = "2020",
                           extra      = list()) {
  dataset <- match.arg(dataset)
  if (!is.null(line_code) && length(line_code) != 1) {
    stop("build_bea_spec: line_code must be length 1; loop over multiple line codes upstream.")
  }
  c(
    list(
      'UserID'      = api_key,
      'Method'      = 'GetData',
      'datasetname' = dataset,
      'TableName'   = table_name,
      'GeoFips'     = if (length(geo_fips) == 1) geo_fips else collapse_csv(geo_fips),
      'LineCode'    = if (!is.null(line_code)) as.character(line_code) else NULL,
      'Year'        = if (is.character(years) && length(years) == 1) years else collapse_years(years)
    ),
    extra
  )
}

# Collapse numeric or character vectors to comma-separated strings
collapse_years <- function(years) {
  if (length(years) == 1 && years %in% c("ALL","X","LAST5","LAST10")) return(years)
  paste(as.integer(years), collapse = ",")
}

collapse_csv <- function(x) paste(unique(as.character(x)), collapse = ",")

# Build our Table
bea_fetch_table <- function(spec) {
  # 1) raw list to surface API errors clearly (optional but helpful)
  raw <- bea.R::beaGet(spec, asList = TRUE, asTable = FALSE, asString = FALSE)
  if (!is.null(raw$APIError)) stop(raw$APIError$ErrorDetail)
  
  # 2) table (long)
  out <- bea.R::beaGet(spec, asTable = TRUE, asWide = FALSE)
  tibble::as_tibble(out) %>% janitor::clean_names()
}

# Update our ingest to have an API limit
bea_get_safe <- function(spec,
                         max_retries = 5,
                         base_sleep  = 1.0,  # seconds between calls
                         backoff     = 1.8,  # multiply delay on retry
                         jitter      = 0.3   # randomize a bit to avoid thundering herd
) {
  delay <- base_sleep
  for (i in 0:max_retries) {
    # always pace requests (helps prevent 429)
    if (i == 0) Sys.sleep(base_sleep)
    
    raw <- try(bea.R::beaGet(spec, asList = TRUE, asTable = FALSE, asString = FALSE), silent = TRUE)
    
    # success path
    if (!(inherits(raw, "try-error")) && is.null(raw$APIError)) {
      out <- bea.R::beaGet(spec, asTable = TRUE, asWide = FALSE)
      return(tibble::as_tibble(out) |> janitor::clean_names())
    }
    
    # error → retry with backoff
    if (i < max_retries) {
      # small randomized backoff
      sleep_now <- delay * (1 + runif(1, -jitter, jitter))
      message(sprintf("BEA retry %d/%d in %.2fs ...", i + 1, max_retries, sleep_now))
      Sys.sleep(sleep_now)
      delay <- delay * backoff
    } else {
      # give informative error
      if (!is.null(raw$APIError)) stop(raw$APIError$ErrorDetail)
      stop("bea_get_safe: request failed and retries exhausted.")
    }
  }
}

# Fetch Multiple Line Codes
bea_fetch_regional_lines_geos <- function(api_key, table_name, line_codes, years, geofips_vec,
                                          dataset = "Regional", chunk_size = 200,
                                          sleep_between_calls = 1.0,  # pacing
                                          verbose = TRUE) {
  stopifnot(length(line_codes) >= 1, length(geofips_vec) >= 1)
  chunks <- if (length(geofips_vec) == 1) list(geofips_vec) else
    split(geofips_vec, ceiling(seq_along(geofips_vec)/chunk_size))
  
  out_list <- list(); k <- 1L
  for (lc in line_codes) {
    for (geo_chunk in chunks) {
      spec <- build_bea_spec(api_key, dataset, table_name,
                             geo_fips  = geo_chunk,
                             line_code = lc,            # single per request
                             years     = years)
      
      if (verbose) message(sprintf("Fetching %s | Line=%s | Geos=%d", table_name, lc, length(geo_chunk)))
      
      # paced + retried call
      Sys.sleep(sleep_between_calls)
      df <- bea_get_safe(spec, base_sleep = sleep_between_calls)
      
      if (!"code" %in% names(df)) df$code <- NA_character_
      df$line_code_req  <- as.integer(lc)
      df$table_name     <- sub("-.*$", "", df$code)
      df$line_code_resp <- suppressWarnings(as.integer(sub("^.*-", "", df$code)))
      
      out_list[[k]] <- df
      k <- k + 1L
    }
  }
  dplyr::bind_rows(out_list)
}
# Takes a raw BEA Regional tibble/data.frame and a geo_level label,
# returns staging-ready rows with scaled numeric values.
normalize_bea_regional_stage <- function(raw_df, geo_level) {
  raw_df %>%
    mutate(
      value_raw = suppressWarnings(as.numeric(data_value)),
      period    = suppressWarnings(as.integer(time_period)),
      unit_mult = suppressWarnings(as.integer(unit_mult)),
      value     = ifelse(is.na(value_raw) | is.na(unit_mult),
                         NA_real_,
                         value_raw * (10 ^ unit_mult))
    ) %>%
    mutate(line_code = suppressWarnings(as.integer(line_code_req))) %>%
    transmute(
      code       = code,
      table      = table_name,     # e.g., "CAINC1"
      geo_level  = geo_level,      # "cbsa" | "county" | "state"
      geo_id     = geo_fips,       # canonical area code from BEA
      geo_name   = geo_name,
      period,                      # year (int)
      line_code,                   # BEA line
      unit_raw   = cl_unit,        # BEA unit label
      unit_mult,                   # BEA power-of-10
      value_raw,                   # API value before scaling
      value,                       # scaled numeric
      note_ref
    ) %>%
    filter(!is.na(value))
}

## CAINC1 ----
# Has State, CBSA, County

### Set Configs
years   <- 2000:2023
line_codes <- c("1","2","3")

### CBSA ----

### FETCH: CAINC1 | CBSA | lines 1:3 
# Ingest data
raw_cainc1_cbsa <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAINC1",
  line_codes  = line_codes,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cainc1_cbsa <- normalize_bea_regional_stage(raw_cainc1_cbsa, "cbsa")

# Write Staging data
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bea_regional_cbsa_cainc1"),
                  stage_cainc1_cbsa, overwrite = TRUE)



### County ----
### FETCH: CAINC1 | County | lines 1:3 
# Ingest data
raw_cainc1_county <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAINC1",
  line_codes  = line_codes,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all CBSAs
  verbose     = TRUE
)

stage_cainc1_county <- normalize_bea_regional_stage(raw_cainc1_county, "county")

# Write Staging data
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bea_regional_county_cainc1"),
                  stage_cainc1_county, overwrite = TRUE)

### State ----
### FETCH: CAINC1 | State | lines 1:3 
# Ingest data
raw_cainc1_state <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAINC1",
  line_codes  = line_codes,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all CBSAs
  verbose     = TRUE
)

stage_cainc1_state <- normalize_bea_regional_stage(raw_cainc1_state, "state")

# Write Staging data
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bea_regional_state_cainc1"),
                  stage_cainc1_state, overwrite = TRUE)



# CAINC4 ----
## Identify the Line Codes for CAINC4 ----
cainc4_line_codes <- tbl_lines %>%
  filter(table_name_ref == "CAINC4") 

# Add filepath 
# write_csv(cainc4_line_codes, ".../cainc4_line_codes.csv")

## Set Configs ----
years   <- 2000:2023
line_codes <- c(11,12,35,36,37,38,42,45,46,47,50,60,61,62,70,71,72)
# Create smaller groups for Counties
g1 <- c(11,12)
g2 <- c(35,36,37,38)
g3 <- c(42,45,46,47)
g4 <- c(50,60,61,62)
g5 <- c(70,71,72)   # optional

## Ingest data ----
### CBSA ----
raw_cainc4_cbsa <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAINC4",
  line_codes  = line_codes,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cainc4_cbsa <- normalize_bea_regional_stage(raw_cainc4_cbsa, "cbsa")


# Write Staging data
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bea_regional_cbsa_cainc4"),
                  stage_cainc4_cbsa, overwrite = TRUE)

### County ----
# G1
raw_cainc4_county_g1 <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAINC4",
  line_codes  = g1,          
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        
  verbose     = TRUE
)

stage_cainc4_county_g1 <- normalize_bea_regional_stage(raw_cainc4_county_g1, "county")

# G2
raw_cainc4_county_g2 <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAINC4",
  line_codes  = g2,          
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        
  verbose     = TRUE
)

stage_cainc4_county_g2 <- normalize_bea_regional_stage(raw_cainc4_county_g2, "county")

# G3
raw_cainc4_county_g3 <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAINC4",
  line_codes  = g3,          
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        
  verbose     = TRUE
)

stage_cainc4_county_g3 <- normalize_bea_regional_stage(raw_cainc4_county_g3, "county")

# G4
raw_cainc4_county_g4 <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAINC4",
  line_codes  = g4,          
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        
  verbose     = TRUE
)

stage_cainc4_county_g4 <- normalize_bea_regional_stage(raw_cainc4_county_g4, "county")

# G5
raw_cainc4_county_g5 <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAINC4",
  line_codes  = g5,          
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        
  verbose     = TRUE
)

stage_cainc4_county_g5 <- normalize_bea_regional_stage(raw_cainc4_county_g5, "county")

# Bind data together 
stage_cainc4_county <- dplyr::bind_rows(
  stage_cainc4_county_g1,
  stage_cainc4_county_g2,
  stage_cainc4_county_g3,
  stage_cainc4_county_g4,
  stage_cainc4_county_g5
)

# Write Staging data
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bea_regional_county_cainc4"),
                  stage_cainc4_county, overwrite = TRUE)

### State ----
raw_cainc4_state <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAINC4",
  line_codes  = line_codes,          
  years       = collapse_years(years),
  geofips_vec = "STATE",        
  verbose     = TRUE
)

stage_cainc4_state <- normalize_bea_regional_stage(raw_cainc4_state, "state")


# Write Staging data
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bea_regional_state_cainc4"),
                  stage_cainc4_state, overwrite = TRUE)


# CAGDP2 ----
## Identify the Line Codes for CAINC4 ----
cagdp2_line_codes <- tbl_lines %>%
  filter(table_name_ref == "CAGDP2") 


## Set Configs ----
years   <- 2000:2023


# Create smaller groups for Counties
# CAGDP2 (current $) and CAGDP9 (real $) line packs

  A_aggregates <- c(1, 2, 83, 91, 92)
  B_goods_mfg  <- c(10, 11, 12, 13, 25)
  C_trade_tti  <- c(34, 35, 36, 45)
  D_fire_re    <- c(51, 56)
  E_prof_biz   <- c(60, 64, 65)
  F_ed_health  <- c(68, 70)
  G_leisure_os <- c(76, 79, 82)
  X_optional   <- c(87, 88, 89, 90)  # only if you want umbrella groups


## Ingest data ----
### CBSA ----
raw_cagdp2_cbsa_a <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = A_aggregates,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_cbsa_a <- normalize_bea_regional_stage(raw_cagdp2_cbsa_a, "cbsa")

raw_cagdp2_cbsa_b <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = B_goods_mfg,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_cbsa_b <- normalize_bea_regional_stage(raw_cagdp2_cbsa_b, "cbsa")

raw_cagdp2_cbsa_c <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = C_trade_tti,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_cbsa_c <- normalize_bea_regional_stage(raw_cagdp2_cbsa_c, "cbsa")

raw_cagdp2_cbsa_d <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = D_fire_re,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_cbsa_d <- normalize_bea_regional_stage(raw_cagdp2_cbsa_d, "cbsa")

raw_cagdp2_cbsa_e <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = E_prof_biz,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_cbsa_e <- normalize_bea_regional_stage(raw_cagdp2_cbsa_e, "cbsa")

raw_cagdp2_cbsa_f <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = F_ed_health,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_cbsa_f <- normalize_bea_regional_stage(raw_cagdp2_cbsa_f, "cbsa")

raw_cagdp2_cbsa_g <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = G_leisure_os,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_cbsa_g <- normalize_bea_regional_stage(raw_cagdp2_cbsa_g, "cbsa")

raw_cagdp2_cbsa_x <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = X_optional,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_cbsa_x <- normalize_bea_regional_stage(raw_cagdp2_cbsa_x, "cbsa")

# Bind data together 
stage_cagdp2_cbsa <- dplyr::bind_rows(
  stage_cagdp2_cbsa_a,
  stage_cagdp2_cbsa_b,
  stage_cagdp2_cbsa_c,
  stage_cagdp2_cbsa_d,
  stage_cagdp2_cbsa_e,
  stage_cagdp2_cbsa_f,
  stage_cagdp2_cbsa_g,
  stage_cagdp2_cbsa_x
)

# Write Staging data
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bea_regional_cbsa_cagdp2"),
                  stage_cagdp2_cbsa, overwrite = TRUE)


### County ----
years <- 2010:2023

raw_cagdp2_county_a <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = A_aggregates,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_county_a <- normalize_bea_regional_stage(raw_cagdp2_county_a, "county")

raw_cagdp2_county_b <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = B_goods_mfg,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_county_b <- normalize_bea_regional_stage(raw_cagdp2_county_b, "county")

raw_cagdp2_county_c <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = C_trade_tti,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_county_c <- normalize_bea_regional_stage(raw_cagdp2_county_c, "county")

raw_cagdp2_county_d <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = D_fire_re,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_county_d <- normalize_bea_regional_stage(raw_cagdp2_county_d, "county")

raw_cagdp2_county_e <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = E_prof_biz,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_county_e <- normalize_bea_regional_stage(raw_cagdp2_county_e, "county")

raw_cagdp2_county_f <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = F_ed_health,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_county_f <- normalize_bea_regional_stage(raw_cagdp2_county_f, "county")

raw_cagdp2_county_g <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = G_leisure_os,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_county_g <- normalize_bea_regional_stage(raw_cagdp2_county_g, "county")

raw_cagdp2_county_x <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = X_optional,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp2_county_x <- normalize_bea_regional_stage(raw_cagdp2_county_x, "county")

# Bind data together 
stage_cagdp2_county <- dplyr::bind_rows(
  stage_cagdp2_county_a,
  stage_cagdp2_county_b,
  stage_cagdp2_county_c,
  stage_cagdp2_county_d,
  stage_cagdp2_county_e,
  stage_cagdp2_county_f,
  stage_cagdp2_county_g,
  stage_cagdp2_county_x
)

# Write Staging data
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bea_regional_county_cagdp2"),
                  stage_cagdp2_county, overwrite = TRUE)



### State ----
raw_cagdp2_state_a <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = A_aggregates,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all States
  verbose     = TRUE
)

stage_cagdp2_state_a <- normalize_bea_regional_stage(raw_cagdp2_state_a, "state")

raw_cagdp2_state_b <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = B_goods_mfg,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all States
  verbose     = TRUE
)

stage_cagdp2_state_b <- normalize_bea_regional_stage(raw_cagdp2_state_b, "state")


raw_cagdp2_state_c <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = C_trade_tti,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all states
  verbose     = TRUE
)

stage_cagdp2_state_c <- normalize_bea_regional_stage(raw_cagdp2_state_c, "state")

raw_cagdp2_state_d <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = D_fire_re,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all states
  verbose     = TRUE
)

stage_cagdp2_state_d <- normalize_bea_regional_stage(raw_cagdp2_state_d, "state")

raw_cagdp2_state_e <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = E_prof_biz,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all states
  verbose     = TRUE
)

stage_cagdp2_state_e <- normalize_bea_regional_stage(raw_cagdp2_state_e, "state")

raw_cagdp2_state_f <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = F_ed_health,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all states
  verbose     = TRUE
)

stage_cagdp2_state_f <- normalize_bea_regional_stage(raw_cagdp2_state_f, "state")

raw_cagdp2_state_g <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = G_leisure_os,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all states
  verbose     = TRUE
)

stage_cagdp2_state_g <- normalize_bea_regional_stage(raw_cagdp2_state_g, "state")

raw_cagdp2_state_x <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP2",
  line_codes  = X_optional,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all states
  verbose     = TRUE
)

stage_cagdp2_state_x <- normalize_bea_regional_stage(raw_cagdp2_state_x, "state")

# Bind data together 
stage_cagdp2_state <- dplyr::bind_rows(
  stage_cagdp2_state_a,
  stage_cagdp2_state_b,
  stage_cagdp2_state_c,
  stage_cagdp2_state_d,
  stage_cagdp2_state_e,
  stage_cagdp2_state_f,
  stage_cagdp2_state_g,
  stage_cagdp2_state_x
)

# Write Staging data
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bea_regional_state_cagdp2"),
                  stage_cagdp2_state, overwrite = TRUE)


# CAGDP9 ----
## Identify the Line Codes for CAINC4 ----
cagdp9_line_codes <- tbl_lines %>%
  filter(table_name_ref == "CAGDP9") 

# write_csv(cagdp9_line_codes, ".../cagdp9_line_codes.csv")

## Set Configs ----
years   <- 2000:2023


# Create smaller groups for Counties
# CAGDP9 (current $) and CAGDP9 (real $) line packs

A_aggregates <- c(1, 2, 83, 91, 92)
B_goods_mfg  <- c(10, 11, 12, 13, 25)
C_trade_tti  <- c(34, 35, 36, 45)
D_fire_re    <- c(50, 51, 56, 59)
E_prof_biz   <- c(60, 64, 65)
F_ed_health  <- c(68, 69, 70)
G_leisure_os <- c(75, 76, 79, 82)
H_primary    <- c(3, 6)
X_optional   <- c(87, 88, 89, 90)  # only if you want umbrella groups


## Ingest data ----
### CBSA ----
raw_cagdp9_cbsa_a <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = A_aggregates,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp9_cbsa_a <- normalize_bea_regional_stage(raw_cagdp9_cbsa_a, "cbsa")

raw_cagdp9_cbsa_b <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = B_goods_mfg,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp9_cbsa_b <- normalize_bea_regional_stage(raw_cagdp9_cbsa_b, "cbsa")

raw_cagdp9_cbsa_c <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = C_trade_tti,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp9_cbsa_c <- normalize_bea_regional_stage(raw_cagdp9_cbsa_c, "cbsa")

raw_cagdp9_cbsa_d <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = D_fire_re,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp9_cbsa_d <- normalize_bea_regional_stage(raw_cagdp9_cbsa_d, "cbsa")

raw_cagdp9_cbsa_e <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = E_prof_biz,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp9_cbsa_e <- normalize_bea_regional_stage(raw_cagdp9_cbsa_e, "cbsa")

raw_cagdp9_cbsa_f <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = F_ed_health,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp9_cbsa_f <- normalize_bea_regional_stage(raw_cagdp9_cbsa_f, "cbsa")

raw_cagdp9_cbsa_g <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = G_leisure_os,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp9_cbsa_g <- normalize_bea_regional_stage(raw_cagdp9_cbsa_g, "cbsa")

raw_cagdp9_cbsa_h <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = H_primary,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp9_cbsa_h <- normalize_bea_regional_stage(raw_cagdp9_cbsa_h, "cbsa")


raw_cagdp9_cbsa_x <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = X_optional,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_cagdp9_cbsa_x <- normalize_bea_regional_stage(raw_cagdp9_cbsa_x, "cbsa")

# Bind data together 
stage_cagdp9_cbsa <- dplyr::bind_rows(
  stage_cagdp9_cbsa_a,
  stage_cagdp9_cbsa_b,
  stage_cagdp9_cbsa_c,
  stage_cagdp9_cbsa_d,
  stage_cagdp9_cbsa_e,
  stage_cagdp9_cbsa_f,
  stage_cagdp9_cbsa_g,
  stage_cagdp9_cbsa_h,
  stage_cagdp9_cbsa_x
)

# Write Staging data
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bea_regional_cbsa_cagdp9"),
                  stage_cagdp9_cbsa, overwrite = TRUE)

### County ----
# Set years to 2010:2023
years   <- 2010:2023

raw_cagdp9_county_a <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = A_aggregates,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all countys
  verbose     = TRUE,
  sleep_between_calls = 2
)

stage_cagdp9_county_a <- normalize_bea_regional_stage(raw_cagdp9_county_a, "county")

raw_cagdp9_county_b <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = B_goods_mfg,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all countys
  verbose     = TRUE
)

stage_cagdp9_county_b <- normalize_bea_regional_stage(raw_cagdp9_county_b, "county")

raw_cagdp9_county_c <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = C_trade_tti,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all countys
  verbose     = TRUE
)

stage_cagdp9_county_c <- normalize_bea_regional_stage(raw_cagdp9_county_c, "county")

raw_cagdp9_county_d <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = D_fire_re,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all countys
  verbose     = TRUE
)

stage_cagdp9_county_d <- normalize_bea_regional_stage(raw_cagdp9_county_d, "county")

raw_cagdp9_county_e <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = E_prof_biz,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all countys
  verbose     = TRUE
)

stage_cagdp9_county_e <- normalize_bea_regional_stage(raw_cagdp9_county_e, "county")

raw_cagdp9_county_f <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = F_ed_health,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all countys
  verbose     = TRUE
)

stage_cagdp9_county_f <- normalize_bea_regional_stage(raw_cagdp9_county_f, "county")

raw_cagdp9_county_g <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = G_leisure_os,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all countys
  verbose     = TRUE
)

stage_cagdp9_county_g <- normalize_bea_regional_stage(raw_cagdp9_county_g, "county")

raw_cagdp9_county_h <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = H_primary,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all countys
  verbose     = TRUE
)

stage_cagdp9_county_h <- normalize_bea_regional_stage(raw_cagdp9_county_h, "county")


raw_cagdp9_county_x <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = X_optional,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "COUNTY",        # all countys
  verbose     = TRUE
)

stage_cagdp9_county_x <- normalize_bea_regional_stage(raw_cagdp9_county_x, "county")

# Bind data together 
stage_cagdp9_county <- dplyr::bind_rows(
  stage_cagdp9_county_a,
  stage_cagdp9_county_b,
  stage_cagdp9_county_c,
  stage_cagdp9_county_d,
  stage_cagdp9_county_e,
  stage_cagdp9_county_f,
  stage_cagdp9_county_g,
  stage_cagdp9_county_h,
  stage_cagdp9_county_x
)

# Write Staging data
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bea_regional_county_cagdp9"),
                  stage_cagdp9_county, overwrite = TRUE)

### State ----
raw_cagdp9_state_a <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = A_aggregates,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all States
  verbose     = TRUE
)

stage_cagdp9_state_a <- normalize_bea_regional_stage(raw_cagdp9_state_a, "state")

raw_cagdp9_state_b <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = B_goods_mfg,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all States
  verbose     = TRUE
)

stage_cagdp9_state_b <- normalize_bea_regional_stage(raw_cagdp9_state_b, "state")


raw_cagdp9_state_c <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = C_trade_tti,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all states
  verbose     = TRUE
)

stage_cagdp9_state_c <- normalize_bea_regional_stage(raw_cagdp9_state_c, "state")

raw_cagdp9_state_d <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = D_fire_re,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all states
  verbose     = TRUE
)

stage_cagdp9_state_d <- normalize_bea_regional_stage(raw_cagdp9_state_d, "state")

raw_cagdp9_state_e <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = E_prof_biz,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all states
  verbose     = TRUE
)

stage_cagdp9_state_e <- normalize_bea_regional_stage(raw_cagdp9_state_e, "state")

raw_cagdp9_state_f <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = F_ed_health,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all states
  verbose     = TRUE
)

stage_cagdp9_state_f <- normalize_bea_regional_stage(raw_cagdp9_state_f, "state")

raw_cagdp9_state_g <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = G_leisure_os,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all states
  verbose     = TRUE
)

stage_cagdp9_state_g <- normalize_bea_regional_stage(raw_cagdp9_state_g, "state")

raw_cagdp9_state_h <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = H_primary,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all states
  verbose     = TRUE
)

stage_cagdp9_state_h <- normalize_bea_regional_stage(raw_cagdp9_state_h, "state")


raw_cagdp9_state_x <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "CAGDP9",
  line_codes  = X_optional,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all states
  verbose     = TRUE
)

stage_cagdp9_state_x <- normalize_bea_regional_stage(raw_cagdp9_state_x, "state")

# Bind data together 
stage_cagdp9_state <- dplyr::bind_rows(
  stage_cagdp9_state_a,
  stage_cagdp9_state_b,
  stage_cagdp9_state_c,
  stage_cagdp9_state_d,
  stage_cagdp9_state_e,
  stage_cagdp9_state_f,
  stage_cagdp9_state_g,
  stage_cagdp9_state_h,
  stage_cagdp9_state_x
)

# Write Staging data
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bea_regional_state_cagdp9"),
                  stage_cagdp9_state, overwrite = TRUE)

# MARPP ----
## Identify the Line Codes for MARPP ----
marpp_line_codes <- tbl_lines %>%
  filter(table_name_ref == "MARPP") 

# write_csv(marpp_line_codes, ".../cagdp9_line_codes.csv")

## Set Configs ----
years   <- 2000:2023

marpp_codes <- c("1","2","3","4", "5", "6", "7", "8")

## Ingest data ----
### CBSA ----
raw_marpp_cbsa <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "MARPP",
  line_codes  = marpp_codes,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "MSA",        # all CBSAs
  verbose     = TRUE
)

stage_marpp_cbsa <- normalize_bea_regional_stage(raw_marpp_cbsa, "cbsa")

# Write Staging data
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bea_regional_cbsa_marpp"),
                  stage_marpp_cbsa, overwrite = TRUE)

### States ----
raw_marpp_state <- bea_fetch_regional_lines_geos(
  api_key     = bea_key,
  table_name  = "SARPP",
  line_codes  = marpp_codes,          # CAINC1 valid: 1,2,3
  years       = collapse_years(years),
  geofips_vec = "STATE",        # all States
  verbose     = TRUE
)

stage_marpp_state <- normalize_bea_regional_stage(raw_marpp_state, "state")

# Write Staging data
DBI::dbWriteTable(con, DBI::Id(schema="staging", table="bea_regional_state_marpp"),
                  stage_marpp_state, overwrite = TRUE)


# Shutdown ----
dbDisconnect(con, shutdown = TRUE)

