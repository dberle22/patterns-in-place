# Source Spec: IRS

## 1. Overview

- Source: Internal Revenue Service Statistics of Income migration files
- Access pattern: annual CSV downloads
- Primary dependency: public IRS SOI files plus local raw-data and DuckDB paths
- Scope in Foundations: current coverage focuses on domestic inflow migration records that land in state and county staging tables, then flow into documented Silver and Gold migration contracts.
- Documentation goal: this file is the provider-level spec for IRS migration coverage as it currently exists in Foundations.

## 2. Coverage Matrix

This source spec covers the IRS topic groups currently documented in the data dictionary.

| Topic group | Staging family contracts | Silver outputs |
| --- | --- | --- |
| Migration inflows | [../layers/staging/staging__irs_migration.md](../layers/staging/staging__irs_migration.md) | [../layers/silver/silver__irs_migration_flows.md](../layers/silver/silver__irs_migration_flows.md), [../layers/silver/silver__irs_migration_summary.md](../layers/silver/silver__irs_migration_summary.md) |

## 3. Source Contract

- Provider: Internal Revenue Service Statistics of Income
- Retrieval interface in current coverage: annual county inflow CSV downloads
- Common request pattern: download one file per origin-year / destination-year pair, cache locally, then normalize domestic flow records
- Common geography pattern: county-to-county inflows and state-level inflow summaries
- Common time pattern: destination years 2012 through 2022 in the current staging pipeline, with `origin_year` carried alongside `dest_year`

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- [../../etl/staging/get_irs_migration.R](../../etl/staging/get_irs_migration.R)

| Topic group | Source files / subject area | Staging ingest entrypoint |
| --- | --- | --- |
| Migration inflows | SOI county inflow migration files with returns, exemptions, and AGI flows | [../../etl/staging/get_irs_migration.R](../../etl/staging/get_irs_migration.R) |

## 4. Staging Shape

Common IRS staging pattern in current coverage:
- one staging family contract
- one county inflow table plus one state inflow table
- one row per migration flow-year record at the source slice level

Shared staging columns:
- `flow_id`
- `year`
- `origin_year`
- `dest_year`
- `dest_state_fips`
- `origin_state_fips`
- `n_returns`
- `n_exemptions`
- `agi_thousands`
- `agi`

| Topic group | Staging family | Coverage shape |
| --- | --- | --- |
| Migration inflows | `staging__irs_migration` | county inflow detail plus state inflow summary materializations |

## 5. Staging To Silver

Current IRS handoff pattern:
1. Normalize inflow staging rows with origin and destination geography identifiers.
2. Join state and county naming metadata from crosswalk tables.
3. Materialize a detailed origin-destination Silver flow table for county and state rows.
4. Roll detailed flows into county, CBSA, and state Silver summary rows.
5. Join the Silver summary table into the Gold migration mart for county, CBSA, and state coverage.

| Topic group | Silver handoff | Special path |
| --- | --- | --- |
| Migration inflows | staging family -> `silver.irs_migration_flows` and `silver.irs_migration_summary` -> `gold.migration_wide` | Gold enrichment applies only to county, CBSA, and state rows because those are the geographies present in the IRS summary contract |

## 6. Transformation Notes

| Topic group | Current modeled role | Derivation logic |
| --- | --- | --- |
| Migration inflows | documented staged source with detailed and summary migration outputs | ingest builds `flow_id`, pads FIPS codes, drops within-county non-migrants, converts suppressed negative values to nulls, scales `agi_thousands` into dollar `agi`, deduplicates repeated staged county flows in Silver, and rebases county flows to CBSA for the summary contract |

Additional IRS-wide transform notes:
- The ingest script carries both `origin_year` and `dest_year`, while `year` is treated as the canonical analysis year.
- Current coverage centers on inflow files rather than maintaining a parallel outflow contract.
- `silver.irs_migration_flows` preserves county and state origin-destination detail in one shared contract with `geo_level`.
- `silver.irs_migration_summary` nets inflows and outflows at county, CBSA, and state grain; CBSA summaries exclude within-CBSA county moves.
- `gold.migration_wide` uses ACS as the geography backbone and enriches county/CBSA/state rows with IRS return-count and AGI migration metrics where summary rows exist.

## 7. Data Quality Expectations

| Topic group | Non-boilerplate checks worth preserving |
| --- | --- |
| Migration inflows | verify uniqueness of `flow_id + year`; confirm suppression handling keeps negative source values from leaking into measures; check that origin and destination FIPS normalization yields valid domestic geography IDs; monitor reconciliation between county detail and state summary slices |

## 8. Operational Notes

- Staging entrypoint:
  [../../etl/staging/get_irs_migration.R](../../etl/staging/get_irs_migration.R)
- Silver modeling entrypoint:
  [../../etl/silver/irs_migration_silver.R](../../etl/silver/irs_migration_silver.R)
- Gold modeling entrypoint:
  [../../etl/gold/gold_migration_wide.sql](../../etl/gold/gold_migration_wide.sql)
- Required local environment wiring:
  `DATA` for cached IRS CSVs and `DB_PATH` for DuckDB materialization
- Current documentation pattern:
  staging remains family-contract based, while Silver and Gold coverage now live in paired YAML + Markdown table contracts

## 9. Known Gaps

- Current IRS coverage remains domestic and inflow-sourced; there is no separate raw outbound file contract.
- Gold IRS enrichment applies only to county, CBSA, and state rows, not the broader ACS geography ladder.
- The semantic layer currently exposes IRS count-based metrics but not the new AGI migration fields as first-class queryable metrics.

---

## 10. Architecture Decisions

**Decision date:** 2026-06-02

### Silver contract
Build two Silver tables:

- `silver.irs_migration_flows` — full origin-destination pairs, one row per `geo_level + origin_geo_id + dest_geo_id + year`, with `n_returns`, `n_exemptions`, `agi_thousands`, and dollar-scaled `agi`. This is the analytical asset for deep-dive work (which counties or states a place is gaining from, plus the income profile of movers).
- `silver.irs_migration_summary` — collapsed to one row per `geo_level + geo_id + year`, with inflow, outflow, and net counts for returns, exemptions, and AGI. Rolled up to county, CBSA, and state using the standard geo crosswalk.

Implemented 2026-06-03 in `foundations/etl/silver/irs_migration_silver.R`.

### Gold contract
The county/CBSA/state rows from `silver.irs_migration_summary` feed `gold.migration_wide` alongside the existing ACS mobility columns. IRS adds return-count migration metrics (`irs_inflow_total`, `irs_outflow_total`, `irs_net_migration`, `irs_net_migration_rate`, `irs_migration_churn`) plus AGI migration metrics (`irs_inflow_agi`, `irs_outflow_agi`, `irs_net_agi`). Grain stays one row per `geo_level + geo_id + year`, matching the existing Gold table.

Implemented 2026-06-03 in `foundations/etl/gold/gold_migration_wide.sql`.
