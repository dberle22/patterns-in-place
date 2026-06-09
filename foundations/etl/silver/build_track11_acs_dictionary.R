source(here::here("foundations", "etl", "utils.R"))
library(yaml)

db_path <- get_env_path("DB_PATH")
con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = TRUE)
on.exit(DBI::dbDisconnect(con), add = TRUE)

dict_dir <- here::here("foundations", "data_dictionary", "layers", "silver")

numeric_types <- c(
  "TINYINT", "SMALLINT", "INTEGER", "BIGINT", "HUGEINT",
  "UTINYINT", "USMALLINT", "UINTEGER", "UBIGINT",
  "FLOAT", "DOUBLE", "DECIMAL"
)

shared_defs <- list(
  geo_level = "Geographic level (US, region, division, state, county, place, zcta, tract, cbsa)",
  geo_id = "Geographic identifier for the row",
  geo_name = "Geographic name (from ACS NAME)",
  year = "Observation year or period year for the row."
)

quote_ident <- function(x) as.character(DBI::dbQuoteIdentifier(con, x))

format_md_value <- function(x) {
  if (is.null(x) || length(x) == 0 || is.na(x)) return("NULL")
  as.character(x)
}

english_label <- function(name) {
  name %>%
    stringr::str_replace_all("_", " ") %>%
    stringr::str_replace_all("incl ", "including ") %>%
    stringr::str_replace_all(" incl ", " including ") %>%
    stringr::str_replace_all("5 17", "5 to 17") %>%
    stringr::str_replace_all("18 34", "18 to 34") %>%
    stringr::str_replace_all("35 64", "35 to 64") %>%
    stringr::str_replace_all("65 74", "65 to 74") %>%
    stringr::str_replace_all("75 plus", "75 and older")
}

get_broadband_defs <- function(table_name) {
  defs <- c(
    shared_defs,
    internet_total_hhE = "Total households in the broadband and internet-access universe.",
    internet_with_subscriptionE = "Households with an internet subscription of any kind.",
    internet_dial_up_onlyE = "Households with dial-up internet service only.",
    internet_broadband_anyE = "Households with a broadband internet subscription of any kind.",
    internet_cellular_data_onlyE = "Households with only a cellular data plan and no other internet subscription.",
    internet_cellular_and_otherE = "Households with a cellular data plan plus one or more non-broadband internet subscriptions.",
    internet_broadband_and_cellularE = "Households with a broadband subscription and a cellular data plan.",
    internet_broadband_no_cellularE = "Households with a broadband subscription and no cellular data plan.",
    internet_satellite_onlyE = "Households with a satellite internet subscription only.",
    internet_satellite_and_otherE = "Households with satellite internet plus another non-cellular subscription type.",
    internet_other_serviceE = "Households with another internet service type not captured by the named categories.",
    internet_access_no_subscriptionE = "Households with internet access but no paid internet subscription.",
    internet_no_accessE = "Households with no internet access."
  )

  if (table_name == "broadband_kpi") {
    defs <- c(
      shared_defs,
      internet_total_hh = "Total households in the broadband and internet-access universe.",
      internet_with_subscription = "Households with an internet subscription of any kind.",
      internet_broadband_subscription = "Households with a broadband internet subscription of any kind.",
      internet_cellular_only = "Households with only a cellular data plan and no other internet subscription.",
      internet_access_no_subscription = "Households with internet access but no paid internet subscription.",
      internet_no_access = "Households with no internet access.",
      internet_with_any_access = "Households with any form of internet access, whether subscribed or not.",
      pct_internet_subscription = "Share of households with an internet subscription of any kind.",
      pct_broadband_subscription = "Share of households with a broadband internet subscription.",
      pct_cellular_only = "Share of households that rely on only a cellular data plan.",
      pct_access_no_subscription = "Share of households with internet access but no subscription.",
      pct_no_internet_access = "Share of households with no internet access.",
      pct_any_internet_access = "Share of households with any form of internet access."
    )
  }

  defs
}

