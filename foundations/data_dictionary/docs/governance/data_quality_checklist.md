# Patterns Foundations Master Data Quality Checklist

Use this checklist for any table dictionary build/update and for recurring QA runs.

## How to Use
- Mark each check as `[x]` pass, `[ ]` pending, or `[!]` fail.
- Record run metadata: date, table, environment, and checker.
- Treat checks marked **Critical** as release blockers.

## Run Metadata (fill each run)
- Table: ``
- Schema: ``
- Run date: ``
- Data vintage / snapshot: ``
- Environment: ``
- Checked by: ``

## 1) Schema & Contract Checks
- [ ] **Critical** Table exists in expected schema.
- [ ] **Critical** Required columns are present.
- [ ] **Critical** Column data types match documented contract.
- [ ] Column order matches contract (if order-dependent consumers exist).
- [ ] No unexpected extra columns (or extras are documented/approved).

## 2) Grain, Keys, and Uniqueness
- [ ] **Critical** Grain statement is still valid for current data.
- [ ] **Critical** Primary key candidate has zero duplicates.
- [ ] Alternate keys (if documented) behave as expected.
- [ ] Key columns have expected formatting (padding, length, case).

## 3) Nullness & Completeness
- [ ] **Critical** Required key columns have 0% nulls.
- [ ] Required descriptor columns meet null-rate thresholds.
- [ ] Nullable columns with expected nulls are still within expected range.
- [ ] No sudden null spikes vs prior run.

## 4) Domain & Value Validations
- [ ] **Critical** Enumerated fields stay within allowed values.
- [ ] Code length/shape checks pass (e.g., FIPS/GEOID width).
- [ ] Numeric columns are in sensible ranges.
- [ ] No impossible or contradictory values.

## 5) Referential Integrity
- [ ] **Critical** Documented foreign-key-like joins resolve at expected rate.
- [ ] Orphan key count is within tolerance and explained.
- [ ] Crosswalk cardinality behavior remains expected.

## 6) Coverage Checks (Time & Geography)
- [ ] Time coverage matches expected vintage/range.
- [ ] Geographic coverage (levels/regions/states) matches expectations.
- [ ] Row count is within expected band vs previous run.
- [ ] Distinct entity counts (geo ids, KPI ids, etc.) are stable or explained.

## 7) Distribution & Drift Checks
- [ ] Top values for categorical columns are stable or explained.
- [ ] Distinct-count drift is reviewed and documented.
- [ ] Numeric distribution drift is reviewed (when applicable).
- [ ] Significant composition shifts have a source explanation.

## 8) Lineage & Freshness
- [ ] **Critical** Source dataset/file is identified and accessible.
- [ ] ETL script path and write target are documented.
- [ ] Source vintage/version metadata is captured.
- [ ] Last refresh timestamp is recorded where available.

## 9) Documentation Quality
- [ ] Overview, grain, keys, and coverage sections are complete.
- [ ] Column definitions are complete; unknowns flagged `needs confirmation`.
- [ ] Data Quality Notes are updated from current run results.
- [ ] Known Gaps / To-Dos reflect outstanding risks.

## 10) Release Decision
- [ ] **Critical** No open critical failures.
- [ ] Warning-level issues are accepted and tracked.
- [ ] Artifacts updated:
- [ ] `data_dictionary/layers/<layer>/<schema>__<table>.md`
- [ ] `data_dictionary/layers/<layer>/<schema>__<table>.yml`

## Current Implementation Status (as of 2026-03-02)

### Checks we are currently running
- Table existence and schema discovery via DuckDB `information_schema` queries.
- Row count profiling.
- Column profiling: type, null %, distinct count, min/max (or text length min/max), top-5 values.
- Candidate key uniqueness checks.
- Basic coverage checks used during table write-ups (e.g., distinct geo counts, vintage min/max).
- Manual lineage extraction from ETL scripts and SQL files.

### Checks partially present (manual/non-blocking)
- Duplicate checks are computed in some ETL scripts (for example BEA silver scripts create `*_dupe` data frames), but runs are not failed automatically.
- Some SQL outputs include quality flag columns, but these are not centralized as a project-wide gate.

### Checks not yet automated as enforced gates
- No centralized pass/fail DQ pipeline across Bronze/Staging/Silver/Gold.
- No enforced PK/FK constraints at the DuckDB table level for documented key candidates.
- No standardized threshold registry (null-rate, drift %, orphan-rate) applied on every run.
- No run-history logging table for DQ outcomes.

## Suggested Next Step
- Start with one table-level DQ runner for `silver.xwalk_cbsa_county` that writes pass/fail results to a `silver.data_quality_runs` log table, then generalize to other tables in the shared `projects/patterns_in_place` workspace.
