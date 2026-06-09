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
    - Gold: Population Demographics
    - Columns: 
        - Pct White, Pct Black, Pct AIAN, Pct Asian, Pct NHPI, Pct Hispanic, Diversity Index
- Ethnicity
    - Source: ACS (Not Ingested)
- Age
    - Source: ACS Age
    - Gold: Population Demographics
    - Columns:
        - Median Age, Pct Age Under 18, Pct Age 18-64, Pct Age Over 64
- Educational Attainment
    - Source: ACS Education
    - Gold: Population Demographics
    - Columns: Pct HS or Less, Pct Bachelor's, Pct Greater Than Bachelor's
- Foreign Born
    - Source: ACS
    - Columns: Pct Foreign Born
- Population Density
    - Notes: This is more relevant for in-market analyses

### Social Fabric & civic identity
How engaged the population is in a shared civic responsibility.

- Voting Rates - Midterm Elections (Less National Enthusiasm)
    - Source: 
- Social Capital Atlas - Opportunity Index (Ingest)
    - Source: Opportunity Index
        - Link: https://data.humdata.org/dataset/social-capital-atlas
- Nonprofits per 100k - NCCS
- Residential Stability (Migration)
    - Source: IRS
    - Gold: Migration Wide
    - Columns: Net Inflow, Total Inflow, Total Outflow
    - Source ACS:
    - Gold: Migration Wide
    - Columns: Pct Moved Same County, Pct Moved Same State, Pct Moved Different State, Pct Moved From Abroad
- Single-person household share:
    - Source: ACS
        - ACS B11001
- Single-parent family share
    - Source: ACS
        - ACS B11003
- Violent Crime Per 100k
    - Source: FBI
    - Notes: This primarily a Livability metric and there we are using CHR data since FBI data isn't cleanly presented at a County / CBSA level. We are deferring.
- Social Associations Per 10k
    - Source: CHR
- Emotional Support
    - Source: CDC BRFSS
        Link: https://data.cdc.gov/browse?category=Behavioral+Risk+Factors&sortBy=relevance&page=1&pageSize=20
    - Notes: Defer from broader analysis, potentially interesting down the road.

### Recreation & cultural amenities
We're deferring the Recreation section entirely until we get better Points ingestion coverage.

- Green Space per 100k
    - Source: Trust for Public Land Park Score
    - Notes: There are deep spatial datasets or rankings for the Top 100 Cities by Population
- Entertainment Venues per 100k
    - Source: OSM, Overture Maps
- Museums and Libraries Per 100k - IMLS
    - Source: OSM, Overture Maps
    - Source: IMLS
        - Notes: IMLS appears to only be at the State level
- Nightlife - Points
    - Source: OSM, Overture Maps
- Pct Access to Parks
    - Source: CHR
- Number of Universities
- University Rankings


## Livablity

The main Sub-Topics are the following:
- Affordability
- Health
- Safety
- Access & Infrastructure (transit, walkability, food, basic services)
- Education access
- Physical Environment

### Affordability
This sub-topic approaches if someone can afford to live in an area. Can they afford a home, are prices of essential goods reasonable, does their paycheck cover their needs.

- Housing Cost Burden
    - Source: ACS
    - Notes: This is a mix of Rent to Income and Home Price to Income, let's just use those two metrics
- Rent-to-Income
    - Source: ACS
    - Gold: Affordability Wide
    - Columns: Rent to Income
- Home Price to Income
    - Source: ACS
    - Gold: Affordability Wide
    - Columns: Value to Income
- Cost of Living
    - Source: BEA RPP
    - Gold: Affordability Wide
    - Columns: RPP Real PC Income
    - Notes: Use RPP to normalize Income to see what places have the highest earnings after normalization
- Inflation Rates
    - Notes: Not granular enough, drop
- Food Insecurity Rates
    - Source: CHR
    - Gold: Health Wide
- Child Care Cost Burden
    - Source: CHR
    - Gold: Health Wide
- Poverty Rates
    - Source: ACS
    - Gold: TBD, In Silver
    - Notes: Need to promote to Gold

### Health
How healthy a community is and the major outcomes

- Life Expectancy
    - Source: CHR
    - Gold: Health Wide
- Premature Death Rate
    - Source: CHR
    - Gold: Health Wide
- Child and Infant Mortality
    - Source: CHR
    - Gold: Health Wide
- Drug Overdoses
    - Source: CHR
    - Gold: Health Wide
- Insurance Rates
    - Source: CHR
    - Gold: Health Wide
- Preventable Hospital Stay Rate
    - Source: CHR
    - Gold: Health Wide
- Primary Care Physician Rate
    - Source: CHR
    - Gold: Health Wide
- Physical Inactivity
    - Source: CHR
    - Gold: Health Wide
    - Notes: Needs to be ingested and promoted, we should just update and rerun the ingestion script
