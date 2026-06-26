# In this script we turn the annual county-first LEHD QWI staging table into a
# canonical Silver labor-dynamics table.
#
# 1. Audit the staged county coverage and the CBSA/state rollup crosswalks.
# 2. Standardize the county rows to one analytical contract with readable demo
#    and industry labels.
# 3. Roll the county base to CBSA, state, division, and U.S. rows.
# 4. Recompute rates and weighted earnings after rollup, then write
#    `silver.lehd_qwi`.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS silver;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

append_manual_state_rows <- function(state_region_df) {
  # `xwalk_state_region` currently covers the 50 states plus DC. QWI staging
  # also includes Puerto Rico, so we add a small manual row here so Silver can
  # keep a complete state surface even though PR is not assigned to a Census
  # region/division in the managed crosswalk table.
  bind_rows(
    state_region_df,
    tibble::tibble(
      state_fips = "72",
      state_abbr = "PR",
      state_name = "Puerto Rico",
      census_region = NA_character_,
      census_division = NA_character_
    )
  ) %>%
    distinct(.data$state_fips, .keep_all = TRUE)
}

division_ref <- tibble::tribble(
  ~census_division, ~division_id,
  "New England", "1",
  "Middle Atlantic", "2",
  "East North Central", "3",
  "West North Central", "4",
  "South Atlantic", "5",
  "East South Central", "6",
  "West South Central", "7",
  "Mountain", "8",
  "Pacific", "9"
)

demo_map <- tibble::tribble(
  ~demo_family, ~demo_code, ~demo_label, ~demo_sort_order, ~is_total_demo,
  "age", "A00", "All Ages (14-99)", 0L, TRUE,
  "age", "A01", "Age 14-18", 1L, FALSE,
  "age", "A02", "Age 19-21", 2L, FALSE,
  "age", "A03", "Age 22-24", 3L, FALSE,
  "age", "A04", "Age 25-34", 4L, FALSE,
  "age", "A05", "Age 35-44", 5L, FALSE,
  "age", "A06", "Age 45-54", 6L, FALSE,
  "age", "A07", "Age 55-64", 7L, FALSE,
  "age", "A08", "Age 65-99", 8L, FALSE,
  "education", "E1", "Less than high school", 1L, FALSE,
  "education", "E2", "High school or equivalent", 2L, FALSE,
  "education", "E3", "Some college or Associate degree", 3L, FALSE,
  "education", "E4", "Bachelor's degree or advanced degree", 4L, FALSE,
  "education", "E5", "Educational attainment not available (workers aged 24 or younger)", 5L, FALSE
)

industry_map <- tibble::tribble(
  ~industry_code, ~industry_label, ~industry_rollup_family, ~is_total_industry,
  "00", "Total, all NAICS sectors", "total", TRUE,
  "11", "Agriculture, forestry, fishing and hunting", "ag_mining", FALSE,
  "21", "Mining, quarrying, and oil and gas extraction", "ag_mining", FALSE,
  "22", "Utilities", "transport_util", FALSE,
  "23", "Construction", "construction", FALSE,
  "31-33", "Manufacturing", "manufacturing", FALSE,
  "42", "Wholesale trade", "wholesale", FALSE,
  "44-45", "Retail trade", "retail", FALSE,
  "48-49", "Transportation and warehousing", "transport_util", FALSE,
  "51", "Information", "information", FALSE,
  "52", "Finance and insurance", "finance_real", FALSE,
  "53", "Real estate and rental and leasing", "finance_real", FALSE,
  "54", "Professional, scientific, and technical services", "professional", FALSE,
  "55", "Management of companies and enterprises", "professional", FALSE,
  "56", "Administrative and support and waste management", "professional", FALSE,
  "61", "Educational services", "educ_health", FALSE,
  "62", "Health care and social assistance", "educ_health", FALSE,
  "71", "Arts, entertainment, and recreation", "arts_accomm_food", FALSE,
  "72", "Accommodation and food services", "arts_accomm_food", FALSE,
  "81", "Other services except public administration", "other_services", FALSE,
  "92", "Public administration", "public_admin", FALSE
)

