# Correlation heatmap render tests with question-specific DuckDB queries.

if (file.exists(".Renviron")) readRenviron(".Renviron")

source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_correlation_heatmap.R")
source("visual_library/shared/render/render_correlation_heatmap.R")

run_correlation_heatmap_query <- function(con, sql_path) {
  sql <- read_sql_file(sql_path)
  DBI::dbGetQuery(con, sql)
}

assert_correlation_heatmap_contract <- function(data, question_id) {
  validation <- validate_correlation_heatmap_contract(data)
  if (isTRUE(validation$pass)) {
    return(invisible(validation))
  }

  stop(
    sprintf(
      "Correlation heatmap contract validation failed for %s. Missing required: %s. Rows: %s",
      question_id,
      paste(validation$missing_required, collapse = ", "),
      validation$rows
    )
  )
}

save_correlation_heatmap_plot <- function(plot, output_dir, filename, width = 10, height = 8) {
  path <- file.path(output_dir, filename)
  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 300, bg = "white")
  path
}

run_correlation_heatmap_tests <- function() {
  output_dir <- "visual_library/charts/correlation_heatmap/sample_output"
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  con <- connect_metro_duckdb(read_only = TRUE)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  outputs <- c()

  q1_path <- "visual_library/charts/correlation_heatmap/sample_sql/q1_redundant_kpis.sql"
  q1_raw <- run_correlation_heatmap_query(con, q1_path)
  assert_correlation_heatmap_contract(q1_raw, "corr_redundant_kpis")
  q1_df <- prep_correlation_heatmap(
    q1_raw,
    config = list(
      question_id = "corr_redundant_kpis",
      method = "spearman",
      order_method = "clustered"
    )
  )
  q1_plot <- render_correlation_heatmap(
    q1_df,
    config = list(
      output_mode = "presentation",
      legend_title = "Spearman r",
      title = "Which CBSA KPIs look redundant enough to avoid double-counting?",
      subtitle = "All CBSAs | 2024 snapshot | Spearman correlation with pairwise-complete handling | clustered metric order",
      caption_side_note = "This matrix uses intentionally overlapping affordability and income metrics so near-duplicate signals show up as strong blocks.",
      show_cell_labels = TRUE
    )
  )
  outputs["corr_redundant_kpis"] <- save_correlation_heatmap_plot(
    q1_plot,
    output_dir,
    "correlation_heatmap_q1_redundant_kpis.png"
  )

  q2_path <- "visual_library/charts/correlation_heatmap/sample_sql/q2_growth_vs_level_blocks.sql"
  q2_raw <- run_correlation_heatmap_query(con, q2_path)
  assert_correlation_heatmap_contract(q2_raw, "corr_growth_vs_level_blocks")
  q2_df <- prep_correlation_heatmap(
    q2_raw,
    config = list(
      question_id = "corr_growth_vs_level_blocks",
      method = "spearman",
      order_method = "clustered",
      weak_threshold = 0.2
    )
  )
  q2_plot <- render_correlation_heatmap(
    q2_df,
    config = list(
      output_mode = "presentation",
      legend_title = "Spearman r",
      title = "Do growth metrics separate from level metrics in the national CBSA KPI set?",
      subtitle = "All CBSAs | 2024 snapshot | Spearman correlation with pairwise-complete handling | weak relationships under |r| < 0.20 are masked",
      caption_side_note = "The KPI mix is balanced on purpose: five level metrics plus four growth metrics to make block structure easy to inspect.",
      show_cell_labels = FALSE
    )
  )
  outputs["corr_growth_vs_level_blocks"] <- save_correlation_heatmap_plot(
    q2_plot,
    output_dir,
    "correlation_heatmap_q2_growth_vs_level_blocks.png"
  )

  q3_path <- "visual_library/charts/correlation_heatmap/sample_sql/q3_rent_burden_driver_scan.sql"
  q3_raw <- run_correlation_heatmap_query(con, q3_path)
  assert_correlation_heatmap_contract(q3_raw, "corr_rent_burden_driver_scan")
  q3_df <- prep_correlation_heatmap(
    q3_raw,
    config = list(
      question_id = "corr_rent_burden_driver_scan",
      method = "spearman",
      order_method = "clustered"
    )
  )
  q3_plot <- render_correlation_heatmap(
    q3_df,
    config = list(
      output_mode = "presentation",
      legend_title = "Spearman r",
      title = "Which indicators move most closely with rent burden across CBSAs?",
      subtitle = "All CBSAs | 2024 snapshot | Spearman correlation with pairwise-complete handling | clustered metric order",
      caption_side_note = "Read the rent-burden row and column first; the rest of the matrix gives context on whether the strongest links lean toward income, labor, or supply conditions.",
      show_cell_labels = TRUE
    )
  )
  outputs["corr_rent_burden_driver_scan"] <- save_correlation_heatmap_plot(
    q3_plot,
    output_dir,
    "correlation_heatmap_q3_rent_burden_driver_scan.png"
  )

  q4_path <- "visual_library/charts/correlation_heatmap/sample_sql/q4_sweet_spot_compare.sql"
  q4_raw <- run_correlation_heatmap_query(con, q4_path)
  assert_correlation_heatmap_contract(q4_raw, "corr_sweet_spot_compare")
  q4_df <- prep_correlation_heatmap(
    q4_raw,
    config = list(
      question_id = "corr_sweet_spot_compare",
      method = "spearman",
      order_method = "clustered",
      facet_by = "group"
    )
  )
  q4_plot <- render_correlation_heatmap(
    q4_df,
    config = list(
      output_mode = "presentation",
      legend_title = "Spearman r",
      facet_by = "group",
      title = "Does the Sweet Spot shortlist show a different KPI correlation structure?",
      subtitle = "2024 CBSA comparison | Faceted Spearman matrices for all CBSAs versus a derived 12-metro shortlist",
      caption_side_note = "Derived shortlist is a proxy; DuckDB has no canonical Sweet Spot flag yet.",
      caption_methodology_note = "Spearman | pairwise | clustered",
      show_cell_labels = FALSE
    )
  )
  outputs["corr_sweet_spot_compare"] <- save_correlation_heatmap_plot(
    q4_plot,
    output_dir,
    "correlation_heatmap_q4_sweet_spot_compare.png",
    width = 14.5,
    height = 7.5
  )

  q5_path <- "visual_library/charts/correlation_heatmap/sample_sql/q5_county_within_cbsa.sql"
  q5_raw <- run_correlation_heatmap_query(con, q5_path)
  assert_correlation_heatmap_contract(q5_raw, "corr_county_within_cbsa")
  q5_df <- prep_correlation_heatmap(
    q5_raw,
    config = list(
      question_id = "corr_county_within_cbsa",
      method = "spearman",
      order_method = "clustered"
    )
  )
  q5_plot <- render_correlation_heatmap(
    q5_df,
    config = list(
      output_mode = "presentation",
      legend_title = "Spearman r",
      title = "Which housing indicators co-move most across Atlanta-area counties?",
      subtitle = "Atlanta-Sandy Springs-Roswell, GA counties | 2024 snapshot | Spearman correlation with pairwise-complete handling",
      caption_side_note = "This within-metro read trades national breadth for a dense county set where housing structure, prices, and burden can be compared side by side.",
      show_cell_labels = TRUE
    )
  )
  outputs["corr_county_within_cbsa"] <- save_correlation_heatmap_plot(
    q5_plot,
    output_dir,
    "correlation_heatmap_q5_county_within_cbsa.png"
  )

  outputs
}

outputs <- run_correlation_heatmap_tests()
print(outputs)
