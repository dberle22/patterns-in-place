# Bump chart render tests with question-specific DuckDB queries.

if (file.exists(".Renviron")) readRenviron(".Renviron")

source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_bump_chart.R")
source("visual_library/shared/render/render_bump_chart.R")

run_bump_chart_query <- function(con, sql_path) {
  DBI::dbGetQuery(con, read_sql_file(sql_path))
}

assert_bump_chart_contract <- function(data, question_id) {
  validation <- validate_bump_chart_contract(data, require_single_geo_level = TRUE)
  metric_count <- length(unique(stats::na.omit(data$metric_id)))
  period_count <- length(unique(stats::na.omit(data$period)))

  if (isTRUE(validation$pass) && metric_count == 1 && period_count >= 3) {
    return(invisible(validation))
  }

  stop(
    sprintf(
      "Bump chart contract validation failed for %s. Missing required: %s. Rows: %s. Metric count: %s. Period count: %s",
      question_id,
      paste(validation$missing_required, collapse = ", "),
      validation$rows,
      metric_count,
      period_count
    )
  )
}

assert_bump_rank_direction <- function(data, question_id) {
  if (!all(is.finite(data$rank))) {
    stop(sprintf("Bump chart rank validation failed for %s: non-finite ranks found after prep.", question_id))
  }

  best_rows <- stats::aggregate(rank ~ period, data = data, FUN = min)
  if (!all(best_rows$rank >= 1)) {
    stop(sprintf("Bump chart rank validation failed for %s: ranks must start at 1 or greater.", question_id))
  }

  invisible(TRUE)
}

save_bump_chart_plot <- function(plot, output_dir, filename, width = 12, height = 8) {
  path <- file.path(output_dir, filename)
  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 300, bg = "white")
  path
}

write_bump_chart_review <- function(output_dir, outputs) {
  review_path <- file.path(output_dir, "test_bump_chart_business_questions.md")
  lines <- c(
    "# Bump Chart Testing",
    "",
    "## Canonical Questions",
    "1. Which CBSAs moved into the top 10 for 5-year population growth?",
    "2. Did the target CBSA improve in affordability rank since 2018?",
    "3. Are the top performers stable or rotating?",
    "4. Which counties within the CBSA rose fastest in rent-burden rank?",
    "5. How did Sweet Spot markets shift in overheating risk rank over time?",
    "",
    "## Output Files",
    paste0("- `bump_top10_growth`: ", outputs[["bump_top10_growth"]]),
    paste0("- `bump_target_affordability_rank`: ", outputs[["bump_target_affordability_rank"]]),
    paste0("- `bump_top_performer_stability`: ", outputs[["bump_top_performer_stability"]]),
    paste0("- `bump_county_rent_burden_rank`: ", outputs[["bump_county_rent_burden_rank"]]),
    paste0("- `bump_sweet_spot_overheating`: ", outputs[["bump_sweet_spot_overheating"]]),
    "",
    "## QA Notes",
    "- Shared prep preserves raw `metric_value` and uses `rank` as the plotted value.",
    "- Rank 1 is plotted at the top; upward movement means moving toward rank 1.",
    "- Derived ranks use deterministic row-number ties: metric value, then geography name, then geography id.",
    "- Fixed top-N samples compute ranks on the full query universe before trimming to the display set.",
    "- The first PNG set is chart-local; no broad shared-standard changes were made."
  )
  writeLines(lines, review_path)
  review_path
}

