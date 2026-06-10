# Source Spec: IRS EO Business Master File

## 1. Overview

- Source: Internal Revenue Service Exempt Organizations Business Master File Extract (`EO BMF`)
- Provider family: Internal Revenue Service
- Access pattern in current first-pass scope: public monthly CSV snapshots, published as one file per state plus DC, Puerto Rico, international, and four regional rollups
- Current verified posting on the IRS landing page as of `June 9, 2026`: updated `May 12, 2026`, national record count `1,966,267`
- Native geography in current first-pass files: organization mailing / filing address, not county-native
- Scope in Foundations: latest-snapshot nonprofit organization counts allocated from ZIP5 to county, then rolled from county to CBSA as a proxy for organized civic life
- Documentation goal: define the real file shape, decide the county-allocation method, and document the first-pass exclusion logic for a `nonprofits_per_100k` metric

The key practical finding is that EO BMF is operationally simple but geographically indirect. The IRS gives us one row per exempt organization with a filing address and ZIP code, not a county code. That means the first-pass ingest should stay narrow: latest snapshot only, ingest the four regional files rather than all state files, allocate organizations from ZIP5 to county using the existing HUD ZIP-county crosswalk, and publish a small county / CBSA metric family rather than overmodeling the source.

---

## 2. Coverage Matrix

| Release slice | Native grain | Recommended staging contract | Recommended Silver path | Status |
| --- | --- | --- | --- | --- |
| Regional EO BMF CSVs | one row per organization EIN in the region's current filing-address file | `staging.irs_bmf` | `silver.irs_bmf` | In scope |
| State EO BMF CSVs | same content packaged as state slices | fallback / debug option only | None in first pass | Out of scope |
| Puerto Rico EO BMF CSV | one row per organization EIN in PR | Later option if we expand geography policy | None in first pass | Out of scope |
| International EO BMF CSV | one row per non-domestic organization EIN | None | None | Out of scope |

First-pass coverage should use the regional files rather than the state files because:
- the data content is the same provider-managed monthly extract, just packaged in four larger slices
- four raw ingests are operationally simpler than 50 states plus DC
- the platform only needs one national organization table before ZIP-to-county allocation, not a state-by-state raw audit surface
- any later state-level debugging can still fall back to the state files without changing the modeled contract

---

## 3. Source Contract

- Provider: Internal Revenue Service
- Landing page:
  `https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf`
- Code sheet / information sheet:
  `https://www.irs.gov/pub/foia/ig/tege/eo-info.pdf`
- Preferred first-pass file pattern:
  `https://www.irs.gov/pub/irs-soi/eo<region>.csv`
- State-file fallback pattern:
  `https://www.irs.gov/pub/irs-soi/eo_<state>.csv`
- Verified state-file example:
  `https://www.irs.gov/pub/irs-soi/eo_al.csv`
- Authentication: none

**What we verified**

- The IRS page says the EO BMF is extracted monthly and is a cumulative file containing the most recent information the IRS has for each organization.
- The IRS publishes one CSV for each state, the District of Columbia, Puerto Rico, and international organizations, plus four regional CSV rollups.
- State and region are based on the filing address and generally represent the location of the organization's headquarters, but may not represent the places where the organization actually operates.
- The live CSV header matches the IRS code sheet and includes address, classification, status, filing, financial, and NTEE fields.
- The region files are described on the IRS page as area bundles of the same state families, which makes them an acceptable lighter-weight raw ingest surface for a national rollup use case.

**Observed live CSV header**

The verified Alabama file currently begins with:

`EIN, NAME, ICO, STREET, CITY, STATE, ZIP, GROUP, SUBSECTION, AFFILIATION, CLASSIFICATION, RULING, DEDUCTIBILITY, FOUNDATION, ACTIVITY, ORGANIZATION, STATUS, TAX_PERIOD, ASSET_CD, INCOME_CD, FILING_REQ_CD, PF_FILING_REQ_CD, ACCT_PD, ASSET_AMT, INCOME_AMT, REVENUE_AMT, NTEE_CD, SORT_NAME`

