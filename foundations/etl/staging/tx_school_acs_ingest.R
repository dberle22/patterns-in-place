# In this script we get our ACS Raw data

# Find our current directory 
getwd()

# Set up our environment ----
# Read our common libraries & set other packages
source(here::here("foundations", "etl", "utils.R"))


# Set paths for our environments
# Make sure we're reading from the project Renviron
if (file.exists(".Renviron")) readRenviron(".Renviron")

# Set our Paths - Pointing to our Bronze folder in Data
bronze_acs <- get_env_path("DATA_DEMO_RAW")
db_path <- get_env_path("DB_PATH")

# Connect to the DB ----
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)

# Load ACS Vars ----
acs_v23 <- load_variables(year = '2023', dataset = "acs5", cache = TRUE)

# Create our Vars mapping ----
# Demographics, Poverty, Income, Education Rates

vars <- c(
  pop_total              = "B01001_001",
  median_age             = "B01002_001",
  
  # Population
  pop_male_total         = "B01001_002",
  pop_age_male_under5    = "B01001_003",
  pop_age_male_5_9       = "B01001_004",
  pop_age_male_10_14     = "B01001_005",
  pop_age_male_15_17     = "B01001_006",
  pop_age_male_18_19     = "B01001_007",
  pop_age_male_20        = "B01001_008",
  pop_age_male_21        = "B01001_009",
  pop_age_male_22_24     = "B01001_010",
  pop_age_male_25_29     = "B01001_011",
  pop_age_male_30_34     = "B01001_012",
  pop_age_male_35_39     = "B01001_013",
  pop_age_male_40_44     = "B01001_014",
  pop_age_male_45_49     = "B01001_015",
  pop_age_male_50_54     = "B01001_016",
  pop_age_male_55_59     = "B01001_017",
  pop_age_male_60_61     = "B01001_018",
  pop_age_male_62_64     = "B01001_019",
  pop_age_male_65_66     = "B01001_020",
  pop_age_male_67_69     = "B01001_021",
  pop_age_male_70_74     = "B01001_022",
  pop_age_male_75_79     = "B01001_023",
  pop_age_male_80_84     = "B01001_024",
  pop_age_male_85_plus   = "B01001_025",
  pop_female_total       = "B01001_026",
  pop_age_female_under5  = "B01001_027",
  pop_age_female_5_9     = "B01001_028",
  pop_age_female_10_14   = "B01001_029",
  pop_age_female_15_17   = "B01001_030",
  pop_age_female_18_19   = "B01001_031",
  pop_age_female_20      = "B01001_032",
  pop_age_female_21      = "B01001_033",
  pop_age_female_22_24   = "B01001_034",
  pop_age_female_25_29   = "B01001_035",
  pop_age_female_30_34   = "B01001_036",
  pop_age_female_35_39   = "B01001_037",
  pop_age_female_40_44   = "B01001_038",
  pop_age_female_45_49   = "B01001_039",
  pop_age_female_50_54   = "B01001_040",
  pop_age_female_55_59   = "B01001_041",
  pop_age_female_60_61   = "B01001_042",
  pop_age_female_62_64   = "B01001_043",
  pop_age_female_65_66   = "B01001_044",
  pop_age_female_67_69   = "B01001_045",
  pop_age_female_70_74   = "B01001_046",
  pop_age_female_75_79   = "B01001_047",
  pop_age_female_80_84   = "B01001_048",
  pop_age_female_85_plus = "B01001_049",
  
  # Poverty Rate
  pov_universe = "B17001_001",
  pov_below = "B17001_002",
  pov_below_male_u5 = "B17001_004",
  pov_below_male_5 = "B17001_005",
  pov_below_male_6_11 = "B17001_006",
  pov_below_male_12_14 = "B17001_007",
  pov_below_male_15 = "B17001_008",
  pov_below_male_16_17 = "B17001_009",
  pov_below_female_u5 = "B17001_018",
  pov_below_female_5 = "B17001_019",
  pov_below_female_6_11 = "B17001_020",
  pov_below_female_12_14 = "B17001_021",
  pov_below_female_15 = "B17001_022",
  pov_below_female_16_17 = "B17001_023",
  
  # Median Income
  median_income = "B19013_001",
  
  # Education
  edu_total_25p               = "B15003_001",
  edu_no_schooling            = "B15003_002",
  edu_nursery                 = "B15003_003",
  edu_kindergarten            = "B15003_004",
  edu_grade1                  = "B15003_005",
  edu_grade2                  = "B15003_006",
  edu_grade3                  = "B15003_007",
  edu_grade4                  = "B15003_008",
  edu_grade5                  = "B15003_009",
  edu_grade6                  = "B15003_010",
  edu_grade7                  = "B15003_011",
  edu_grade8                  = "B15003_012",
  edu_grade9                  = "B15003_013",
  edu_grade10                 = "B15003_014",
  edu_grade11                 = "B15003_015",
  edu_grade12_no_diploma      = "B15003_016",
  edu_hs_diploma              = "B15003_017",
  edu_ged_alt_credential      = "B15003_018",
  edu_some_college_lt1yr      = "B15003_019",
  edu_some_college_ge1yr      = "B15003_020",
  edu_associates              = "B15003_021",
  edu_bachelors               = "B15003_022",
  edu_masters                 = "B15003_023",
  edu_professional            = "B15003_024",
  edu_doctorate               = "B15003_025",
  
  # Race
  pop_total_b03002     = "B03002_001",
  white_nonhisp        = "B03002_003",
  black_nonhisp        = "B03002_004",
  amind_nonhisp        = "B03002_005",
  asian_nonhisp        = "B03002_006",
  pacisl_nonhisp       = "B03002_007",
  other_nonhisp        = "B03002_008",
  two_plus_nonhisp     = "B03002_009",
  hispanic_any         = "B03002_012",
  
  # Households w/ Children
  total_households = "B11005_001",
  households_w_children = "B11005_002",
  households_no_children = "B11005_011"
)



