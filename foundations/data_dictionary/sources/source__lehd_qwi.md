# Source Spec: LEHD QWI

## 1. Overview

- Source: U.S. Census Bureau
- Program: Longitudinal Employer-Household Dynamics (LEHD) Quarterly Workforce Indicators (QWI)
- Access pattern in current first-pass scope: public state-based `csv.gz` release files plus `version_qwi.txt` metadata; no API key required
- Current verified schema release as of `June 20, 2026`: `V4.14.0`, last modified `January 20, 2026`
- Current verified public release vintage example: Delaware `R2026Q2`, with `QWI_F` through `2025:3`
- Native geographies in the public files: national, state, county, metro-state part, and workforce investment area
- Scope in Foundations: county-only quarterly workforce composition by worker age and education, paired with industry, then rolled to canonical CBSA / state / division / national outputs downstream
- Documentation goal: define the real file shape, current history window, and a manageable first-pass ingest scope before writing staging code

QWI is the LEHD product that most directly fills the current labor-market composition gap in Foundations. Unlike LAUS or QCEW, it carries employment, hires, separations, earnings, and payroll alongside worker characteristics and firm characteristics in the same quarterly row contract.

This is a topic-level child spec for the LEHD family. LODES and J2J should get their own child specs because their file shapes and downstream modeling rules are materially different.

---

## 2. Coverage Matrix

| Topic group | Staging family contracts | Silver outputs | Gold outputs |
| --- | --- | --- | --- |
| LEHD QWI age x industry and education x industry | planned `staging__lehd_qwi.md` | planned `silver.lehd_qwi` | planned `gold.economics_labor_wide` |

---

## 3. Source Contract

- Provider: U.S. Census Bureau
- LEHD data landing page: `https://lehd.ces.census.gov/data/`
- QWI landing page: `https://lehd.ces.census.gov/data/#qwi`
- Current QWI release index: `https://lehd.ces.census.gov/data/qwi/latest_release/`
- Current schema bundle: `https://lehd.ces.census.gov/data/schema/latest/`
- Current public-use schema: `https://lehd.ces.census.gov/data/schema/latest/lehd_public_use_schema.html`
- Current naming specification: `https://lehd.ces.census.gov/data/schema/latest/lehd_csv_naming.html`
- Query tool: `https://ledextract.ces.census.gov/`
- Authentication: none

**What we verified**

- The live `latest_release` index currently publishes directories for all `50` states plus `DC`, `PR`, and `US`.
- The current schema bundle is `V4.14.0`, last modified on `January 20, 2026`.
- The current Delaware metadata file reports `QWI_F DE 10 1998:3-2025:3 V4.14.0 R2026Q2`.
- Public QWI files follow the documented naming convention `qwi_[geohi]_[demo]_[fas]_[geocat]_[indcat]_[owncat]_[sa].csv.gz`.
- Live state files are directly downloadable and do not require the LED Extraction Tool to materialize a first-pass staging table.

**Implementation note from local validation**

The current Track 23 plan text assumes a `lehdr::get_qwi()` helper. On local validation on `June 20, 2026`, the installed `lehdr` package did not expose `get_qwi`, and the current public `jamgreen/lehdr` README appears focused on LODES retrieval rather than QWI. That means the first-pass staging implementation should treat direct QWI file ingestion as the reliable baseline unless we later pin a package version that explicitly supports QWI.

---

## 4. Native File Shape

The public QWI files are already normalized row tables, not nested JSON or wide yearly spreadsheets.

**Observed file naming pieces**

| Segment | Example | Meaning |
| --- | --- | --- |
| `demo` | `sa`, `se`, `rh` | sex x age, sex x education, race x ethnicity |
| `fas` | `f`, `fa`, `fs` | no firm age/size detail, by firm age, by firm size |
| `geocat` | `gc`, `gm`, `gs` | county, metro-state part, state |
| `indcat` | `n`, `ns`, `n3`, `n4` | all industries, NAICS sectors, subsectors, industry groups |
| `owncat` | `op`, `oslp`, `of` | all private, state/local/private, federal |
| `sa` | `u`, `s` | unadjusted, seasonally adjusted |

**Observed row shape**

Each row is keyed by:

- `periodicity`
- `seasonadj`
- `geo_level`
- `geography`
- `ind_level`
- `industry`
- `ownercode`
- `sex`
- `agegrp`
- `race`
- `ethnicity`
- `education`
- `firmage`
- `firmsize`
- `year`
- `quarter`
- `agg_level`

Each row then carries a wide payload of measures including:

- employment stocks: `Emp`, `EmpEnd`, `EmpS`, `EmpTotal`, `EmpSpv`
- flows: `HirA`, `HirN`, `HirR`, `Sep`, `HirAEnd`, `SepBeg`, `HirAEndRepl`
- rates already present on the live `qwi` files: `HirAEndR`, `SepBegR`, `HirAEndReplR`, `TurnOvrS`
- earnings and payroll: `EarnS`, `EarnBeg`, `EarnHirAS`, `EarnHirNS`, `EarnSepS`, `Payroll`
- status fields for each major measure: `sEmp`, `sHirA`, `sEarnS`, `sPayroll`, etc.

This means the first-pass Foundations ingest does not need to start from a second derived rate table to get the core hire-rate and separation-rate fields. The live `qwi` files already include them.

**Status / suppression codes**

The LEHD `label_flags.csv` file defines the current status values, including:

- `1`: OK
- `5`: suppressed because the value does not meet Census publication standards
- `6`: calculated from other released measures, no significant distortion
- `9`: significantly distorted, fuzzed value released
- `10`: aggregate of cells, no significant distortion
- `-1`: data not available to compute the estimate
- `-2`: no data available in that category for that quarter

Staging should preserve these codes directly rather than coercing them into nulls too early.

---

## 5. Historical Coverage

**Verified metadata**

- Delaware `version_qwi.txt` currently reports:
  - `QWI_F`: `1998:3-2025:3`
  - `QWI_FA`: `1998:3-2025:2`
  - `QWI_FS`: `1998:3-2025:2`

**Verified file observations**

- A live Delaware county-sector `sa` file begins at `1998 Q3`.
- A live Delaware county-sector `se` file also begins at `1998 Q3`.
- A live Delaware county-sector `rh` file also begins at `1998 Q3`.

That means the older planning assumption that education and race/ethnicity only begin in `2009` was not confirmed by the current live Delaware files. We should not carry the `2009` boundary forward as a hard rule unless staging reveals a broader state-specific limitation that is not visible in the current release samples.

**Important indicator-history caveat**

The schema explicitly notes that only `EmpTotal` and `Payroll` are guaranteed for the full metadata span because many other QWI indicators require prior or subsequent quarters to compute. For example:

- `Emp` requires `1` prior quarter
- `EmpEnd` requires `1` subsequent quarter
- `EmpS` requires `1` prior and `1` subsequent quarter
- `HirNS` requires `5` prior quarters and `1` subsequent quarter

This means annual summaries should be built with awareness that some quarter-edge values will be structurally unavailable even when the file itself exists.

---

## 6. Recommended First-Pass Scope

The simplest high-value first pass is narrower than the full QWI surface:

1. Pull worker-demographic file families `sa` and `se`.
2. Use `fas = f` so we avoid exploding the grain with firm age and firm size on the first pass.
3. Use `indcat = ns` so we start at NAICS sector level rather than subsector / industry-group volume.
4. Use `owncat = op` as the canonical first industry-detail slice.
5. Use `sa = u` for the first pass so we preserve the native unadjusted quarterly values.
6. Land only `gc` county files in staging, then derive complete CBSA, state, division, and national outputs downstream from county geography joins.
7. Keep only all-sex rows (`sex = 0`) so the first pass truly lands `age x industry` and `education x industry` rather than the wider `sex x age` and `sex x education` cubes.
8. Keep only the latest rolling `10` years from each file rather than the full historical panel.

**Why `op` first**

`op` (`A05`, all private) gives the cleanest comparable industry-detail surface and aligns best with the current QCEW Silver pattern, which also treats private-sector industry detail as canonical. `oslp` can be added later for a broader total-ownership view if we decide we need it for Gold headline rows.

**Why derive all higher geographies in Silver**

For Foundations, the safer canonical path is:

- keep staging source-faithful
- derive county rows directly from `gc`
- roll counties to complete CBSA using `silver.xwalk_cbsa_county`
- roll counties to states using `silver.xwalk_county_state`
- roll states to divisions using `silver.xwalk_state_region`
- roll the county/state base to national in Silver
That avoids double counting cross-state metros, avoids mixing overlapping published geography families in staging, and matches the repo's existing county-first rollup pattern.

---

## 7. Expected Row Volume

Observed first-pass file sizes and row counts already show that QWI is large enough to warrant a disciplined scope.

**Observed live examples**

| State / file | Observed rows |
| --- | ---: |
| Delaware `qwi_de_sa_f_gc_ns_op_u.csv.gz` | `232,714` |
| Delaware `qwi_de_se_f_gc_ns_op_u.csv.gz` | `155,143` |
| California `qwi_ca_sa_f_gc_ns_op_u.csv.gz` | `4,336,363` |
| California `qwi_ca_sa_f_gm_ns_op_u.csv.gz` | `2,736,775` |