state_region_ref <- DBI::dbGetQuery(
  con,
  "SELECT state_fips, state_abbr, state_name, census_region, census_division FROM silver.xwalk_state_region"
) %>%
  mutate(across(everything(), as.character)) %>%
  append_manual_state_rows()

county_xwalk <- DBI::dbGetQuery(
  con,
  "
  SELECT
    state_fip,
    county_geoid,
    county_name_long,
    state_abbr
  FROM silver.xwalk_county_state
  "
) %>%
  transmute(
    state_fips = as.character(.data$state_fip),
    county_geoid = as.character(.data$county_geoid),
    county_name_long = as.character(.data$county_name_long),
    state_abbr = as.character(.data$state_abbr)
  ) %>%
  distinct()

cbsa_xwalk <- DBI::dbGetQuery(
  con,
  "
  SELECT
    county_geoid,
    cbsa_code,
    cbsa_name
  FROM silver.xwalk_cbsa_county
  "
) %>%
  transmute(
    county_geoid = as.character(.data$county_geoid),
    cbsa_code = as.character(.data$cbsa_code),
    cbsa_name = as.character(.data$cbsa_name)
  ) %>%
  distinct()

# 1. Audit geography coverage and mapping domains ----
unmatched_counties <- DBI::dbGetQuery(
  con,
  "
  SELECT COUNT(*) AS unmatched_counties
  FROM (
    SELECT DISTINCT geo_id
    FROM staging.lehd_qwi
  ) q
  LEFT JOIN silver.xwalk_county_state x
    ON q.geo_id = x.county_geoid
  WHERE x.county_geoid IS NULL
  "
)

if (unmatched_counties$unmatched_counties[[1]] > 0) {
  stop(
    sprintf(
      "%s staged LEHD QWI county GEOIDs did not resolve to silver.xwalk_county_state.",
      unmatched_counties$unmatched_counties[[1]]
    ),
    call. = FALSE
  )
}

duplicate_cbsa_counties <- cbsa_xwalk %>%
  count(.data$county_geoid, name = "cbsa_count") %>%
  filter(.data$cbsa_count > 1)

if (nrow(duplicate_cbsa_counties) > 0) {
  stop(
    sprintf(
      paste(
        "LEHD QWI Silver rollups require a one-county-to-one-CBSA crosswalk.",
        "%s county GEOIDs resolve to multiple CBSAs."
      ),
      nrow(duplicate_cbsa_counties)
    ),
    call. = FALSE
  )
}

unmapped_demo_codes <- DBI::dbGetQuery(
  con,
  "
  SELECT
    demo_family,
    CASE
      WHEN demo_family = 'age' THEN agegrp
      WHEN demo_family = 'education' THEN education
    END AS demo_code
  FROM staging.lehd_qwi
  GROUP BY 1, 2
  "
) %>%
  anti_join(
    demo_map %>% select("demo_family", "demo_code"),
    by = c("demo_family", "demo_code")
  )

if (nrow(unmapped_demo_codes) > 0) {
  stop("LEHD QWI staging contains demo codes that are not mapped in the Silver script.", call. = FALSE)
}

unmapped_industry_codes <- DBI::dbGetQuery(
  con,
  "SELECT DISTINCT industry_code FROM staging.lehd_qwi"
) %>%
  mutate(industry_code = as.character(.data$industry_code)) %>%
  anti_join(
    industry_map %>% select("industry_code"),
    by = "industry_code"
  )

if (nrow(unmapped_industry_codes) > 0) {
  stop("LEHD QWI staging contains industry codes that are not mapped in the Silver script.", call. = FALSE)
}

DBI::dbWriteTable(con, "tmp_lehd_qwi_demo_map", demo_map, temporary = TRUE, overwrite = TRUE)
DBI::dbWriteTable(con, "tmp_lehd_qwi_industry_map", industry_map, temporary = TRUE, overwrite = TRUE)
DBI::dbWriteTable(con, "tmp_lehd_qwi_state_region_ref", state_region_ref, temporary = TRUE, overwrite = TRUE)
DBI::dbWriteTable(con, "tmp_lehd_qwi_division_ref", division_ref, temporary = TRUE, overwrite = TRUE)

