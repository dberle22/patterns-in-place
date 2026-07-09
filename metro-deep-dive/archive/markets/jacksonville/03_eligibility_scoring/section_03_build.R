# Section 03 build script
# Purpose: data prep and core transformations for section 03_eligibility_scoring.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()
source("notebooks/retail_opportunity_finder/data_platform/layers/02_tract_scoring/tract_scoring_workflow.R")

message("Running section 03 build: 03_eligibility_scoring")

con <- connect_project_duckdb(read_only = FALSE)
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

products <- build_tract_scoring_products(con)
publish_tract_scoring_products(con, products)

funnel_counts <- products$funnel_counts
eligible_tracts <- products$eligible_tracts
scored_tracts <- products$scored_tracts
top_tracts <- products$top_tracts
cluster_seed_tracts <- products$cluster_seed_tracts
tract_component_score_table <- products$tract_component_scores
price_hist_input <- products$price_hist_input
growth_hist_input <- products$growth_hist_input
tract_sf <- products$tract_sf

save_artifact(
  funnel_counts,
  resolve_output_path("03_eligibility_scoring", "section_03_funnel_counts")
)
save_artifact(
  eligible_tracts,
  resolve_output_path("03_eligibility_scoring", "section_03_eligible_tracts")
)
save_artifact(
  scored_tracts,
  resolve_output_path("03_eligibility_scoring", "section_03_scored_tracts")
)
save_artifact(
  top_tracts,
  resolve_output_path("03_eligibility_scoring", "section_03_top_tracts")
)
save_artifact(
  cluster_seed_tracts,
  resolve_output_path("03_eligibility_scoring", "section_03_cluster_seed_tracts")
)
save_artifact(
  tract_component_score_table,
  resolve_output_path("03_eligibility_scoring", "section_03_tract_component_scores")
)
readr::write_csv(
  tract_component_score_table,
  resolve_output_path("03_eligibility_scoring", "section_03_tract_component_scores", ext = "csv")
)
save_artifact(
  price_hist_input,
  resolve_output_path("03_eligibility_scoring", "section_03_price_hist_input")
)
save_artifact(
  growth_hist_input,
  resolve_output_path("03_eligibility_scoring", "section_03_growth_hist_input")
)
save_artifact(
  tract_sf,
  resolve_output_path("03_eligibility_scoring", "section_03_tract_sf")
)

message("Section 03 build complete.")
