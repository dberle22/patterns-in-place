library(here)
library(DBI)
library(duckdb)
library(dplyr)
library(tidyr)
library(purrr)
library(readr)
library(arrow)
library(yaml)
library(tibble)
library(cli)

if (Sys.getenv("DB_PATH") == "" && file.exists(here(".Renviron"))) {
  readRenviron(here(".Renviron"))
}

source(here("exploration/intelligence_framework/R/utils.R"))
source(here("exploration/intelligence_framework/phase_6_trajectory/R/phase6_config.R"))

run_phase6_trajectory <- function() {
  cli::cli_h1("Run Phase 6 Trajectory")

  config <- phase6_trajectory_config()
  con <- db_connect()
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  phase6_config <<- config
  assign("con", con, envir = .GlobalEnv)

  source(here::here(
    "exploration",
    "intelligence_framework",
    "phase_6_trajectory",
    "R",
    "phase6_frame_build.R"
  ), local = .GlobalEnv)
  source(here::here(
    "exploration",
    "intelligence_framework",
    "phase_6_trajectory",
    "R",
    "phase6_trajectory_core.R"
  ), local = .GlobalEnv)
  source(here::here(
    "exploration",
    "intelligence_framework",
    "phase_6_trajectory",
    "R",
    "phase6_opportunity_turn_signals.R"
  ), local = .GlobalEnv)
  source(here::here(
    "exploration",
    "intelligence_framework",
    "phase_6_trajectory",
    "R",
    "phase6_patterns.R"
  ), local = .GlobalEnv)
  source(here::here(
    "exploration",
    "intelligence_framework",
    "phase_6_trajectory",
    "R",
    "phase6_candidate_list.R"
  ), local = .GlobalEnv)

  cli::cli_alert_success(
    "Phase 6 runner finished. Wrote canonical outputs to {.file {config$output_dir}}."
  )

  invisible(
    list(
      config = phase6_config,
      frame_build = phase6_frame_build_bundle,
      trajectory_core = phase6_trajectory_core_bundle,
      patterns = phase6_patterns_bundle,
      candidate_list = phase6_candidate_list
    )
  )
}

if (sys.nframe() == 0) {
  run_phase6_trajectory()
}
