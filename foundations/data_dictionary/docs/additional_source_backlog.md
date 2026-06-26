# Data Sources — Research & Backlog Reference
## Patterns in Place / Metro Deep Dive Platform

**Purpose:** Reference document for evaluating and prioritizing new data source ingestion. Covers sources identified in a research session on June 9, 2026. Each entry includes what the source is, what it provides, how it fits the platform's Intelligence Framework (Character / Livability / Opportunity), ingestion complexity, cadence, known limitations, and links for further research.

**How to use this doc:** Each source is written to stand alone as a backlog ticket input. Copy the relevant section into your planning tool of choice when prioritizing. Sources are grouped by recommended priority tier, but final prioritization should be done against the full platform backlog.

---

## Priority Tiers at a Glance

| Source | Tier | Primary Frame(s) | Geo Depth | Cadence | Ingestion Complexity |
|---|---|---|---|---|---|
| BLS OEWS | 1 — Clear gap | Opportunity, Character | CBSA / MSA | Annual | Low |
| LEHD QWI | 1 — Clear gap | Opportunity | County, CBSA | Quarterly | Low–Medium |
| LEHD LODES | 1 — Clear gap | Character, Livability | Census Block | Annual | Medium–High |
| LEHD J2J | 2 — Strong add | Opportunity | State, CBSA | Quarterly | Medium |
| BLS CES Metro | 2 — Strong add | Opportunity | MSA (~450) | Monthly | Low |
| BEA CAINC5N | 2 — Strong add | Opportunity | County | Annual | Low |
| Economic Census 2022 | 2 — Strong add | Opportunity, Character | County, Metro, Place | Every 5 years | Medium |
| HUD CHAS (deeper) | 3 — When needed | Livability | Census Tract | ~3–4 years | Low |
| USDA ERS Typology | 3 — When needed | Character | County | ~5 years | Trivial |
| USDA ERS Food Access | 3 — When needed | Livability | Census Tract | Irregular | Low |
| FRED Metro Series | 3 — Reference | Opportunity | CBSA, County | Various | Low |
| LEHD PSEO | 3 — Niche | Character, Opportunity | Institution | Annual | Low |

---

## Tier 1 — Clear Gaps, Should Be in the Pipeline

---

### BLS OEWS — Occupational Employment and Wage Statistics

**What it is**

OEWS is the Bureau of Labor Statistics' annual survey of employment and wages by occupation, cross-tabulated by industry and geography. It covers approximately 830 occupations using the Standard Occupational Classification (SOC) system. The survey samples roughly 1.1 million establishments over a rolling 3-year window, enabling reliable estimates at fine geographic levels.

This is the single most significant omission from the current platform stack. The distinction from sources already in the pipeline is fundamental: QCEW and BEA tell you employment and wages by *industry sector* — how many people work in healthcare, how much the construction sector pays in aggregate. OEWS tells you employment and wages by *occupation* — how many registered nurses, software engineers, or truck drivers a metro has, and what each of them earns at the 10th, 25th, 50th, 75th, and 90th wage percentiles. These are orthogonal analytical cuts that answer different questions.

**What it provides**

- Employment counts and wage estimates for ~830 occupations at the national, state, and MSA level
- Wage distribution percentiles (10th / 25th / median / 75th / 90th) — not just averages
- Cross-tabulations by industry sector (so you can ask: what do software developers in healthcare earn vs. software developers in finance?)
- National industry-specific occupational estimates at NAICS 3–6 digit levels
- Coverage: ~530 MSAs and nonmetropolitan areas

**Fit in the Intelligence Framework**

*Opportunity frame:* Occupation mix is often a better leading indicator of a metro's economic trajectory than industry mix alone. A metro transitioning to a knowledge economy shows up first in occupation data — rising share of management/professional/STEM occupations — before GDP or income aggregates fully reflect it. The wage percentile distribution also reveals whether a metro's growth is broad-based or concentrated at the top.

*Character frame:* Occupation composition is one of the most empirically grounded anchors for demographic archetype labels. "Creative Class / Knowledge Hub" is measurable via share of STEM, arts/media/entertainment, and management occupations. "Production Town" shows up as a high share of production/transportation/material moving. You can benchmark any CBSA's occupational profile against national distributions and peer CBSAs to produce defensible archetype classification.

*Livability frame (secondary):* Wage percentile distribution is a proxy for economic inclusion — a metro with a compressed wage distribution has less inequality than one with a wide spread. Relevant for the affordability sub-dimension.

**Relationship to existing pipeline**

Extends or supplements:
- `gold.economics_industry_wide` — industry shares from BEA/QCEW are the demand-side view; OEWS adds the supply/workforce-side view
- `gold.economics_income_wide` — ACS income at household level; OEWS adds occupation-level wage benchmarks
- Planned composite scores: `economic_strength_index`, `industry_concentration_score`

Does not replace any existing source — it is genuinely additive.

**Cadence and recency**

Annual. Released each spring for the prior May reference period. Most recent available: May 2024 (released April 2025). Approximately 12–18 month lag.

**Ingestion complexity**

