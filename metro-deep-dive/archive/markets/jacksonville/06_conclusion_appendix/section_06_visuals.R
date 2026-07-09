# Section 06 visuals script
# Purpose: generate plots/tables from section outputs.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

message("Running section 06 visuals: 06_conclusion_appendix")

conclusion_payload <- readRDS(read_artifact_path("06_conclusion_appendix", "section_06_conclusion_payload"))
appendix_payload <- readRDS(read_artifact_path("06_conclusion_appendix", "section_06_appendix_payload"))

conclusion_summary_table <- conclusion_payload$highlights$cluster_zone_highlights %>%
  gt::gt() %>%
  gt::tab_header(title = "Top Cluster Zones - Final Highlight") %>%
  gt::cols_label(
    zone_id = "Zone ID",
    zone_label = "Zone Label",
    tracts = "Tracts",
    retail_parcel_count = "Retail Parcels",
    retail_area_density = "Retail Area Density",
    zone_quality_score = "Zone Quality Score"
  ) %>%
  gt::fmt_number(columns = c(tracts, retail_parcel_count), decimals = 0) %>%
  gt::fmt_number(columns = c(retail_area_density, zone_quality_score), decimals = 3)

shortlist_summary_table <- conclusion_payload$highlights$shortlist_summary %>%
  gt::gt() %>%
  gt::tab_header(title = "Cluster Shortlist Summary") %>%
  gt::cols_label(
    n_shortlisted = "Shortlisted Parcels",
    n_zones = "Zones Covered",
    median_shortlist_score = "Median Shortlist Score",
    p90_shortlist_score = "P90 Shortlist Score",
    median_parcel_area_sqmi = "Median Parcel Area (sq mi)",
    median_assessed_value = "Median Assessed Value"
  ) %>%
  gt::fmt_number(columns = c(n_shortlisted, n_zones), decimals = 0) %>%
  gt::fmt_number(columns = c(median_shortlist_score, p90_shortlist_score, median_parcel_area_sqmi), decimals = 3) %>%
  gt::fmt_currency(columns = median_assessed_value, decimals = 0)

qa_summary_table <- appendix_payload$qa_summary %>%
  gt::gt() %>%
  gt::tab_header(title = "Section QA Summary Rollup") %>%
  gt::cols_label(
    section = "Section",
    report_path = "Validation Report",
    pass = "Pass",
    warning_count = "Warnings"
  ) %>%
  gt::fmt_number(columns = warning_count, decimals = 0)

assumptions_caveats_table <- appendix_payload$assumptions_caveats %>%
  gt::gt() %>%
  gt::tab_header(title = "Assumptions and Caveats") %>%
  gt::cols_label(
    category = "Category",
    statement = "Statement"
  )

recommendations_table <- tibble::tibble(
  recommendation_order = seq_along(conclusion_payload$recommendations),
  recommendation = conclusion_payload$recommendations
) %>%
  gt::gt() %>%
  gt::tab_header(title = "Recommended Next Actions") %>%
  gt::cols_label(
    recommendation_order = "Order",
    recommendation = "Action"
  ) %>%
  gt::fmt_number(columns = recommendation_order, decimals = 0)

save_artifact(
  list(
    conclusion_summary_table = conclusion_summary_table,
    shortlist_summary_table = shortlist_summary_table,
    qa_summary_table = qa_summary_table,
    assumptions_caveats_table = assumptions_caveats_table,
    recommendations_table = recommendations_table
  ),
  resolve_output_path("06_conclusion_appendix", "section_06_visual_objects")
)

message("Section 06 visuals complete.")
