# Source Spec: USDA Food Access Research Atlas

## 1. Overview

- Source: U.S. Department of Agriculture, Economic Research Service
- Program family in scope: Food Access Research Atlas (FARA)
- Access pattern: public XLSX / ZIP download plus ArcGIS REST map service; no API key required
- Current source vintage: `2019`
- Native geography: census tract
- Scope in Foundations: food-access / food-desert indicators for access and infrastructure analysis
- Documentation goal: define the first-pass ingest path, confirm the tract identifier, and identify the compact subset of fields to keep from the wide tract delivery

Unlike EPA Smart Location, this source already lands at tract grain, so the first implementation can stay tract-first and derive county / CBSA rows downstream without any block-group preprocessing step.

---

## 2. Source Contract

- Provider: U.S. Department of Agriculture, Economic Research Service
- Landing page: `https://www.ers.usda.gov/data-products/food-access-research-atlas`
- Verified download page: `https://www.ers.usda.gov/data-products/food-access-research-atlas/download-the-data`
- Verified developer page: `https://www.ers.usda.gov/developer/geospatial-apis`
- Verified ArcGIS REST service: `https://gisportal.ers.usda.gov/server/rest/services/FARA/FARA_2019/MapServer`
- Authentication: none

**What we verified**

- ERS's download page, updated on `January 5, 2025`, still lists the current downloadable data as "Food Access Research Atlas Data Download 2019."
- The current downloadable files are an `XLSX` workbook and a `ZIP` package; the page does not advertise a newer `2024`, `2025`, or `2026` release.
- ERS's main product page, updated on `September 23, 2025`, still describes the Atlas as a 2019-vintage comparison product against 2015.
- ERS also publishes a tract-based ArcGIS map service for the 2019 release.

**Recency conclusion**

There does not appear to be a newer public tract release than the 2019 Food Access Research Atlas as of `June 8, 2026`. We should treat 2019 as the current official vintage unless ERS publishes a new Atlas release later.

**Recommended ingestion path**

For Foundations, the bulk tabular download is the cleanest first path:

1. Prefer the downloadable workbook or ZIP package as the canonical raw landing.
2. Use the ArcGIS REST service as a schema-validation and QA fallback.
3. Avoid screen-scraping the interactive atlas because ERS already provides both bulk files and a service endpoint.

---

## 3. Native Geography And Format

**Observed tract-layer fields from the ERS ArcGIS service**

| Field | Meaning | Foundations handling |
| --- | --- | --- |
| `GEOID10` | Census tract identifier | Canonical tract key |
| `St_Name` | State name | QA helper |
| `Cnty_Name` | County name | QA helper |
| `CensusTract` | Display label | Optional QA helper |
| `Urban` | Urban tract flag | Important for interpreting 1-mile / 10-mile thresholds |
| `POP2010` | Tract population | Rollup weight / denominator |
| `OHU2010` | Housing units | Context field |

The ArcGIS layer describes `GEOID10` as the census tract field and exposes it as an 11-character string. That is the tract identifier we should standardize around in staging and Silver.

**Important source-vintage note**

ERS states the Atlas is based on `2010` census tract polygons even though some supporting demographic inputs come from later ACS releases. This means the tract key is a stable 2010-vintage tract identifier and should be treated as text immediately to preserve leading zeros.

---

## 4. Column Selection Approach

ERS publishes a much wider tract matrix than the handful of "food desert" flags most downstream use cases need.

The approved first-pass approach is:

1. Keep the tract identifier and a small set of context fields.
2. Keep the main low-income + low-access designation flags.
3. Keep the population counts and shares that let us summarize food-access burden, not just tract classifications.
4. Keep a few subgroup burden fields if they meaningfully improve interpretation.
5. Leave the full long tail of race- and threshold-specific variants in raw staging only if the source package makes them easy to retain.

This gives us a tract-level contract that is useful analytically without forcing every downstream table to inherit the entire ERS field inventory.

---

## 5. Preferred First-Pass Keep List

**Core geography and tract context**

