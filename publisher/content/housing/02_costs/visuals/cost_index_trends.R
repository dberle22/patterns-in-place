#!/usr/bin/env Rscript

# This visual compares how rents and home values moved over the 2019-to-2024
# run-up. We keep the chart indexed so the story is pace-of-change rather than
# absolute-dollar scale, then facet by scope to keep the national and
# major-metro read equally legible.

source("publisher/content/housing/02_costs/visuals/_shared_costs_visuals.R")

script_path <- costs_get_script_path("publisher/content/housing/02_costs/visuals/cost_index_trends.R")
ctx <- costs_build_context(script_path)
output_path <- file.path(ctx$output_dir, "cost_index_trends.png")

costs_load_visual_library(ctx$foundations_dir, chart_types = c("line"))

con <- costs_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

line_raw <- costs_run_sql_file(con, ctx$sql_dir, "cost_index_trends.sql")
line_df <- prep_line(
  line_raw,
  config = list(
    question_id = "cost_index_trends",
    time_window = "2019_to_2024_index",
    metric_id = "indexed_cost_level",
    variant = "indexed",
    base_period = 2019,
    period_min = 2019,
    period_max = 2024
  )
)

line_plot <- render_line(
  line_df,
  config = list(
    title = "Rents and home values both climbed sharply from 2019 to 2024",
    subtitle = paste(
      "Indexed to 2019 = 100 | Facets compare the national path with the housing-unit-weighted major-CBSA average",
      "| Home values rose faster than rents in both views"
    ),
    output_mode = "presentation",
    facet_by = "group",
    legend_position = "bottom",
    show_points = TRUE,
    color_mode = "geo_name",
    label_style = "number",
    label_accuracy = 1,
    start_at_zero = FALSE,
    y_limits = c(95, NA),
    x_breaks = 2019:2024,
    caption_side_note = "The major-metro series uses the temporary major-CBSA 100k flag and housing-unit-weighted averages."
  )
)

costs_save_plot(
  line_plot,
  output_path = output_path,
  width = 10.8,
  height = 7.4
)

message(sprintf("Saved %s", output_path))
