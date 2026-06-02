# Highlight + Context Map render tests with question-specific DuckDB queries.

if (file.exists(".Renviron")) readRenviron(".Renviron")

source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_highlight_context_map.R")
source("visual_library/shared/render/render_highlight_context_map.R")

run_highlight_context_query <- function(con, sql_path) {
  sql <- read_sql_file(sql_path)
  DBI::dbGetQuery(con, sql)
}

assert_highlight_context_contract <- function(data, question_id) {
  validation <- validate_highlight_context_map_contract(data)
  if (isTRUE(validation$pass)) {
    return(invisible(validation))
  }

  stop(
    sprintf(
      "Highlight + context contract validation failed for %s. Missing required: %s. Rows: %s",
      question_id,
      paste(validation$missing_required, collapse = ", "),
      validation$rows
    )
  )
}

save_highlight_context_plot <- function(plot, output_dir, filename, width = 11, height = 7) {
  path <- file.path(output_dir, filename)
  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 300, bg = "white")
  path
}

load_contiguous_states_context <- function(con) {
  states_sql <- paste(
    "SELECT state_abbr, state_name, ST_AsText(geom) AS geom_wkt",
    "FROM geo.states",
    "WHERE state_abbr NOT IN ('AK', 'HI', 'PR')"
  )
  states_raw <- DBI::dbGetQuery(con, states_sql)
  sf::st_as_sf(states_raw, wkt = "geom_wkt", crs = 4326)
}

load_contiguous_us_outline <- function(states_sf) {
  outline_geom <- sf::st_union(states_sf)
  sf::st_sf(
    data.frame(layer = "contiguous_us"),
    geometry = sf::st_sfc(outline_geom, crs = sf::st_crs(states_sf))
  )
}

