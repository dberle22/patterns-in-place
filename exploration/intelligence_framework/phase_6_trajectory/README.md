# Phase 6 Trajectory Methodology

This folder holds the trajectory layer that sits on top of the completed Character, Livability, Opportunity, and Phase 5 cross-frame outputs.

Phase 6 asks a different question than the earlier phases:

- not just "Where does this metro rank today?"
- but "How far from the national middle is it, and which direction is it moving?"

The main goal is to surface metros that are analytically interesting for Deep Dives:

- places catching up
- places pulling farther ahead
- places slipping
- places telling conflicting stories across frames

The primary output is `outputs/phase6_candidate_list.csv`.

## Model Overview

Phase 6 combines two ideas for every frame:

- **position**: where a metro sits today relative to the `396`-CBSA national universe
- **momentum**: how much that metro moved over the last `1` or `5` years, depending on the KPI

Those two pieces are combined into a trajectory score and a direction label.

This means a metro can be interesting for different reasons:

- it is already far from the middle
- it is moving quickly
- it is moving in the "wrong" direction relative to its current position
- its three frames disagree with each other

## Universe And Inputs

The current Phase 6 model uses the same `396` non-Puerto-Rico CBSAs used in the completed frame models.

Phase 6 does not recalibrate the frame scores themselves. It uses:

- recurring annual Gold-table KPI series as the trajectory input
- published Phase 2 Character scores as current-state context
- published Phase 3 Livability scores as current-state context
- published Phase 4 Opportunity scores as current-state context
- published Phase 5 cross-frame overlap flags as candidate-list enrichment

The main input rule is:

- use recurring annual series for trajectory
- keep single-vintage or not-yet-verified series as context only

That is why some KPIs appear in Phase 6 outputs as context but do not contribute to movement scoring.

## Coverage Rules

Phase 6 carries forward a few explicit coverage policies.

### Connecticut Exclusion

All `7` Connecticut CBSAs are excluded from ACS-derived `5`-year trajectory metrics.

Those CBSAs are:

- `14860` Bridgeport-Stamford-Danbury, CT
- `25540` Hartford-West Hartford-East Hartford, CT
- `35300` New Haven, CT
- `35980` Norwich-New London-Willimantic, CT
- `39480` Putnam, CT
- `45860` Torrington, CT
- `47930` Waterbury-Shelton, CT

The exclusion is applied as missing trajectory input, not as imputed movement. Affected metros are tagged with `ct_exclusion_flag`.

### Context-Only Metrics

These KPIs are currently carried as context only because they are single-vintage or not yet verified as recurring annual series in Gold:

- `friending_bias`
- `civic_engagement_volunteering_rate`
- `civic_organizations_per_1000`
- `nonprofits_per_100k`
- `walkability_index`
- `jobs_access_45min_transit`
- `pct_population_low_income_low_access_1_10`
- `economic_connectedness`

### ZORI Annotation

`zori_annual_avg_yoy_pct` stays in the Opportunity pass, but metros with limited or annotated ZORI coverage are tagged with `zori_coverage_flag`.

## Time Windows

The model uses different windows by frame.

- Character: `5yr` only
- Livability: `5yr` only in the canonical score; `1yr` is sensitivity-only
- Opportunity: `5yr` plus `1yr`

Opportunity keeps both because short-run market turns are analytically useful even when the medium-term direction says something different.

## How The Trajectory Score Works

Phase 6 builds movement one KPI at a time, then rolls it up to the frame level.

### Step 1: Build A Current Value And A Lagged Value

For each CBSA and KPI, the pipeline finds:

- the most recent available value
- the value `1` or `5` years earlier, depending on the configured window

The raw change is:

- `change_raw = current_value - lag_value`

### Step 2: Standardize Position And Change

Within the national CBSA universe, each KPI gets:

- `position_z`: how far the current value is from the national mean
- `change_z`: how unusual the recent change is relative to other metros

This is important because a raw change of `+1` means very different things across different KPIs.

### Step 3: Align The Sign To "Higher Is Better"