Low. Bulk download available as flat XLSX or CSV files by geography type (national, state, MSA). No API key required. MSA-level file is the primary target. State-based files organized by SOC code and geography. Structure is consistent year-over-year. A Silver script ingesting the MSA flat file and normalizing to `(geo_id, geo_level, year, soc_code, occupation_title, employment, wage_p10, wage_p25, wage_median, wage_p75, wage_p90)` grain should be a half-day build.

**Known limitations**

- Does not cover self-employed workers
- Wage data collected on an interval scale (ranges), not exact point data — medians are interpolated
- Small-MSA occupational cells can be suppressed for confidentiality
- 3-year rolling sample means the estimates reflect conditions over a window, not a single point in time — fine for structural analysis, imprecise for measuring a single-year shift
- SOC system revisions (most recent: 2018 SOC) can create comparability issues in long time series for specific occupation codes

**Suggested Gold table**

`gold.economics_occupation_wide` — grain: `(geo_level, geo_id, year)` with occupation-family employment, employment shares, state-benchmarked location quotients, weighted mean wages, and compact OEWS quality counts for the managed `STEM`, `management_professional`, `service`, `production_transportation`, and `other` families

**Links**

- Program home: https://www.bls.gov/oes/
- MSA data tables: https://www.bls.gov/oes/tables.htm
- May 2024 MSA estimates: https://www.bls.gov/oes/current/oessrcma.htm
- Technical documentation: https://www.bls.gov/oes/oes_emp.htm
- SOC classification system: https://www.bls.gov/soc/

---

### LEHD QWI — Quarterly Workforce Indicators

**What it is**

QWI is the public-use labor market data product from the Census Bureau's Longitudinal Employer-Household Dynamics (LEHD) program. It draws on the same underlying infrastructure as LODES — a longitudinally linked employer-employee database built from state unemployment insurance records matched to Census Bureau data. QWI exposes that infrastructure as a quarterly time series of employment, hires, separations, and earnings broken down simultaneously by worker characteristics and firm characteristics.

The critical differentiator from every other labor source in the pipeline: QWI is the only public source that lets you ask "how many 25–34 year olds with a bachelor's degree were hired in the healthcare sector in this metro, and what did they earn, this quarter?" No other public data source at CBSA grain does that.

**What it provides**

