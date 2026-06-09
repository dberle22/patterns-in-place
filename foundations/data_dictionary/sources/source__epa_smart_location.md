# Source Spec: EPA Smart Location Database

## 1. Overview

- Source: U.S. Environmental Protection Agency
- Program family in scope: Smart Location Database (SLD), version `3.0`
- Access pattern: public bulk download plus ArcGIS REST map service; no API key required
- Current source vintage: EPA states the current SLD version was updated in `2021`
- Native geography: census block group
- Scope in Foundations: transportation / built-form indicators that complement ACS commute behavior with built-environment context
- Documentation goal: define the first-pass ingest path, confirm the native block-group key, and identify the compact subset of SLD indicators we want to keep for Foundations

This is a topic-level child spec under the broader EPA provider family. EPA already has a provider-level source spec in [source__epa.md](./source__epa.md); this document narrows to the Smart Location Database dataset family because its geography, delivery format, and downstream modeling path differ from AQI and EJScreen.

---

## 2. Source Contract

- Provider: U.S. Environmental Protection Agency
- Landing page: `https://www.epa.gov/smartgrowth/smart-location-mapping`
- Verified bulk download entry point: EPA's SLD page links a public ZIP download for "all areas with coverage"
- Verified direct CSV file: `https://edg.epa.gov/data/Public/OA/EPA_SmartLocationDatabase_V3_Jan_2021_Final.csv`
- Verified API entry point: `https://geodata.epa.gov/arcgis/rest/services/OA/SmartLocationDatabase/MapServer`
- Verified technical guide: `https://www.epa.gov/system/files/documents/2023-10/epa_sld_3.0_technicaldocumentationuserguide_may2021_0.pdf`
- Authentication: none
- Refresh pattern: infrequent point-in-time releases, not an annual recurring feed

**What we verified**

- EPA says the Smart Location Database "was updated to its current version in 2021."
- EPA describes the dataset as a nationwide block-group resource with more than 90 attributes.
- EPA exposes the dataset as a downloadable ZIP and as an ArcGIS REST service.
- EPA's technical documentation identifies `GEOID10` as the 2010 census block-group FIPS code and also documents an updated `GEOID20` based on newer block-group boundaries.

**Recommended ingestion path**

For Foundations, the easiest operational path is to ingest the tabular form rather than the full geospatial package:

1. Prefer the bulk tabular extract if EPA's ZIP resolves to a flat file export.
2. If the ZIP only yields a geodatabase, fall back to reading the attribute table from the geodatabase.
3. Keep the ArcGIS REST service as a secondary retrieval path for schema inspection, targeted QA, or if the bulk file moves.

In practice, the direct CSV file is the best first-pass ingest path for Foundations. It is easier than the geodatabase route and already contains the attribute fields we need for staging.

Because Track 9 is explicitly about modeled indicators rather than geometry storage, we should avoid treating SLD as a shapefile-first ingest unless the tabular path proves unavailable.

---

## 3. Native Geography And Format

**Observed geography keys from EPA documentation**

| Field | Meaning | Foundations handling |
| --- | --- | --- |
| `GEOID10` | 2010 census block-group FIPS code | Preferred canonical key for first-pass staging because Track 9 explicitly called out `GEOID10` |
| `GEOID20` | Updated block-group FIPS code based on newer boundaries | Keep in staging for future reconciliation, but do not make it the first canonical key yet |
| `STATEFP` | State FIPS | QA / rollup helper |
| `COUNTYFP` | County FIPS | QA / county rollup helper |
| `TRACTCE` | Tract code | Use with state + county for tract derivation |
| `CBSA` | Core-based statistical area code | Helpful for direct metro rollup validation |
| `CBSA_Name` | CBSA display name | QA / display helper |

**Geography decision**

Track 9 asked us to confirm `GEOID10` as the block-group identifier. Based on EPA's published documentation, we should:

- use `GEOID10` as the first-pass block-group join key
- retain `GEOID20` in staging as a future-proof helper
- derive tract GEOID as the first 11 characters of `GEOID10` for tract aggregation
- derive county GEOID as the first 5 characters of `GEOID10` for county aggregation

This keeps the first implementation aligned with the published track scope while still preserving the newer boundary field for later compatibility work.

**Important delivery quirk from the live CSV**

The current EPA CSV writes both `GEOID10` and `GEOID20` in scientific notation, which makes them unsafe as direct join keys. The companion component fields (`STATEFP`, `COUNTYFP`, `TRACTCE`, `BLKGRPCE`) are intact, so the staging script should reconstruct the canonical 12-digit block-group GEOID from those parts and retain the raw `GEOID10` / `GEOID20` strings only as provenance helpers.