run_highlight_context_map_tests <- function() {
  output_dir <- "visual_library/charts/highlight_context_map/sample_output"
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  con <- connect_metro_duckdb(read_only = TRUE)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)
  try(DBI::dbExecute(con, "LOAD spatial"), silent = TRUE)

  contiguous_states <- load_contiguous_states_context(con)
  contiguous_us_outline <- load_contiguous_us_outline(contiguous_states)
  standard_contiguous_context <- build_map_context_layers(
    us_outline = contiguous_us_outline,
    state_outlines = contiguous_states
  )

  outputs <- c()

  # Query block: target CBSA locator
  q1_path <- "visual_library/charts/highlight_context_map/sample_sql/q1_target_cbsa_locator.sql"
  q1_raw <- run_highlight_context_query(con, q1_path)
  assert_highlight_context_contract(q1_raw, "highlight_target_locator")

  # Prep block
  q1_df <- prep_highlight_context_map(
    q1_raw,
    config = list(
      question_id = "highlight_target_locator",
      time_window = "2024_locator",
      variant = "focus_only",
      require_single_time_window = TRUE
    )
  )

  # Render block
  q1_plot <- render_highlight_context_map(
    q1_df,
    config = list(
      variant = "focus_only",
      composition_preset = "national_compact",
      output_mode = "presentation",
      title = "Atlanta in the national CBSA footprint",
      subtitle = paste(
        "Blue polygon = Atlanta-Sandy Springs-Roswell, GA | Gray polygons = other contiguous-US CBSAs",
        "| State outlines orient the reader; no metric is encoded in this locator view"
      ),
      context_layers = standard_contiguous_context,
      show_us_outline = TRUE,
      show_state_outlines = TRUE,
      context_fill = "#DDE6EF",
      border_color = "#CAD5E0",
      border_linewidth = 0.18,
      label_field = "label_text",
      caption_side_note = "Use this as an orientation map: it answers where the target market is in the national metro system, not whether it is outperforming peers.",
      caption_wrap_width = 120
    )
  )

  # Export path
  outputs["highlight_target_locator"] <- save_highlight_context_plot(
    q1_plot,
    output_dir,
    "highlight_context_q1_target_locator.png",
    width = 11.8,
    height = 7.6
  )

  # Query block: target CBSA tract affordability outlier proxy
  q2_path <- "visual_library/charts/highlight_context_map/sample_sql/q2_target_cbsa_outlier_proxy.sql"
  q2_raw <- run_highlight_context_query(con, q2_path)
  assert_highlight_context_contract(q2_raw, "highlight_zcta_outliers")

  # Prep block
  q2_df <- prep_highlight_context_map(
    q2_raw,
    config = list(
      question_id = "highlight_zcta_outliers",
      time_window = "2024_snapshot",
      variant = "binned",
      require_single_time_window = TRUE
    )
  )
  q2_df$bin <- cut(
    q2_df$metric_value,
    breaks = stats::quantile(q2_df$metric_value, probs = seq(0, 1, by = 0.2), na.rm = TRUE, names = FALSE, type = 7),
    include.lowest = TRUE,
    labels = c("Q1", "Q2", "Q3", "Q4", "Q5")
  )

  # Render block
  q2_plot <- render_highlight_context_map(
    q2_df,
    config = list(
      variant = "binned",
      composition_preset = "local_focus",
      output_mode = "presentation",
      title = "Within Atlanta, which small areas read as affordability outliers?",
      subtitle = paste(
        "Atlanta-Sandy Springs-Roswell tracts, 2024 snapshot | Fill = quintile of home value to household income ratio",
        "| Magenta outline marks the top 5% of tract ratios as the current proxy for the intended ZCTA outlier view"
      ),
      fill_field = "bin",
      legend_title = "Ratio quintile",
      focus_legend_title = "Focus layer",
      highlight_outline_color = "#D81B60",
      highlight_outline_linewidth = 0.26,
      highlight_halo_linewidth = 0.48,
      border_color = "#EEF2F6",
      border_linewidth = 0.08,
      caption_side_note = "The library does not yet have a reviewable ZCTA geometry layer, so this canonical outlier sample currently uses tract geometry as the local proxy.",
      caption_wrap_width = 120
    )
  )

  # Export path
  outputs["highlight_zcta_outliers"] <- save_highlight_context_plot(
    q2_plot,
    output_dir,
    "highlight_context_q2_target_outlier_proxy.png",
    width = 9.2,
    height = 8.3
  )

  # Query block: neighbor county growth context
  q3_path <- "visual_library/charts/highlight_context_map/sample_sql/q3_neighbor_growth_context.sql"
  q3_raw <- run_highlight_context_query(con, q3_path)
  assert_highlight_context_contract(q3_raw, "highlight_neighbor_growth")

  # Prep block
  q3_df <- prep_highlight_context_map(
    q3_raw,
    config = list(
      question_id = "highlight_neighbor_growth",
      time_window = "2014_to_2024_growth",
      variant = "continuous",
      require_single_time_window = TRUE
    )
  )

  # Render block
  q3_plot <- render_highlight_context_map(
    q3_df,
    config = list(
      variant = "continuous",
      composition_preset = "local_focus",
      output_mode = "presentation",
      title = "Do Fulton County's neighbors show a similar growth pattern?",
      subtitle = paste(
        "Georgia counties, 2014-2024 growth | Fill = 10-year population growth rate",
        "| Charcoal outline marks touching counties and magenta outline marks Fulton County"
      ),
      fill_label = "10-year growth",
      legend_title = "10-year growth",
      focus_legend_title = "Focus layer",
      highlight_outline_color = "#D81B60",
      highlight_outline_linewidth = 1.08,
      neighbor_outline_color = "#111827",
      neighbor_outline_linewidth = 0.7,
      outline_halo_linewidth_add = 0.55,
      trim_quantiles = c(0.02, 0.98),
      caption_side_note = "Using the full Georgia county context keeps the neighbor ring interpretable without losing the statewide pattern around metro Atlanta.",
      caption_wrap_width = 120
    )
  )

  # Export path
  outputs["highlight_neighbor_growth"] <- save_highlight_context_plot(
    q3_plot,
    output_dir,
    "highlight_context_q3_neighbor_growth.png",
    width = 9.8,
    height = 8.4
  )

  # Query block: adjacent county rent burden comparison
  q4_path <- "visual_library/charts/highlight_context_map/sample_sql/q4_adjacent_rent_burden.sql"
  q4_raw <- run_highlight_context_query(con, q4_path)
  assert_highlight_context_contract(q4_raw, "highlight_adjacent_rent_burden")

  # Prep block
  q4_df <- prep_highlight_context_map(
    q4_raw,
    config = list(
      question_id = "highlight_adjacent_rent_burden",
      time_window = "2024_snapshot",
      variant = "continuous",
      require_single_time_window = TRUE
    )
  )

  # Render block
  q4_plot <- render_highlight_context_map(
    q4_df,
    config = list(
      variant = "continuous",
      composition_preset = "local_focus",
      output_mode = "presentation",
      title = "How does Fulton County compare to adjacent counties on rent burden?",
      subtitle = paste(
        "Georgia counties, 2024 snapshot | Fill = renter households spending 30%+ of income on rent",
        "| Neighbor ring helps compare the target against the immediately adjacent housing context"
      ),
      fill_label = "Rent burden",
      legend_title = "Rent burden",
      focus_legend_title = "Focus layer",
      highlight_outline_color = "#D81B60",
      highlight_outline_linewidth = 1.08,
      neighbor_outline_color = "#111827",
      neighbor_outline_linewidth = 0.7,
      outline_halo_linewidth_add = 0.55,
      trim_quantiles = c(0.02, 0.98),
      caption_side_note = "This version uses the same focus treatment as the growth map so the only major change between the two views is the metric itself.",
      caption_wrap_width = 120
    )
  )

  # Export path
  outputs["highlight_adjacent_rent_burden"] <- save_highlight_context_plot(
    q4_plot,
    output_dir,
    "highlight_context_q4_adjacent_rent_burden.png",
    width = 9.8,
    height = 8.4
  )

  # Query block: shortlisted markets
  q5_path <- "visual_library/charts/highlight_context_map/sample_sql/q5_sweet_spot_shortlist.sql"
  q5_raw <- run_highlight_context_query(con, q5_path)
  assert_highlight_context_contract(q5_raw, "highlight_shortlist_geography")

  # Prep block
  q5_df <- prep_highlight_context_map(
    q5_raw,
    config = list(
      question_id = "highlight_shortlist_geography",
      time_window = "2024_shortlist",
      variant = "focus_only",
      require_single_time_window = TRUE
    )
  )

  # Render block
  q5_plot <- render_highlight_context_map(
    q5_df,
    config = list(
      variant = "focus_only",
      composition_preset = "national_compact",
      output_mode = "presentation",
      title = "Shortlisted markets cluster in the Southeast, with Austin set apart",
      subtitle = paste(
        "Blue polygons = Austin, Charlotte, Jacksonville, Nashville, and Raleigh | Gray polygons = other contiguous-US CBSAs",
        "| The map answers spatial clustering only; no performance metric is encoded"
      ),
      context_layers = standard_contiguous_context,
      show_us_outline = TRUE,
      show_state_outlines = TRUE,
      context_fill = "#DDE6EF",
      border_color = "#CAD5E0",
      border_linewidth = 0.18,
      label_field = "label_text",
      caption_side_note = "Use this as a geography-of-the-shortlist view: it shows whether selected markets are regionally clustered or geographically dispersed.",
      caption_wrap_width = 120
    )
  )

  # Export path
  outputs["highlight_shortlist_geography"] <- save_highlight_context_plot(
    q5_plot,
    output_dir,
    "highlight_context_q5_shortlist_geography.png",
    width = 11.8,
    height = 7.6
  )

  outputs
}

outputs <- run_highlight_context_map_tests()
print(outputs)
