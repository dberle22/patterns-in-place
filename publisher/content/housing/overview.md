# Overview

We're working on a series of articles about housing in the United States. We'll explore some key indicators, breaking them down by different dimensions, and presenting an overarching analysis of how they work together. Housing is a complex topic so writing individual series of different components of the housing market will only confuse our thinking instead of bringing clarity. Also, the most interesting analysis is in the in-between area where concepts overlap.

Our outputs from this section will include quick-hit visuals, listicle type articles, and longer form analyses that bring together the different concepts. Our goal isn't to be overly exhaustive, it's to uncover interesting insights and start to think more deeply about how housing works. We will go down to the county level grain, but we're not committing to any county visuals yet.

## Key Concepts to explore:

- Are certain markets “overheating”? And on the flip side and where are good deals still found?
- What is the relationship between new housing permits, vacancy, and home and rental prices?
- What kind of new housing is being built and how does that relate to growth?
- What are the costs of housing?

## Workflow

1. Define the housing section data model.
   - Confirm the input Gold marts in `foundations/`.
   - Define the reusable `core_metrics` mart at `division`, `state`, `cbsa`, and `county`.
   - Use `2024` as the reference year for section snapshots and rankings.
   - Add temporary `major_cbsa_100k_flag` and `major_cbsa_250k_flag` fields until a canonical Intelligence Layer flag exists.

2. Validate the core mart before writing visuals.
   - Check year and geography coverage.
   - Profile null rates for each KPI by geography level.
   - Confirm which KPIs are safe for county vs CBSA analysis.

3. Build the Overheating Matrix on top of the shared marts.
   - Use `gold.housing_market_wide` for price and rent momentum signals.
   - Keep the table as a feature-and-component-score mart rather than a single locked heuristic.
   - Include raw inputs plus derived ranks / standardized scores so downstream visuals can choose the final framing.

4. Write section-specific chart SQL and visuals.
   - Keep business logic in the mart layer where possible.
   - Use section queries mainly for chart shaping and framing.

5. Draft articles and synthesis once the marts are stable.


## Gold Inputs

This section will use shared Gold marts from `foundations/` rather than building topic-specific source joins inside each notebook.

### Primary Gold marts

- `gold.housing_core_wide`
  - Core housing levels, affordability, vacancy, permit activity, and structure mix.
- `gold.population_demographics`
  - Population scale and growth context.
- `gold.economics_income_wide`
  - Income levels, growth, poverty, and inequality context.
- `gold.housing_market_wide`
  - Housing-market momentum measures from FHFA and Zillow annualized into geo-year records.

### Reference year

- `2024` is the canonical snapshot year for section-level comparisons, rankings, and most visuals.
- Time-series visuals may use longer history where available.
- `housing_market_wide` extends beyond 2024, but the section should anchor cross-mart comparisons on the shared 2024 surface.

### Initial validation notes

- Live warehouse checks on July 5, 2026 confirm `2024` coverage for `division`, `state`, `cbsa`, and `county` in `gold.housing_core_wide`, `gold.population_demographics`, and `gold.economics_income_wide`.
- `gold.housing_market_wide` currently supports `cbsa` and `county` only, with coverage from `2016` to `2025`. It does not currently provide `division` or `state` rows.
- `income_pc_growth_1yr` and `income_pc_growth_5yr` are BEA-based fields. The live BEA `CAINC` surface currently runs through `2023`, so `2024` Gold income rows carry ACS level fields but not BEA growth fields. Use `2023` as the latest year for income-growth comparisons until BEA `2024` lands.
- `core_metrics` now adds `acs_income_pc_growth_1yr` and `acs_income_pc_growth_5yr` so the section can use a contemporaneous `2024` income-growth signal for snapshot comparisons without backfilling BEA.
- The Gold income build had a state-key mismatch that dropped BEA state rows; that join has now been fixed in `foundations/etl/gold/gold_economy_income.sql`, and `2023` state growth fields now populate as expected.
- Division-level income growth remains unavailable in the current warehouse because the BEA income source is only modeled at `state`, `cbsa`, and `county` today. Division income levels can still be read from ACS-backed fields, but division income-growth analysis should wait for an explicit rollup design.
- HUD benchmark rent fields such as `fmr_2br` are effectively unavailable on the `2024` section surface in the current snapshot because the live HUD FMR and rent50 tables currently run through `2023` only. Use `2023` as the latest year for HUD benchmark rent comparisons.
- `ZORI` coverage remains partial in `2024`, especially for counties, so rent-momentum visuals should treat `zori_annual_avg_yoy_pct` as an enhancement rather than a row-inclusion requirement.