---

## 4. Column Selection Approach

EPA publishes 90+ variables. Foundations should not carry the full SLD width into Silver or Gold.

The approved first-pass approach is:

1. Stage the geography helpers plus a compact set of high-signal built-form fields.
2. Keep enough denominator and provenance fields to support rollups and QA.
3. Focus the modeled contract on density, land-use mix, street-network design, walkability, and accessibility.
4. Leave more specialized or duplicative SLD variables out of the first modeled pass unless Gold clearly needs them.

The goal is not to recreate EPA's full transportation research product in Foundations. The goal is to preserve the subset that best improves our transportation / built-form topic beyond ACS commute metrics.

---

## 5. Preferred First-Pass Keep List

**Core geography and helper fields**

| Output column | Source column | Why keep it |
| --- | --- | --- |
| `bg_geoid` | `GEOID10` | Canonical first-pass block-group key |
| `bg_geoid_2020` | `GEOID20` | Boundary-transition QA helper |
| `state_fips` | `STATEFP` | Geography QA |
| `county_fips` | `COUNTYFP` | County rollup helper |
| `tract_code` | `TRACTCE` | Tract rollup helper |
| `cbsa_code` | `CBSA` | Metro rollup QA helper |
| `cbsa_name` | `CBSA_Name` | Human-readable metro helper |
| `total_population` | `TotPop` | Weight for tract / county / CBSA aggregation |
| `housing_units` | `CountHU` | Useful scale denominator and QA field |
| `households` | `HH` | Useful scale denominator and QA field |
| `land_acres_unprotected` | `Ac_Unpr` | Denominator context for gross density fields |

**High-signal modeled indicators for Foundations**

| Output column | Source column | Why keep it |
| --- | --- | --- |
| `walkability_index` | `NatWalkInd` | EPA's compact composite walkability signal |
| `employment_housing_mix` | `D2A_EPHHM` | Strong built-form diversity measure combining jobs and housing |
| `employment_mix` | `D2B_E8MIXA` | Employment diversity / land-use mix signal |
| `street_intersection_density` | `D3b` | Canonical walkable-network measure |
| `auto_oriented_intersection_share` | `D3aao` | Useful street-network complement to pedestrian-oriented density |
| `transit_service_density` | `D4b025` | Practical transit-service intensity signal where GTFS coverage exists |
| `transit_frequency_peak` | `D4d` | Peak transit service signal |
| `distance_to_transit` | `D4e` | Simple and interpretable access-to-transit measure |
| `jobs_access_45min_transit` | `D5ar` | Destination accessibility by transit |
| `workers_access_45min_transit` | `D5ae` | Access to working-age population by transit |
| `jobs_access_45min_auto` | `D5br` | Destination accessibility by auto |
| `workers_access_45min_auto` | `D5be` | Access to working-age population by auto |
| `employment_density_gross` | `D1c` | Core employment density field |
| `population_density_gross` | `D1b` | Core population density field |
| `housing_density_gross` | `D1a` | Core residential density field |

This is the ~15-field compact contract Track 9 called for. It covers the main "5 Ds" families without dragging along the full SLD research matrix.

---

## 6. Preferred First-Pass Staging Contract

Recommended staging table:
- `staging.epa_sld`
- one row per census block group
- no geometry retained in the first pass
- source names normalized with straightforward snake_case aliases in the staging script

**`staging.epa_sld`**

