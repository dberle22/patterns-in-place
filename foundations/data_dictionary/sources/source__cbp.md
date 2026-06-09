# Source Spec: CBP (County Business Patterns)

## 1. Overview

- Source: U.S. Census Bureau
- Program: County Business Patterns (CBP), including ZIP Code Business Patterns (ZBP)
- Access pattern: public annual ZIP downloads containing delimited text files; API also available; no key required
- Current official annual release as of `June 9, 2026`: `2023`
- Native geography options in scope: U.S., state, CSA, MSA, county, ZIP code totals, ZIP code industry detail
- Scope in Foundations: annual establishment counts, employment, and payroll by industry, with county as the canonical first-pass geography because it aligns cleanly to QCEW and BEA / CAGDP downstream joins
- Documentation goal: lock the first-pass ingest path, confirm the delivered columns, and define a small-footprint Silver strategy that stays consistent with the existing Gold industry families

CBP is not just a "current snapshot" in the sense of a one-off latest-state file. It is an annual historical series. Each annual file is itself a year-end business structure snapshot built around the reference year, with employment measured during the pay period including March 12 and payroll provided for first quarter and full year.

## 2. Coverage Matrix

| Topic group | Staging family contracts | Silver outputs | Gold outputs |
| --- | --- | --- | --- |
| CBP county annual core | `staging__cbp.md` | `silver.cbp` | landed extension in `gold.economics_industry_wide` |
| CBP ZIP totals | supporting helper file if needed alongside ZIP detail | optional helper or QA-only use | none in first pass |
| CBP ZIP industry detail | latest-year-only `staging.cbp_zip_detail` | planned separate `silver.cbp_zip` latest-year surface | possible later ZIP / ZCTA business-presence outputs |

The Census release page also publishes U.S., state, CSA, and MSA files. For Foundations, those are useful as QA references, but they do not need to be first-pass staged if Silver is going to derive `cbsa` and `state` from county rows for consistency with QCEW.

## 3. Source Contract

- Provider: U.S. Census Bureau
- Program landing page: `https://www.census.gov/programs-surveys/cbp.html`
- Current annual dataset page used for this spec: `https://www.census.gov/data/datasets/2023/econ/cbp/2023-cbp.html`
- CBP datasets index: `https://www.census.gov/programs-surveys/cbp/data/datasets.html`
- Technical record layouts index: `https://www.census.gov/programs-surveys/cbp/technical-documentation/record-layouts.html`
- API overview: `https://api.census.gov/data/2023/cbp.html`
- Authentication: none

**Verified current 2023 download URLs**

| Geography / file | URL |
| --- | --- |
| U.S. | `https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23us.zip` |
| State | `https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23st.zip` |
| CSA | `https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23csa.zip` |
| MSA | `https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23msa.zip` |
| County | `https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip` |
| ZIP totals | `https://www2.census.gov/programs-surveys/cbp/datasets/2023/zbp23totals.zip` |
| ZIP industry detail | `https://www2.census.gov/programs-surveys/cbp/datasets/2023/zbp23detail.zip` |

**What we verified**

- Census currently labels `2023` as the latest CBP annual release and says `2024` data will be released in summer `2026`.
- The dataset page lists all geography slices above and describes them as downloadable CSV-format datasets.
- The downloaded county archive currently contains a single file named `cbp23co.txt`, but the file itself is comma-delimited with a quoted header row. In practice, this should be treated as a CSV-like text file, not as fixed-width text.
- The ZIP industry detail file is materially larger than the rest of the release at `284.3 MB`, which is a strong reason not to make it the default first-pass ingest.
- The live `2023` geometry slices are not identical:
  - county: `1,100,961` rows and `23` columns
  - MSA: `576,818` rows and `22` columns
  - state: `348,204` rows and `73` columns because it adds `lfo` plus size-band employment and payroll matrices
  - ZIP totals: `34,954` rows and `12` columns
  - ZIP detail: `2,974,116` rows and `16` columns
- The county file is the cleanest canonical base because it keeps the core annual business metrics plus establishment size buckets without adding the state-only `lfo` branch or forcing ZIP detail scale on day one.

