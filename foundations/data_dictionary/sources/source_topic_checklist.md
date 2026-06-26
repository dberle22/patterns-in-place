# Source And Topic Checklist

Coverage unit: upstream source plus the main topic groups called out in `notes/patterns_in_place_notes/Data/Sources/`.

Status meanings:
- `Ingested` means the source has a real Foundations ingest path and current dictionary coverage.
- `Partial` means some pipeline pieces exist, but Silver / Gold coverage or broader production use is incomplete.
- `Planned` means the source is documented in notes but not yet part of the shared Foundations ingest surface.
- `Product-specific` means the source is active in another product or market-specific workflow rather than the shared Foundations layer.

## Shared Foundations Coverage

| Status | Source | Topic groups in notes | Current Foundations state | Source notes |
| --- | --- | --- | --- | --- |
| [x] Ingested | ACS | Demographics; Housing; Income & poverty; Labor; Migration & mobility; Transportation | Provider spec and staging / Silver coverage exist; Texas school metrics remain a special-case direct Silver output | [ACS.md](../../../notes/patterns_in_place_notes/Data/Sources/ACS.md) |
| [x] Ingested | BEA | GDP; Personal income; Industry output; Regional Price Parity; CAINC5N earnings and compensation | Provider spec and staging / Silver / Gold coverage now include the dedicated CAINC5N path; current BEA scope spans GDP, income, regional price parity, and the broad-family earnings plus all-industry compensation slice in `gold.economics_industry_wide` | [BEA.md](../../../notes/patterns_in_place_notes/Data/Sources/BEA.md) |
| [x] Ingested | BLS | Labor market via LAUS; Industry employment and wages via QCEW; Occupation structure and wages via OEWS | Provider spec, staging, Silver, and Gold coverage now exist; LAUS feeds `gold.economics_labor_wide`, curated QCEW feeds `gold.economics_industry_wide`, and OEWS feeds `gold.economics_occupation_wide` | [BLS.md](../../../notes/patterns_in_place_notes/Data/Sources/BLS.md) |
| [x] Ingested | BPS | Housing supply; multifamily share | Provider spec and staging / Silver coverage exist | [BPS.md](../../../notes/patterns_in_place_notes/Data/Sources/BPS.md) |
| [x] Ingested | HUD | Fair Market Rents; Rent burden / CHAS | Provider spec, staging, Silver, and Gold coverage now exist; CHAS is modeled as a documented CBSA/county/place burden table feeding `gold.affordability_wide` for 2021 rows | [HUD.md](../../../notes/patterns_in_place_notes/Data/Sources/HUD.md) |
| [x] Ingested | IRS Migration | Migration flows; Income migration | Provider spec, staging, Silver, and Gold coverage now exist; IRS summary enriches county/CBSA/state rows in `gold.migration_wide` | [IRS Migration.md](../../../notes/patterns_in_place_notes/Data/Sources/IRS%20Migration.md) |
| [x] Ingested | LEHD J2J | Labor fluidity; worker job-to-job transitions; earnings change on transition | Child topic spec, staging, Silver, and Gold coverage now exist; current shared contract annualizes the public state + metro `J2J` counts, models the age-family state/CBSA Silver surface, and publishes the complete-year all-age all-industry mart `gold.labor_j2j_wide` while keeping `J2JR` and `J2JOD` deferred | [source__lehd_j2j.md](./source__lehd_j2j.md) |
| [x] Ingested | Zillow | Home values via ZHVI; Market rents via ZORI | Provider spec, staging, Silver, and Gold coverage now exist; current modeled contract covers county/ZCTA/CBSA, with city/state still under follow-up review for future extension | [Zillow.md](../../../notes/patterns_in_place_notes/Data/Sources/Zillow.md) |
| [x] Ingested | TIGER / Census geographies | Geometry; geography crosswalks; `dim_geo` support | Core infrastructure source already active through `xwalk_*` tables and shared geo logic | [TIGER.md](../../../notes/patterns_in_place_notes/Data/Sources/TIGER.md) |

## Product-Specific Or Market-Specific Active Sources

