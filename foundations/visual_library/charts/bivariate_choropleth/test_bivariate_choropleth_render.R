# Bivariate choropleth sample runner.
#
# How to use this file:
# - Run the whole file from the repo root with:
#     Rscript visual_library/charts/bivariate_choropleth/test_bivariate_choropleth_render.R
# - Each canonical question follows the same four-step pattern:
#     1. Query block: read one SQL file from sample_sql/.
#     2. Contract block: fail early if required fields are missing.
#     3. Prep block: filter rows, coerce geometry, and compute bivariate bins.
#     4. Render/export block: draw a PNG into sample_output/.
# - To add a new sample, copy one existing question block and change only:
#     SQL path, question_id, time_window, title/subtitle/caption, and filename.
# - The shared behavior lives in prep_bivariate_choropleth.R and
#   render_bivariate_choropleth.R; keep one-off logic here only when it is
#   specific to a review sample.

if (file.exists(".Renviron")) readRenviron(".Renviron")

source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_bivariate_choropleth.R")
source("visual_library/shared/render/render_bivariate_choropleth.R")

run_bivariate_choropleth_query <- function(con, sql_path) {
  sql <- read_sql_file(sql_path)
  DBI::dbGetQuery(con, sql)
}

assert_bivariate_choropleth_contract <- function(data, question_id) {
  validation <- validate_bivariate_choropleth_contract(data)
  if (isTRUE(validation$pass)) {
    return(invisible(validation))
  }

  stop(
    sprintf(
      "Bivariate choropleth contract validation failed for %s. Missing required: %s. Rows: %s",
      question_id,
      paste(validation$missing_required, collapse = ", "),
      validation$rows
    )
  )
}