## Core Analytical Meanings And KPIs

We want the mart to support a few recurring meanings rather than a long undifferentiated KPI list.

### Tightness
- `vacancy_rate`
- `pct_rent_burden_30plus`
- `pct_rent_burden_50plus`
- `permits_per_1000_housing_units`
- `permits_per_1000_population`

### Housing cost and affordability
- `median_gross_rent`
- `annualized_median_rent`
- `median_home_value`
- `rent_to_income`
- `value_to_income`
- `fmr_2br`
- `fmr_gap_2br_vs_median_rent`

### Supply character
- `permits_share_multifam_units`
- `permits_share_units_5_plus`
- `permits_avg_units_per_bldg`
- `pct_struct_multifam`

### Growth and pressure
- `pop_total`
- `pop_growth_1yr`
- `pop_growth_3yr`
- `pop_growth_5yr`
- `median_hh_income`
- `acs_income_pc_growth_1yr`
- `acs_income_pc_growth_5yr`
- `income_pc_growth_1yr`
- `income_pc_growth_5yr`
- `hpi_yoy_pct`
- `hpi_5yr_pct`
- `zhvi_annual_avg_yoy_pct`
- `zori_annual_avg_yoy_pct`

## Data Model

The foundation of this analysis will be two mart tables in `content/housing/sql/`.

### 1. Core Metrics
A wide, reusable housing mart built for the full section.

- Grain: one row per `geo_level + geo_id + year`
- Geo levels: `division`, `state`, `cbsa`, `county`
- Time coverage: full available history
- Reference year: `2024` for section snapshots
- Inputs:
  - `gold.housing_core_wide`
  - `gold.population_demographics`
  - `gold.economics_income_wide`
  - selected joins from shared geography / Intelligence Layer reference assets as needed
- Required flags:
  - `major_cbsa_100k_flag`
  - `major_cbsa_250k_flag`
- Income growth guidance:
  - use `acs_income_pc_growth_1yr` / `acs_income_pc_growth_5yr` for `2024` snapshot rankings and cross-sectional comparisons
  - keep `income_pc_growth_1yr` / `income_pc_growth_5yr` as BEA-based historical context fields whose latest live year is currently `2023`
- Purpose:
  - support most section visuals directly
  - provide consistent input fields for cross-section comparisons
  - centralize shared KPI definitions instead of re-deriving them in each notebook

### 2. Overheating Matrix
A CBSA- and county-level feature mart used for overheating analysis.

- Grain: one row per `geo_level + geo_id + year`
- Geo levels: `cbsa`, `county`
- Inputs:
  - `core_metrics`
  - `gold.housing_market_wide`
- Design:
  - keep raw inputs
  - add derived change metrics, percentile ranks, and standardized component scores
  - include a provisional composite score for review during analysis
  - do not lock the section into a single irreversible composite too early
- Purpose:
  - support overheating rankings
  - support quadrant and bivariate visual framing
  - preserve flexibility as we refine the heuristic

#### Historical Reference Logic

We have prior overheating / investment-index logic outside this folder. If those files are brought into the repo or duplicated into the workspace, we should review them for:
- reusable KPI choices
- ranking / normalization choices
- threshold logic
- naming consistency

