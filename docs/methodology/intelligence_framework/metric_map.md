# Metric Map

Here we outline our main metrics by Theme and Sub-Topic. We start at a Theme and Sub-Topic level to think through what data may be relevant, then we identify the source and gold table we can retrieve the data from. This provides us an extra audit layer before we get into building our analyses.

## Character

The main Sub-Topics we're analyzing here are:
- Demographics
- Social fabric & civic identity
- Recreation & cultural amenities

### Demographics
The basic makeup of an area.

- Race
    - Source: ACS Race
    - Gold: `gold.population_demographics`
    - Columns: `pct_white_nh`, `pct_black_nh`, `pct_aian_nh`, `pct_asian_nh`, `pct_nhpi_nh`, `pct_hispanic`, `diversity_index`
- Age
    - Source: ACS Age
    - Gold: `gold.population_demographics`
    - Columns: `median_age`, `pct_age_under_18`, `pct_age_18_64`, `pct_age_over_64`
- Educational Attainment
    - Source: ACS Education
    - Gold: `gold.population_demographics`
    - Columns: `pct_hs_or_less`, `pct_ba`, `pct_ba_plus`, `pct_grad_plus`
- Foreign Born
    - Source: ACS (via migration family)
    - Gold: `gold.migration_wide`
    - Columns: `pct_foreign_born`, `pct_non_citizen`
- Population Density
    - Source: ACS
    - Gold: `gold.transport_built_form_wide`
    - Columns: `pop_weighted_density_sqmi`, `gross_density_sqmi`
    - Notes: More relevant for in-market analyses. `pop_weighted_density_sqmi` weights density by where people actually live.

### Social Fabric & civic identity
How engaged the population is in a shared civic responsibility.

- Voting Rates - Midterm Elections
    - Source: MIT Election Lab
    - Status: Deferred — Track 21.1 not started. County-level data requires VAP denominator from CVAP; clean historical series needed before this metric is usable.
- Social Capital (Economic Connectedness, Civic Engagement)
    - Source: Opportunity Insights Social Capital Atlas
    - Gold: `gold.social_fabric_wide`
    - Columns: `economic_connectedness`, `friending_bias`, `cohesion_clustering`, `cohesion_support_ratio`, `civic_engagement_volunteering_rate`, `civic_organizations_per_1000`
    - Additional sub-indices: `childhood_economic_connectedness`, `neighborhood_economic_connectedness`, `childhood_friending_bias`, `neighborhood_friending_bias`
    - Notes: Static baseline (2022 release). `economic_connectedness` is the headline cross-class social ties measure. `friending_bias` captures the degree to which low-SES individuals friend high-SES individuals less than expected.
- Nonprofits per 100k
    - Source: IRS Business Master File
    - Gold: `gold.social_fabric_wide`
    - Columns: `nonprofits_per_100k`, `nonprofits_total_per_100k`
    - Notes: Latest snapshot; county and CBSA only.
- Residential Stability
    - Source: ACS (via migration family)
    - Gold: `gold.migration_wide`
    - Columns: `pct_same_house`, `mobility_rate`, `pct_moved_same_cnty`, `pct_moved_same_st`, `pct_moved_diff_st`, `pct_moved_abroad`
- Residential Stability (IRS migration direction / churn)
    - Source: IRS Migration
    - Gold: `gold.migration_wide`
    - Columns: `irs_net_migration`, `irs_net_migration_rate`
    - Notes: Keep the migration-count and migration-rate signals in Character as rootedness / churn indicators. Move the AGI flow fields to Opportunity, where they fit better as market / investor momentum signals.
- Single-person household share
    - Source: ACS B11001
    - Gold: `gold.social_infra_wide`
    - Columns: `pct_hh_single_person`
- Single-parent family share
    - Source: ACS B11003
    - Gold: `gold.social_infra_wide`
    - Columns: `pct_family_single_parent`
