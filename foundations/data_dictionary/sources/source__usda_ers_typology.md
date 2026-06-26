# Source Spec: USDA ERS County Typology and Rural-Urban Continuum Codes

## 1. Overview

- Source: U.S. Department of Agriculture, Economic Research Service
- Program family in scope: Rural-Urban Continuum Codes (`RUCC`) and County Typology Codes
- Access pattern: public CSV / XLSX downloads plus methodology pages; no API key required
- Current verified releases as of `June 24, 2026`: `2023` Rural-Urban Continuum Codes and `2025` County Typology Codes
- Native geography: county or county-equivalent, with important source-specific geography differences called out below
- Scope in Foundations: slow-moving county classification attributes that are best treated as geography-dimension enrichments rather than recurring fact tables
- Documentation goal: confirm the live download surface, document the delivered file shape, and define the narrowest safe staging -> Silver -> Gold path

This source family is small, but it is not quite trivial. The files are already compact and mostly normalized, so the ETL can stay light. The main wrinkle is geography alignment: `RUCC` is published on the current county-equivalent backbone including Connecticut planning regions and U.S. territories, while the `2025` County Typology file covers only the 50 States plus Washington, D.C. and mixes Connecticut planning regions with legacy Connecticut counties depending on the attribute family.

---

## 2. Coverage Matrix

| Topic group | Staging family contracts | Silver outputs | Likely Gold placement |
| --- | --- | --- | --- |
| Rural-Urban Continuum Codes (`2023`) | `staging.usda_rucc` | `silver.usda_county_typology` | county-level structural columns on `gold.dim_geo` |
| County Typology Codes (`2025`) | `staging.usda_county_typology` | `silver.usda_county_typology` | county-level structural columns on `gold.dim_geo` |

The cleanest first pass is two tiny staging tables feeding one unified Silver dimension table.

---

## 3. Source Contract

- Provider: U.S. Department of Agriculture, Economic Research Service
- RUCC landing page: `https://www.ers.usda.gov/data-products/rural-urban-continuum-codes/`
- RUCC documentation page: `https://www.ers.usda.gov/data-products/rural-urban-continuum-codes/documentation`
- RUCC current CSV download: `https://www.ers.usda.gov/media/5768/2023-rural-urban-continuum-codes.csv?v=25487`
- County Typology landing page: `https://www.ers.usda.gov/data-products/county-typology-codes/`
- County Typology descriptions/maps page: `https://www.ers.usda.gov/data-products/county-typology-codes/descriptions-and-maps`
- County Typology documentation page: `https://www.ers.usda.gov/data-products/county-typology-codes/documentation`
- County Typology current CSV download: `https://www.ers.usda.gov/media/6174/ers-county-typology-codes-2025-edition.csv?v=55079`
- Authentication: none

**What we verified**

- The live RUCC product page was updated on `December 30, 2025` and still serves the `2023` edition.
- The RUCC download artifact itself is marked `Last Updated 1/22/2024`.
- The live County Typology product page was updated on `December 31, 2025` and serves the `2025` edition.
- The County Typology CSV artifact is marked `Last Updated 4/11/2025`.
- RUCC is updated roughly once per decade: `1974`, `1983`, `1993`, `2003`, `2013`, `2023`.
- County Typology is also roughly decennial rather than annual: historical files include `1979/1986`, `1989`, `2004`, `2015`, and `2025`.

**County identifier conclusion**

- The operational join key is a 5-character county or county-equivalent FIPS code.
- RUCC publishes that key as `FIPS`.
- County Typology publishes that key as `FIPStxt`.
- Both should be cast to text immediately and preserved with leading zeros.

**Important geography scope differences**

- RUCC classifies `3,235` county and county-equivalent entities, including Puerto Rico and other outlying territories.
- RUCC includes Connecticut planning regions instead of legacy Connecticut counties.
- The RUCC documentation explicitly notes that two American Samoa entities with zero population in `2020` are carried in the file but do not receive a `RUCC_2023` row.
- The `2025` County Typology file covers `3,152` entities in the 50 States plus Washington, D.C.; county-equivalents in U.S. territories are not classified.
- County Typology uses mixed Connecticut geography:
  - ACS-based attributes use the `9` Connecticut planning regions.
  - BEA / older-ACS / migration-based attributes use the `8` legacy Connecticut counties.