| Column | Type | Description |
| --- | --- | --- |
| `bg_geoid` | VARCHAR | 12-digit block-group GEOID from `GEOID10` |
| `bg_geoid_2020` | VARCHAR | Updated block-group GEOID from `GEOID20` |
| `state_fips` | VARCHAR | Two-digit state FIPS |
| `county_fips` | VARCHAR | Three-digit county FIPS within state |
| `tract_code` | VARCHAR | Six-digit tract code within county |
| `cbsa_code` | VARCHAR | CBSA code where available |
| `cbsa_name` | VARCHAR | CBSA name where available |
| `total_population` | DOUBLE | Population denominator |
| `housing_units` | DOUBLE | Housing-unit denominator |
| `households` | DOUBLE | Household denominator |
| `land_acres_unprotected` | DOUBLE | Unprotected land area denominator |
| `walkability_index` | DOUBLE | EPA walkability index |
| `employment_housing_mix` | DOUBLE | Employment + housing diversity signal |
| `employment_mix` | DOUBLE | Employment entropy / mix |
| `street_intersection_density` | DOUBLE | Pedestrian-oriented intersection density |
| `auto_oriented_intersection_share` | DOUBLE | Auto-oriented network signal |
| `transit_service_density` | DOUBLE | Transit service density |
| `transit_frequency_peak` | DOUBLE | Peak transit frequency |
| `distance_to_transit` | DOUBLE | Distance to nearest transit stop |
| `jobs_access_45min_transit` | DOUBLE | Jobs accessible by transit |
| `workers_access_45min_transit` | DOUBLE | Working-age population accessible by transit |
| `jobs_access_45min_auto` | DOUBLE | Jobs accessible by car |
| `workers_access_45min_auto` | DOUBLE | Working-age population accessible by car |
| `employment_density_gross` | DOUBLE | Jobs per acre |
| `population_density_gross` | DOUBLE | People per acre |
| `housing_density_gross` | DOUBLE | Housing units per acre |

---

## 7. Preferred Silver Contract

Preferred first-pass Silver output:
- `silver.epa_sld`
- tract, county, and CBSA rows
- one row per `geo_level + geo_id + year`
- use `2021` as the published SLD vintage year

Recommended aggregation logic:

- population-weighted means for accessibility and mix measures tied to people or neighborhood experience
- simple sums are generally not appropriate for index-like fields such as `NatWalkInd`
- density fields should be recomputed carefully only if the source numerators and denominators are preserved; otherwise use weighted means with explicit documentation
- transit fields will have partial coverage because EPA notes GTFS-based transit measures are only available where agencies share GTFS feeds

Recommended first-pass Silver columns:

| Silver column | Source basis | Notes |
| --- | --- | --- |
| `geo_level` | derived | `tract`, `county`, `cbsa` |
| `geo_id` | derived from `bg_geoid` / crosswalks | Canonical Foundations geography key |
| `year` | fixed `2021` | SLD version vintage |
| `walkability_index` | `NatWalkInd` | Core composite built-form signal |
| `employment_housing_mix` | `D2A_EPHHM` | Core land-use mix signal |
| `employment_mix` | `D2B_E8MIXA` | Employment diversity signal |
| `street_intersection_density` | `D3b` | Core network design signal |
| `transit_service_density` | `D4b025` | Transit service intensity |
| `transit_frequency_peak` | `D4d` | Peak-period service |
| `distance_to_transit` | `D4e` | Transit proximity |
| `jobs_access_45min_transit` | `D5ar` | Transit accessibility to jobs |
| `workers_access_45min_transit` | `D5ae` | Transit accessibility to workers |
| `jobs_access_45min_auto` | `D5br` | Auto accessibility to jobs |
| `workers_access_45min_auto` | `D5be` | Auto accessibility to workers |
| `employment_density_gross` | `D1c` | Employment density |
| `population_density_gross` | `D1b` | Population density |
| `housing_density_gross` | `D1a` | Housing density |

---

## 8. Operational Notes

- This is a static-ish baseline source, not a rolling annual feed.
- The block-group grain means Silver should own all tract / county / CBSA aggregation decisions.
- `GEOID10` and `GEOID20` should both be preserved in staging until we decide whether the rest of the tract backbone should migrate to newer block-group boundaries.
- Transit-service fields are coverage-limited by GTFS availability, so nulls are expected outside supported metros.
- If EPA's bulk ZIP proves awkward to read directly, the ArcGIS REST service gives us a stable fallback for schema discovery and targeted extracts.
- Current implementation note: the first modeled Silver contract should stay county-only. The direct CSV is sufficient for reliable county rollups because `STATEFP` and `COUNTYFP` survive delivery intact, but tract-level recovery is not yet reliable from the CSV alone because the delivered `GEOID10` / `GEOID20` values are scientific-notation strings and a meaningful share of reconstructed tract IDs do not resolve cleanly against the current tract backbone. A future tract fix should use the official Census 2010/2020 tract relationship files or the geodatabase-based SLD delivery.
- County edge-case note: the first-pass Silver model keeps the 8 legacy Connecticut county GEOIDs through an explicit manual fallback so the 2021 SLD rows align with the 2021 ACS county transport contract. Alaska county-equivalent `02261` still remains excluded because the current county crosswalk no longer carries that retired geography.

Shared source references:
- [source__epa.md](./source__epa.md)
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- planned: `../../etl/staging/get_epa_sld.R`
