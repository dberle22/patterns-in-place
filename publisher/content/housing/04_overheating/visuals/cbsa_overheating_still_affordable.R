#!/usr/bin/env Rscript

# This visual is intentionally cautious. It does not claim these are the "best"
# housing markets. Instead, it surfaces major metros that still look relatively
# affordable after requiring below-median rent and value strain, then favoring
# lower strain and lower momentum.

source("publisher/content/housing/04_overheating/visuals/_shared_overheating_visuals.R")

script_path <- overheating_get_script_path("publisher/content/housing/04_overheating/visuals/cbsa_overheating_still_affordable.R")
ctx <- overheating_build_context(script_path)
output_path <- file.path(ctx$output_dir, "cbsa_overheating_still_affordable.png")

overheating_load_visual_library(ctx$foundations_dir, chart_types = c("bar"))

con <- overheating_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

bar_raw <- overheating_run_sql_file(con, ctx$sql_dir, "cbsa_overheating_rankings.sql")
bar_df <- prep_bar(
  bar_raw,
  config = list(
    question_id = "overheating_still_affordable",
    time_window = "2024_snapshot",
    metric_id = "still_affordable_score",
    top_n = 10,
    sort_desc = TRUE
  )
)

bar_plot <- render_bar(
  bar_df,
  config = list(
    title = "A few major metros still screen as comparatively affordable under the current heuristic",
    subtitle = paste(
      "Shortlist, 2024 | Markets first need below-median rent and value strain, then higher bars reflect lower strain and lower momentum",
      "| This is a careful shortlist, not a definitive 'best markets' ranking"
    ),
    output_mode = "presentation",
    label_style = "number",
    label_accuracy = 1,
    show_benchmark = TRUE,
    benchmark_value = 50,
    benchmark_label = "Midpoint",
    y_label = "Still-affordable shortlist score (0-100)",
    caption_side_note = "The shortlist first requires below-median rent-to-income and value-to-income levels within the major-CBSA universe."
  )
)

overheating_save_plot(
  bar_plot,
  output_path = output_path,
  width = 10.8,
  height = 7.4
)

message(sprintf("Saved %s", output_path))
