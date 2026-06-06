# Section bootstrap for Retail Opportunity Finder modules
#
# This creates a single entry-point so each section script can load:
# 1) project-wide runtime from scripts/utils.R
# 2) section-specific config/helpers in this folder

initialize_section_runtime <- function() {
  project_utils <- "scripts/utils.R"
  shared_market_profiles <- "notebooks/retail_opportunity_finder/sections/_shared/market_profiles.R"
  shared_config <- "notebooks/retail_opportunity_finder/sections/_shared/config.R"
  shared_helpers <- "notebooks/retail_opportunity_finder/sections/_shared/helpers.R"
  platform_helpers <- "notebooks/retail_opportunity_finder/data_platform/shared/platform_helpers.R"

  if (!file.exists(project_utils)) {
    stop("Missing required runtime file: scripts/utils.R", call. = FALSE)
  }
  if (!file.exists(shared_market_profiles)) {
    stop("Missing shared market profiles file.", call. = FALSE)
  }
  if (!file.exists(shared_config)) {
    stop("Missing section config file.", call. = FALSE)
  }
  if (!file.exists(shared_helpers)) {
    stop("Missing section helpers file.", call. = FALSE)
  }
  if (!file.exists(platform_helpers)) {
    stop("Missing data platform helper file.", call. = FALSE)
  }

  source(project_utils)
  source(shared_market_profiles)
  source(shared_config)
  source(shared_helpers)
  source(platform_helpers)

  invisible(TRUE)
}
