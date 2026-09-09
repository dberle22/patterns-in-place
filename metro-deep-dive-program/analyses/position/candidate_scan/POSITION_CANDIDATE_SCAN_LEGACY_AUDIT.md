# Position Candidate Scan — Legacy Audit

**Completed:** 2026-09-08  
**Scope:** Epic 1 audit for the Candidate Scan notebook

## Decision

The legacy Candidate List remains a read-only comparison baseline. The first
Marimo method will be `candidate_scan_v1`: an analysis-local ranking that uses
the current cross-frame and Time-Series contracts without recreating Phase 6
pattern logic.

This is a review-priority score, not a metro-quality, opportunity, or
publication score.

## Sources audited

| Source | Role in the port | Disposition |
|---|---|---|
| `metro-deep-dive/research-tool/components/candidate_tab.py` | Legacy interaction behavior | Retain the all-market table, division and pattern-oriented filtering concept, active-market context, and CSV baseline behavior as notebook views. Do not port Streamlit controls or export. |
| `exploration/intelligence_framework/phase_6_trajectory/R/phase6_candidate_list.R` | Legacy formula | Comparison evidence only. Its pattern flags and trajectory-strength calculation are not current contracts. |
| `exploration/intelligence_framework/phase_6_trajectory/outputs/phase6_candidate_list.csv` | Persisted legacy ordering | Read-only baseline for side-by-side rank comparison. The file has 396 rows, ranks 1–396, and the same CBSA codes as the current marts. |
| `mart_intelligence.intelligence_cross_frame` | Current Profile evidence | Canonical source for identity, divergence, alignment, and signature. |
| `mart_intelligence.intelligence_trajectory_frame` | Current trajectory evidence | Canonical source for stored five-year frame salience, labels, tiers, and coverage. |
| `mart_intelligence.intelligence_trajectory_turn_signals` | Current turn evidence | Canonical source for the stored Opportunity five-year-versus-one-year turn status. |
| `mart_area_explorer.cbsa_profile_year` | Governed filters | Canonical source for population, state, Census division, and region filters at its latest available year. |

## Observed contract state

- The current Profile universe contains 396 CBSAs, one row per `cbsa_code`.
- The legacy candidate CSV also contains 396 CBSAs. The older Research Tool
  roadmap's reference to 401 CBSAs is stale and must not shape the port.
- `trajectory_pilot_v1` has five-year Character, Livability, and Opportunity
  rows for all 396 CBSAs. Three-frame coverage is eligible for 390 CBSAs and
  ineligible for six.
- The current Opportunity turn surface has six `confirmed_turn`, 34
  `emerging_turn_watch`, 350 `no_turn_signal`, and six
  `insufficient_evidence` rows.
- Current cross-frame evidence has no nulls in `frame_percentile_gap`,
  `overlap_profile`, or `signature`.

## Legacy-to-current field disposition

| Legacy concept or field | Current field(s) | Disposition |
|---|---|---|
| CBSA identity | `intelligence_cross_frame.cbsa_code`, `cbsa_name` | Retain. |
| Census division, state, region, population | Latest `mart_area_explorer.cbsa_profile_year` row | Retain as governed filters. |
| `frame_percentile_gap`, `overlap_profile`, `half_alignment`, `signature` | Same-named `intelligence_cross_frame` fields | Retain as Profile context. |
| `phase5_overlap_rank`, `phase5_overlap_pct` | Derive a transparent percentile from current `frame_percentile_gap` | Replace. The old rank was an opaque Phase 5 artifact; the raw current gap is canonical. |
| Frame trajectory scores and directions | Five-year `trajectory_salience_percentile`, `signal_tier`, `trajectory_label`, `coverage_status` by frame | Replace. Current stored concepts are salience and labels, not the old score/direction fields. |
| `opp_turn_signal`, `opp_turn_signal_type` | Opportunity `turn_status` for `five_year_vs_one_year` | Replace. Keep the engine-owned status visible. |
| Five pattern flags and `pattern_count` | None | Retire. Bounce Back, Hidden Livability Winner, Diverging From Themselves, Fast Demographic Changer, and Environmental Risk Outlier depend on Phase 6 calculations that are intentionally not reproduced by the Time-Series contract. |
| `overall_trajectory_strength` and percentile | None | Retire. Use a visible mean of the current stored frame-salience percentiles instead. |
| `candidate_score`, `candidate_rank`, CT exclusion, ZORI coverage | None | Keep only the score and rank as legacy-comparison columns. Do not carry old exclusion or coverage flags forward. |

## Candidate method: `candidate_scan_v1`

### Eligibility

Rank a market only when it has a cross-frame row and eligible five-year
trajectory coverage for Character, Livability, and Opportunity. Keep every
other current-universe market in the coverage table with its reason for
ineligibility. Missing trajectory evidence is never converted to zero.

### Components

All components use a 0–100 scale.

| Component | Definition | Weight |
|---|---|---:|
| Cross-frame divergence | Percentile rank of the current `frame_percentile_gap` across the Profile universe | 45% |
| Trajectory salience | Mean of the three stored five-year `trajectory_salience_percentile` values | 45% |
| Opportunity turn | Local editorial bonus: 10 for `confirmed_turn`, 5 for `emerging_turn_watch`, and 0 for `no_turn_signal`; engine status remains visible beside the bonus | 10% |

`candidate_score = 0.45 * divergence + 0.45 * trajectory_salience + 0.10 * opportunity_turn`.

The notebook may calculate the percentile rank, average, bonus, score, and
rank locally because they are explicitly the analysis-local candidate method.
It must read all upstream frame salience, coverage, and turn labels from the
materialized engine tables rather than recreate them.

### Required sensitivity cases

- divergence-heavy: 60% divergence, 30% salience, 10% turn
- trajectory-heavy: 30% divergence, 60% salience, 10% turn
- no-turn-bonus: 50% divergence, 50% salience, 0% turn

The sensitivity view will show rank movement against the default method, not
silently replace its ordering.

## Port behavior retained for Epic 2

- all-market ranked table with visible contributing fields
- division, state, population, Profile-context, trajectory-signal, and turn
  filters
- selected-market explanation and legacy-rank comparison
- compact shortlist comparison

The legacy CSV download, Streamlit navigation, CT-exclusion toggle, and direct
port of pattern filters are not part of the notebook boundary. Pattern filters
are replaced by current divergence, trajectory, and turn-status filters.

## Build implication

Epic 2 needs one notebook only. It will load the legacy CSV strictly for the
comparison columns and query all current evidence from DuckDB read-only. No
candidate mart, SQL-owned calculation, headless runner, or persisted QA bundle
is warranted.
