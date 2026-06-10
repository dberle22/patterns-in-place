# Source Spec: CHR (County Health Rankings)

## 1. Overview

- Source: County Health Rankings & Roadmaps (Robert Wood Johnson Foundation + University of Wisconsin Population Health Institute)
- Access pattern: public annual CSV bulk downloads — no API, no key required
- Primary dependency: public CHR data portal files plus local raw-data and DuckDB paths
- Scope in Foundations: CHR provides the primary health, safety, and select social/environment signals for the Livability Health sub-score. The source aggregates CDC, ACS, EPA, and other agency data into a consistent county-level annual release, making it a high-value convenience layer for metrics that would otherwise require multi-source ingestion. The current landed coverage uses annual analytic backfill for `2016-2025`; the provider Trends CSV is documented separately as a narrower optional helper surface rather than the main historical backbone.
- Documentation goal: this file is the provider-level spec for CHR as it will be represented in Foundations, including a full measure inventory with inclusion decisions.
  As of 2026-06-09, the landed Foundations implementation now uses annual analytic backfill for `2016-2025`, with a source-faithful current-year wide staging table plus a curated historical staging panel.

---

## 2. Coverage Matrix

| Topic group | Staging family contract | Silver outputs |
| --- | --- | --- |
| Health outcomes | [../layers/staging/staging__chr_health_rankings.md](../layers/staging/staging__chr_health_rankings.md) | `silver.chr_health_outcomes` |
| Health behaviors | [../layers/staging/staging__chr_health_rankings.md](../layers/staging/staging__chr_health_rankings.md) | `silver.chr_health_outcomes` (selected columns) |
| Clinical care | [../layers/staging/staging__chr_health_rankings.md](../layers/staging/staging__chr_health_rankings.md) | `silver.chr_health_outcomes` (selected columns) |
| Social & economic | [../layers/staging/staging__chr_health_rankings.md](../layers/staging/staging__chr_health_rankings.md) | `silver.chr_health_outcomes` (selected columns) |
| Physical environment | [../layers/staging/staging__chr_health_rankings.md](../layers/staging/staging__chr_health_rankings.md) | `silver.chr_health_outcomes` (selected columns; lagged vs. primary EPA/FEMA sources) |
| Safety | [../layers/staging/staging__chr_health_rankings.md](../layers/staging/staging__chr_health_rankings.md) | `silver.chr_health_outcomes` (selected columns) |
| Education | [../layers/staging/staging__chr_health_rankings.md](../layers/staging/staging__chr_health_rankings.md) | `silver.chr_health_outcomes` (selected columns) |

All topic groups share the same staging family and feed a single unified Silver table at the `geo_level + geo_id + year` grain.

---

## 3. Source Contract

- Provider: Robert Wood Johnson Foundation / University of Wisconsin Population Health Institute
- Data portal: `https://www.countyhealthrankings.org/health-data/methodology-and-sources/data-documentation`
- Retrieval interface: direct CSV downloads, no authentication required
- Annual release cadence: typically published March–April each year
- Common geography pattern: county-focused analytic file with one national summary row, one state summary row per state, and ~3,150 county/county-equivalent rows; no sub-county or CBSA native grain
- Common time pattern: single-year cross-section per analytic file; Foundations now stitches those annual files into a multi-year `2016-2025` panel, while the provider also offers a separate narrower Trends CSV (see Section 9)

**Key files:**

| File | Description |
| --- | --- |
| `analytic_data<year>_v3.csv` | Core annual analytic file; one row per county; ~2,388 columns in 2025 |
| `chr_trends_csv_<year>.csv` | Long-format trends file; 15 measures back to ~1997; rolling 3-year and single-year spans mixed |

**File structure (analytic file):**

Each measure produces 3–8 columns in the wide analytic file: `raw value`, `numerator`, `denominator`, `CI low`, `CI high`, plus racial/ethnic breakdowns for selected measures. Only `raw value` columns are promoted to Silver; all others are retained in staging as provenance.