Worker characteristic breakdowns:
- Age (8 bands: under 25, 25–34, 35–44, 45–54, 55–64, 65+, and two further splits)
- Sex
- Education (less than high school, high school, some college, bachelor's or higher) — available from 2009 onward
- Race/ethnicity — available from 2009 onward

Firm characteristic breakdowns:
- Industry (NAICS sector through 4-digit)
- Firm age (startup vs. established)
- Firm size (employment size classes)

Core metrics per cell:
- Beginning-of-quarter employment
- Full-quarter employment (stable jobs)
- New hires (from unemployment + job-to-job)
- Separations
- Average monthly earnings
- Earnings for full-quarter employees

Geography: State, CBSA, county, and WIA (Workforce Investment Area). Available for most states 2000–present, quarterly.

**Fit in the Intelligence Framework**

*Opportunity frame (primary):* QWI is the most granular quarterly pulse on labor market conditions at sub-state geography available in the public domain. You can track whether a metro is adding young professional workers, whether wages for full-quarter employees are rising, and whether job stability (full-quarter vs. beginning-of-quarter employment ratio) is improving — all at a CBSA grain with a 6–12 month lag rather than ACS's 2-year lag.

*Character frame:* The age × education × industry breakdowns let you characterize the *composition* of a metro's workforce in ways ACS income/occupation data alone can't. A metro that's adding young, college-educated workers in professional services has a different trajectory signature than one adding older workers in production.

*Livability frame (secondary):* Earnings by age and education band is a more precise input to affordability analysis than ACS household income — you can ask whether low-wage workers (young, less-educated) can afford to live where the jobs are.

**Relationship to existing pipeline**

Extends:
- `gold.economics_labor_wide` — BLS LAUS gives you labor force and unemployment rate; QWI adds hires, separations, earnings, and worker demographic breakdowns at the same geography
- `gold.economics_industry_wide` — QCEW gives you industry employment and wages in aggregate; QWI adds the worker demographic × industry cross-tab

Does not replace LAUS (which is the standard unemployment rate source) or QCEW (which goes deeper on payroll at fine industry levels). QWI and QCEW are complementary.

**Cadence and recency**

Quarterly. Typically 6–12 months behind current quarter. State partnership determines lag — some states report faster than others. Full national coverage for most states from 2000–present.

**Ingestion complexity**

Low–Medium. QWI is available via a dedicated API (the LEHD public data API) with well-documented parameters for geography, industry, worker characteristics, and time range. R package `lehdr` wraps this API and is the recommended ingestion path given your R-first stack. The dimensional cross-tabs (all combinations of worker characteristics × firm characteristics) generate large result sets — scope the initial Silver script to the most analytically useful cuts (age × industry, education × industry) rather than pulling all combinations.

**Known limitations**

- Federal employment not included until 2010; creates a comparability break for government-heavy metros
- Some state/year/industry cells are suppressed for confidentiality (small cell counts)
- Education and race/ethnicity variables not available before 2009
- QWI counts jobs, not workers — a worker with two jobs appears twice; relevant for metros with high multi-job-holding rates
- "New hires" definition includes workers re-entering employment after a gap, not just genuinely new entrants to the labor market

**Suggested Gold table**

`gold.labor_qwi_wide` — two cuts: (1) grain `(geo_level, geo_id, year, quarter, industry_sector, age_group)` for the trend/time-series use case; (2) a collapsed annual summary for joining to ACS-based Gold tables.

**Links**

- LEHD program home: https://lehd.ces.census.gov/
- QWI overview: https://lehd.ces.census.gov/data/#qwi
- QWI Explorer (interactive): https://qwiexplorer.ces.census.gov/
- LEHD public API documentation: https://lehd.ces.census.gov/data/schema/
- R package `lehdr`: https://github.com/jamgreen/lehdr
- Code samples: https://lehd.ces.census.gov/data/lehd-code-samples.html

---

### LEHD LODES — Origin-Destination Employment Statistics

**What it is**

LODES is the spatial layer of the LEHD program — the data product that powers Census's OnTheMap application. Where QWI is a time series of workforce characteristics, LODES is a spatial snapshot answering a specific question: where do workers live, where do they work, and how do those geographies overlap or diverge within a metro?

LODES files are released at census block grain — the finest spatial resolution in the public labor data universe. Three file types: Origin-Destination (OD) links a worker's home block to their work block; Residence Area Characteristics (RAC) profiles the workforce living in each block; Workplace Area Characteristics (WAC) profiles the workforce employed in each block.

This is the data product that makes the jobs/housing spatial mismatch analysis possible — one of the most analytically distinctive outputs the platform could produce for Deep Dive work.

**What it provides**

Per census block (aggregatable to tract, NTA, ZCTA, county, CBSA):

*Workplace Area Characteristics (WAC):*
- Total jobs
- Jobs by earnings band (under $1,250/month, $1,251–$3,333, over $3,333)
- Jobs by NAICS sector (broad: 20 sector codes)
- Jobs by worker age band (29 or under, 30–54, 55+)
- Jobs by worker education (no high school diploma through graduate degree)
- Jobs by worker race/ethnicity
- Jobs by firm age (0–1 years, 2–3 years, 4–5 years, 6–10 years, 11+ years)
- Jobs by firm size (0–19 employees through 1,000+ employees)

*Residence Area Characteristics (RAC):* Same breakdown as WAC but for where workers live rather than where they work.

*Origin-Destination (OD):* Worker counts linking home census block to work census block — with earnings band, age, and NAICS sector breakdowns. This is the commute flow data.

Coverage: Most states, 2002–2022 (LODES 8.3). State-based files.

**Fit in the Intelligence Framework**

*Character frame (primary for zone analysis):* The WAC file at census tract/NTA/ZCTA grain lets you characterize the economic activity happening in a neighborhood — what kinds of jobs are there, who works there, what do they earn. This is the employment-side complement to the residential demographic profile ACS provides. A neighborhood that is residentially middle-class but has a WAC profile dominated by low-wage service jobs is economically distinct from one where workers and employers share similar income characteristics.

*Livability frame:* The spatial mismatch between where affordable housing is and where jobs are located is one of the most important structural features of a metro's livability. LODES OD files make this directly measurable — you can compute the average distance between where workers in a given income band live vs. where they work, for any metro.

*Opportunity frame:* Firm age and firm size distributions in the WAC file are signals of entrepreneurial activity and economic dynamism at sub-metro grain. A tract with a high share of young, small firms looks very different from one dominated by large established employers — both can be high-employment but they represent different Opportunity trajectories.

**Relationship to existing pipeline**

Extends:
- Zone analysis methodology for Metro Deep Dive — LODES WAC is the employment-side input to cluster modeling alongside ACS residential demographics
- `gold.economics_labor_wide` — sub-CBSA grain that fills the spatial gap between CBSA-level labor stats and neighborhood-level residential data

Does not replace ACS commute data in `gold.transport_built_form_wide` — ACS captures mode choice and commute time; LODES captures the origin-destination geography. Both are needed for a complete commute picture.

**Cadence and recency**

Annual. LODES 8.3 (November 2024) includes 2022 data. Typically released with a 2-year lag. State-based bulk download files (not API); `lehdr` R package also supports LODES ingestion.

**Ingestion complexity**

Medium–High. Files are state-based and large — the national OD file across all states is tens of millions of rows at census block grain. The Silver script needs to handle state-by-state ingestion, block-to-tract/county/CBSA aggregation (requires TIGER crosswalk), and schema normalization. The WAC and RAC files are more tractable than OD for initial ingestion. Recommended approach: ingest WAC and RAC first at tract grain for metro Deep Dive markets; defer the full national OD file until the spatial mismatch analysis is actively being built.

**Known limitations**

- Private-sector jobs only — federal employment excluded until 2010
- Self-employed not covered (consistent with QWI)
- Block-level precision is spurious for small counts — suppression and noise-infusion applied
- 2022 data released November 2024; roughly a 2-year lag
- State availability varies slightly; a few states have data gaps in specific years

**Suggested Gold table**

Two tables: `gold.lodes_wac_tract` (workplace area characteristics at census tract grain) and `gold.lodes_rac_tract` (residence area characteristics at census tract grain). OD flows at county or CBSA grain as a third table for the spatial mismatch analysis. Block-grain data stays in Silver as a processing artifact.

**Links**

- LODES data page: https://lehd.ces.census.gov/data/#lodes
- OnTheMap application (interactive exploration): https://onthemap.ces.census.gov/
- LODES technical documentation: https://lehd.ces.census.gov/data/lodes/LODES8/
- R package `lehdr` (QWI + LODES): https://github.com/jamgreen/lehdr
- November 2024 release announcement: https://census.gov/newsroom/press-releases/2024/onthemap-lodes-data.html

---

## Tier 2 — Strong Analytical Additions

---

### LEHD J2J — Job-to-Job Flows

**What it is**

J2J is a LEHD data product that tracks workers moving directly from one employer to another without an intervening unemployment spell. Where QWI counts the stock and flow of jobs, J2J measures the *mobility* of workers between jobs, industries, geographies, and firm types. It distinguishes between job-to-job transitions (worker moves directly) and employment-to-unemployment-to-employment transitions (worker separates, then finds a new job).

This is a niche but powerful source for understanding labor market dynamism — the degree to which workers are upgrading their positions, switching industries, or moving between geographies.

**What it provides**

- Job-to-job hire and separation counts by origin/destination industry sector
- Earnings changes associated with job transitions (did the worker earn more or less after the move?)
- Geographic origin-destination flows (workers moving between CBSAs or states)
- Breakdowns by worker age, sex, and earnings band
- Available at state and CBSA level; national and regional aggregates

**Fit in the Intelligence Framework**

*Opportunity frame:* J2J is the most direct measure of labor market fluidity and worker advancement available in public data. A metro with high job-to-job transition rates and positive earnings changes on transition is one where workers can climb the ladder — a genuine Opportunity signal. Industry-switching flows reveal whether a metro's labor market is diversifying or consolidating. Geographic J2J flows show whether a metro is a net importer or exporter of experienced workers.

**Cadence and recency**

Quarterly. Approximately 12–18 month lag. Available from 2000–present for most states.

**Ingestion complexity**

Medium. Available via the LEHD public API (same infrastructure as QWI). More complex schema than QWI due to origin-destination pairs. R package `lehdr` supports J2J ingestion. Recommended to defer until QWI and LODES are established — J2J is the deepest cut and rewards having the foundational labor tables already built.

**Known limitations**

- Covers only employer-to-employer transitions — misses self-employment transitions and transitions into/out of the labor force
- Geographic J2J flows are most reliable at state level; CBSA-level flows have higher suppression rates for smaller metros
- Earnings change calculations require careful handling of the interval-scale earnings data

**Suggested Gold table**

`gold.labor_j2j_wide` — grain: `(geo_level, geo_id, year, quarter, origin_industry, destination_industry)` for industry switching flows; supplemental table for geographic origin-destination flows at state/CBSA grain.

**Links**

- J2J data page: https://lehd.ces.census.gov/data/#j2j
- J2J Explorer (interactive): https://j2jexplorer.ces.census.gov/
- Technical documentation: https://lehd.ces.census.gov/data/j2j/

---

### BLS CES — Current Employment Statistics (State and Metro)

**What it is**

CES is the BLS program that produces the monthly "jobs report" — the headline nonfarm payroll employment number you see in the news. The State and Metro Area component extends that to approximately 450 metropolitan areas and all 50 states, producing monthly payroll employment, average weekly hours, and average hourly earnings by broad industry sector.

The distinction from BLS LAUS (already in the pipeline) is fundamental: LAUS measures the *labor force* using a household survey — it counts employed and unemployed residents regardless of where they work. CES measures *payroll jobs* from an establishment survey — it counts jobs located in an area, regardless of where the workers live. In a strong commuter metro (suburban ring workers commuting to a city core), these measures diverge materially. Both tell you something true; they answer different questions.

**What it provides**

- Monthly nonfarm payroll employment by NAICS supersector (about 11 broad industry groups)
- Average weekly hours worked
- Average hourly earnings
- Over-the-year employment change (seasonally adjusted and not seasonally adjusted)
- Coverage: ~450 MSAs and all states; monthly from early 1990s for most metros

**Fit in the Intelligence Framework**

*Opportunity frame (primary):* CES is the most timely economic momentum indicator available at MSA grain. A 12-month trailing employment change from CES tells you whether a metro is gaining or losing jobs right now — not 2 years ago. The industry sector breakdown lets you see which sectors are driving growth or contraction. For a Deep Dive report, CES provides the "current conditions" anchor that neither ACS nor QCEW can give you.

**Relationship to existing pipeline**

Supplements:
- `gold.economics_labor_wide` — BLS LAUS is already there; CES adds establishment-based payroll count, hours, and earnings on a monthly basis
- `gold.economics_industry_wide` — QCEW is the deep annual industry source; CES provides the monthly leading indicator

Does not replace QCEW or LAUS — they serve different analytical purposes and different time horizons.

**Cadence and recency**

Monthly. Preliminary estimates released approximately 3–4 weeks after the reference month. Revised twice: once the following month, again in the annual benchmark revision (March). Very low lag — near-real-time for labor market conditions.

**Ingestion complexity**

Low. BLS API with consistent series codes. Same infrastructure as LAUS — likely a minor extension to the existing BLS Silver script. The main schema consideration is handling monthly grain (vs. annual grain of most Gold tables) — either store monthly in Silver and aggregate to annual in Gold, or create a separate `gold.labor_ces_monthly` table for the time-series use case.

**Known limitations**

- Broad industry categories only (11 supersectors at metro level) — not the NAICS 4-digit depth of QCEW
- Establishment survey subject to benchmark revisions; preliminary monthly estimates can be revised significantly
- Does not cover self-employed, unpaid family workers, or agricultural workers
- Some smaller MSAs have limited industry detail due to confidentiality thresholds
- Seasonal adjustment at metro level is less reliable than at national level

**Suggested Gold table**

`gold.labor_ces_monthly` — grain: `(geo_level, geo_id, year, month, supersector_code)` with employment, average weekly hours, average hourly earnings, and computed over-year change. Annual summary table as a bridge to the ACS-grain Gold tables.

**Links**

- CES State and Metro overview: https://www.bls.gov/sae/
- Data tools and downloads: https://www.bls.gov/sae/data.htm
- Metro area definitions: https://www.bls.gov/sae/additional-resources/metropolitan-areas-for-the-ces-program.htm

---

### BEA CAINC5N — Compensation of Employees by NAICS Industry

**What it is**

CAINC5N is a table in the BEA's Local Area Personal Income (LAPI) series — specifically the one that breaks down compensation of employees by NAICS industry sector at the county and state level, annually. It is part of the same BEA Regional API infrastructure already in the pipeline (you're already pulling GDP and RPP from BEA).

