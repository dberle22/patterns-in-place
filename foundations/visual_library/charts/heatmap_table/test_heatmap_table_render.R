# Heatmap table render tests with question-specific DuckDB queries.

if (file.exists(".Renviron")) readRenviron(".Renviron")

source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_heatmap_table.R")
source("visual_library/shared/render/render_heatmap_table.R")

run_heatmap_table_query <- function(con, sql_path) {
  sql <- read_sql_file(sql_path)
  DBI::dbGetQuery(con, sql)
}

filter_display_rows <- function(data) {
  if (!"display_flag" %in% names(data)) {
    return(data)
  }
  data[data$display_flag %in% TRUE, , drop = FALSE]
}

assert_heatmap_table_contract <- function(data, question_id) {
  validation <- validate_heatmap_table_contract(data)
  if (isTRUE(validation$pass)) {
    return(invisible(validation))
  }

  stop(
    sprintf(
      "Heatmap table contract validation failed for %s. Missing required: %s. Rows: %s",
      question_id,
      paste(validation$missing_required, collapse = ", "),
      validation$rows
    )
  )
}

save_heatmap_table_plot <- function(plot, output_dir, filename, width = 11, height = 8) {
  path <- file.path(output_dir, filename)
  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 300, bg = "white")
  path
}

write_heatmap_table_review <- function(output_dir, outputs) {
  review_path <- file.path(output_dir, "test_heatmap_table_business_questions.md")
  lines <- c(
    "# Heatmap Table Testing",
    "",
    "## Canonical Questions",
    "1. Across the tract shortlist, which places are consistently strong across income, talent, housing headroom, and affordability guardrails?",
    "2. For counties in the target CBSA, which dimensions are strongest versus weakest?",
    "3. For selected peer CBSAs, what does the full KPI profile look like in one scannable matrix?",
    "4. For rent burden, which ZCTAs show persistent stress across years?",
    "5. Which metrics improved most in the target CBSA from 2013 to 2023?",
    "",
    "## Output Files",
    paste0("- `heatmap_shortlist_scan`: ", outputs[["heatmap_shortlist_scan"]]),
    paste0("- `heatmap_county_dimension_compare`: ", outputs[["heatmap_county_dimension_compare"]]),
    paste0("- `heatmap_peer_cbsa_profile`: ", outputs[["heatmap_peer_cbsa_profile"]]),
    paste0("- `heatmap_zcta_persistent_stress`: ", outputs[["heatmap_zcta_persistent_stress"]]),
    paste0("- `heatmap_target_metric_improvement`: ", outputs[["heatmap_target_metric_improvement"]]),
    "",
    "## QA Notes",
    "- Shared prep keeps raw `metric_value` for labels and uses `normalized_value`/`fill_value` for color.",
    "- Multi-metric samples apply percentile normalization within each metric and time window, with lower-is-better metrics inverted before coloring.",
    "- Missing matrix cells are completed by prep and labeled as `No data` instead of being silently dropped.",
    "- The first PNG set is intentionally chart-local; no broad shared-standard changes were made."
  )
  writeLines(lines, review_path)
  review_path
}

