#!/usr/bin/env Rscript

# This visual names the major metros where vacancy is highest, giving the
# section a direct "loosest markets" ranking view.

source("publisher/content/housing/01_vacancy/visuals/_shared_vacancy_visuals.R")

script_path <- vacancy_get_script_path("publisher/content/housing/01_vacancy/visuals/cbsa_vacancy_loosest.R")
ctx <- vacancy_build_context(script_path)
output_path <- file.path(ctx$output_dir, "cbsa_vacancy_loosest.png")

vacancy_load_visual_library(ctx$foundations_dir, chart_types = c("bar"))

con <- vacancy_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

extremes_raw <- vacancy_run_sql_file(con, ctx$sql_dir, "cbsa_vacancy_extremes.sql")
loosest_df <- prep_bar(
  extremes_raw,
  config = list(
    question_id = "vacancy_bar_loosest",
    time_window = "2024_snapshot",
    metric_id = "vacancy_rate",
    sort_desc = TRUE,
    top_n = 10
  )
)

loosest_plot <- render_bar(
  loosest_df,
  config = list(
    output_mode = "presentation",
    title = "The loosest major metro housing markets in 2024",
    subtitle = "Top 10 vacancy rates among major CBSAs with 2024 population of 100k+",
    y_label = "Vacancy rate",
    label_style = "percent",
    label_accuracy = 0.1,
    show_benchmark = TRUE,
    benchmark_label = "US housing-unit-weighted context",
    caption_side_note = "High vacancy can reflect seasonal housing stock, second-home markets, or weaker local demand, so the tail deserves interpretation rather than a simple good/bad read."
  )
)

vacancy_save_plot(
  loosest_plot,
  output_path = output_path,
  width = 11.0,
  height = 7.0
)

message(sprintf("Saved %s", output_path))
