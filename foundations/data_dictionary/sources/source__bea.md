# Source Spec: BEA

## 1. Overview

- Source: U.S. Bureau of Economic Analysis
- Access pattern: API via `bea.R`
- Primary credential dependency: `BEA_KEY`
- Scope in Foundations: BEA Regional data supplies economic output, personal income, and regional price parity datasets that land in a shared staging schema and are then modeled into Silver long and wide tables.
- Documentation goal: this file is the source-level spec for BEA as a provider. Topic-level variation is documented within each section below.

## 2. Coverage Matrix

This source spec covers the BEA Regional topic groups currently documented in the data dictionary.

| Topic group | Staging family contracts | Silver outputs |
| --- | --- | --- |
| CAGDP | [../layers/staging/staging__bea_cagdp2.md](../layers/staging/staging__bea_cagdp2.md), [../layers/staging/staging__bea_cagdp9.md](../layers/staging/staging__bea_cagdp9.md) | `silver.bea_regional_cagdp2_long`, `silver.bea_regional_cagdp2_wide`, `silver.bea_regional_cagdp9_long`, `silver.bea_regional_cagdp9_wide` |
| CAINC | [../layers/staging/staging__bea_cainc1.md](../layers/staging/staging__bea_cainc1.md), [../layers/staging/staging__bea_cainc4.md](../layers/staging/staging__bea_cainc4.md) | `silver.bea_regional_cainc1_long`, `silver.bea_regional_cainc1_wide`, `silver.bea_regional_cainc4_long`, `silver.bea_regional_cainc4_wide` |
| CAINC5N | [../layers/staging/staging__bea_cainc5n.md](../layers/staging/staging__bea_cainc5n.md) | `silver.bea_cainc5n` |
| MARPP | [../layers/staging/staging__bea_marpp.md](../layers/staging/staging__bea_marpp.md) | `silver.bea_regional_marpp_long`, `silver.bea_regional_marpp_wide` |
| Metadata / reference | [../layers/staging/staging__bea_metadata.md](../layers/staging/staging__bea_metadata.md) | `silver.bea_regional_tables`, `silver.bea_regional_line_codes`, `silver.bea_regional_metrics_ref`, `silver.bea_regional_metrics_clean` |

## 3. Source Contract

- Provider: U.S. Bureau of Economic Analysis
- Retrieval interface: `bea.R`
- Dataset family in current pipeline: `Regional`
- Common request pattern: table name + geography token(s) + line code + year range
- Common geography pattern: state, county, and CBSA for most Regional tables; MARPP currently uses state and CBSA only
- Common time pattern: script-defined year ranges by table family, with older historical coverage in CAGDP2 / CAINC1 and shorter coverage in some newer series

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- [../../etl/staging/get_bea.R](../../etl/staging/get_bea.R)

| Topic group | BEA table families in scope | Subject area |
| --- | --- | --- |
| CAGDP | `CAGDP2`, `CAGDP9` | GDP totals and GDP industry detail |
| CAINC | `CAINC1`, `CAINC4` | personal income headlines and personal income detail |
| CAINC5N | `CAINC5N` | earnings by broad NAICS industry plus all-industry compensation components |
| MARPP | `MARPP` and `SARPP`-style price parity mappings in metric metadata | regional price parity and real consumption / deflator metrics |
| Metadata / reference | Regional table registry, line-code registry, curated metric dictionary | table discovery, line-code interpretation, and metric-key mapping |

## 4. Staging Shape

Common BEA staging pattern:
- one staging family contract per BEA table family
- shared normalized schema across metric families
- long-format rows keyed by source table, geography, time period, and line code

Shared staging columns across the main BEA metric families:
- `code`
- `table`
- `geo_level`
- `geo_id`
- `geo_name`
- `period`
- `line_code`
- `unit_raw`
- `unit_mult`
- `value_raw`
- `value`
- `note_ref`

