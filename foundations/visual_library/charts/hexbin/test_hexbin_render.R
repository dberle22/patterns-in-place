# Hexbin chart render tests with question-specific DuckDB queries.

if (file.exists(".Renviron")) readRenviron(".Renviron")

source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_hexbin.R")
source("visual_library/shared/render/render_hexbin.R")

run_hexbin_query <- function(con, sql_path) {
  sql <- read_sql_file(sql_path)
  DBI::dbGetQuery(con, sql)
}

assert_hexbin_contract <- function(data, question_id) {
  validation <- validate_hexbin_contract(data)
  if (isTRUE(validation$pass)) {
    return(invisible(validation))
  }

  stop(
    sprintf(
      "Hexbin contract validation failed for %s. Missing required: %s. Rows: %s",
      question_id,
      paste(validation$missing_required, collapse = ", "),
      validation$rows
    )
  )
}

save_hexbin_plot <- function(plot, output_dir, filename, width = 11, height = 7) {
  path <- file.path(output_dir, filename)
  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 300, bg = "white")
  path
}

active_density_method <- function() {
  if (requireNamespace("hexbin", quietly = TRUE)) "Hexbin" else "2D bins"
}

run_hexbin_tests <- function() {
  output_dir <- "visual_library/charts/hexbin/sample_output"
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  con <- connect_metro_duckdb(read_only = TRUE)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  outputs <- c()
  density_method <- active_density_method()

  q1_path <- "visual_library/charts/hexbin/sample_sql/q1_zcta_affordability_density.sql"
  q1_raw <- run_hexbin_query(con, q1_path)
  assert_hexbin_contract(q1_raw, "hexbin_affordability_density")
  q1_df <- prep_hexbin(
    q1_raw,
    config = list(
      question_id = "hexbin_affordability_density",
      time_window = "2023_snapshot",
      x_quantile_limits = c(0.01, 0.99),
      y_quantile_limits = c(0.01, 0.99)
    )
  )
  q1_plot <- render_hexbin(
    q1_df,
    config = list(
      output_mode = "presentation",
      method = "hex",
      bins = 30,
      title = "Where do most neighborhoods sit on income vs rent burden?",
      subtitle = paste(
        "All ZCTAs, 2023 snapshot |",
        density_method,
        "fill = neighborhood count per bin | 1st-99th percentile trim on both axes"
      ),
      label_style_x = "dollar",
      label_accuracy_x = 1,
      label_style_y = "percent",
      label_accuracy_y = 1,
      legend_position = "right",
      caption_side_note = "Use the dense core to locate the typical affordability tradeoff before reading the sparse tails."
    )
  )
  outputs["hexbin_affordability_density"] <- save_hexbin_plot(
    q1_plot,
    output_dir,
    "hexbin_q1_affordability_density.png"
  )

  q2_path <- "visual_library/charts/hexbin/sample_sql/q2_zcta_growth_vs_burden_clusters.sql"
  q2_raw <- run_hexbin_query(con, q2_path)
  assert_hexbin_contract(q2_raw, "hexbin_growth_vs_burden_clusters")
  q2_df <- prep_hexbin(
    q2_raw,
    config = list(
      question_id = "hexbin_growth_vs_burden_clusters",
      time_window = "2018_to_2023_growth",
      x_quantile_limits = c(0.01, 0.99),
      y_quantile_limits = c(0.01, 0.99)
    )
  )
  q2_plot <- render_hexbin(
    q2_df,
    config = list(
      output_mode = "presentation",
      method = "hex",
      bins = 28,
      overlay_highlights = TRUE,
      add_reference_lines = TRUE,
      title = "Are there distinct clusters with both high growth and high rent burden?",
      subtitle = paste(
        "All ZCTAs, 2023 snapshot |",
        density_method,
        "fill = neighborhood count per bin | 1st-99th percentile trim on both axes | Highlighted points come from the extreme high-growth/high-burden tail"
      ),
      label_style_x = "number",
      label_accuracy_x = 1,
      label_style_y = "percent",
      label_accuracy_y = 1,
      legend_position = "right",
      caption_side_note = "Median reference lines help separate the dense center from the upper-right hotspot tail."
    )
  )
  outputs["hexbin_growth_vs_burden_clusters"] <- save_hexbin_plot(
    q2_plot,
    output_dir,
    "hexbin_q2_growth_vs_burden_clusters.png"
  )

  q3_path <- "visual_library/charts/hexbin/sample_sql/q3_target_cbsa_tradeoff_shape.sql"
  q3_raw <- run_hexbin_query(con, q3_path)
  assert_hexbin_contract(q3_raw, "hexbin_target_cbsa_tradeoff_shape")
  q3_df <- prep_hexbin(
    q3_raw,
    config = list(
      question_id = "hexbin_target_cbsa_tradeoff_shape",
      time_window = "2023_snapshot",
      require_single_time_window = TRUE
    )
  )
  q3_plot <- render_hexbin(
    q3_df,
    config = list(
      output_mode = "presentation",
      method = "hex",
      bins = 22,
      overlay_highlights = TRUE,
      title = "What is the local affordability tradeoff shape inside New York-Newark-Jersey City?",
      subtitle = paste(
        "Target CBSA ZCTAs, 2023 snapshot |",
        density_method,
        "| X = home value / income ratio | Y = rent / income ratio (%) | Highlighted points are local outliers"
      ),
      label_style_x = "number",
      label_accuracy_x = 0.1,
      label_style_y = "percent",
      label_accuracy_y = 1,
      legend_position = "right",
      caption_side_note = "This local view swaps national coverage for more detail on the metro's internal affordability structure."
    )
  )
  outputs["hexbin_target_cbsa_tradeoff_shape"] <- save_hexbin_plot(
    q3_plot,
    output_dir,
    "hexbin_q3_target_cbsa_tradeoff_shape.png"
  )

  q4_path <- "visual_library/charts/hexbin/sample_sql/q4_regional_density_compare.sql"
  q4_raw <- run_hexbin_query(con, q4_path)
  assert_hexbin_contract(q4_raw, "hexbin_regional_density_compare")
  q4_df <- prep_hexbin(
    q4_raw,
    config = list(
      question_id = "hexbin_regional_density_compare",
      time_window = "2023_snapshot",
      x_quantile_limits = c(0.01, 0.99),
      y_quantile_limits = c(0.01, 0.99)
    )
  )
  q4_plot <- render_hexbin(
    q4_df,
    config = list(
      output_mode = "presentation",
      method = "hex",
      bins = 24,
      facet_by = "group",
      title = "How does affordability density differ across census regions?",
      subtitle = paste(
        "All ZCTAs, 2023 snapshot | Faceted",
        density_method,
        "with fixed axes | 1st-99th percentile trim on both axes"
      ),
      label_style_x = "dollar",
      label_accuracy_x = 1,
      label_style_y = "percent",
      label_accuracy_y = 1,
      legend_position = "right",
      caption_side_note = "Fixed axes make the regional density shapes directly comparable across panels."
    )
  )
  outputs["hexbin_regional_density_compare"] <- save_hexbin_plot(
    q4_plot,
    output_dir,
    "hexbin_q4_regional_density_compare.png",
    width = 12,
    height = 9
  )

  q5_path <- "visual_library/charts/hexbin/sample_sql/q5_population_weighted_tradeoff.sql"
  q5_raw <- run_hexbin_query(con, q5_path)
  assert_hexbin_contract(q5_raw, "hexbin_population_weighted_tradeoff")
  q5_df <- prep_hexbin(
    q5_raw,
    config = list(
      question_id = "hexbin_population_weighted_tradeoff",
      time_window = "2023_snapshot",
      x_quantile_limits = c(0.01, 0.99),
      y_quantile_limits = c(0.01, 0.99)
    )
  )
  q5_plot <- render_hexbin(
    q5_df,
    config = list(
      output_mode = "presentation",
      method = "hex",
      bins = 30,
      use_weights = TRUE,
      weight_label = "Population per bin",
      legend_title = "Population per bin",
      title = "If weighted by population, where do most people fall on the affordability tradeoff curve?",
      subtitle = paste(
        "All ZCTAs, 2023 snapshot | Population-weighted",
        density_method,
        "| 1st-99th percentile trim on both axes"
      ),
      label_style_x = "dollar",
      label_accuracy_x = 1,
      label_style_y = "percent",
      label_accuracy_y = 1,
      legend_position = "right",
      caption_side_note = "This view shifts the emphasis from where places sit to where people are concentrated."
    )
  )
  outputs["hexbin_population_weighted_tradeoff"] <- save_hexbin_plot(
    q5_plot,
    output_dir,
    "hexbin_q5_population_weighted_tradeoff.png"
  )

  outputs
}

outputs <- run_hexbin_tests()
print(outputs)
