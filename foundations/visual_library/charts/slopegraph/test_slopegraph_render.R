# Slopegraph render tests with question-specific DuckDB queries.

if (file.exists(".Renviron")) readRenviron(".Renviron")

source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_slopegraph.R")
source("visual_library/shared/render/render_slopegraph.R")

run_slopegraph_query <- function(con, sql_path) {
  DBI::dbGetQuery(con, read_sql_file(sql_path))
}

assert_slopegraph_contract <- function(data, question_id) {
  validation <- validate_slopegraph_contract(data, require_single_geo_level = FALSE)
  period_count <- length(unique(stats::na.omit(data$period)))
  metric_count <- length(unique(stats::na.omit(data$metric_id)))

  if (isTRUE(validation$pass) && period_count == 2 && metric_count == 1) {
    return(invisible(validation))
  }

  stop(
    sprintf(
      "Slopegraph contract validation failed for %s. Missing required: %s. Rows: %s. Period count: %s. Metric count: %s",
      question_id,
      paste(validation$missing_required, collapse = ", "),
      validation$rows,
      period_count,
      metric_count
    )
  )
}

save_slopegraph_plot <- function(plot, output_dir, filename, width, height) {
  path <- file.path(output_dir, filename)
  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 300, bg = "white")
  path
}

run_slopegraph_tests <- function() {
  chart_dir <- "visual_library/charts/slopegraph"
  sql_dir <- file.path(chart_dir, "sample_sql")
  output_dir <- file.path(chart_dir, "sample_output")
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  con <- connect_metro_duckdb(read_only = TRUE)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  outputs <- c()

  # Question 1: Which CBSAs saw the largest change in real per-capita income?
  income_sql <- file.path(sql_dir, "slope_income_change_cbsas.sql")
  raw_income <- run_slopegraph_query(con, income_sql)
  assert_slopegraph_contract(raw_income, "slope_income_change_cbsas")
  income_df <- prep_slopegraph(
    raw_income,
    config = list(
      question_id = "slope_income_change_cbsas",
      metric_id = "rpp_real_pc_income",
      periods = c(2013, 2023),
      order_by = "abs_delta",
      sort_desc = TRUE,
      top_n = 12
    )
  )
  income_plot <- render_slopegraph(
    income_df,
    config = list(
      output_mode = "presentation",
      title = "Which CBSAs had the largest real income shifts?",
      subtitle = "2013-2023 CBSA comparison | Top movers selected by absolute change in real per-capita income",
      y_label = "Real per-capita income",
      label_style = "dollar",
      label_accuracy = 1,
      label_mode = "end",
      label_size = 2.9,
      caption_side_note = "Endpoint labels show the 2023 metro and 2013-2023 dollar change."
    )
  )
  outputs["slope_income_change_cbsas"] <- save_slopegraph_plot(
    income_plot,
    output_dir,
    "slope_income_change_cbsas.png",
    width = 12,
    height = 8
  )

  # Question 2: How did rent burden change for counties within the target CBSA?
  county_sql <- file.path(sql_dir, "slope_county_rent_burden.sql")
  raw_county <- run_slopegraph_query(con, county_sql)
  assert_slopegraph_contract(raw_county, "slope_county_rent_burden")
  county_df <- prep_slopegraph(
    raw_county,
    config = list(
      question_id = "slope_county_rent_burden",
      metric_id = "pct_rent_burden_30plus",
      periods = c(2018, 2023),
      order_by = "end_value",
      sort_desc = TRUE
    )
  )
  county_plot <- render_slopegraph(
    county_df,
    config = list(
      output_mode = "presentation",
      title = "How did rent burden change across Wilmington-area counties?",
      subtitle = "2018-2023 county comparison within CBSA 48900 | Sorted by latest rent-burden share",
      y_label = "Rent-burdened renter households (%)",
      label_style = "percent",
      label_accuracy = 0.1,
      label_mode = "both",
      caption_side_note = "Rent-burdened households spend at least 30 percent of income on rent."
    )
  )
  outputs["slope_county_rent_burden"] <- save_slopegraph_plot(
    county_plot,
    output_dir,
    "slope_county_rent_burden.png",
    width = 11,
    height = 7
  )

  # Question 3: Did peer affordability rank improve or worsen pre/post 2020?
  peer_sql <- file.path(sql_dir, "slope_peer_affordability_shift.sql")
  raw_peer <- run_slopegraph_query(con, peer_sql)
  assert_slopegraph_contract(raw_peer, "slope_peer_affordability_shift")
  peer_df <- prep_slopegraph(
    raw_peer,
    config = list(
      question_id = "slope_peer_affordability_shift",
      metric_id = "value_to_income",
      periods = c(2019, 2024),
      variant = "rank",
      order_by = "rank",
      sort_desc = FALSE,
      rank_higher_is_better = FALSE
    )
  )
  peer_plot <- render_slopegraph(
    peer_df,
    config = list(
      output_mode = "presentation",
      title = "Did Wilmington's affordability rank shift after 2020?",
      subtitle = "2019 vs 2024 selected peer set | Lower value-to-income rank indicates better relative affordability",
      y_label = "Affordability rank",
      label_style = "rank",
      label_accuracy = 1,
      label_mode = "both",
      show_delta_labels = FALSE,
      caption_side_note = "Rank is computed within the selected peer set for each endpoint year."
    )
  )
  outputs["slope_peer_affordability_shift"] <- save_slopegraph_plot(
    peer_plot,
    output_dir,
    "slope_peer_affordability_shift.png",
    width = 11,
    height = 7
  )

  # Question 4: Which ZCTAs moved most on home value-to-income?
  zcta_sql <- file.path(sql_dir, "slope_zcta_value_to_income_change.sql")
  raw_zcta <- run_slopegraph_query(con, zcta_sql)
  assert_slopegraph_contract(raw_zcta, "slope_zcta_value_to_income_change")
  zcta_df <- prep_slopegraph(
    raw_zcta,
    config = list(
      question_id = "slope_zcta_value_to_income_change",
      metric_id = "value_to_income",
      periods = c(2019, 2024),
      order_by = "abs_delta",
      sort_desc = TRUE,
      top_n = 18
    )
  )
  zcta_plot <- render_slopegraph(
    zcta_df,
    config = list(
      output_mode = "presentation",
      title = "Which Wilmington ZCTAs moved most on value-to-income?",
      subtitle = "2019-2024 ZCTA comparison within CBSA 48900 | Top movers by absolute ratio change",
      y_label = "Home value-to-income ratio",
      label_style = "number",
      label_accuracy = 0.1,
      label_mode = "end",
      caption_side_note = "Endpoint labels show the 2024 ZCTA and 2019-2024 ratio-point change."
    )
  )
  outputs["slope_zcta_value_to_income_change"] <- save_slopegraph_plot(
    zcta_plot,
    output_dir,
    "slope_zcta_value_to_income_change.png",
    width = 12,
    height = 8
  )

  # Question 5: How did the target CBSA shift relative to its region benchmark?
  benchmark_sql <- file.path(sql_dir, "slope_target_vs_region.sql")
  raw_benchmark <- run_slopegraph_query(con, benchmark_sql)
  assert_slopegraph_contract(raw_benchmark, "slope_target_vs_region")
  benchmark_df <- prep_slopegraph(
    raw_benchmark,
    config = list(
      question_id = "slope_target_vs_region",
      metric_id = "rpp_real_pc_income",
      periods = c(2013, 2023),
      order_by = "end_value",
      sort_desc = TRUE
    )
  )
  benchmark_plot <- render_slopegraph(
    benchmark_df,
    config = list(
      output_mode = "presentation",
      title = "Did Wilmington gain ground on its regional income benchmark?",
      subtitle = "2013-2023 comparison | Wilmington CBSA versus its Census division benchmark",
      y_label = "Real per-capita income",
      label_style = "dollar",
      label_accuracy = 1,
      label_mode = "both",
      caption_side_note = "Dashed line is the regional benchmark series."
    )
  )
  outputs["slope_target_vs_region"] <- save_slopegraph_plot(
    benchmark_plot,
    output_dir,
    "slope_target_vs_region.png",
    width = 10.5,
    height = 6.5
  )

  outputs
}

outputs <- run_slopegraph_tests()
print(outputs)