| Output column | Source column | Why keep it |
| --- | --- | --- |
| `tract_geoid` | `GEOID10` | Canonical tract key |
| `state_name` | `St_Name` | QA helper |
| `county_name` | `Cnty_Name` | QA helper |
| `census_tract_label` | `CensusTract` | Human-readable QA helper |
| `urban_flag` | `Urban` | Needed to interpret threshold logic |
| `population_total` | `POP2010` | Rollup weight and core denominator |
| `housing_units_total` | `OHU2010` | Context field |
| `group_quarters_flag` | `GroupQuartersFlag` | Useful caveat field for tract interpretation |
| `group_quarters_population` | `NUMGQTRS` | Context field |
| `group_quarters_share` | `PCTGQTRS` | Context field |

**Primary low-income and low-access flags**

| Output column | Source column | Why keep it |
| --- | --- | --- |
| `lila_1_and_10_flag` | `LILATracts_1And10` | Canonical food-desert style designation ERS emphasizes |
| `lila_half_and_10_flag` | `LILATracts_halfAnd10` | Alternate urban threshold sensitivity check |
| `lila_1_and_20_flag` | `LILATracts_1And20` | Rural threshold sensitivity check |
| `lila_vehicle_flag` | `LILATracts_Vehicle` | Vehicle-access variant |
| `low_income_flag` | `LowIncomeTracts` | Separates poverty status from access status |
| `low_access_1_and_10_flag` | `LA1and10` | Main low-access tract flag aligned to urban/rural thresholds |
| `low_access_half_and_10_flag` | `LAhalfand10` | Alternate threshold |
| `low_access_1_and_20_flag` | `LA1and20` | Rural threshold alternative |

**Primary burden counts and shares**

| Output column | Source column | Why keep it |
| --- | --- | --- |
| `low_access_pop_1` | `lapop1` | Core user-requested burden count at 1 mile |
| `low_access_pop_1_share` | `lapop1share` | Share version of the same burden |
| `low_access_pop_1_10` | `LAPOP1_10` | Urban/rural-combined burden count aligned to main ERS threshold |
| `low_access_pop_half_10` | `LAPOP05_10` | Alternate threshold burden count |
| `low_access_pop_1_20` | `LAPOP1_20` | Rural-threshold sensitivity burden count |
| `low_access_low_income_pop_1` | `lalowi1` | Low-income + low-access burden count |
| `low_access_low_income_pop_1_share` | `lalowi1share` | Share version of the same burden |
| `low_access_low_income_pop_1_10` | `LALOWI1_10` | Combined burden count at main threshold |
| `poverty_rate` | `PovertyRate` | Interpretation context |
| `median_family_income` | `MedianFamilyIncome` | Interpretation context |

**Optional first-pass subgroup burden fields worth keeping**

| Output column | Source column | Why keep it |
| --- | --- | --- |
| `low_access_children_1` | `lakids1` | Vulnerable population context |
| `low_access_children_1_share` | `lakids1share` | Share version |
| `low_access_seniors_1` | `laseniors1` | Vulnerable population context |
| `low_access_seniors_1_share` | `laseniors1share` | Share version |
| `low_access_no_vehicle_housing_1` | `lahunv1` | Mobility constraint signal if present in the bulk file |
| `low_access_no_vehicle_housing_1_share` | `lahunv1share` | Share version if present |
| `low_access_snap_housing_1` | `lasnap1` | Food assistance context if present |
| `low_access_snap_housing_1_share` | `lasnap1share` | Share version if present |

If the bulk workbook uses slightly different capitalization than the ArcGIS layer, staging should preserve the source names first and normalize them afterward.

---

## 6. Preferred First-Pass Staging Contract

Recommended staging table:
- `staging.usda_food_atlas`
- one row per census tract
- no geometry retained in the first pass
- retain tract FIPS as character immediately

**`staging.usda_food_atlas`**