get_disability_base_def <- function(column_name) {
  if (column_name %in% names(shared_defs)) return(shared_defs[[column_name]])
  if (column_name == "disability_totalE") {
    return("Total civilian noninstitutionalized population in the disability-status universe.")
  }

  stem <- stringr::str_remove(column_name, "E$")
  stem <- stringr::str_remove(stem, "^disability_")

  if (stem %in% c("male_total", "female_total")) {
    sex <- ifelse(stem == "male_total", "Male", "Female")
    return(sprintf("%s civilian noninstitutionalized population in the disability-status universe.", sex))
  }

  if (stringr::str_ends(stem, "_with_disability")) {
    subject <- stringr::str_remove(stem, "_with_disability$")
    return(sprintf("%s with a disability.", english_label(subject) %>% stringr::str_to_sentence()))
  }

  if (stringr::str_ends(stem, "_no_disability")) {
    subject <- stringr::str_remove(stem, "_no_disability$")
    return(sprintf("%s without a disability.", english_label(subject) %>% stringr::str_to_sentence()))
  }

  if (stringr::str_ends(stem, "_total")) {
    subject <- stringr::str_remove(stem, "_total$")
    return(sprintf("%s in the disability-status universe.", english_label(subject) %>% stringr::str_to_sentence()))
  }

  "Disability-status count from ACS B18101."
}

get_disability_kpi_defs <- function() {
  c(
    shared_defs,
    disability_total = "Total civilian noninstitutionalized population in the disability-status universe.",
    disability_with = "Population with a disability.",
    disability_without = "Population without a disability.",
    disability_male_total = "Male civilian noninstitutionalized population in the disability-status universe.",
    disability_male_with = "Male population with a disability.",
    disability_female_total = "Female civilian noninstitutionalized population in the disability-status universe.",
    disability_female_with = "Female population with a disability.",
    disability_under_5_total = "Population under age 5 in the disability-status universe.",
    disability_under_5_with = "Population under age 5 with a disability.",
    disability_5_17_total = "Population ages 5 to 17 in the disability-status universe.",
    disability_5_17_with = "Population ages 5 to 17 with a disability.",
    disability_18_34_total = "Population ages 18 to 34 in the disability-status universe.",
    disability_18_34_with = "Population ages 18 to 34 with a disability.",
    disability_35_64_total = "Population ages 35 to 64 in the disability-status universe.",
    disability_35_64_with = "Population ages 35 to 64 with a disability.",
    disability_65_74_total = "Population ages 65 to 74 in the disability-status universe.",
    disability_65_74_with = "Population ages 65 to 74 with a disability.",
    disability_75_plus_total = "Population age 75 and older in the disability-status universe.",
    disability_75_plus_with = "Population age 75 and older with a disability.",
    disability_under_18_total = "Population under age 18 in the disability-status universe.",
    disability_under_18_with = "Population under age 18 with a disability.",
    disability_18_64_total = "Population ages 18 to 64 in the disability-status universe.",
    disability_18_64_with = "Population ages 18 to 64 with a disability.",
    disability_65_plus_total = "Population age 65 and older in the disability-status universe.",
    disability_65_plus_with = "Population age 65 and older with a disability.",
    pct_disabled = "Share of the disability-status universe with a disability.",
    pct_disabled_male = "Share of the male disability-status universe with a disability.",
    pct_disabled_female = "Share of the female disability-status universe with a disability.",
    pct_disabled_under_5 = "Share of the under-5 disability-status universe with a disability.",
    pct_disabled_5_17 = "Share of the ages 5 to 17 disability-status universe with a disability.",
    pct_disabled_18_34 = "Share of the ages 18 to 34 disability-status universe with a disability.",
    pct_disabled_35_64 = "Share of the ages 35 to 64 disability-status universe with a disability.",
    pct_disabled_65_74 = "Share of the ages 65 to 74 disability-status universe with a disability.",
    pct_disabled_75_plus = "Share of the age 75 and older disability-status universe with a disability.",
    pct_disabled_under_18 = "Share of the under-18 disability-status universe with a disability.",
    pct_disabled_18_64 = "Share of the ages 18 to 64 disability-status universe with a disability.",
    pct_disabled_65_plus = "Share of the age 65 and older disability-status universe with a disability."
  )
}

