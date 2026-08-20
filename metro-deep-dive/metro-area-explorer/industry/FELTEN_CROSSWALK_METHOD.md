# Felten Crosswalk Method

This note summarizes how we crosswalked Felten AI exposure data onto the Industry explorer's internal NAICS and SOC surfaces, how we audited the gaps, and how we converted the reviewed decisions into the final app-facing join shape.

## Goal

We wanted D6 to use Felten exposure scores against our internal industry and occupation datasets without relying on a brittle one-off join. The final objective was:

- preserve the raw Felten appendix tables as the canonical score source
- audit where our live NAICS and SOC codes did not map cleanly
- review and lock manual override decisions where needed
- produce final app-facing crosswalk tables that D6 can read directly

## Source Inputs

Raw Felten inputs remain section-owned:

- `metro-deep-dive/metro-area-explorer/industry/reference_data/AIOE_DataAppendix.xlsx`
  - Appendix A: occupation exposure (`AIOE`)
  - Appendix B: industry exposure (`AIIE`)

Internal code surfaces used for the audit:

- NAICS:
  - national 2024 detailed industry rows built from `staging.bls_qcew_county`
  - filtered through `silver.bls_qcew_industry_map`
- SOC:
  - national 2025 detailed occupation rows built from `silver.bls_oews`

## First Join Logic

The first pass did two different things:

- SOC joined more directly because many detailed SOC codes line up to Felten Appendix A.
- NAICS required more handling because Felten Appendix B uses an older/static NAICS shape and some aggregate codes.

We already had a small runtime NAICS fallback map in `data_prep.py` for obvious appendix-vintage mismatches such as:

- retail code revisions
- a few communications and finance aggregations
- select grouped wholesale and trucking codes

That got us to a usable first-pass join, but not a reviewed final one.

## Audit Build

We created a dedicated audit builder:

- `metro-deep-dive/metro-area-explorer/industry/build_felten_review_crosswalks.py`

That script produced national-weighted audit files so we could review coverage using real employment weights rather than Richmond-only weights.

Key outputs:

- `audit_felten_naics_national_2024.csv`
- `audit_felten_soc_national_2025.csv`
- `recommended_felten_naics_overrides_initial.csv`
- `recommended_felten_soc_overrides_initial.csv`
- `remaining_felten_naics_review_queue_national_2024.csv`
- `remaining_felten_soc_review_queue_national_2025.csv`
- `audit_crosswalk_analysis.md`

Each audit row included:

- our code and name
- current Felten match status
- employment weight and share of total
- candidate 1/2/3 codes and names
- title-similarity scores
- Felten exposure scores for candidates where available
- review buckets and manual decision fields

## SOC Review Approach

SOC used two layers:

1. Direct Appendix A joins where our detailed SOC code already matched Felten.
2. Review support for unmatched rows using:
   - the official BLS `2010 -> 2018` SOC crosswalk
   - title similarity within the same SOC major group

This gave us a much better audit surface for newer OEWS detailed SOC codes that did not exist in Felten's static appendix under the same exact code.

We then manually reviewed the remaining unresolved SOC rows and saved the final decisions into repo-owned artifacts:

- `reviewed_remaining_felten_soc_review_queue_national_2025.csv`
- `locked_felten_soc_manual_overrides_national_2025.csv`

Result:

- SOC is now treated as locked for D6
- the final runtime no longer depends on the first-pass audit heuristics

## NAICS Review Approach

NAICS was harder because Appendix B has much thinner coverage for certain families, especially agriculture and related industries.

The first audit pass exposed a real problem:

- when Felten lacked a same-family concept, broad title similarity sometimes surfaced bad candidates
- agricultural production industries were especially prone to nonsense suggestions because Felten often carried only support activities rather than the production industries themselves

We tightened the candidate logic to avoid misleading matches:

- prefer same 3-digit family candidates
- allow narrow family-specific proxy logic only where that was transparent
- stop falling back to unrelated global title matches
- leave structurally missing concepts unmatched when Felten does not truly carry them

For agriculture and similar cases, the second pass behaved more honestly:

- crop production rows could point to `1151` support activities for crop production as an explicit proxy candidate
- animal production rows could point to `1152` support activities for animal production
- forestry rows narrowed to `1133` logging versus `1151`
- concepts with no defensible proxy stayed unmatched

We then manually reviewed the remaining NAICS rows and saved the final decisions into repo-owned artifacts:

- `reviewed_remaining_felten_naics_review_queue_national_2024.csv`
- `locked_felten_naics_manual_overrides_national_2024.csv`

## Final App-Facing Shape

We decided to separate:

- the raw Felten score tables
- the audit/review trail
- the final runtime crosswalks

That means the app does not read the review queues directly. Instead it reads final resolved crosswalk tables:

- `felten_naics_crosswalk_final.csv`
- `felten_soc_crosswalk_final.csv`

These tables combine:

- rows that already matched directly
- rows resolved through the locked manual overrides

They include fields such as:

- our code
- Felten code
- Felten name
- Felten score
- `match_basis`
- `manual_notes`
- `review_source`

## Runtime Join Pattern

The final D6 join path is:

1. internal code table
2. join to final crosswalk on our code
3. resolve final Felten code and score from that crosswalk
4. compute coverage and weighted exposure metrics from the resolved score

In practice:

- sector D6 now joins 4-digit QCEW rows through `felten_naics_crosswalk_final.csv`
- occupation D6 now joins detailed OEWS rows through `felten_soc_crosswalk_final.csv`

This replaced the earlier runtime behavior that relied more heavily on first-pass matching logic and inline fallback joins.

## Why This Was Better

This workflow gave us four things:

1. A preserved raw source of truth.
   - The workbook remains untouched and remains the canonical source for Felten scores.

2. A transparent audit trail.
   - We kept review queues, candidate rankings, and manual notes rather than burying decisions in code.

3. A stable app-facing interface.
   - D6 reads final crosswalk tables, not review heuristics.

4. A defensible methods story.
   - We can explain where direct matches were used, where manual overrides were used, and where Felten coverage is structurally limited.

## Final Files To Know

Raw source:

- `reference_data/AIOE_DataAppendix.xlsx`

Audit and review:

- `outputs/national/d6_coverage_review/audit_felten_naics_national_2024.csv`
- `outputs/national/d6_coverage_review/audit_felten_soc_national_2025.csv`
- `outputs/national/d6_coverage_review/reviewed_remaining_felten_naics_review_queue_national_2024.csv`
- `outputs/national/d6_coverage_review/reviewed_remaining_felten_soc_review_queue_national_2025.csv`
- `outputs/national/d6_coverage_review/locked_felten_naics_manual_overrides_national_2024.csv`
- `outputs/national/d6_coverage_review/locked_felten_soc_manual_overrides_national_2025.csv`

Final runtime crosswalks:

- `outputs/national/d6_coverage_review/felten_naics_crosswalk_final.csv`
- `outputs/national/d6_coverage_review/felten_soc_crosswalk_final.csv`

Runtime implementation:

- `metro-deep-dive/metro-area-explorer/industry/data_prep.py`

Audit builder:

- `metro-deep-dive/metro-area-explorer/industry/build_felten_review_crosswalks.py`

## Current Status

As of August 9, 2026:

- SOC crosswalk decisions are locked and used at runtime
- NAICS reviewed overrides are locked and used at runtime
- D6 uses final reviewed crosswalk tables in the app
- the full audit trail remains preserved beside the final runtime assets