The distinction from QCEW: QCEW gives you payroll (wages and salaries paid by employers, from UI records) at detailed industry levels. CAINC5N gives you compensation (wages + supplements like employer benefits and contributions) at a somewhat coarser industry level but with better conceptual alignment to national income accounting. CAINC5N is what BEA uses as the compensation input to GDP accounting — it's the "official" wage series for national income purposes.

**What it provides**

- Wages and salaries by NAICS sector at county and state grain
- Supplements to wages and salaries (benefits, employer contributions)
- Total compensation = wages + supplements
- Annual, back to 2001 for most series
- NAICS sector level (20 sectors) — less granular than QCEW but consistent with BEA's GDP accounting framework

**Fit in the Intelligence Framework**

*Opportunity frame:* Compensation growth by industry sector at county level, aligned with BEA's GDP series. Lets you link income growth directly to GDP growth in a way that is internally consistent within the BEA data family — the regression of CAINC5N compensation growth on CAGDP GDP growth is a defensible analytical building block.

**Relationship to existing pipeline**

Extends:
- `gold.economics_income_wide` — already has BEA personal income; CAINC5N adds the industry decomposition of the compensation component
- `gold.economics_industry_wide` — QCEW industry payroll is already there; CAINC5N adds BEA-framework compensation (including benefits) for consistency with GDP tables