get_language_base_def <- function(column_name) {
  if (column_name %in% names(shared_defs)) return(shared_defs[[column_name]])
  if (column_name == "language_totalE") {
    return("Total population age 5 and older in the language-spoken-at-home universe.")
  }

  stem <- stringr::str_remove(column_name, "E$")
  stem <- stringr::str_remove(stem, "^language_")

  if (stem == "speak_only_english") {
    return("Population age 5 and older who speak only English at home.")
  }

  if (stringr::str_ends(stem, "_speak_english_very_well")) {
    subject <- stringr::str_remove(stem, "_speak_english_very_well$")
    return(sprintf(
      "Population age 5 and older who speak %s at home and speak English very well.",
      english_label(subject)
    ))
  }

  if (stringr::str_ends(stem, "_speak_english_less_than_very_well")) {
    subject <- stringr::str_remove(stem, "_speak_english_less_than_very_well$")
    return(sprintf(
      "Population age 5 and older who speak %s at home and speak English less than very well.",
      english_label(subject)
    ))
  }

  sprintf("Population age 5 and older who speak %s at home.", english_label(stem))
}

get_language_kpi_defs <- function() {
  c(
    shared_defs,
    language_total = "Total population age 5 and older in the language-spoken-at-home universe.",
    language_english_only = "Population age 5 and older who speak only English at home.",
    language_non_english = "Population age 5 and older who speak a language other than English at home.",
    language_limited_english = "Population age 5 and older who speak a language other than English at home and speak English less than very well.",
    language_spanish = "Population age 5 and older who speak Spanish at home.",
    language_other_indo_european = "Population age 5 and older who speak a non-Spanish Indo-European language at home.",
    language_asian_pacific = "Population age 5 and older who speak an Asian or Pacific language at home.",
    language_middle_eastern_african = "Population age 5 and older who speak an Arabic, Afro-Asiatic, or African language at home.",
    language_native_north_american = "Population age 5 and older who speak a Native North American language at home.",
    language_other_unspecified = "Population age 5 and older who speak another or unspecified language at home.",
    pct_english_only = "Share of the language-spoken-at-home universe that speaks only English at home.",
    pct_non_english = "Share of the language-spoken-at-home universe that speaks a language other than English at home.",
    pct_limited_english = "Share of the language-spoken-at-home universe that speaks English less than very well.",
    pct_spanish = "Share of the language-spoken-at-home universe that speaks Spanish at home.",
    pct_other_indo_european = "Share of the language-spoken-at-home universe that speaks a non-Spanish Indo-European language at home.",
    pct_asian_pacific = "Share of the language-spoken-at-home universe that speaks an Asian or Pacific language at home.",
    pct_middle_eastern_african = "Share of the language-spoken-at-home universe that speaks an Arabic, Afro-Asiatic, or African language at home.",
    pct_native_north_american = "Share of the language-spoken-at-home universe that speaks a Native North American language at home.",
    pct_other_unspecified = "Share of the language-spoken-at-home universe that speaks another or unspecified language at home."
  )
}

