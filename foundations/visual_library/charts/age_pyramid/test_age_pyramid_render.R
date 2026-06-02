# Age pyramid render tests with question-specific DuckDB queries.

if (file.exists(".Renviron")) readRenviron(".Renviron")

source("visual_library/shared/standards.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/scatter_query_helpers.R")
source("visual_library/shared/prep/prep_age_pyramid.R")
source("visual_library/shared/render/render_age_pyramid.R")

age_pyramid_age_levels <- c(
  "0-4", "5-14", "15-17", "18-24", "25-34", "35-44",
  "45-54", "55-64", "65-74", "75-84", "85+"
)

read_age_pyramid_sql <- function(filename) {
  sql_dir <- "visual_library/charts/age_pyramid/sample_sql"
  sql <- read_sql_file(file.path(sql_dir, filename))
  helper <- read_sql_file(file.path(sql_dir, "age_pyramid_age_sex_helper.sql"))
  gsub("{{AGE_PYRAMID_HELPER}}", helper, sql, fixed = TRUE)
}

run_age_pyramid_query <- function(con, filename) {
  sql <- read_age_pyramid_sql(filename)
  DBI::dbGetQuery(con, sql)
}

assert_age_pyramid_contract <- function(data, question_id, allow_multiple_periods = FALSE) {
  assert_age_pyramid_ready(
    data,
    question_id = question_id,
    allow_multiple_periods = allow_multiple_periods,
    expected_age_bins = age_pyramid_age_levels
  )
}

save_age_pyramid_plot <- function(plot, output_dir, filename, width = 11, height = 7) {
  path <- file.path(output_dir, filename)
  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 300, bg = "white")
  path
}

