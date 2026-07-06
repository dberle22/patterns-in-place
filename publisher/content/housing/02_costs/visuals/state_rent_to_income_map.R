#!/usr/bin/env Rscript

# This visual build script owns one deliverable:
# a production-ready PNG for the Costs section's opening affordability map.
# The script mirrors the Vacancy production pattern so the section stays easy to
# rerun and review visual by visual.

source("publisher/content/housing/02_costs/visuals/_shared_costs_visuals.R")

script_path <- costs_get_script_path("publisher/content/housing/02_costs/visuals/state_rent_to_income_map.R")
ctx <- costs_build_context(script_path)
output_path <- file.path(ctx$output_dir, "state_rent_to_income_map.png")

costs_load_visual_library(ctx$foundations_dir, chart_types = c("choropleth"))

con <- costs_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

states_sf <- costs_load_contiguous_states_context(con)
contiguous_us_outline <- costs_load_contiguous_us_outline(states_sf)
standard_contiguous_context <- build_map_context_layers(
  us_outline = contiguous_us_outline,
  state_outlines = states_sf
)

state_map_raw <- costs_run_sql_file(con, ctx$sql_dir, "state_rent_to_income_map.sql")
state_map_df <- prep_choropleth(
  state_map_raw,
  config = list(
    question_id = "cost_rent_to_income_state_map",
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
    title = "State rent-to-income ratios in 2024",
    subtitle = paste(
      "Lower 48 states and DC, 2024 snapshot | Fill = annualized median rent as a share of household income",
      "| This opening view sets the national affordability map before the metro cuts"
    ),
    fill_label = "Rent-to-income (%)",
    legend_title = "Rent-to-income (%)",
    trim_quantiles = c(0.02, 0.98),
    show_us_outline = FALSE,
    show_state_outlines = FALSE,
    context_layers = standard_contiguous_context,
    caption_side_note = "The map excludes Alaska, Hawaii, and Puerto Rico so the contiguous-US affordability pattern reads clearly at article scale."
  )
)

costs_save_plot(
  state_map_plot,
  output_path = output_path,
  width = 10.5,
  height = 6.8
)

message(sprintf("Saved %s", output_path))