**Historical availability**

- CBP downloadable dataset files exist from `1986` to current for U.S., state, and county.
- ZIP Code Business Patterns downloadable files start in `1994`.
- CSA files start in `2017`.
- Census notes that data prior to `1986` are available through the National Archives, but that is outside the first-pass Foundations ingest scope.
- Historical shape is not uniform across the full archive:
  - `1998` county uses `naics`
  - `1997` and earlier county uses `sic`
  - newer county releases such as `2022` and `2023` share the current 23-column county shape closely enough for one first-pass contract

**Historical boundary recommendation**

If we backfill historical county CBP for the first managed annual series, the approved first-pass floor is `2010` rather than the full `1998` NAICS-era span. That keeps the history useful for current Gold time series without widening the initial ingestion burden more than necessary.

**Recommended ingestion path**

1. Use the county bulk ZIP as the canonical raw source for first-pass staging.
2. Treat published state / MSA / CSA files as QA references rather than parallel source-of-truth feeds.
3. Defer ZIP work until the county ingest, Silver, and Gold path is stable, then add the latest-year ZIP industry detail file as the first ZIP expansion.
4. Prefer the bulk ZIP over the API for staging because the ZIP is a stable annual artifact and keeps row-level ingestion simple.
5. Keep the full county file payload in staging rather than prematurely dropping columns.

Why county first:
- it reduces the number of geography families we have to ingest and validate in the first pass
- it gives us one canonical fine-grain business base that aligns with QCEW and BEA / CAGDP
- it makes county -> CBSA and county -> state rollups fully governed inside our own pipeline
- it keeps the first-pass Gold logic smaller and easier to QA before we add ZIP
- it avoids the extra state-only `lfo` dimension and extra size-band employment/payroll payload, which would create a second raw-shape branch immediately

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- planned `../../etl/staging/get_cbp.R`

## 4. Staging Shape

Preferred first-pass staging output:
- `staging.cbp_county`
- one row per `county_fips + year + naics`
- keep the full published county file for the county geography, including size-class columns
- preserve source noise flags instead of trying to "fix" them in staging
- do not land separate first-pass staging tables for state, MSA, CSA, or ZIP

**Observed county file header from the live 2023 archive**

| Source column |
| --- |
| `fipstate` |
| `fipscty` |
| `naics` |
| `emp_nf` |
| `emp` |
| `qp1_nf` |
| `qp1` |
| `ap_nf` |
| `ap` |
| `est` |
| `n<5` |
| `n5_9` |
| `n10_19` |
| `n20_49` |
| `n50_99` |
| `n100_249` |
| `n250_499` |
| `n500_999` |
| `n1000` |
| `n1000_1` |
| `n1000_2` |
| `n1000_3` |
| `n1000_4` |

**Recommended normalized staging contract**

| Column | Type | Description |
| --- | --- | --- |
| `year` | INTEGER | CBP reference year |
| `state_fips` | VARCHAR | Two-digit state FIPS from `fipstate` |
| `county_fips` | VARCHAR | Five-digit county FIPS built from `fipstate || fipscty` |
| `naics_code` | VARCHAR | Published NAICS code such as `------`, `11----`, `44-45`, `5413--` |
| `emp_noise_flag` | VARCHAR | Published employment noise flag |
| `employment_march12` | DOUBLE | Mid-March employment |
| `qp1_noise_flag` | VARCHAR | Published first-quarter payroll noise flag |
| `first_quarter_payroll_k` | DOUBLE | First-quarter payroll in thousands of dollars |
| `ap_noise_flag` | VARCHAR | Published annual payroll noise flag |
| `annual_payroll_k` | DOUBLE | Annual payroll in thousands of dollars |
| `establishments` | DOUBLE | Total establishments |
| `est_n_lt_5` | DOUBLE | Establishments with fewer than 5 employees |
| `est_n_5_9` | DOUBLE | Establishments with 5-9 employees |
| `est_n_10_19` | DOUBLE | Establishments with 10-19 employees |
| `est_n_20_49` | DOUBLE | Establishments with 20-49 employees |
| `est_n_50_99` | DOUBLE | Establishments with 50-99 employees |
| `est_n_100_249` | DOUBLE | Establishments with 100-249 employees |
| `est_n_250_499` | DOUBLE | Establishments with 250-499 employees |
| `est_n_500_999` | DOUBLE | Establishments with 500-999 employees |
| `est_n_1000_plus` | DOUBLE | Establishments with 1,000 or more employees |
| `est_n_1000_1499` | DOUBLE | Establishments with 1,000-1,499 employees |
| `est_n_1500_2499` | DOUBLE | Establishments with 1,500-2,499 employees |
| `est_n_2500_4999` | DOUBLE | Establishments with 2,500-4,999 employees |
| `est_n_5000_plus` | DOUBLE | Establishments with 5,000 or more employees |
| `source_file` | VARCHAR | Raw file identifier such as `cbp23co.txt` |

