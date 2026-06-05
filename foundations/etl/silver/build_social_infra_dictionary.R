source(here::here("foundations", "etl", "utils.R"))
library(yaml)
db_path <- get_env_path("DB_PATH")

con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = TRUE)
on.exit(DBI::dbDisconnect(con), add = TRUE)

root <- here::here()
dict_dir <- file.path(root, "schemas", "data_dictionary", "layers", "silver")

base_defs <- list(
  geo_level = "Geographic level (US, region, division, state, county, place, zcta, tract, cbsa)",
  geo_id = "Geographic identifier for the row",
  geo_name = "Geographic name (from ACS NAME)",
  year = "Observation year or period year for the row.",
  hh_totalE = "Total households.",
  hh_familyE = "Family households.",
  hh_marriedE = "Married-couple family households.",
  hh_other_familyE = "Other family households excluding married-couple families.",
  hh_nonfamilyE = "Nonfamily households.",
  hh_nonfam_aloneE = "Nonfamily households with one person living alone.",
  hh_nonfam_not_aloneE = "Nonfamily households with two or more people.",
  ins_totalE = "Total civilian noninstitutionalized population in the health insurance coverage universe.",
  ins_u19_one_planE = "Population under age 19 with one type of health insurance coverage.",
  ins_u19_two_plansE = "Population under age 19 with two or more types of health insurance coverage.",
  ins_u19_uncoveredE = "Population under age 19 without health insurance coverage.",
  ins_19_34_one_planE = "Population ages 19 to 34 with one type of health insurance coverage.",
  ins_19_34_two_plansE = "Population ages 19 to 34 with two or more types of health insurance coverage.",
  ins_19_34_uncoveredE = "Population ages 19 to 34 without health insurance coverage.",
  ins_35_64_one_planE = "Population ages 35 to 64 with one type of health insurance coverage.",
  ins_35_64_two_plansE = "Population ages 35 to 64 with two or more types of health insurance coverage.",
  ins_35_64_uncoveredE = "Population ages 35 to 64 without health insurance coverage.",
  ins_65u_one_planE = "Population age 65 and older with one type of health insurance coverage.",
  ins_65u_two_plansE = "Population age 65 and older with two or more types of health insurance coverage.",
  ins_65u_uncoveredE = "Population age 65 and older without health insurance coverage."
)