This is probably a Silver script extension to the existing BEA ingest rather than a new track.

**Cadence and recency**

Annual. Released each November for the prior year. Approximately 11-month lag.

**Ingestion complexity**

Low. BEA Regional API already in the pipeline — CAINC5N is another table code in the same API call structure. The main work is adding the table to the existing BEA Silver script and normalizing the NAICS industry codes to match the rest of the platform's industry taxonomy.

**Known limitations**

- County-level data for some industries is suppressed (D) to avoid disclosure of individual employer data — same suppression issue as QCEW but sometimes worse at fine industry detail
- Supplements (benefits) estimates are model-based at the county level — less precise than the wages component
- NAICS sector level only at county grain; more industry detail available at state level

**Links**

- BEA Regional Data landing page: https://www.bea.gov/data/economic-accounts/regional
- CAINC5N table documentation: https://apps.bea.gov/regional/docs/RegionalIncome.cfm
- BEA Regional API: https://apps.bea.gov/api/

---

### Economic Census 2022

**What it is**

The Economic Census is the U.S. government's official five-year census of business activity — conducted for years ending in 2 and 7. It is a mandatory survey (response required by law), not a sample, making it the most accurate point-in-time picture of industry structure available. The 2022 edition covers data from the 2022 reference year with full releases completed through early 2026.

Unlike QCEW or BEA (which measure employment and payroll), the Economic Census adds revenue/sales, products sold, and firm structure data — the business-side metrics that employment counts alone don't capture.

**What it provides**

