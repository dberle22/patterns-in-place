# In this script we turn the annualized state + metro LEHD J2J staging table
# into a canonical Silver labor-mobility table.
#
# 1. Audit the staged geography coverage and mapping domains.
# 2. Standardize the staged state and metro rows to one analytical contract.
# 3. Derive canonical mobility rates and earnings-delta measures only when the
#    annual row is complete enough to support them.
# 4. Write `silver.lehd_j2j`.

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
DBI::dbExecute(con, "CREATE SCHEMA IF NOT EXISTS silver;")

on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

demo_map <- tibble::tribble(
  ~demo_code, ~demo_label, ~demo_sort_order, ~is_total_demo,
  "A00", "All Ages (14-99)", 0L, TRUE,
  "A01", "Age 14-18", 1L, FALSE,
  "A02", "Age 19-21", 2L, FALSE,
  "A03", "Age 22-24", 3L, FALSE,
  "A04", "Age 25-34", 4L, FALSE,
  "A05", "Age 35-44", 5L, FALSE,
  "A06", "Age 45-54", 6L, FALSE,
  "A07", "Age 55-64", 7L, FALSE,
  "A08", "Age 65-99", 8L, FALSE
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

state_ref <- DBI::dbGetQuery(
  con,
  "SELECT state_fips, state_abbr, state_name FROM silver.xwalk_state_region"
) %>%
  dplyr::mutate(dplyr::across(dplyr::everything(), as.character)) %>%
  dplyr::distinct(.data$state_fips, .keep_all = TRUE)

metro_ref <- DBI::dbGetQuery(
  con,
  "
  SELECT DISTINCT
    cbsa_code,
    cbsa_name
  FROM silver.xwalk_cbsa_county
  "
) %>%
  dplyr::transmute(
    cbsa_code = as.character(.data$cbsa_code),
    cbsa_name = as.character(.data$cbsa_name)
  ) %>%
  dplyr::distinct(.data$cbsa_code, .keep_all = TRUE)

unmapped_demo_codes <- DBI::dbGetQuery(
  con,
  "SELECT DISTINCT agegrp AS demo_code FROM staging.lehd_j2j"
) %>%
  dplyr::mutate(demo_code = as.character(.data$demo_code)) %>%
  dplyr::anti_join(
    demo_map %>% dplyr::select("demo_code"),
    by = "demo_code"
  )

if (nrow(unmapped_demo_codes) > 0) {
  stop("LEHD J2J staging contains age codes that are not mapped in the Silver script.", call. = FALSE)
}

unmapped_industry_codes <- DBI::dbGetQuery(
  con,
  "SELECT DISTINCT industry_code FROM staging.lehd_j2j"
) %>%
  dplyr::mutate(industry_code = as.character(.data$industry_code)) %>%
  dplyr::anti_join(
    industry_map %>% dplyr::select("industry_code"),
    by = "industry_code"
  )

if (nrow(unmapped_industry_codes) > 0) {
  stop("LEHD J2J staging contains industry codes that are not mapped in the Silver script.", call. = FALSE)
}

invalid_geo_rows <- DBI::dbGetQuery(
  con,
  "
  SELECT
    SUM(CASE WHEN source_scope_type = 'state' AND geo_level <> 'S' THEN 1 ELSE 0 END) AS invalid_state_geo_level_rows,
    SUM(CASE WHEN source_scope_type = 'metro' AND geo_level <> 'B' THEN 1 ELSE 0 END) AS invalid_metro_geo_level_rows,
    SUM(CASE WHEN source_scope_type = 'state' AND NOT regexp_matches(geo_id, '^[0-9]{2}$') THEN 1 ELSE 0 END) AS invalid_state_geo_id_rows,
    SUM(CASE WHEN source_scope_type = 'metro' AND NOT regexp_matches(geo_id, '^[0-9]{5}$') THEN 1 ELSE 0 END) AS invalid_metro_geo_id_rows
  FROM staging.lehd_j2j
  "
)

if (invalid_geo_rows$invalid_state_geo_level_rows[[1]] > 0 ||
    invalid_geo_rows$invalid_metro_geo_level_rows[[1]] > 0 ||
    invalid_geo_rows$invalid_state_geo_id_rows[[1]] > 0 ||
    invalid_geo_rows$invalid_metro_geo_id_rows[[1]] > 0) {
  stop("LEHD J2J staging geography validation failed before Silver standardization.", call. = FALSE)
}

DBI::dbWriteTable(con, "tmp_lehd_j2j_demo_map", demo_map, temporary = TRUE, overwrite = TRUE)
DBI::dbWriteTable(con, "tmp_lehd_j2j_industry_map", industry_map, temporary = TRUE, overwrite = TRUE)
DBI::dbWriteTable(con, "tmp_lehd_j2j_state_ref", state_ref, temporary = TRUE, overwrite = TRUE)
DBI::dbWriteTable(con, "tmp_lehd_j2j_metro_ref", metro_ref, temporary = TRUE, overwrite = TRUE)

DBI::dbExecute(
  con,
  "
  CREATE OR REPLACE TABLE silver.lehd_j2j AS
  WITH standardized AS (
    SELECT
      CASE
        WHEN s.source_scope_type = 'state' THEN 'state'
        WHEN s.source_scope_type = 'metro' THEN 'cbsa'
      END AS geo_level,
      s.geo_id,
      CASE
        WHEN s.source_scope_type = 'state' THEN sr.state_name
        WHEN s.source_scope_type = 'metro' THEN COALESCE(mr.cbsa_name, CONCAT('Legacy metro code ', s.geo_id))
      END AS geo_name,
      s.source_scope_type,
      s.source_scope_id,
      CASE
        WHEN s.source_scope_type = 'state' THEN s.geo_id
        ELSE CAST(NULL AS VARCHAR)
      END AS state_fips,
      CASE
        WHEN s.source_scope_type = 'state' THEN sr.state_abbr
        ELSE CAST(NULL AS VARCHAR)
      END AS state_abbr,
      CAST(s.year AS INTEGER) AS year,
      s.demo_family,
      s.agegrp AS demo_code,
      dm.demo_label,
      dm.demo_sort_order,
      dm.is_total_demo,
      s.ind_level,
      s.industry_code,
      im.industry_label,
      im.industry_rollup_family,
      im.is_total_industry,
      CASE
        WHEN s.ind_level = 'A' THEN 'all_industries'
        WHEN s.ind_level = 'S' THEN 'sector'
        ELSE 'other'
      END AS industry_rollup_level,
      s.ownercode,
      s.periodicity,
      s.source_periodicity,
      CAST(s.quarters_observed AS INTEGER) AS quarters_observed,
      CASE
        WHEN CAST(s.quarters_observed AS INTEGER) = 4 THEN TRUE
        ELSE FALSE
      END AS is_complete_year,
      s.release_id,
      s.schema_version,
      s.metadata_period_range,
      CAST(s.latest_source_year AS INTEGER) AS latest_source_year,
      CAST(s.keep_start_year AS INTEGER) AS keep_start_year,
      CAST(s.keep_end_year AS INTEGER) AS keep_end_year,
      CAST(s.annual_mhire AS DOUBLE) AS hires_total,
      CAST(s.annual_msep AS DOUBLE) AS separations_total,
      CAST(s.annual_mjobstart AS DOUBLE) AS job_starts_total,
      CAST(s.annual_mjobend AS DOUBLE) AS job_ends_total,
      CAST(s.annual_eehire AS DOUBLE) AS hires_from_employment,
      CAST(s.annual_eesep AS DOUBLE) AS separations_to_employment,
      CAST(s.annual_aqhire AS DOUBLE) AS hires_from_adjacent_quarter_nonemployment,
      CAST(s.annual_aqsep AS DOUBLE) AS separations_to_adjacent_quarter_nonemployment,
      CAST(s.annual_j2jhire AS DOUBLE) AS j2j_hires,
      CAST(s.annual_j2jsep AS DOUBLE) AS j2j_separations,
      CAST(s.annual_nehire AS DOUBLE) AS hires_from_nonemployment,
      CAST(s.annual_ensep AS DOUBLE) AS separations_to_nonemployment,
      CAST(s.annual_avg_nepersist AS DOUBLE) AS avg_nonemployment_persistence,
      CAST(s.annual_avg_enpersist AS DOUBLE) AS avg_employment_persistence_after_nonemployment,
      CAST(s.annual_avg_nefullq AS DOUBLE) AS avg_full_quarter_nonemployment,
      CAST(s.annual_avg_enfullq AS DOUBLE) AS avg_full_quarter_employment_after_nonemployment,
      CAST(s.annual_avg_mainb AS DOUBLE) AS avg_main_job_beginning_count,
      CAST(s.annual_avg_maine AS DOUBLE) AS avg_main_job_ending_count,
      CAST(s.annual_avg_nepersists AS DOUBLE) AS avg_nonemployment_persistence_stable_count,
      CAST(s.annual_avg_enpersists AS DOUBLE) AS avg_employment_persistence_stable_count,
      CAST(s.annual_avg_jobstays AS DOUBLE) AS avg_job_stayers_count,
      CAST(s.annual_avg_mainbs AS DOUBLE) AS avg_main_job_beginning_stable_count,
      CAST(s.annual_avg_maines AS DOUBLE) AS avg_main_job_ending_stable_count,
      CAST(s.annual_avg_nehiresearn_dest AS DOUBLE) AS avg_nonemployment_hire_earnings_dest,
      CAST(s.annual_avg_ensepsearn_orig AS DOUBLE) AS avg_nonemployment_sep_earnings_orig,
      CAST(s.annual_avg_jobstaysearn_orig AS DOUBLE) AS avg_jobstayer_earnings_orig,
      CAST(s.annual_avg_jobstaysearn_dest AS DOUBLE) AS avg_jobstayer_earnings_dest,
      CAST(s.annual_avg_eesepsearn_orig AS DOUBLE) AS avg_ee_sep_earnings_orig,
      CAST(s.annual_avg_eehiresearn_dest AS DOUBLE) AS avg_ee_hire_earnings_dest,
      CAST(s.annual_avg_aqsepsearn_orig AS DOUBLE) AS avg_aq_sep_earnings_orig,
      CAST(s.annual_avg_aqhiresearn_dest AS DOUBLE) AS avg_aq_hire_earnings_dest,
      CASE
        WHEN CAST(s.quarters_observed AS INTEGER) = 4 AND s.annual_mhire > 0
          THEN CAST(s.annual_j2jhire AS DOUBLE) / CAST(s.annual_mhire AS DOUBLE)
        ELSE NULL
      END AS j2j_hire_share,
      CASE
        WHEN CAST(s.quarters_observed AS INTEGER) = 4 AND s.annual_msep > 0
          THEN CAST(s.annual_j2jsep AS DOUBLE) / CAST(s.annual_msep AS DOUBLE)
        ELSE NULL
      END AS j2j_sep_share,
      CASE
        WHEN CAST(s.quarters_observed AS INTEGER) = 4 AND s.annual_mhire > 0
          THEN CAST(s.annual_eehire AS DOUBLE) / CAST(s.annual_mhire AS DOUBLE)
        ELSE NULL
      END AS ee_hire_share,
      CASE
        WHEN CAST(s.quarters_observed AS INTEGER) = 4 AND s.annual_mhire > 0
          THEN CAST(s.annual_nehire AS DOUBLE) / CAST(s.annual_mhire AS DOUBLE)
        ELSE NULL
      END AS ne_hire_share,
      CASE
        WHEN CAST(s.quarters_observed AS INTEGER) = 4 AND s.annual_msep > 0
          THEN CAST(s.annual_eesep AS DOUBLE) / CAST(s.annual_msep AS DOUBLE)
        ELSE NULL
      END AS ee_sep_share,
      CASE
        WHEN CAST(s.quarters_observed AS INTEGER) = 4 AND s.annual_msep > 0
          THEN CAST(s.annual_ensep AS DOUBLE) / CAST(s.annual_msep AS DOUBLE)
        ELSE NULL
      END AS en_sep_share,
      CASE
        WHEN CAST(s.quarters_observed AS INTEGER) = 4
          AND s.annual_avg_eehiresearn_dest IS NOT NULL
          AND s.annual_avg_eesepsearn_orig IS NOT NULL
        THEN CAST(s.annual_avg_eehiresearn_dest AS DOUBLE) - CAST(s.annual_avg_eesepsearn_orig AS DOUBLE)
        ELSE NULL
      END AS avg_ee_earnings_delta,
      CASE
        WHEN mr.cbsa_name IS NOT NULL THEN TRUE
        WHEN s.source_scope_type = 'metro' THEN FALSE
        ELSE NULL
      END AS has_current_cbsa_match,
      'Census LEHD J2J' AS source
    FROM staging.lehd_j2j s
    INNER JOIN tmp_lehd_j2j_demo_map dm
      ON s.agegrp = dm.demo_code
    INNER JOIN tmp_lehd_j2j_industry_map im
      ON s.industry_code = im.industry_code
    LEFT JOIN tmp_lehd_j2j_state_ref sr
      ON s.source_scope_type = 'state'
      AND s.geo_id = sr.state_fips
    LEFT JOIN tmp_lehd_j2j_metro_ref mr
      ON s.source_scope_type = 'metro'
      AND s.geo_id = mr.cbsa_code
  )
  SELECT *
  FROM standardized
  "
)

duplicate_summary <- DBI::dbGetQuery(
  con,
  "
  SELECT COUNT(*) AS duplicate_keys
  FROM (
    SELECT
      geo_level,
      geo_id,
      year,
      demo_code,
      industry_code,
      COUNT(*) AS n
    FROM silver.lehd_j2j
    GROUP BY 1,2,3,4,5
    HAVING COUNT(*) > 1
  )
  "
)

if (duplicate_summary$duplicate_keys[[1]] > 0) {
  stop(
    sprintf(
      "LEHD J2J Silver is not unique at geo_level + geo_id + year + demo_code + industry_code. Duplicate keys found: %s",
      duplicate_summary$duplicate_keys[[1]]
    ),
    call. = FALSE
  )
}

invalid_scope_summary <- DBI::dbGetQuery(
  con,
  "
  SELECT
    SUM(CASE WHEN geo_level NOT IN ('state', 'cbsa') THEN 1 ELSE 0 END) AS invalid_geo_levels,
    SUM(CASE WHEN demo_family <> 'age' THEN 1 ELSE 0 END) AS invalid_demo_families,
    SUM(CASE WHEN periodicity <> 'A' THEN 1 ELSE 0 END) AS non_annual_rows,
    SUM(CASE WHEN source_periodicity <> 'Q' THEN 1 ELSE 0 END) AS non_quarter_sources
  FROM silver.lehd_j2j
  "
)

if (invalid_scope_summary$invalid_geo_levels[[1]] > 0) {
  stop("LEHD J2J Silver contains invalid geography levels.", call. = FALSE)
}

if (invalid_scope_summary$invalid_demo_families[[1]] > 0) {
  stop("LEHD J2J Silver contains demo families outside the approved age-only scope.", call. = FALSE)
}

if (invalid_scope_summary$non_annual_rows[[1]] > 0) {
  stop("LEHD J2J Silver contains non-annual rows.", call. = FALSE)
}

if (invalid_scope_summary$non_quarter_sources[[1]] > 0) {
  stop("LEHD J2J Silver contains unexpected source periodicity values.", call. = FALSE)
}

DBI::dbExecute(con, "CHECKPOINT")