# Ingest Data ----
school_tx_acs_raw <- acs_ingest(
  geography = "school district (unified)",
  state = 'TX',
  years     = 2012:2023,
  variables = vars,
  survey    = "acs5",
  output    = "wide"
)

school_tx_acs_clean <- standardize_acs_df(school_tx_acs_raw, 
                                          "School District (Unified)",
                                          drop_e = TRUE)

school_tx_acs_metrics <- school_tx_acs_clean %>%
  transmute(
    geo_level = geo_level,
    geo_id = geo_id,
    geo_name = geo_name,
    year = year,
    population = pop_total,
    median_age = median_age,
    median_income = median_income,
    child_poverty_rate = (
    pov_below_male_u5 + pov_below_male_5 + pov_below_male_6_11 +
    pov_below_male_12_14 + pov_below_male_15 + pov_below_male_16_17 +
    pov_below_female_u5 + pov_below_female_5 + pov_below_female_6_11 +
    pov_below_female_12_14 + pov_below_female_15 + pov_below_female_16_17
  ) / (
    pop_age_male_under5 + pop_age_male_5_9 + pop_age_male_10_14 + 
      pop_age_male_15_17 +
      pop_age_female_under5 + pop_age_female_5_9 + pop_age_female_10_14 + 
      pop_age_female_15_17
  ),
  edu_assoc_share = edu_associates / edu_total_25p,
  edu_bach_share = edu_bachelors / edu_total_25p,
  edu_masters_plus = 
    (edu_masters + edu_professional + edu_doctorate) / edu_total_25p,
  edu_no_higher_ed = 1 - (edu_assoc_share + edu_bach_share + edu_masters_plus),
  households_w_children_share = households_w_children / total_households,
    # Diversity - Calculate Race Shares then get the sum of squares 
  white_nonhisp_share = white_nonhisp / pop_total_b03002,
  black_nonhisp_share        = black_nonhisp / pop_total_b03002,
  amind_nonhisp_share        = amind_nonhisp / pop_total_b03002,
  asian_nonhisp_share        = asian_nonhisp / pop_total_b03002,
  pacisl_nonhisp_share       = pacisl_nonhisp / pop_total_b03002,
  other_nonhisp_share        = other_nonhisp / pop_total_b03002,
  two_plus_nonhisp_share     = two_plus_nonhisp / pop_total_b03002,
  hispanic_any_share         = hispanic_any / pop_total_b03002,
  racial_diversity_index = white_nonhisp_share^2 + black_nonhisp_share^2 + amind_nonhisp_share ^2 +
    asian_nonhisp_share^2 + pacisl_nonhisp_share^2 + other_nonhisp_share^2 + 
    two_plus_nonhisp_share^2 + hispanic_any_share^2
  )



# Name tables Source <> KPI <> Gran
dbWriteTable(con, 
             DBI::Id(schema = "silver", table = "acs_tx_school_metrics"),
             school_tx_acs_metrics, 
             overwrite = TRUE)

dbDisconnect(con, shutdown = TRUE)