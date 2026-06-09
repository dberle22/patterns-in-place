# In this script we model ACS language data to Silver
#
# The staging family lands the full ACS B16001 language table across the
# standard geography ladder. This Silver step standardizes those wide source
# fields, rebases county counts to CBSA, and then derives a smaller KPI table
# that summarizes English proficiency and broad language families.

# 1. Set up our Environment ----
getwd()

here::i_am("foundations/etl/silver/acs_language_silver.R")
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

bronze_acs <- get_env_path("DATA_DEMO_RAW")
db_path <- get_env_path("DB_PATH")

con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# 2. Read staging ACS language slices ----
us_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_language_us")
region_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_language_region")
division_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_language_division")
state_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_language_state")
county_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_language_county")
place_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_language_place")
zcta_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_language_zcta")
tract_acs_stage <- dbGetQuery(con, "SELECT * FROM staging.acs_language_tract")

cbsa_county_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_cbsa_county")

# 3. Standardize geography fields and remove MOE columns ----
us_acs_clean <- standardize_acs_df(us_acs_stage, "US", drop_e = FALSE)
region_acs_clean <- standardize_acs_df(region_acs_stage, "Region")
division_acs_clean <- standardize_acs_df(division_acs_stage, "division")
state_acs_clean <- standardize_acs_df(state_acs_stage, "state")
county_acs_clean <- standardize_acs_df(county_acs_stage, "county")
place_acs_clean <- standardize_acs_df(place_acs_stage, "place")
zcta_acs_clean <- standardize_acs_df(zcta_acs_stage, "zcta")
tract_acs_clean <- standardize_acs_df(tract_acs_stage, "tract")

# 4. Rebase county counts to CBSA ----
# The language table is fully count-based, so the CBSA rollup is a direct sum
# across county members.
cbsa_acs_clean <- county_acs_clean %>%
  inner_join(
    cbsa_county_xwalk %>% dplyr::select(cbsa_code, cbsa_name, county_geoid),
    by = c("geo_id" = "county_geoid")
  ) %>%
  sum_pops_by_cbsa(pop_pattern = "language_") %>%
  mutate(geo_level = "cbsa") %>%
  select(
    geo_level,
    geo_id = cbsa_code,
    geo_name = cbsa_name,
    year,
    language_totalE:language_other_and_unspecified_languages_speak_english_less_than_very_wellE
  )

# 5. Build the base and KPI tables ----
language_base <- dplyr::bind_rows(
  us_acs_clean,
  region_acs_clean,
  division_acs_clean,
  state_acs_clean,
  cbsa_acs_clean,
  county_acs_clean,
  place_acs_clean,
  zcta_acs_clean,
  tract_acs_clean
) %>%
  select(-any_of("state"))

