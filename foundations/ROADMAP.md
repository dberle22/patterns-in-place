# Foundations Roadmap

**Status:** Active
**Updated:** 2026-09-29

Foundations is complete enough for current work: 22 Gold tables, governed geography in `mart_geography`, and the Intelligence Framework promoted to `mart_intelligence`. From here, work is **pulled by a consumer** (the Metro Deep Dive program, the public panel, or a resumed product), not pushed ahead of need.

The task-level detail below is carried over word for word from the retired `PLATFORM_COMPLETION_PLAN.md` (archived at `foundations/archive/2026-09_platform_completion_plan/`), which also records the 20 completed tracks.

---

## Now

- [x] **County-first CBSA refresh.** Done; it fed public panel v2026.1. Archived at [archive/2026-09_county_first_cbsa_refresh/](archive/2026-09_county_first_cbsa_refresh/EPIC_COUNTY_FIRST_CBSA_REFRESH.md).
- [ ] **Promote from the MDD program when the rule is met.** An engine moves into `foundations/` once two consumers use it unchanged. Current candidates: the POI engine (`mart_poi`) and the geography relationships the program already relies on.

## Next: when a consumer pulls it

| Item | Pulled by |
|---|---|
| Public panel v2 source candidates (BFS, CBP, QCEW, HUD CHAS, permits, vacancy) and sparse BEA GDP-share fields | Public panel Epic 7 ([BUILD_PLAN.md](../public-cbsa-panel/BUILD_PLAN.md)) |
| `housing_market_wide` Connecticut coverage fix (Track 18.7) | Any analysis using Zillow or FHFA for CT metros |
| Semantic layer alignment pass: prune low-variance metrics from `theme_catalog.yml`, check `metric_catalog.yml` against calibrated KPI sets, run an end-to-end question test | Area Explorer public app or the chatbot resuming |
| Cloud-hosted warehouse (MotherDuck) with `mart_intelligence` queryable | Any cloud-deployed app |
| ACS broadband/disability/language close-out (Track 11.6–11.8) | Next time those Gold tables are touched |
| HMDA mortgage lending (Track 13), IPEDS (Track 10) | An analysis that needs lending or postsecondary data |

## Later: on demand only

- **Points layer (Tracks 15–17).** These tracks predate the MDD POI engine, which now produces classified POIs with tract and county assignment. Re-scope them before starting: promote what the engine has proven rather than building 16–17 as originally written.
- **Other Points gaps:** listing ingest (Zillow or StreetEasy) for Stoop Search, and parcel data outside NYC and the Southeast.
- **Stanford SEDA (Track 22), Economic Census 2022 (Track 27), MIT Election Lab (Track 21.1, deferred), EPA SLD tract normalization (Track 9.11).**
- **Documentation close-out (Track 18)** once the tracks above settle.

**Skipped:** FBI UCR / NIBRS crime data (Track 8). County files have large voluntary-reporting gaps, and CHR already covers homicide and other death-record measures. For crime in Deep Dive markets, use city open-data incident feeds.

---

## Backlog detail

### Partly done

#### Track 9 — New Source: EPA Smart Location Database (Transportation)

*Completed items omitted; see the archived plan.*

- [ ] **9.11** Tract SLD normalization follow-on: add a governed tract relationship bridge or switch to a source artifact that preserves tract identity reliably enough for the canonical tract backbone before attempting tract Silver / Gold promotion

#### Track 11 — ACS Expansions (Broadband, Disability, Language)

*Completed items omitted; see the archived plan.*

- [ ] **11.6** Update the appropriate Gold SQL and data dictionary
- [ ] **11.7** Add ACS broadband/disability/language to `source_topic_checklist.md` (Ingested)
- [ ] **11.8** Update `pipeline_manifest.yml` with any new steps

#### Track 21 — Social Fabric Sources (MIT Election Lab + IRS Business Master File)

*Completed items omitted; see the archived plan.*

