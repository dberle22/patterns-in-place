# Strength strip chart render tests with question-specific DuckDB queries.

if (file.exists(".Renviron")) readRenviron(".Renviron")

source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_strength_strip.R")
source("visual_library/shared/render/render_strength_strip.R")

run_strength_strip_query <- function(con, sql_path) {
  sql <- read_sql_file(sql_path)
  DBI::dbGetQuery(con, sql)
}

filter_target_geo <- function(data, target_geo_id = "48900") {
  data[data$geo_id == target_geo_id, , drop = FALSE]
}

filter_display_rows <- function(data) {
  if (!"display_flag" %in% names(data)) {
    return(data)
  }
  data[data$display_flag %in% TRUE, , drop = FALSE]
}

assert_strength_strip_contract <- function(data, question_id) {
  validation <- validate_strength_strip_contract(data)
  if (isTRUE(validation$pass)) {
    return(invisible(validation))
  }

  stop(
    sprintf(
      "Strength strip contract validation failed for %s. Missing required: %s. Rows: %s",
      question_id,
      paste(validation$missing_required, collapse = ", "),
      validation$rows
    )
  )
}

save_strength_strip_plot <- function(plot, output_dir, filename, width = 10, height = 7.5) {
  path <- file.path(output_dir, filename)
  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 300, bg = "white")
  path
}

write_strength_strip_review <- function(output_dir, outputs) {
  review_path <- file.path(output_dir, "test_strength_strip_business_questions.md")
  lines <- c(
    "# Strength Strip Testing",
    "",
    "## Canonical Questions",
    "1. What is Wilmington, NC's KPI profile versus the national CBSA universe?",
    "2. Which KPI dimensions are strengths or weaknesses versus nearby South Atlantic peers when benchmarked against the full South Atlantic CBSA universe?",
    "3. Which KPIs are dragging down the target versus the national CBSA median?",
    "4. How does Wilmington's profile differ between 2023 levels and 2018-2023 growth windows?",
    "5. Which county inside the Wilmington CBSA has the strongest overall profile when benchmarked against the full South Atlantic county universe?",
    "",
    "## Output Files",
    paste0("- `strip_cbsa_profile`: ", outputs[["strip_cbsa_profile"]]),
    paste0("- `strip_target_vs_peers`: ", outputs[["strip_target_vs_peers"]]),
    paste0("- `strip_score_driver_scan`: ", outputs[["strip_score_driver_scan"]]),
    paste0("- `strip_level_vs_growth_compare`: ", outputs[["strip_level_vs_growth_compare"]]),
    paste0("- `strip_county_profile_compare`: ", outputs[["strip_county_profile_compare"]]),
    "",
    "## QA Notes",
    "- Shared prep applies percentile normalization within each metric and time window, with polarity inversion for lower-is-better KPIs.",
    "- The score-driver sample includes a benchmark tick for the national CBSA median on each KPI row.",
    "- The peer and county comparison samples normalize against broad South Atlantic universes, then display only the compact comparison sets."
  )
  writeLines(lines, review_path)
  review_path
}