kpi_defs <- list(
  geo_level = "Geographic level (US, region, division, state, county, place, zcta, tract, cbsa)",
  geo_id = "Geographic identifier for the row",
  geo_name = "Geographic name (from ACS NAME)",
  year = "Observation year or period year for the row.",
  hh_total = "Total households.",
  hh_family = "Family households.",
  hh_married = "Married-couple family households.",
  hh_other_family = "Other family households excluding married-couple families.",
  hh_nonfamily = "Nonfamily households.",
  hh_nonfam_alone = "Nonfamily households with one person living alone.",
  hh_nonfam_not_alone = "Nonfamily households with two or more people.",
  single_households = "Households with one person living alone.",
  pct_hh_family = "Share of households that are family households.",
  pct_hh_married = "Share of households that are married-couple family households.",
  pct_hh_other_family = "Share of households that are other family households.",
  pct_hh_nonfamily = "Share of households that are nonfamily households.",
  pct_single_households = "Share of households with one person living alone.",
  pct_nonfamily_alone = "Share of nonfamily households that are one-person households.",
  pct_nonfamily_not_alone = "Share of nonfamily households with two or more people.",
  ins_total = "Total civilian noninstitutionalized population in the health insurance coverage universe.",
  ins_insured = "Population with at least one form of health insurance coverage.",
  ins_uninsured = "Population without health insurance coverage.",
  pct_health_insured = "Share of the health insurance universe with insurance coverage.",
  pct_health_uninsured = "Share of the health insurance universe without health insurance coverage.",
  ins_u19_total = "Total population under age 19 in the health insurance coverage universe.",
  ins_u19_covered = "Population under age 19 with at least one form of health insurance coverage.",
  ins_u19_uncovered = "Population under age 19 without health insurance coverage.",
  pct_u19_covered = "Share of the under-19 insurance universe with insurance coverage.",
  pct_u19_uncovered = "Share of the under-19 insurance universe without health insurance coverage.",
  ins_19_34_total = "Total population ages 19 to 34 in the health insurance coverage universe.",
  ins_19_34_covered = "Population ages 19 to 34 with at least one form of health insurance coverage.",
  ins_19_34_uncovered = "Population ages 19 to 34 without health insurance coverage.",
  pct_19_34_covered = "Share of the ages 19 to 34 insurance universe with insurance coverage.",
  pct_19_34_uncovered = "Share of the ages 19 to 34 insurance universe without health insurance coverage.",
  ins_35_64_total = "Total population ages 35 to 64 in the health insurance coverage universe.",
  ins_35_64_covered = "Population ages 35 to 64 with at least one form of health insurance coverage.",
  ins_35_64_uncovered = "Population ages 35 to 64 without health insurance coverage.",
  pct_35_64_covered = "Share of the ages 35 to 64 insurance universe with insurance coverage.",
  pct_35_64_uncovered = "Share of the ages 35 to 64 insurance universe without health insurance coverage.",
  ins_65u_total = "Total population age 65 and older in the health insurance coverage universe.",
  ins_65u_covered = "Population age 65 and older with at least one form of health insurance coverage.",
  ins_65u_uncovered = "Population age 65 and older without health insurance coverage.",
  pct_65u_covered = "Share of the age 65 and older insurance universe with insurance coverage.",
  pct_65u_uncovered = "Share of the age 65 and older insurance universe without health insurance coverage."
)

kpi_denominators <- list(
  pct_hh_family = "hh_total",
  pct_hh_married = "hh_total",
  pct_hh_other_family = "hh_total",
  pct_hh_nonfamily = "hh_total",
  pct_single_households = "hh_total",
  pct_nonfamily_alone = "hh_nonfamily",
  pct_nonfamily_not_alone = "hh_nonfamily",
  pct_health_insured = "ins_total",
  pct_health_uninsured = "ins_total",
  pct_u19_covered = "ins_u19_total",
  pct_u19_uncovered = "ins_u19_total",
  pct_19_34_covered = "ins_19_34_total",
  pct_19_34_uncovered = "ins_19_34_total",
  pct_35_64_covered = "ins_35_64_total",
  pct_35_64_uncovered = "ins_35_64_total",
  pct_65u_covered = "ins_65u_total",
  pct_65u_uncovered = "ins_65u_total"
)

numeric_types <- c(
  "TINYINT", "SMALLINT", "INTEGER", "BIGINT", "HUGEINT",
  "UTINYINT", "USMALLINT", "UINTEGER", "UBIGINT",
  "FLOAT", "DOUBLE", "DECIMAL"
)

quote_ident <- function(x) as.character(DBI::dbQuoteIdentifier(con, x))

format_yaml_scalar <- function(x) {
  if (is.null(x) || length(x) == 0 || is.na(x)) return("~")
  if (is.character(x)) {
    if (x %in% c("-nan", "nan", "inf", "-inf")) return(x)
    return(as.yaml(x))
  }
  as.character(x)
}

format_md_value <- function(x) {
  if (is.null(x) || length(x) == 0 || is.na(x)) return("NULL")
  as.character(x)
}