- [ ] **21.1.1** Research & spec: confirm MIT Election Lab county-level returns download URL and column layout; verify county FIPS identifier, election year, total votes cast, and VAP denominator source (CVAP from Census); document in `foundations/data_dictionary/sources/source__mit_election_lab.md` — Deferred
- [ ] **21.1.2** Write `foundations/etl/staging/get_mit_election_lab.R` — download county returns for midterm election years (2010, 2014, 2018, 2022), parse to `staging.mit_election_lab`; retain county FIPS, year, total votes, office type filter (House or Governor as midterm proxy) — Deferred
- [ ] **21.1.3** Write staging contract: `layers/staging/staging__mit_election_lab.md`; note that VAP denominator comes from Census CVAP, not raw population — Deferred
- [ ] **21.1.4** Write `foundations/etl/silver/mit_election_lab_silver.R` — standardize county FIPS, compute `voter_turnout_rate` as total votes ÷ CVAP (join to ACS working-age population as proxy if CVAP not yet ingested), derive CBSA rollup rows (population-weighted); produce `silver.mit_election_lab` — Deferred
- [ ] **21.1.5** Write Silver YAML + Markdown: `layers/silver/silver__mit_election_lab.yml` + `.md` — Deferred

### Not started: Places sources

#### Track 10 — New Source: IPEDS (Postsecondary Education)

**Priority: Medium**

- [ ] **10.1** Research & spec: read `notes/.../Sources/IPEDS.md`, confirm current year file names (`HD<year>.zip`, `EFIA<year>.zip`, `C<year>_A.zip`), verify `FIPS`+`COUNTYCD` geocoding path, write `foundations/data_dictionary/sources/source__ipeds.md` source spec and update `SOURCES.md`
- [ ] **10.2** Write `foundations/etl/staging/get_ipeds.R` — download and unzip three IPEDS files, join on `UNITID`, produce `staging.ipeds_institutions` (characteristics, enrollment, completions joined)
- [ ] **10.3** Write staging contract: `layers/staging/staging__ipeds_institutions.md`
- [ ] **10.4** Write `foundations/etl/silver/ipeds_silver.R` — geocode to county via `FIPS`+`COUNTYCD`, aggregate to county/CBSA grain with `institution_count`, `total_enrollment`, `degrees_granted`, `rd_expenditures`; produce `silver.ipeds_county`
- [ ] **10.5** Write Silver YAML + Markdown: `layers/silver/silver__ipeds_county.yml` + `.md`
- [ ] **10.6** Decide whether IPEDS Gold lands in `gold_population_demographics` (college presence as character signal) or a new `gold_education_postsecondary_wide` table; document decision
- [ ] **10.7** Update or write the appropriate Gold SQL and data dictionary
- [ ] **10.8** Add IPEDS row to `source_topic_checklist.md` (Ingested)
- [ ] **10.9** Add IPEDS to `create_DB.R` / `pipeline_manifest.yml`

#### Track 13 — HMDA (Mortgage Lending)

**Priority: Medium — FHFA is now stable, unblocking this track**

HMDA (via CFPB) provides mortgage originations, denial rates, and lending equity metrics at census tract grain. This is the primary source for the lending-access dimension of the Housing topic. The tract-level grain makes it a natural complement to FHFA HPI and ACS housing metrics.

- [ ] **13.1** Research & spec: confirm CFPB HMDA flat-file download URL and column layout for the most recent year; identify the ~10 key fields (loan purpose, action taken, denial reason, applicant race, loan amount, tract FIPS); document in `foundations/data_dictionary/sources/source__hmda.md`; update `SOURCES.md`
- [ ] **13.2** Write `foundations/etl/staging/get_hmda.R` — download HMDA institution/loan-level flat file for target year(s), filter to home-purchase and refinance originations, produce `staging.hmda`; this file is large — document row count and filtering decisions in the staging contract
- [ ] **13.3** Write staging contract: `layers/staging/staging__hmda.md`; note that staging retains loan-level rows (one row per application) before Silver aggregation
- [ ] **13.4** Write `foundations/etl/silver/hmda_silver.R` — aggregate loan-level staging to tract/county/CBSA grain; compute `origination_rate`, `denial_rate`, `median_loan_amount`, `minority_applicant_denial_gap`; produce `silver.hmda`
- [ ] **13.5** Write Silver YAML + Markdown: `layers/silver/silver__hmda.yml` + `.md`
- [ ] **13.6** Decide whether HMDA Gold extends `gold.housing_core_wide` or `gold.housing_market_wide`, or lands in a new `gold.housing_lending_wide`; document decision (lending equity metrics may warrant their own table)
- [ ] **13.7** Update or write the appropriate Gold SQL and data dictionary
- [ ] **13.8** Add HMDA row to `source_topic_checklist.md` (Ingested)
- [ ] **13.9** Add HMDA to `pipeline_manifest.yml`