- Social Associations per 10k
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `social_associations_per_10k`
- Violent Crime / Homicide Rate
    - Source: CHR (CDC WONDER death records)
    - Gold: `gold.health_wide`
    - Columns: `homicide_rate`
    - Notes: CHR preferred over FBI UCR at county grain (Track 8 skipped). Use as Social Fabric proxy alongside firearm fatality rate.

### Recreation & cultural amenities
Deferred entirely until Points layer ingestion is available (Track 16/17). No Gold coverage currently.

- Green Space / Park Access
    - Source: CHR (proxy only)
    - Gold: `gold.health_wide`
    - Columns: `pct_access_to_parks`
    - Notes: CHR provides a crude county-level access proxy. Full spatial coverage deferred to Points layer.
- Entertainment Venues, Museums, Libraries, Nightlife
    - Source: OSM, Overture Maps, IMLS
    - Status: Deferred — Track 16/17 (Points layer framework, depends on Stoop migration)
- Number of Universities / University Rankings
    - Source: IPEDS (Points layer)
    - Status: Deferred — Track 10 / Track 16

---

## Livability

The main Sub-Topics are the following:
- Affordability
- Health
- Safety
- Access & Infrastructure (transit, walkability, food, basic services)
- Education access
- Physical Environment

### Affordability
Can someone afford to live here?

- Rent-to-Income
    - Source: ACS
    - Gold: `gold.affordability_wide`
    - Columns: `rent_to_income`
- Home Price to Income
    - Source: ACS
    - Gold: `gold.affordability_wide`
    - Columns: `value_to_income`
- Housing Cost Burden
    - Source: HUD CHAS
    - Gold: `gold.affordability_wide`
    - Columns: `pct_cost_burdened`, `pct_severely_cost_burdened`, `pct_renter_severely_cost_burdened`
    - Notes: These are the CHAS burden fields. They are not the same as the recurring ACS rent-burden panel below.
- Rent Burden
    - Source: ACS
    - Gold: `gold.affordability_wide` (also present in `gold.housing_core_wide`)
    - Columns: `pct_rent_burden_30plus`, `pct_rent_burden_50plus`
    - Notes: Use `pct_rent_burden_30plus` as the recurring CBSA affordability-burden input for Phase 1.
- Cost of Living (RPP-adjusted)
    - Source: BEA RPP
    - Gold: `gold.affordability_wide`
    - Columns: `rpp_real_pc_income`
    - Notes: Use to normalize income for cross-metro comparability.
- Poverty Rate
    - Source: ACS B17001
    - Gold: `gold.economics_income_wide`
    - Columns: `pov_rate`, `pov_rate_change_1yr`, `pov_rate_change_5yr`
    - Notes: Also available in `gold.housing_core_wide` as `pov_rate` (level only).
- Housing Supply
    - Source: BPS (building permits)
    - Gold: `gold.housing_core_wide` (primary — full permit detail); `gold.affordability_wide` (headline rates only)
    - Columns: `permits_per_1000_housing_units`, `permits_per_1000_population`, `permits_share_multifam_units`, `permits_share_units_5_plus`, `permits_avg_units_per_bldg`, `permits_structure_mix`
    - Notes: `housing_core_wide` has the full permit breakdown including `permits_multifam_units`, `permits_avg_units_per_mf_bldg`, `permits_total_units`. Use `permits_share_multifam_units` + `permits_avg_units_per_bldg` as the density-of-supply signal.
- Housing Structure Mix
    - Source: ACS
    - Gold: `gold.housing_core_wide`
    - Columns: `pct_struct_multifam`, `pct_struct_sf_det`, `pct_struct_small_mf`, `pct_struct_mid_mf`, `pct_struct_large_mf`, `pct_struct_mobile`
    - Notes: Structural composition of existing housing stock — distinct from permit activity (future supply).

### Health
How healthy is this community?