- Obesity Rate
    - Source: CHR
    - Gold: Health Wide
    - Notes: Needs to be ingested and promoted, we should just update and rerun the ingestion script
- Poor Mental Health Days
    - Source: CHR
    - Gold: Health Wide
    - Notes: Needs to be ingested and promoted, we should just update and rerun the ingestion script

### Safety

- Homicide Rate
    - Source: CHR
    - Gold: Health Wide
- Firearms Fatality Rate
    - Source: CHR
    - Gold: Health Wide
- Motor Vehicle Crash Rate
    - Source: CHR
    - Gold: Health Wide

### Access & Infrastructure

- Mean travel time to work
    - Source: ACS
- Transit Commute Share
    - Source: ACS
    - Columns: Pct Commute Transit, Pct Commute Walking, Pct WFH
- Vehicle Share
    - Source: ACS
    - Columns: Pct HH 0 Vehicles
- Transit System Quality
    - Notes: Not a true metric, defer until we can find a source
- Walkability
    - Source: EPA SLD
    - Notes: Latest version uses 2019 data, needs ingesting
- Transit Access:
    - Source: EPA SLD
    - Notes: Latest version uses 2019 data, needs ingesting
- Jobs Accessability:
    - Source: EPA SLD
    - Notes: Latest version uses 2019 data, needs ingesting
- Population Density
    - Source: ACS
    - Columns: Pop Weighted Density Sq Miles
- Multi-Family Housing
    - Source: ACS
    - Columns: Pct Struct Multifam
- Broadband Access
    - Source: ACS
    - Notes: Need to start ingestion
- Food Access
    - Source: USDA Food Access Research Atlast
    - Notes: Needs to be ingested

### Education

- HS Graduation Rate
    - Source: CHR
    - Gold: Health Wide
- Math Scores
    - Source: CHR
    - Gold: Health Wide
- Reading Scores
    - Source: CHR
    - Gold: Health Wide
- K-12 Quality
    - Source: Standford SEDA
    - Notes: Future Ingestion, need more discovery on the best sources

### Physical Environment

- Air Pollution
    - Source: CHR
        - Gold: Health Wide
    - Source: EPA AQS, EPA EJScreen
        - Gold: Environment Wide
        - Clumns: AQI Median, AQI P90, Unhealthy Days, EJ PM2.5, EJ Ozone, EJ Diesel PM
        - Notes: AQI available 2016–2025; EJScreen currently 2024 only
- Environmental Hazard Exposure
    - Source: EPA EJScreen
    - Gold: Environment Wide
    - Columns: Traffic Proximity, Superfund Proximity, RMP Proximity, Wastewater Discharge, Drinking Water Noncompliance
- Adverse Weather Events
    - Source: CHR
    - Gold: Health Wide
    - Source: FEMA National Risk Index
        - Notes: Need to Ingest
- Weather
    - Notes: How do we model this and what's the value? Is it useful for labeling areas? Defer for now

## Opportunity

Trajectory-focused. About economic momentum, market signals, and whether conditions are improving for residents, investors, and businesses.

- Resident Opportunities
- Market / Investor Opportunity
- Business & Industry Opportunity

### Resident Opportunities

- Income Growth (1yr, 5yr)
    - Source: BEA CAINC
    - Gold: Economics Income Wide
    - Columns: income_pc_growth_1yr, income_pc_growth_5yr, income_pc_cagr_5yr
    - Notes: BEA-derived (calc_income_pc). Use RPP-adjusted version from Affordability Wide (rpp_real_pc_income) for cross-metro comparability.
- Wage Levels
    - Source: BLS QCEW
    - Gold: Economics Income Wide
    - Columns: qcew_total_covered_avg_wkly_wage, qcew_private_avg_wkly_wage
    - Notes: QCEW measures what employers pay in covered jobs. BEA pi_wages_salary and pi_wage_share (Economics Income Wide) are the income-flows complement — use both. QCEW wages are the right source for "what does a job here pay."
- Unemployment Rate & Labor Force Participation Rate
    - Source: BLS LAUS / ACS
    - Gold: Economics Labor Wide
    - Columns: pct_unemployment_rate, lfpr, lfpr_growth_5yr, unemployment_rate_change_1yr
- Poverty Rate Change
    - Source: ACS B17001
    - Gold: Economics Income Wide (level: pov_rate — query-ready)
    - Notes: Level is already in gold. Trend (year-over-year or 5yr change) needs to be derived — compute from the pov_rate time series in income_wide; no new ingestion needed, just a derived column.
- Intergenerational Mobility
    - Source: Opportunity Insights — Opportunity Atlas
    - Gold: Not ingested
    - Notes: Probability of reaching top income quintile if born in bottom quintile, by birth CBSA. Same ingestion pipeline as Social Capital Atlas. High-value metric — the single best measure of whether a place delivers on its opportunity promise for low-income residents.