Sample ZIP format from the live file:
- `35824-1490`
- `36532-2923`

So the staging ingest should preserve the raw ZIP string and derive `zip5` from the first five digits.

**Recommended ingestion path**

1. Read the IRS landing page and extract the four regional file URLs.
2. Download `eo1.csv`, `eo2.csv`, `eo3.csv`, and `eo4.csv`.
3. Exclude the separate Puerto Rico and international files from the first pass to stay aligned with the current Foundations geography backbone.
4. Row-bind the four region files into one national staging table.
5. Filter that combined table back to the supported U.S. state + DC scope because `eo4.csv` can carry non-state rows.
6. Preserve the published columns with light normalization only.
7. Derive `zip5` from the raw ZIP field for downstream county allocation.

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- planned `../../etl/staging/get_irs_bmf.R`
- existing ZIP crosswalk builder:
  [../../etl/silver/geo_crosswalks_silver.R](../../etl/silver/geo_crosswalks_silver.R)

---

## 4. Staging Shape

Preferred first-pass staging output:
- `staging.irs_bmf`
- one row per organization EIN in the current monthly snapshot
- latest snapshot only; no historical panel in the first pass

Recommended normalized staging keep set:

| Column | Type | Description |
| --- | --- | --- |
| `ein` | VARCHAR | Employer Identification Number |
| `name` | VARCHAR | Primary organization name |
| `ico` | VARCHAR | In-care-of name |
| `street` | VARCHAR | Street address |
| `city` | VARCHAR | Filing-address city |
| `state` | VARCHAR | Filing-address state / jurisdiction code |
| `zip_raw` | VARCHAR | Source ZIP field as published, often ZIP+4 |
| `zip5` | VARCHAR | First five digits derived from `zip_raw` |
| `group_exemption_number` | VARCHAR | Source `GROUP` field |
| `subsection_code` | VARCHAR | IRS subsection code |
| `affiliation_code` | VARCHAR | IRS affiliation code |
| `classification_codes` | VARCHAR | IRS classification codes |
| `ruling_yyyymm` | VARCHAR | IRS ruling / determination letter date |
| `deductibility_code` | VARCHAR | Contribution deductibility code |
| `foundation_code` | VARCHAR | Foundation code |
| `activity_codes` | VARCHAR | IRS activity codes |
| `organization_code` | VARCHAR | Type-of-organization code |
| `status_code` | VARCHAR | Exempt organization status code |
| `tax_period_yyyymm` | VARCHAR | Latest return tax period |
| `asset_code` | VARCHAR | Asset code bucket |
| `income_code` | VARCHAR | Income code bucket |
| `filing_requirement_code` | VARCHAR | Primary filing requirement code |
| `pf_filing_requirement_code` | VARCHAR | Private-foundation filing code |
| `accounting_period_mm` | VARCHAR | Fiscal-year ending month |
| `asset_amt` | DOUBLE | Latest reported asset amount |
| `income_amt` | DOUBLE | Latest reported income amount |
| `revenue_amt` | DOUBLE | Latest reported revenue amount |
| `ntee_cd` | VARCHAR | NTEE code |
| `sort_name` | VARCHAR | Secondary name / sort line |
| `snapshot_date` | DATE or VARCHAR | IRS landing-page posting date for the monthly extract |
| `source_file` | VARCHAR | Region source file name such as `eo1.csv` |

Why keep staging source-faithful:
- the file is already row-level and narrow enough that a wide keep set is manageable
- several IRS classification fields may be useful later for alternate nonprofit subsets
- the real modeling complexity lives in ZIP allocation and exclusion logic, not raw parsing

---

## 5. Staging To Silver

