# Foundation Epic — County-First CBSA Data Refresh

**Status:** Done — confirmed by Dan on 2026-09-29. Public panel v2026.1 (published 2026-09-28) ships the county-derived BEA GDP and HUD FMR series this epic produced. The task checkboxes below were never ticked individually.  
**Updated:** 2026-09-29  
**Owner area:** `foundations/etl`  
**Downstream consumer:** Patterns in Place: Metro & Micro Panel v2026.1

## Goal

Make the shared Foundation CBSA series reproducible from county-level source data and the
versioned county-to-CBSA crosswalk. Refresh the relevant BEA county data through 2024, add a
historical HUD Fair Market Rent series, and replace the current real-GDP rollup with BEA's
county aggregation methodology.

This is upstream data-platform work. It must land and be validated in Foundations before the
public-panel exporter is built against the resulting Gold tables.

## Product contract

- Production CBSA values for this scope originate from county-level source data.
- `silver.xwalk_cbsa_county` supplies the versioned County → CBSA membership used for every
  rollup.
- Direct BEA CBSA files may be retained only as a historical validation benchmark; they must
  not be the production source for the refreshed CBSA series.
- Every output must retain source vintage, coverage, and derivation metadata sufficient for a
  downstream release manifest.
- HUD FMR periods are fiscal years, not calendar years; that distinction must be carried into
  the data dictionary and downstream documentation.

## Scope

### 1. Refresh county BEA GDP inputs through 2024

- [x] Inspect the current BEA API/download availability and revision vintage for county GDP.
- [x] Update the county staging path to retrieve the 2024 revised county data required for
  industry GDP: current-dollar county-by-industry GDP and the inputs required to calculate real
  GDP under BEA's published aggregation method.
- [ ] Preserve the existing historical series, record the retrieval date and provider release
  date, and identify revisions to 2020–2023 rather than treating them as silent replacements.
- [ ] Confirm county identifiers, Connecticut 2024 planning-region treatment, suppressions, and
  line-code coverage before writing Silver transformations.
- [ ] Update only the BEA staging/Silver/Gold assets and pipeline wiring necessary for the
  county-first GDP series; do not broaden this epic to new sources or metrics.

### 2. Build a correct county-to-CBSA GDP aggregation

- [x] Keep current-dollar GDP aggregation as a sum of like county-industry cells.
- [x] Replace the existing simple sum of county real/chained-dollar GDP with BEA's published
  methodology: aggregate detailed county current-dollar GDP by industry, apply the required
  national industry price indexes, and construct chain-type real GDP at the target geography.
- [x] Implement this as reusable, documented Foundation logic rather than a public-panel-only
  calculation.
- [ ] Ensure ratios, industry shares, and concentration measures are calculated after the CBSA
  totals are derived.
- [x] Treat suppressed county inputs conservatively and make the resulting missingness explicit.
- [ ] Use the pre-discontinuation direct BEA CBSA series only to backtest 2017–2023 results.
  Define and document tolerances by metric; investigate material differences before accepting
  the new series.
- [ ] Explicitly test the Connecticut 2024 county-equivalent break and document the resulting
  continuity behavior.

### 3. Add historical county HUD Fair Market Rents

- [x] Inventory official HUD county-level FMR files from FY2012 through the latest available
  fiscal year and record their URLs, release dates, and file formats.
- [x] Generalize `get_hud_fmr.R`, which is currently effectively fixed to FY2023, to ingest the
  selected historical fiscal-year range without hard-coded single-year URLs.
- [x] Normalize county identifiers and bedroom FMR fields in staging while preserving source
  fidelity and fiscal-year metadata.
- [x] Inspect staged annual coverage, duplicate keys, missing county values, and changes in
  geographic/file conventions before modifying Silver.
- [x] Rebuild county and CBSA FMR outputs using the existing documented population-weighted
  aggregation rule, or revise that rule only if the source review demonstrates it is invalid.
- [ ] Validate annual county and CBSA coverage; explain all major gaps in the data dictionary.

### 4. Materialize, validate, and hand off

- [x] Run staging and Silver materializations sequentially; do not run concurrent
  DuckDB writers.
- [ ] Add focused checks for county source coverage, crosswalk membership, CBSA key uniqueness,
  real-GDP aggregation behavior, HUD fiscal-year coverage, and the 935-CBSA current universe.
- [x] Update `pipeline_manifest.yml` / `pipeline_manifest.md` with all added or changed build
  steps.
- [ ] Update table documentation and lineage with exact source vintages, field definitions,
  fiscal-year semantics, aggregation formulas, known suppression behavior, and the Connecticut
  caveat.
- [ ] Produce a concise handoff report: changed assets, source vintages, annual coverage,
  validation/backtest results, unresolved caveats, and the precise Gold tables/columns ready for
  the public-panel exporter.

## Non-goals

- Publishing the public Parquet/DuckDB release or creating public documentation.
- Adding QCEW, BFS, CBP, Zillow, CHAS, permits, vacancy, or occupancy measures.
- Changing the public panel's approved field allowlist without an explicit product decision.
- Claiming that county-derived real GDP is an official BEA CBSA estimate.

## Acceptance criteria

1. The relevant Gold CBSA GDP fields use county inputs and the versioned crosswalk, not direct
   BEA CBSA production data.
2. County GDP coverage includes the 2024 BEA vintage, with revisions and any geographic breaks
   recorded.
3. Real GDP is derived with BEA's published aggregation procedure and has a documented
   2017–2023 backtest against historical direct CBSA values.
4. County and CBSA HUD FMR coverage spans FY2012 through the chosen latest fiscal year, with
   annual coverage and missingness documented.
5. The Foundation pipeline, documentation, and handoff report are sufficient for the public
   panel to consume the refreshed Gold data without rediscovering source or methodology facts.

## Authoritative references

- [BEA FAQ on discontinuing aggregate-geography GDP and income estimates](https://www.bea.gov/help/faq/1481)
- [BEA technical document: geographic aggregation of county statistics](https://www.bea.gov/sites/default/files/2026-02/geo-aggregator-technical-document.pdf)
- [HUD Fair Market Rents data portal](https://www.huduser.gov/portal/datasets/fmr.html)