| Column | Description |
| --- | --- |
| `State FIPS Code` | 2-digit state FIPS |
| `County FIPS Code` | 3-digit county FIPS (within state) |
| `5-digit FIPS Code` | Concatenated 5-digit county FIPS — used as `geo_id` |
| `State Abbreviation` | 2-letter state abbreviation |
| `Name` | County display name |
| `Release Year` | CHR release year |
| `<Measure> raw value` | Observed metric value (rate, ratio, or index) |
| `<Measure> numerator` | Raw count underlying the rate |
| `<Measure> denominator` | Population base for the rate |
| `<Measure> CI low / CI high` | 95% confidence interval bounds |
| `<Measure> flag` | Data quality flag (0=none, 1=unreliable, 2=suppressed) |

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- [../../etl/staging/get_chr.R](../../etl/staging/get_chr.R)

---

## 4. Full Measure Inventory and Inclusion Decisions

The 2025 analytic file contains ~50 distinct measures. The table below documents every measure considered, with a decision and rationale for each.

### Health Outcomes

| Measure | Silver decision | Rationale |
| --- | --- | --- |
| **Life Expectancy** | **Include** | Best single summary of population health; county-grain not available from other current Foundations sources |
| **Premature Death** (YPLL rate) | **Include** | Years of potential life lost per 100k before age 75; complements life expectancy with a mortality burden signal |
| **Premature Age-Adjusted Mortality** | **Include** | Age-adjusted death rate for adults 25–64; better cross-county comparability than crude rates |
| **Child Mortality** | **Include** | Deaths per 100k children ages 1–14; no equivalent in current ACS or BLS coverage |
| **Infant Mortality** | **Include** | Deaths per 1,000 live births; CDC WONDER source; no equivalent in current Foundations coverage |
| Poor Physical Health Days | Staging only | Composite self-report; less interpretable than mortality measures at national scale |
| **Poor Mental Health Days** | **Include** | Useful prevalence signal for recurring mental-health strain that complements the provider access ratio rather than replacing it |
| Poor or Fair Health | Staging only | Overlaps conceptually with premature death and life expectancy already in Silver |
| Frequent Physical Distress | Staging only | Redundant with poor physical health days; both in staging for potential future use |
| Frequent Mental Distress | Staging only | Staging only; mental health provider ratio covers the access angle more cleanly |
| Low Birth Weight | Staging only | Infant mortality already captures the birth outcome signal; LBW adds detail without adding a distinct dimension |

### Health Behaviors

| Measure | Silver decision | Rationale |
| --- | --- | --- |
| **Drug Overdose Deaths** | **Include** | Strong signal for county distress and public health crisis; CDC WONDER source; suppression flag retained alongside raw value |
| Adult Smoking | Staging only | Health behavior signal; interesting but not a primary differentiator for market or livability scoring at national scale |
| **Adult Obesity** | **Include** | Widely used chronic-disease risk and livability signal; distinct enough to keep even with overlapping built-environment context elsewhere |
| **Physical Inactivity** | **Include** | Important behavioral health signal that complements obesity and park access rather than duplicating them |
| Excessive Drinking | Staging only | Staging only |
| Insufficient Sleep | Staging only | Self-report behavioral measure; staging only |
| Alcohol-Impaired Driving Deaths | Staging only | Overlaps with safety signals; covered by motor vehicle crash deaths already in Silver |
| Flu Vaccinations | Staging only | Public health behavior; available in CHR Trends but narrow use case for market analysis |
| Teen Births | Staging only | Socioeconomic proxy; child poverty and food insecurity cover the need more directly |
| Sexually Transmitted Infections | Staging only | Narrow public health signal; staging only |

### Clinical Care

| Measure | Silver decision | Rationale |
| --- | --- | --- |
| **Uninsured Adults** | **Include** | Primary healthcare access gap signal; CHR sources from ACS SAHIE which extends county coverage beyond standard ACS tables |
| **Primary Care Physicians ratio** | **Include** | Population per primary care physician; no equivalent in current Foundations sources; direct access structure signal |
| **Mental Health Providers ratio** | **Include** | Population per mental health provider; unique to CHR in current Foundations coverage |
| **Preventable Hospital Stays** | **Include** | Rate of hospital admissions preventable with good primary care; integrates access + utilization into a single signal |
| Dentists ratio | Staging only | Access signal but lower priority than physician and mental health ratios for market/livability scoring |
| Mammography Screening | Staging only | Public health quality metric; staging only |
| Other Primary Care Providers ratio | Staging only | Complements physician ratio but redundant once physician ratio is in Silver |
| Uninsured Children | Staging only | Adults rate is primary signal; children rate retained in staging as breakout |

### Social & Economic Factors

