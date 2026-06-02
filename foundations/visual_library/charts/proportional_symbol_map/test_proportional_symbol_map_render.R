# Proportional symbol map render tests with question-specific DuckDB queries.

if (file.exists(".Renviron")) readRenviron(".Renviron")

source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_proportional_symbol_map.R")
source("visual_library/shared/render/render_proportional_symbol_map.R")

run_proportional_symbol_query <- function(con, sql_path) {
  sql <- read_sql_file(sql_path)
  DBI::dbGetQuery(con, sql)
}

assert_proportional_symbol_contract <- function(data, question_id) {
  validation <- validate_proportional_symbol_map_contract(data)
  if (isTRUE(validation$pass)) {
    return(invisible(validation))
  }

  stop(
    sprintf(
      "Proportional symbol map contract validation failed for %s. Missing required: %s. Rows: %s",
      question_id,
      paste(validation$missing_required, collapse = ", "),
      validation$rows
    )
  )
}

save_proportional_symbol_plot <- function(plot, output_dir, filename, width = 11, height = 7) {
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

load_market_county_context <- function(con, cbsa_code) {
  county_sql <- sprintf(
    paste(
      "SELECT county_geoid, county_name, geom_wkt",
      "FROM foundation.market_county_geometry",
      "WHERE cbsa_code = %s"
    ),
    DBI::dbQuoteString(con, cbsa_code)
  )
  county_raw <- DBI::dbGetQuery(con, county_sql)
  sf::st_as_sf(county_raw, wkt = "geom_wkt", crs = 4326)
}

run_proportional_symbol_map_tests <- function() {
  output_dir <- "visual_library/charts/proportional_symbol_map/sample_output"
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  con <- connect_metro_duckdb(read_only = TRUE)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)
  try(DBI::dbExecute(con, "LOAD spatial"), silent = TRUE)

  contiguous_states <- load_contiguous_states_context(con)
  contiguous_us_outline <- load_contiguous_us_outline(contiguous_states)
  # Use the same national context layers as choropleth so map-family outputs
  # share extent, boundary treatment, and visual rhythm.
  standard_contiguous_context <- build_map_context_layers(
    us_outline = contiguous_us_outline,
    state_outlines = contiguous_states
  )
  # Local-focus samples get light county outlines as orientation, not as a
  # second metric layer.
  wilmington_counties <- load_market_county_context(con, "48900")
  jacksonville_counties <- load_market_county_context(con, "27260")
  atlanta_counties <- load_market_county_context(con, "12060")

  outputs <- c()

  # Query block: CBSA population concentration
  q1_path <- "visual_library/charts/proportional_symbol_map/sample_sql/q1_cbsa_population_concentration.sql"
  q1_raw <- run_proportional_symbol_query(con, q1_path)
  assert_proportional_symbol_contract(q1_raw, "bubble_population_concentration")

  # Prep block
  q1_df <- prep_proportional_symbol_map(
    q1_raw,
    config = list(
      question_id = "bubble_population_concentration",
      time_window = "2024_snapshot",
      top_n = 80,
      label_top_n = 6,
      label_strategy = "top_n",
      require_single_time_window = TRUE
    )
  )

  # Render block
  q1_plot <- render_proportional_symbol_map(
    q1_df,
    config = list(
      composition_preset = "national_compact",
      output_mode = "presentation",
      title = "Where is metro population most concentrated?",
      subtitle = "Top 80 contiguous-US CBSAs by 2024 population | Bubble area represents total population; color groups metros by Census region",
      size_label = "Population",
      legend_title = "Population",
      value_style = "number",
      color_mode = "color_group",
      color_legend_title = "Region",
      context_layers = standard_contiguous_context,
      point_alpha = 0.74,
      label_size = 2.6,
      caption_side_note = "Top-N filtering keeps the national concentration pattern readable; labels show the six largest metros.",
      caption_wrap_width = 115
    )
  )

  # Export path
  outputs["bubble_population_concentration"] <- save_proportional_symbol_plot(
    q1_plot,
    output_dir,
    "proportional_symbol_q1_population_concentration.png",
    width = 11.4,
    height = 7.4
  )

  # Query block: county permit majority
  q2_path <- "visual_library/charts/proportional_symbol_map/sample_sql/q2_county_permit_majority.sql"
  q2_raw <- run_proportional_symbol_query(con, q2_path)
  assert_proportional_symbol_contract(q2_raw, "bubble_permit_majority_counties")

  # Prep block
  q2_df <- prep_proportional_symbol_map(
    q2_raw,
    config = list(
      question_id = "bubble_permit_majority_counties",
      time_window = "2024_snapshot",
      top_n = 70,
      label_top_n = 8,
      label_strategy = "top_n",
      require_single_time_window = TRUE
    )
  )

  # Render block
  q2_plot <- render_proportional_symbol_map(
    q2_df,
    config = list(
      composition_preset = "national_compact",
      output_mode = "presentation",
      title = "Which counties account for the largest share of new permitted units?",
      subtitle = "Top 70 contiguous-US counties by 2024 permitted housing units | Teal bubbles are counties in the cumulative first half of units after ranking",
      size_label = "Permitted units",
      legend_title = "Permitted units",
      value_style = "number",
      color_mode = "highlight",
      highlight_fill = "#0C7C78",
      comparison_fill = "#AEBECD",
      context_layers = standard_contiguous_context,
      point_alpha = 0.72,
      label_size = 2.5,
      caption_side_note = "The source is total permitted units, not a per-capita rate, so bubble sizing highlights absolute construction concentration.",
      caption_wrap_width = 115
    )
  )

  # Export path
  outputs["bubble_permit_majority_counties"] <- save_proportional_symbol_plot(
    q2_plot,
    output_dir,
    "proportional_symbol_q2_permit_majority_counties.png",
    width = 11.4,
    height = 7.4
  )

  # Query block: largest ZCTAs in Wilmington CBSA
  # This sample uses tract-weighted ZCTA coordinates until dedicated ZCTA
  # geometry is available in DuckDB.
  q3_path <- "visual_library/charts/proportional_symbol_map/sample_sql/q3_wilmington_largest_zctas.sql"
  q3_raw <- run_proportional_symbol_query(con, q3_path)
  assert_proportional_symbol_contract(q3_raw, "bubble_largest_zctas_in_cbsa")

  # Prep block
  q3_df <- prep_proportional_symbol_map(
    q3_raw,
    config = list(
      question_id = "bubble_largest_zctas_in_cbsa",
      time_window = "2024_snapshot",
      top_n = 24,
      label_top_n = 8,
      label_strategy = "top_n",
      require_single_time_window = TRUE
    )
  )

  # Render block
  q3_plot <- render_proportional_symbol_map(
    q3_df,
    config = list(
      composition_preset = "local_focus",
      output_mode = "presentation",
      title = "Within Wilmington, where are the largest ZCTA population nodes?",
      subtitle = "Wilmington, NC CBSA, 2024 snapshot | Top 24 ZCTAs; bubble area represents total population using tract-weighted ZCTA coordinates",
      size_label = "ZCTA population",
      legend_title = "Population",
      value_style = "number",
      context_data = wilmington_counties,
      context_color = "#AAB7C4",
      context_linewidth = 0.35,
      point_alpha = 0.78,
      label_top_n = 8,
      caption_side_note = "ZCTA coordinates are approximated from tract crosswalk weights because a dedicated ZCTA geometry layer is not yet materialized.",
      caption_wrap_width = 115
    )
  )

  # Export path
  outputs["bubble_largest_zctas_in_cbsa"] <- save_proportional_symbol_plot(
    q3_plot,
    output_dir,
    "proportional_symbol_q3_largest_zctas_wilmington.png",
    width = 8.8,
    height = 8.0
  )

  # Query block: retail parcel cluster proxy
  # Parcel clusters are not materialized yet, so the query intentionally uses
  # high-scoring target-zone tracts as a reviewable proxy.
  q4_path <- "visual_library/charts/proportional_symbol_map/sample_sql/q4_jacksonville_retail_parcel_cluster_proxy.sql"
  q4_raw <- run_proportional_symbol_query(con, q4_path)
  assert_proportional_symbol_contract(q4_raw, "bubble_retail_parcel_clusters")

  # Prep block
  q4_df <- prep_proportional_symbol_map(
    q4_raw,
    config = list(
      question_id = "bubble_retail_parcel_clusters",
      time_window = "2024_snapshot",
      top_n = 35,
      label_top_n = 8,
      label_strategy = "top_n",
      require_single_time_window = TRUE
    )
  )

  # Render block
  q4_plot <- render_proportional_symbol_map(
    q4_df,
    config = list(
      composition_preset = "local_focus",
      output_mode = "presentation",
      title = "Where do Jacksonville retail target-zone proxies cluster?",
      subtitle = "Jacksonville, FL CBSA target-zone tract proxy, 2024 snapshot | Bubble area represents tract population in high-scoring retail opportunity zones",
      size_label = "Target-zone tract population",
      legend_title = "Population",
      value_style = "number",
      color_mode = "color_group",
      color_legend_title = "Tract status",
      context_data = jacksonville_counties,
      context_color = "#AAB7C4",
      context_linewidth = 0.35,
      point_alpha = 0.76,
      label_size = 2.5,
      caption_side_note = "Parcel-level retail clusters are not yet in DuckDB, so this sample uses eligible high-scoring tracts as a reviewable target-zone proxy.",
      caption_wrap_width = 115
    )
  )

  # Export path
  outputs["bubble_retail_parcel_clusters"] <- save_proportional_symbol_plot(
    q4_plot,
    output_dir,
    "proportional_symbol_q4_retail_parcel_cluster_proxy.png",
    width = 8.8,
    height = 8.0
  )

  # Query block: county jobs concentration
  # Current gold tables expose employed residents, not workplace establishment
  # totals; the caption keeps that proxy explicit for review.
  q5_path <- "visual_library/charts/proportional_symbol_map/sample_sql/q5_county_jobs_concentration.sql"
  q5_raw <- run_proportional_symbol_query(con, q5_path)
  assert_proportional_symbol_contract(q5_raw, "bubble_jobs_concentration")

  # Prep block
  q5_df <- prep_proportional_symbol_map(
    q5_raw,
    config = list(
      question_id = "bubble_jobs_concentration",
      time_window = "2023_snapshot",
      label_top_n = 6,
      label_strategy = "top_n",
      require_single_time_window = TRUE
    )
  )

  # Render block
  q5_plot <- render_proportional_symbol_map(
    q5_df,
    config = list(
      composition_preset = "local_focus",
      output_mode = "presentation",
      title = "How concentrated is employment across Atlanta counties?",
      subtitle = "Atlanta-Sandy Springs-Roswell counties, 2023 snapshot | Bubble area represents employed residents by county",
      size_label = "Employed residents",
      legend_title = "Employed residents",
      value_style = "number",
      context_data = atlanta_counties,
      context_color = "#AAB7C4",
      context_linewidth = 0.35,
      point_alpha = 0.78,
      caption_side_note = "This uses employed residents from the labor wide table as the current jobs-concentration proxy until establishment workplace totals are added.",
      caption_wrap_width = 115
    )
  )

  # Export path
  outputs["bubble_jobs_concentration"] <- save_proportional_symbol_plot(
    q5_plot,
    output_dir,
    "proportional_symbol_q5_jobs_concentration_atlanta.png",
    width = 8.8,
    height = 8.0
  )

  outputs
}

outputs <- run_proportional_symbol_map_tests()
print(outputs)