run_strength_strip_tests <- function() {
  output_dir <- "visual_library/charts/strength_strip/sample_output"
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  con <- connect_metro_duckdb(read_only = TRUE)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  outputs <- c()

  q1_path <- "visual_library/charts/strength_strip/sample_sql/q1_strip_cbsa_profile.sql"
  q1_raw <- run_strength_strip_query(con, q1_path)
  assert_strength_strip_contract(q1_raw, "strip_cbsa_profile")
  q1_prepped <- prep_strength_strip(q1_raw, config = list(question_id = "strip_cbsa_profile"))
  q1_target <- filter_target_geo(q1_prepped)
  q1_plot <- render_strength_strip(
    q1_target,
    config = list(
      output_mode = "presentation",
      title = "Wilmington, NC strength strip",
      subtitle = "2023 latest common year | Percentile positions versus all CBSAs | Higher percentile means stronger relative standing after polarity alignment",
      caption_side_note = "This single-market view uses scorecard bars plus endpoints to show Wilmington's percentile standing across the canonical KPI set."
    )
  )
  outputs["strip_cbsa_profile"] <- save_strength_strip_plot(
    q1_plot,
    output_dir,
    "strength_strip_q1_cbsa_profile.png"
  )

  q2_path <- "visual_library/charts/strength_strip/sample_sql/q2_strip_target_vs_peers.sql"
  q2_raw <- run_strength_strip_query(con, q2_path)
  assert_strength_strip_contract(q2_raw, "strip_target_vs_peers")
  q2_prepped <- prep_strength_strip(q2_raw, config = list(question_id = "strip_target_vs_peers"))
  q2_display <- filter_display_rows(q2_prepped)
  q2_plot <- render_strength_strip(
    q2_display,
    config = list(
      output_mode = "presentation",
      title = "Wilmington, NC versus South Atlantic peers",
      subtitle = "2023 latest common year | Percentiles are computed against all South Atlantic CBSAs, while the plot displays Wilmington plus its three closest population peers",
      caption_side_note = "The displayed peer set stays compact, but the percentile positions come from the broader South Atlantic CBSA universe."
    )
  )
  outputs["strip_target_vs_peers"] <- save_strength_strip_plot(
    q2_plot,
    output_dir,
    "strength_strip_q2_target_vs_peers.png"
  )

  q3_path <- "visual_library/charts/strength_strip/sample_sql/q3_strip_score_driver_scan.sql"
  q3_raw <- run_strength_strip_query(con, q3_path)
  assert_strength_strip_contract(q3_raw, "strip_score_driver_scan")
  q3_prepped <- prep_strength_strip(q3_raw, config = list(question_id = "strip_score_driver_scan"))
  q3_target <- filter_target_geo(q3_prepped)
  q3_plot <- render_strength_strip(
    q3_target,
    config = list(
      output_mode = "presentation",
      title = "Which KPIs are dragging down Wilmington's profile?",
      subtitle = "2023 latest common year | Scorecard bars show Wilmington's percentile standing, with benchmark ticks at the national CBSA median",
      show_benchmark = TRUE,
      caption_side_note = "Rows where Wilmington sits well left of the median benchmark are the most plausible score drags."
    )
  )
  outputs["strip_score_driver_scan"] <- save_strength_strip_plot(
    q3_plot,
    output_dir,
    "strength_strip_q3_score_driver_scan.png"
  )

  q4_path <- "visual_library/charts/strength_strip/sample_sql/q4_strip_level_vs_growth_compare.sql"
  q4_raw <- run_strength_strip_query(con, q4_path)
  assert_strength_strip_contract(q4_raw, "strip_level_vs_growth_compare")
  q4_prepped <- prep_strength_strip(q4_raw, config = list(question_id = "strip_level_vs_growth_compare"))
  q4_target <- filter_target_geo(q4_prepped)
  q4_target$time_window <- factor(
    q4_target$time_window,
    levels = c("2023 levels", "2018-2023 growth")
  )
  q4_plot <- render_strength_strip(
    q4_target,
    config = list(
      output_mode = "presentation",
      facet_by = "time_window",
      title = "Wilmington, NC levels versus growth profile",
      subtitle = "Percentiles are computed separately within each window across all CBSAs, so the panels compare relative standing rather than raw units",
      caption_side_note = "The split panels show whether Wilmington's current level profile and recent momentum tell the same story."
    )
  )
  outputs["strip_level_vs_growth_compare"] <- save_strength_strip_plot(
    q4_plot,
    output_dir,
    "strength_strip_q4_level_vs_growth_compare.png",
    width = 10.5,
    height = 9
  )

  q5_path <- "visual_library/charts/strength_strip/sample_sql/q5_strip_county_profile_compare.sql"
  q5_raw <- run_strength_strip_query(con, q5_path)
  assert_strength_strip_contract(q5_raw, "strip_county_profile_compare")
  q5_prepped <- prep_strength_strip(q5_raw, config = list(question_id = "strip_county_profile_compare"))
  q5_display <- filter_display_rows(q5_prepped)
  county_scores <- stats::aggregate(
    normalized_value ~ geo_name,
    data = q5_display,
    FUN = function(x) mean(x, na.rm = TRUE)
  )
  strongest_county <- as.character(county_scores$geo_name[which.max(county_scores$normalized_value)])
  q5_display$highlight_flag <- as.character(q5_display$geo_name) == strongest_county
  q5_plot <- render_strength_strip(
    q5_display,
    config = list(
      output_mode = "presentation",
      title = "Which Wilmington-area county has the strongest profile?",
      subtitle = "2023 latest common year | Percentiles are computed against all South Atlantic counties, while the plot displays the three counties in the Wilmington, NC CBSA",
      caption_side_note = paste("Highlighted county has the highest mean normalized score across the canonical KPI set:", strongest_county)
    )
  )
  outputs["strip_county_profile_compare"] <- save_strength_strip_plot(
    q5_plot,
    output_dir,
    "strength_strip_q5_county_profile_compare.png"
  )

  outputs["review_markdown"] <- write_strength_strip_review(output_dir, outputs)
  outputs
}

outputs <- run_strength_strip_tests()
print(outputs)