- Life Expectancy
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `life_expectancy`, `life_expectancy_change_1yr`, `life_expectancy_change_5yr`
- Premature Death Rate
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `premature_death_rate`, `premature_death_rate_change_1yr`, `premature_death_rate_change_5yr`
- Child and Infant Mortality
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `child_mortality_rate`, `infant_mortality_rate`
- Drug Overdoses
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `drug_overdose_death_rate`
- Insurance Rates
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `pct_uninsured_adults`, `pct_uninsured_adults_change_1yr`, `pct_uninsured_adults_change_5yr`
    - Notes: ACS-based uninsured rate also available in `gold.social_infra_wide` (`pct_health_uninsured`) for tract-level analyses.
- Preventable Hospital Stay Rate
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `preventable_hospital_stay_rate`, `preventable_hospital_stay_rate_change_5yr`
- Primary Care Access
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `primary_care_ratio`, `primary_care_ratio_change_5yr`, `mental_health_provider_ratio`
- Physical Inactivity
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `physical_inactivity`, `physical_inactivity_change_5yr`
- Obesity Rate
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `adult_obesity`, `adult_obesity_change_5yr`
- Poor Mental Health Days
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `poor_mental_health_days`, `poor_mental_health_days_change_5yr`
- Food Insecurity Rate
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `food_insecurity_rate`
- Child Care Cost Burden
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `child_care_cost_burden_rate`

### Safety

- Homicide Rate
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `homicide_rate`
- Firearms Fatality Rate
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `firearm_fatality_rate`
- Motor Vehicle Crash Rate
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `motor_vehicle_crash_rate`

### Access & Infrastructure

- Mean Travel Time to Work
    - Source: ACS
    - Gold: `gold.transport_built_form_wide`
    - Columns: `mean_travel_time`
- Transit Commute Share
    - Source: ACS
    - Gold: `gold.transport_built_form_wide`
    - Columns: `pct_commute_transit`, `pct_commute_walk`, `pct_commute_wfh`
- Vehicle Access
    - Source: ACS
    - Gold: `gold.transport_built_form_wide`
    - Columns: `pct_hh_0_vehicles`
- Walkability / Transit Accessibility / Jobs Accessibility
    - Source: EPA Smart Location Database
    - Gold: `gold.transport_built_form_sld`
    - Notes: 2021 vintage; county-only first pass. Block-group → county aggregation. Tract-level recovery deferred.
- Population Density
    - Source: ACS
    - Gold: `gold.population_demographics`
    - Columns: `pop_total` (density derivable at CBSA/county grain using area from dim_geo)
- Vacancy Rate
    - Source: ACS
    - Gold: `gold.housing_core_wide`
    - Columns: `vacancy_rate`
    - Notes: Slack in the housing market. High vacancy = soft market; low vacancy = supply-constrained.
- Broadband Access
    - Source: ACS B28002
    - Gold: `gold.social_infra_wide`
    - Columns: `pct_broadband_subscription`, `pct_no_internet_access`
    - Notes: Available 2017+. Question wording changed 2019 — treat pre/post 2019 with care.
- Food Access
    - Source: USDA Food Access Research Atlas
    - Gold: `gold.food_access_wide`
    - Notes: 2019 vintage; tract, county, and CBSA grain. Tract-native based on 2010 tracts.

### Education

- HS Graduation Rate
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `hs_graduation_rate`
- Math Scores
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `math_score_index`
- Reading Scores
    - Source: CHR
    - Gold: `gold.health_wide`
    - Columns: `reading_score_index`
- K-12 Learning Quality
    - Source: Stanford SEDA
    - Status: Deferred — Track 22 (depends on Track 15 NCES CCD for district-county crosswalk)

### Physical Environment