run_bump_chart_tests <- function() {
  chart_dir <- "visual_library/charts/bump_chart"
  sql_dir <- file.path(chart_dir, "sample_sql")
  output_dir <- file.path(chart_dir, "sample_output")
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  con <- connect_metro_duckdb(read_only = TRUE)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  outputs <- c()

  # Question 1: Which CBSAs moved into the top 10 for 5-year population growth?
  growth_raw <- run_bump_chart_query(con, file.path(sql_dir, "bump_top10_growth.sql"))
  assert_bump_chart_contract(growth_raw, "bump_top10_growth")
  growth_df <- prep_bump_chart(
    growth_raw,
    config = list(
      question_id = "bump_top10_growth",
      metric_id = "pop_growth_5yr",
      entity_strategy = "fixed_top_n",
      selection_period_role = "end",
      top_n = 10,
      use_precomputed_rank = FALSE,
      rank_method = "row_number",
      metric_higher_is_better = TRUE,
      include_highlighted = FALSE
    )
  )
  assert_bump_rank_direction(growth_df, "bump_top10_growth")
  growth_plot <- render_bump_chart(
    growth_df,
    config = list(
      output_mode = "presentation",
      title = "Which CBSAs moved into the top 10 for population growth?",
      subtitle = "2018-2024 annual rank | Fixed set selected from 2024 top 10 | Universe: all CBSAs",
      label_mode = "top_n",
      label_top_n = 6,
      label_style = "percent",
      label_accuracy = 0.1,
      rank_band_n = 10,
      caption_side_note = "Ranks use 5-year population growth; ties are broken by geography name and id."
    )
  )
  outputs["bump_top10_growth"] <- save_bump_chart_plot(
    growth_plot,
    output_dir,
    "bump_top10_growth.png",
    width = 12.5,
    height = 8
  )

  # Question 2: Did the target CBSA improve in affordability rank since 2018?
  affordability_raw <- run_bump_chart_query(con, file.path(sql_dir, "bump_target_affordability_rank.sql"))
  assert_bump_chart_contract(affordability_raw, "bump_target_affordability_rank")
  affordability_df <- prep_bump_chart(
    affordability_raw,
    config = list(
      question_id = "bump_target_affordability_rank",
      metric_id = "value_to_income",
      entity_strategy = "peer_set",
      use_precomputed_rank = TRUE,
      include_highlighted = TRUE
    )
  )
  assert_bump_rank_direction(affordability_df, "bump_target_affordability_rank")
  affordability_plot <- render_bump_chart(
    affordability_df,
    config = list(
      output_mode = "presentation",
      title = "Did Wilmington improve in affordability rank?",
      subtitle = "2018-2024 selected peer CBSAs | Rank 1 has the lowest home value-to-income ratio",
      label_mode = "highlight",
      label_style = "number",
      label_accuracy = 0.1,
      rank_band_n = 3,
      caption_side_note = "Peer set is fixed across all years; endpoint label shows Wilmington's latest rank and rank change."
    )
  )
  outputs["bump_target_affordability_rank"] <- save_bump_chart_plot(
    affordability_plot,
    output_dir,
    "bump_target_affordability_rank.png",
    width = 11.5,
    height = 7
  )

  # Question 3: Are top performers stable or rotating?
  stability_raw <- run_bump_chart_query(con, file.path(sql_dir, "bump_top_performer_stability.sql"))
  assert_bump_chart_contract(stability_raw, "bump_top_performer_stability")
  stability_df <- prep_bump_chart(
    stability_raw,
    config = list(
      question_id = "bump_top_performer_stability",
      metric_id = "income_pc_growth_5yr",
      entity_strategy = "fixed_top_n",
      selection_period_role = "end",
      top_n = 15,
      use_precomputed_rank = FALSE,
      rank_method = "row_number",
      metric_higher_is_better = TRUE,
      include_highlighted = FALSE
    )
  )
  assert_bump_rank_direction(stability_df, "bump_top_performer_stability")
  stability_plot <- render_bump_chart(
    stability_df,
    config = list(
      output_mode = "presentation",
      title = "Are top income-growth performers stable or rotating?",
      subtitle = "2018-2024 annual CBSA rank | Fixed set selected from 2024 top 15 | Universe: all CBSAs",
      label_mode = "top_n",
      label_top_n = 8,
      label_style = "percent",
      label_accuracy = 0.1,
      rank_band_n = 15,
      comparison_alpha = 0.58,
      caption_side_note = "Crossing lines show churn in the latest-year top-performer set."
    )
  )
  outputs["bump_top_performer_stability"] <- save_bump_chart_plot(
    stability_plot,
    output_dir,
    "bump_top_performer_stability.png",
    width = 13,
    height = 8.5
  )

  # Question 4: Which counties within the CBSA rose fastest in rent-burden rank?
  county_raw <- run_bump_chart_query(con, file.path(sql_dir, "bump_county_rent_burden_rank.sql"))
  assert_bump_chart_contract(county_raw, "bump_county_rent_burden_rank")
  county_df <- prep_bump_chart(
    county_raw,
    config = list(
      question_id = "bump_county_rent_burden_rank",
      metric_id = "pct_rent_burden_30plus",
      entity_strategy = "peer_set",
      use_precomputed_rank = TRUE,
      include_highlighted = TRUE
    )
  )
  assert_bump_rank_direction(county_df, "bump_county_rent_burden_rank")
  county_plot <- render_bump_chart(
    county_df,
    config = list(
      output_mode = "presentation",
      title = "Which Wilmington-area counties rose in rent-burden rank?",
      subtitle = "2013-2024 counties within CBSA 48900 | Rank 1 has the highest rent-burdened renter share",
      label_mode = "all",
      label_style = "percent",
      label_accuracy = 0.1,
      label_include_value = TRUE,
      caption_side_note = "This is a stress-rank view: upward movement means a county moved toward a higher rent-burden rank."
    )
  )
  outputs["bump_county_rent_burden_rank"] <- save_bump_chart_plot(
    county_plot,
    output_dir,
    "bump_county_rent_burden_rank.png",
    width = 11.5,
    height = 6.7
  )

  # Question 5: How did Sweet Spot markets shift in overheating risk rank over time?
  sweet_spot_raw <- run_bump_chart_query(con, file.path(sql_dir, "bump_sweet_spot_overheating.sql"))
  assert_bump_chart_contract(sweet_spot_raw, "bump_sweet_spot_overheating")
  sweet_spot_df <- prep_bump_chart(
    sweet_spot_raw,
    config = list(
      question_id = "bump_sweet_spot_overheating",
      metric_id = "overheating_score",
      entity_strategy = "peer_set",
      use_precomputed_rank = TRUE,
      include_highlighted = TRUE
    )
  )
  assert_bump_rank_direction(sweet_spot_df, "bump_sweet_spot_overheating")
  sweet_spot_plot <- render_bump_chart(
    sweet_spot_df,
    config = list(
      output_mode = "presentation",
      title = "How did Sweet Spot markets shift in overheating risk rank?",
      subtitle = "2018-2023 fixed latest-year Sweet Spot CBSA set | Rank 1 has the highest overheating-risk score",
      label_mode = "highlight_or_all",
      label_all_max_n = 10,
      label_style = "number",
      label_accuracy = 1,
      rank_band_n = 5,
      caption_side_note = "Risk score blends population growth, income growth, value-to-income pressure, and rent-burden pressure."
    )
  )
  outputs["bump_sweet_spot_overheating"] <- save_bump_chart_plot(
    sweet_spot_plot,
    output_dir,
    "bump_sweet_spot_overheating.png",
    width = 12.5,
    height = 8
  )

  outputs["review_markdown"] <- write_bump_chart_review(output_dir, outputs)
  outputs
}

outputs <- run_bump_chart_tests()
print(outputs)