run_heatmap_table_tests <- function() {
  output_dir <- "visual_library/charts/heatmap_table/sample_output"
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  con <- connect_metro_duckdb(read_only = TRUE)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  outputs <- c()

  q1_path <- "visual_library/charts/heatmap_table/sample_sql/q1_heatmap_shortlist_scan.sql"
  q1_raw <- run_heatmap_table_query(con, q1_path)
  assert_heatmap_table_contract(q1_raw, "heatmap_shortlist_scan")
  q1_prepped <- prep_heatmap_table(q1_raw, config = list(question_id = "heatmap_shortlist_scan"))
  q1_display <- filter_display_rows(q1_prepped)
  q1_plot <- render_heatmap_table(
    q1_display,
    config = list(
      output_mode = "presentation",
      title = "Wilmington tract shortlist guardrail scan",
      subtitle = "Top 25 tracts in the Wilmington, NC CBSA | Fill is percentile within all target-CBSA tracts after lower-is-better polarity alignment",
      caption_side_note = "Rows are ordered by mean normalized score across the guardrail set; darker green means stronger relative standing."
    )
  )
  outputs["heatmap_shortlist_scan"] <- save_heatmap_table_plot(
    q1_plot,
    output_dir,
    "heatmap_table_q1_shortlist_scan.png",
    width = 11.5,
    height = 10
  )

  q2_path <- "visual_library/charts/heatmap_table/sample_sql/q2_heatmap_county_dimension_compare.sql"
  q2_raw <- run_heatmap_table_query(con, q2_path)
  assert_heatmap_table_contract(q2_raw, "heatmap_county_dimension_compare")
  q2_prepped <- prep_heatmap_table(q2_raw, config = list(question_id = "heatmap_county_dimension_compare"))
  q2_display <- filter_display_rows(q2_prepped)
  q2_plot <- render_heatmap_table(
    q2_display,
    config = list(
      output_mode = "presentation",
      title = "Wilmington-area county dimension comparison",
      subtitle = "Latest common year | Fill is percentile versus South Atlantic counties after polarity alignment | Cell labels show raw metric values",
      caption_side_note = "The county view is compact by design: use it to scan each county profile across the same KPI dimensions."
    )
  )
  outputs["heatmap_county_dimension_compare"] <- save_heatmap_table_plot(
    q2_plot,
    output_dir,
    "heatmap_table_q2_county_dimension_compare.png",
    width = 10.5,
    height = 6.5
  )

  q3_path <- "visual_library/charts/heatmap_table/sample_sql/q3_heatmap_peer_cbsa_profile.sql"
  q3_raw <- run_heatmap_table_query(con, q3_path)
  assert_heatmap_table_contract(q3_raw, "heatmap_peer_cbsa_profile")
  q3_prepped <- prep_heatmap_table(q3_raw, config = list(question_id = "heatmap_peer_cbsa_profile"))
  q3_display <- filter_display_rows(q3_prepped)
  q3_plot <- render_heatmap_table(
    q3_display,
    config = list(
      output_mode = "presentation",
      title = "Wilmington, NC peer CBSA KPI profile",
      subtitle = "Wilmington plus closest South Atlantic population peers | Fill is percentile versus all CBSAs after polarity alignment | Highlight border marks the target CBSA",
      caption_side_note = "This table-first heatmap favors readable row and column labels over maximum tile count."
    )
  )
  outputs["heatmap_peer_cbsa_profile"] <- save_heatmap_table_plot(
    q3_plot,
    output_dir,
    "heatmap_table_q3_peer_cbsa_profile.png",
    width = 13,
    height = 7.8
  )

  q4_path <- "visual_library/charts/heatmap_table/sample_sql/q4_heatmap_zcta_persistent_stress.sql"
  q4_raw <- run_heatmap_table_query(con, q4_path)
  assert_heatmap_table_contract(q4_raw, "heatmap_zcta_persistent_stress")
  q4_prepped <- prep_heatmap_table(
    q4_raw,
    config = list(
      question_id = "heatmap_zcta_persistent_stress",
      variant = "geo_period",
      label_value_field = "metric_value",
      sort_rows = "mean_normalized_desc"
    )
  )
  q4_display <- filter_display_rows(q4_prepped)
  q4_plot <- render_heatmap_table(
    q4_display,
    config = list(
      output_mode = "presentation",
      legend_title = "Stress percentile",
      title = "Which Wilmington-area ZCTAs show persistent rent-burden stress?",
      subtitle = "2015-2023 | Fill is percentile within each year; higher values mean more rent-burden stress, not better performance",
      caption_side_note = "Rows are the highest average-stress ZCTAs with enough observed years. No data cells indicate unavailable annual estimates."
    )
  )
  outputs["heatmap_zcta_persistent_stress"] <- save_heatmap_table_plot(
    q4_plot,
    output_dir,
    "heatmap_table_q4_zcta_persistent_stress.png",
    width = 12,
    height = 9
  )

  q5_path <- "visual_library/charts/heatmap_table/sample_sql/q5_heatmap_target_metric_improvement.sql"
  q5_raw <- run_heatmap_table_query(con, q5_path)
  assert_heatmap_table_contract(q5_raw, "heatmap_target_metric_improvement")
  q5_prepped <- prep_heatmap_table(
    q5_raw,
    config = list(
      question_id = "heatmap_target_metric_improvement",
      variant = "metric_period"
    )
  )
  q5_plot <- render_heatmap_table(
    q5_prepped,
    config = list(
      output_mode = "presentation",
      title = "Which Wilmington metrics improved most over time?",
      subtitle = "2013-2023 target CBSA history | Fill is normalized within each metric after directionality alignment, so higher color means a stronger year for that metric | Cell labels show raw values",
      caption_side_note = "Rows are ordered by directional improvement from first to last available year."
    )
  )
  outputs["heatmap_target_metric_improvement"] <- save_heatmap_table_plot(
    q5_plot,
    output_dir,
    "heatmap_table_q5_target_metric_improvement.png",
    width = 13,
    height = 8
  )

  outputs["review_markdown"] <- write_heatmap_table_review(output_dir, outputs)
  outputs
}

outputs <- run_heatmap_table_tests()
print(outputs)