| Measure | Silver decision | Rationale |
| --- | --- | --- |
| **Food Insecurity** | **Include** | Sourced from Feeding America's Map the Meal Gap model — not from ACS; genuinely unique signal not available in current Foundations coverage |
| **Social Associations** | **Include** | Membership organizations per 10,000 residents from County Business Patterns; unique community fabric signal with no ACS equivalent |
| **Child Care Cost Burden** | **Include** | Sourced from state licensing data + ACS; child care affordability as a distinct economic stress signal not in current Gold tables |
| **High School Graduation Rate** | **Include** | 4-year cohort graduation rate from EDFacts/NCES — different from ACS educational attainment (which measures adult completion share); unique measure worth keeping |
| Income Inequality | Staging only | Gini coefficient sourced from ACS B19083 — same underlying data as what we can derive from ACS; skip to avoid duplication |
| Children in Poverty | Staging only | Sourced from ACS SAIPE; we have child poverty from ACS already |
| Unemployment | Staging only | We have BLS LAUS as the primary source; redundant here |
| Some College | Staging only | ACS educational attainment already covers this |
| Gender Pay Gap | Staging only | Sourced from ACS; we can derive from ACS income tables if needed |
| Median Household Income | Staging only | ACS primary source; redundant |
| Living Wage | Staging only | MIT Living Wage model; interesting but niche for current use cases |
| Child Mortality (social factor variant) | Staging only | Already captured under Health Outcomes |
| Injury Deaths | Staging only | Overlaps with safety signals already in Silver |
| Residential Segregation — Black/White | Staging only | Interesting but out of scope for current Livability sub-score |
| Child Care Centers | Staging only | Related to child care cost burden; staging-only for now |
| Census Participation | Staging only | Civic engagement proxy; staging only |
| Voter Turnout | Staging only | Civic engagement proxy; staging only |

### Physical Environment

| Measure | Silver decision | Rationale |
| --- | --- | --- |
| **Air Pollution: Particulate Matter (PM2.5)** | **Include (with lag note)** | County annual PM2.5 from EPA; not yet in Foundations from any primary source. CHR's version lags primary EPA data by 1–3 years. Include now as a holdover; plan to replace or validate against direct EPA ingest in Track 6 |
| **Adverse Climate Events** | **Include (with lag note)** | Days affected by drought, heat, or disasters; no equivalent in current Foundations coverage. FEMA NRI (Track 7) will eventually provide a more detailed risk picture; CHR version serves as a holdover |
| **Access to Parks** | **Include** | Share of residents with adequate access to parks; OSM/built-environment signal not currently in Foundations at county grain |
| Severe Housing Problems | Staging only | HUD CHAS already covers cost burden and overcrowding; overlapping content |
| Severe Housing Cost Burden | Staging only | Direct overlap with `gold.affordability_wide` cost burden metrics from HUD CHAS |
| Drinking Water Violations | Staging only | Useful but narrow; retain in staging pending any future EPA water quality track |
| Broadband Access | Staging only | FCC is the primary source; staging only for now |
| Library Access | Staging only | Staging only |
| Traffic Volume | Staging only | ACS commute patterns cover the car-dependency angle more directly |

### Safety

| Measure | Silver decision | Rationale |
| --- | --- | --- |
| **Homicide Rate** | **Include** | CDC WONDER death certificate source — more complete than FBI UCR at county grain because it does not depend on voluntary police reporting |
| **Firearm Fatality Rate** | **Include** | CDC WONDER source; unique signal covering both homicide and suicide by firearm; no equivalent in current Foundations |
| **Motor Vehicle Crash Deaths** | **Include** | CDC WONDER source; county-level traffic safety signal |
| Injury Deaths | Staging only | Aggregate of homicide + MV crash + other injury; component measures already in Silver |
| Suicides | Staging only | CDC WONDER source; heavily suppressed in small counties; staging only for now — consider adding if sub-score needs a mental health crisis dimension |

**Coverage note:** CHR safety covers fatal violence well via CDC WONDER death records. It does not cover property crime (theft, burglary). FBI UCR (Track 8) remains the primary path for a full crime picture; CHR is a useful complement, not a replacement.

### Education

