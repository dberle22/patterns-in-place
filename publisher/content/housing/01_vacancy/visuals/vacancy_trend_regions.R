#!/usr/bin/env Rscript

# This visual compares the national vacancy path against the major-metro
# average and the four Census regions, all on a housing-unit-weighted basis
# where appropriate.

source("publisher/content/housing/01_vacancy/visuals/_shared_vacancy_visuals.R")

script_path <- vacancy_get_script_path("publisher/content/housing/01_vacancy/visuals/vacancy_trend_regions.R")
ctx <- vacancy_build_context(script_path)
output_path <- file.path(ctx$output_dir, "vacancy_trend_regions.png")

vacancy_load_visual_library(ctx$foundations_dir, chart_types = c("line"))

con <- vacancy_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

trend_raw <- vacancy_run_sql_file(con, ctx$sql_dir, "vacancy_trends.sql")
vacancy_region_trend_df <- prep_line(
  trend_raw,
  config = list(
    question_id = "vacancy_trend_regions",
    metric_id = "vacancy_rate",
    variant = "multi",
    period_min = 2012,
    period_max = 2024
  )
)

vacancy_region_trend_plot <- render_line(
  vacancy_region_trend_df,
  config = list(
    output_mode = "presentation",
    title = "Vacancy has opened up unevenly across regions",
    subtitle = "2012-2024 annual series | US headline, major-CBSA weighted average, and housing-unit-weighted region averages",
    y_label = "Vacancy rate",
    label_style = "percent",
    label_accuracy = 0.1,
    show_points = TRUE,
    caption_side_note = "Region and CBSA comparison lines are weighted by housing units so large markets carry proportionate influence."
  )
)

vacancy_save_plot(
  vacancy_region_trend_plot,
  output_path = output_path,
  width = 11.2,
  height = 7.0
)

message(sprintf("Saved %s", output_path))
