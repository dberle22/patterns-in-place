# Source Spec: Opportunity Zones + FHFA Underserved Areas

## 1. Overview

- Sources: U.S. Treasury CDFI Fund Opportunity Zones list plus FHFA Low-Income Areas / Designated Disaster Areas file
- Access pattern: public bulk downloads, no API keys
- Scope in Foundations: tract-level policy designation flags that standardize into Silver tract backbones and county / CBSA rollups, then land in `gold.dim_policy_designations`
- Documentation goal: one provider-spec file covering the two Track 5 designation sources because they share the same downstream Gold destination and modeling pattern

---

## 2. Coverage Matrix

| Topic group | Staging family contract | Silver outputs | Gold output |
| --- | --- | --- | --- |
| Opportunity Zones | [../layers/staging/staging__opportunity_zones.md](../layers/staging/staging__opportunity_zones.md) | `silver.opportunity_zones` | `gold.dim_policy_designations` |
| FHFA underserved areas | [../layers/staging/staging__fhfa_underserved.md](../layers/staging/staging__fhfa_underserved.md) | `silver.fhfa_underserved` | `gold.dim_policy_designations` |

---

## 3. Source Contract

### Opportunity Zones

- Provider page: `https://www.cdfifund.gov/opportunity-zones`
- Retrieval interface: ArcGIS REST query against the official CDFI map service layer `Designated Opportunity Zone Tracts`
- Cadence: static designation list, but the service exposes current tract identifiers directly
- Native grain: one row per designated tract
- Foundations decision: use the official service response instead of the older public workbook because the service exposes the current 11-digit tract identifiers expected by the Track 5 handoff, then use `silver.xwalk_tract_county` as the full tract backbone so downstream joins can rely on `TRUE/FALSE` coverage rather than an allowlist-only slice

### FHFA Underserved Areas

- Provider page: `https://www.fhfa.gov/data/underserved-areas`
- Retrieval interface: yearly ZIP archive containing a fixed-width text file plus a data-layout PDF and map
- Cadence: annual
- Native grain: one row per census tract record in the FHFA low-income areas file
- Foundations decision: use only the latest available release for the first pass, normalize to tract booleans, and roll up county / CBSA shares from the tract backbone

---

## 4. Key Fields

### Opportunity Zones layer response

| Column | Description |
| --- | --- |
| `CensusTractFIPS` | 11-digit tract GEOID |
| `StateName` | State name |
| `CountyName` | County name |
| `OZoneDesignated` | Opportunity Zone flag (`Yes`) |
| `NMTCQualified` | NMTC qualification helper flag carried as source context |
| `DataSource` | Source lineage field from the official layer |

### FHFA low-income areas file

| Field | Description |
| --- | --- |
| `STATE` | 2-digit state FIPS |
| `CNTY` | 3-digit county FIPS |
| `TRACT` | 6-digit tract code with two implied decimals |
| `LYA` | Low-income area flag: `1=yes`, `0=no`, `9=missing` |
| `MIN_TRCT` | Minority tract flag: `1=yes`, `0=no`, `9=missing` |
| `DDA` | Disaster-area flag: `1=yes`, `0=no` |

Foundations normalizes FHFA into:
- `tract_geoid`
- `year`
- `is_underserved`
- `is_low_income_area`
- `is_minority_area`
- `is_disaster_area`

`is_underserved` is derived as `TRUE` when any of the three component designations is true.

---

## 5. Modeling Decisions

- Opportunity Zones source choice is final for Track 5: use the official CDFI Fund designation response rather than TIGER or a copied historical workbook.
- Zero-pad all tract identifiers to 11 digits before validation or joins.
- `silver.opportunity_zones` is a full tract-coverage table, not a list of designated tracts only.
- `silver.fhfa_underserved` is a `geo_level + geo_id + year` table for the latest release year only in the first pass.
- County and CBSA rollups use `silver.xwalk_tract_county` plus the repo-standard `get_cbsa_rollup_xwalk()` helper, with the latest tract `silver.age_kpi.pop_total` snapshot supplying the population denominator for OZ population-share overlays.
- Gold destination is `gold.dim_policy_designations`; do not add these flags to `gold.dim_geo`.

---

## 6. Known Edge Cases

- The public CDFI workbook still reflects the older 2018 designation list. Foundations uses the official ArcGIS layer response because it exposes the current tract identifiers expected by the Track 5 handoff.
- FHFA includes Puerto Rico tracts and a small number of special geography cases that are not part of the current `silver.xwalk_tract_county` backbone. Those unmatched tracts should be counted and reported.
- FHFA’s source file can contain split-tract records for special metro / nonmetro handling. Foundations collapses those to one tract-level record per `tract_geoid + year` for the first-pass contract.

---

## 7. Lineage

1. [`../../etl/staging/get_opportunity_zones.R`](../../etl/staging/get_opportunity_zones.R) queries the official CDFI ArcGIS Opportunity Zone layer and normalizes the response into `staging.opportunity_zones`.
2. [`../../etl/staging/get_fhfa_underserved.R`](../../etl/staging/get_fhfa_underserved.R) resolves the latest FHFA yearly ZIP, parses the fixed-width text file, and writes `staging.fhfa_underserved`.
3. [`../../etl/silver/opportunity_zones_silver.R`](../../etl/silver/opportunity_zones_silver.R) expands the OZ allowlist to a full tract backbone, joins the latest tract ACS population snapshot from `silver.age_kpi`, and derives county / CBSA tract-share and population-share rollups.
4. [`../../etl/silver/fhfa_underserved_silver.R`](../../etl/silver/fhfa_underserved_silver.R) standardizes the tract flags and derives county / CBSA rollups for the current release year.
5. [`../../etl/gold/gold_policy_designations.sql`](../../etl/gold/gold_policy_designations.sql) unions the static OZ rows and annual FHFA rows into `gold.dim_policy_designations`.
