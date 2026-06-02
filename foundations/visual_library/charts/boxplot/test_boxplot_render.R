# Boxplot chart render tests with question-specific DuckDB queries.

if (file.exists(".Renviron")) readRenviron(".Renviron")

source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_boxplot.R")
source("visual_library/shared/render/render_boxplot.R")

run_boxplot_query <- function(con, sql_path) {
  sql <- read_sql_file(sql_path)
  DBI::dbGetQuery(con, sql)
}

assert_boxplot_contract <- function(data, question_id) {
  validation <- validate_boxplot_contract(data)
  if (isTRUE(validation$pass)) {
    return(invisible(validation))
  }

  stop(
    sprintf(
      "Boxplot contract validation failed for %s. Missing required: %s. Rows: %s",
      question_id,
      paste(validation$missing_required, collapse = ", "),
      validation$rows
    )
  )
}

save_boxplot_plot <- function(plot, output_dir, filename, width = 11, height = 7) {
  path <- file.path(output_dir, filename)
  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 300, bg = "white")
  path
}

write_boxplot_review <- function(output_dir, outputs) {
  review_path <- file.path(output_dir, "test_boxplot_business_questions.md")
  lines <- c(
    "# Boxplot Testing",
    "",
    "## Canonical Questions",
    "1. How does rent burden vary across regions, and where does the target CBSA fall?",
    "2. For counties in the target CBSA, what is the distribution of median rent-to-income?",
    "3. Within the target CBSA, do ZCTAs show a long tail of high commute intensity?",
    "4. Are Sweet Spot markets outliers on affordability relative to all CBSAs?",
    "5. How does the distribution of income growth differ by CBSA type?",
    "",
    "## Output Files",
    paste0("- `boxplot_rent_burden_by_region`: ", outputs[["boxplot_rent_burden_by_region"]]),
    paste0("- `boxplot_target_cbsa_county_rent_to_income`: ", outputs[["boxplot_target_cbsa_county_rent_to_income"]]),
    paste0("- `boxplot_target_cbsa_zcta_commute_tail`: ", outputs[["boxplot_target_cbsa_zcta_commute_tail"]]),
    paste0("- `boxplot_sweet_spot_affordability_outliers`: ", outputs[["boxplot_sweet_spot_affordability_outliers"]]),
    paste0("- `boxplot_income_growth_by_cbsa_type`: ", outputs[["boxplot_income_growth_by_cbsa_type"]]),
    "",
    "## QA Notes",
    "- Shared prep validates the boxplot contract, filters to the requested question, coerces numeric/logical fields, creates `box_group`, and orders groups by median by default.",
    "- Shared render uses the visual-library theme, standard 1.5 IQR boxplot whiskers, optional jitter, shared benchmark helpers, and shared label helpers for highlighted geographies.",
    "- The first sample set keeps boxplot-specific decisions local except for adding the shared boxplot contract and chart defaults.",
    "- County and ZCTA examples intentionally use target markets with enough observations for distribution review."
  )
  writeLines(lines, review_path)
  review_path
}