language_kpi <- language_base %>%
  mutate(
    language_total = language_totalE,
    language_english_only = language_speak_only_englishE,
    language_non_english = language_totalE - language_speak_only_englishE,
    language_limited_english = language_spanish_speak_english_less_than_very_wellE +
      language_french_incl_cajun_speak_english_less_than_very_wellE +
      language_haitian_speak_english_less_than_very_wellE +
      language_italian_speak_english_less_than_very_wellE +
      language_portuguese_speak_english_less_than_very_wellE +
      language_german_speak_english_less_than_very_wellE +
      language_yiddish_pennsylvania_dutch_or_other_west_germanic_languages_speak_english_less_than_very_wellE +
      language_greek_speak_english_less_than_very_wellE +
      language_russian_speak_english_less_than_very_wellE +
      language_polish_speak_english_less_than_very_wellE +
      language_serbo_croatian_speak_english_less_than_very_wellE +
      language_ukrainian_or_other_slavic_languages_speak_english_less_than_very_wellE +
      language_armenian_speak_english_less_than_very_wellE +
      language_persian_incl_farsi_dari_speak_english_less_than_very_wellE +
      language_gujarati_speak_english_less_than_very_wellE +
      language_hindi_speak_english_less_than_very_wellE +
      language_urdu_speak_english_less_than_very_wellE +
      language_punjabi_speak_english_less_than_very_wellE +
      language_bengali_speak_english_less_than_very_wellE +
      language_nepali_marathi_or_other_indic_languages_speak_english_less_than_very_wellE +
      language_other_indo_european_languages_speak_english_less_than_very_wellE +
      language_telugu_speak_english_less_than_very_wellE +
      language_tamil_speak_english_less_than_very_wellE +
      language_malayalam_kannada_or_other_dravidian_languages_speak_english_less_than_very_wellE +
      language_chinese_incl_mandarin_cantonese_speak_english_less_than_very_wellE +
      language_japanese_speak_english_less_than_very_wellE +
      language_korean_speak_english_less_than_very_wellE +
      language_hmong_speak_english_less_than_very_wellE +
      language_vietnamese_speak_english_less_than_very_wellE +
      language_khmer_speak_english_less_than_very_wellE +
      language_thai_lao_or_other_tai_kadai_languages_speak_english_less_than_very_wellE +
      language_other_languages_of_asia_speak_english_less_than_very_wellE +
      language_tagalog_incl_filipino_speak_english_less_than_very_wellE +
      language_ilocano_samoan_hawaiian_or_other_austronesian_languages_speak_english_less_than_very_wellE +
      language_arabic_speak_english_less_than_very_wellE +
      language_hebrew_speak_english_less_than_very_wellE +
      language_amharic_somali_or_other_afro_asiatic_languages_speak_english_less_than_very_wellE +
      language_yoruba_twi_igbo_or_other_languages_of_western_africa_speak_english_less_than_very_wellE +
      language_swahili_or_other_languages_of_central_eastern_and_southern_africa_speak_english_less_than_very_wellE +
      language_navajo_speak_english_less_than_very_wellE +
      language_other_native_languages_of_north_america_speak_english_less_than_very_wellE +
      language_other_and_unspecified_languages_speak_english_less_than_very_wellE,
    language_spanish = language_spanishE,
    language_other_indo_european = language_french_incl_cajunE +
      language_haitianE +
      language_italianE +
      language_portugueseE +
      language_germanE +
      language_yiddish_pennsylvania_dutch_or_other_west_germanic_languagesE +
      language_greekE +
      language_russianE +
      language_polishE +
      language_serbo_croatianE +
      language_ukrainian_or_other_slavic_languagesE +
      language_armenianE +
      language_persian_incl_farsi_dariE +
      language_gujaratiE +
      language_hindiE +
      language_urduE +
      language_punjabiE +
      language_bengaliE +
      language_nepali_marathi_or_other_indic_languagesE +
      language_other_indo_european_languagesE,
    language_asian_pacific = language_teluguE +
      language_tamilE +
      language_malayalam_kannada_or_other_dravidian_languagesE +
      language_chinese_incl_mandarin_cantoneseE +
      language_japaneseE +
      language_koreanE +
      language_hmongE +
      language_vietnameseE +
      language_khmerE +
      language_thai_lao_or_other_tai_kadai_languagesE +
      language_other_languages_of_asiaE +
      language_tagalog_incl_filipinoE +
      language_ilocano_samoan_hawaiian_or_other_austronesian_languagesE,
    language_middle_eastern_african = language_arabicE +
      language_hebrewE +
      language_amharic_somali_or_other_afro_asiatic_languagesE +
      language_yoruba_twi_igbo_or_other_languages_of_western_africaE +
      language_swahili_or_other_languages_of_central_eastern_and_southern_africaE,
    language_native_north_american = language_navajoE +
      language_other_native_languages_of_north_americaE,
    language_other_unspecified = language_other_and_unspecified_languagesE
  ) %>%
  mutate(
    pct_english_only = language_english_only / dplyr::na_if(language_total, 0),
    pct_non_english = language_non_english / dplyr::na_if(language_total, 0),
    pct_limited_english = language_limited_english / dplyr::na_if(language_total, 0),
    pct_spanish = language_spanish / dplyr::na_if(language_total, 0),
    pct_other_indo_european = language_other_indo_european / dplyr::na_if(language_total, 0),
    pct_asian_pacific = language_asian_pacific / dplyr::na_if(language_total, 0),
    pct_middle_eastern_african = language_middle_eastern_african / dplyr::na_if(language_total, 0),
    pct_native_north_american = language_native_north_american / dplyr::na_if(language_total, 0),
    pct_other_unspecified = language_other_unspecified / dplyr::na_if(language_total, 0)
  ) %>%
  select(
    geo_level, geo_id, geo_name, year,
    language_total,
    language_english_only,
    language_non_english,
    language_limited_english,
    language_spanish,
    language_other_indo_european,
    language_asian_pacific,
    language_middle_eastern_african,
    language_native_north_american,
    language_other_unspecified,
    pct_english_only,
    pct_non_english,
    pct_limited_english,
    pct_spanish,
    pct_other_indo_european,
    pct_asian_pacific,
    pct_middle_eastern_african,
    pct_native_north_american,
    pct_other_unspecified
  )

# 6. Materialize to Silver ----
DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "language_base"),
  language_base,
  overwrite = TRUE
)

DBI::dbWriteTable(
  con,
  DBI::Id(schema = "silver", table = "language_kpi"),
  language_kpi,
  overwrite = TRUE
)

dbExecute(con, "CHECKPOINT")
dbDisconnect(con, shutdown = TRUE)
