# Explanation Q2 — National Job-Concentration Review

**Purpose:** Record the Epic 1 review of the completed national job-concentration
notebook before the market job-center method is revised.

**Scope:** This is method evidence, not a market ranking and not a selected
job-center rule.

## Cohort and coverage

The notebook's active 95% WAC-geometry-coverage threshold produces:

| Measure | Result |
|---|---:|
| CBSAs in the coverage reader | 925 |
| Eligible CBSAs | 868 |
| Excluded CBSAs | 57 |
| Eligible WAC tract rows | 74,781 |
| Minimum eligible WAC coverage | 95.2% |
| Median eligible WAC coverage | 100.0% |

The surface is a 2023 WAC workplace-job snapshot. RAC is retained only as
resident-worker context. The excluded cohort includes all observed Michigan and
Alaska WAC gaps, including Detroit-Warren-Dearborn and Anchorage, so those
markets must not enter the national comparison or center-method calibration.

## National concentration context

The table shows the national distribution of the notebook's market-level
concentration measures. `tract share` is the share of ranked tract rows needed
to reach the stated share of workplace jobs.

| Percentile | Tract share to 50% of jobs | Tract share to 80% of jobs | Job share in top 20% of tracts |
|---|---:|---:|---:|
| 10th | 11.5% | 34.6% | 46.2% |
| 25th | 15.2% | 39.5% | 51.6% |
| Median | 20.0% | 45.7% | 57.8% |
| 75th | 25.0% | 52.4% | 63.5% |
| 90th | 30.8% | 60.0% | 68.7% |

Richmond is more concentrated than the median eligible market: 10.9% of its
330 tracts hold 50% of its 594,430 workplace jobs, and 33.9% hold 80%. Its top
20% of tracts hold 66.5% of workplace jobs.

## Primary candidate signals for the market method

The next method iteration should prioritize the two signals chosen for Q2:

1. **Tract share of CBSA workplace jobs** identifies tracts that matter to the
   market's employment geography, rather than only clearing a count that may be
   routine in a large market.
2. **Jobs-to-resident-workers ratio** distinguishes workplace-heavy tracts from
   broadly residential tracts that happen to contain many jobs.

Neither signal is sufficient alone. A ratio can be inflated by a small resident
worker denominator, while market share can represent modest job counts in small
CBSAs. Census tracts are generally designed around roughly 4,000 residents, so
the floor is not a correction for arbitrarily sized population units; it is a
guardrail against small-count ratio artifacts. Show it visibly as a sensitivity,
not as an inherited rule.

For exploration only, a screen of at least 1% market job share, at least 1.5
jobs per resident worker, and at least 2,500 workplace jobs identifies 19
Richmond tracts containing 214,592 jobs (36.1% of the market total). These are
not selected centers; the contiguous-cluster review still determines whether
the tracts form recognizable districts.

## Contrast-market shortlist

| Market | Why it is useful | 50% job tract share | Exploratory two-signal candidates* |
|---|---|---:|---:|
| Richmond, VA (`40060`) | First local method-review market. | 10.9% | 19 |
| San Jose-Sunnyvale-Santa Clara, CA (`41940`) | Strong concentrated contrast: only 4.5% of tracts hold half of jobs, but the exploratory screen yields a similar 18 tracts. Tests whether the two-signal rule remains interpretable under high concentration. | 4.5% | 18 |
| Madison, WI (`31540`) | More diffuse, comparable-scale contrast: 15.3% of tracts hold half of jobs and the screen yields 23 tracts. Tests whether the rule fragments or over-selects in a less concentrated market. | 15.3% | 23 |

\* At least 1% market job share, at least 1.5 jobs per resident worker, and at
least 2,500 workplace jobs. This is a review screen, not a recommended cutoff.

**Recommendation:** retain Richmond as the first method-review market. Use San
Jose as the first contrast run because it is a clean concentrated counterpoint;
use Madison as a subsequent diffuse-market sensitivity run. No national result
supports promoting the exploratory 1% / 1.5 / 2,500 settings as a fixed rule.

## Handoff to the Proximity Method notebook

The market method notebook should display Richmond's concentration context and
compare independent flags for market job share, jobs-to-workers, and the
absolute-job guardrail. It should map their overlap and contiguous components,
then require a human-reviewed center/district decision before writing the
distance-to-nearest-job-center surface.