| Column | Type | Description |
| --- | --- | --- |
| `tract_geoid` | VARCHAR | 11-digit tract GEOID |
| `state_name` | VARCHAR | State name |
| `county_name` | VARCHAR | County name |
| `census_tract_label` | VARCHAR | Human-readable tract label |
| `urban_flag` | INTEGER | Urban tract indicator |
| `population_total` | INTEGER | Tract population |
| `housing_units_total` | INTEGER | Tract housing units |
| `group_quarters_flag` | DOUBLE | High group-quarters tract flag |
| `group_quarters_population` | INTEGER | Group-quarters count |
| `group_quarters_share` | DOUBLE | Group-quarters share |
| `lila_1_and_10_flag` | INTEGER | Main low-income + low-access flag |
| `lila_half_and_10_flag` | INTEGER | Alternate threshold LILA flag |
| `lila_1_and_20_flag` | INTEGER | Rural threshold LILA flag |
| `lila_vehicle_flag` | INTEGER | Vehicle-access LILA flag |
| `low_income_flag` | INTEGER | Low-income tract flag |
| `low_access_1_and_10_flag` | INTEGER | Main low-access flag |
| `low_access_half_and_10_flag` | INTEGER | Alternate threshold low-access flag |
| `low_access_1_and_20_flag` | INTEGER | Rural threshold low-access flag |
| `low_access_pop_1` | INTEGER | Population with low access at 1 mile |
| `low_access_pop_1_share` | DOUBLE | Share with low access at 1 mile |
| `low_access_pop_1_10` | INTEGER | Main threshold low-access population count |
| `low_access_pop_half_10` | INTEGER | Alternate threshold count |
| `low_access_pop_1_20` | INTEGER | Rural threshold count |
| `low_access_low_income_pop_1` | INTEGER | Low-income + low-access count at 1 mile |
| `low_access_low_income_pop_1_share` | DOUBLE | Share version |
| `low_access_low_income_pop_1_10` | INTEGER | Main threshold low-income + low-access count |
| `poverty_rate` | DOUBLE | Tract poverty rate |
| `median_family_income` | INTEGER | Median family income |

---

## 7. Preferred Silver Contract

Preferred first-pass Silver output:
- `silver.usda_food_atlas`
- tract, county, and CBSA rows
- one row per `geo_level + geo_id + year`
- use `2019` as the Atlas vintage year

Recommended first-pass Silver columns:

| Silver column | Source basis | Notes |
| --- | --- | --- |
| `geo_level` | derived | `tract`, `county`, `cbsa` |
| `geo_id` | tract GEOID or derived county / CBSA key | Canonical Foundations geography key |
| `year` | fixed `2019` | Current official Atlas vintage |
| `pct_lila_tracts_1_and_10` | mean of `LILATracts_1And10` | Share of tracts designated low income + low access |
| `pct_low_income_tracts` | mean of `LowIncomeTracts` | Share of tracts designated low income |
| `pct_low_access_tracts_1_and_10` | mean of `LA1and10` | Share of tracts designated low access |
| `population_low_access_1_10` | sum of `LAPOP1_10` | Count burden at main threshold |
| `population_low_income_low_access_1_10` | sum of `LALOWI1_10` | Combined burden count |
| `pct_population_low_access_1_10` | summed burden divided by summed population | Main interpretable population burden rate |
| `pct_population_low_access_1` | summed `lapop1` divided by summed population | Simple urban-style burden measure |
| `pct_population_low_income_low_access_1` | summed `lalowi1` divided by summed population | Combined burden rate |
| `poverty_rate` | population-weighted mean | Context field |
| `median_family_income` | population-weighted mean or staged-only | Keep only if aggregation is analytically acceptable |

County and CBSA rollups should be derived in Silver, not staged upstream. The tract grain is already source-native and should remain the canonical raw landing.

---

## 8. Operational Notes

- This source is materially stale compared with many other annual feeds, but it is still the current official ERS Food Access Research Atlas release.
- The download page explicitly says the tract data should be joined to census tract boundaries for GIS use; that is another signal that the workbook / flat-file path is the intended tabular ingest route.
- The ArcGIS REST service is especially useful for validating field names before we write the staging script because it exposes the tract schema directly.
- The Atlas mixes tract classifications, burden counts, burden shares, and subgroup fields. Silver should be deliberate about which of those become stable modeled metrics.
- In practice, the tract key is strong enough to keep tract rows source-native in Silver and derive counties directly from the tract GEOID prefix.
- The first-pass modeled contract follows the same lesson as EPA SLD: treat this as a specialty baseline source and keep it in its own Gold mart (`gold.food_access_wide`) rather than mixing sparse 2019-only fields into the broader recurring transport panel.
- The county geography edge case mirrors Track 9: keep the 8 legacy Connecticut county GEOIDs explicitly for alignment with the current county contract and exclude Alaska county-equivalent `02261` from the derived county / CBSA rollups.

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- `../../etl/staging/get_usda_food_atlas.R`
