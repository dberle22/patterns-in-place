#!/usr/bin/env Rscript

# This visual shows the finer-grained division paths behind the broader region
# story, again using housing-unit-weighted averages where the series is rolled up.

source("publisher/content/housing/01_vacancy/visuals/_shared_vacancy_visuals.R")

script_path <- vacancy_get_script_path("publisher/content/housing/01_vacancy/visuals/vacancy_trend_divisions.R")
ctx <- vacancy_build_context(script_path)
output_path <- file.path(ctx$output_dir, "vacancy_trend_divisions.png")

vacancy_load_visual_library(ctx$foundations_dir, chart_types = c("line"))

con <- vacancy_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

trend_raw <- vacancy_run_sql_file(con, ctx$sql_dir, "vacancy_trends.sql")
vacancy_division_trend_df <- prep_line(
  trend_raw,
  config = list(
    question_id = "vacancy_trend_divisions",
    metric_id = "vacancy_rate",
    variant = "multi",
    period_min = 2012,
    period_max = 2024
  )
)

vacancy_division_trend_plot <- render_line(
  vacancy_division_trend_df,
  config = list(
    output_mode = "presentation",
    title = "Division-level vacancy paths show where looseness really accumulated",
    subtitle = "2012-2024 annual series | US headline, major-CBSA weighted average, and housing-unit-weighted division averages",
    y_label = "Vacancy rate",
    label_style = "percent",
    label_accuracy = 0.1,
    show_points = FALSE,
    caption_side_note = "This denser follow-up view shows which divisions are doing the real work behind region-level vacancy patterns."
  )
)

vacancy_save_plot(
  vacancy_division_trend_plot,
  output_path = output_path,
  width = 11.5,
  height = 7.3
)

message(sprintf("Saved %s", output_path))