#### Track 22 — Stanford SEDA (K–12 Learning Rates)

**Priority: Low — future ingestion; crosswalk complexity warrants separate track**

The Stanford Education Data Archive (SEDA) provides district-level standardized test score averages and learning rate estimates (growth per grade level) derived from state assessment data. It is more analytically useful than CHR's test score indices because it measures learning rates rather than proficiency levels, and it covers a longer time series (approximately 2009–2018). The primary challenge is crosswalking school districts to counties and CBSAs, since districts do not nest cleanly into counties.

_Depends on: Track 15 (NCES CCD) completing first, since CCD provides the district-to-county relationship file needed for the crosswalk._

- [ ] **22.1** Research & spec: confirm Stanford SEDA download URL and most recent release year; review available measures (mean test scores, learning rates, trend estimates); confirm district NCES ID as the join key; document crosswalk approach (NCES district → county via NCES geographic relationship files) in `foundations/data_dictionary/sources/source__stanford_seda.md`; update `SOURCES.md`
- [ ] **22.2** Write `foundations/etl/staging/get_stanford_seda.R` — download SEDA district-level CSV, parse to `staging.stanford_seda`; retain NCES district ID, grade-level mean scores, learning rate estimates, year range
- [ ] **22.3** Write staging contract: `layers/staging/staging__stanford_seda.md`; document coverage years and note that learning rates are more reliable than single-year score averages
- [ ] **22.4** Write `foundations/etl/silver/stanford_seda_silver.R` — join NCES district ID to county via NCES geographic relationship file (enrollment-weighted where multiple counties share a district); aggregate to county and CBSA grain; produce `silver.stanford_seda` with `avg_learning_rate`, `avg_test_score_grade3`, `avg_test_score_grade8`, `score_trend_5yr`
- [ ] **22.5** Write Silver YAML + Markdown: `layers/silver/silver__stanford_seda.yml` + `.md`; document district-to-county crosswalk methodology and enrollment-weighting approach
- [ ] **22.6** Decide Gold placement: extend `gold.health_wide` (education group alongside CHR graduation and test scores) or new `gold.education_k12_wide`; document decision — coordinate with Track 15 (NCES CCD) Gold placement decision
- [ ] **22.7** Update or write the appropriate Gold SQL and data dictionary
- [ ] **22.8** Add Stanford SEDA to `source_topic_checklist.md` (Ingested)
- [ ] **22.9** Add Stanford SEDA to `pipeline_manifest.yml`

#### Track 27 — Economic Census 2022

**Priority: Medium — structural benchmark; 5-year cadence warrants its own track**

The Economic Census is the U.S. government's mandatory five-year census of business activity (years ending in 2 and 7). Unlike QCEW or BEA which measure annual employment and payroll, the Economic Census adds revenue/sales, firm concentration ratios, and product-mix data — the business-side metrics that employment counts alone cannot capture. The 2022 edition is fully released as of early 2026 and includes side-by-side 2017 vs. 2022 comparative statistics, making it the cleanest available picture of how metro industry structure shifted through the COVID period.

First-pass scope: Geographic Area Statistics tables for four priority sectors — Retail Trade, Professional Services, Healthcare, and Manufacturing. These cover the most analytically important industry families for Deep Dive work and keep the schema manageable. The full 19-sector ingest and product statistics are documented follow-ons.

The 5-year cadence means this behaves like a structural benchmark layer, not a recurring annual panel — similar to EPA SLD and USDA Food Atlas. Gold should be a dedicated table rather than enrichment of the annual industry mart.

