# Patterns Foundations Data Dictionary

## Purpose
This folder is the durable metadata layer for the shared warehouse and semantic assets used across the Patterns in Place workspace.  
It is designed for:
- Human analysts who need clear, reusable field and table definitions
- Codex/agent workflows that need machine-readable contracts for profiling, QA, and documentation updates

## What The Dictionary Contains
Dictionary artifacts follow two patterns:
- Silver and Gold table dictionaries are stored as pairs: `<layer>/<schema>__<table>.yml` and `<layer>/<schema>__<table>.md`.
- Staging dictionaries are currently source/theme family contracts stored as Markdown files, with coverage matrices documenting the geography-replica tables owned by each family.

The dictionary captures:
- Table-level metadata: purpose, grain, keys, time coverage, geo coverage
- Column-level metadata: type, null %, distinct count, ranges/top values, definition
- Lineage: upstream sources, ETL scripts, and write targets
- KPI definitions where applicable

## Folder Structure
- [layers/bronze](./layers/bronze)
- [layers/staging](./layers/staging)
- [layers/silver](./layers/silver)
- [layers/gold](./layers/gold)

Workspace context:
- This repo is intended to live under `projects/patterns_in_place/patterns-foundations`
- Sibling repos such as `patterns-data` may consume or extend these contracts
- Keep local paths repo-relative so the folder can move cleanly between machines and GitHub

Project-wide control docs:
- [docs/governance/coverage_checklist.md](./docs/governance/coverage_checklist.md)
- [docs/governance/data_quality_checklist.md](./docs/governance/data_quality_checklist.md)
- [agent.md](./agent.md)
- [docs/governance/bug_fixes.md](./docs/governance/bug_fixes.md)

Layer guides:
- [docs/layer_guides/bronze.md](./docs/layer_guides/bronze.md)
- [docs/layer_guides/staging.md](./docs/layer_guides/staging.md)
- [docs/layer_guides/silver.md](./docs/layer_guides/silver.md)
- [docs/layer_guides/gold.md](./docs/layer_guides/gold.md)

Generated artifacts:
- `artifacts/audits/` for run-level audit outputs
- `artifacts/coverage/` for coverage summaries and unresolved-definition extracts
- `artifacts/backlog/` for remediation backlogs and ranking files

## Main Dictionary Themes
- Layered contracts: Bronze -> Staging -> Silver -> Gold
- Staging contracts are family-level landing contracts rather than one file per geography replica table
- Standardized geo/time fields across analytics tables (`geo_level`, `geo_id`, `geo_name`, `year`/`period`)
- ACS pattern in Silver:
`<theme>_base` tables: ACS-aligned base metrics and direct variable definitions
`<theme>_kpi` tables: business/semantic KPI definitions based on transformations
- BEA pattern in Silver:
long/wide table pairs, reference tables, and line code metadata
- Crosswalk pattern in Silver:
`xwalk_*` tables that define geographic mapping relationships

## Gold Layer Reference
Gold tables are curated analytic outputs that combine selected Silver metrics into decision-ready views.

Current Gold themes:
- Economics:
`gold.economics_gdp_wide`, `gold.economics_income_wide`, `gold.economics_labor_wide`, `gold.economics_industry_wide`
- Population and demographics:
`gold.population_demographics`
- Texas district metrics:
`gold.tx_isd_metrics` (active but still under refinement)

Gold definition conventions:
- If a Gold column is carried from Silver, the Gold definition should match the Silver definition directly.
- If a Gold column is derived in Gold SQL/R, use a semantic business definition in Gold and keep formula details in lineage.
- Avoid placeholder language like `Metric from ... table` in final Gold definitions.

Gold lineage conventions:
- Link each Gold table to its `scripts/etl/gold/*.sql` or `.R` model(s).
- Note major operations explicitly (joins, window functions, growth/CAGR logic, denominator choices).
- Preserve upstream references when metrics are carried from Silver.

Gold documentation workflow:
1. Update `gold__*.yml` first.
2. Validate definitions:
all carried fields use Silver definitions; derived fields use semantic definitions.
3. Sync `gold__*.md` from YAML.
4. Re-run coverage checks and unresolved-definition audit.
5. Log significant changes in `docs/governance/bug_fixes.md` if behavior/definitions changed materially.

## Source Of Truth Rules
- YAML is the source of truth for Silver and Gold table dictionaries.
- Staging is the current exception: source/theme family contracts are maintained directly in Markdown until a family-level machine-readable format is introduced.
- When a table has both YAML and Markdown artifacts, update YAML first, then sync Markdown.

## How Analysts Should Use This
- Start with the relevant `.md` contract file for quick understanding.
- For staging, that usually means the source/theme family contract rather than an individual replica table.
- Use `Grain & Keys` before joining tables.
- Use `Columns` definitions to interpret metrics and avoid misuse.
- Check `Data Quality Notes` and `Known Gaps / To-Dos` before publishing outputs.
- For derived KPIs, use semantic definitions as analysis meaning, and lineage for formula context.

## How Agents Should Use This
- Read `.yml` first for deterministic parsing when a YAML artifact exists.
- For staging family contracts, use the Markdown contract and its coverage matrix as the current source of truth.
- Treat `columns[].definition` and `needs_confirmation` as contract quality signals.
- Use lineage entries to trace transformations in ETL scripts.
- Prefer dictionary values over inferred guesses when generating analysis or visuals.
- When updating definitions:
- Keep key fields standardized across tables
- Label uncertain entries with `needs_confirmation: yes`
- Preserve deterministic formatting and section structure

## Coverage And Quality Workflow
- Coverage status by layer is tracked in `docs/governance/coverage_checklist.md` and layer-specific checklist files.
- DQ workflow is tracked in `docs/governance/data_quality_checklist.md`.
- Recommended update order for themed datasets:
1. Fill `*_base` definitions from authoritative source mappings
2. Fill `*_kpi` definitions with semantic business meaning
3. Sync corresponding `.md` from `.yml`
4. Re-run coverage and unresolved-definition audits

## Current Status (Working Convention)
- Staging family contracts and Silver dictionaries are primary references, but staging coverage should be interpreted at the source/theme family level rather than as one doc per replica table.
- Gold dictionary coverage is now operational and should be updated in lockstep with Gold ETL changes.
- `gold.tx_isd_metrics` remains a known exception area for ongoing definition hardening.

## Naming Note
- Historical references to `metro_deep_dive` remain in some lineage notes, script names, and copied artifacts because they document upstream provenance.
- Treat this repo as the canonical home for the dictionary itself, regardless of those inherited source references.

## Quick Start
1. Open the layer checklist (for example `layers/silver/checklist.md`).
2. Pick the next table or theme group.
3. If the artifact has YAML, update the `.yml` dictionary first; for staging family contracts, update the `.md` file directly.
4. Sync/update the companion `.md` file when a YAML artifact exists.
5. Log notable fixes in `docs/governance/bug_fixes.md` and update coverage checklists.
