# Section 06 checks script
# Purpose: sanity checks and QA assertions for section outputs.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

message("Running section 06 checks: 06_conclusion_appendix")

required_paths <- c(
  read_artifact_path("06_conclusion_appendix", "section_06_conclusion_payload"),
  read_artifact_path("06_conclusion_appendix", "section_06_appendix_payload"),
  read_artifact_path("06_conclusion_appendix", "section_06_visual_objects"),
  read_artifact_path("03_eligibility_scoring", "section_03_validation_report"),
  read_artifact_path("04_zones", "section_04_validation_report"),
  read_artifact_path("05_parcels", "section_05_validation_report")
)
missing_paths <- required_paths[!file.exists(required_paths)]
if (length(missing_paths) > 0) {
  stop(
    glue::glue("Section 06 checks missing required inputs: {paste(missing_paths, collapse = '; ')}"),
    call. = FALSE
  )
}

conclusion_payload <- readRDS(read_artifact_path("06_conclusion_appendix", "section_06_conclusion_payload"))
appendix_payload <- readRDS(read_artifact_path("06_conclusion_appendix", "section_06_appendix_payload"))
visual_objects <- readRDS(read_artifact_path("06_conclusion_appendix", "section_06_visual_objects"))

section_03_report <- readRDS(read_artifact_path("03_eligibility_scoring", "section_03_validation_report"))
section_04_report <- readRDS(read_artifact_path("04_zones", "section_04_validation_report"))
section_05_report <- readRDS(read_artifact_path("05_parcels", "section_05_validation_report"))

or_else <- function(x, fallback) if (is.null(x)) fallback else x

schema_checks <- list(
  conclusion_zone_highlights = validate_columns(
    conclusion_payload$highlights$cluster_zone_highlights,
    c("zone_id", "zone_label", "tracts", "retail_parcel_count", "retail_area_density", "zone_quality_score"),
    "section_06_conclusion_payload.highlights.cluster_zone_highlights"
  ),
  conclusion_shortlist_summary = validate_columns(
    conclusion_payload$highlights$shortlist_summary,
    c("n_shortlisted", "n_zones", "median_shortlist_score", "p90_shortlist_score"),
    "section_06_conclusion_payload.highlights.shortlist_summary"
  ),
  conclusion_top_shortlist_preview = validate_columns(
    conclusion_payload$highlights$top_shortlist_preview,
    c("shortlist_rank_system", "zone_label", "parcel_uid", "shortlist_score"),
    "section_06_conclusion_payload.highlights.top_shortlist_preview"
  ),
  appendix_kpi_dictionary = validate_columns(
    appendix_payload$kpi_dictionary,
    c("kpi_key", "label", "direction", "source_table"),
    "section_06_appendix_payload.kpi_dictionary"
  ),
  appendix_assumptions_caveats = validate_columns(
    appendix_payload$assumptions_caveats,
    c("category", "statement"),
    "section_06_appendix_payload.assumptions_caveats"
  ),
  appendix_qa_summary = validate_columns(
    appendix_payload$qa_summary,
    c("section", "report_path", "pass", "warning_count"),
    "section_06_appendix_payload.qa_summary"
  )
)

visual_checks <- list(
  has_conclusion_summary_table = "conclusion_summary_table" %in% names(visual_objects),
  has_shortlist_summary_table = "shortlist_summary_table" %in% names(visual_objects),
  has_qa_summary_table = "qa_summary_table" %in% names(visual_objects),
  has_assumptions_caveats_table = "assumptions_caveats_table" %in% names(visual_objects),
  has_recommendations_table = "recommendations_table" %in% names(visual_objects)
)

report_reference_checks <- list(
  section_03_pass = isTRUE(or_else(section_03_report$pass, (all(vapply(section_03_report$checks[1:5], `[[`, logical(1), "pass")) && all(unlist(section_03_report$logic_checks))))),
  section_04_pass = isTRUE(section_04_report$pass),
  section_05_pass = isTRUE(section_05_report$pass),
  appendix_qa_rows_match_expected = nrow(appendix_payload$qa_summary) == 3
)

narrative_checks <- list(
  recommendations_non_empty = length(conclusion_payload$recommendations) >= 3 &&
    all(nchar(trimws(conclusion_payload$recommendations)) > 0),
  assumptions_non_empty = nrow(appendix_payload$assumptions_caveats) >= 4 &&
    all(nchar(trimws(appendix_payload$assumptions_caveats$statement)) > 0),
  qa_summary_has_no_missing_pass = all(!is.na(appendix_payload$qa_summary$pass)),
  qa_summary_has_no_missing_warning_count = all(!is.na(appendix_payload$qa_summary$warning_count)),
  input_snapshot_present = !is.null(appendix_payload$section_06_input_snapshot)
)

schema_pass <- all(vapply(schema_checks, `[[`, logical(1), "pass"))
visual_pass <- all(unlist(visual_checks))
reference_pass <- all(unlist(report_reference_checks))
narrative_pass <- all(unlist(narrative_checks))

validation_report <- list(
  run_metadata = run_metadata(),
  schema_checks = schema_checks,
  visual_checks = visual_checks,
  report_reference_checks = report_reference_checks,
  narrative_checks = narrative_checks,
  pass = schema_pass && visual_pass && reference_pass && narrative_pass
)

save_artifact(
  validation_report,
  resolve_output_path("06_conclusion_appendix", "section_06_validation_report")
)

if (!isTRUE(validation_report$pass)) {
  stop("Section 06 checks failed. See section_06_validation_report.rds.", call. = FALSE)
}

message("Section 06 checks complete.")