- Gini Index (Income Inequality)
    - Source: ACS
    - Gold: Economics Income Wide
    - Columns: gini_index
    - Notes: Already in gold, not yet mapped anywhere. Primary home is Opportunity (is growth inclusive?); also relevant to Livability health outcomes per Wilkinson & Pickett.

### Market / Investor Opportunity

- Home Price Appreciation
    - Source: FHFA HPI
    - Gold: Housing Market Wide
    - Columns: To confirm - check gold__housing_market_wide.md for HPI appreciation columns
    - Notes: Repeat-sales index; controls for housing mix shifts. Use 1yr and 5yr appreciation rates.
- Rent Growth
    - Source: Zillow ZORI
    - Gold: Housing Market Wide
    - Columns: To confirm - check housing_market_wide for ZORI growth columns
    - Notes: Observed rent index, market-rate only. Does not capture subsidized or below-market units.
- Population Growth
    - Source: ACS
    - Gold: Population Demographics
    - Columns: pop_growth_1yr, pop_growth_5yr, pop_cagr_5yr
- Net Migration (AGI)
    - Source: IRS
    - Gold: Migration Wide
    - Columns: irs_net_migration_rate, irs_net_agi, irs_inflow_agi, irs_outflow_agi
    - Notes: irs_net_agi is the key investor signal — are high-income households net moving in or out? Cross-reference with Character/Residential Stability for the demographic composition story.
- Permit Activity
    - Source: BPS
    - Gold: Affordability Wide
    - Columns: permits_per_1000_housing_units, permits_per_1000_population, permits_share_multifam_units
    - Notes: A proxy for how much new building is happening. Total permits signals supply response to demand. Multifamily share signals rental market investment activity specifically.

### Business & Industry Opportunity

- GDP Growth
    - Source: BEA CAGDP
    - Gold: Economics GDP Wide
    - Columns: real_gdp_growth_5yr, real_gdp_cagr_5yr, real_gdp_pc, real_gdp_pc_growth_5yr, productivity_growth_5yr
    - Notes: Use real (inflation-adjusted) GDP, not nominal. productivity_growth_5yr (real GDP per employed person) is the cleanest long-run economic health signal.
- Industry Concentration
    - Source: BEA CAGDP9 (via industry_wide)
    - Gold: Economics Industry Wide
    - Columns: industry_concentration_hhi
    - Notes: Derived from BEA GDP shares. Lower HHI = more diversified = more resilient to sector shocks. Already computed in gold.
- Sector Share Changes
    - Source: BLS QCEW + BEA CAGDP9
    - Gold: Economics Industry Wide
    - Columns: pct_qcew_private_emp_* (employment share by sector), pct_real_gdp_* (GDP share by sector)
    - Notes: QCEW employment shares show labor market composition; BEA GDP shares show economic output composition. Both needed — a sector can be a large GDP contributor but small employer (finance, energy). Track direction of change over time, not just level.
- Average wages by sector
    - Source: BLS QCEW
    - Gold: Economics Industry Wide
    - Columns: qcew_private_avg_wkly_wage_* (per sector)
    - Notes: The Autor polarization diagnostic — are growing sectors high-wage or low-wage? A metro adding jobs in professional services vs. arts/accommodation tells a very different structural story.
- Business formation rates
    - Source: Census Bureau BFS (Business Formation Statistics)
    - Gold: Not ingested
    - Notes: Tracks new business applications weekly, published quarterly at state and some metro grain. More timely and forward-looking than CBP. Leading indicator of entrepreneurial activity. Worth ingesting.
- Location Quotient by Sector
    - Source: BLS QCEW (derived from industry_wide)
    - Gold: Not yet computed — derivable from pct_qcew_private_emp_* vs. national averages
    - Notes: LQ > 1.25 in a sector = genuine specialization, not just national average exposure. No new ingestion needed; a derived column or notebook calculation from existing gold data.
- Average establishment size
    - Source: Census County Business Patterns (CBP)
    - Gold: Not ingested — derivable from CBP employment ÷ establishments once ingested
    - Notes: Declining average size can mean either growing entrepreneurialism (more small firms) or anchor employer exit. Context-dependent; useful as a trend metric.
- Establishments per 1000 population by sector
    - Source: Census County Business Patterns (CBP)
    - Gold: Not ingested
    - Notes: CBP counts employer establishments by industry and geography. Complements QCEW employment — high employment + few establishments signals concentration in large employers; many small establishments signals distributed entrepreneurial base. Different economic structure stories.
- Education Attainment Trend
    - Source: ACS
    - Gold: Population Demographics
    - Columns: Derive from pct_ba_plus year-over-year change across the time series (2012–2024)
    - Notes: The human capital accumulation signal behind Glaeser's knowledge economy framework. Level lives in Character/Demographics; the change in BA+ share over 5 years belongs here as a leading indicator of industry mix trajectory.
