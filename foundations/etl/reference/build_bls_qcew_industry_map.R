# Build a reproducible QCEW industry metadata seed from the published annual-by-industry ZIP.
#
# The raw annual archive publishes one CSV per industry member. We keep staging source-faithful,
# then use this metadata seed downstream to distinguish plain NAICS codes from BLS aggregate
# supersectors and to flag the smaller canonical subsets we may want in Silver later.

getwd()

source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

data <- get_env_path("DATA")
raw_dir <- file.path(data, "demographics", "raw", "bls", "qcew")
output_path <- here::here("foundations", "etl", "reference", "bls_qcew_industry_map.csv")
mapping_years <- 2010:2024

download_qcew_archive <- function(year) {
  zip_name <- glue("{year}_annual_by_industry.zip")
  zip_path <- file.path(raw_dir, zip_name)

  if (!file.exists(zip_path)) {
    zip_url <- glue("https://data.bls.gov/cew/data/files/{year}/csv/{zip_name}")

    resp <- httr::GET(
      zip_url,
      httr::user_agent("Mozilla/5.0 (compatible; R; +https://cran.r-project.org)")
    )
    httr::stop_for_status(resp)

    writeBin(httr::content(resp, "raw"), zip_path)
  }

  zip_path
}

member_catalog <- purrr::map_dfr(
  mapping_years,
  \(year_value) {
    zip_path <- download_qcew_archive(year_value)

    unzip(zip_path, list = TRUE) %>%
      tibble::as_tibble() %>%
      transmute(
        source_year = year_value,
        member_name = Name,
        member_file = basename(Name),
        industry_code = stringr::str_match(
          member_file,
          "^\\d{4}\\.annual\\s+([0-9-]+)\\s+.*\\.csv$"
        )[, 2],
        industry_title = stringr::str_match(
          member_file,
          "^\\d{4}\\.annual\\s+[0-9-]+\\s+(.*)\\.csv$"
        )[, 2]
      ) %>%
      filter(!is.na(industry_code), !is.na(industry_title))
  }
)

member_summary <- member_catalog %>%
  group_by(industry_code) %>%
  summarise(
    industry_title = dplyr::first(industry_title),
    first_seen_year = min(source_year),
    last_seen_year = max(source_year),
    years_present = paste(sort(unique(source_year)), collapse = "|"),
    member_count = n(),
    .groups = "drop"
  )

aggregate_component_map <- c(
  "10" = "",
  "31-33" = "31|32|33",
  "44-45" = "44|45",
  "48-49" = "48|49",
  "101" = "11|21|23|31-33",
  "1011" = "11|21",
  "1012" = "23",
  "1013" = "31-33",
  "102" = "22|42|44-45|48-49|51|52|53|54|55|56|61|62|71|72|81|92|99",
  "1021" = "22|42|44-45|48-49",
  "1022" = "51",
  "1023" = "52|53",
  "1024" = "54|55|56",
  "1025" = "61|62",
  "1026" = "71|72",
  "1027" = "81",
  "1028" = "92",
  "1029" = "99"
)

silver_keep_codes <- c(
  "10", "11", "21", "22", "23", "31-33", "42", "44-45", "48-49",
  "51", "52", "53", "54", "55", "56", "61", "62", "71", "72", "81", "92"
)

supersector_rollup_map <- c(
  "101" = "goods_producing",
  "1011" = "natural_resources_and_mining",
  "1012" = "construction",
  "1013" = "manufacturing",
  "102" = "service_providing",
  "1021" = "trade_transport_utilities",
  "1022" = "information",
  "1023" = "financial_activities",
  "1024" = "professional_business_services",
  "1025" = "education_health_services",
  "1026" = "leisure_hospitality",
  "1027" = "other_services",
  "1028" = "public_administration",
  "1029" = "unclassified"
)

industry_map <- member_summary %>%
  mutate(
    code_length = stringr::str_length(industry_code),
    code_type = case_when(
      industry_code == "10" ~ "total",
      industry_code %in% c("101", "102", "1011", "1012", "1013", "1021", "1022", "1023", "1024", "1025", "1026", "1027", "1028", "1029") ~ "supersector_aggregate",
      stringr::str_detect(industry_code, "^[0-9]{2}-[0-9]{2}$") ~ "naics_compound_sector",
      industry_code == "99" ~ "unclassified",
      stringr::str_detect(industry_code, "^[0-9]{2}$") ~ "naics_sector",
      stringr::str_detect(industry_code, "^[0-9]{3}$") ~ "naics_subsector",
      stringr::str_detect(industry_code, "^[0-9]{4}$") ~ "naics_industry_group",
      stringr::str_detect(industry_code, "^[0-9]{5}$") ~ "naics_industry",
      stringr::str_detect(industry_code, "^[0-9]{6}$") ~ "naics_national_industry",
      TRUE ~ "other"
    ),
    is_aggregate = code_type %in% c("total", "supersector_aggregate", "naics_compound_sector"),
    aggregate_components = dplyr::recode(industry_code, !!!aggregate_component_map, .default = ""),
    keep_in_staging = TRUE,
    keep_in_silver_canonical = industry_code %in% silver_keep_codes,
    silver_rollup_family = dplyr::recode(industry_code, !!!supersector_rollup_map, .default = ""),
    notes = case_when(
      industry_code == "10" ~ "Published total across all industries.",
      industry_code %in% c("31-33", "44-45", "48-49") ~ "Published compound NAICS sector.",
      code_type == "supersector_aggregate" ~ "Published BLS aggregate that overlaps leaf NAICS coverage.",
      industry_code %in% c("999", "9999", "99999", "999999") ~ "Unclassified ladder; retain in staging for source fidelity.",
      TRUE ~ ""
    )
  ) %>%
  arrange(
    factor(
      code_type,
      levels = c(
        "total",
        "supersector_aggregate",
        "naics_compound_sector",
        "naics_sector",
        "naics_subsector",
        "naics_industry_group",
        "naics_industry",
        "naics_national_industry",
        "unclassified",
        "other"
      )
    ),
    code_length,
    industry_code
  )

readr::write_csv(industry_map, output_path, na = "")

message("Wrote QCEW industry map: ", output_path)
message("Rows: ", nrow(industry_map))
