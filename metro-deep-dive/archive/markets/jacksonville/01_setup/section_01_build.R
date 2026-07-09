# Section 01 build script
# Purpose: data prep and core transformations for section 01_setup.

source("notebooks/retail_opportunity_finder/sections/_shared/bootstrap.R")
initialize_section_runtime()

message("Running section 01 build: 01_setup")

project_root <- resolve_project_root()
model_params_check <- validate_model_params(MODEL_PARAMS)
market_profile <- get_market_profile()
market_context <- get_market_context()
market_profile_check <- validate_market_profile(market_profile)
run_meta <- run_metadata()
section_output_dir <- resolve_market_output_dir("01_setup")

foundation_payload <- list(
  run_metadata = run_meta,
  project_root = project_root,
  market_context = market_context,
  output_dir = section_output_dir,
  market_profile = market_profile,
  market_profile_check = market_profile_check,
  model_params = MODEL_PARAMS,
  model_params_check = model_params_check,
  kpi_dictionary = KPI_DICTIONARY,
  generated_at = as.character(Sys.time())
)

save_artifact(
  run_meta,
  resolve_output_path("01_setup", "section_01_run_metadata")
)

save_artifact(
  foundation_payload,
  resolve_output_path("01_setup", "section_01_foundation")
)

message("Section 01 build complete.")