Every KPI inherits its polarity from `foundations/semantic_layer/intelligence_catalog.yml`.

- positive-polarity KPI: higher is better
- negative-polarity KPI: lower is better

Phase 6 flips negative-polarity KPIs so the aligned scores are comparable:

- `aligned_position_z`
- `aligned_change_z`

After alignment:

- positive values mean "better than average" or "moving in a better direction"
- negative values mean "worse than average" or "moving in a worse direction"

### Step 4: Compute KPI-Level Trajectory Strength And Score

Each KPI gets two related outputs:

- `metric_trajectory_strength = 0.5 * abs(aligned_position_z) + 0.5 * abs(aligned_change_z)`
- `metric_trajectory_score = 0.5 * aligned_position_z + 0.5 * aligned_change_z`

Interpretation:

- **strength** measures how far from normal and how fast the KPI is moving, regardless of sign
- **score** keeps the sign, so improving and declining metros stay distinct

### Step 5: Roll Up To The Frame Level

Within each frame and window, Phase 6 averages the aligned KPI signals:

- `frame_position_z`
- `frame_momentum_z`
- `frame_trajectory_strength`
- `frame_trajectory_score = 0.5 * frame_position_z + 0.5 * frame_momentum_z`

That produces the published frame-level outputs:

- `character_trajectory_score`
- `livability_trajectory_score`
- `opportunity_trajectory_score`

## Direction Segmentation

Direction Segmentation is the simplest way to read a trajectory score.

It asks two questions:

1. Is the metro currently above or below the national middle?
2. Is it moving in a better direction or a worse direction?

That creates four buckets:

- `diverging-improving`: above average and moving further in a good direction
- `diverging-declining`: below average and moving further in a bad direction
- `converging-improving`: below average but catching up
- `converging-declining`: above average but slipping back toward the middle

A simple mental model:

- **diverging** = becoming more unusual
- **converging** = moving back toward the middle
- **improving** = moving in a better aligned direction
- **declining** = moving in a worse aligned direction

Examples:

- a weak Opportunity metro with fast job and income improvement is `converging-improving`
- a strong Livability metro getting even better is `diverging-improving`
- a weak metro getting worse is `diverging-declining`
- a strong metro losing momentum is `converging-declining`

This matters because rank alone only tells us where a place stands now. Direction segmentation tells us what kind of story the place is in.

## Opportunity Turn Signals

Opportunity is the only frame that keeps both a canonical `5yr` pass and a short-run `1yr` pass.

Phase 6 compares those two windows to detect contradictions:

- short-run improving vs. medium-term declining
- short-run declining vs. medium-term improving

Those cases are written to `outputs/phase6_opp_turn_signals.csv` and added back onto the main output as:

- `opp_turn_signal`
- `opp_turn_signal_type`

This is useful for spotting possible market turns that would be hidden in a pure `5`-year average.

## Pattern Scan

Phase 6 does not pre-rank one narrative above the others. It scans all metros for five different trajectory patterns.

### 1. Bounce Back

Definition:

- Opportunity direction is `converging-improving`
- Opportunity trajectory strength is in the national top decile
- current Opportunity percentile is `50` or below

Interpretation:

- weaker or middling places that appear to be catching up fast

### 2. Hidden Livability Winners

Definition:

- Livability direction is `diverging-improving`
- Livability trajectory strength is in the national top decile
- Phase 5 cross-frame percentile stays in a middle band: `35` to `70`

Interpretation:

- places improving on livability without already looking like nationally obvious stars

### 3. Diverging From Themselves

Definition:

- at least one frame is improving
- at least one frame is declining
- cross-frame trajectory disagreement is in the national top decile

Interpretation:

- the metro is telling conflicting stories internally

### 4. Fast Demographic Changers

Definition:

- Character trajectory strength is in the national top decile

Interpretation:

- population mix, migration, density, or educational composition is moving unusually fast

### 5. Environmental Risk Outliers

Definition:

- Livability direction is `diverging-declining`
- worsening in both `aqi_unhealthy_days` and `fema_risk_score` is in the national top decile

Interpretation:

- places with unusually bad environmental movement on both air-quality and hazard-risk dimensions

## Default Thresholds

The current published Phase 6 defaults use top-decile national cutoffs rather than hard-coded z-score thresholds.

- pattern thresholds use the `90th` percentile
- candidate scoring gives equal weight to each pattern
- Phase 5 overlap gets a smaller bonus rather than dominating the list

These defaults were chosen to keep the scan broad enough to surface different kinds of trajectory stories without turning the result into a one-pattern ranking.

## How Changing The Defaults Would Affect Results

This is one of the most important review points in Phase 6.

### If Pattern Thresholds Get Stricter

If the cutoff moves above the `90th` percentile:

- fewer metros qualify for each pattern
- the list concentrates around the most extreme outliers
- candidate ranks become more driven by a smaller number of large metros and unusual edge cases

### If Pattern Thresholds Get Looser

If the cutoff moves below the `90th` percentile:

- more metros qualify
- pattern counts rise quickly
- the candidate list becomes less selective and more sensitive to tie-breaking

### If One Pattern Gets More Weight

If one pattern receives more weight than the others:

- the candidate list becomes more narrative-specific
- metros matching that one story move up quickly
- the top of the list becomes less balanced across the five review surfaces

### If The Phase 5 Overlap Bonus Changes

- increasing the bonus favors metros that were already highly contradictory in the cross-frame position model
- decreasing the bonus favors pure trajectory movement, even if the Phase 5 profile was less unusual

## Candidate Scoring

The Phase 6 candidate list is not a generic "best metros" ranking.

It is a review-prioritization score built to answer:

- which metros are moving in analytically interesting ways
- which metros deserve a deeper read because the frame stories disagree
- which metros combine Phase 6 movement with Phase 5 cross-frame contradiction

The current logic is:

- each of the five patterns contributes `20` points if flagged
- that pattern total is multiplied by `(0.5 + overall_trajectory_strength_pct)`
- then a smaller Phase 5 overlap bonus is added: `15 * phase5_overlap_pct`

This produces:

- `pattern_signal_score`
- `overall_trajectory_strength`
- `candidate_score`
- `candidate_rank`

Use this output as a prioritization surface for review, not as a universal market ranking.

## Outputs

- `outputs/trajectory_scores.parquet`
  One row per CBSA with frame trajectory scores, directions, pattern flags, candidate score context, and annotations.
- `outputs/phase6_kpi_trajectory_long.csv`
  Long-format KPI-level trajectory output for interpretation and notebook review.
- `outputs/phase6_opp_turn_signals.csv`
  Opportunity `1yr` vs `5yr` contradiction scan.
- `outputs/phase6_pattern_summary.csv`
  Pattern counts, top examples, and sensitivity notes.
- `outputs/phase6_candidate_list.csv`
  Ranked Phase 6 candidate list.

## Structure

- `R/phase6_config.R`
  Defines metric eligibility, coverage rules, time windows, and file paths.
- `R/phase6_frame_build.R`
  Builds the long annual KPI series from DuckDB and applies coverage rules.
- `R/phase6_trajectory_core.R`
  Computes KPI-level and frame-level movement, position, strength, and direction outputs.
- `R/phase6_opportunity_turn_signals.R`
  Computes the short-run vs medium-term Opportunity contradiction scan.
- `R/phase6_patterns.R`
  Applies the five pattern filters and writes the summary output.
- `R/phase6_candidate_list.R`
  Joins Phase 5 overlap context and computes the ranked candidate list.
- `R/run_phase6_trajectory.R`
  Canonical runner for the full Phase 6 build.
- `notebooks/`
  Focused review notebooks that read `outputs/` only.

## Canonical Run Order

1. Run `R/run_phase6_trajectory.R`
2. Review outputs in `outputs/`
3. Render the notebooks when you want visual or narrative review

The notebooks are review surfaces only. They should not query Gold tables directly or rebuild the pipeline logic.
