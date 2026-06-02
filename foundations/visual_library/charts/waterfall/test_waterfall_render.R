# Waterfall chart render tests with question-specific DuckDB queries.

# Load local environment settings so the shared DuckDB helper can find DATA.
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Source shared standards, contract validators, query helpers, and the chart's
# prep/render functions. Keeping this runner thin makes chart behavior reusable.
source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_waterfall.R")
source("visual_library/shared/render/render_waterfall.R")

# Read and execute one chart-local SQL file. Each canonical question owns its
# query so the data intent stays reviewable next to the rendered output.
run_waterfall_query <- function(con, sql_path) {
  sql <- read_sql_file(sql_path)
  DBI::dbGetQuery(con, sql)
}

# Fail fast if a query no longer returns the required waterfall contract fields.
assert_waterfall_contract <- function(data, question_id) {
  validation <- validate_waterfall_contract(data)
  if (isTRUE(validation$pass)) {
    return(invisible(validation))
  }

  stop(
    sprintf(
      "Waterfall contract validation failed for %s. Missing required: %s. Rows: %s",
      question_id,
      paste(validation$missing_required, collapse = ", "),
      validation$rows
    )
  )
}

# Waterfalls are only valid when components add to the total story. The prep
# function computes additive QA fields; this runner treats failures as blockers.
assert_additive_waterfall <- function(data, question_id, tolerance = 1e-6) {
  if (!("additive_pass" %in% names(data)) || any(!data$additive_pass, na.rm = TRUE)) {
    stop(sprintf("Waterfall additive validation failed for %s.", question_id))
  }
  residual <- max(abs(data$additive_residual %||% 0), na.rm = TRUE)
  if (is.finite(residual) && residual > tolerance) {
    stop(sprintf("Waterfall additive residual too large for %s: %s", question_id, residual))
  }
  invisible(TRUE)
}

# Centralize PNG export settings so every sample is rendered consistently.
save_waterfall_plot <- function(plot, output_dir, filename, width = 11, height = 7) {
  path <- file.path(output_dir, filename)
  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 300, bg = "white")
  path
}

# Write a small review index that maps canonical questions to the regenerated
# PNGs and documents the shared QA assumptions.
write_waterfall_review <- function(output_dir, outputs) {
  review_path <- file.path(output_dir, "test_waterfall_business_questions.md")
  lines <- c(
    "# Waterfall Testing",
    "",
    "## Canonical Questions",
    "1. What drove the change in personal income from 2013 to 2023 in the target CBSA?",
    "2. How does the income component mix differ from a regional benchmark?",
    "3. What components explain GDP change by major sector?",
    "4. For housing stock change, what share came from single-unit vs multifamily additions?",
    "5. Which components offset growth in the last 5 years for a target-market county?",
    "",
    "## Output Files",
    paste0("- `waterfall_income_change_drivers`: ", outputs[["waterfall_income_change_drivers"]]),
    paste0("- `waterfall_income_mix_compare`: ", outputs[["waterfall_income_mix_compare"]]),
    paste0("- `waterfall_gdp_sector_change`: ", outputs[["waterfall_gdp_sector_change"]]),
    paste0("- `waterfall_housing_stock_components`: ", outputs[["waterfall_housing_stock_components"]]),
    paste0("- `waterfall_negative_offsets`: ", outputs[["waterfall_negative_offsets"]]),
    "",
    "## QA Notes",
    "- Shared prep validates the waterfall contract, filters to the requested question, chooses delta vs level mode, creates running cumulative positions by waterfall group, and appends a terminal total bar.",
    "- Shared render uses visual-library theme defaults, diverging positive/negative colors, total bars, connector lines, value labels, source/vintage captions, and optional facets for benchmark comparison.",
    "- Component ordering follows `waterfall_decisions.md`: canonical logical order is preferred over magnitude sorting.",
    "- Additive validation is checked after prep for every canonical question before rendering."
  )
  writeLines(lines, review_path)
  review_path
}

