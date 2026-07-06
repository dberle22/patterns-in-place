#!/usr/bin/env Rscript

# This visual build script owns one deliverable:
# a production-ready PNG for the Vacancy section's opening state choropleth.
# The script stays intentionally narrow so it can become the reusable pattern
# for the rest of the section's standalone visual builds.

source("publisher/content/housing/01_vacancy/visuals/_shared_vacancy_visuals.R")

script_path <- vacancy_get_script_path("publisher/content/housing/01_vacancy/visuals/state_vacancy_map.R")
ctx <- vacancy_build_context(script_path)
output_path <- file.path(ctx$output_dir, "state_vacancy_map.png")

vacancy_load_visual_library(ctx$foundations_dir, chart_types = c("choropleth"))

con <- vacancy_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

states_sf <- vacancy_load_contiguous_states_context(con)
contiguous_us_outline <- vacancy_load_contiguous_us_outline(states_sf)
standard_contiguous_context <- build_map_context_layers(
  us_outline = contiguous_us_outline,
  state_outlines = states_sf
)

state_map_raw <- vacancy_run_sql_file(con, ctx$sql_dir, "state_vacancy_map.sql")
state_map_df <- prep_choropleth(
  state_map_raw,
  config = list(
    question_id = "vacancy_state_map",
    time_window = "2024_snapshot",
    variant = "continuous"
  )
)

state_map_plot <- render_choropleth(
  state_map_df,
  config = list(
    variant = "continuous",
    composition_preset = "national_compact",
    output_mode = "presentation",
    title = "State housing vacancy rates in 2024",
    subtitle = paste(
      "Contiguous 48 states, 2024 snapshot | Fill = vacancy rate (%)",
      "| This opening view is intended to establish the broad national pattern before metro cuts"
    ),
    fill_label = "Vacancy rate (%)",
    legend_title = "Vacancy rate (%)",
    trim_quantiles = c(0.02, 0.98),
    show_us_outline = FALSE,
    show_state_outlines = FALSE,
    context_layers = standard_contiguous_context,
    caption_side_note = "The map excludes Alaska, Hawaii, and Puerto Rico so the contiguous-US pattern reads clearly at article scale."
  )
)

vacancy_save_plot(
  state_map_plot,
  output_path = output_path,
  width = 10.5,
  height = 6.8
)

message(sprintf("Saved %s", output_path))