| Measure | Silver decision | Rationale |
| --- | --- | --- |
| **Reading Scores** | **Include** | Stanford Education Data Archive via CHR; 3rd–8th grade proficiency index; no equivalent in current Foundations coverage |
| **Math Scores** | **Include** | Stanford Education Data Archive via CHR; 3rd–8th grade proficiency index; no equivalent in current Foundations coverage |
| High School Graduation | Included above under Social/Economic | EDFacts 4-year cohort rate; listed in Social/Economic section |
| School Funding Adequacy | Staging only | Interesting equity signal but niche for national market analysis; staging only |
| School Segregation | Staging only | Staging only |
| Children Eligible for Free or Reduced Price Lunch | Staging only | Poverty proxy; child poverty and food insecurity already cover this angle |

---

## 5. Final Silver Column Set

**25 columns** promoted from staging to `silver.chr_health_outcomes`: `23` raw-value measures plus `2` provider-ratio helper fields. All other measures remain in staging as raw provenance.

| Column | Category | Source measure |
| --- | --- | --- |
| `life_expectancy` | Health outcomes | Life Expectancy raw value |
| `premature_death_rate` | Health outcomes | Premature Death raw value (YPLL per 100k) |
| `premature_age_adjusted_mortality` | Health outcomes | Premature Age-Adjusted Mortality raw value |
| `child_mortality_rate` | Health outcomes | Child Mortality raw value |
| `infant_mortality_rate` | Health outcomes | Infant Mortality raw value |
| `drug_overdose_death_rate` | Health behaviors | Drug Overdose Deaths raw value |
| `poor_mental_health_days` | Health behaviors | Poor Mental Health Days raw value |
| `adult_obesity` | Health behaviors | Adult Obesity raw value |
| `physical_inactivity` | Health behaviors | Physical Inactivity raw value |
| `pct_uninsured_adults` | Clinical care | Uninsured Adults raw value |
| `primary_care_ratio` | Clinical care | Ratio of population to primary care physicians |
| `mental_health_provider_ratio` | Clinical care | Ratio of population to mental health providers |
| `preventable_hospital_stay_rate` | Clinical care | Preventable Hospital Stays raw value |
| `food_insecurity_rate` | Social/economic | Food Insecurity raw value |
| `social_associations_per_10k` | Social/economic | Social Associations raw value |
| `child_care_cost_burden_rate` | Social/economic | Child Care Cost Burden raw value |
| `hs_graduation_rate` | Social/economic | High School Graduation raw value |
| `air_pollution_pm25` | Physical environment | Air Pollution: Particulate Matter raw value *(lagged 1–3 yrs vs. EPA primary)* |
| `adverse_climate_events` | Physical environment | Adverse Climate Events raw value *(holdover pending Track 7 FEMA NRI)* |
| `pct_access_to_parks` | Physical environment | Access to Parks raw value |
| `homicide_rate` | Safety | Homicides raw value |
| `firearm_fatality_rate` | Safety | Firearm Fatalities raw value |
| `motor_vehicle_crash_rate` | Safety | Motor Vehicle Crash Deaths raw value |
| `reading_score_index` | Education | Reading Scores raw value |
| `math_score_index` | Education | Math Scores raw value |

---

## 6. Staging Shape

Single staging table — all measures land in one wide table preserving source column names:

**`staging.chr_health_rankings`**

| Column | Type | Description |
| --- | --- | --- |
| `fips5` | VARCHAR | 5-digit county FIPS (`5-digit FIPS Code` from source) |
| `state_fips` | VARCHAR | 2-digit state FIPS |
| `county_fips` | VARCHAR | 3-digit county FIPS within state |
| `state_abbr` | VARCHAR | 2-letter state abbreviation |
| `county_name` | VARCHAR | County display name |
| `release_year` | INTEGER | CHR release year |
| `<measure>_raw` | DOUBLE | Raw value for each measure (snake_cased) |
| `<measure>_num` | DOUBLE | Numerator for each measure |
| `<measure>_denom` | DOUBLE | Denominator for each measure |
| `<measure>_ci_low` | DOUBLE | Lower confidence bound |
| `<measure>_ci_high` | DOUBLE | Upper confidence bound |
| `<measure>_flag` | INTEGER | Data quality flag where available |

---

## 7. Staging To Silver

CHR handoff pattern:
1. Download annual analytic CSV and cache locally.
2. Parse all columns into `staging.chr_health_rankings` with snake_cased names.
3. Silver selects the `25` approved measures defined in Section 5.
   The only exceptions to the raw-value pattern are the provider access columns, which use CHR's published ratio helper fields (`population:provider`) instead of the corresponding per-100k raw values.