---

## 4. Staging Shape

Both downloads are already delivered in long `Attribute` / `Value` form, which is unusually convenient for a first-pass staging design.

### `2023` RUCC CSV

Observed header:

- `FIPS`
- `State`
- `County_Name`
- `Attribute`
- `Value`

Observed shape:

- `9,704` total rows including header
- `3,235` unique county or county-equivalent keys
- `3` expected attributes:
  - `Population_2020`
  - `RUCC_2023`
  - `Description`
- `RUCC_2023` appears for `3,233` entities rather than `3,235` because `60030` and `60040` in American Samoa do not receive a code row

This means the source is already almost a tiny EAV table and does not need any denormalization in staging.

### `2025` County Typology CSV

Observed header:

- `FIPStxt`
- `State`
- `County_Name`
- `Metro2023`
- `Attribute`
- `Value`
- `PublicationDate`
- `Source`

Observed shape:

- `40,977` total rows including header
- `3,152` unique county or county-equivalent keys
- `13` expected attributes:
  - `High_Farming_2025`
  - `High_Mining_2025`
  - `High_Manufacturing_2025`
  - `High_Government_2025`
  - `High_Recreation_2025`
  - `Nonspecialized_2025`
  - `Industry_Dependence_2025`
  - `Low_PostSecondary_Ed_2025`
  - `Low_Employment_2025`
  - `Population_Loss_2025`
  - `Housing_Stress_2025`
  - `Retirement_Destination_2025`
  - `Persistent_Poverty_1721`

Observed value patterns:

- Most concentration and demographic flags are coded as `0` / `1`.
- `Industry_Dependence_2025` carries categorical numeric codes with observed values `0`, `1`, `2`, `3`, `4`, `5`, and `99`.
- `Persistent_Poverty_1721` also carries special sentinel values: observed values include `-1`, `0`, `1`, and `99`.
- `99` is used in the file where a code is not classified or not available for that geography / attribute family and should be preserved source-faithfully in staging.

The delivered file is already small enough that staging should keep it nearly verbatim.

---

## 5. Staging To Silver

Recommended first-pass handoff:

1. Stage `RUCC` source-faithfully in `staging.usda_rucc`.
2. Stage County Typology source-faithfully in `staging.usda_county_typology`.
3. Pivot each staging table to one row per source geography key in Silver prep.
4. Join the two widened county-classification tables on normalized FIPS where the geography backbone matches directly.
5. Materialize one unified Silver dimension table, `silver.usda_county_typology`.
6. Keep any CBSA rollups as derived Silver rows rather than pushing those derived summaries straight into Gold.

Recommended first-pass Silver grain:

- one row per `geo_level + geo_id + vintage_year`
- `geo_level` in practice should start with `county`
- optional derived `cbsa` rows can be added after county QA is stable

The simplest useful Silver design is a wide county-classification table with one column per stable ERS concept, plus the published `2023` metro/nonmetro flag.

---

## 6. Transformation Notes

### Recommended staging tables

**`staging.usda_rucc`**

- keep the file in source-native long form
- preserve:
  - `fips`
  - `state_abbr`
  - `county_name`
  - `attribute`
  - `value`

**`staging.usda_county_typology`**

- keep the file in source-native long form
- preserve:
  - `fips`
  - `state_abbr`
  - `county_name`
  - `metro2023`
  - `attribute`
  - `value`
  - `publication_date`
  - `source_note`

### Recommended Silver columns

The county-level Silver table should likely carry:

- `geo_level`
- `geo_id`
- `geo_name`
- `vintage_year`
- `rucc_2023_code`
- `rucc_2023_description`
- `population_2020`
- `metro2023_flag`
- `high_farming_flag`
- `high_mining_flag`
- `high_manufacturing_flag`
- `high_government_flag`
- `high_recreation_flag`
- `nonspecialized_flag`
- `industry_dependence_code`
- `industry_dependence_label`
- `low_postsecondary_ed_flag`
- `low_employment_flag`
- `population_loss_flag`
- `housing_stress_flag`
- `retirement_destination_flag`
- `persistent_poverty_flag`