- [ ] **27.1** Research & spec: confirm Census API table codes for 2022 Economic Census Geographic Area Statistics (priority sectors: Retail Trade `EC2200BASIC`, Professional Services, Healthcare, Manufacturing); verify county and MSA geography availability; document suppression behavior and NAICS reclassification between 2017–2022; write `foundations/data_dictionary/sources/source__economic_census.md`; update `SOURCES.md`
- [ ] **27.2** Write `foundations/etl/staging/get_economic_census.R` — download 2022 Geographic Area Statistics for the four priority sectors via Census API; also download 2017 data for the same sectors to enable comparative statistics; produce `staging.economic_census` at `(year, geo_level, geo_id, naics_sector, naics_subsector)` grain with establishments, employment, payroll, and revenue
- [ ] **27.3** Write staging contract: `layers/staging/staging__economic_census.md`; document sector scope decision, suppression handling, 2017/2022 NAICS bridge note, and deferred full-sector expansion path
- [ ] **27.4** Write `foundations/etl/silver/economic_census_silver.R` — normalize geo identifiers, standardize suppression flags, compute 5-year change metrics (establishment count change, revenue change, employment change 2017 → 2022), derive CBSA rows from county via `silver.xwalk_cbsa_county`; produce `silver.economic_census`
- [ ] **27.5** Write Silver YAML + Markdown: `layers/silver/silver__economic_census.yml` + `.md`; document 5-year structural benchmark nature, sector scope, and the revenue-vs-payroll distinction vs. QCEW
- [ ] **27.6** Write `foundations/etl/gold/gold_economic_census_wide.sql` — dedicated Gold table at `(geo_level, geo_id, year, naics_sector)` grain with establishments, employment, payroll, revenue, revenue per establishment, and 5-year change columns; designed as a structural context layer separate from the annual `gold.economics_industry_wide` panel
- [ ] **27.7** Write Gold data dictionary: `layers/gold/gold__economic_census_wide.yml` + `.md`; note that this is a point-in-time structural benchmark, not a recurring time series
- [ ] **27.8** Add Economic Census row to `source_topic_checklist.md` (Ingested — 2022 priority sectors only)
- [ ] **27.9** Add Economic Census to `create_DB.R` / `pipeline_manifest.yml`

### Not started: Points layer

#### Track 15 — NCES CCD (K–12 Schools, Points Layer)

**Priority: Medium — national-once ingest; prerequisite for per-market school aggregations**

NCES Common Core of Data provides lat/lon, enrollment, Title I status, grade span, and locale code for every U.S. public school. This is the primary K–12 source for the Points layer (`dim_point_of_interest`) and the upstream source for county/CBSA school-density aggregations that flow into the Places layer. Ingest once nationally; no per-market parameterization needed.

_Depends on: basic Points layer schema decisions (surrogate `point_id`, `point_source_mapping`) being made before this track runs. Those decisions are part of Track 16._

- [ ] **15.1** Research & spec: confirm NCES CCD annual ZIP download URL and column layout (`NCESSCH`, lat/lon, `MEMBER` enrollment, `TITLEI_STATUS`, `GSLO`/`GSHI`, `LOCALE`); write `foundations/data_dictionary/sources/source__nces_ccd.md`; update `SOURCES.md`
- [ ] **15.2** Write `foundations/etl/staging/get_nces_ccd.R` — download most recent CCD school-level file, parse to `staging.nces_ccd`; retain `NCESSCH` as source ID, lat/lon, key attributes
- [ ] **15.3** Write staging contract: `layers/staging/staging__nces_ccd.md`
- [ ] **15.4** Write `foundations/etl/silver/nces_ccd_silver.R` — assign surrogate `point_id`, write to `dim_point_of_interest` (category = `education / k12_school`) and `point_source_mapping` (source = `nces`, source_id = `NCESSCH`); pass through native lat/lon; enrich with county/CBSA from spatial join (or crosswalk via `xwalk_tract_county` if geometry not yet available)
- [ ] **15.5** Write Silver YAML + Markdown for the CCD contribution to `dim_point_of_interest` and `point_source_mapping`
- [ ] **15.6** Aggregate school-level Points to county/CBSA grain: `school_count`, `title1_share`, `avg_enrollment`, `locale_urban_share`; write aggregation SQL or dbt model that feeds `gold.population_demographics` or a new `gold.education_k12_wide`
- [ ] **15.7** Write Gold data dictionary for new K–12 aggregation columns
- [ ] **15.8** Add NCES CCD row to `source_topic_checklist.md` (Ingested)
- [ ] **15.9** Add NCES CCD to `pipeline_manifest.yml`

#### Track 16 — Points Layer Foundation (Schema + National-Once Sources)

**Priority: Ready to start — Stoop migration is complete**

