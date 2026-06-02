# Choropleth chart render tests with question-specific DuckDB queries.

if (file.exists(".Renviron")) readRenviron(".Renviron")

source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_choropleth.R")
source("visual_library/shared/render/render_choropleth.R")

run_choropleth_query <- function(con, sql_path) {
  sql <- read_sql_file(sql_path)
  DBI::dbGetQuery(con, sql)
}

assert_choropleth_contract <- function(data, question_id) {
  validation <- validate_choropleth_contract(data)
  if (isTRUE(validation$pass)) {
    return(invisible(validation))
  }

  stop(
    sprintf(
      "Choropleth contract validation failed for %s. Missing required: %s. Rows: %s",
      question_id,
      paste(validation$missing_required, collapse = ", "),
      validation$rows
    )
  )
}

save_choropleth_plot <- function(plot, output_dir, filename, width = 11, height = 7) {
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

run_choropleth_tests <- function() {
  output_dir <- "visual_library/charts/choropleth/sample_output"
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

  # Query block: county rent burden clusters
  q1_path <- "visual_library/charts/choropleth/sample_sql/q1_county_rent_burden_clusters.sql"
  q1_raw <- run_choropleth_query(con, q1_path)
  assert_choropleth_contract(q1_raw, "map_rent_burden_clusters")

  # Prep block
  q1_df <- prep_choropleth(
    q1_raw,
    config = list(
      question_id = "map_rent_burden_clusters",
      time_window = "2024_snapshot",
      variant = "continuous"
    )
  )

  # Render block
  q1_plot <- render_choropleth(
    q1_df,
    config = list(
      variant = "continuous",
      output_mode = "presentation",
      title = "Where are rent burden clusters most concentrated across counties?",
      subtitle = paste(
        "Contiguous 48 states plus DC counties, 2024 snapshot | Fill = renter households spending 30%+ of income on rent",
        "| Use this first-pass national surface to spot regional clusters before drilling into local markets"
      ),
      fill_label = "Rent burden",
      legend_title = "Rent burden",
      trim_quantiles = c(0.02, 0.98),
      map_extent = "contiguous_us",
      show_us_outline = FALSE,
      show_state_outlines = FALSE,
      caption_side_note = "The map is limited to the contiguous 48 plus DC and trimmed to the 2nd-98th percentile range so moderate county differences remain readable.",
      caption_wrap_width = 120
    )
  )

  # Export path
  outputs["map_rent_burden_clusters"] <- save_choropleth_plot(
    q1_plot,
    output_dir,
    "choropleth_q1_rent_burden_clusters.png",
    width = 12,
    height = 8
  )

  q1_compact_plot <- render_choropleth(
    q1_df,
    config = list(
      variant = "continuous",
      composition_preset = "national_compact",
      output_mode = "presentation",
      title = "Rent burden clusters across counties",
      subtitle = "Contiguous 48 states plus DC counties, 2024 snapshot | National compact composition preset",
      fill_label = "Rent burden",
      legend_title = "Rent burden",
      trim_quantiles = c(0.02, 0.98),
      show_us_outline = FALSE,
      show_state_outlines = FALSE,
      caption_side_note = "Preset demo: national_compact keeps a consistent contiguous-US extent with tighter margins for national map review.",
      caption_wrap_width = 110
    )
  )
  outputs["preset_national_compact_county"] <- save_choropleth_plot(
    q1_compact_plot,
    output_dir,
    "choropleth_preset_national_compact_county.png",
    width = 10.5,
    height = 6.8
  )

  # Query block: county population growth corridors
  q2_path <- "visual_library/charts/choropleth/sample_sql/q2_county_population_growth_corridors.sql"
  q2_raw <- run_choropleth_query(con, q2_path)
  assert_choropleth_contract(q2_raw, "map_population_growth_corridors")

  # Prep block
  q2_df <- prep_choropleth(
    q2_raw,
    config = list(
      question_id = "map_population_growth_corridors",
      time_window = "2014_to_2024_growth",
      variant = "continuous"
    )
  )

  # Render block
  q2_plot <- render_choropleth(
    q2_df,
    config = list(
      variant = "continuous",
      output_mode = "presentation",
      title = "Which county growth patterns look like corridors instead of isolated spikes?",
      subtitle = "Contiguous 48 states plus DC counties, 2014-2024 growth | Fill = 10-year population growth rate",
      fill_label = "10-year growth",
      legend_title = "10-year growth",
      trim_quantiles = c(0.02, 0.98),
      map_extent = "contiguous_us",
      show_us_outline = FALSE,
      show_state_outlines = FALSE,
      caption_side_note = "Continuous fill helps us read regional corridors and growth belts across the contiguous US before deciding whether a binned version is easier to explain.",
      caption_wrap_width = 120
    )
  )

  # Export path
  outputs["map_population_growth_corridors"] <- save_choropleth_plot(
    q2_plot,
    output_dir,
    "choropleth_q2_population_growth_corridors.png",
    width = 12,
    height = 8
  )

  # Query block: within-CBSA affordability outliers
  q3_path <- "visual_library/charts/choropleth/sample_sql/q3_tract_affordability_outliers_within_cbsa.sql"
  q3_raw <- run_choropleth_query(con, q3_path)
  assert_choropleth_contract(q3_raw, "map_affordability_outliers_within_cbsa")

  # Prep block
  q3_df <- prep_choropleth(
    q3_raw,
    config = list(
      question_id = "map_affordability_outliers_within_cbsa",
      time_window = "2024_snapshot",
      variant = "binned",
      bins = seq(0, 1, by = 0.2),
      bin_labels = c("Q1", "Q2", "Q3", "Q4", "Q5")
    )
  )

  # Render block
  q3_plot <- render_choropleth(
    q3_df,
    config = list(
      variant = "binned",
      output_mode = "presentation",
      title = "Within Atlanta, which tracts look like affordability outliers?",
      subtitle = paste(
        "Atlanta-Sandy Springs-Roswell tracts, 2024 snapshot | Fill = quintile of home value to household income ratio",
        "| Yellow outline marks the top 5% of tract ratios"
      ),
      fill_field = "bin",
      legend_title = "Ratio quintile",
      highlight_outline_color = "#F0C808",
      highlight_outline_linewidth = 0.35,
      map_extent = "data",
      show_us_outline = FALSE,
      show_state_outlines = FALSE,
      caption_side_note = "This first pass uses tract geometry as the local small-area proxy until a ZCTA geometry layer is added.",
      caption_wrap_width = 120
    )
  )

  # Export path
  outputs["map_affordability_outliers_within_cbsa"] <- save_choropleth_plot(
    q3_plot,
    output_dir,
    "choropleth_q3_affordability_outliers_within_cbsa.png",
    width = 10,
    height = 8
  )

  q3_local_focus_plot <- render_choropleth(
    q3_df,
    config = list(
      variant = "binned",
      composition_preset = "local_focus",
      output_mode = "presentation",
      title = "Atlanta tract affordability outliers",
      subtitle = "Local focus composition preset | Fill = quintile of home value to household income ratio",
      fill_field = "bin",
      legend_title = "Ratio quintile",
      highlight_outline_color = "#F0C808",
      highlight_outline_linewidth = 0.35,
      show_us_outline = FALSE,
      show_state_outlines = FALSE,
      caption_side_note = "Preset demo: local_focus fits the map tightly to the market footprint with light padding for labels and outlines.",
      caption_wrap_width = 110
    )
  )
  outputs["preset_local_focus_atlanta"] <- save_choropleth_plot(
    q3_local_focus_plot,
    output_dir,
    "choropleth_preset_local_focus_atlanta.png",
    width = 8.6,
    height = 8.4
  )

  # Query block: benchmark-relative metros
  q4_path <- "visual_library/charts/choropleth/sample_sql/q4_cbsa_benchmark_relative_metros.sql"
  q4_raw <- run_choropleth_query(con, q4_path)
  assert_choropleth_contract(q4_raw, "map_benchmark_relative_metros")

  # Prep block
  q4_df <- prep_choropleth(
    q4_raw,
    config = list(
      question_id = "map_benchmark_relative_metros",
      time_window = "2023_snapshot",
      variant = "diverging"
    )
  )
  q4_benchmark <- unique(stats::na.omit(q4_df$benchmark_value))[[1]]
  q4_benchmark_label <- format_value_vector(q4_benchmark, style = "dollar", accuracy = 1, compact = TRUE)

  # Render block
  q4_plot <- render_choropleth(
    q4_df,
    config = list(
      variant = "diverging",
      output_mode = "presentation",
      title = "Which metros sit above or below the 2023 population-weighted CBSA benchmark?",
      subtitle = paste(
        "Contiguous 48 states plus DC CBSAs, 2023 snapshot | Benchmark =",
        q4_benchmark_label,
        "population-weighted real per capita income across mapped CBSAs | Fill shows each metro's dollar delta from that benchmark"
      ),
      fill_label = "Benchmark delta",
      legend_title = "Delta vs benchmark",
      show_highlight_outline = FALSE,
      context_layers = standard_contiguous_context,
      map_extent = "contiguous_us",
      show_us_outline = TRUE,
      show_state_outlines = TRUE,
      border_color = "#EEF2F6",
      border_linewidth = 0.18,
      trim_quantiles = c(0.02, 0.98),
      caption_side_note = "The source table does not currently publish a populated US real-income row, so this benchmark uses the 2023 population-weighted average across mapped CBSAs.",
      caption_wrap_width = 120
    )
  )

  # Export path
  outputs["map_benchmark_relative_metros"] <- save_choropleth_plot(
    q4_plot,
    output_dir,
    "choropleth_q4_benchmark_relative_metros.png",
    width = 12,
    height = 8
  )

  # Query block: growth window comparison
  q5_path <- "visual_library/charts/choropleth/sample_sql/q5_cbsa_growth_window_compare.sql"
  q5_raw <- run_choropleth_query(con, q5_path)
  assert_choropleth_contract(q5_raw, "map_growth_window_compare")

  # Prep block
  q5_df <- prep_choropleth(
    q5_raw,
    config = list(
      question_id = "map_growth_window_compare",
      variant = "continuous",
      require_single_time_window = FALSE
    )
  )

  # Render block
  q5_plot <- render_choropleth(
    q5_df,
    config = list(
      variant = "continuous",
      output_mode = "presentation",
      title = "How do CBSA growth patterns change when the window changes?",
      subtitle = "Facet comparison of 5-year versus 10-year population growth across contiguous 48 plus DC metros",
      fill_label = "Growth rate",
      legend_title = "Growth rate",
      context_layers = standard_contiguous_context,
      map_extent = "contiguous_us",
      show_us_outline = TRUE,
      show_state_outlines = TRUE,
      border_color = "#EEF2F6",
      border_linewidth = 0.14,
      facet_by = "time_window",
      facet_ncol = 2,
      trim_quantiles = c(0.02, 0.98),
      caption_side_note = "Fixed styling across facets makes it easier to see which metros look cyclical versus consistently fast-growing.",
      caption_wrap_width = 120
    )
  )

  # Export path
  outputs["map_growth_window_compare"] <- save_choropleth_plot(
    q5_plot,
    output_dir,
    "choropleth_q5_growth_window_compare.png",
    width = 13,
    height = 7.5
  )

  q5_facet_preset_plot <- render_choropleth(
    q5_df,
    config = list(
      variant = "continuous",
      composition_preset = "facet_national",
      output_mode = "presentation",
      title = "CBSA growth windows with facet-national composition",
      subtitle = "5-year versus 10-year population growth across contiguous 48 plus DC metros",
      fill_label = "Growth rate",
      legend_title = "Growth rate",
      context_layers = standard_contiguous_context,
      show_us_outline = TRUE,
      show_state_outlines = TRUE,
      border_color = "#EEF2F6",
      facet_by = "time_window",
      facet_ncol = 2,
      trim_quantiles = c(0.02, 0.98),
      caption_side_note = "Preset demo: facet_national keeps shared extent and leaner framing so national comparisons still read at smaller panel size.",
      caption_wrap_width = 110
    )
  )
  outputs["preset_facet_national_growth"] <- save_choropleth_plot(
    q5_facet_preset_plot,
    output_dir,
    "choropleth_preset_facet_national_growth.png",
    width = 12.2,
    height = 6.6
  )

  outputs
}

outputs <- run_choropleth_tests()
print(outputs)
