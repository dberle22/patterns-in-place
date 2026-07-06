#!/usr/bin/env Rscript

# This visual focuses on the broad regional distribution of vacancy rates
# across major CBSAs. It is the first metro-level follow-up to the national map.

source("publisher/content/housing/01_vacancy/visuals/_shared_vacancy_visuals.R")

script_path <- vacancy_get_script_path("publisher/content/housing/01_vacancy/visuals/cbsa_vacancy_boxplot_region.R")
ctx <- vacancy_build_context(script_path)
output_path <- file.path(ctx$output_dir, "cbsa_vacancy_boxplot_region.png")

vacancy_load_visual_library(ctx$foundations_dir, chart_types = c("boxplot"))

con <- vacancy_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

distribution_raw <- vacancy_run_sql_file(con, ctx$sql_dir, "cbsa_vacancy_distributions.sql")
vacancy_region_df <- prep_boxplot(
  distribution_raw,
  config = list(
    question_id = "vacancy_boxplot_region",
    time_window = "2024_snapshot",
    metric_id = "vacancy_rate",
    order_groups = "median_desc"
  )
)

vacancy_region_plot <- render_boxplot(
  vacancy_region_df,
  config = list(
    output_mode = "presentation",
    title = "How do major-metro vacancy rates differ by Census region?",
    subtitle = "Major CBSAs with 2024 population of 100k+, grouped by Census region | Groups ordered by median vacancy rate",
    group_label = "Census region",
    value_label = "Vacancy rate",
    label_style = "percent",
    label_accuracy = 0.1,
    show_jitter = TRUE,
    caption_side_note = "This uses the section's temporary major-CBSA 100k flag so the distribution stays focused on larger metro markets."
  )
)

vacancy_save_plot(
  vacancy_region_plot,
  output_path = output_path,
  width = 11.2,
  height = 7.0
)

message(sprintf("Saved %s", output_path))