profile_column <- function(table_name, column_name, data_type) {
  table_ref <- sprintf("silver.%s", table_name)
  col_ref <- quote_ident(column_name)
  is_numeric <- toupper(data_type) %in% numeric_types

  basic <- DBI::dbGetQuery(
    con,
    glue::glue("
      SELECT
        SUM(CASE WHEN {col_ref} IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS null_pct,
        COUNT(DISTINCT {col_ref}) AS distinct_count
      FROM {table_ref}
    ")
  )

  if (is_numeric) {
    range_stats <- DBI::dbGetQuery(
      con,
      glue::glue("
        SELECT MIN({col_ref}) AS min_value, MAX({col_ref}) AS max_value
        FROM {table_ref}
        WHERE {col_ref} IS NOT NULL
      ")
    )
    min_value <- range_stats$min_value[[1]]
    max_value <- range_stats$max_value[[1]]
    min_length <- NA
    max_length <- NA
  } else {
    range_stats <- DBI::dbGetQuery(
      con,
      glue::glue("
        SELECT
          MIN(LENGTH(CAST({col_ref} AS VARCHAR))) AS min_length,
          MAX(LENGTH(CAST({col_ref} AS VARCHAR))) AS max_length
        FROM {table_ref}
        WHERE {col_ref} IS NOT NULL
      ")
    )
    min_value <- NA
    max_value <- NA
    min_length <- range_stats$min_length[[1]]
    max_length <- range_stats$max_length[[1]]
  }

  top_values <- DBI::dbGetQuery(
    con,
    glue::glue("
      SELECT CAST({col_ref} AS VARCHAR) AS value, COUNT(*) AS count
      FROM {table_ref}
      GROUP BY 1
      ORDER BY count DESC, value NULLS LAST
      LIMIT 5
    ")
  )

  if (nrow(top_values) == 0) {
    top_values <- tibble::tibble(value = character(), count = integer())
  }

  top_values$value[is.na(top_values$value)] <- NA_character_

  list(
    name = column_name,
    type = data_type,
    null_pct = round(basic$null_pct[[1]], 4),
    distinct_count = as.integer(basic$distinct_count[[1]]),
    min_value = min_value,
    max_value = max_value,
    min_length = min_length,
    max_length = max_length,
    top_values = purrr::pmap(
      top_values,
      function(value, count) list(value = value, count = as.integer(count))
    )
  )
}

key_stats <- function(table_name) {
  combos <- list(
    c("geo_level", "geo_id", "geo_name", "year"),
    c("geo_level", "geo_id", "year"),
    c("geo_id", "year"),
    c("geo_level")
  )

  purrr::map(combos, function(cols) {
    cols_sql <- paste(vapply(cols, quote_ident, character(1)), collapse = ", ")
    out <- DBI::dbGetQuery(
      con,
      glue::glue("
        SELECT
          COUNT(*) AS rows,
          COUNT(*) - COUNT(DISTINCT ({cols_sql})) AS duplicates,
          COUNT(DISTINCT ({cols_sql})) AS distinct_count
        FROM silver.{table_name}
      ")
    )

    list(
      cols = cols,
      rows = as.integer(out$rows[[1]]),
      distinct_count = as.integer(out$distinct_count[[1]]),
      duplicates = as.integer(out$duplicates[[1]])
    )
  })
}

build_md <- function(table_name, purpose, row_count, pk, year_min, year_max, distinct_geo_levels, distinct_geo_id, columns, lineage_note, is_kpi) {
  null_columns <- columns[vapply(columns, function(x) x$null_pct > 0, logical(1))]
  null_note <- if (length(null_columns) == 0) {
    "- No columns with non-zero null rates in current snapshot."
  } else {
    vals <- vapply(null_columns, function(x) sprintf("%s=%.4f%%", x$name, x$null_pct), character(1))
    if (length(vals) > 10) vals <- c(vals[1:10], "...")
    paste0("- Columns with non-zero null rates: ", paste(vals, collapse = ", "))
  }

  lines <- c(
    sprintf("# Data Dictionary: silver.%s", table_name),
    "",
    "## Overview",
    sprintf("- **Table**: `silver.%s`", table_name),
    sprintf("- **Purpose**: %s", purpose),
    sprintf("- **Row count**: %s", format(row_count, big.mark = ",")),
    sprintf("- **KPI applicability**: %s", ifelse(is_kpi, "KPI table (or has KPI dictionary entries).", "Base/source-aligned Silver table.")),
    "",
    "## Grain & Keys",
    "- **Declared grain (inferred)**: One row per `geo_level + geo_id + geo_name + year`.",
    "- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `geo_name`, `year`)"
  )

  for (stat in pk) {
    lines <- c(
      lines,
      sprintf(
        "  - `%s` => rows=%s, distinct=%s, duplicates=%s",
        paste(stat$cols, collapse = " + "),
        stat$rows,
        stat$distinct_count,
        stat$duplicates
      )
    )
  }

  lines <- c(
    lines,
    sprintf("- **Time coverage**: `year` min=%s, max=%s", year_min, year_max),
    sprintf("- **Geo coverage**: distinct_geo_levels=%s; distinct_geo_id=%s", distinct_geo_levels, distinct_geo_id),
    "",
    "## Columns",
    "",
    "| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |",
    "|---|---|---:|---:|---|---|---|"
  )

  for (col in columns) {
    range_txt <- if (!is.na(col$min_value) || !is.na(col$max_value)) {
      sprintf("min %s, max %s", format_md_value(col$min_value), format_md_value(col$max_value))
    } else if (!is.na(col$min_length) || !is.na(col$max_length)) {
      sprintf("len %s-%s", format_md_value(col$min_length), format_md_value(col$max_length))
    } else {
      ""
    }

    top_txt <- paste(
      vapply(
        col$top_values,
        function(tv) sprintf("%s (%s)", format_md_value(tv$value), tv$count),
        character(1)
      ),
      collapse = "; "
    )

    lines <- c(
      lines,
      sprintf(
        "| `%s` | `%s` | %.4f | %s | %s | %s | %s |",
        col$name,
        col$type,
        col$null_pct,
        format(col$distinct_count, big.mark = ","),
        range_txt,
        top_txt,
        col$definition
      )
    )
  }

  lines <- c(
    lines,
    "## Data Quality Notes",
    null_note,
    "- Primary/foreign keys are not enforced as DB constraints in current pipeline.",
    "",
    "## Lineage",
    "1. **Creation/write references**:",
    paste0("   - `", lineage_note, "`"),
    "",
    "## Known Gaps / To-Dos",
    "- Validate and harden grain/PK contracts with automated DQ checks.",
    "- Re-run the landed profile after major ACS topic changes and sync both this `.md` file and the companion `.yml` artifact."
  )

  paste(lines, collapse = "\n")
}

build_yaml <- function(table_name, columns, lineage_script, lineage_details) {
  year_stats <- DBI::dbGetQuery(con, glue::glue("SELECT MIN(year) AS min_year, MAX(year) AS max_year FROM silver.{table_name}"))
  geo_stats <- DBI::dbGetQuery(
    con,
    glue::glue("
      SELECT
        COUNT(DISTINCT geo_level) AS distinct_geo_levels,
        COUNT(DISTINCT geo_id) AS distinct_geo_id
      FROM silver.{table_name}
    ")
  )

  yaml_obj <- list(
    table_name = table_name,
    schema = "silver",
    grain = "One row per geo_level + geo_id + geo_name + year (inferred).",
    primary_key = c("geo_level", "geo_id", "geo_name", "year"),
    foreign_keys = list(),
    time_coverage = list(
      type = "range",
      column = "year",
      min = as.character(year_stats$min_year[[1]]),
      max = as.character(year_stats$max_year[[1]])
    ),
    geo_coverage = list(
      notes = c(
        sprintf("distinct_geo_levels=%s", geo_stats$distinct_geo_levels[[1]]),
        sprintf("distinct_geo_id=%s", geo_stats$distinct_geo_id[[1]])
      )
    ),
    columns = lapply(columns, function(col) {
      list(
        name = col$name,
        type = col$type,
        null_pct = col$null_pct,
        distinct_count = col$distinct_count,
        min_value = if (is.na(col$min_value)) NULL else col$min_value,
        max_value = if (is.na(col$max_value)) NULL else col$max_value,
        min_length = if (is.na(col$min_length)) NULL else as.integer(col$min_length),
        max_length = if (is.na(col$max_length)) NULL else as.integer(col$max_length),
        top_values = lapply(col$top_values, function(tv) {
          list(value = if (is.na(tv$value)) NULL else tv$value, count = tv$count)
        }),
        definition = col$definition,
        needs_confirmation = "no"
      )
    }),
    lineage = list(
      list(
        step = "write_target",
        script = lineage_script,
        details = lineage_details
      )
    )
  )

  yaml::as.yaml(yaml_obj, indent.mapping.sequence = TRUE, line.sep = "\n")
}

document_table <- function(table_name, purpose, definitions, lineage_script, lineage_details, is_kpi = FALSE) {
  row_count <- DBI::dbGetQuery(con, glue::glue("SELECT COUNT(*) AS n FROM silver.{table_name}"))$n[[1]]
  schema_cols <- DBI::dbGetQuery(
    con,
    glue::glue("
      SELECT column_name, data_type
      FROM information_schema.columns
      WHERE table_schema = 'silver'
        AND table_name = '{table_name}'
      ORDER BY ordinal_position
    ")
  )

  columns <- purrr::pmap(schema_cols, function(column_name, data_type) {
    prof <- profile_column(table_name, column_name, data_type)
    prof$definition <- definitions[[column_name]] %||% "Needs definition confirmation."
    prof
  })

  pk <- key_stats(table_name)
  year_stats <- DBI::dbGetQuery(con, glue::glue("SELECT MIN(year) AS min_year, MAX(year) AS max_year FROM silver.{table_name}"))
  geo_stats <- DBI::dbGetQuery(
    con,
    glue::glue("
      SELECT
        COUNT(DISTINCT geo_level) AS distinct_geo_levels,
        COUNT(DISTINCT geo_id) AS distinct_geo_id
      FROM silver.{table_name}
    ")
  )

  md_text <- build_md(
    table_name = table_name,
    purpose = purpose,
    row_count = row_count,
    pk = pk,
    year_min = year_stats$min_year[[1]],
    year_max = year_stats$max_year[[1]],
    distinct_geo_levels = geo_stats$distinct_geo_levels[[1]],
    distinct_geo_id = geo_stats$distinct_geo_id[[1]],
    columns = columns,
    lineage_note = lineage_details,
    is_kpi = is_kpi
  )

  yaml_text <- build_yaml(table_name, columns, lineage_script, lineage_details)

  writeLines(md_text, file.path(dict_dir, sprintf("silver__%s.md", table_name)))
  writeLines(yaml_text, file.path(dict_dir, sprintf("silver__%s.yml", table_name)))
}

document_table(
  table_name = "broadband_base",
  purpose = "Silver broadband base table (`base` type).",
  definitions = get_broadband_defs("broadband_base"),
  lineage_script = "foundations/etl/silver/acs_broadband_silver.R",
  lineage_details = "foundations/etl/silver/acs_broadband_silver.R writes silver.broadband_base from staging.acs_broadband_* with CBSA rebasing from county data via silver.xwalk_cbsa_county.",
  is_kpi = FALSE
)

document_table(
  table_name = "broadband_kpi",
  purpose = "Silver broadband KPI table (`kpi` type).",
  definitions = get_broadband_defs("broadband_kpi"),
  lineage_script = "foundations/etl/silver/acs_broadband_silver.R",
  lineage_details = "foundations/etl/silver/acs_broadband_silver.R writes silver.broadband_kpi from staging.acs_broadband_* with CBSA rebasing from county data via silver.xwalk_cbsa_county.",
  is_kpi = TRUE
)

document_table(
  table_name = "disability_base",
  purpose = "Silver disability base table (`base` type).",
  definitions = stats::setNames(
    lapply(DBI::dbGetQuery(con, "SELECT column_name FROM information_schema.columns WHERE table_schema = 'silver' AND table_name = 'disability_base' ORDER BY ordinal_position")$column_name, get_disability_base_def),
    DBI::dbGetQuery(con, "SELECT column_name FROM information_schema.columns WHERE table_schema = 'silver' AND table_name = 'disability_base' ORDER BY ordinal_position")$column_name
  ),
  lineage_script = "foundations/etl/silver/acs_disability_silver.R",
  lineage_details = "foundations/etl/silver/acs_disability_silver.R writes silver.disability_base from staging.acs_disability_* with CBSA rebasing from county data via silver.xwalk_cbsa_county.",
  is_kpi = FALSE
)

document_table(
  table_name = "disability_kpi",
  purpose = "Silver disability KPI table (`kpi` type).",
  definitions = get_disability_kpi_defs(),
  lineage_script = "foundations/etl/silver/acs_disability_silver.R",
  lineage_details = "foundations/etl/silver/acs_disability_silver.R writes silver.disability_kpi from staging.acs_disability_* with CBSA rebasing from county data via silver.xwalk_cbsa_county.",
  is_kpi = TRUE
)

document_table(
  table_name = "language_base",
  purpose = "Silver language base table (`base` type).",
  definitions = stats::setNames(
    lapply(DBI::dbGetQuery(con, "SELECT column_name FROM information_schema.columns WHERE table_schema = 'silver' AND table_name = 'language_base' ORDER BY ordinal_position")$column_name, get_language_base_def),
    DBI::dbGetQuery(con, "SELECT column_name FROM information_schema.columns WHERE table_schema = 'silver' AND table_name = 'language_base' ORDER BY ordinal_position")$column_name
  ),
  lineage_script = "foundations/etl/silver/acs_language_silver.R",
  lineage_details = "foundations/etl/silver/acs_language_silver.R writes silver.language_base from staging.acs_language_* with CBSA rebasing from county data via silver.xwalk_cbsa_county.",
  is_kpi = FALSE
)

document_table(
  table_name = "language_kpi",
  purpose = "Silver language KPI table (`kpi` type).",
  definitions = get_language_kpi_defs(),
  lineage_script = "foundations/etl/silver/acs_language_silver.R",
  lineage_details = "foundations/etl/silver/acs_language_silver.R writes silver.language_kpi from staging.acs_language_* with CBSA rebasing from county data via silver.xwalk_cbsa_county.",
  is_kpi = TRUE
)