- Air Pollution
    - Source: CHR (lagged proxy)
    - Gold: `gold.health_wide`
    - Columns: `air_pollution_pm25`, `air_pollution_pm25_change_5yr`
    - Source: EPA AQI + EJScreen
    - Gold: `gold.environment_wide`
    - Columns: `aqi_median`, `aqi_p90`, `aqi_unhealthy_days`, `ej_pm25`, `ej_ozone`, `ej_diesel_pm`
    - Notes: AQI available 2016–2025 (county + CBSA); EJScreen 2024 only (tract-aggregated to county/CBSA).
- Environmental Hazard Exposure
    - Source: EPA EJScreen
    - Gold: `gold.environment_wide`
    - Columns: `ej_traffic_proximity`, `ej_superfund_proximity`, `ej_rmp_proximity`, `ej_wastewater_discharge`, `ej_drinking_water_noncompliance`
- Adverse Weather / Climate Hazard Risk
    - Source: CHR (proxy)
    - Gold: `gold.health_wide`
    - Columns: `adverse_climate_events`
    - Source: FEMA National Risk Index
    - Gold: `gold.environment_wide`
    - Columns: `fema_risk_score`, `fema_eal_score`, per-hazard risk scores (18 hazard types)
    - Notes: FEMA NRI ingested (Track 7 complete). 2025 vintage; county + derived CBSA.

---

## Opportunity

Trajectory-focused. About economic momentum, market signals, and whether conditions are improving for residents, investors, and businesses.

### Resident Opportunities

- Income Growth (1yr, 5yr)
    - Source: BEA CAINC
    - Gold: `gold.economics_income_wide`
    - Columns: `income_pc_growth_1yr`, `income_pc_growth_5yr`, `income_pc_cagr_5yr`
    - Notes: Use RPP-adjusted version (`rpp_real_pc_income` in `gold.affordability_wide`) for cross-metro comparability.
- Wage Levels
    - Source: BLS QCEW
    - Gold: `gold.economics_industry_wide`
    - Columns: `qcew_total_covered_avg_wkly_wage`, `qcew_private_avg_wkly_wage`
    - Notes: Employer-side wage signal. Complement with `pi_wages_salary` in income_wide for the income-flows picture.
- Unemployment Rate & Labor Force Participation Rate
    - Source: BLS LAUS / ACS
    - Gold: `gold.economics_labor_wide`
    - Columns: `pct_unemployment_rate`, `lfpr`, `lfpr_growth_5yr`, `unemployment_rate_change_1yr`
- Poverty Rate Change
    - Source: ACS B17001
    - Gold: `gold.economics_income_wide`
    - Columns: `pov_rate`, `pov_rate_change_1yr`, `pov_rate_change_5yr`
- Gini Index (Income Inequality)
    - Source: ACS
    - Gold: `gold.economics_income_wide`
    - Columns: `gini_index`
    - Notes: Primary home is Opportunity (is growth inclusive?); also relevant to Livability health outcomes per Wilkinson & Pickett.
- Intergenerational Mobility
    - Source: Opportunity Insights — Opportunity Atlas
    - Status: Deferred — Track 14 (Opportunity Atlas portion). Social Capital Atlas economic connectedness is a meaningful proxy already in Gold. Resume if deeper mobility analysis is needed post Phase 1.

### Market / Investor Opportunity

- Home Price Appreciation
    - Source: FHFA HPI
    - Gold: `gold.housing_market_wide`
    - Columns: `hpi_yoy_pct`, `hpi_5yr_pct`, `hpi_10yr_pct`
- Rent Growth
    - Source: Zillow ZORI
    - Gold: `gold.housing_market_wide`
    - Columns: `zori_annual_avg`, `zori_annual_avg_yoy_pct`, `zori_december`, `zori_december_yoy_pct`
- Population Growth
    - Source: ACS
    - Gold: `gold.population_demographics`
    - Columns: `pop_growth_1yr`, `pop_growth_5yr`, `pop_cagr_5yr`