| Topic group | Staging families | Coverage shape |
| --- | --- | --- |
| CAGDP | `staging__bea_cagdp2`, `staging__bea_cagdp9` | three geography slices each: CBSA, county, state |
| CAINC | `staging__bea_cainc1`, `staging__bea_cainc4` | three geography slices each: CBSA, county, state |
| CAINC5N | dedicated `staging.bea_cainc5n` fact table plus `staging.bea_cainc5n_line_codes` reference table | live staging includes county, state, and U.S. rows from the Regional API; industry detail is published as earnings lines rather than parallel wages/supplements rows |
| MARPP | `staging__bea_marpp` | two geography slices: CBSA and state |
| Metadata / reference | `staging__bea_metadata` | not a geography ladder; registry-style reference outputs |

Notes:
- The main BEA metric families all currently document the same 12-column staging signature.
- The metadata family is structurally different and is better treated as a reference-output exception rather than a fact-table family.

## 5. Staging To Silver

Common BEA handoff pattern:
1. Fetch normalized long-format BEA rows into staging.
2. Join staging rows to BEA metric reference metadata to derive `metric_key` and cleaned labels.
3. De-duplicate or aggregate where needed at the geography-period-metric level.
4. Rebuild or standardize CBSA rows in Silver where the model uses county-based rebasing.
5. Materialize one long Silver table and one wide Silver table per topic family.

| Topic group | Silver handoff | Special path |
| --- | --- | --- |
| CAGDP | `CAGDP2` staging -> `silver.bea_regional_cagdp2_long` / `_wide`; `CAGDP9` staging -> `silver.bea_regional_cagdp9_long` / `_wide` | CBSA rows are rebuilt from county totals in the Silver scripts |
| CAINC | `CAINC1` staging -> `silver.bea_regional_cainc1_long` / `_wide`; `CAINC4` staging -> `silver.bea_regional_cainc4_long` / `_wide` | `CAINC1` explicitly derives `pi_per_capita`; `CAINC4` drops `pi_per_capita` from the detail flow |
| CAINC5N | dedicated staging -> `silver.bea_cainc5n` | the curated Silver contract keeps one row per `geo_level + geo_id + period + industry_key`; broad industry rows carry `earnings_total`, while `wages_salaries`, `supplements`, and derived `compensation_total` are populated only on the `all_industries` row because BEA does not publish parallel industry-detail compensation rows in `CAINC5N` |
| MARPP | `MARPP` staging -> `silver.bea_regional_marpp_long` / `_wide` | state and CBSA only; wide output depends on curated metric-key mapping from the reference tables |
| Metadata / reference | staging metadata outputs + curated dictionary build -> `silver.bea_regional_tables`, `silver.bea_regional_line_codes`, `silver.bea_regional_metrics_ref`, `silver.bea_regional_metrics_clean` | reference outputs are written in `silver`, even though the family is documented under staging |

## 6. Transformation Notes

| Topic group | Long-table role | Wide-table / derivation logic |
| --- | --- | --- |
| CAGDP | preserves geography-period-metric rows for GDP totals and industry metrics | pivots `metric_key` into GDP columns; `CAGDP2` focuses on nominal GDP measures and `CAGDP9` on real GDP measures |
| CAINC | preserves geography-period-metric rows for income components and population | pivots selected income metrics wide; `CAINC1` derives per-capita personal income while `CAINC4` carries a broader component set |
| CAINC5N | preserves geography-period-industry rows for a curated broad-family earnings contract plus all-industry compensation components | does not pivot to a managed wide table in the first pass; CBSA rows are additive county rollups because the retained measures are dollar totals rather than rates |
| MARPP | preserves geography-period-metric rows for regional price parity metrics | pivots curated price / deflator / real-consumption metrics wide based on the metric reference dictionary |
| Metadata / reference | stores discovered BEA table and line-code metadata plus curated metric mappings | enables the other Silver BEA scripts to translate line codes into stable metric keys and decide which metrics belong in wide outputs |