Core statistics produced for every industry × geography combination:
- Number of establishments
- Number of employees and payroll
- Sales, value of shipments, or revenue (the top-line metric QCEW lacks)
- Primary business activity (6-digit NAICS)

Additional data products:
- *Geographic Area Statistics:* National, state, county, metro area, and place-level tables at 2–6 digit NAICS. The deepest geographic × industry cross-tab in the public domain.
- *Establishment and Firm Size Statistics:* Revenue-size and employment-size distributions; single-unit vs. multi-unit firms; concentration ratios of the 4, 8, 20, and 50 largest firms.
- *Product Statistics:* What goods and services are actually being sold, using the North American Product Classification System (NAPCS) — not just what industry an establishment is classified in.
- *Comparative Statistics:* 2022 vs. 2017 side-by-side at the national level; bridge statistics for industries that changed NAICS codes between censuses.

Covers 19 NAICS in-scope sectors across 950+ detailed industries; geographic tables for nearly 21,000 geographic areas.

**Fit in the Intelligence Framework**

*Opportunity frame:* The 2017-vs-2022 comparative statistics are the cleanest available picture of how a metro's industry structure shifted over a 5-year window — including through the COVID disruption. Revenue growth by sector (not just employment) captures which industries are actually expanding economically vs. adding low-productivity jobs. Concentration ratios reveal whether local economies are dominated by a handful of large firms or have a healthy competitive structure.

*Character frame:* Product Statistics are uniquely useful for characterizing the economic identity of a place at a level of specificity that industry codes alone miss. A metro with high manufacturing employment could be making pharmaceuticals, aerospace components, or processed food — the NAPCS product data distinguishes these. That distinction matters for the "what kind of place is this?" question.

**Relationship to existing pipeline**

Supplements:
- `gold.economics_industry_wide` — QCEW and BEA give you annual industry employment and income; Economic Census adds the 5-year structural anchor including revenue, product mix, and firm concentration
- Retail Opportunity Finder lineage — ROF used retail-specific Economic Census data for Jacksonville; this generalizes that to a national framework

Not a replacement for QCEW — the annual cadence of QCEW is essential for trend work. Economic Census is the structural benchmark that QCEW trends are measured against.

**Cadence and recency**

Every 5 years (years ending in 2 and 7). The 2022 census data is fully released as of early 2026. The next edition covers reference year 2027, with data releases expected 2029–2030.

**Ingestion complexity**

Medium. Data available via the Census API (`data.census.gov`) and bulk XLSX downloads by sector. The main complexity is schema management across 19 sectors (each has somewhat different tables and column structures) and handling suppression flags consistently. Recommended approach: ingest the Geographic Area Statistics tables for the sectors most relevant to Deep Dive work first (retail trade, professional services, healthcare, manufacturing) rather than attempting a full-census ingest. 2017 data ingestion alongside 2022 enables the comparative analysis.

**Known limitations**

- 5-year cadence means data is always somewhat dated — 2022 data reflects pre-2022 conditions by the time you're using it
- Suppression for confidentiality is significant at fine geography × industry cells; small-county/small-industry combinations are frequently withheld
- Excludes farms, private households, and most government establishments — not a complete picture of all economic activity
- NAICS reclassifications between censuses (2017 vs. 2022 NAICS) require bridge statistics for accurate trend comparison

**Suggested Gold table**

`gold.economic_census_wide` — grain: `(geo_level, geo_id, year, naics_sector, naics_subsector)` with establishments, employment, payroll, revenue, and firm concentration metrics. Supplemental table for product statistics at state/national grain.

**Links**

- Economic Census program home: https://www.census.gov/programs-surveys/economic-census.html
- About the 2022 Economic Census: https://www.census.gov/programs-surveys/economic-census/year/2022/about.html
- 2022 data releases: https://www.census.gov/programs-surveys/economic-census/year/2022/news-updates/ecdata-releases.html
- Geographic Area Statistics: https://www.census.gov/programs-surveys/economic-census/geographies.html
- Census API for Economic Census: https://api.census.gov/data.html (search for EC2022 tables)

---

## Tier 3 — Ingest When the Use Case Is Felt

---

### HUD CHAS — Comprehensive Housing Affordability Strategy (Deeper Tables)

**What it is**

CHAS is a HUD data product built from a special tabulation of ACS microdata, designed specifically for housing policy analysis. You already have HUD Fair Market Rents in the pipeline. CHAS is a different and deeper HUD product that goes substantially further on housing cost burden by breaking it down across income bands, household types, renter vs. owner status, and cost burden severity.

**What it provides**

At census tract and county grain:
- Households by cost burden severity: not burdened (<30% of income on housing), moderately burdened (30–50%), severely burdened (>50%)
- Breakdowns by income band (extremely low / very low / low / moderate income as shares of Area Median Income)
- Renter vs. owner breakdowns at each income × burden cell
- Household type (elderly, small family, large family, etc.)
- Units affordable at each income level vs. households needing them — the supply/demand gap

**Fit in the Intelligence Framework**