save_bivariate_choropleth_plot <- function(plot, output_dir, filename, width = 12, height = 8) {
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

run_bivariate_choropleth_tests <- function() {
  # All review artifacts for this chart type go here. Avoid adding a second
  # output/ folder unless there is a separate publishing workflow.
  output_dir <- "visual_library/charts/bivariate_choropleth/sample_output"
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  # The sample SQL is DuckDB-backed. connect_metro_duckdb() expects DATA to
  # point at the project data root containing duckdb/metro_deep_dive.duckdb.
  con <- connect_metro_duckdb(read_only = TRUE)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)
  try(DBI::dbExecute(con, "LOAD spatial"), silent = TRUE)

  # National maps borrow the same context-layer pattern as choropleth:
  # light state outlines plus a contiguous-US outline behind the mapped layer.
  contiguous_states <- load_contiguous_states_context(con)
  contiguous_us_outline <- load_contiguous_us_outline(contiguous_states)
  standard_contiguous_context <- build_map_context_layers(
    us_outline = contiguous_us_outline,
    state_outlines = contiguous_states
  )

  outputs <- c()

  # Query block: counties high growth and relatively affordable
  q1_path <- "visual_library/charts/bivariate_choropleth/sample_sql/q1_county_growth_affordability.sql"
  q1_raw <- run_bivariate_choropleth_query(con, q1_path)
  assert_bivariate_choropleth_contract(q1_raw, "bivar_growth_affordability_counties")

  # Prep block
  q1_df <- prep_bivariate_choropleth(
    q1_raw,
    config = list(
      # question_id and time_window are the main sample filters. Keep these
      # matched to constants emitted by the SQL.
      question_id = "bivar_growth_affordability_counties",
      time_window = "2014_to_2024_growth",
      # n_bins = 3 is the default bivariate library standard: a 3x3 quantile
      # grid. Use 4 only when the story genuinely needs more classes.
      n_bins = 3
    )
  )

  # Render block
  q1_plot <- render_bivariate_choropleth(
    q1_df,
    config = list(
      # composition_preset reuses choropleth map-layout decisions:
      # national_compact, facet_national, local_focus, or none.
      composition_preset = "national_compact",
      # presentation mode increases title/caption hierarchy for review PNGs.
      output_mode = "presentation",
      title = "Where are counties growing quickly while remaining relatively affordable?",
      subtitle = "Contiguous 48 states plus DC counties, 2014-2024 | 3x3 quantile bins compare population growth with inverse value-to-income affordability",
      context_layers = standard_contiguous_context,
      show_us_outline = TRUE,
      show_state_outlines = TRUE,
      border_color = "#EEF2F6",
      border_linewidth = 0.1,
      caption_side_note = "High-high cells identify counties in the top growth and affordability bins within the mapped county universe.",
      caption_wrap_width = 115
    )
  )

  # Export path
  outputs["bivar_growth_affordability_counties"] <- save_bivariate_choropleth_plot(
    q1_plot,
    output_dir,
    "bivariate_choropleth_q1_growth_affordability_counties.png",
    # Export dimensions are intentionally set per sample so maps and the
    # bivariate key both remain legible in review.
    width = 12.4,
    height = 7.4
  )

  # Query block: small-area stress-zone proxy for ZCTA question
  q2_path <- "visual_library/charts/bivariate_choropleth/sample_sql/q2_tract_stress_zone_proxy.sql"
  q2_raw <- run_bivariate_choropleth_query(con, q2_path)
  assert_bivariate_choropleth_contract(q2_raw, "bivar_stress_zone_zctas")

  # Prep block
  q2_df <- prep_bivariate_choropleth(
    q2_raw,
    config = list(
      question_id = "bivar_stress_zone_zctas",
      time_window = "2024_snapshot",
      # This sample uses tract geometry as a temporary ZCTA proxy; see
      # bivariate_choropleth_decisions.md for the replacement decision.
      n_bins = 3
    )
  )

  # Render block
  q2_plot <- render_bivariate_choropleth(
    q2_df,
    config = list(
      # local_focus computes a tight map extent from the sf geometry.
      composition_preset = "local_focus",
      output_mode = "presentation",
      title = "Where do high rent burden and lower incomes overlap in Atlanta?",
      subtitle = "Atlanta tracts, 2024 snapshot | Tract proxy for the ZCTA stress-zone question until ZCTA geometry is available",
      border_color = "#F7FAFC",
      border_linewidth = 0.08,
      caption_side_note = "The y-axis is negative median household income, so higher y bins mean lower incomes.",
      caption_wrap_width = 110
    )
  )

  # Export path
  outputs["bivar_stress_zone_zctas"] <- save_bivariate_choropleth_plot(
    q2_plot,
    output_dir,
    "bivariate_choropleth_q2_stress_zone_tract_proxy.png",
    width = 10.4,
    height = 8.2
  )

  # Query block: local overlap within target CBSA
  q3_path <- "visual_library/charts/bivariate_choropleth/sample_sql/q3_local_overlap_target_cbsa.sql"
  q3_raw <- run_bivariate_choropleth_query(con, q3_path)
  assert_bivariate_choropleth_contract(q3_raw, "bivar_local_overlap_target_cbsa")

  # Prep block
  q3_df <- prep_bivariate_choropleth(
    q3_raw,
    config = list(
      question_id = "bivar_local_overlap_target_cbsa",
      time_window = "2024_snapshot",
      n_bins = 3
    )
  )

  # Render block
  q3_plot <- render_bivariate_choropleth(
    q3_df,
    config = list(
      composition_preset = "local_focus",
      output_mode = "presentation",
      title = "Which Atlanta tracts combine renter cost pressure and long commutes?",
      subtitle = "Atlanta-Sandy Springs-Roswell tracts, 2024 snapshot | 3x3 quantile bins compare rent burden with mean commute time",
      border_color = "#F7FAFC",
      border_linewidth = 0.08,
      caption_side_note = "High-high cells represent tracts with both higher rent burden and longer mean travel time among Atlanta tracts.",
      caption_wrap_width = 110
    )
  )

  # Export path
  outputs["bivar_local_overlap_target_cbsa"] <- save_bivariate_choropleth_plot(
    q3_plot,
    output_dir,
    "bivariate_choropleth_q3_local_overlap_target_cbsa.png",
    width = 10.4,
    height = 8.2
  )

  # Query block: CBSA regional economic strength and affordability overlap
  q4_path <- "visual_library/charts/bivariate_choropleth/sample_sql/q4_cbsa_region_overlap.sql"
  q4_raw <- run_bivariate_choropleth_query(con, q4_path)
  assert_bivariate_choropleth_contract(q4_raw, "bivar_cbsa_region_overlap")

  # Prep block
  q4_df <- prep_bivariate_choropleth(
    q4_raw,
    config = list(
      question_id = "bivar_cbsa_region_overlap",
      time_window = "2018_to_2023_growth",
      n_bins = 3
    )
  )

  # Render block
  q4_plot <- render_bivariate_choropleth(
    q4_df,
    config = list(
      composition_preset = "national_compact",
      output_mode = "presentation",
      title = "Which metro regions combine economic strength with rent affordability?",
      subtitle = "Contiguous 48 states plus DC CBSAs, 2018-2023 | 3x3 quantile bins compare income growth with inverse rent-to-income affordability",
      context_layers = standard_contiguous_context,
      show_us_outline = TRUE,
      show_state_outlines = TRUE,
      border_color = "#EEF2F6",
      border_linewidth = 0.16,
      caption_side_note = "CBSAs are drawn with state context layers so regional clusters remain visible despite non-contiguous metro polygons.",
      caption_wrap_width = 115
    )
  )

  # Export path
  outputs["bivar_cbsa_region_overlap"] <- save_bivariate_choropleth_plot(
    q4_plot,
    output_dir,
    "bivariate_choropleth_q4_cbsa_region_overlap.png",
    width = 12.4,
    height = 7.4
  )

  # Query block: growth-window comparison
  q5_path <- "visual_library/charts/bivariate_choropleth/sample_sql/q5_county_growth_window_compare.sql"
  q5_raw <- run_bivariate_choropleth_query(con, q5_path)
  assert_bivariate_choropleth_contract(q5_raw, "bivar_growth_window_compare")

  # Prep block
  q5_df <- prep_bivariate_choropleth(
    q5_raw,
    config = list(
      question_id = "bivar_growth_window_compare",
      n_bins = 3,
      # Faceted samples intentionally allow multiple time windows.
      require_single_time_window = FALSE
    )
  )

  # Render block
  q5_plot <- render_bivariate_choropleth(
    q5_df,
    config = list(
      # facet_national keeps a shared contiguous-US extent across panels.
      composition_preset = "facet_national",
      output_mode = "presentation",
      title = "How does the growth-affordability overlap change by growth window?",
      subtitle = "County comparison across 5-year and 10-year population growth windows | Shared 3x3 quantile bins preserve cross-panel comparability",
      context_layers = standard_contiguous_context,
      show_us_outline = TRUE,
      show_state_outlines = TRUE,
      border_color = "#EEF2F6",
      border_linewidth = 0.1,
      # facet_by can be any column in the prepped data, but time_window is the
      # standard comparison field for growth-window samples.
      facet_by = "time_window",
      facet_ncol = 2,
      caption_side_note = "Both panels use the same binning universe so class changes reflect the growth window rather than a panel-specific rebasing.",
      caption_wrap_width = 115
    )
  )

  # Export path
  outputs["bivar_growth_window_compare"] <- save_bivariate_choropleth_plot(
    q5_plot,
    output_dir,
    "bivariate_choropleth_q5_growth_window_compare.png",
    width = 13.5,
    height = 7.4
  )

  outputs
}

outputs <- run_bivariate_choropleth_tests()
print(outputs)