| Status | Source | Topic groups in notes | Current state | Source notes |
| --- | --- | --- | --- | --- |
| [~] Product-specific | Google Maps / Places API | Food & drink; Culture & entertainment; Retail; Services | Active in NYC and other point-POI workflows, not yet a shared Foundations source spec | [Google Maps.md](../../../notes/patterns_in_place_notes/Data/Sources/Google%20Maps.md) |
| [~] Product-specific | OSM | Transit; Parks & open space; Civic; Walkability context | Active in NYC public-POI workflows, not yet a shared Foundations source spec | [OSM.md](../../../notes/patterns_in_place_notes/Data/Sources/OSM.md) |
| [~] Product-specific | Local Tax Records | Ownership; Valuation; Land use; Transaction history | Active in NYC and ROF parcel workflows, not yet standardized as a shared Foundations source | [Local Tax Records.md](../../../notes/patterns_in_place_notes/Data/Sources/Local%20Tax%20Records.md) |

## Planned Sources

| Status | Source | Topic groups in notes | Priority / notes status | Source notes |
| --- | --- | --- | --- | --- |
| [x] Ingested | CHR | Health outcomes; Health behaviors; Clinical care; Social & economic factors; Physical environment | Provider spec, staging, Silver, and Gold coverage now exist; current modeled contract is a 2025 county + derived CBSA health mart built from the analytic CSV | [CHR.md](../../../notes/patterns_in_place_notes/Data/Sources/CHR.md) |
| [x] Ingested | CBP | Business structure; Establishments; Employment; Payroll | Provider spec, staging, Silver, ZIP Silver, and Gold coverage now exist; current managed scope keeps `2010-2023` county history as the canonical base and a latest-year ZIP industry-detail surface as a separate analytical table | [CBP.md](../../../notes/patterns_in_place_notes/Data/Sources/CBP.md) |
| [x] Ingested | EPA | Air quality; Hazard proximity; Toxic releases | AQI provider spec, staging, Silver, and Gold coverage now exist; current shared contract combines source-native AQI county/CBSA rows with tract-derived archival EJScreen rollups in `gold.environment_wide` | [EPA.md](../../../notes/patterns_in_place_notes/Data/Sources/EPA.md) |
| [x] Ingested | EPA Smart Location Database | Walkability; Transit access; Jobs accessibility | Source spec, staging, Silver, and Gold coverage now exist; current modeled contract keeps a compact 2021 county + derived CBSA/state built-form slice in `silver.epa_sld` and the dedicated baseline mart `gold.transport_built_form_sld`, with tract recovery deferred | [EPA.md](../../../notes/patterns_in_place_notes/Data/Sources/EPA.md) |
| [ ] Planned | FBI UCR / NIBRS | Violent crime; Property crime | Planned, medium priority; coverage audit first | [FBI UCR.md](../../../notes/patterns_in_place_notes/Data/Sources/FBI%20UCR.md) |
| [x] Ingested | FEMA | National Risk Index; Flood zone designations; Disaster declarations | Provider spec, staging, Silver, and Gold now cover FEMA NRI; current shared contract stages both county-equivalent and tract releases, models county + derived CBSA in Silver, and exposes a compact FEMA risk slice in `gold.environment_wide`; NFIP and disaster declarations remain future work | [FEMA.md](../../../notes/patterns_in_place_notes/Data/Sources/FEMA.md) |
| [x] Ingested | FHFA | Home price appreciation; Underserved areas | Provider spec, staging, Silver, and Gold now cover both annual HPI and the current-year underserved designation surface; the policy-designation slice lands in `gold.dim_policy_designations` | [FHFA.md](../../../notes/patterns_in_place_notes/Data/Sources/FHFA.md) |
| [x] Ingested | BFS | Business applications; Entrepreneurial activity | Provider spec, staging, Silver, and Gold coverage now exist; current managed scope is the annual county workbook with county-derived CBSA/state rollups, while monthly BFS remains a documented later option | [BFS.md](../../../notes/patterns_in_place_notes/Data/Sources/BFS.md) |
| [x] Ingested | BLS OEWS | Occupation structure; Occupational wages; Occupational specialization | Child topic spec, staging, Silver, and Gold coverage now exist; current shared contract stages the live `May 2025` state and metro/nonmetro workbooks, models the direct `state` + `cbsa` occupation panel in `silver.bls_oews`, and publishes the wide occupation-family mart `gold.economics_occupation_wide` | [source__bls_oews.md](./source__bls_oews.md) |
| [x] Ingested | IRS EO BMF | Nonprofits per 100k; Organized civic life | Provider spec, staging, Silver, and Gold coverage now exist; current managed scope uses the latest EO BMF snapshot, aggregates active organizations to ZIP5 first, allocates ZIP summaries to county via the HUD ZIP-county crosswalk, derives CBSA rows, and enriches `gold.social_fabric_wide` with nonprofit-density metrics | [source__irs_bmf.md](./source__irs_bmf.md) |
| [ ] Planned | IPEDS | College presence; Degrees granted; Research activity | Planned, medium priority | [IPEDS.md](../../../notes/patterns_in_place_notes/Data/Sources/IPEDS.md) |
| [ ] Planned | NOAA | Climate normals; Storm events; Sea level / coastal risk | Planned, lower priority; after FEMA NRI | [NOAA.md](../../../notes/patterns_in_place_notes/Data/Sources/NOAA.md) |
| [x] Ingested | Opportunity Zones | OZ designation | Provider spec, staging, Silver, and Gold coverage now exist; the static designation slice lands in `gold.dim_policy_designations` | [Opportunity Zones.md](../../../notes/patterns_in_place_notes/Data/Sources/Opportunity%20Zones.md) |
| [x] Ingested | Opportunity Insights Social Capital Atlas | Social capital; Economic connectedness; Cohesion; Civic engagement | Provider spec, staging, Silver, and Gold coverage now exist; current managed scope lands county and ZIP source slices in staging, models county/state/CBSA/ZCTA rows in `silver.opportunity_insights_social_capital`, and publishes the static baseline mart `gold.social_fabric_wide` | [source__social_capital_atlas.md](./source__social_capital_atlas.md) |
| [ ] Deferred | Opportunity Atlas | Intergenerational mobility; Upward mobility; Childhood-place outcomes | Research/spec is documented, but implementation is intentionally deferred for now to keep Track 14 focused on the Social Capital Atlas half | [source__opportunity_atlas.md](./source__opportunity_atlas.md) |
| [x] Ingested | USDA Food Access Research Atlas | Food desert designation; Low-access burden; Access & infrastructure | Source spec, staging, Silver, and Gold coverage now exist; current modeled contract keeps the 2019 tract-native baseline in `silver.usda_food_atlas` and the dedicated baseline mart `gold.food_access_wide` | [USDA.md](../../../notes/patterns_in_place_notes/Data/Sources/USDA.md) |
| [x] Ingested | USDA ERS County Typology | Rurality; Economic dependence; Persistent poverty; Retirement destination | Source spec, staging, and county-only Silver coverage now exist; the current managed contract keeps the full county-equivalent FIPS union in `silver.usda_county_typology` and defers any CBSA summarization to Gold | [source__usda_ers_typology.md](./source__usda_ers_typology.md) |
| [ ] Planned | Walk Score | Walkability; Transit access; Bikeability | Planned, medium priority; API access needed | [Walk Score.md](../../../notes/patterns_in_place_notes/Data/Sources/Walk%20Score.md) |

## Immediate Gaps To Close

- [x] Finish IRS beyond staging: canonical Silver contract now includes both a full OD flow table and a geography summary table, with Gold migration enrichment in place.
- [x] Promote Zillow from staging into documented Silver outputs and decide whether Gold belongs in `housing_core_wide` or a dedicated market table.
- [x] Model HUD CHAS into a documented Silver table and expose the approved burden fields in `gold.affordability_wide`.
- [x] Expand BLS beyond LAUS: QCEW staging, Silver curation, and Gold industry enrichment are now documented and materialized.

## Near-Term High-Priority Adds From Notes

- [x] CHR
- [x] Opportunity Zones

## Documentation Follow-Up

- [ ] Add source specs for product-specific active sources if they are expected to graduate into shared Foundations coverage.
- [ ] Keep this checklist aligned with both `sources/checklist.md` and the note files under `notes/patterns_in_place_notes/Data/Sources/`.
