# Position Candidate Scan — Epic 3 Review

**Status:** Quantitative review complete; interactive analyst review pending  
**Reviewed:** 2026-09-08  
**Method:** `candidate_scan_v1` with `trajectory_pilot_v1`

## Run result

The Marimo notebook completed a headless run against the live DuckDB marts.
The current Profile universe has 396 markets; 390 have eligible five-year
coverage for all three frames and receive a rank. The six unranked markets are
the Connecticut CBSAs with `insufficient_evidence` across all three frames.
They are correctly visible as coverage exceptions rather than assigned a zero
score.

## Legacy comparison

The legacy CSV and v1 share the same 396 CBSA codes. Among the 390 eligible
v1 markets, rank correlation is 0.731 and median absolute rank movement is 40
places. That is a substantive method update, as intended: v1 removes the
retired Phase 6 pattern calculations and uses only current stored divergence,
salience, and turn evidence.

Large movements are therefore not by themselves a defect. They require an
analyst to decide whether the current evidence is a better market-selection
signal than the old pattern-oriented list.

## Required market checks

| Market | v1 rank | Legacy rank | v1 score | Read |
|---|---:|---:|---:|---|
| Jacksonville, FL | 12 | 77 | 74.8 | High divergence percentile (91.9) and strong mean trajectory salience (74.4) move it into the initial review set despite `no_turn_signal`. |
| Richmond, VA | 378 | 373 | 17.7 | Low divergence percentile (4.8) and modest mean trajectory salience (34.6) keep it low under both methods. This is a stable result, not a coverage problem. |

The v1 top five are Moses Lake, WA; Wheeling, WV-OH; Pittsfield, MA;
Eureka-Arcata, CA; and Fond du Lac, WI. The top 20 average 87.6 on divergence
and 77.1 on trajectory salience. Two have `confirmed_turn` and two have
`emerging_turn_watch`, so the top is not being mechanically driven by the
turn component.

## Material rank movers to inspect

| Direction | Example markets | Interpretation to review |
|---|---|---|
| Rise under v1 | Bloomington, IL (394 → 64); Jacksonville, NC (391 → 78); Pittsfield, MA (172 → 3) | These markets gain because current stored salience and/or divergence now count directly, rather than requiring a legacy pattern flag. |
| Fall under v1 | Stockton-Lodi, CA (12 → 356); Washington, DC region (53 → 387); San Francisco, CA (10 → 341) | These cases were favored by the retired Phase 6 formula but have low current cross-frame divergence and only moderate or low current salience. |

## Sensitivity

| Scenario | Median absolute rank movement | Largest movement | Read |
|---|---:|---:|---|
| Divergence-heavy (60/30/10) | 17.0 | 97 | The ranking reacts meaningfully to placing more emphasis on cross-frame contrast. |
| Trajectory-heavy (30/60/10) | 22.5 | 135 | This is the largest sensitivity: some markets are driven primarily by stored trajectory salience. |
| No-turn-bonus (50/50/0) | 3.0 | 80 | The turn contribution has limited typical influence but can affect a small set of tied or near-tied markets. |

The default 45/45/10 split remains defensible for the first interactive
review. No weight change is recommended from this quantitative pass alone.

## QA outcome

- 396 Profile rows and no duplicate CBSA codes
- 390 eligible ranks, with no score missing among eligible markets
- no rank assigned to an ineligible market
- no duplicate eligible rank
- all current CBSA codes match a legacy comparison row

## Interactive review requested

In the notebook, review Richmond, Jacksonville, and at least three of the
material movers above. Decide whether the v1 top list surfaces markets worth
the next analyst look, rather than merely markets with extreme components.
In particular, decide whether the default balance should favor divergence or
trajectory more strongly. Record a change only if a concrete editorial failure
appears; otherwise retain `candidate_scan_v1` for Epic 4.