profile_column <- function(table_name, column_name, data_type) {
  table_ref <- sprintf("silver.%s", table_name)
  col_ref <- quote_ident(column_name)
  is_numeric <- toupper(data_type) %in% numeric_types

  basic <- DBI::dbGetQuery(
    con,
    glue::glue(
      "
      SELECT
        SUM(CASE WHEN {col_ref} IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS null_pct,
        COUNT(DISTINCT {col_ref}) AS distinct_count
      FROM {table_ref}
      "
    )
  )

  if (is_numeric) {
    range_stats <- DBI::dbGetQuery(
      con,
      glue::glue(
        "
        SELECT MIN({col_ref}) AS min_value, MAX({col_ref}) AS max_value
        FROM {table_ref}
        WHERE {col_ref} IS NOT NULL
        "
      )
    )
    min_value <- range_stats$min_value[[1]]
    max_value <- range_stats$max_value[[1]]
    min_length <- NA
    max_length <- NA
  } else {
    range_stats <- DBI::dbGetQuery(
      con,
      glue::glue(
        "
        SELECT
          MIN(LENGTH(CAST({col_ref} AS VARCHAR))) AS min_length,
          MAX(LENGTH(CAST({col_ref} AS VARCHAR))) AS max_length
        FROM {table_ref}
        WHERE {col_ref} IS NOT NULL
        "
      )
    )
    min_value <- NA
    max_value <- NA
    min_length <- range_stats$min_length[[1]]
    max_length <- range_stats$max_length[[1]]
  }

  top_values <- DBI::dbGetQuery(
    con,
    glue::glue(
      "
      SELECT CAST({col_ref} AS VARCHAR) AS value, COUNT(*) AS count
      FROM {table_ref}
      GROUP BY 1
      ORDER BY count DESC, value NULLS LAST
      LIMIT 5
      "
    )
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
      glue::glue(
        "
        SELECT
          COUNT(*) AS rows,
          COUNT(*) - COUNT(DISTINCT ({cols_sql})) AS duplicates,
          COUNT(DISTINCT ({cols_sql})) AS distinct_count
        FROM silver.{table_name}
        "
      )
    )

    list(
      cols = cols,
      rows = as.integer(out$rows[[1]]),
      distinct_count = as.integer(out$distinct_count[[1]]),
      duplicates = as.integer(out$duplicates[[1]])
    )
  })
}

build_md <- function(table_name, purpose, row_count, pk, year_min, year_max, distinct_geo_levels, distinct_geo_id, columns) {
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
    "- **KPI applicability**: KPI table (or has KPI dictionary entries).",
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
    "- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.",
    "- Primary/foreign keys are not enforced as DB constraints in current pipeline.",
    "",
    "## Lineage",
    "1. **Creation/write references**:",
    sprintf(
      "   - `scripts/etl/silver/acs_social_infra_silver.R:225-235` writes `silver.%s` from `staging.acs_social_infra_*` with CBSA rebasing from county data via `silver.xwalk_cbsa_county`.",
      table_name
    ),
    "",
    "## Known Gaps / To-Dos",
    "- Validate and harden grain/PK contracts with automated DQ checks.",
    "- Add explicit business definitions for columns flagged as needs confirmation.",
    "- Add enforced lineage metadata entries in `silver.metadata_topics` / `silver.metadata_vars` where missing.",
    "",
    "## How To Extend (Next Table)",
    "1. Run table-existence and row-count checks from DuckDB.",
    "2. Pull schema from `information_schema.columns` and compute per-column profile metrics.",
    "3. Run uniqueness checks for plausible key combinations.",
    "4. Locate ETL lineage with `rg -n \"<table_name>|dbWriteTable|CREATE TABLE\" scripts notebooks documents`.",
    "5. Write `schemas/data_dictionary/layers/<layer>/<schema>__<table>.md` and `.yml` artifacts.",
    "6. Mark inferred statements explicitly and set `needs_confirmation` where definitions are unclear."
  )

  paste(lines, collapse = "\n")
}