*Livability frame (primary):* CHAS is the most policy-relevant affordability data source available and goes well beyond the rent-to-income ratios currently in `gold.affordability_wide`. The income-band × burden-severity cross-tab is essential for answering "who specifically is being squeezed?" — a metro where moderate-income households are burdened tells a different story than one where only extremely low-income households are. The supply/demand gap metric (units affordable at each income level) is one of the most cited statistics in housing policy research.

**Cadence and recency**

Irregular; approximately every 3–4 years. Based on ACS 5-year estimates. Most recent release uses 2016–2020 ACS data. HUD typically releases CHAS data 2–3 years after the ACS reference period.

**Ingestion complexity**

Low. Flat files available for download from HUD's website by geography type. Same HUD API relationship already in the pipeline.

**Known limitations**

- Infrequent updates limit use for trend analysis — best treated as a structural snapshot
- Tract-level cells have suppression issues for small populations
- AMI bands are defined locally (by HUD metro area), which requires careful handling when making cross-metro comparisons

**Links**

- CHAS data page: https://www.huduser.gov/portal/datasets/cp.html
- CHAS technical documentation: https://www.huduser.gov/portal/datasets/cp/CHAS-technical-notes.pdf

---

### USDA ERS — County Typology Codes and Rural-Urban Continuum Codes

**What it is**

The USDA Economic Research Service produces several county-level classification schemes that place counties on spectrums from urban to rural and characterize their economic base. The most useful for the platform are the Rural-Urban Continuum Codes (Beale Codes) and the County Typology Codes.

**What it provides**

*Rural-Urban Continuum Codes (2023):* Nine-category classification distinguishing metro counties by metro population size and nonmetro counties by degree of urbanization and adjacency to a metro area. Every US county receives a single code 1 (large metro core) through 9 (completely rural, not adjacent to metro).

*County Typology Codes:* Classify counties by economic base (farming-dependent, mining-dependent, manufacturing-dependent, federal/state government-dependent, recreation) and by persistent socioeconomic challenges (persistent poverty, persistent child poverty, low education, low employment, population loss, retirement destination).

*Urban Influence Codes:* 12-category scheme that places counties in hierarchical urban networks, emphasizing the role of neighboring metro size.

*Rural-Urban Commuting Area Codes (RUCA):* Census-tract-level classification using urbanization and commuting flow criteria — provides a finer-grained urban/rural gradient below the county level.

**Fit in the Intelligence Framework**

*Character frame (primary):* The typology codes are excellent dimension-table enrichments for CBSA characterization. A metro with several farming-dependent or mining-dependent hinterland counties has a distinct Character profile — and a different Opportunity trajectory — compared to a metro surrounded entirely by suburban counties. The recreation-destination classification is particularly useful for identifying metros where the tourism/amenity economy is a significant driver (relevant to Character archetype labeling). The persistent poverty flag is a strong Livability signal.

**Cadence and recency**

Slow-moving. Continuum Codes updated approximately every 5–10 years (most recent: 2023). Typology Codes updated irregularly. These are classification layers, not time-series data — they describe structural characteristics that change slowly.

**Ingestion complexity**

Trivial. Small flat files (one row per county, a handful of classification columns). Ingests as a dimension table — `dim_county_typology` — that enriches any county-grain Gold table via join on FIPS code.

**Links**

- Rural-Urban Continuum Codes: https://www.ers.usda.gov/data-products/rural-urban-continuum-codes/
- County Typology Codes: https://www.ers.usda.gov/data-products/county-typology-codes/
- RUCA codes: https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes/
- ERS Data Products index: https://www.ers.usda.gov/data-products/

---

### USDA ERS — Food Access Research Atlas

**What it is**

A USDA ERS data product mapping food access at census tract level using distance to the nearest supermarket, supercenter, or large grocery store, with vehicle availability breakdowns. It is the primary public data source for identifying "food desert" tracts — areas with low income and limited supermarket access.

**What it provides**

At census tract grain:
- Share of population living more than 0.5, 1, or 10 miles from a supermarket (urban/rural thresholds)
- Low-income + low-access tract flags (the "food desert" designation)
- Vehicle access breakdowns (low access without a vehicle is more severe)
- SNAP-authorized store counts

**Fit in the Intelligence Framework**

*Livability frame:* Food access is a Livability input — a tract that is both low-income and far from a grocery store is measurably worse to live in than a comparable tract with nearby food retail. For Deep Dive zone analysis, the food desert flag is a useful input to the "Distressed" zone type. Also directly relevant to the ROF retail lineage — a food desert tract is a candidate for a grocery or food retail opportunity.

**Cadence and recency**

Irregular and currently dated. Most recent estimates use 2019 data. There is no announced cadence for future updates. This is a structural enrichment layer, not a time-series source.

**Ingestion complexity**

Low. Downloadable flat file by census tract. Small schema — a handful of flag and distance variables per tract. Joins to any tract-grain Gold table via GEOID.

**Known limitations**

- 2019 data only — limited value for tracking change
- "Food desert" definition is contested; distance thresholds are somewhat arbitrary
- Does not account for food quality, pricing, or variety — only physical proximity

**Links**