We should not assume the old composite carries over unchanged; the current section should be built against the modern Gold marts first.

## Sections

We're organizing our writings into individual sections. This keeps us organized and on track for posting.

### Vacancy
This section explores what vacancy rates look across the country. It sets the stage for the idea that housing is hard to come by.
- National Vacancy Rates - Choropleth map of States with their current Vacancy Rates.
- Distributions:
    - Boxplot of the major CBSAs in our Intelligence Layer. 
    - Boxplot of CBSAs that's broken out by Census Region or Division.
- Extremes: Horizontal Bar Charts of the top/bottom 10 markets.
- Change over time: line chart of national average, CBSA weighted average, and division/region averages.

### Costs
Here we cover the costs of housing and how they've changed over time.
- Comovement: indexed line charts of home values and rents
- Correlation heatmap of value-growth vs rent-growth
- Scatter plot of vacancy and cost changes. Let's call out falling vacancy + rising prices = tight, rising vacancy + rising price = interesting contradiction that we should call out. We will focus on the vacancy change vs cost changes here.
- Choropleth of rent-to-income to show what markets or states have potentially affordable rent.

### Supply Character
What does the housing supply look like across the US? How much new building is going on and what does the housing stock look like?
- Where is new building happening: proportional symbol map, permits per 1,000 housing units by CBSA. I'm envisioning a map where spiky points stick out.
- What's being built: stacked bar charts of share of multi-family vs single family permits. Pair this with a bar chart of the current housing stock.
- Supply vs Growth: A scatter plot that compares permits to population growth, using a quadrant framing as well.

### Overheating Heuristic

We will rebuild the overheating model using the current Gold marts and keep the mart flexible enough to support multiple visual framings.

The key idea is that overheating is not just “prices are high.” It is a combination of:

- price and rent momentum
- income and population growth pressure
- affordability strain
- vacancy and supply context

The Overheating Matrix should therefore store both the raw KPI inputs and their normalized component scores. We can then test different composite framings without rebuilding the base table each time.

Likely inputs to evaluate first:
- `hpi_yoy_pct`
- `hpi_5yr_pct`
- `zori_annual_avg_yoy_pct`
- `income_pc_growth_1yr`
- `income_pc_growth_5yr`
- `pop_growth_1yr`
- `pop_growth_5yr`
- `vacancy_rate`
- `rent_to_income`
- `value_to_income`
- `permits_per_1000_housing_units`
- `permits_share_multifam_units`

Source roles for overheating should stay distinct:
- `FHFA` / `gold.housing_market_wide` provides the primary home-price momentum signals.
- `ACS` / `gold.housing_core_wide` provides the broad-coverage affordability and tightness context, especially `rent_to_income`, `value_to_income`, burden, and vacancy.
- `ZORI` / `gold.housing_market_wide` is an optional rent-momentum enhancer where coverage exists, not a required input for row inclusion.

### Synthesis

This section brings it all together. We incorporate different sections into a broader analysis and shine a spotlight on some key markets.
- Relationship between Vacancy Rate changes and Costs.
- Correlation heatmap of all core metrics.
- A ranking table of key variables per metro, with a composite divergence score (sum of absolute rank differences) to surface metros that are outliers across multiple dimensions.

## Code Scaffold

```
content/housing/
  overview.md
  sql/
    core_metrics.sql        ← materializes the Core Metrics mart table
    overheating_matrix.sql  ← materializes the Overheating Matrix mart table
  vacancy/
    analysis.qmd
  costs/
    analysis.qmd
  supply_character/
    analysis.qmd
  overheating/
    analysis.qmd
  synthesis/
    analysis.qmd
```

The SQL files materialize mart tables into DuckDB. Each `.qmd` connects to DuckDB and contains all visuals for that section. Visuals are extracted into standalone files only once they're stable and committed for publishing.

## Posting Plan

We will create a posting plan for our content so we can track what is being built, how it's being delivered and the overall status of our series.