**ZIP products and first-pass ZIP boundary**

`zbp23totals.zip` delivers ZIP-level totals with `zip`, `name`, `emp_nf`, `emp`, `qp1_nf`, `qp1`, `ap_nf`, `ap`, `est`, `city`, `stabbr`, and `cty_name`.

`zbp23detail.zip` delivers ZIP-by-NAICS detail with `zip`, `name`, `naics`, `est`, size-class establishment counts, `city`, `stabbr`, and `cty_name`.

Those two files are useful, but they should not widen the first-pass county historical staging scope.

Approved ZIP boundary after county stabilization:
- land `zbp<yy>detail.zip` for the most recent release year only because that is the file with meaningful ZIP-by-industry business counts
- keep that ZIP staging surface separate from `staging.cbp_county`
- build a separate latest-year `silver.cbp_zip` table for ZIP-by-industry business-presence analysis
- optionally land `zbp<yy>totals.zip` alongside it only as a helper or QA surface if we find it useful later

**Staging boundary decision**

For Track 12 first pass, the recommended staging boundary is:
- yes: all columns from the county file for the approved `2010+` history
- no: separate state, MSA, CSA, or ZIP historical staging tables yet
- latest-year follow-on: ZIP industry detail only, in a separate ZIP staging surface

This is the best balance between source fidelity and pipeline control:
- we keep all county business metrics and size buckets available for later modeling
- we avoid duplicating rollup geographies that Silver should derive
- we avoid introducing the state-only `lfo` branch before it has a product use case
- we avoid landing nearly 3 million ZIP-detail rows before the county path is proven

## 5. Staging To Silver

Preferred first-pass Silver output:
- `silver.cbp`
- one row per `geo_level + geo_id + year + industry_code`
- county is the only staged base grain
- `cbsa` and `state` should be derived from counties using the same crosswalk strategy already used in QCEW

Handoff pattern:
1. Read `staging.cbp_county`.
2. Keep the county rows source-faithful in staging.
3. Curate the analytical industry subset in Silver.
4. Roll county rows to `cbsa` and `state`.
5. Join or reuse the same broad industry family mapping already used by `gold.economics_industry_wide`.

The first-pass Silver should not depend on published CBP MSA or state files if the goal is cross-source consistency with county-derived QCEW and BEA joins.

## 5A. Silver To Gold

Current first-pass Gold output:
- `gold.economics_industry_wide`

Current Gold use of CBP:
1. Read `silver.cbp`.
2. Keep the all-sectors row as the source of total establishments, March employment, and payroll context.
3. Roll the aligned broad families into establishment counts by industry family.
4. Publish establishment shares and overall `cbp_estabs_per_1000_residents` alongside the existing ACS, QCEW, and BEA industry structure metrics.

This keeps CBP focused on the business-structure story it adds most cleanly to Gold rather than duplicating the fuller employment-and-wage role already served by QCEW.

## 6. Transformation Notes

### Industry strategy

CBP publishes a much larger NAICS universe than the broad industry families we expose downstream. The cleanest approach is:

1. Keep all county NAICS rows in staging.
2. In Silver, keep the all-sectors total row `------`.
3. Select the canonical broad NAICS sector rows that align to the existing Gold/QCEW families:
   - `11` + `21` -> `ag_mining`
   - `22` + `48-49` -> `transport_util`
   - `23` -> `construction`
   - `31-33` -> `manufacturing`
   - `42` -> `wholesale`
   - `44-45` -> `retail`
   - `51` -> `information`
   - `52` + `53` -> `finance_real`
   - `54` + `55` + `56` -> `professional`
   - `61` + `62` -> `educ_health`
   - `71` + `72` -> `arts_accomm_food`
   - `81` -> `other_services`
   - `92` -> `public_admin`, if present and analytically usable in CBP
4. Avoid deeper 3- to 6-digit detail in the first-pass Silver table unless a later product explicitly needs it.

This keeps CBP aligned with the same broad-family surface described in [../layers/gold/gold__economics_industry_wide.md](../layers/gold/gold__economics_industry_wide.md) rather than introducing a second industry vocabulary.

### Metric strategy

Recommended first-pass Silver measures:
- `establishments`
- `employment_march12`
- `annual_payroll_k`
- `first_quarter_payroll_k`
- optional derived `avg_annual_payroll_per_employee` only if we are comfortable with suppressed / noised numerators and denominators

### Snapshot interpretation

CBP should be documented as an annual structural business dataset:
- employment is a point-in-time March snapshot
- payroll is quarterly and annual flow data
- establishments are annual stock counts

That distinction matters when comparing CBP with QCEW annual-average employment.

## 7. Data Quality Expectations

| Check | What to verify |
| --- | --- |
| County key completeness | `state_fips` and `county_fips` are always zero-padded text |
| Row uniqueness | uniqueness at `county_fips + year + naics_code` |
| NAICS universe | the staged county NAICS-code inventory matches the published annual county file |
| Noise flag preservation | `emp_nf`, `qp1_nf`, and `ap_nf` are retained exactly as published |
| Total-row presence | county rows include the all-sectors `------` record |
| Rollup consistency | county-derived state / CBSA totals reconcile reasonably against published CBP state / MSA slices |
| Geography anomalies | document handling for county-equivalent units, including Connecticut planning regions when present in the source vintage |

## 8. Operational Notes

- Latest official annual CBP release verified for this spec: `2023`.
- The annual county file is large enough to matter, but still manageable at roughly `12.7 MB` zipped and about `108 MB` uncompressed in the current release.
- The ZIP industry detail file is the real growth risk and should stay out of the first county-first pass.
- ZIP totals alone are too thin for our intended ZIP use case because they do not carry the industry detail we actually want downstream.
- The API is useful for QA and spot checks, but the annual bulk ZIP is the better governed ETL input.
- After the first stable county pipeline is in place, the next recommended expansion is:
  1. add ZIP industry detail for the most recent release year only
  2. keep ZIP in its own staging and Silver path rather than mixing it into county history
  3. decide whether the ZIP analytical contract should stay ZIP-native or be treated as a ZCTA proxy
  4. use ZIP totals only if we need a small helper or QA file alongside ZIP detail
- After the first stable current-year county pipeline is in place, we should backfill historical county CBP for the approved first-pass annual range beginning in `2010`.

## 9. Known Gaps

- We have not yet decided whether ZIP outputs should remain ZIP-native or be translated into a ZCTA-style contract later.
- CBP employment is March-point-in-time employment, not annual-average employment, so downstream docs should avoid describing it as interchangeable with QCEW employment.
- We still need to verify how consistently `92 Public administration` appears in the county files before promising a Gold-level public-administration CBP metric.
- SIC-era county files (`1997` and earlier) are a separate historical decision and should not be mixed silently into the first NAICS-based CBP path.

## 10. Source References

- https://www.census.gov/data/datasets/2023/econ/cbp/2023-cbp.html
- https://www.census.gov/programs-surveys/cbp/data/datasets.html
- https://www.census.gov/programs-surveys/cbp/technical-documentation/record-layouts.html
- https://www.census.gov/topics/employment/cbp-redirect.html
- https://api.census.gov/data/2023/cbp.html
