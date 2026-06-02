# Line chart render tests with question-specific DuckDB queries.

if (file.exists(".Renviron")) readRenviron(".Renviron")

source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_line.R")
source("visual_library/shared/render/render_line.R")

sql_string <- function(con, value) {
  as.character(DBI::dbQuoteString(con, value))
}

run_line_query <- function(con, sql) {
  DBI::dbGetQuery(con, sql)
}

assert_line_contract <- function(data, question_id) {
  validation <- validate_line_contract(data)
  if (isTRUE(validation$pass)) {
    return(invisible(validation))
  }

  stop(
    sprintf(
      "Line contract validation failed for %s. Missing required: %s. Rows: %s",
      question_id,
      paste(validation$missing_required, collapse = ", "),
      validation$rows
    )
  )
}

line_sql_single_population <- function(con) {
  target_geo_id <- sql_string(con, "48900")
  vintage <- sql_string(con, format(Sys.Date(), "%Y-%m-%d"))

  paste(
    "SELECT",
    "  'line_test_single' AS question_id,",
    "  p.geo_level,",
    "  p.geo_id,",
    "  p.geo_name,",
    "  p.year AS period,",
    "  'level' AS time_window,",
    "  'pop_total' AS metric_id,",
    "  'Population' AS metric_label,",
    "  p.pop_total::DOUBLE AS metric_value,",
    "  'gold.population_demographics' AS source,",
    paste0("  ", vintage, " AS vintage,"),
    "  NULL::VARCHAR AS \"group\",",
    "  TRUE AS highlight_flag,",
    "  NULL::DOUBLE AS benchmark_value,",
    "  NULL::INTEGER AS index_base_period,",
    "  NULL::VARCHAR AS note",
    "FROM metro_deep_dive.gold.population_demographics p",
    "WHERE p.geo_level = 'cbsa'",
    paste0("  AND p.geo_id = ", target_geo_id),
    "  AND p.year BETWEEN 2013 AND 2023",
    "  AND p.pop_total IS NOT NULL",
    "ORDER BY p.year",
    collapse = "\n"
  )
}

line_sql_multi_income_peers <- function(con) {
  target_geo_id <- sql_string(con, "48900")
  vintage <- sql_string(con, format(Sys.Date(), "%Y-%m-%d"))

  paste(
    "WITH selected_geos AS (",
    paste0("  SELECT ", target_geo_id, " AS geo_id, TRUE AS highlight_flag UNION ALL"),
    "  SELECT '16740' AS geo_id, FALSE AS highlight_flag UNION ALL",
    "  SELECT '39580' AS geo_id, FALSE AS highlight_flag",
    "),",
    "division_lookup AS (",
    "  SELECT",
    "    x.cbsa_code AS geo_id,",
    "    MIN(s.census_division) AS census_division",
    "  FROM metro_deep_dive.silver.xwalk_cbsa_county x",
    "  LEFT JOIN metro_deep_dive.silver.xwalk_state_region s",
    "    ON x.state_fips = s.state_fips",
    "  GROUP BY 1",
    ")",
    "SELECT",
    "  'line_test_multi' AS question_id,",
    "  i.geo_level,",
    "  i.geo_id,",
    "  i.geo_name,",
    "  i.year AS period,",
    "  'level' AS time_window,",
    "  'calc_income_pc' AS metric_id,",
    "  'Per capita income' AS metric_label,",
    "  i.calc_income_pc::DOUBLE AS metric_value,",
    "  'gold.economics_income_wide' AS source,",
    paste0("  ", vintage, " AS vintage,"),
    "  d.census_division AS \"group\",",
    "  g.highlight_flag,",
    "  NULL::DOUBLE AS benchmark_value,",
    "  NULL::INTEGER AS index_base_period,",
    "  NULL::VARCHAR AS note",
    "FROM metro_deep_dive.gold.economics_income_wide i",
    "JOIN selected_geos g",
    "  ON i.geo_id = g.geo_id",
    "LEFT JOIN division_lookup d",
    "  ON i.geo_id = d.geo_id",
    "WHERE i.geo_level = 'cbsa'",
    "  AND i.year BETWEEN 2013 AND 2023",
    "  AND i.calc_income_pc IS NOT NULL",
    "ORDER BY i.geo_id, i.year",
    collapse = "\n"
  )
}