**Context:** The Stoop pipeline already has a working POI architecture that this track promotes into Foundations. The core patterns — SHA256 surrogate `poi_id`, `source_system` namespacing, `category/subcategory` taxonomy, bounding-box OSM Overpass queries, per-source adapter modules — are all proven and in production. Track 16 is primarily a translation and promotion job, not greenfield design.

**What exists in Stoop today (do not rebuild):**
- `dim_public_poi` schema with `poi_id`, `source_system`, `source_id`, `category`, `subcategory`, `lat`, `lon`, `attributes` — directly maps to the Foundations `dim_point_of_interest` design
- `build_dim_public_poi()` with SHA256 stable ID generation — adopt as-is for the surrogate key approach
- `stoop/config/poi_categories.yaml` — the canonical taxonomy; promote to `foundations/config/poi_categories.yaml`
- OSM Overpass adapter (`osm.py`) — parameterize by bounding box, already handles multi-endpoint fallback, retries, GeoJSON parsing
- NYC Open Data adapter (`nyc_open_data.py`) — the schools, parks, libraries, farmers market sources here are the template for national equivalents
- `stoop/sql/gold/fct_nta_features.sql` — the aggregation pattern (point-in-polygon → NTA features) is the template for `fct_geo_aggregations`

**What's genuinely new:**
- Promote schema from Stoop DuckDB into `patterns_in_place.duckdb` under `gold` schema
- Add `point_source_mapping` table (Stoop uses a simpler single-ID approach; multi-source deduplication is new)
- Replace NYC-specific sources (NYC Open Data schools, BPL/QPL libraries) with national equivalents (NCES CCD, HIFLD, IMLS)
- Add `tract_id` and `county_fips` geography links alongside `nta_id` for national use

##### 16.1 Schema and taxonomy promotion

- [ ] **16.1.1** Promote `poi_categories.yaml` from `stoop/config/` to `foundations/config/poi_categories.yaml`; extend slugs to cover national-once source categories not yet in the Stoop taxonomy (`k12_school`, `hospital`, `public_library`, `farmers_market`, `college`)
- [ ] **16.1.2** Write `foundations/etl/gold/gold_dim_point_of_interest.sql` — create `gold.dim_point_of_interest` and `gold.point_source_mapping` in `patterns_in_place.duckdb`; schema inherits from Stoop `dim_public_poi` with additions: `tract_id`, `county_fips` geography links; `point_source_mapping` is new (one row per source ID per point)
- [ ] **16.1.3** Write Gold data dictionary: `layers/gold/gold__dim_point_of_interest.yml` + `.md`, `gold__point_source_mapping.yml` + `.md`
- [ ] **16.1.4** Document the stable ID strategy and deduplication rules in `foundations/data_dictionary/docs/data_platform_architecture.md` Points layer section — note what Stoop does today vs. what Foundations adds (multi-source mapping table)

##### 16.2 National-once sources (all have native lat/lon — no geocoding needed)

Each follows the same pattern: R staging script → staging contract → silver script → silver contract → Gold INSERT into `dim_point_of_interest` + `point_source_mapping`.

- [ ] **16.2.1** NCES CCD (K–12 schools) — write `foundations/etl/staging/get_nces_ccd.R`; download annual CCD school file; produce `staging.nces_ccd`; source_id = `NCESSCH`, category = `education/k12_school`; replaces NYC Open Data schools in Stoop for national use
- [ ] **16.2.2** HIFLD hospitals — write `foundations/etl/staging/get_hifld_hospitals.R`; download HIFLD hospital shapefile; produce `staging.hifld_hospitals`; source_id = CMS Certification Number, category = `health/hospital`
- [ ] **16.2.3** IMLS public libraries — write `foundations/etl/staging/get_imls.R`; download IMLS Public Library Survey CSV; produce `staging.imls_libraries`; source_id = FSCSKEY, category = `civic/library`; replaces BPL/QPL Open Data sources in Stoop for national use
- [ ] **16.2.4** USDA Farmers Markets — write `foundations/etl/staging/get_usda_farmers_markets.R`; download USDA NFMD CSV; produce `staging.usda_farmers_markets`; source_id = FMID, category = `food/farmers_market`
- [ ] **16.2.5** Write Silver scripts for all four national-once sources — standardize to `dim_point_of_interest` column contract, validate lat/lon ranges, join `tract_id` and `county_fips` via `silver.xwalk_tract_county` spatial join or FIPS prefix; produce Silver tables feeding the Gold INSERT
- [ ] **16.2.6** Write staging and Silver data dictionary contracts for all four sources
- [ ] **16.2.7** Update `source_topic_checklist.md`, `pipeline_manifest.yml`, and `create_DB.R` for all four national-once sources