run_age_pyramid_tests <- function() {
  output_dir <- "visual_library/charts/age_pyramid/sample_output"
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  con <- connect_metro_duckdb(read_only = TRUE)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  outputs <- c()

  # 1. Does this CBSA skew younger or older than the national benchmark?
  raw_cbsa_vs_us <- run_age_pyramid_query(con, "pyramid_cbsa_vs_us.sql")
  assert_age_pyramid_contract(raw_cbsa_vs_us, "pyramid_cbsa_vs_us")
  cbsa_vs_us_df <- prep_age_pyramid(
    raw_cbsa_vs_us,
    config = list(
      question_id = "pyramid_cbsa_vs_us",
      measure = "share",
      age_bin_levels = age_pyramid_age_levels
    )
  )
  assert_age_pyramid_ready(cbsa_vs_us_df, "pyramid_cbsa_vs_us", expected_age_bins = age_pyramid_age_levels, check_share_sums = TRUE)
  cbsa_vs_us_plot <- render_age_pyramid(
    cbsa_vs_us_df,
    config = list(
      output_mode = "presentation",
      title = "Age structure: Wilmington, NC vs the United States",
      subtitle = "2024 ACS age-by-sex structure | Bars show Wilmington share of total population; outline shows the US benchmark",
      label_threshold = 0.04,
      caption_side_note = "Use the outline gap to see where Wilmington skews older or younger than the national structure."
    )
  )
  outputs["pyramid_cbsa_vs_us"] <- save_age_pyramid_plot(
    cbsa_vs_us_plot,
    output_dir,
    "pyramid_cbsa_vs_us.png"
  )

  # 2. Which counties within the CBSA have the strongest family formation profile?
  raw_county_family <- run_age_pyramid_query(con, "pyramid_county_family_profile.sql")
  assert_age_pyramid_contract(raw_county_family, "pyramid_county_family_profile")
  county_family_df <- prep_age_pyramid(
    raw_county_family,
    config = list(
      question_id = "pyramid_county_family_profile",
      measure = "share",
      age_bin_levels = age_pyramid_age_levels
    )
  )
  assert_age_pyramid_ready(county_family_df, "pyramid_county_family_profile", expected_age_bins = age_pyramid_age_levels, check_share_sums = TRUE)
  county_family_plot <- render_age_pyramid(
    county_family_df,
    config = list(
      output_mode = "presentation",
      title = "Which Wilmington-area counties show a family-formation bulge?",
      subtitle = "2024 ACS county age structure | Top counties by children plus ages 25-44; CBSA outline repeated for context",
      facet_by = "facet_label",
      facet_ncol = 3,
      label_threshold = 0.055,
      caption_side_note = "Family formation profile ranks counties by combined ages 0-14 and 25-44."
    )
  )
  outputs["pyramid_county_family_profile"] <- save_age_pyramid_plot(
    county_family_plot,
    output_dir,
    "pyramid_county_family_profile.png",
    width = 13,
    height = 7.5
  )

  # 3. Is the metro aging faster than the benchmark structure?
  raw_peer_aging <- run_age_pyramid_query(con, "pyramid_peer_aging_compare.sql")
  assert_age_pyramid_contract(raw_peer_aging, "pyramid_peer_aging_compare", allow_multiple_periods = TRUE)
  peer_aging_df <- prep_age_pyramid(
    raw_peer_aging,
    config = list(
      question_id = "pyramid_peer_aging_compare",
      measure = "share",
      age_bin_levels = age_pyramid_age_levels,
      allow_multiple_periods = TRUE,
      require_single_period = FALSE
    )
  )
  assert_age_pyramid_ready(
    peer_aging_df,
    "pyramid_peer_aging_compare",
    allow_multiple_periods = TRUE,
    expected_age_bins = age_pyramid_age_levels,
    check_share_sums = TRUE
  )
  peer_aging_plot <- render_age_pyramid(
    peer_aging_df,
    config = list(
      output_mode = "presentation",
      title = "Is Wilmington's age structure shifting older?",
      subtitle = "2013 and 2024 ACS snapshots | Wilmington bars compared with same-year US outlines",
      facet_by = "facet_label",
      facet_ncol = 2,
      label_threshold = 0.05,
      caption_side_note = "Facets are separate snapshots, so the comparison reads as structural change rather than a continuous time series."
    )
  )
  outputs["pyramid_peer_aging_compare"] <- save_age_pyramid_plot(
    peer_aging_plot,
    output_dir,
    "pyramid_peer_aging_compare.png",
    width = 12,
    height = 7
  )

  # 4. Do target ZCTAs show a retiree concentration?
  raw_zcta_retiree <- run_age_pyramid_query(con, "pyramid_zcta_retiree_profile.sql")
  assert_age_pyramid_contract(raw_zcta_retiree, "pyramid_zcta_retiree_profile")
  zcta_retiree_df <- prep_age_pyramid(
    raw_zcta_retiree,
    config = list(
      question_id = "pyramid_zcta_retiree_profile",
      measure = "share",
      age_bin_levels = age_pyramid_age_levels
    )
  )
  assert_age_pyramid_ready(zcta_retiree_df, "pyramid_zcta_retiree_profile", expected_age_bins = age_pyramid_age_levels, check_share_sums = TRUE)
  zcta_retiree_plot <- render_age_pyramid(
    zcta_retiree_df,
    config = list(
      output_mode = "presentation",
      title = "Which Wilmington ZCTAs show retiree concentration?",
      subtitle = "2024 ACS ZCTA age structure | Top retiree-share ZCTAs with county benchmark outlines",
      facet_by = "facet_label",
      facet_ncol = 3,
      label_threshold = 0.06,
      caption_side_note = "ZCTAs below 2,500 population are excluded to reduce small-sample volatility."
    )
  )
  outputs["pyramid_zcta_retiree_profile"] <- save_age_pyramid_plot(
    zcta_retiree_plot,
    output_dir,
    "pyramid_zcta_retiree_profile.png",
    width = 13,
    height = 7.5
  )

  # 5. How do age-structure differences align with housing demand signals?
  raw_housing_alignment <- run_age_pyramid_query(con, "pyramid_housing_demand_alignment.sql")
  assert_age_pyramid_contract(raw_housing_alignment, "pyramid_housing_demand_alignment")
  housing_alignment_df <- prep_age_pyramid(
    raw_housing_alignment,
    config = list(
      question_id = "pyramid_housing_demand_alignment",
      measure = "share",
      age_bin_levels = age_pyramid_age_levels
    )
  )
  assert_age_pyramid_ready(housing_alignment_df, "pyramid_housing_demand_alignment", expected_age_bins = age_pyramid_age_levels, check_share_sums = TRUE)
  housing_alignment_plot <- render_age_pyramid(
    housing_alignment_df,
    config = list(
      output_mode = "presentation",
      title = "Where does age structure point toward family housing demand?",
      subtitle = "2024 ACS county age structure | Highest family-age county compared with Wilmington CBSA benchmark",
      label_threshold = 0.045,
      caption_side_note = "Age structure is paired with housing-core context in the query; the chart focuses on the demographic side of demand."
    )
  )
  outputs["pyramid_housing_demand_alignment"] <- save_age_pyramid_plot(
    housing_alignment_plot,
    output_dir,
    "pyramid_housing_demand_alignment.png"
  )

  outputs
}

outputs <- run_age_pyramid_tests()
print(outputs)