- Food Access Research Atlas: https://www.ers.usda.gov/data-products/food-access-research-atlas/
- Atlas documentation: https://www.ers.usda.gov/data-products/food-access-research-atlas/documentation/
- Food Environment Atlas (county-level companion): https://www.ers.usda.gov/data-products/food-environment-atlas/

---

### FRED — Federal Reserve Economic Data (Metro Series)

**What it is**

FRED is the Federal Reserve Bank of St. Louis's data aggregation platform — one of the largest repositories of economic time series in the world, covering over 800,000 series from 100+ sources. Most of the metro-relevant series in FRED are sourced from BLS, Census, and BEA — sources already in the pipeline. However, FRED adds convenience (unified API), historical depth, and a few series not easily accessible elsewhere.

**What it might add that isn't already in the pipeline**

- *Delinquency and foreclosure rates* (CFPB/Federal Reserve data): Mortgage delinquency rates at metro level are an Opportunity/housing stress signal not covered by FHFA or Zillow. Available at varying geographies and cadences.
- *Small Business Lending (CRA data)*: Community Reinvestment Act data on small business loan originations by county — an Opportunity signal for entrepreneurial activity.
- *Fed District industrial production indices*: Regional manufacturing and industrial production indices published by individual Federal Reserve Banks (e.g., the Philadelphia Fed Coincident Index for states).

**Fit in the Intelligence Framework**

Supplementary to Opportunity frame primarily. Most useful as a convenience API for sourcing series from BLS/Census/BEA that are already in the pipeline but where FRED's API is cleaner than the primary source API. The unique FRED series (delinquency, lending) are niche additions.

**Recommendation**

Don't ingest FRED as a source in its own right — use it as a reference and secondary ingestion path for specific series when the primary source API is difficult. The delinquency/foreclosure series is worth a specific evaluation when Deep Dive mortgage/housing stress analysis is active.

**Links**

- FRED home: https://fred.stlouisfed.org/
- FRED API documentation: https://fred.stlouisfed.org/docs/api/fred/
- Metro area series search: https://fred.stlouisfed.org/categories/32071

---

### LEHD PSEO — Post-Secondary Employment Outcomes

**What it is**

PSEO is a newer LEHD product linking college transcript records to earnings and employment outcomes. It produces statistics on where graduates of specific institutions work, what industries they enter, and what they earn — 1 year, 5 years, and 10 years after graduation.

**What it provides**

- Earnings outcomes by institution, degree level, and field of study
- Industry employment by institution and field of study
- Geographic mobility of graduates (where they work relative to where they went to school)
- Coverage: select participating institutions only — not a national census

**Fit in the Intelligence Framework**

*Character frame (niche):* For metros anchored by a major research university, PSEO data answers a specific question: does the university actually retain graduates in the local economy, or is it a talent exporter? A "College Town" CBSA where graduates leave after graduation has a very different economic dynamic than one where graduates stay and form companies. This is genuinely publishable as a standalone post for university towns.

**Recommendation**

Niche addition — relevant for specific Deep Dive markets with major university presence (Raleigh-Durham, Ann Arbor, Pittsburgh, etc.) rather than a general pipeline addition. Low ingestion complexity when the use case arrives.

**Links**

- PSEO data page: https://lehd.ces.census.gov/data/#pseo
- PSEO Explorer: https://pseo.ces.census.gov/

---

## Appendix: Sequencing Recommendation

Based on the analysis above and the current platform roadmap, the recommended ingestion sequence is:

**Before Area Explorer Phase 1 (no blockers, high analytical value):**
1. **BLS OEWS** — highest analytical value, lowest complexity, fills the single biggest gap in the Opportunity/Character framework. Half-day Silver script.
2. **BLS CES Metro** — extends existing BLS infrastructure; adds monthly labor momentum. Minor script extension.

**Alongside or immediately after LEHD ingestion decision:**
3. **LEHD QWI** — use `lehdr` R package; scope to age × industry and education × industry cuts first. Quarterly pulse that no other source provides.
4. **USDA ERS Typology Codes** — trivial effort, useful dimension table for CBSA context labels.

**During Area Explorer build:**
5. **BEA CAINC5N** — minor extension to existing BEA Silver script.

**When Deep Dive zone analysis begins:**
6. **LEHD LODES (WAC + RAC first)** — tract-level employment characteristics for zone clustering. Defer OD files until spatial mismatch analysis is actively being built.
7. **LEHD J2J** — labor market dynamism layer; adds editorial differentiation to Opportunity frame.

**Structural benchmarks (ingest once, reference repeatedly):**
8. **Economic Census 2022** — ingest prioritized sectors (retail, professional services, healthcare, manufacturing) before the first Deep Dive market is analyzed.
9. **HUD CHAS deeper tables** — when affordability analysis needs income-band resolution below CBSA grain.
10. **USDA ERS Food Access Atlas** — when zone analysis includes food access as a Distressed zone input.

---

*Document generated: June 9, 2026. Sources verified against Census Bureau, BLS, BEA, USDA ERS, and LEHD program pages as of this date.*