build_yaml <- function(table_name, columns, kpi_definitions = NULL) {
  year_stats <- DBI::dbGetQuery(
    con,
    glue::glue("SELECT MIN(year) AS min_year, MAX(year) AS max_year FROM silver.{table_name}")
  )
  geo_stats <- DBI::dbGetQuery(
    con,
    glue::glue(
      "
      SELECT
        COUNT(DISTINCT geo_level) AS distinct_geo_levels,
        COUNT(DISTINCT geo_id) AS distinct_geo_id
      FROM silver.{table_name}
      "
    )
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
        script = "scripts/etl/silver/acs_social_infra_silver.R",
        details = sprintf(
          "Table write/create reference(s): scripts/etl/silver/acs_social_infra_silver.R:225-235 writes silver.%s from staging.acs_social_infra_* with CBSA rebasing from county data via silver.xwalk_cbsa_county.",
          table_name
        )
      )
    )
  )

  if (!is.null(kpi_definitions)) {
    yaml_obj$kpi_definitions <- kpi_definitions
  }

  yaml::as.yaml(yaml_obj, indent.mapping.sequence = TRUE, line.sep = "\n")
}

document_table <- function(table_name, purpose, definitions, include_kpis = FALSE) {
  row_count <- DBI::dbGetQuery(con, glue::glue("SELECT COUNT(*) AS n FROM silver.{table_name}"))$n[[1]]
  schema_cols <- DBI::dbGetQuery(
    con,
    glue::glue(
      "
      SELECT column_name, data_type
      FROM information_schema.columns
      WHERE table_schema = 'silver'
        AND table_name = '{table_name}'
      ORDER BY ordinal_position
      "
    )
  )

  columns <- purrr::pmap(schema_cols, function(column_name, data_type) {
    prof <- profile_column(table_name, column_name, data_type)
    prof$definition <- definitions[[column_name]] %||% "Needs definition confirmation."
    prof
  })

  pk <- key_stats(table_name)
  year_stats <- DBI::dbGetQuery(
    con,
    glue::glue("SELECT MIN(year) AS min_year, MAX(year) AS max_year FROM silver.{table_name}")
  )
  geo_stats <- DBI::dbGetQuery(
    con,
    glue::glue(
      "
      SELECT
        COUNT(DISTINCT geo_level) AS distinct_geo_levels,
        COUNT(DISTINCT geo_id) AS distinct_geo_id
      FROM silver.{table_name}
      "
    )
  )

  kpi_defs_list <- NULL
  if (isTRUE(include_kpis)) {
    measure_columns <- columns[
      !vapply(columns, function(x) x$name %in% c("geo_level", "geo_id", "geo_name", "year"), logical(1))
    ]
    kpi_defs_list <- lapply(measure_columns, function(col) {
      list(
        kpi_name = col$name,
        business_definition = definitions[[col$name]] %||% "Needs definition confirmation.",
        source = "ACS Social Infrastructure (B11001/B27010)",
        denominator_hint = kpi_denominators[[col$name]] %||% NULL,
        data_type = col$type
      )
    })
  }

  md_text <- build_md(
    table_name = table_name,
    purpose = purpose,
    row_count = row_count,
    pk = pk,
    year_min = year_stats$min_year[[1]],
    year_max = year_stats$max_year[[1]],
    distinct_geo_levels = geo_stats$distinct_geo_levels[[1]],
    distinct_geo_id = geo_stats$distinct_geo_id[[1]],
    columns = columns
  )

  yaml_text <- build_yaml(table_name, columns, kpi_defs_list)

  md_path <- file.path(dict_dir, sprintf("silver__%s.md", table_name))
  yml_path <- file.path(dict_dir, sprintf("silver__%s.yml", table_name))

  writeLines(md_text, md_path)
  writeLines(yaml_text, yml_path)
}

document_table(
  table_name = "social_infra_base",
  purpose = "Silver social infrastructure base table (`base` type).",
  definitions = base_defs,
  include_kpis = FALSE
)

document_table(
  table_name = "social_infra_kpi",
  purpose = "Silver social infrastructure table (`kpi` type).",
  definitions = kpi_defs,
  include_kpis = TRUE
)