Recommended first-pass Silver output:
- `silver.irs_bmf`
- county rows allocated from organization ZIP5s
- derived CBSA rows rolled up from county rows
- latest snapshot only

Recommended handoff pattern:
1. Read `staging.irs_bmf`.
2. Restrict to active U.S. organizations in the latest snapshot.
3. Derive `zip5` from `zip_raw`.
4. Aggregate organizations to one row per `zip5`.
5. Join `zip5` to `silver.xwalk_zcta_county`.
6. Allocate ZIP-level organization counts fractionally across counties using the ZIP-county relationship weight.
7. Sum the fractional counts to county.
8. Roll county counts to CBSA with `silver.xwalk_cbsa_county`.
9. Join ACS population to publish per-capita rates.

### County allocation decision

Use `silver.xwalk_zcta_county.rel_weight_bus` as the default county-allocation weight.

Reasoning:
- EO BMF reflects filing / mailing addresses for organizations, not residential population
- the existing HUD crosswalk already carries a business-oriented ratio field
- `rel_weight_bus` is a better fit than residential weighting for organization headquarters density

Implementation fallback:
- if a ZIP has no positive `rel_weight_bus` total in the HUD crosswalk, fall back to `rel_weight_hu`
- if both business and housing totals are missing, fall back to `rel_weight_pop`

This keeps the preferred business weighting where available without discarding ZIPs that lack business-ratio coverage in the crosswalk.

### First-pass active-organization rule

Keep rows whose IRS `status_code` indicates an active exempt organization record in the live BMF snapshot.

For the first pass, the active keep set should be:
- `01` unconditional exemption
- `02` conditional exemption
- `12` trust described in section 4947(a)(2)
- `25` organization terminating private-foundation status under section 507(b)(1)(B)

This mirrors the status codes documented in the IRS information sheet and avoids inventing a narrower unsupported filter.

### Non-religious nonprofit decision

The metric map asks for a civic-life proxy rather than a census of all exempt entities. For the first pass, use a conservative exclusion rule rather than a complex NTEE include list.

Recommended exclusion logic for `nonprofit_org_count_nonreligious_est`:
- exclude NTEE major group `X*` (`Religion-Related`) when `ntee_cd` is present
- exclude IRS filing-requirement codes that explicitly indicate church / religious non-filer treatment:
  - `06` not required to file (`church`)
  - `13` not required to file (`religious organization`)

This should be documented as an approximation, not a perfect classifier, because:
- some rows have blank `ntee_cd`
- some faith-based nonprofits may appear outside `X*`
- some religiously affiliated service organizations may remain in-scope by design if they are not coded as religious organizations in the IRS file

### Recommended Silver fields

| Silver column | Why keep it |
| --- | --- |
| `geo_level` | `county` or `cbsa` |
| `geo_id` | county FIPS or CBSA code |
| `geo_name` | display geography name |
| `snapshot_date` | identifies the IRS monthly extract used |
| `nonprofit_org_count_est` | estimated total active exempt-organization count after ZIP allocation |
| `nonprofit_org_count_nonreligious_est` | estimated active non-religious count after the first-pass exclusion rule |
| `nonprofits_per_100k` | non-religious count per 100,000 residents |
| `nonprofits_total_per_100k` | optional all-org companion rate for QA / editorial comparison |
| `organization_weight_method` | fixed metadata value such as `zip5_bus_ratio` |

Optional later Silver extensions if we decide they add value:
- `charitable_org_count_est` for a narrower public-charity slice
- broad NTEE-family counts such as arts, education, health, human services, environment, civic / advocacy

---

## 6. Transformation Notes

### Simple architecture recommendation

The simplest correct first-pass architecture is:

