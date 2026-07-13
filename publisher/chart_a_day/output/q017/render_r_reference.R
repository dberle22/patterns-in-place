suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q017")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_slopegraph.R")
source("visual_library/shared/render/render_slopegraph.R")

short_names <- c(
  "New York-Newark-Jersey City, NY-NJ" = "New York",
  "Los Angeles-Long Beach-Anaheim, CA" = "Los Angeles",
  "Chicago-Naperville-Elgin, IL-IN" = "Chicago",
  "Dallas-Fort Worth-Arlington, TX" = "Dallas-Fort Worth",
  "Houston-Pasadena-The Woodlands, TX" = "Houston",
  "Washington-Arlington-Alexandria, DC-VA-MD-WV" = "Washington, DC",
  "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD" = "Philadelphia",
  "Atlanta-Sandy Springs-Roswell, GA" = "Atlanta",
  "Miami-Fort Lauderdale-West Palm Beach, FL" = "Miami",
  "Phoenix-Mesa-Chandler, AZ" = "Phoenix",
  "Boston-Cambridge-Newton, MA-NH" = "Boston",
  "San Francisco-Oakland-Fremont, CA" = "San Francisco",
  "Riverside-San Bernardino-Ontario, CA" = "Riverside",
  "Detroit-Warren-Dearborn, MI" = "Detroit",
  "Seattle-Tacoma-Bellevue, WA" = "Seattle"
)

result_df <- as.data.frame(readr::read_csv(result_path, show_col_types = FALSE))
result_df$geo_name <- ifelse(
  result_df$geo_name %in% names(short_names),
  unname(short_names[result_df$geo_name]),
  result_df$geo_name
)
side_note <- unique(stats::na.omit(result_df$note))[[1]]

slope_df <- prep_slopegraph(
  result_df,
  config = list(
    metric_id = "rent_to_income",
    start_period = "2018",
    end_period = "2023",
    variant = "value",
    order_by = "end_value",
    sort_desc = TRUE,
    drop_incomplete = TRUE
  )
)

slope_plot <- render_slopegraph(
  slope_df,
  config = list(
    title = "How did the rent-to-income ratio change between 2018 and 2023 in the 15 largest metros?",
    subtitle = "Top 15 CBSAs by 2023 population | Rare affordability improvements are highlighted",
    label_style = "number",
    label_accuracy = 0.1,
    label_mode = "highlight_end",
    label_max_chars = 24,
    show_delta_labels = TRUE,
    right_margin_pt = 160,
    side_note = side_note
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = slope_plot,
  width = 12,
  height = 8,
  dpi = 300,
  bg = "white"
)