line_sql_indexed_income_peers <- function(con) {
  target_geo_id <- sql_string(con, "48900")
  vintage <- sql_string(con, format(Sys.Date(), "%Y-%m-%d"))

  paste(
    "WITH selected_geos AS (",
    paste0("  SELECT ", target_geo_id, " AS geo_id, TRUE AS highlight_flag UNION ALL"),
    "  SELECT '16740' AS geo_id, FALSE AS highlight_flag UNION ALL",
    "  SELECT '39580' AS geo_id, FALSE AS highlight_flag",
    "),",
    "division_lookup AS (",
    "  SELECT",
    "    x.cbsa_code AS geo_id,",
    "    MIN(s.census_division) AS census_division",
    "  FROM metro_deep_dive.silver.xwalk_cbsa_county x",
    "  LEFT JOIN metro_deep_dive.silver.xwalk_state_region s",
    "    ON x.state_fips = s.state_fips",
    "  GROUP BY 1",
    ")",
    "SELECT",
    "  'line_test_indexed' AS question_id,",
    "  i.geo_level,",
    "  i.geo_id,",
    "  i.geo_name,",
    "  i.year AS period,",
    "  'indexed' AS time_window,",
    "  'calc_income_pc' AS metric_id,",
    "  'Per capita income' AS metric_label,",
    "  i.calc_income_pc::DOUBLE AS metric_value,",
    "  'gold.economics_income_wide' AS source,",
    paste0("  ", vintage, " AS vintage,"),
    "  d.census_division AS \"group\",",
    "  g.highlight_flag,",
    "  NULL::DOUBLE AS benchmark_value,",
    "  2013::INTEGER AS index_base_period,",
    "  NULL::VARCHAR AS note",
    "FROM metro_deep_dive.gold.economics_income_wide i",
    "JOIN selected_geos g",
    "  ON i.geo_id = g.geo_id",
    "LEFT JOIN division_lookup d",
    "  ON i.geo_id = d.geo_id",
    "WHERE i.geo_level = 'cbsa'",
    "  AND i.year BETWEEN 2013 AND 2023",
    "  AND i.calc_income_pc IS NOT NULL",
    "ORDER BY i.geo_id, i.year",
    collapse = "\n"
  )
}

save_line_plot <- function(plot, output_dir, filename, width, height) {
  path <- file.path(output_dir, filename)
  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 300, bg = "white")
  path
}

run_line_tests <- function() {
  output_dir <- "visual_library/charts/line/sample_output"
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  con <- connect_metro_duckdb(read_only = TRUE)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  outputs <- c()

  sql_single <- line_sql_single_population(con)
  raw_single <- run_line_query(con, sql_single)
  assert_line_contract(raw_single, "line_test_single")
  single_df <- prep_line(
    raw_single,
    config = list(
      question_id = "line_test_single",
      metric_id = "pop_total",
      variant = "single",
      geo_ids = "48900",
      period_min = 2013,
      period_max = 2023
    )
  )
  single_plot <- render_line(
    single_df,
    config = list(
      output_mode = "presentation",
      title = "Did Wilmington's population growth accelerate after 2018?",
      subtitle = "2013-2023 annual CBSA population | Wilmington, NC metro only",
      y_label = "Population",
      label_style = "integer",
      legend_position = "none",
      caption_side_note = "Use the line slope to assess whether the metro's growth rate steepened after 2018."
    )
  )
  outputs["line_test_single"] <- save_line_plot(
    single_plot,
    output_dir,
    "line_test_single.png",
    width = 11,
    height = 7
  )

  sql_multi <- line_sql_multi_income_peers(con)
  raw_multi <- run_line_query(con, sql_multi)
  assert_line_contract(raw_multi, "line_test_multi")
  multi_df <- prep_line(
    raw_multi,
    config = list(
      question_id = "line_test_multi",
      metric_id = "calc_income_pc",
      variant = "multi",
      geo_ids = c("48900", "16740", "39580"),
      period_min = 2013,
      period_max = 2023
    )
  )
  multi_plot <- render_line(
    multi_df,
    config = list(
      output_mode = "presentation",
      title = "How has Wilmington's per-capita income changed versus Raleigh and Charlotte?",
      subtitle = "2013-2023 annual CBSA series | Wilmington highlighted against North Carolina peers",
      y_label = "Per-capita income ($)",
      label_style = "dollar",
      label_accuracy = 1,
      caption_side_note = "Level comparison shows both absolute income gaps and the pace of recent gains."
    )
  )
  outputs["line_test_multi"] <- save_line_plot(
    multi_plot,
    output_dir,
    "line_test_multi.png",
    width = 11,
    height = 7
  )

  sql_indexed <- line_sql_indexed_income_peers(con)
  raw_indexed <- run_line_query(con, sql_indexed)
  assert_line_contract(raw_indexed, "line_test_indexed")
  indexed_df <- prep_line(
    raw_indexed,
    config = list(
      question_id = "line_test_indexed",
      metric_id = "calc_income_pc",
      variant = "indexed",
      geo_ids = c("48900", "16740", "39580"),
      period_min = 2013,
      period_max = 2023,
      base_period = 2013
    )
  )
  indexed_plot <- render_line(
    indexed_df,
    config = list(
      output_mode = "presentation",
      title = "Are Wilmington's income gains keeping pace with Raleigh and Charlotte?",
      subtitle = "2013-2023 annual CBSA series | Indexed so each metro starts at 2013 = 100",
      y_label = "Per-capita income index (2013 = 100)",
      label_style = "number",
      label_accuracy = 1,
      caption_side_note = "Indexed comparison removes starting-level differences so the chart emphasizes relative growth trajectories."
    )
  )
  outputs["line_test_indexed"] <- save_line_plot(
    indexed_plot,
    output_dir,
    "line_test_indexed.png",
    width = 11,
    height = 7
  )

  outputs
}

outputs <- run_line_tests()
print(outputs)
