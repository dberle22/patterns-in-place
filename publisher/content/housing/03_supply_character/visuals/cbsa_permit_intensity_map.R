#!/usr/bin/env Rscript

# This visual opens the Supply Character section with a national metro map of
# where building activity is strongest. Bubble size is the main encoding, while
# region color acts as lightweight orientation rather than the core message.

source("publisher/content/housing/03_supply_character/visuals/_shared_supply_character_visuals.R")

script_path <- supply_get_script_path("publisher/content/housing/03_supply_character/visuals/cbsa_permit_intensity_map.R")
ctx <- supply_build_context(script_path)
output_path <- file.path(ctx$output_dir, "cbsa_permit_intensity_map.png")

supply_load_visual_library(ctx$foundations_dir, chart_types = c("proportional_symbol_map"))

con <- supply_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

states_sf <- supply_load_contiguous_states_context(con)
contiguous_us_outline <- supply_load_contiguous_us_outline(states_sf)
standard_contiguous_context <- build_map_context_layers(
  us_outline = contiguous_us_outline,
  state_outlines = states_sf
)

map_raw <- supply_run_sql_file(con, ctx$sql_dir, "cbsa_permit_intensity_map.sql")
# The proportional-symbol prep derives point-on-surface coordinates from CBSA
# polygons. sf warns that lon/lat point-on-surface coordinates are approximate,
# which is expected here because the points are only used as in-polygon bubble
# anchors rather than analytical geometry outputs.
map_df <- suppressWarnings(
  prep_proportional_symbol_map(
    map_raw,
    config = list(
      question_id = "supply_permit_intensity_map",
      time_window = "2024_snapshot",
      label_top_n = 12,
      label_strategy = "provided_or_top_n"
    )
  )
)

map_plot <- render_proportional_symbol_map(
  map_df,
  config = list(
    output_mode = "presentation",
    composition_preset = "national_compact",
    title = "New housing permits were heavily concentrated in a growth-belt set of metros",
    subtitle = paste(
      "Major CBSAs, 2024 | Bubble size = permits per 1,000 housing units",
      "| Labels call out the highest-intensity building markets"
    ),
    color_mode = "color_group",
    color_legend_title = "Region",
    legend_title = "Permits per 1,000 housing units",
    value_style = "number",
    value_accuracy = 0.1,
    size_range = c(2.5, 20),
    label_field = "geo_name",
    label_include_value = TRUE,
    show_context = TRUE,
    context_layers = standard_contiguous_context,
    context_fill = NA,
    context_color = "#D1DAE3",
    context_linewidth = 0.18,
    map_extent = "contiguous_us",
    caption_side_note = "The bubble map uses the temporary major-CBSA 100k flag and shared CBSA polygons to derive in-metro point locations."
  )
)

supply_save_plot(
  map_plot,
  output_path = output_path,
  width = 11.2,
  height = 7.4
)

message(sprintf("Saved %s", output_path))