Additional BEA-wide transform notes:
- The staging script first discovers BEA parameter metadata and writes `silver.bea_regional_tables` and `silver.bea_regional_line_codes`.
- `silver.bea_regional_metrics_ref` is the main curated bridge from BEA line codes to project metric keys.
- The GDP and income Silver scripts use `silver.bea_regional_metrics_ref` to join `line_code` to `metric_key`.
- Most topic families pivot from long to wide at `geo_level + geo_id + period`.

## 7. Data Quality Expectations

| Topic group | Non-boilerplate checks worth preserving |
| --- | --- |
| CAGDP | verify long-table uniqueness at `geo_level + geo_id + period + metric_key`; monitor whether county-to-CBSA rebasing still yields expected coverage and no duplicate metric rows |
| CAINC | verify long-table uniqueness and sanity-check per-capita derivation paths, especially where population is used as a denominator or where `pi_per_capita` is omitted from detailed component flows |
| MARPP | monitor null-heavy wide metrics such as real-consumption outputs and price-deflator fields; confirm expected state / CBSA coverage only |
| Metadata / reference | treat `line_code` as non-unique by itself; use caution around duplicate line codes across tables and around reference-table keys marked provisional in the current docs |

## 8. Operational Notes

- Primary BEA ingest entrypoint:
  [../../etl/staging/get_bea.R](../../etl/staging/get_bea.R)
- Planned CAINC5N first-pass ingest note:
  although CAINC5N lives in the same BEA Regional API family, the approved first-pass implementation should use a dedicated staging entrypoint (for example `get_bea_cainc5n.R`) rather than extending `get_bea.R` immediately.
  This is an intentional safety choice so the new CAINC5N path can be validated end to end without risking regressions in the existing BEA refresh.
  After the dedicated CAINC5N staging, Silver, and Gold path is working and documented, we can come back and consolidate the BEA ingest scripts if that still looks worthwhile.
- CAINC5N modeling note:
  the table name sounds narrower than the live payload actually is. The published industry detail rows are earnings rows, while `wages and salaries` and `supplements to wages and salaries` are published as all-industries component totals.
  Foundations therefore models CAINC5N as a broad industry earnings table with all-industry compensation columns, rather than allocating wages or supplements across industry rows.
- Curated metric dictionary builder:
  [../../etl/silver/bea_metric_dictionary.R](../../etl/silver/bea_metric_dictionary.R)
- Topic-specific Silver model entrypoints:
  [../../etl/silver/bea_cagdp2_silver.R](../../etl/silver/bea_cagdp2_silver.R),
  [../../etl/silver/bea_cagdp9_silver.R](../../etl/silver/bea_cagdp9_silver.R),
  [../../etl/silver/bea_cainc1_silver.R](../../etl/silver/bea_cainc1_silver.R),
  [../../etl/silver/bea_cainc4_silver.R](../../etl/silver/bea_cainc4_silver.R),
  [../../etl/silver/bea_marpp_silver.R](../../etl/silver/bea_marpp_silver.R)
- Current documentation pattern:
  staging remains family-contract based, Silver remains table-contract based, and this file sits above both as the provider-level spec
- Important implementation wrinkle:
  the BEA metadata family is documented under staging, but the ingest script writes its core registry outputs directly to `silver`

## 9. Known Gaps

- The BEA source spec now covers `CAGDP`, `CAINC`, `MARPP`, and the metadata/reference layer at a summary level, but it does not try to restate every line-code mapping already preserved in the Silver reference tables.
- `CAINC5N` now has dedicated staging, Silver, and Gold coverage, but the BEA provider spec still summarizes it at the source-family level rather than in a separate child source file.
- Existing staging family contracts summarize the landing shape but do not yet explain the full Silver handoff in place.
- The layer boundary for metadata outputs is still slightly awkward because the family is documented under staging while the canonical outputs live in `silver`.
- Some table-level lineage references still use older path conventions and should be normalized over time.
