#!/usr/bin/env Rscript

# This visual is the main safeguard against overreading the provisional
# composite. It shows the component profile behind the hottest metros so we can
# see whether a market is ranking highly because of broad-based pressure or
# because one or two components are doing most of the work.

source("publisher/content/housing/04_overheating/visuals/_shared_overheating_visuals.R")

script_path <- overheating_get_script_path("publisher/content/housing/04_overheating/visuals/cbsa_overheating_component_heatmap.R")
ctx <- overheating_build_context(script_path)
output_path <- file.path(ctx$output_dir, "cbsa_overheating_component_heatmap.png")

overheating_load_visual_library(ctx$foundations_dir, chart_types = c("heatmap_table"))

con <- overheating_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

heatmap_raw <- overheating_run_sql_file(con, ctx$sql_dir, "cbsa_overheating_component_heatmap.sql")
heatmap_df <- prep_heatmap_table(
  heatmap_raw,
  config = list(
    time_window = "2024_snapshot",
    variant = "geo_metric",
    normalize = FALSE,
    fill_value_field = "normalized_value",
    label_value_field = "metric_value",
    label_style = "number",
    label_accuracy = 1,
    keep_missing = TRUE
  )
)

heatmap_plot <- render_heatmap_table(
  heatmap_df,
  config = list(
    output_mode = "presentation",
    title = "The hottest metros do not all arrive there for the same reason",
    subtitle = paste(
      "Top 10 major CBSAs by provisional overheating score, 2024",
      "| Fill and labels use the 0-100 component scale so the markets can be compared directly"
    ),
    fill_value_field = "normalized_value",
    legend_title = "Component score",
    show_cell_labels = TRUE,
    x_text_angle = 28,
    caption_side_note = "The final column is the composite percentile, while the earlier columns show the component families that feed into the provisional ranking."
  )
)

overheating_save_plot(
  heatmap_plot,
  output_path = output_path,
  width = 11.2,
  height = 8.8
)

message(sprintf("Saved %s", output_path))