# 2. Standardize county rows and derive higher geographies in DuckDB ----
DBI::dbExecute(
  con,
  "
  CREATE OR REPLACE TABLE silver.lehd_qwi AS
  WITH county_base AS (
    SELECT
      'county' AS geo_level,
      s.geo_id,
      cx.county_name_long AS geo_name,
      CAST(s.year AS INTEGER) AS year,
      cx.state_fip AS state_fips,
      cx.state_abbr,
      s.demo_family,
      CASE
        WHEN s.demo_family = 'age' THEN s.agegrp
        WHEN s.demo_family = 'education' THEN s.education
      END AS demo_code,
      dm.demo_label,
      dm.demo_sort_order,
      dm.is_total_demo,
      s.industry_code,
      im.industry_label,
      im.industry_rollup_family,
      im.is_total_industry,
      s.ownercode,
      s.periodicity,
      s.source_periodicity,
      CAST(s.quarters_observed AS INTEGER) AS quarters_observed,
      s.release_id,
      s.schema_version,
      s.metadata_period_range,
      CAST(s.annual_avg_emp AS DOUBLE) AS employment,
      CAST(s.annual_avg_earns AS DOUBLE) AS avg_earnings,
      CAST(s.annual_avg_earnhiras AS DOUBLE) AS new_hire_avg_earnings,
      CAST(s.annual_avg_earnseps AS DOUBLE) AS separation_avg_earnings,
      CAST(s.annual_hira AS DOUBLE) AS hires,
      CAST(s.annual_sep AS DOUBLE) AS separations,
      CAST(s.annual_hiraendrepl AS DOUBLE) AS replacements,
      CAST(s.annual_payroll AS DOUBLE) AS payroll,
      CASE
        WHEN s.annual_avg_emp > 0 THEN s.annual_hira / s.annual_avg_emp
        ELSE NULL
      END AS hire_rate,
      CASE
        WHEN s.annual_avg_emp > 0 THEN s.annual_sep / s.annual_avg_emp
        ELSE NULL
      END AS separation_rate,
      CASE
        WHEN s.annual_avg_emp > 0 THEN s.annual_hiraendrepl / s.annual_avg_emp
        ELSE NULL
      END AS replacement_rate,
      CASE
        WHEN s.annual_avg_emp > 0 THEN s.annual_payroll / s.annual_avg_emp
        ELSE NULL
      END AS payroll_per_employee,
      'Census LEHD QWI' AS source
    FROM staging.lehd_qwi s
    INNER JOIN silver.xwalk_county_state cx
      ON s.geo_id = cx.county_geoid
    INNER JOIN tmp_lehd_qwi_demo_map dm
      ON s.demo_family = dm.demo_family
      AND (
        (s.demo_family = 'age' AND s.agegrp = dm.demo_code)
        OR
        (s.demo_family = 'education' AND s.education = dm.demo_code)
      )
    INNER JOIN tmp_lehd_qwi_industry_map im
      ON s.industry_code = im.industry_code
  ),
  cbsa_rollup_base AS (
    SELECT
      'cbsa' AS geo_level,
      cb.cbsa_code AS geo_id,
      cb.cbsa_name AS geo_name,
      c.year,
      CAST(NULL AS VARCHAR) AS state_fips,
      CAST(NULL AS VARCHAR) AS state_abbr,
      c.demo_family,
      c.demo_code,
      MIN(c.demo_label) AS demo_label,
      MIN(c.demo_sort_order) AS demo_sort_order,
      BOOL_OR(c.is_total_demo) AS is_total_demo,
      c.industry_code,
      MIN(c.industry_label) AS industry_label,
      MIN(c.industry_rollup_family) AS industry_rollup_family,
      BOOL_OR(c.is_total_industry) AS is_total_industry,
      MIN(c.ownercode) AS ownercode,
      MIN(c.periodicity) AS periodicity,
      MIN(c.source_periodicity) AS source_periodicity,
      MIN(c.quarters_observed) AS quarters_observed,
      MIN(c.release_id) AS release_id,
      MIN(c.schema_version) AS schema_version,
      MIN(c.metadata_period_range) AS metadata_period_range,
      SUM(c.employment) AS employment,
      SUM(
        CASE
          WHEN c.avg_earnings IS NOT NULL AND c.employment > 0
            THEN c.avg_earnings * c.employment
          ELSE NULL
        END
      ) AS avg_earnings_weighted_sum,
      SUM(
        CASE
          WHEN c.avg_earnings IS NOT NULL AND c.employment > 0
            THEN c.employment
          ELSE NULL
        END
      ) AS avg_earnings_weight,
      SUM(
        CASE
          WHEN c.new_hire_avg_earnings IS NOT NULL AND c.hires > 0
            THEN c.new_hire_avg_earnings * c.hires
          ELSE NULL
        END
      ) AS new_hire_avg_earnings_weighted_sum,
      SUM(
        CASE
          WHEN c.new_hire_avg_earnings IS NOT NULL AND c.hires > 0
            THEN c.hires
          ELSE NULL
        END
      ) AS new_hire_avg_earnings_weight,
      SUM(
        CASE
          WHEN c.separation_avg_earnings IS NOT NULL AND c.separations > 0
            THEN c.separation_avg_earnings * c.separations
          ELSE NULL
        END
      ) AS separation_avg_earnings_weighted_sum,
      SUM(
        CASE
          WHEN c.separation_avg_earnings IS NOT NULL AND c.separations > 0
            THEN c.separations
          ELSE NULL
        END
      ) AS separation_avg_earnings_weight,
      SUM(c.hires) AS hires,
      SUM(c.separations) AS separations,
      SUM(c.replacements) AS replacements,
      SUM(c.payroll) AS payroll,
      MIN(c.source) AS source
    FROM county_base c
    INNER JOIN silver.xwalk_cbsa_county cb
      ON c.geo_id = cb.county_geoid
    GROUP BY
      cb.cbsa_code,
      cb.cbsa_name,
      c.year,
      c.demo_family,
      c.demo_code,
      c.industry_code
  ),
  cbsa_rollup AS (
    SELECT
      geo_level,
      geo_id,
      geo_name,
      year,
      state_fips,
      state_abbr,
      demo_family,
      demo_code,
      demo_label,
      demo_sort_order,
      is_total_demo,
      industry_code,
      industry_label,
      industry_rollup_family,
      is_total_industry,
      ownercode,
      periodicity,
      source_periodicity,
      quarters_observed,
      release_id,
      schema_version,
      metadata_period_range,
      employment,
      CASE
        WHEN avg_earnings_weight > 0
          THEN avg_earnings_weighted_sum / avg_earnings_weight
        ELSE NULL
      END AS avg_earnings,
      CASE
        WHEN new_hire_avg_earnings_weight > 0
          THEN new_hire_avg_earnings_weighted_sum / new_hire_avg_earnings_weight
        ELSE NULL
      END AS new_hire_avg_earnings,
      CASE
        WHEN separation_avg_earnings_weight > 0
          THEN separation_avg_earnings_weighted_sum / separation_avg_earnings_weight
        ELSE NULL
      END AS separation_avg_earnings,
      hires,
      separations,
      replacements,
      payroll,
      CASE
        WHEN employment > 0 THEN hires / employment
        ELSE NULL
      END AS hire_rate,
      CASE
        WHEN employment > 0 THEN separations / employment
        ELSE NULL
      END AS separation_rate,
      CASE
        WHEN employment > 0 THEN replacements / employment
        ELSE NULL
      END AS replacement_rate,
      CASE
        WHEN employment > 0 THEN payroll / employment
        ELSE NULL
      END AS payroll_per_employee,
      source
    FROM cbsa_rollup_base
  ),
  state_rollup_base AS (
    SELECT
      'state' AS geo_level,
      sr.state_fips AS geo_id,
      sr.state_name AS geo_name,
      c.year,
      sr.state_fips,
      sr.state_abbr,
      c.demo_family,
      c.demo_code,
      MIN(c.demo_label) AS demo_label,
      MIN(c.demo_sort_order) AS demo_sort_order,
      BOOL_OR(c.is_total_demo) AS is_total_demo,
      c.industry_code,
      MIN(c.industry_label) AS industry_label,
      MIN(c.industry_rollup_family) AS industry_rollup_family,
      BOOL_OR(c.is_total_industry) AS is_total_industry,
      MIN(c.ownercode) AS ownercode,
      MIN(c.periodicity) AS periodicity,
      MIN(c.source_periodicity) AS source_periodicity,
      MIN(c.quarters_observed) AS quarters_observed,
      MIN(c.release_id) AS release_id,
      MIN(c.schema_version) AS schema_version,
      MIN(c.metadata_period_range) AS metadata_period_range,
      SUM(c.employment) AS employment,
      SUM(
        CASE
          WHEN c.avg_earnings IS NOT NULL AND c.employment > 0
            THEN c.avg_earnings * c.employment
          ELSE NULL
        END
      ) AS avg_earnings_weighted_sum,
      SUM(
        CASE
          WHEN c.avg_earnings IS NOT NULL AND c.employment > 0
            THEN c.employment
          ELSE NULL
        END
      ) AS avg_earnings_weight,
      SUM(
        CASE
          WHEN c.new_hire_avg_earnings IS NOT NULL AND c.hires > 0
            THEN c.new_hire_avg_earnings * c.hires
          ELSE NULL
        END
      ) AS new_hire_avg_earnings_weighted_sum,
      SUM(
        CASE
          WHEN c.new_hire_avg_earnings IS NOT NULL AND c.hires > 0
            THEN c.hires
          ELSE NULL
        END
      ) AS new_hire_avg_earnings_weight,
      SUM(
        CASE
          WHEN c.separation_avg_earnings IS NOT NULL AND c.separations > 0
            THEN c.separation_avg_earnings * c.separations
          ELSE NULL
        END
      ) AS separation_avg_earnings_weighted_sum,
      SUM(
        CASE
          WHEN c.separation_avg_earnings IS NOT NULL AND c.separations > 0
            THEN c.separations
          ELSE NULL
        END
      ) AS separation_avg_earnings_weight,
      SUM(c.hires) AS hires,
      SUM(c.separations) AS separations,
      SUM(c.replacements) AS replacements,
      SUM(c.payroll) AS payroll,
      MIN(c.source) AS source
    FROM county_base c
    INNER JOIN tmp_lehd_qwi_state_region_ref sr
      ON c.state_fips = sr.state_fips
    GROUP BY
      sr.state_fips,
      sr.state_name,
      sr.state_abbr,
      c.year,
      c.demo_family,
      c.demo_code,
      c.industry_code
  ),
  state_rollup AS (
    SELECT
      geo_level,
      geo_id,
      geo_name,
      year,
      state_fips,
      state_abbr,
      demo_family,
      demo_code,
      demo_label,
      demo_sort_order,
      is_total_demo,
      industry_code,
      industry_label,
      industry_rollup_family,
      is_total_industry,
      ownercode,
      periodicity,
      source_periodicity,
      quarters_observed,
      release_id,
      schema_version,
      metadata_period_range,
      employment,
      CASE
        WHEN avg_earnings_weight > 0
          THEN avg_earnings_weighted_sum / avg_earnings_weight
        ELSE NULL
      END AS avg_earnings,
      CASE
        WHEN new_hire_avg_earnings_weight > 0
          THEN new_hire_avg_earnings_weighted_sum / new_hire_avg_earnings_weight
        ELSE NULL
      END AS new_hire_avg_earnings,
      CASE
        WHEN separation_avg_earnings_weight > 0
          THEN separation_avg_earnings_weighted_sum / separation_avg_earnings_weight
        ELSE NULL
      END AS separation_avg_earnings,
      hires,
      separations,
      replacements,
      payroll,
      CASE
        WHEN employment > 0 THEN hires / employment
        ELSE NULL
      END AS hire_rate,
      CASE
        WHEN employment > 0 THEN separations / employment
        ELSE NULL
      END AS separation_rate,
      CASE
        WHEN employment > 0 THEN replacements / employment
        ELSE NULL
      END AS replacement_rate,
      CASE
        WHEN employment > 0 THEN payroll / employment
        ELSE NULL
      END AS payroll_per_employee,
      source
    FROM state_rollup_base
  ),
  division_rollup_base AS (
    SELECT
      'division' AS geo_level,
      dr.division_id AS geo_id,
      sr.census_division AS geo_name,
      s.year,
      CAST(NULL AS VARCHAR) AS state_fips,
      CAST(NULL AS VARCHAR) AS state_abbr,
      s.demo_family,
      s.demo_code,
      MIN(s.demo_label) AS demo_label,
      MIN(s.demo_sort_order) AS demo_sort_order,
      BOOL_OR(s.is_total_demo) AS is_total_demo,
      s.industry_code,
      MIN(s.industry_label) AS industry_label,
      MIN(s.industry_rollup_family) AS industry_rollup_family,
      BOOL_OR(s.is_total_industry) AS is_total_industry,
      MIN(s.ownercode) AS ownercode,
      MIN(s.periodicity) AS periodicity,
      MIN(s.source_periodicity) AS source_periodicity,
      MIN(s.quarters_observed) AS quarters_observed,
      MIN(s.release_id) AS release_id,
      MIN(s.schema_version) AS schema_version,
      MIN(s.metadata_period_range) AS metadata_period_range,
      SUM(s.employment) AS employment,
      SUM(
        CASE
          WHEN s.avg_earnings IS NOT NULL AND s.employment > 0
            THEN s.avg_earnings * s.employment
          ELSE NULL
        END
      ) AS avg_earnings_weighted_sum,
      SUM(
        CASE
          WHEN s.avg_earnings IS NOT NULL AND s.employment > 0
            THEN s.employment
          ELSE NULL
        END
      ) AS avg_earnings_weight,
      SUM(
        CASE
          WHEN s.new_hire_avg_earnings IS NOT NULL AND s.hires > 0
            THEN s.new_hire_avg_earnings * s.hires
          ELSE NULL
        END
      ) AS new_hire_avg_earnings_weighted_sum,
      SUM(
        CASE
          WHEN s.new_hire_avg_earnings IS NOT NULL AND s.hires > 0
            THEN s.hires
          ELSE NULL
        END
      ) AS new_hire_avg_earnings_weight,
      SUM(
        CASE
          WHEN s.separation_avg_earnings IS NOT NULL AND s.separations > 0
            THEN s.separation_avg_earnings * s.separations
          ELSE NULL
        END
      ) AS separation_avg_earnings_weighted_sum,
      SUM(
        CASE
          WHEN s.separation_avg_earnings IS NOT NULL AND s.separations > 0
            THEN s.separations
          ELSE NULL
        END
      ) AS separation_avg_earnings_weight,
      SUM(s.hires) AS hires,
      SUM(s.separations) AS separations,
      SUM(s.replacements) AS replacements,
      SUM(s.payroll) AS payroll,
      MIN(s.source) AS source
    FROM state_rollup s
    INNER JOIN tmp_lehd_qwi_state_region_ref sr
      ON s.geo_id = sr.state_fips
    INNER JOIN tmp_lehd_qwi_division_ref dr
      ON sr.census_division = dr.census_division
    GROUP BY
      dr.division_id,
      sr.census_division,
      s.year,
      s.demo_family,
      s.demo_code,
      s.industry_code
  ),
  division_rollup AS (
    SELECT
      geo_level,
      geo_id,
      geo_name,
      year,
      state_fips,
      state_abbr,
      demo_family,
      demo_code,
      demo_label,
      demo_sort_order,
      is_total_demo,
      industry_code,
      industry_label,
      industry_rollup_family,
      is_total_industry,
      ownercode,
      periodicity,
      source_periodicity,
      quarters_observed,
      release_id,
      schema_version,
      metadata_period_range,
      employment,
      CASE
        WHEN avg_earnings_weight > 0
          THEN avg_earnings_weighted_sum / avg_earnings_weight
        ELSE NULL
      END AS avg_earnings,
      CASE
        WHEN new_hire_avg_earnings_weight > 0
          THEN new_hire_avg_earnings_weighted_sum / new_hire_avg_earnings_weight
        ELSE NULL
      END AS new_hire_avg_earnings,
      CASE
        WHEN separation_avg_earnings_weight > 0
          THEN separation_avg_earnings_weighted_sum / separation_avg_earnings_weight
        ELSE NULL
      END AS separation_avg_earnings,
      hires,
      separations,
      replacements,
      payroll,
      CASE
        WHEN employment > 0 THEN hires / employment
        ELSE NULL
      END AS hire_rate,
      CASE
        WHEN employment > 0 THEN separations / employment
        ELSE NULL
      END AS separation_rate,
      CASE
        WHEN employment > 0 THEN replacements / employment
        ELSE NULL
      END AS replacement_rate,
      CASE
        WHEN employment > 0 THEN payroll / employment
        ELSE NULL
      END AS payroll_per_employee,
      source
    FROM division_rollup_base
  ),
  us_rollup_base AS (
    SELECT
      'us' AS geo_level,
      '1' AS geo_id,
      'United States' AS geo_name,
      c.year,
      CAST(NULL AS VARCHAR) AS state_fips,
      CAST(NULL AS VARCHAR) AS state_abbr,
      c.demo_family,
      c.demo_code,
      MIN(c.demo_label) AS demo_label,
      MIN(c.demo_sort_order) AS demo_sort_order,
      BOOL_OR(c.is_total_demo) AS is_total_demo,
      c.industry_code,
      MIN(c.industry_label) AS industry_label,
      MIN(c.industry_rollup_family) AS industry_rollup_family,
      BOOL_OR(c.is_total_industry) AS is_total_industry,
      MIN(c.ownercode) AS ownercode,
      MIN(c.periodicity) AS periodicity,
      MIN(c.source_periodicity) AS source_periodicity,
      MIN(c.quarters_observed) AS quarters_observed,
      MIN(c.release_id) AS release_id,
      MIN(c.schema_version) AS schema_version,
      MIN(c.metadata_period_range) AS metadata_period_range,
      SUM(c.employment) AS employment,
      SUM(
        CASE
          WHEN c.avg_earnings IS NOT NULL AND c.employment > 0
            THEN c.avg_earnings * c.employment
          ELSE NULL
        END
      ) AS avg_earnings_weighted_sum,
      SUM(
        CASE
          WHEN c.avg_earnings IS NOT NULL AND c.employment > 0
            THEN c.employment
          ELSE NULL
        END
      ) AS avg_earnings_weight,
      SUM(
        CASE
          WHEN c.new_hire_avg_earnings IS NOT NULL AND c.hires > 0
            THEN c.new_hire_avg_earnings * c.hires
          ELSE NULL
        END
      ) AS new_hire_avg_earnings_weighted_sum,
      SUM(
        CASE
          WHEN c.new_hire_avg_earnings IS NOT NULL AND c.hires > 0
            THEN c.hires
          ELSE NULL
        END
      ) AS new_hire_avg_earnings_weight,
      SUM(
        CASE
          WHEN c.separation_avg_earnings IS NOT NULL AND c.separations > 0
            THEN c.separation_avg_earnings * c.separations
          ELSE NULL
        END
      ) AS separation_avg_earnings_weighted_sum,
      SUM(
        CASE
          WHEN c.separation_avg_earnings IS NOT NULL AND c.separations > 0
            THEN c.separations
          ELSE NULL
        END
      ) AS separation_avg_earnings_weight,
      SUM(c.hires) AS hires,
      SUM(c.separations) AS separations,
      SUM(c.replacements) AS replacements,
      SUM(c.payroll) AS payroll,
      MIN(c.source) AS source
    FROM county_base c
    GROUP BY
      c.year,
      c.demo_family,
      c.demo_code,
      c.industry_code
  ),
  us_rollup AS (
    SELECT
      geo_level,
      geo_id,
      geo_name,
      year,
      state_fips,
      state_abbr,
      demo_family,
      demo_code,
      demo_label,
      demo_sort_order,
      is_total_demo,
      industry_code,
      industry_label,
      industry_rollup_family,
      is_total_industry,
      ownercode,
      periodicity,
      source_periodicity,
      quarters_observed,
      release_id,
      schema_version,
      metadata_period_range,
      employment,
      CASE
        WHEN avg_earnings_weight > 0
          THEN avg_earnings_weighted_sum / avg_earnings_weight
        ELSE NULL
      END AS avg_earnings,
      CASE
        WHEN new_hire_avg_earnings_weight > 0
          THEN new_hire_avg_earnings_weighted_sum / new_hire_avg_earnings_weight
        ELSE NULL
      END AS new_hire_avg_earnings,
      CASE
        WHEN separation_avg_earnings_weight > 0
          THEN separation_avg_earnings_weighted_sum / separation_avg_earnings_weight
        ELSE NULL
      END AS separation_avg_earnings,
      hires,
      separations,
      replacements,
      payroll,
      CASE
        WHEN employment > 0 THEN hires / employment
        ELSE NULL
      END AS hire_rate,
      CASE
        WHEN employment > 0 THEN separations / employment
        ELSE NULL
      END AS separation_rate,
      CASE
        WHEN employment > 0 THEN replacements / employment
        ELSE NULL
      END AS replacement_rate,
      CASE
        WHEN employment > 0 THEN payroll / employment
        ELSE NULL
      END AS payroll_per_employee,
      source
    FROM us_rollup_base
  )
  SELECT * FROM county_base
  UNION ALL
  SELECT * FROM cbsa_rollup
  UNION ALL
  SELECT * FROM state_rollup
  UNION ALL
  SELECT * FROM division_rollup
  UNION ALL
  SELECT * FROM us_rollup
  "
)