##### 16.3 Geo-aggregations stub

- [ ] **16.3.1** Write `foundations/etl/gold/gold_fct_geo_aggregations.sql` — POI counts and density by category per census tract and county; pattern is directly adapted from `stoop/sql/gold/fct_nta_features.sql`; produces `gold.fct_geo_aggregations` as the aggregation surface that feeds Places Gold tables
- [ ] **16.3.2** Write Gold data dictionary: `layers/gold/gold__fct_geo_aggregations.yml` + `.md`

**Estimated effort:** 3–4 days total. Schema + taxonomy (16.1) is half a day. Each national-once source (16.2) is 2–3 hours given the existing R staging patterns. Geo-aggregations stub (16.3) is half a day adapting the Stoop SQL.

#### Track 17 — Points Layer: Per-Market Framework

**Priority: Run immediately before first Deep Dive market — not a prerequisite for Intelligence Layer work**

**Context:** The Stoop OSM Overpass adapter (`osm.py`) is the direct template. The key change is parameterizing the hardcoded `NYC_BBOX` and `OSM_EXPORTS` to accept a bounding box and category set at runtime. The Overture pipeline is genuinely new (GeoParquet on S3, different query pattern) but the Silver deduplication logic against existing `dim_point_of_interest` rows is the same for both.

Run this track as a single focused sprint when the first Deep Dive market is selected. Do not pre-build it speculatively.

##### 17.1 Architecture decisions (document before building)

- [ ] **17.1.1** Confirm bounding-box parameterization approach for OSM Overpass — the Stoop `osm.py` `NYC_BBOX` tuple becomes a `bbox` parameter; `OSM_EXPORTS` category set becomes a config-driven list from `poi_categories.yaml`; no other structural change needed
- [ ] **17.1.2** Confirm Overture approach — DuckDB spatial query against GeoParquet on S3 via httpfs extension (no local download); parameterize by bounding box; map Overture `categories.primary` → `poi_categories.yaml` slugs
- [ ] **17.1.3** Write per-market onboarding checklist in `foundations/data_dictionary/docs/data_platform_architecture.md` — neighborhood boundary source decision, GTFS feed ID, city open data portals; one checklist entry per market type (large city with published boundaries, market without published boundaries falls back to census tracts)

##### 17.2 OSM per-market framework

- [ ] **17.2.1** Refactor `stoop/src/nyc_property_finder/public_poi/sources/osm.py` into a parameterized module at `foundations/etl/staging/get_osm_pois.py` — replace `NYC_BBOX` with `bbox` parameter, replace `OSM_EXPORTS` hardcoded dict with category list driven by `poi_categories.yaml`; keep multi-endpoint fallback and retry logic unchanged
- [ ] **17.2.2** Write staging contract template: `layers/staging/staging__osm_pois_{market}.md`
- [ ] **17.2.3** Write silver script `foundations/etl/silver/osm_pois_silver.py` — normalize OSM source rows into `dim_point_of_interest` column contract; deduplicate against existing rows by proximity + name match; produce `staging.osm_pois_{market}` Silver contribution

##### 17.3 Overture per-market framework

- [ ] **17.3.1** Write `foundations/etl/staging/get_overture_places.py` — DuckDB httpfs query against Overture GeoParquet filtered by bounding box; map Overture `categories.primary` to `poi_categories.yaml` slugs; produce `staging.overture_places_{market}`
- [ ] **17.3.2** Write staging contract template: `layers/staging/staging__overture_places_{market}.md`
- [ ] **17.3.3** Write silver script `foundations/etl/silver/overture_places_silver.py` — normalize Overture rows; deduplicate against existing `dim_point_of_interest` rows (Overture is primary; OSM fills gaps); produce Silver contribution

##### 17.4 Transitland GTFS per-market framework