**Planning implication**

- Small states are already in the low hundreds of thousands of rows per file family.
- Large states reach multiple millions of rows for just one demographic family (`sa`) and one geography family.
- Pulling all demographic, industry, ownership, and firm-characteristic combinations at once would be much larger than the current Track 23 scope needs.
- Filtering to all-sex rows and the latest rolling `10` years cuts the file volume substantially before staging materialization.

For Track `23.1`, this supports keeping the first pass at:

- `sa` + `se`
- `gc` only
- `ns`
- `op`
- unadjusted `u`
- all-sex rows only
- latest rolling `10` years only

---

## 8. Preferred Staging Contract

Preferred first-pass staging table:

- `staging.lehd_qwi`
- one row per retained QWI county observation
- source-faithful dimension columns preserved even when a file family fixes some of them at all-categories values

Recommended staging fields:

| Column | Type | Description |
| --- | --- | --- |
| `periodicity` | VARCHAR | Published periodicity code, expected `Q` |
| `seasonadj` | VARCHAR | `U` or `S` |
| `geo_level` | VARCHAR | Published LEHD geography level |
| `geo_id` | VARCHAR | Published geography code |
| `ind_level` | VARCHAR | Industry aggregation level |
| `industry_code` | VARCHAR | Industry code |
| `ownercode` | VARCHAR | Ownership code |
| `sex` | VARCHAR | Worker sex code |
| `agegrp` | VARCHAR | Worker age code |
| `race` | VARCHAR | Worker race code |
| `ethnicity` | VARCHAR | Worker ethnicity code |
| `education` | VARCHAR | Worker education code |
| `firmage` | VARCHAR | Firm age code |
| `firmsize` | VARCHAR | Firm size code |
| `year` | INTEGER | Source year |
| `quarter` | INTEGER | Source quarter |
| `agg_level` | INTEGER | LEHD aggregation-level index |
| `Emp` ... `Payroll` | DOUBLE | Core measure payload |
| `sEmp` ... `sPayroll` | INTEGER | Measure-status / suppression payload |
| `source_file` | VARCHAR | File of origin |
| `release_id` | VARCHAR | Release stamp such as `R2026Q2` from `version_qwi.txt` |
| `state_scope` | VARCHAR | State or scope folder from the release path |
| `keep_start_year` | INTEGER | First retained year in the rolling 10-year window |
| `keep_end_year` | INTEGER | Last retained year in the rolling 10-year window |

Even though the planned Silver table will simplify to canonical fields such as `industry_sector`, `age_group`, and `education`, staging should keep the full published identifier family so we can inspect actual aggregation behavior before pruning. The implementation should retain only:

- county rows
- all-sex age rows where `education = E0`
- all-sex education rows where `agegrp = A00` and `education != E0`
- the latest rolling `10` years in each state file

---

## 9. Staging To Silver

Recommended Silver handoff:

1. Read `staging.lehd_qwi`.
2. Keep the county rows from `geo_level = C` as the canonical fine-grain geography.
3. Join `silver.xwalk_cbsa_county` to derive complete CBSA rows from counties.
4. Join `silver.xwalk_county_state` to derive canonical state rows from counties.
5. Join `silver.xwalk_state_region` to derive division rows from the state base.
6. Derive national rows from the county/state base.
7. Normalize the first-pass analytical grain to:
   - `geo_level`
   - `geo_id`
   - `year`
   - `quarter`
   - `industry_sector`
   - `age_group`
   - `education`
8. Compute annual summaries only after the quarterly source shape has been validated.

The key design choice is to keep staging fully source-faithful and defer all cross-state CBSA reconciliation to Silver, where the repo already owns those geography rules.

---

## 10. Operational Notes

- The current live release index shows staggered 2026 refresh dates across states rather than one perfectly synchronized publish timestamp.
- The schema says the `2025` TIGER/Line geography vintage is used as of release `R2026Q1`.
- Because the public files are already compressed CSVs with stable naming, a direct file-ingest staging script is operationally simpler than browser automation or manual extraction.
- The current plan text should not assume a `2009` demographic-history boundary without revalidation.
- The current plan text should also not assume the `lehdr::get_qwi()` wrapper exists in the runtime unless we intentionally pin and verify a package version that exports it.
- The implemented staging path should download files to a temporary scratch directory, filter them immediately, write only the retained 10-year county subset to DuckDB, and then delete the full raw files rather than caching the full historical panels on disk.

