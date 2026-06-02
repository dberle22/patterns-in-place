# Scatter chart render tests for Q1/Q2/Q3.

if (file.exists(".Renviron")) readRenviron(".Renviron")

source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_scatter.R")
source("visual_library/shared/render/render_scatter.R")

run_scatter_tests <- function() {
  output_dir <- "visual_library/charts/scatter/output"
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  con <- connect_metro_duckdb(read_only = TRUE)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  q1_path <- "visual_library/charts/scatter/sample_sql/q1_cbsa_income_growth_vs_rent_burden.sql"
  q2_path <- "visual_library/charts/scatter/sample_sql/q2_county_home_value_vs_income.sql"
  q3_path <- "visual_library/charts/scatter/sample_sql/q3_zcta_rent_vs_income_outliers.sql"

  q1_raw <- run_scatter_query(con, q1_path)
  q2_raw <- run_scatter_query(con, q2_path)
  q3_raw <- run_scatter_query(con, q3_path)

  v1 <- validate_scatter_contract(q1_raw)
  v2 <- validate_scatter_contract(q2_raw)
  v3 <- validate_scatter_contract(q3_raw)

  if (!(v1$pass && v2$pass && v3$pass)) {
    stop("Scatter contract validation failed for one or more query outputs.")
  }

  q1_df <- prep_scatter(q1_raw, time_window = "2018_to_2023_growth")
  q2_df <- prep_scatter(q2_raw, time_window = "2023_snapshot")
  q3_df <- prep_scatter(q3_raw, time_window = "2023_snapshot")

  p1 <- render_scatter(
    q1_df,
    title = "Q1 Scatter: Income Growth vs Rent Burden (CBSA)",
    subtitle = "Bubble size = housing units; labels highlight target geo",
    highlight_mode = "labels",
    add_trend_line = TRUE,
    add_reference_line = FALSE,
    add_quadrants = TRUE
  )

  p2 <- render_scatter(
    q2_df,
    title = "Q2 Scatter: Home Value vs Income (County)",
    subtitle = "Highlighted points are top ratio outliers",
    highlight_mode = "color",
    add_trend_line = TRUE,
    add_reference_line = FALSE,
    add_quadrants = TRUE
  )

  p3 <- render_scatter(
    q3_df,
    title = "Q3 Scatter: Rent vs Income Outliers (ZCTA)",
    subtitle = "Within selected CBSA; labels show z-score outliers",
    highlight_mode = "labels",
    add_trend_line = FALSE,
    add_reference_line = FALSE,
    add_quadrants = TRUE
  )

  out1 <- file.path(output_dir, "scatter_q1_cbsa_income_growth_vs_rent_burden.png")
  out2 <- file.path(output_dir, "scatter_q2_county_home_value_vs_income.png")
  out3 <- file.path(output_dir, "scatter_q3_zcta_rent_vs_income_outliers.png")

  ggplot2::ggsave(out1, plot = p1, width = 11, height = 7, dpi = 300, bg = "white")
  ggplot2::ggsave(out2, plot = p2, width = 11, height = 7, dpi = 300, bg = "white")
  ggplot2::ggsave(out3, plot = p3, width = 11, height = 7, dpi = 300, bg = "white")

  c(out1, out2, out3)
}

outputs <- run_scatter_tests()
print(outputs)