- Migration & Wealth Flows
    - Source: IRS
    - Gold: `gold.migration_wide`
    - Columns: `irs_net_migration_rate`, `irs_net_agi`, `irs_inflow_agi`, `irs_outflow_agi`
    - Notes: `irs_net_agi` is the key investor signal — are high-income households net moving in or out? `irs_net_migration_rate` stays relevant here as a market-demand companion to the wealth-flow story, even though it is also useful in Character as a migration-churn signal.
- Permit Activity (supply momentum)
    - Source: BPS
    - Gold: `gold.housing_core_wide` (primary); `gold.affordability_wide` (headline rates)
    - Columns: `permits_per_1000_housing_units`, `permits_per_1000_population`, `permits_share_multifam_units`, `permits_share_units_5_plus`
    - Notes: Forward-looking supply signal. Cross-reference with `vacancy_rate` and `hpi_yoy_pct` to distinguish supply-response vs. speculative building.

### Business & Industry Opportunity

- GDP Growth
    - Source: BEA CAGDP
    - Gold: `gold.economics_gdp_wide`
    - Columns: `real_gdp_growth_5yr`, `real_gdp_cagr_5yr`, `real_gdp_pc`, `real_gdp_pc_growth_5yr`, `productivity_growth_5yr`
    - Notes: Use real (inflation-adjusted) GDP. `productivity_growth_5yr` is the cleanest long-run economic health signal.
- Industry Concentration
    - Source: BEA CAGDP9 (via industry_wide)
    - Gold: `gold.economics_industry_wide`
    - Columns: `industry_concentration_hhi`
    - Notes: Derived from BEA GDP shares. Lower HHI = more diversified = more resilient to sector shocks.
- Sector Share Changes
    - Source: BLS QCEW + BEA CAGDP9
    - Gold: `gold.economics_industry_wide`
    - Columns: `pct_qcew_private_emp_*` (employment share by sector), `pct_real_gdp_*` (GDP share by sector)
    - Notes: QCEW employment shares show labor market composition; BEA GDP shares show economic output composition.
- Average Wages by Sector
    - Source: BLS QCEW
    - Gold: `gold.economics_industry_wide`
    - Columns: `qcew_private_avg_wkly_wage_*` (per sector)
    - Notes: The Autor polarization diagnostic — are growing sectors high-wage or low-wage?
- Business Formation Rates
    - Source: Census Bureau BFS
    - Gold: `gold.economics_industry_wide`
    - Columns: `bfs_business_applications`, `bfs_business_applications_yoy_pct`, `bfs_business_application_rate_per_1000_establishments`, `bfs_business_applications_per_1000_residents`
    - Notes: Track 12 complete. Annual county + derived CBSA. CBP-backed rate populated 2012–2023.
- Establishment Density by Sector
    - Source: Census County Business Patterns (CBP)
    - Gold: `gold.economics_industry_wide`
    - Columns: `cbp_total_establishments`, `cbp_estabs_per_1000_residents`, broad-family establishment counts and shares
    - Notes: Track 12 complete. 2010–2023 county + derived CBSA. Latest-year ZIP detail in separate `silver.cbp_zip`.
- Location Quotient by Sector
    - Source: BLS QCEW (derived from industry_wide)
    - Gold: `gold.economics_industry_wide`
    - Columns: `lq_ag_mining`, `lq_arts_accomm_food`, `lq_construction`, `lq_educ_health`, `lq_finance_real`, `lq_information`, `lq_manufacturing`, `lq_other_services`, `lq_professional`, `lq_retail`, `lq_transport_util`, `lq_wholesale`
- Education Attainment Trend
    - Source: ACS
    - Gold: `gold.population_demographics`
    - Columns: `pct_ba_plus`, `pct_ba_plus_change_5yr`
    - Notes: The human capital accumulation signal. Level lives in Character/Demographics; 5yr change belongs here as a leading indicator of industry mix trajectory.