---

## 11. Runbook

This runbook is the recommended operator path for loading QWI staging without keeping an agent attached to a long-running session.

### Pre-flight

Confirm these conditions before running:

- `DB_PATH` is set and points to the working DuckDB file
- no other process is currently writing `staging.lehd_qwi`
- you are running from the repo root: `patterns_in_place/`

Recommended command forms:

```bash
Rscript foundations/etl/staging/get_lehd_qwi.R
```

```bash
LEHD_QWI_STATE_SCOPE=de,md,pa Rscript foundations/etl/staging/get_lehd_qwi.R
```

Chunked append-mode form:

```bash
LEHD_QWI_APPEND_MODE=true LEHD_QWI_STATE_SCOPE=de,md,pa Rscript foundations/etl/staging/get_lehd_qwi.R
```

Recommended background run with logging:

```bash
Rscript foundations/etl/staging/get_lehd_qwi.R > /tmp/lehd_qwi_run.log 2>&1
```

Chunked append-mode run with logging:

```bash
LEHD_QWI_APPEND_MODE=true LEHD_QWI_STATE_SCOPE=de,md,pa Rscript foundations/etl/staging/get_lehd_qwi.R > /tmp/lehd_qwi_run.log 2>&1
```

Watch progress with:

```bash
tail -f /tmp/lehd_qwi_run.log
```

### Milestone 1: Small-state smoke test

Run:

```bash
LEHD_QWI_STATE_SCOPE=de,md,pa Rscript foundations/etl/staging/get_lehd_qwi.R
```

What to look for:

- the script prints `Processing LEHD QWI county files for scope:` for each requested scope
- the script exits without an error
- no raw files are left behind in a permanent cache path

Quick QA after completion:

```bash
Rscript -e "source('foundations/etl/utils.R'); con <- DBI::dbConnect(duckdb::duckdb(), dbdir = get_env_path('DB_PATH'), read_only = TRUE); print(DBI::dbGetQuery(con, 'select state_scope, min(year) as min_year, max(year) as max_year, count(*) as rows from staging.lehd_qwi group by 1 order by 1')); DBI::dbDisconnect(con, shutdown = TRUE)"
```

Success signals:

- each requested scope appears exactly once
- `min_year` is the expected rolling-window start for that scope
- `max_year` is the latest published year for that scope
- row counts are non-trivial and vary by state rather than being zero or identical

### Milestone 2: Large-state stress test

Run:

```bash
LEHD_QWI_STATE_SCOPE=ca,tx,fl Rscript foundations/etl/staging/get_lehd_qwi.R
```

What to look for:

- the script continues advancing state by state rather than stalling before the first write
- memory usage stays stable because batches are written one state/demo family at a time
- the run completes without a DuckDB connection error or out-of-memory failure

Quick QA after completion:

```bash
Rscript -e "source('foundations/etl/utils.R'); con <- DBI::dbConnect(duckdb::duckdb(), dbdir = get_env_path('DB_PATH'), read_only = TRUE); print(DBI::dbGetQuery(con, 'select demo_family, count(*) as rows from staging.lehd_qwi group by 1 order by 1')); print(DBI::dbGetQuery(con, \"select count(distinct geo_id) as counties, min(year) as min_year, max(year) as max_year from staging.lehd_qwi\")); DBI::dbDisconnect(con, shutdown = TRUE)"
```

Success signals:

- both demo families appear: `age` and `education`
- county counts are materially larger than the small-state test
- the retained year range still matches the rolling 10-year contract

### Milestone 3: Full national run

Run:

```bash
Rscript foundations/etl/staging/get_lehd_qwi.R > /tmp/lehd_qwi_run.log 2>&1
```

What to look for while it runs:

- the log advances through state scopes one at a time
- there are no repeated retries of the same scope
- the process remains alive until the final `CHECKPOINT`

Quick QA after completion:

```bash
Rscript -e "source('foundations/etl/utils.R'); con <- DBI::dbConnect(duckdb::duckdb(), dbdir = get_env_path('DB_PATH'), read_only = TRUE); print(DBI::dbGetQuery(con, 'select count(*) as rows, count(distinct state_scope) as scopes, count(distinct demo_family) as demo_families, min(year) as min_year, max(year) as max_year from staging.lehd_qwi')); print(DBI::dbGetQuery(con, 'select state_scope, count(*) as rows from staging.lehd_qwi group by 1 order by 1')); DBI::dbDisconnect(con, shutdown = TRUE)"
```

Success signals:

- `demo_families = 2`
- `scopes = 52` for the default first-pass scope (`50` states + `DC` + `PR`)
- `min_year` and `max_year` look plausible for the retained 10-year panel
- every default scope has rows

### Milestone 4: Contract sanity checks

If the full run completes, run one more contract-focused QA:

```bash
Rscript -e "source('foundations/etl/utils.R'); con <- DBI::dbConnect(duckdb::duckdb(), dbdir = get_env_path('DB_PATH'), read_only = TRUE); print(DBI::dbGetQuery(con, \"select demo_family, min(sex) as min_sex, max(sex) as max_sex, min(agegrp) as min_agegrp, max(agegrp) as max_agegrp, min(education) as min_education, max(education) as max_education from staging.lehd_qwi group by 1 order by 1\")); DBI::dbDisconnect(con, shutdown = TRUE)"
```

Success signals:

- `age` rows show `sex = 0` and `education = E0`
- `education` rows show `sex = 0` and `agegrp = A00`
- there are no unexpected demographic slices leaking into staging

### If something fails

Start with the smallest reproducible rerun:

```bash
LEHD_QWI_STATE_SCOPE=de Rscript foundations/etl/staging/get_lehd_qwi.R
```

Then expand to the failing scope set once the single-state run is clean.

The script overwrites `staging.lehd_qwi`, so do not run multiple copies in parallel and do not treat a partial failed table as final output.

### Append mode

The staging script now supports a safe chunked mode:

- set `LEHD_QWI_APPEND_MODE=true`
- pass a subset of scopes in `LEHD_QWI_STATE_SCOPE`
- the script will replace rows for each incoming `state_scope` before inserting the refreshed batch

That means append mode is:

- resumable by chunk
- safe to rerun for the same state subset
- still not safe to run in parallel

Example regional chunk pattern:

```bash
LEHD_QWI_APPEND_MODE=true LEHD_QWI_STATE_SCOPE=de,md,pa,nj,ny,ct,ri,ma,vt,nh,me Rscript foundations/etl/staging/get_lehd_qwi.R > /tmp/lehd_qwi_northeast.log 2>&1
```

```bash
LEHD_QWI_APPEND_MODE=true LEHD_QWI_STATE_SCOPE=va,wv,nc,sc,ga,fl,ky,tn,ms,al,ar,la,ok,tx,dc,pr Rscript foundations/etl/staging/get_lehd_qwi.R > /tmp/lehd_qwi_south.log 2>&1
```

```bash
LEHD_QWI_APPEND_MODE=true LEHD_QWI_STATE_SCOPE=oh,mi,in,il,wi,mn,ia,mo,nd,sd,ne,ks Rscript foundations/etl/staging/get_lehd_qwi.R > /tmp/lehd_qwi_midwest.log 2>&1
```

```bash
LEHD_QWI_APPEND_MODE=true LEHD_QWI_STATE_SCOPE=mt,wy,co,nm,id,ut,az,nv,ca,or,wa,ak,hi Rscript foundations/etl/staging/get_lehd_qwi.R > /tmp/lehd_qwi_west.log 2>&1
```

Recommended QA after each chunk:

```bash
Rscript -e "source('foundations/etl/utils.R'); con <- DBI::dbConnect(duckdb::duckdb(), dbdir = get_env_path('DB_PATH'), read_only = TRUE); print(DBI::dbGetQuery(con, 'select state_scope, min(year) as min_year, max(year) as max_year, count(*) as rows from staging.lehd_qwi group by 1 order by 1')); DBI::dbDisconnect(con, shutdown = TRUE)"
```

---

## 12. Known Gaps

- The precise reason the older `2009` education / race planning note diverges from the current live Delaware files is still unclear. The safest current conclusion is that the note is stale, not that every state has identical historical depth.
- We have verified the public release directories and live file shape, but we have not yet built the governed staging contract that will test all states end to end.
- The first-pass spec now recommends county-only staging plus county-derived higher geographies. If later profiling shows a compelling reason to ingest published state or metro files for QA, that can be revisited separately without changing the canonical staging contract.

---

## 13. Source References

- https://lehd.ces.census.gov/data/
- https://lehd.ces.census.gov/data/#qwi
- https://lehd.ces.census.gov/data/qwi/latest_release/
- https://lehd.ces.census.gov/data/qwi/latest_release/de/version_qwi.txt
- https://lehd.ces.census.gov/data/schema/latest/
- https://lehd.ces.census.gov/data/schema/latest/lehd_public_use_schema.html
- https://lehd.ces.census.gov/data/schema/latest/lehd_csv_naming.html
- https://ledextract.ces.census.gov/
