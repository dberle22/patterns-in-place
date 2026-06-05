# Source Spec: Zillow

## 1. Overview

- Source: Zillow Research public market-data files
- Access pattern: provider CSV downloads
- Primary dependency: public Zillow Research files plus local raw-data and DuckDB paths
- Scope in Foundations: current coverage includes the Zillow Home Value Index and Zillow Observed Rent Index, both staged as monthly long tables across several geography types, plus documented Silver and Gold contracts for the county / ZCTA / CBSA surface.
- Documentation goal: this file is the provider-level spec for Zillow as it is currently represented in Foundations.

## 2. Coverage Matrix

This source spec covers the Zillow topic groups currently documented in the data dictionary.

| Topic group | Staging family contracts | Silver outputs |
| --- | --- | --- |
| ZHVI | [../layers/staging/staging__zillow_zhvi.md](../layers/staging/staging__zillow_zhvi.md) | [../layers/silver/silver__zillow_zhvi.md](../layers/silver/silver__zillow_zhvi.md) |
| ZORI | [../layers/staging/staging__zillow_zori.md](../layers/staging/staging__zillow_zori.md) | [../layers/silver/silver__zillow_zori.md](../layers/silver/silver__zillow_zori.md) |

## 3. Source Contract

- Provider: Zillow Research
- Retrieval interface in current coverage: public CSV downloads
- Common request pattern: one CSV per geography type and index family, cached locally before being pivoted into monthly long format
- Common geography pattern:
  ZHVI covers state, county, city, and ZIP;
  ZORI covers county, city, and ZIP
- Common time pattern: monthly observations, filtered to years after 2010 during staging

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- [../../etl/staging/get_zillow.R](../../etl/staging/get_zillow.R)

| Topic group | Source files / subject area | Staging ingest entrypoint |
| --- | --- | --- |
| ZHVI | Zillow Home Value Index public CSVs by geography type | [../../etl/staging/get_zillow.R](../../etl/staging/get_zillow.R) |
| ZORI | Zillow Observed Rent Index public CSVs by geography type | [../../etl/staging/get_zillow.R](../../etl/staging/get_zillow.R) |

## 4. Staging Shape

Common Zillow staging pattern:
- one staging family contract per index
- one materialized table per geography slice
- monthly source columns are pivoted from wide to long
- each row carries a parsed date plus `year` and `month`

| Topic group | Staging family | Coverage shape |
| --- | --- | --- |
| ZHVI | `staging__zillow_zhvi` | state, county, city, and ZIP monthly long tables |
| ZORI | `staging__zillow_zori` | county, city, and ZIP monthly long tables |

Shared staging notes by topic:
- ZHVI shared columns center on `state`, `region_type`, `date`, `year`, `month`, and `zhvi`, with county, city, or ZIP identifiers added by slice.
- ZORI shared columns center on `region_type`, `state`, `metro`, `county_name`, `date`, `year`, `month`, and `zori`, with city or ZIP identifiers added by slice.

## 5. Staging To Silver

Current Zillow handoff pattern:
1. Download geography-specific Zillow files.
2. Pivot monthly columns into long-format staging tables.
3. Standardize county and ZIP slices into Silver analytical contracts.
4. Rebase county slices to CBSA in Silver using ACS housing-unit weights.
5. Aggregate monthly Silver rows into annual Gold market metrics.

| Topic group | Silver handoff | Special path |
| --- | --- | --- |
| ZHVI | modeled into `silver.zillow_zhvi` | county and ZIP are direct; CBSA is derived from county using `silver.xwalk_cbsa_county` plus ACS housing weights |
| ZORI | modeled into `silver.zillow_zori` | county and ZIP are direct; CBSA is derived from county using `silver.xwalk_cbsa_county` plus ACS housing weights |

## 6. Transformation Notes

| Topic group | Current modeled role | Derivation logic |
| --- | --- | --- |
| ZHVI | staging-first monthly home-value series | monthly wide source columns are pivoted to one row per geography-date, with county GEOIDs derived from state and municipal FIPS where available |
| ZORI | staging-first monthly rent-index series | monthly wide source columns are pivoted to one row per geography-date, with county GEOIDs derived where available and monthly date parts split into `date`, `year`, and `month` |

Additional Zillow-wide transform notes:
- State tables are only present for ZHVI in current coverage.
- Silver keeps only the last 10 calendar years and drops null-value rows to keep the modeled surface compact.
- Gold annualizes the monthly Silver series using both yearly averages and December point-in-time values.

## 7. Data Quality Expectations

| Topic group | Non-boilerplate checks worth preserving |
| --- | --- |
| ZHVI | verify uniqueness at the geography-plus-date grain for each slice; monitor continuity of monthly periods after pivoting; watch county GEOID construction from state and municipal FIPS fields |
| ZORI | verify uniqueness at the geography-plus-date grain for each slice; monitor continuity of monthly periods and naming drift in city / ZIP geography labels across source refreshes |

## 8. Operational Notes

- Staging entrypoint:
  [../../etl/staging/get_zillow.R](../../etl/staging/get_zillow.R)
- Required local environment wiring:
  `DATA` for cached Zillow CSVs and `DB_PATH` for DuckDB materialization
- Current documentation pattern:
  staging remains family-contract based, and this file documents the provider-level behavior above those family contracts

## 9. Known Gaps

- The source URLs in the ingest script are hard-coded download links and may need refresh when Zillow rotates file endpoints.
- The provider spec does not try to capture every Zillow metadata field because the current modeled contract focuses on analytical series rather than the full raw source metadata surface.

---

## 10. Architecture Decisions

**Decision date:** 2026-06-02
**Updated:** 2026-06-03

### Silver contract
Two Silver tables in long format (one row per geo × month), with trimmed history and sparse storage:

- `silver.zillow_zhvi` — monthly median home value by geo_level × geo_id × month
- `silver.zillow_zori` — monthly observed rent index by geo_level × geo_id × month

Current modeled geo levels are `county`, `zcta`, and derived `cbsa`.
Silver keeps only 2016-forward rows and stores only observed monthly values (null months are dropped).

### City and state decision
City and state staging slices were reviewed after Gold implementation and are intentionally **not** included in the current modeled contract.

- **State**: leave out for now even though it is cleaner than city, because the current market mart is intentionally scoped to county / ZCTA / CBSA and we do not yet need a separate state series in downstream products.
- **City**: leave out because Zillow city rows do not carry a stable Census place GEOID, while the existing Foundations `place` level is a real Census place geography with 7-digit IDs. Promoting Zillow city rows directly would risk mixing provider city labels with Census place entities.

### Gold contract
A new `gold_housing_market_wide` table at annual grain, one row per geo_level × geo_id × year. Key columns include yearly average and December reference values for both ZHVI and ZORI, plus YoY change fields for each reference.

**Separation rationale:** `gold_housing_core_wide` covers structural supply and regulatory pricing (BPS permits, HUD FMR). `gold_housing_market_wide` covers observed market pricing — Zillow is the first source here, and FHFA HPI (Track 3) will also land in this table when ingested.