# 3. Post-write QA ----
duplicate_rows <- DBI::dbGetQuery(
  con,
  "
  SELECT COUNT(*) AS duplicate_rows
  FROM (
    SELECT
      geo_level,
      geo_id,
      year,
      demo_family,
      demo_code,
      industry_code,
      COUNT(*) AS n
    FROM silver.lehd_qwi
    GROUP BY 1, 2, 3, 4, 5, 6
    HAVING COUNT(*) > 1
  )
  "
)

if (duplicate_rows$duplicate_rows[[1]] > 0) {
  stop(
    sprintf(
      "silver.lehd_qwi has duplicate geo_level + geo_id + year + demo_family + demo_code + industry_code rows (%s duplicates).",
      duplicate_rows$duplicate_rows[[1]]
    ),
    call. = FALSE
  )
}

negative_measure_rows <- DBI::dbGetQuery(
  con,
  "
  SELECT
    SUM(
      CASE
        WHEN employment < 0
          OR hires < 0
          OR separations < 0
          OR replacements < 0
          OR payroll < 0
        THEN 1
        ELSE 0
      END
    ) AS negative_rows
  FROM silver.lehd_qwi
  "
)

if (negative_measure_rows$negative_rows[[1]] > 0) {
  stop(
    sprintf(
      "silver.lehd_qwi contains %s rows with negative count or payroll measures.",
      negative_measure_rows$negative_rows[[1]]
    ),
    call. = FALSE
  )
}

missing_labels <- DBI::dbGetQuery(
  con,
  "
  SELECT
    SUM(CASE WHEN demo_label IS NULL THEN 1 ELSE 0 END) AS missing_demo_labels,
    SUM(CASE WHEN industry_label IS NULL THEN 1 ELSE 0 END) AS missing_industry_labels
  FROM silver.lehd_qwi
  "
)

if (missing_labels$missing_demo_labels[[1]] > 0 || missing_labels$missing_industry_labels[[1]] > 0) {
  stop("silver.lehd_qwi contains null demo or industry labels after standardization.", call. = FALSE)
}

DBI::dbExecute(con, "CHECKPOINT")