run_waterfall_tests <- function() {
  # All review artifacts for this chart type live under sample_output/.
  output_dir <- "visual_library/charts/waterfall/sample_output"
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  # Open the project DuckDB read-only because this runner should only query
  # sample data and render files, never mutate the database.
  con <- connect_metro_duckdb(read_only = TRUE)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  outputs <- c()

  # Query block: personal income change drivers. This pulls a target-CBSA
  # decomposition of 2013-2023 income change into wage and non-wage components.
  q1_path <- "visual_library/charts/waterfall/sample_sql/q1_income_change_drivers.sql"
  q1_raw <- run_waterfall_query(con, q1_path)
  assert_waterfall_contract(q1_raw, "waterfall_income_change_drivers")

  # Prep block: render component_delta as the bar contribution and append a net
  # change total bar so the final additive result is explicit.
  q1_df <- prep_waterfall(
    q1_raw,
    config = list(
      question_id = "waterfall_income_change_drivers",
      time_window = "2013-2023 change",
      value_mode = "delta",
      include_total = TRUE,
      total_label = "Net change"
    )
  )
  assert_additive_waterfall(q1_df, "waterfall_income_change_drivers")

  # Render block: configure presentation labels and dollar formatting for the
  # first canonical business question.
  q1_plot <- render_waterfall(
    q1_df,
    config = list(
      output_mode = "presentation",
      title = "What drove Wilmington personal income change?",
      subtitle = "Wilmington, NC CBSA, 2013-2023 | Components are changes in total personal income; non-wage income reconciles to total",
      value_label = "$ millions",
      label_style = "dollar",
      label_accuracy = 1,
      caption_side_note = "Use this as the cleanest two-part income decomposition available in the current wide income table."
    )
  )

  # Export path: save the reviewable PNG with a stable filename.
  outputs["waterfall_income_change_drivers"] <- save_waterfall_plot(
    q1_plot,
    output_dir,
    "waterfall_q1_income_change_drivers.png",
    width = 9.5,
    height = 6.8
  )

  # Query block: income component mix versus benchmark. This returns target and
  # regional benchmark rows using the same per-capita component definitions.
  q2_path <- "visual_library/charts/waterfall/sample_sql/q2_income_mix_compare.sql"
  q2_raw <- run_waterfall_query(con, q2_path)
  assert_waterfall_contract(q2_raw, "waterfall_income_mix_compare")

  # Prep block: use level values, not deltas, and group paths by benchmark panel
  # so each facet has its own cumulative waterfall.
  q2_df <- prep_waterfall(
    q2_raw,
    config = list(
      question_id = "waterfall_income_mix_compare",
      value_mode = "level",
      include_total = TRUE,
      total_label = "Total income per resident",
      group_fields = c("benchmark_label", "geo_id", "time_window")
    )
  )
  assert_additive_waterfall(q2_df, "waterfall_income_mix_compare")

  # Render block: facet by benchmark label to show target and benchmark side by
  # side without mixing them into one cumulative path.
  q2_plot <- render_waterfall(
    q2_df,
    config = list(
      output_mode = "presentation",
      title = "How does Wilmington's income mix compare with its region?",
      subtitle = "Latest CBSA income year | Components are dollars per resident; South benchmark is population-weighted across regional CBSAs",
      value_label = "$ per resident",
      label_style = "dollar",
      label_accuracy = 1,
      facet_by = "benchmark_label",
      facet_ncol = 2,
      rotate_x_labels = TRUE,
      caption_side_note = "Faceted benchmark comparison keeps the same component definitions and avoids mixing target and benchmark bars in one cumulative path."
    )
  )

  # Export path: save the benchmark-comparison PNG.
  outputs["waterfall_income_mix_compare"] <- save_waterfall_plot(
    q2_plot,
    output_dir,
    "waterfall_q2_income_mix_compare.png",
    width = 12,
    height = 6.8
  )

  # Query block: GDP sector change. This pulls real GDP sector deltas in a
  # canonical economic order, with Other reconciling sector sum to total.
  q3_path <- "visual_library/charts/waterfall/sample_sql/q3_gdp_sector_change.sql"
  q3_raw <- run_waterfall_query(con, q3_path)
  assert_waterfall_contract(q3_raw, "waterfall_gdp_sector_change")

  # Prep block: use sector component deltas as the waterfall contributions and
  # add a net real GDP change total bar.
  q3_df <- prep_waterfall(
    q3_raw,
    config = list(
      question_id = "waterfall_gdp_sector_change",
      time_window = "2013-2023 change",
      value_mode = "delta",
      include_total = TRUE,
      total_label = "Net real GDP change"
    )
  )
  assert_additive_waterfall(q3_df, "waterfall_gdp_sector_change")

  # Render block: keep the sector-ordering caveat in the caption because this is
  # a reusable decision for market-to-market comparisons.
  q3_plot <- render_waterfall(
    q3_df,
    config = list(
      output_mode = "presentation",
      title = "Which sectors drove Wilmington real GDP change?",
      subtitle = "Wilmington, NC CBSA, 2013-2023 | Sector components are real GDP changes; Other reconciles sector sum to total",
      value_label = "$ millions",
      label_style = "dollar",
      label_accuracy = 1,
      caption_side_note = "The sector list is kept in canonical economic order to support repeat comparison across markets."
    )
  )

  # Export path: save the GDP-sector decomposition PNG.
  outputs["waterfall_gdp_sector_change"] <- save_waterfall_plot(
    q3_plot,
    output_dir,
    "waterfall_q3_gdp_sector_change.png",
    width = 12.5,
    height = 7.2
  )

  # Query block: housing stock components. This decomposes recent housing-stock
  # change by structure type and includes a reconciliation component.
  q4_path <- "visual_library/charts/waterfall/sample_sql/q4_housing_stock_components.sql"
  q4_raw <- run_waterfall_query(con, q4_path)
  assert_waterfall_contract(q4_raw, "waterfall_housing_stock_components")

  # Prep block: use housing-unit deltas and append a net housing-unit change bar.
  q4_df <- prep_waterfall(
    q4_raw,
    config = list(
      question_id = "waterfall_housing_stock_components",
      time_window = "2019-2024 change",
      value_mode = "delta",
      include_total = TRUE,
      total_label = "Net housing unit change"
    )
  )
  assert_additive_waterfall(q4_df, "waterfall_housing_stock_components")

  # Render block: use integer formatting because these values are unit counts,
  # not dollars or rates.
  q4_plot <- render_waterfall(
    q4_df,
    config = list(
      output_mode = "presentation",
      title = "What kind of housing stock changed in Wilmington?",
      subtitle = "Wilmington, NC CBSA, 2019-2024 | Components are change in housing structure counts",
      value_label = "Housing units",
      label_style = "integer",
      caption_side_note = "Other/attached units reconciles the published structure categories to total structure units."
    )
  )

  # Export path: save the housing-stock decomposition PNG.
  outputs["waterfall_housing_stock_components"] <- save_waterfall_plot(
    q4_plot,
    output_dir,
    "waterfall_q4_housing_stock_components.png",
    width = 11,
    height = 6.8
  )

  # Query block: negative sector offsets. The SQL chooses a target-market county
  # with positive net growth but at least one negative sector contribution.
  q5_path <- "visual_library/charts/waterfall/sample_sql/q5_negative_offsets.sql"
  q5_raw <- run_waterfall_query(con, q5_path)
  assert_waterfall_contract(q5_raw, "waterfall_negative_offsets")

  # Prep block: use 2018-2023 sector deltas so negative bars show offsets against
  # the positive-growth components.
  q5_df <- prep_waterfall(
    q5_raw,
    config = list(
      question_id = "waterfall_negative_offsets",
      time_window = "2018-2023 change",
      value_mode = "delta",
      include_total = TRUE,
      total_label = "Net real GDP change"
    )
  )
  assert_additive_waterfall(q5_df, "waterfall_negative_offsets")

  # Render block: place the selected county name into the subtitle dynamically,
  # because the SQL may choose a different county as data updates.
  q5_plot <- render_waterfall(
    q5_df,
    config = list(
      output_mode = "presentation",
      title = "Which sectors offset recent county GDP growth?",
      subtitle = paste(
        unique(q5_df$geo_name)[1],
        "in the Wilmington, NC CBSA, 2018-2023 | Negative bars show sectors that offset positive net real GDP growth"
      ),
      value_label = "$ millions",
      label_style = "dollar",
      label_accuracy = 1,
      caption_side_note = "County is selected from the target CBSA by largest negative sector offset among counties with positive net growth."
    )
  )

  # Export path: save the negative-offset decomposition PNG.
  outputs["waterfall_negative_offsets"] <- save_waterfall_plot(
    q5_plot,
    output_dir,
    "waterfall_q5_negative_offsets.png",
    width = 12,
    height = 7
  )

  # Regenerate the markdown review index after all PNG paths are known.
  outputs["review_markdown"] <- write_waterfall_review(output_dir, outputs)
  outputs
}

# Execute the full local sample workflow when this file is run directly.
outputs <- run_waterfall_tests()
print(outputs)
