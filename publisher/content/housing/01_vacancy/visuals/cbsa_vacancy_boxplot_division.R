#!/usr/bin/env Rscript

# This visual deepens the regional story by showing the division-level spread
# behind the broader Census-region differences.

source("publisher/content/housing/01_vacancy/visuals/_shared_vacancy_visuals.R")

script_path <- vacancy_get_script_path("publisher/content/housing/01_vacancy/visuals/cbsa_vacancy_boxplot_division.R")
ctx <- vacancy_build_context(script_path)
output_path <- file.path(ctx$output_dir, "cbsa_vacancy_boxplot_division.png")

vacancy_load_visual_library(ctx$foundations_dir, chart_types = c("boxplot"))

con <- vacancy_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

distribution_raw <- vacancy_run_sql_file(con, ctx$sql_dir, "cbsa_vacancy_distributions.sql")
vacancy_division_df <- prep_boxplot(
  distribution_raw,
  config = list(
    question_id = "vacancy_boxplot_division",
    time_window = "2024_snapshot",
    metric_id = "vacancy_rate",
    order_groups = "median_desc"
  )
)

vacancy_division_plot <- render_boxplot(
  vacancy_division_df,
  config = list(
    output_mode = "presentation",
    title = "How do major-metro vacancy rates differ by Census division?",
    subtitle = "Major CBSAs with 2024 population of 100k+, grouped by Census division | Groups ordered by median vacancy rate",
    group_label = "Census division",
    value_label = "Vacancy rate",
    label_style = "percent",
    label_accuracy = 0.1,
    show_jitter = TRUE,
    flip = TRUE,
    caption_side_note = "This division cut is the finer-grained follow-up view for spotting where broad regional patterns are concentrated."
  )
)

vacancy_save_plot(
  vacancy_division_plot,
  output_path = output_path,
  width = 11.5,
  height = 7.8
)

message(sprintf("Saved %s", output_path))