1. Read the four region CSVs for one posting date.
2. Preserve the active U.S. source rows in one national staging table.
3. Derive `zip5` from the filing-address ZIP.
4. Aggregate organizations to ZIP5 first.
5. Allocate ZIP5 rows to county using `silver.xwalk_zcta_county.rel_weight_bus`, with the documented HUD fallback hierarchy where business weights are unavailable.
6. Aggregate to county and county-derived CBSA rows.
7. Join ACS population to publish per-capita civic-infrastructure density metrics.

That is enough to support the current metric-map goal without turning Track 21.2 into a multi-table sector taxonomy project.

### Interpretation note

This source measures organization mailing / headquarters density, not direct service coverage. It should therefore be described as:
- a proxy for organized civic life and institutional density
- strongest for county / metro headquarters ecosystems
- weaker for organizations that serve one geography but file from another

### Gold placement recommendation

This source belongs with the static / slow-moving civic baseline family rather than in `gold.health_wide`.

Recommended Gold destination:
- `gold.social_fabric_wide`

Reasoning:
- the metric map places it under `Character -> Social Fabric & civic identity`
- it conceptually complements Opportunity Insights Social Capital better than any health or labor mart
- it is effectively a snapshot baseline, not a fast-moving recurring panel

### Why not use the state files as the primary surface

Do not use the state files as the primary ingest surface in the first pass because:
- they add 51 raw ingests where four region files contain the same monthly content in a simpler package
- the modeled output does not need state-sliced provenance before ZIP-to-county allocation
- malformed-file risk is better framed here as a small number of provider-standardized files rather than a long list of near-identical ones

State files should remain a documented fallback when:
- a region file fails validation
- we need to isolate one state during debugging
- the IRS changes regional packaging but leaves state files intact

---

## 7. Data Quality Expectations

| Check | What to verify |
| --- | --- |
| ZIP parsing | `zip5` is correctly extracted from raw ZIP and preserves leading zeros |
| Row uniqueness | staging uniqueness at `ein + source_file + snapshot_date` |
| Crosswalk coverage | fraction of rows whose `zip5` resolves in `silver.xwalk_zcta_county` |
| Weight reconciliation | county allocations for each EIN sum to `1.0` within expected rounding tolerance |
| Geography policy | Puerto Rico and international files are excluded intentionally in the first pass |
| Active-status filter | retained rows use only the documented active status-code keep set |
| Exclusion logic QA | compare all-org vs non-religious counts to make sure the exclusion rule behaves plausibly by county / CBSA |

Specific QA note:
- because the crosswalk uses ZIP relationships rather than exact street geocoding, the output is modeled county density, not an address-verified count

---

## 8. Operational Notes

- Prefer the four region CSVs over any scraping or search-tool path.
- The EO BMF page is updated monthly, but the first-pass Foundations implementation should ingest only the latest available snapshot rather than trying to backfill a monthly panel.
- The landing page reports the posting date and national record count; staging should capture the posting date as snapshot metadata.
- The existing ZIP-county and ZIP-CBSA crosswalk assets already live in the repo and are built from HUD relationship files in [../../etl/silver/geo_crosswalks_silver.R](../../etl/silver/geo_crosswalks_silver.R).
- `BUS_RATIO` is the preferred allocation weight for this source family.
- State CSVs remain a documented fallback / debug surface, not the canonical first-pass ingest.

---

## 9. Known Gaps

- Filing-address geography is not the same as operating geography.
- The first-pass exclusion rule for religious organizations is intentionally conservative and imperfect.
- The latest-snapshot design means the first version will not answer time-trend questions such as nonprofit growth since 2015.
- Puerto Rico and international organizations are excluded from the first pass to stay aligned with the current Foundations geography backbone.
- Some organizations have blank `ntee_cd`, which limits any purely taxonomy-based filtering strategy.

---

## 10. Source References

- IRS EO BMF landing page:
  `https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf`
- IRS EO BMF information sheet:
  `https://www.irs.gov/pub/foia/ig/tege/eo-info.pdf`
- Verified live example state file:
  `https://www.irs.gov/pub/irs-soi/eo_al.csv`
