# Felten Crosswalk Audit

National-weighted audit surface for the Industry D6 Felten joins.

## What These Files Are

- `audit_felten_naics_national_2024.csv` tracks current and unresolved 4-digit NAICS matches against Felten Appendix B.
- `audit_felten_soc_national_2025.csv` tracks current and unresolved detailed SOC matches against Felten Appendix A.
- `our_weight` is the national employment weight from the live platform source.
- `our_share_of_total` is that code's share of the national employment base used for the audit.
- `audit_status` shows whether the row is already matched, unmatched on our side, or unmatched on the Felten side.

## Current National NAICS Audit Status

- `matched`: 255 rows, 96.8% of national detailed NAICS employment
- `unmatched_felten_code`: 15 rows, 0.0% of national detailed NAICS employment
- `unmatched_our_code`: 46 rows, 3.2% of national detailed NAICS employment

## Current National SOC Audit Status

- `matched`: 672 rows, 79.2% of national detailed SOC employment
- `unmatched_felten_code`: 88 rows, 0.0% of national detailed SOC employment
- `unmatched_our_code`: 157 rows, 20.8% of national detailed SOC employment

## How To Use This

- Review `matched` rows only when you want to audit an existing automatic join.
- Review `unmatched_our_code` rows first because those represent current platform coverage gaps.
- Review `unmatched_felten_code` rows second because those are unused Felten candidates that may justify a one-time override.
- Candidate columns are review hints, not final crosswalk decisions.

## First-Pass Recommendation Counts

- NAICS: `2` high-confidence and `14` medium-confidence unmatched-our-code recommendations
- SOC: `83` high-confidence and `33` medium-confidence unmatched-our-code recommendations

## Post-Recommendation Scenario

Assumption: accept every current `recommend_match = True` row as a one-time reviewed override.

### NAICS After Applying Recommendations

- `matched`: 255 rows, 96.8% of national detailed NAICS employment
- `matched_via_recommendation`: 16 rows, 0.9% of national detailed NAICS employment
- `unmatched_felten_code`: 15 rows, 0.0% of national detailed NAICS employment
- `unmatched_our_code`: 30 rows, 2.4% of national detailed NAICS employment

### SOC After Applying Recommendations

- `matched`: 672 rows, 79.2% of national detailed SOC employment
- `matched_via_recommendation`: 116 rows, 13.0% of national detailed SOC employment
- `unmatched_felten_code`: 88 rows, 0.0% of national detailed SOC employment
- `unmatched_our_code`: 41 rows, 7.8% of national detailed SOC employment
