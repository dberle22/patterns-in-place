#!/usr/bin/env Rscript

# This visual turns the broad "value-growth vs rent-growth" prompt into a
# publishable metro correlation matrix. The matrix keeps home-value and rent
# growth at the center, then adds a small set of strain, tightness, and growth
# metrics so the correlations are editorially useful.

source("publisher/content/housing/02_costs/visuals/_shared_costs_visuals.R")

script_path <- costs_get_script_path("publisher/content/housing/02_costs/visuals/cbsa_cost_correlation_heatmap.R")
ctx <- costs_build_context(script_path)
output_path <- file.path(ctx$output_dir, "cbsa_cost_correlation_heatmap.png")

costs_load_visual_library(ctx$foundations_dir, chart_types = c("correlation_heatmap"))

con <- costs_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

heatmap_raw <- costs_run_sql_file(con, ctx$sql_dir, "cbsa_cost_correlation_heatmap.sql")
heatmap_df <- prep_correlation_heatmap(
  heatmap_raw,
  config = list(
    method = "spearman",
    missingness = "pairwise.complete.obs",
    order_method = "input"
  )
)

heatmap_plot <- render_correlation_heatmap(
  heatmap_df,
  config = list(
    output_mode = "presentation",
    title = "Home-value and rent growth moved together across major metros",
    subtitle = paste(
      "Major CBSAs | Spearman correlations across 2019 to 2024 growth fields plus 2024 affordability context",
      "| Strong positive tiles show which pressures tend to travel together"
    ),
    legend_title = "Spearman correlation",
    show_cell_labels = TRUE,
    caption_side_note = "The matrix is centered on 2019-to-2024 rent and home-value growth, then adds vacancy, affordability, and growth-pressure context fields."
  )
)

costs_save_plot(
  heatmap_plot,
  output_path = output_path,
  width = 10.8,
  height = 8.6
)

message(sprintf("Saved %s", output_path))