### Recommended code handling

- Treat `RUCC_2023` as a small integer code but preserve the published description text.
- Treat `Industry_Dependence_2025` as a coded category.
- The observed category ordering strongly suggests:
  - `0` = not dependent
  - `1` = farming dependent
  - `2` = mining dependent
  - `3` = manufacturing dependent
  - `4` = government dependent
  - `5` = recreation dependent
- That label mapping should be documented in Silver as an implementation inference from the published ERS category order and verified against the final ETL QA output.
- Preserve `99` and `-1` through staging; only coerce them to null or explicit sentinel labels in Silver after the affected attribute semantics are pinned in code comments.

### Connecticut handling is the real design decision

This is the only part that should not be glossed over:

- `RUCC` uses the current Connecticut planning-region geography.
- County Typology uses planning regions for ACS-based attributes and legacy counties for several other attributes.
- The current Foundations county contract still prefers the `8` legacy Connecticut county GEOIDs in multiple downstream paths.

Best first-pass approach:

1. Keep both source files fully source-faithful in staging.
2. Make Connecticut reconciliation a deliberate Silver-only step.
3. Do not silently collapse planning regions to legacy counties inside staging.
4. For the first modeled Gold enrichment, prioritize county rows that match the existing county backbone directly and document Connecticut as a managed exception if needed.

That is simpler and safer than inventing a planning-region-to-legacy-county bridge inside raw ingest.

---

## 7. Data Quality Expectations

Non-boilerplate checks worth preserving:

- `RUCC` should have exactly one row per `fips + attribute` and exactly three expected attributes.
- County Typology should have exactly one row per `fips + attribute` and exactly thirteen expected attributes.
- FIPS keys must remain 5-character text with leading zeros preserved.
- `RUCC` should carry `3,235` distinct keys, but only `3,233` `RUCC_2023` code rows.
- County Typology should carry `3,152` distinct keys.
- County Typology should preserve published sentinel values such as `99` and `-1` until the Silver model handles them intentionally.
- Any county-level join audit should explicitly flag Connecticut geography mismatches instead of treating them as generic failed joins.
- Gold enrichment QA should verify that no recurring metrics tables are polluted with static classification fields that belong in a dimension.

---

## 8. Operational Notes

- Shared staging source tracker:
  [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- Recommended staging entrypoint:
  `../../etl/staging/get_usda_ers_typology.R`
- Suggested Silver entrypoint:
  `../../etl/silver/usda_ers_typology_silver.R`

**Why two staging tables and one Silver table is the right size**

- The source family is already small.
- The files are already mostly normalized.
- There is no benefit to splitting RUCC and Typology into separate downstream Silver marts once the county rows are widened.
- The useful downstream semantics are dimension-like place attributes, not time-series facts.

**Recommended Gold placement**

- The best fit is `gold.dim_geo`, not a new fact table.
- County-level fields such as `rucc_2023_code`, `rucc_2023_description`, `industry_dependence_label`, and boolean challenge flags are structural attributes of place.
- Derived CBSA summaries are analytically useful, but they are less natural as permanent `gold.dim_geo` columns than the county-native classifications.
- A good first pass is:
  - enrich county rows on `gold.dim_geo`
  - keep `silver.usda_county_typology` county-only
  - derive any CBSA summaries later in Gold from the common county-equivalent backbone only, with the rollup rule documented explicitly

This is a simpler approach than immediately adding share-based CBSA summary columns to a geography identity dimension.

---

## 9. Known Gaps

- The exact official semantics of County Typology sentinel values `99` and `-1` should be pinned in the ETL comments when the staging script is written.
- Connecticut geography alignment is the only meaningful modeling complication and may require a documented exception policy for Gold.
- `RUCC` includes territories while County Typology does not, so the unified Silver table will have asymmetric source coverage unless we intentionally subset to the common backbone.
- The current source spec confirms shape and ingestion strategy; county-level Gold enrichment and any future CBSA Gold rollups still need a final managed contract.
