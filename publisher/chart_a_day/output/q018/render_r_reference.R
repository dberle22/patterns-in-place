suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q018")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_bump_chart.R")
source("visual_library/shared/render/render_bump_chart.R")

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
  "Seattle-Tacoma-Bellevue, WA" = "Seattle",
  "Minneapolis-St. Paul-Bloomington, MN-WI" = "Minneapolis",
  "Denver-Aurora-Centennial, CO" = "Denver",
  "San Diego-Chula Vista-Carlsbad, CA" = "San Diego",
  "Baltimore-Columbia-Towson, MD" = "Baltimore",
  "Tampa-St. Petersburg-Clearwater, FL" = "Tampa"
)

result_df <- readr::read_csv(result_path, show_col_types = FALSE)
result_df$geo_name <- ifelse(
  result_df$geo_name %in% names(short_names),
  unname(short_names[result_df$geo_name]),
  result_df$geo_name
)
side_note <- unique(stats::na.omit(result_df$note))[[1]]

bump_df <- prep_bump_chart(
  result_df,
  config = list(
    metric_id = "vacancy_rate",
    periods = as.character(2015:2023),
    entity_strategy = "all",
    use_precomputed_rank = TRUE,
    drop_missing_rank = TRUE
  )
)

bump_plot <- render_bump_chart(
  bump_df,
  config = list(
    title = "How have the vacancy rate rankings among major metros shifted since 2015?",
    subtitle = "Top 20 CBSAs by 2023 population | Rank 1 = lowest vacancy rate | Biggest movers highlighted",
    label_mode = "highlight_end",
    label_style = "rank",
    label_max_chars = 22,
    label_include_value = FALSE,
    side_note = side_note
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = bump_plot,
  width = 12,
  height = 8,
  dpi = 300,
  bg = "white"
)
