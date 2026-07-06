#!/usr/bin/env Rscript

# This map translates the momentum-versus-strain logic into geography. It does
# not try to show every component at once; instead, it maps the overlap between
# hot recent momentum and strong affordability strain, which is the clearest
# visual slice of the broader overheating heuristic.

source("publisher/content/housing/04_overheating/visuals/_shared_overheating_visuals.R")

script_path <- overheating_get_script_path("publisher/content/housing/04_overheating/visuals/cbsa_overheating_bivariate_map.R")
ctx <- overheating_build_context(script_path)
output_path <- file.path(ctx$output_dir, "cbsa_overheating_bivariate_map.png")

overheating_load_visual_library(ctx$foundations_dir, chart_types = c("bivariate_choropleth"))

con <- overheating_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

states_sf <- overheating_load_contiguous_states_context(con)
contiguous_us_outline <- overheating_load_contiguous_us_outline(states_sf)
standard_contiguous_context <- build_map_context_layers(
  us_outline = contiguous_us_outline,
  state_outlines = states_sf
)

map_raw <- overheating_run_sql_file(con, ctx$sql_dir, "cbsa_overheating_bivariate_map.sql")
map_df <- prep_bivariate_choropleth(
  map_raw,
  config = list(
    question_id = "overheating_bivariate_map",
    time_window = "2024_snapshot",
    bin_method = "quantile",
    n_bins = 3,
    require_single_geo_level = TRUE,
    require_single_time_window = TRUE
  )
)

map_plot <- render_bivariate_choropleth(
  map_df,
  config = list(
    output_mode = "presentation",
    composition_preset = "national_compact",
    title = "The darkest metros are the ones combining hot momentum with high strain",
    subtitle = paste(
      "Major CBSAs, 2024 | X = momentum component, Y = strain component",
      "| The map is designed to show where both pressures overlap geographically"
    ),
    map_extent = "contiguous_us",
    context_layers = standard_contiguous_context,
    show_bivariate_key = TRUE,
    caption_side_note = "Each axis is quantile-binned across the 2024 major-CBSA universe. Dark high-high metros are not necessarily the most expensive in level terms; they are the most jointly strained on these two dimensions."
  )
)

overheating_save_plot(
  map_plot,
  output_path = output_path,
  width = 12,
  height = 7.6
)

message(sprintf("Saved %s", output_path))
