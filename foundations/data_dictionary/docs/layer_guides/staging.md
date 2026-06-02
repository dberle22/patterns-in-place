# Staging Guide

Staging checklist:
- [layers/staging/checklist.md](../../layers/staging/checklist.md)

## Documentation Model
- Staging dictionaries are grouped by source/theme family, not by every geography replica table.
- One staging family contract should cover all materially identical landing tables produced by the same ingest workflow.
- Geography-replica tables are treated as documented when they appear in the family doc's coverage matrix.
- Create a standalone staging dictionary only when a replica table has a meaningfully different schema or business contract.

## Required Sections For A Family Contract
- Overview with the source/theme family, the ingest script, and the documentation rule.
- Geography coverage matrix, or a coverage matrix for non-geographic variant families.
- Contract summary describing whether the family shares one signature or multiple variants.
- Shared columns, lineage, data quality notes, and known gaps.

## Coverage Expectations
- The staging checklist should track dictionary coverage at the family level.
- Family docs should list every current write target from `scripts/etl/staging` that belongs to that contract.
- Legacy compatibility outputs can remain in the matrix, but they should be labeled as compatibility tables so future cleanup is visible.
