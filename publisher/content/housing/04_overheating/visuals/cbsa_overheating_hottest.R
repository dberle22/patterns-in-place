#!/usr/bin/env Rscript

# This visual names the markets that rise to the top under the current
# provisional overheating composite. The score is shown as a 0-100 index so the
# ranking reads cleanly, but the surrounding section still shows the components
# that sit behind the bars.

source("publisher/content/housing/04_overheating/visuals/_shared_overheating_visuals.R")

script_path <- overheating_get_script_path("publisher/content/housing/04_overheating/visuals/cbsa_overheating_hottest.R")
ctx <- overheating_build_context(script_path)
output_path <- file.path(ctx$output_dir, "cbsa_overheating_hottest.png")

overheating_load_visual_library(ctx$foundations_dir, chart_types = c("bar"))

con <- overheating_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

bar_raw <- overheating_run_sql_file(con, ctx$sql_dir, "cbsa_overheating_rankings.sql")
bar_df <- prep_bar(
  bar_raw,
  config = list(
    question_id = "overheating_hottest",
    time_window = "2024_snapshot",
    metric_id = "provisional_overheating_score",
    top_n = 10,
    sort_desc = TRUE
  )
)

bar_plot <- render_bar(
  bar_df,
  config = list(
    title = "The provisional overheating score points to a small set of especially hot metros",
    subtitle = paste(
      "Major CBSAs, 2024 | Higher scores reflect hotter combined momentum, pressure, strain, and tightness",
      "| This ranking is provisional and should be read alongside the component views"
    ),
    output_mode = "presentation",
    label_style = "number",
    label_accuracy = 1,
    show_benchmark = TRUE,
    benchmark_value = 50,
    benchmark_label = "Midpoint",
    x_label = NULL,
    y_label = "Overheating score (0-100)",
    caption_side_note = "Bars show the provisional composite score scaled to a 0-100 index. The midpoint line is a visual reference, not a formal threshold."
  )
)

overheating_save_plot(
  bar_plot,
  output_path = output_path,
  width = 10.6,
  height = 7.4
)

message(sprintf("Saved %s", output_path))
