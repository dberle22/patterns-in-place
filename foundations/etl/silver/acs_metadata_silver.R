# In this script we get our ACS Raw data

# Find our current directory 
getwd()

# Set up our environment ----
# Read our common libraries & set other packages
source(here::here("foundations", "etl", "utils.R"))


# Set paths for our environments
# Make sure we're reading from the project Renviron
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Set our Paths - Pointing to our Bronze folder in Data
bronze_acs <- get_env_path("DATA_DEMO_RAW")
db_path <- get_env_path("DB_PATH")

# Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# helper: infer topic and table_type from name ----
infer_topic <- function(table_name) {
  table_name %>%
    str_replace("_kpi$", "") %>%
    str_replace("_base$", "")
}

infer_table_type <- function(table_name) {
  dplyr::case_when(
    str_ends(table_name, "_kpi")  ~ "kpi",
    str_ends(table_name, "_base") ~ "base",
    TRUE                          ~ "other"
  )
}

# Get list of Silver tables ----
silver_tables <- dbGetQuery(
  con,
  "
  SELECT table_schema, table_name
  FROM information_schema.tables
  WHERE table_schema = 'silver'
    AND table_type = 'BASE TABLE'
  ORDER BY table_name
  "
)

# Build metadata topics ----
metadata_topics <- map_dfr(seq_len(nrow(silver_tables)), function(i) {
  tbl <- silver_tables$table_name[i]
  
  # try to get counts, year, geo_level — some tables may not have them
  q <- glue::glue("
    SELECT
      COUNT(*) AS row_count,
      COUNT(*) FILTER (WHERE year IS NULL) AS rows_no_year,
      MIN(year) AS min_year,
      MAX(year) AS max_year,
      LIST(DISTINCT geo_level) AS geo_levels
    FROM silver.{tbl}
  ")
  
  stats <- tryCatch(
    dbGetQuery(con, q),
    error = function(e) {
      # table without year/geo_level
      data.frame(
        row_count = NA_integer_,
        rows_no_year = NA_integer_,
        min_year = NA,
        max_year = NA,
        geo_levels = NA
      )
    }
  )
  
  # get column count
  cols <- dbGetQuery(
    con,
    glue::glue("
      SELECT COUNT(*) AS col_count
      FROM information_schema.columns
      WHERE table_schema = 'silver'
        AND table_name = '{tbl}'
    ")
  )
  
  tibble::tibble(
    table_schema   = "silver",
    table_name     = tbl,
    topic          = infer_topic(tbl),
    table_type     = infer_table_type(tbl),
    row_count      = stats$row_count,
    col_count      = cols$col_count,
    min_year       = stats$min_year,
    max_year       = stats$max_year,
    geo_levels     = as.character(stats$geo_levels),
    last_refreshed = Sys.time()
  )
})

# write to DB
dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "metadata_topics"),
  metadata_topics,
  overwrite = TRUE
)

# Build Metadata Vars ----
metadata_vars <- map_dfr(seq_len(nrow(silver_tables)), function(i) {
  tbl <- silver_tables$table_name[i]
  
  cols <- dbGetQuery(
    con,
    glue::glue("
      SELECT
        table_schema,
        table_name,
        column_name,
        ordinal_position,
        data_type
      FROM information_schema.columns
      WHERE table_schema = 'silver'
        AND table_name = '{tbl}'
      ORDER BY ordinal_position
    ")
  )
  
  # heuristics for keys / measures
  cols <- cols %>%
    mutate(
      topic      = infer_topic(table_name),
      is_key     = column_name %in% c("geo_level", "geo_id", "geo_name", "year"),
      is_measure = !is_key & !str_detect(column_name, "name$"),
      description = dplyr::case_when(
        column_name == "geo_level" ~ "Geographic level (US, region, division, state, county, place, zcta, tract, cbsa)",
        column_name == "geo_id"    ~ "Geographic identifier for the row",
        column_name == "geo_name"  ~ "Geographic name (from ACS NAME)",
        column_name == "year"      ~ "ACS 5-year vintage year",
        TRUE ~ paste0("Metric from ", topic, " ACS table")
      )
    )
  
  cols
})

dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "metadata_vars"),
  metadata_vars,
  overwrite = TRUE
)

# KPI Dictionary ----
vars <- dbGetQuery(con, "
  SELECT table_schema, table_name, column_name, data_type, topic, is_key, is_measure
  FROM silver.metadata_vars
  ORDER BY table_name, ordinal_position
")

# auto-build kpi dictionary
kpi_dict <- vars %>%
  filter(is_measure) %>%
  mutate(
    kpi_name = column_name,
    business_definition = case_when(
      str_detect(kpi_name, "^pct_") ~ "Share / percentage; denominator defined in KPI logic.",
      str_detect(kpi_name, "rate") ~ "Rate derived from ACS counts.",
      TRUE ~ "Measure derived from ACS Silver table."
    ),
    source = case_when(
      topic == "housing" ~ "ACS Housing (B2500x)",
      topic == "income"  ~ "ACS Income/Poverty (B19xxx/B17xxx)",
      topic == "labor_occ_ind" ~ "ACS Labor/Industry/Occupation (B23025, C24010, C24030)",
      TRUE ~ "ACS 5-year"
    ),
    denominator_hint = case_when(
      kpi_name == "vacancy_rate" ~ "hu_total",
      kpi_name == "owner_occ_rate" ~ "tenure_total",
      kpi_name == "pct_rent_burden_30plus" ~ "rent_burden_total - not_computed",
      str_detect(kpi_name, "^pct_occ_") ~ "occ_total_emp",
      str_detect(kpi_name, "^pct_ind_") ~ "ind_total_emp",
      str_detect(kpi_name, "^pct_commute_") ~ "commute_workers_total",
      str_detect(kpi_name, "^pct_hh_") ~ "households (topic-specific)",
      TRUE ~ NA_character_
    )
  ) %>%
  select(
    topic,
    table_name,
    kpi_name,
    business_definition,
    source,
    denominator_hint,
    data_type
  )

dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "kpi_dictionary"),
  kpi_dict,
  overwrite = TRUE
)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)