#!/usr/bin/env Rscript

# Batch runner for all first-pass Vacancy visuals.
# This keeps section reruns simple while preserving the one-script-per-visual
# production pattern.

visual_scripts <- c(
  "publisher/content/housing/01_vacancy/visuals/state_vacancy_map.R",
  "publisher/content/housing/01_vacancy/visuals/cbsa_vacancy_boxplot_region.R",
  "publisher/content/housing/01_vacancy/visuals/cbsa_vacancy_boxplot_division.R",
  "publisher/content/housing/01_vacancy/visuals/cbsa_vacancy_tightest.R",
  "publisher/content/housing/01_vacancy/visuals/cbsa_vacancy_loosest.R",
  "publisher/content/housing/01_vacancy/visuals/vacancy_trend_regions.R",
  "publisher/content/housing/01_vacancy/visuals/vacancy_trend_divisions.R"
)

for (script in visual_scripts) {
  message(sprintf("Running %s", script))
  status <- system2("Rscript", script)
  if (!identical(status, 0L)) {
    stop(sprintf("Render failed for %s", script), call. = FALSE)
  }
}

message("Vacancy render complete.")