run_boxplot_tests <- function() {
  output_dir <- "visual_library/charts/boxplot/sample_output"
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  con <- connect_metro_duckdb(read_only = TRUE)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  outputs <- c()

  # Query block: rent burden by region
  q1_path <- "visual_library/charts/boxplot/sample_sql/q1_rent_burden_by_region.sql"
  q1_raw <- run_boxplot_query(con, q1_path)
  assert_boxplot_contract(q1_raw, "boxplot_rent_burden_by_region")

  # Prep block
  q1_df <- prep_boxplot(
    q1_raw,
    config = list(
      question_id = "boxplot_rent_burden_by_region",
      time_window = "2024_snapshot",
      metric_id = "pct_rent_burden_30plus",
      order_groups = "median_desc"
    )
  )

  # Render block
  q1_plot <- render_boxplot(
    q1_df,
    config = list(
      output_mode = "presentation",
      title = "How does rent burden vary across regions?",
      subtitle = "CBSA distribution by Census region, 2024 snapshot | Highlight marks Wilmington, NC | Groups ordered by median rent burden",
      group_label = "Census region",
      value_label = "Rent-burdened renter households",
      label_style = "percent",
      label_accuracy = 0.1,
      show_jitter = TRUE,
      caption_side_note = "Use this to compare regional medians and spread before treating the highlighted target as typical or unusual."
    )
  )

  # Export path
  outputs["boxplot_rent_burden_by_region"] <- save_boxplot_plot(
    q1_plot,
    output_dir,
    "boxplot_q1_rent_burden_by_region.png",
    width = 11.5,
    height = 7.2
  )

  # Query block: target CBSA county rent-to-income
  q2_path <- "visual_library/charts/boxplot/sample_sql/q2_target_cbsa_county_rent_to_income.sql"
  q2_raw <- run_boxplot_query(con, q2_path)
  assert_boxplot_contract(q2_raw, "boxplot_target_cbsa_county_rent_to_income")

  # Prep block
  q2_df <- prep_boxplot(
    q2_raw,
    config = list(
      question_id = "boxplot_target_cbsa_county_rent_to_income",
      time_window = "2024_snapshot",
      metric_id = "rent_to_income",
      order_groups = "median_desc"
    )
  )

  # Render block
  q2_plot <- render_boxplot(
    q2_df,
    config = list(
      output_mode = "presentation",
      title = "Atlanta-area county rent-to-income distribution",
      subtitle = "Counties in the Atlanta-Sandy Springs-Roswell CBSA, 2024 snapshot | Grouped by county state | Highlight marks Fulton County",
      group_label = "County state",
      value_label = "Median rent-to-income ratio",
      label_style = "percent",
      label_accuracy = 0.1,
      show_jitter = TRUE,
      caption_side_note = "Atlanta is used for this county distribution sample because it has enough counties for a meaningful boxplot."
    )
  )

  # Export path
  outputs["boxplot_target_cbsa_county_rent_to_income"] <- save_boxplot_plot(
    q2_plot,
    output_dir,
    "boxplot_q2_target_cbsa_county_rent_to_income.png",
    width = 10.5,
    height = 6.5
  )

  # Query block: target CBSA ZCTA commute tail
  q3_path <- "visual_library/charts/boxplot/sample_sql/q3_target_cbsa_zcta_commute_tail.sql"
  q3_raw <- run_boxplot_query(con, q3_path)
  assert_boxplot_contract(q3_raw, "boxplot_target_cbsa_zcta_commute_tail")

  # Prep block
  q3_df <- prep_boxplot(
    q3_raw,
    config = list(
      question_id = "boxplot_target_cbsa_zcta_commute_tail",
      time_window = "2024_snapshot",
      metric_id = "commute_intensity_proxy",
      order_groups = "median_desc"
    )
  )

  # Render block
  q3_plot <- render_boxplot(
    q3_df,
    config = list(
      output_mode = "presentation",
      title = "Do Wilmington-area ZCTAs have a long commute-intensity tail?",
      subtitle = "ZCTAs in the Wilmington, NC CBSA, 2024 snapshot | Proxy = mean travel time x car commute share | Highlighted points are the three highest values",
      group_label = "County",
      value_label = "Commute intensity proxy",
      label_style = "number",
      label_accuracy = 0.1,
      show_jitter = TRUE,
      caption_side_note = "The point overlay keeps the long-tail ZCTAs visible without replacing the distribution summary."
    )
  )

  # Export path
  outputs["boxplot_target_cbsa_zcta_commute_tail"] <- save_boxplot_plot(
    q3_plot,
    output_dir,
    "boxplot_q3_target_cbsa_zcta_commute_tail.png",
    width = 11,
    height = 6.8
  )

  # Query block: Sweet Spot affordability outliers
  q4_path <- "visual_library/charts/boxplot/sample_sql/q4_sweet_spot_affordability_outliers.sql"
  q4_raw <- run_boxplot_query(con, q4_path)
  assert_boxplot_contract(q4_raw, "boxplot_sweet_spot_affordability_outliers")

  # Prep block
  q4_df <- prep_boxplot(
    q4_raw,
    config = list(
      question_id = "boxplot_sweet_spot_affordability_outliers",
      time_window = "2024_snapshot",
      metric_id = "median_home_value",
      order_groups = "median_desc",
      trim_quantiles = c(0.01, 0.99),
      winsorize_display = TRUE
    )
  )

  # Render block
  q4_plot <- render_boxplot(
    q4_df,
    config = list(
      output_mode = "presentation",
      title = "Are Sweet Spot markets still affordable relative to all CBSAs?",
      subtitle = "2024 CBSA distribution by metro/micro type | Highlight proxy = fast-growing metro areas with home-value percentile <= 85",
      group_label = "CBSA type",
      value_label = "Median home value",
      label_style = "dollar",
      label_accuracy = 1,
      show_jitter = FALSE,
      show_highlight_labels = FALSE,
      show_benchmark = TRUE,
      benchmark_method = "median",
      benchmark_label = "Overall median",
      caption_side_note = "Highlights use a first-pass Sweet Spot proxy from growth and home-value percentiles; this is a sample query, not a finalized market definition. Display values are winsorized at the 1st and 99th percentiles."
    )
  )

  # Export path
  outputs["boxplot_sweet_spot_affordability_outliers"] <- save_boxplot_plot(
    q4_plot,
    output_dir,
    "boxplot_q4_sweet_spot_affordability_outliers.png",
    width = 11,
    height = 6.8
  )

  # Query block: income growth by CBSA type
  q5_path <- "visual_library/charts/boxplot/sample_sql/q5_income_growth_by_cbsa_type.sql"
  q5_raw <- run_boxplot_query(con, q5_path)
  assert_boxplot_contract(q5_raw, "boxplot_income_growth_by_cbsa_type")

  # Prep block
  q5_df <- prep_boxplot(
    q5_raw,
    config = list(
      question_id = "boxplot_income_growth_by_cbsa_type",
      time_window = "2018_to_2023_cagr",
      metric_id = "income_pc_cagr_5yr",
      order_groups = "median_desc"
    )
  )

  # Render block
  q5_plot <- render_boxplot(
    q5_df,
    config = list(
      output_mode = "presentation",
      title = "How does per-capita income growth differ by CBSA type?",
      subtitle = "CBSAs, 2018-2023 CAGR | Metro Area vs Micro Area | Highlight marks Wilmington, NC",
      group_label = "CBSA type",
      value_label = "Per-capita income CAGR",
      label_style = "percent",
      label_accuracy = 0.1,
      show_jitter = TRUE,
      show_benchmark = TRUE,
      benchmark_method = "median",
      benchmark_label = "Overall median",
      caption_side_note = "Distribution view helps separate the typical metro/micro growth range from the highlighted target market."
    )
  )

  # Export path
  outputs["boxplot_income_growth_by_cbsa_type"] <- save_boxplot_plot(
    q5_plot,
    output_dir,
    "boxplot_q5_income_growth_by_cbsa_type.png",
    width = 10.5,
    height = 6.5
  )

  outputs["review_markdown"] <- write_boxplot_review(output_dir, outputs)
  outputs
}

outputs <- run_boxplot_tests()
print(outputs)