- [ ] **17.4.1** Write `foundations/etl/staging/get_transitland_stops.py` — parameterized by GTFS feed ID or bounding box via Transitland API; produce `staging.transit_stops_{market}`; pattern is a generalized version of `stoop/src/nyc_property_finder/public_poi/sources/mta_subway.py`
- [ ] **17.4.2** Write staging contract template: `layers/staging/staging__transit_stops_{market}.md`
- [ ] **17.4.3** Write silver script — normalize to `dim_point_of_interest`; source_id = `{agency_id}:{stop_id}`; category = `transportation/transit_stop`

##### 17.5 Neighborhood boundaries per-market

- [ ] **17.5.1** Write `foundations/etl/staging/get_neighborhood_boundaries.py` parameterized by market — city open data portal (published boundaries) or TIGER tract fallback; produce `staging.neighborhood_boundaries_{market}` in `dim_polygon` contract
- [ ] **17.5.2** Write staging contract template: `layers/staging/staging__neighborhood_boundaries_{market}.md`
- [ ] **17.5.3** Write silver contribution to `dim_polygon` — standardize geometry to WGS84, attach `geo_level`, `market_id`, `boundary_type` (`nta`, `census_tract`, `city_neighborhood`)

##### 17.6 fct_geo_aggregations production

- [ ] **17.6.1** Extend `gold_fct_geo_aggregations.sql` (from Track 16.3) with per-market POI density metrics — point-in-polygon counts by category per tract and NTA/neighborhood, park area per NTA; adapted directly from `stoop/sql/gold/fct_nta_features.sql` and `stoop/sql/datamart/neighborhood_character/`
- [ ] **17.6.2** Update Gold data dictionary for production aggregation columns

**Estimated effort:** 3–4 days for the first market run (framework + Jacksonville). Subsequent markets 4–8 hours each once the framework is in place — the per-market work reduces to: run bounding box query, source neighborhood boundaries, confirm GTFS feed ID.

### Close-out

#### Track 18 — Final Integration and Documentation Sync

These tasks close out the plan after all tracks above are complete.

- [ ] **18.1** Update `source_topic_checklist.md` — verify all status fields are accurate; move any remaining Planned rows with evidence of partial work to Partial
- [ ] **18.2** Update `foundations/data_dictionary/sources/checklist.md` — add new source entries for all tracks: FHFA, CHR, OZ, EPA AQI, EPA EJScreen, EPA SLD, FEMA NRI, IPEDS, ACS expansions, CBP, BFS, HMDA, Opportunity Insights (Social Capital Atlas + Opportunity Atlas), USDA Food Atlas, MIT Election Lab, IRS BMF, Stanford SEDA, NCES CCD, HIFLD, IMLS, USDA farmers markets, Overture, OSM, Transitland, LEHD QWI, LEHD LODES, LEHD J2J, BLS OEWS, BEA CAINC5N, USDA ERS County Typology, Economic Census 2022
- [ ] **18.3** Update `foundations/data_dictionary/README.md` — add new Gold themes (health, environment, transportation built form, postsecondary education, lending, social capital, policy designations, points layer) to the main themes table
- [ ] **18.4** Update `foundations/etl/pipeline_manifest.yml` — verify all new scripts are present with correct `depends_on` entries and `enabled: true`
- [ ] **18.5** Update `foundations/etl/create_DB.R` — confirm new staging/silver/gold scripts are sourced in correct sequence order
- [ ] **18.6** Update `ETL_MIGRATION_PLAN.md` — add a note marking the plan as closed
- [ ] **18.7** **`gold.housing_market_wide` coverage pass** — run a join audit between `gold.dim_geo` (all CBSAs) and `gold.housing_market_wide` to identify CBSAs with zero Zillow/FHFA rows. Known gap: all Connecticut CBSAs are missing because CT restructured its county-equivalent geography and Zillow/FHFA publish under the legacy CBSA codes. Apply the same 2020-vintage CBSA code remapping used in other sources (e.g., the Connecticut county crosswalk approach from Track 9 SLD and the QCEW staging fix) to resolve the CT rows. Puerto Rico CBSAs are a source coverage boundary (Zillow/FHFA do not publish PR data) and should be documented as excluded rather than fixed. After the fix, verify CT CBSA rows populate correctly in both `silver.zillow_zhvi`, `silver.zillow_zori`, and `silver.fhfa_hpi` before rebuilding Gold.
