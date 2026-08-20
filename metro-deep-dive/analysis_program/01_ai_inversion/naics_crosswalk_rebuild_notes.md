# NAICS Crosswalk Rebuild Notes

This note summarizes what we built in [naics_crosswalk_rebuild.ipynb](/Users/danberle/Documents/projects/patterns_in_place/metro-deep-dive/analysis_program/01_ai_inversion/naics_crosswalk_rebuild.ipynb) and how it should fit into the broader AI inversion workflow.

## Purpose

The goal of this notebook is to keep the `NAICS` crosswalk setup separate from the downstream analysis notebook.

That separation helps us:

- rebuild and review the Felten `Appendix B` join in one place
- keep the review logic easy to inspect
- produce one canonical NAICS join table for downstream use
- avoid mixing crosswalk-governance work with the actual AI inversion analysis

## Workflow We Built

The notebook follows a simple staged process.

### 1. Raw Appendix B Baseline

We start by loading the raw Felten `Appendix B` data and the live yearly 4-digit `NAICS` surface from QCEW.

At this stage we measure:

- exact raw code matches
- raw matches after a small explicit normalization map for known code-vintage and aggregate-code differences

This gives us a transparent baseline before we apply any reviewed decisions.

### 2. Accepted Suggested Joins

We then load the accepted rows from `recommended_felten_naics_overrides_initial.csv`.

These are treated as a distinct review layer, not as part of the raw source.

That means we can clearly separate:

- what matched on its own
- what required a reviewed suggested join

### 3. Combined Review Base

Next we combine:

- raw matched rows
- accepted suggested joins

into one notebook-owned review dataframe:

- `naics_step4_review_base`

This gives us one row per live `NAICS` code and becomes the base for manual review.

We also export this intermediate table for easier inspection:

- `outputs/naics_crosswalk_step4_review_base.csv`

### 4. Manual Review

We built a simple manual review helper that lets us inspect:

- the target live `NAICS` code
- nearby live codes in the same family
- nearby Felten `Appendix B` rows in the same family

We also created a notebook-owned manual lock table:

- `naics_notebook_locked_overrides`

This is where final notebook review decisions live.

### 5. Final Canonical NAICS Join Table

Finally we combine:

- the step 4 review base
- the notebook manual locks

and resolve the final selected Felten code back to `Appendix B`.

That produces the canonical final dataframe:

- `naics_felten_join_reference`

and the exported artifact:

- `outputs/naics_felten_join_reference.csv`

## Final Coverage Outcome

After the notebook manual locks were applied, the rebuilt NAICS crosswalk landed at very high weighted coverage.

Current remaining latest-year unresolved codes are:

- `8141` Private households
- `9999` Unclassified
- `3321` Forging and stamping
- `4572` Fuel dealers
- `1142` Hunting and trapping

These appear to be the true residual unmatched concepts rather than notebook wiring problems.

## How This Should Fit With The Main Analysis

The main [ai_inversion.ipynb](/Users/danberle/Documents/projects/patterns_in_place/metro-deep-dive/analysis_program/01_ai_inversion/ai_inversion.ipynb) notebook should focus on analysis, not crosswalk setup.

The intended structure going forward is:

- one notebook for NAICS crosswalk setup and review
- one notebook for SOC crosswalk setup and review
- one main AI inversion notebook that reads the final canonical crosswalk outputs and focuses on analysis

## Next Step

We should build a parallel SOC notebook using the same philosophy as this NAICS notebook, while reusing the validated logic already developed in [ai_inversion.ipynb](/Users/danberle/Documents/projects/patterns_in_place/metro-deep-dive/analysis_program/01_ai_inversion/ai_inversion.ipynb).

That SOC notebook should:

- isolate the SOC crosswalk build and review process
- preserve the raw bridge, accepted decisions, and notebook locks as separate stages
- output one canonical final SOC join table for the main analysis notebook
