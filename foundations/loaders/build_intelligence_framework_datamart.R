loader_scripts <- c(
  "load_character_scores.R",
  "load_livability_scores.R",
  "load_opportunity_scores.R",
  "load_cross_frame_scores.R",
  "load_zone_assignments.R",
  "load_zone_scores_zcta.R"
)

for (script_name in loader_scripts) {
  script_path <- here::here("foundations", "loaders", script_name)
  message(sprintf("Running %s", script_name))
  source(script_path, local = new.env(parent = globalenv()))
}