4. Standardize to `geo_level='county'`, `geo_id=fips5`, `geo_name`, `year=release_year`.
5. Derive CBSA rows via `silver.xwalk_cbsa_county` using population-weighted averages for rate/ratio columns; sum-based aggregation is not appropriate for rates.

**CBSA aggregation note:** CHR does not publish CBSA-native data. CBSA rows must be derived by population-weighting county values using ACS total population weights. Ratio columns (primary care ratio, etc.) require careful handling — they are already expressed as population ratios, so weighted averaging by county population is correct.

---

## 8. Gold Placement

CHR feeds a new `gold.health_wide` table at county + CBSA grain. This is the first source for the Livability Health sub-score. Future sources (EPA Track 6, FEMA Track 7) may extend or replace specific columns but the table structure is established here.

**Planned Gold table:** `gold.health_wide`
- Grain: one row per `geo_level + geo_id + year`
- Geo levels: `county`, `cbsa`
- Year coverage: `2016-2025` in the current landed build

---

## 9. Historical Extension Strategy

As of **June 9, 2026**, the official CHR data documentation pages expose two distinct historical download surfaces:

- The current data page includes the `2025 CHR CSV Analytic Data`, the `2025 CHR CSV Trends Data`, and a **supplemental analytic release dated March 2026**.
- The archive page `National data & documentation: 2010-2023` exposes annual analytic CSVs for each release year from `2010` through `2023`, while the live page separately exposes `2024` and `2025`.

This means we can backfill historical county observations directly from annual analytic files without relying on the more limited Trends extract.

### 9.1 Trends CSV research findings

The Trends CSV (`chr_trends_csv_<year>.csv`) is a separate long-format file with one row per `county × measure × yearspan`.

**2025 trends file layout (from the official Trends documentation):**

| Column | Meaning |
| --- | --- |
| `yearspan` | Year or rolling multi-year span represented by the estimate |
| `measurename` | Provider measure label |
| `statecode`, `countycode` | Source FIPS components |
| `county`, `state` | Geography labels |
| `numerator`, `denominator` | Underlying measure counts where available |
| `rawvalue` | Published measure value |
| `cilow`, `cihigh` | Confidence interval bounds |
| `measureid` | CHR measure identifier |
| `chrreleaseyear` | CHR release year |
| `differflag` | Flag that the estimate differs from the Annual Data Release |
| `trendbreak` | Flag that the observation begins a new trend and should not be compared to earlier years |

**Measures available in the 2025 Trends file (15 total):**

| Measure | Notes |
| --- | --- |
| Premature death | Rolling 3-year windows from `1997-1999` through `2020-2022` |
| Uninsured | Release years included `2012-2025` |
| Uninsured adults | Release years included `2010-2025` |
| Uninsured children | Release years included `2013-2025` |
| Primary care physicians | Release years included `2013-2024` |
| Flu vaccinations | Medicare-based recent-year series |
| Preventable hospital stays | Release years included `2019-2025` |
| Dentists | Release years included `2013-2024` |
| Mammography screening | Release years included `2019-2025` |
| Air pollution — particulate matter | Release years included `2013-2025` |
| Sexually transmitted infections | Included in trends file |
| Alcohol-impaired driving deaths | Included in trends file |
| Children in poverty | Release years included `2010-2025`; source break noted between `2002-2004` and `2005-2023` |
| Unemployment rate | Included in trends file |
| School funding adequacy | Recent-year series |

**Overlap with the current 25-column Silver contract:** only `5` current Silver measures appear in the documented Trends coverage:

- `premature_death_rate`
- `pct_uninsured_adults`
- `primary_care_ratio`
- `preventable_hospital_stay_rate`
- `air_pollution_pm25`

The Trends file does **not** cover most of the current CHR contract, including life expectancy, child and infant mortality, overdose deaths, obesity, physical inactivity, poor mental health days, food insecurity, social associations, graduation, parks, safety measures, or test scores.

### 9.2 Recommended historical ingest path

**Recommendation:** do **not** use the Trends CSV as the primary historical ingest for Foundations. Instead, backfill the annual analytic CSVs for a recent rolling window and keep only the fields we actually model.

Recommended first-pass scope:

- Backfill annual analytic CSVs for release years `2016-2025`
- Keep a **curated historical staging table** rather than a source-faithful full-wide archive
- Retain only:
  - geography keys and labels
  - `release_year`
  - the approved CHR Silver measure columns we want historically
- Prefer raw-value columns only for the historical panel unless a downstream calculation clearly requires numerator, denominator, or CI fields

This approach keeps the historical pipeline aligned with our existing `chr_silver.R` mapping logic and avoids storing ten years of 2,000+ unused provenance columns.

### 9.3 Recommended Silver / Gold behavior

- Rebuild `silver.chr_health_outcomes` as a **multi-year annual panel** at the existing `geo_level + geo_id + year` grain rather than creating a separate long trends table
- Keep `gold.health_wide` as the same schema and grain, simply extending time coverage beyond `2025`
- Preserve the provider Trends CSV as an optional future QA/helper ingest only if we later want CHR-native trend-break metadata for the small subset of covered measures

**Implementation status:** completed on `2026-06-09`.
`staging.chr_health_rankings_history` now materializes the curated county-only panel for `2016-2025`, and both `silver.chr_health_outcomes` and `gold.health_wide` now use that annual analytic backfill.

---

## 10. Operational Notes

- Staging entrypoint: [../../etl/staging/get_chr.R](../../etl/staging/get_chr.R)
- Required local environment wiring: `DATA` for cached CHR CSVs and `DB_PATH` for DuckDB materialization
- Official historical download surfaces verified on **June 9, 2026**:
  - current documentation page for `2024-2025`
  - archive page covering annual national data documentation for `2010-2023`
- The analytic CSV URL pattern changes with each release year (`analytic_data2025_v3.csv`, `analytic_data2024.csv`). The version suffix (`_v3`) is not consistent — verify the current URL against the documentation page before each annual refresh
- The `County Clustered` column (col 7) flags counties that CHR groups together for ranking due to small population; these counties have valid raw values but no county rank. Note this in Silver quality checks
- The live 2025 CSV includes one repeated embedded header row after the true file header. The staging ingest drops that artifact before validating FIPS keys and materializing staging.

---

## 11. Architecture Decisions

**Decision date:** 2026-06-04

### Single-year vs. multi-year
The initial Track 4 implementation used the `2025` analytic file as a single-year snapshot. After the historical review completed on **2026-06-09**, the implementation path changed and was carried through: annual analytic CSVs now provide the multi-year backbone for `2016-2025`, while the Trends CSV remains a secondary helper only. The annual analytic files preserve the broader CHR measure set we already model, while the Trends file covers only `5` of the current `25` Silver columns.

### Silver column scope
25 measures promoted to Silver: 23 raw-value measures plus the published provider-ratio helper fields for primary care and mental health access. All other measures remain in staging as wide provenance columns. Rationale: CHR's 2,388-column analytic file is almost entirely CI bounds, race breakdowns, and numerator/denominator detail that adds storage without analytical value in Gold. We only need the headline measure value per metric downstream, with the provider-ratio helpers kept because they are more interpretable for downstream product use than the paired per-100k raw values. The live 2025 analytic CSV does not ship a standalone overdose suppression flag, so Silver stays measure-only.

### CBSA derivation
County-to-CBSA rollup via population-weighted averages using `silver.xwalk_cbsa_county` and ACS population weights. CHR does not publish CBSA-native data. Rates and ratios are weighted by county population; index scores (reading, math) are weighted by county school-age population if available, otherwise total population.

### Physical environment as holdover
`air_pollution_pm25` and `adverse_climate_events` are included with explicit data dictionary notes that they lag primary EPA/FEMA sources by 1–3 years. These columns are intended to be replaced or validated against direct EPA ingest (Track 6) and FEMA NRI (Track 7). The data dictionary will flag these columns with a `source_lag_note`.

### Safety as CDC WONDER, not FBI
CHR safety metrics (homicide, firearm fatalities, MV crash) are sourced from CDC WONDER death certificate records. These are more complete at county grain than FBI UCR because they do not depend on voluntary police reporting. CHR does not cover property crime. FBI UCR (Track 8) remains the path for a full crime picture.

### Gold table name
New table `gold.health_wide` rather than the `gold_health_outcomes_wide` name in the plan. Rationale: the Silver contract covers more than health outcomes (safety, education, environment) so a shorter, broader name fits better.
