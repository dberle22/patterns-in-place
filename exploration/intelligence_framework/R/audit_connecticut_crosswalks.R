# Audit Connecticut county-key families across Silver and Gold tables.
# This helps identify tables that still use legacy Connecticut county GEOIDs
# (`09001`-`09015`) versus the newer planning-region GEOIDs (`09110`-`09190`)
# and whether CT CBSA rows are materializing downstream.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

library(DBI)
library(dplyr)
library(purrr)
library(readr)
library(glue)
library(here)

db_path <- get_env_path("DB_PATH")
con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = TRUE)
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

dir.create(here("exploration/intelligence_framework/outputs"), recursive = TRUE, showWarnings = FALSE)

legacy_ct_geoids <- c("09001", "09003", "09005", "09007", "09009", "09011", "09013", "09015")
planning_ct_geoids <- c("09110", "09120", "09130", "09140", "09150", "09160", "09170", "09180", "09190")
ct_cbsa_codes <- c("14860", "25540", "35300", "35980", "39480", "45860", "47930")

candidate_tables <- DBI::dbGetQuery(
  con,
  "
  with table_cols as (
    select
      table_schema,
      table_name,
      list(column_name order by column_name) as cols
    from information_schema.columns
    where table_schema in ('silver', 'gold')
    group by 1, 2
  )
  select table_schema, table_name
  from table_cols
  where list_contains(cols, 'geo_level')
    and list_contains(cols, 'geo_id')
  order by table_schema, table_name
  "
)

audit_one_table <- function(schema_name, table_name) {
  sql <- glue(
    "
    with base as (
      select
        geo_level,
        cast(geo_id as varchar) as geo_id
      from {schema_name}.{table_name}
    )
    select
      '{schema_name}' as table_schema,
      '{table_name}' as table_name,
      sum(case when geo_level = 'county' and geo_id in ({legacy_ids}) then 1 else 0 end) as legacy_ct_county_rows,
      sum(case when geo_level = 'county' and geo_id in ({planning_ids}) then 1 else 0 end) as planning_ct_county_rows,
      count(distinct case when geo_level = 'county' and geo_id in ({legacy_ids}) then geo_id end) as legacy_ct_counties,
      count(distinct case when geo_level = 'county' and geo_id in ({planning_ids}) then geo_id end) as planning_ct_counties,
      sum(case when geo_level = 'cbsa' then 1 else 0 end) as any_cbsa_rows,
      sum(case when geo_level = 'cbsa' and geo_id in ({cbsa_ids}) then 1 else 0 end) as ct_cbsa_rows,
      count(distinct case when geo_level = 'cbsa' and geo_id in ({cbsa_ids}) then geo_id end) as ct_cbsas,
      count(*) as total_rows
    from base
    ",
    legacy_ids = paste(shQuote(legacy_ct_geoids), collapse = ", "),
    planning_ids = paste(shQuote(planning_ct_geoids), collapse = ", "),
    cbsa_ids = paste(shQuote(ct_cbsa_codes), collapse = ", ")
  )

  DBI::dbGetQuery(con, sql)
}

audit_tbl <- purrr::map2_dfr(
  candidate_tables$table_schema,
  candidate_tables$table_name,
  audit_one_table
) %>%
  mutate(
    ct_key_pattern = case_when(
      legacy_ct_counties > 0 & planning_ct_counties == 0 ~ "legacy_only",
      legacy_ct_counties == 0 & planning_ct_counties > 0 ~ "planning_only",
      legacy_ct_counties > 0 & planning_ct_counties > 0 ~ "mixed",
      TRUE ~ "none"
    ),
    missing_ct_cbsa_rollup = legacy_ct_counties > 0 & any_cbsa_rows > 0 & ct_cbsas == 0
  ) %>%
  filter(
    legacy_ct_counties > 0 |
      planning_ct_counties > 0 |
      ct_cbsas > 0
  ) %>%
  arrange(desc(missing_ct_cbsa_rollup), desc(legacy_ct_counties), table_schema, table_name)

readr::write_csv(
  audit_tbl,
  here("exploration/intelligence_framework/outputs/connecticut_crosswalk_audit.csv")
)

print(audit_tbl)
