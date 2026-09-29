# Public CBSA panel: narrow scope, no Zillow lineage

**Date:** 2026-09
**Source:** `public-cbsa-panel/public_cbsa_panel_spec.md`; `public-cbsa-panel/spec/v2026.1_scope.md`

## Decision

The first public release (v2026.1) is deliberately narrow: a county-to-CBSA crosswalk plus two CBSA-year panels (`economics_industry_wide`, `affordability_wide`) for all 935 metro and micro CBSAs. No released field may have Zillow anywhere in its lineage. The release workspace stays private and separate from the eventual public repository.

## Why

A dependable, citable contract matters more than breadth for a first release. Other sources are held back until v1 gets feedback, because they add documentation burden or uneven coverage.

Zillow is excluded so the release contains only public data and doesn't depend on Zillow's terms of service. That holds at least for the first releases; revisiting it needs a new decision record.

## What it means

- Fields can't be added during implementation; a field with doubtful lineage is removed, not repaired by widening scope.
- Export validation rejects undeclared columns and any Zillow lineage.
- Public-facing docs are written per release, not as part of the internal docs.
