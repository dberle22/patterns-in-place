# A1 — The AI Inversion: Analysis Plan

**Version:** V3  
**Updated:** 2026-08-20

## V3 Change Log

This spec was updated after the first full H1-H3 notebook build and a review pass on the resulting visuals and interpretations.

### What we learned in the first analysis pass

1. **The descriptive baseline is now analytically useful, not just setup.**  
   The national SOC decomposition views are already helping separate employment share, payroll share, and contribution to the national index. The next task is to make those relationships easier to compare in one visual sequence.

2. **H1 currently looks more falsified than supported.**  
   The observed metro rank correlation is extremely high, and the rank-shift distribution appears broad and roughly normal rather than driven by a few extreme movers. That does not make the payroll measure useless, but it does weaken the original H1 claim that the ranking changes substantially.

3. **H2 currently looks weaker as a falsification target than planned.**  
   The notebook now shows a clear positive relationship between `pct_ba_plus` and metro exposure. The likely interpretation is not that attainment is the wrong variable, but that it is a useful proxy that still leaves meaningful residual variation once industry and occupation structure are examined.

4. **H2 needs an occupation-side comparison, not just industry mix.**  
   Because the broader argument is about occupational structure, the H2 section should compare attainment against both industry composition and broad occupation composition before we settle the framing.

5. **H3 is promising, but the metric needs to be made more legible.**  
   The current concentration outputs are interesting enough to keep, but the notebook needs to explain the HHI construction clearly, restate that the concentration measure is computed within exposure bins rather than only at the top of the metro distribution, and improve the sensitivity visual so it is easier to interpret.

6. **The next task is interpretation and framing, not new data engineering.**  
   The immediate need is to tighten concepts, visual sequence, and section-level conclusions so Parts 4 and 5 can be built from stable findings rather than from half-settled charts.

## V2 Change Log

This spec was updated after building the dedicated SOC and NAICS crosswalk notebooks and rebuilding the main analysis notebook around those cleaned outputs.

### What we learned in development

1. **The SOC denominator needed to be stated more carefully.**  
   Our final SOC Felten coverage is measured against the published **detailed SOC** employment surface, not against OEWS all-occupation totals. The two are not the same denominator.

2. **OEWS total occupation rows are larger than the detailed SOC sum.**  
   In the live `2025` OEWS CBSA data, published detailed SOC rows account for about `97%` of all-occupation employment. That difference is an OEWS publication/suppression issue, not a Felten crosswalk failure.

3. **The notebook now has a clean upstream/downstream split.**  
   Crosswalk construction and manual review live in `soc_crosswalk_rebuild.ipynb` and `naics_crosswalk_rebuild.ipynb`. The main AI inversion notebook should start from the canonical cleaned outputs rather than rebuilding crosswalk logic in place.

4. **SOC is the primary exposure measure, but NAICS remains analytically important.**  
   Occupation exposure is the main inversion measure because Felten Appendix A maps directly to detailed SOC employment. NAICS is still valuable as a secondary comparison lens on industry structure and sector-level exposure, but it is not the primary inversion index.

5. **The live runnable metro universe must be described explicitly.**  
   The intended national frame is all CBSAs, but the current live `silver.bls_oews` `2025` analysis universe is `393` CBSAs. The notebook and the writeup should name the runnable universe clearly rather than silently inheriting the broader conceptual one.

6. **Public-sector employment should remain in the primary SOC measure.**  
   Felten is an occupation exposure measure, not a private-industry-only measure. The main SOC exposure analysis should therefore use all published detailed OEWS occupations, including public-sector workers.

7. **The first notebook cleanup task is now explicit.**  
   Before building H1 and the rest of the analysis, the main notebook must patch the SOC coverage block so `coverage_share` uses the published detailed-SOC denominator only, while the detailed-vs-total OEWS share is preserved as a separate QA field.

**Structure:** data setup → hypotheses → methods and visuals per hypothesis → market application → limitations.

**Immediate notebook cleanup before further build:** patch the SOC coverage logic in the analysis notebook so the primary SOC coverage denominator is total published detailed SOC employment, not OEWS all-occupation totals.

**What this notebook is.** An internal thinking tool. Its job is to establish whether the data holds up, resolve the open methodological decisions empirically rather than by guess, and produce a durable set of artifacts the article gets written from. It is not a deliverable and nobody reads it but you.

**What that changes.** Visuals are fast and disposable — matplotlib defaults, no chart engine, no styling. Build more exhibits rather than better ones; the ones that survive get rebuilt properly at article time. Prose in the notebook is for your own clarity, not for a reader. Anything that's a *presentation* decision (percentile vs. raw index, quadrant names, which chart leads) is deferred to the article and marked as such below.

**How to use this.** Fill the blanks before writing code. Items marked **[settled]** were decided in planning — don't relitigate. Items marked **[article]** are explicitly not notebook decisions.

---

# Part 1 — Data setup

*Nothing in this part tests a hypothesis. It establishes the measure and shows what the data looks like, so a reader can evaluate the hypotheses that follow.*

## 1.1 What the analysis is built from

| Input | Source | Grain | Role |
|---|---|---|---|
| Employment and wages by occupation | `silver.bls_oews` | CBSA × detailed SOC | Weights |
| AI exposure score | Felten et al. (2021) Appendix A | 6-digit SOC | The exposure attribute |
| Industry employment shares | `gold.economics_industry_wide` (QCEW) | CBSA | Comparison variable |
| Secondary industry exposure measure | cleaned Appendix B join + county-rolled QCEW 4-digit NAICS | CBSA × 4-digit NAICS | Comparison variable / structural cross-check |
| Educational attainment | `population_demographics` (ACS) | CBSA | Comparison variable |
| Peer set | D5 peer bundle | CBSA | Market context |

**Universe:** intended national CBSA universe; current live runnable OEWS occupation universe is `393` CBSAs in `2025`. **Case market:** Richmond, VA.

**[settled]** No NAICS↔SOC crosswalk is required. Occupation data and industry data are joined at the metro level; the CBSA is the key.

**[settled]** The primary SOC exposure measure includes all published detailed OEWS occupations, including public-sector workers.

**Binding dependency:** OEWS wages at detailed SOC. If unavailable, H1 cannot be tested.
- Confirmed available? ________________

### 1.1.1 Notebook-ready inputs and remaining gaps

The main notebook now effectively has most of the build inputs already loaded or derivable in-place.

**Available now in the notebook**
- canonical SOC Felten join
- canonical NAICS Felten join
- detailed SOC CBSA employment and local wages
- detailed NAICS CBSA employment
- metro-level SOC exposure objects: `E_m`, `W_m_local`, coverage, payroll coverage
- metro-level NAICS exposure objects
- metro-wide comparison panel fields already merged into `metro_analysis_base`
- national decomposition-ready SOC and NAICS detail frames

**Still needs confirmation / cleanup before H2**
- primary CBSA attainment field is now `pct_ba_plus`
- decide whether to keep `pct_ba_plus` as the only attainment cut or add a secondary attainment robustness field
- add a broad occupation-composition comparison alongside the current industry-composition comparison

**Still needs explicit construction before H3**
- tighten the HHI explanation and notation in the notebook
- confirm whether top-quartile exposed occupations remains the preferred exposed set
- improve the major-group sensitivity visual so it is interpretable at a glance

## 1.1.2 Proposed notebook structure from here

The remaining notebook should read like one argument, not three disconnected analyses.

1. Part 1 Descriptive Baseline
2. H1 Wage-weighted vs employment-weighted exposure
3. H2 Exposure, attainment, and industry mix
4. H3 Exposure level versus exposure shape
5. Richmond / market interpretation hooks
6. Limitations and unresolved sign-of-impact questions

**Build rule:** each section should have:
- one prep cell that builds shared objects
- one metrics / summary cell
- one or two visual cells
- one residual / mover / decomposition cell if needed
- one short markdown takeaway cell once the section stabilizes

## 1.1.3 Immediate notebook refactor plan

The first-pass Marimo conversion is useful, but it still carries too much Jupyter structure and too much build logic inside the notebook. Before adding more analysis, the next cleanup pass should make the notebook more explicitly Marimo-native and move recurring QA into reusable builders.

### A. Presentation refactor inside the notebook

**Goal:** use Marimo's native interaction model instead of Jupyter-style display patterns.

1. Replace remaining Jupyter-style table presentation with Marimo-native viewers.
   - Use `mo.ui.dataframe(...)` for large exploratory tables and full analytical surfaces.
   - Use `mo.ui.table(...)` for compact summary tables, QA summaries, and small ranked exhibits.

2. Remove unnecessary preview-only displays.
   - The Felten load cell does not need to show raw tables by default.
   - Large surfaces like detailed SOC and NAICS CBSA rows should be shown as interactive dataframes rather than `.head(...)` slices.

3. Split visuals into one chart per cell where practical.
   - The descriptive baseline should not bundle multiple charts in one output cell.
   - H1 should keep separate cells for metrics, scatter, rank-shift distribution, and mover/QA tables.

4. Keep narrative order explicit.
   - Build objects first.
   - Show the headline metric or summary second.
   - Show the visual third.
   - Keep raw ranked tables and residual reference tables at the end of a section.

### B. Structural refactor of the build logic

**Goal:** separate "construct the data" from "inspect and interpret the data."

1. Split the metro exposure build into clearer units.
   - SOC build cell
   - NAICS build cell
   - comparison-base assembly cell

2. Keep the conceptual distinction explicit:
   - **Metro exposure tables** are the scored metro-year analytical products built directly from detailed SOC and NAICS surfaces.
   - **Comparison base** is the latest-row merged panel used for H2, H3, and broader interpretation.

3. Defer historical SOC expansion unless it becomes necessary for a real analytical question.
   - Current default: latest-year cross-sectional analysis
   - Historical SOC exposure: optional later extension, not a prerequisite for cleaning up H1

### C. Visual priority changes

**Goal:** elevate the most interpretable national decomposition views.

1. Promote national SOC major-group decomposition as the primary broad decomposition view.
   - Preferred visuals:
     - side-by-side horizontal bars for employment-weighted vs payroll-weighted contribution
     - stacked bars for employment share vs payroll share
     - slope chart if we want to emphasize which groups gain weight under payroll weighting
   - Do **not** use pie charts as the primary chart type.

2. Keep detailed occupation decomposition available, but treat it as a drill-down layer rather than the lead graphic.

3. Reframe industry decomposition as secondary.
   - Industry groups can remain as a comparison lens.
   - Broad SOC occupation groups should carry the main interpretive story.

### D. H1 interpretation and QA clarifications

**Goal:** make the H1 result easier to trust and easier to explain.

1. State the rank-correlation method clearly in the notebook.
   - H1 Spearman is computed on the metro rank vectors for `E_m` and `W_m_local`.
   - Because both measures come from the same underlying occupational structure, a high rank correlation is plausible even when rank shifts are analytically meaningful.

2. Keep the rank-shift histogram as a core H1 exhibit.
   - If the distribution remains roughly normal, that supports the interpretation that H1 is about broad reshuffling rather than a handful of extreme outliers.

3. Downgrade the current in-notebook coverage QA from a "result" to a lightweight check.
   - The current H1 coverage QA is useful as a quick read, but it is not strong enough to be the primary validation layer.

### E. Builder-script direction

**Goal:** keep the notebook focused on analysis and presentation, not data construction QA.

1. Add a reusable builder script that materializes the main derived analysis tables.
   - metro SOC exposure table
   - metro NAICS exposure table
   - latest-row comparison base
   - standard QA summary tables

2. Move repetitive QA into the builder layer.
   - coverage checks
   - row-count and merge diagnostics
   - matched-employment and matched-payroll summaries
   - any threshold flags we decide to keep

3. Keep the notebook responsible for:
   - descriptive baseline
   - H1, H2, and H3 sections
   - national decomposition exhibits
   - interpretation notes and section takeaways

### F. Next implementation order

1. Finish the Marimo-native presentation cleanup.
2. Split remaining multi-chart baseline cells into one-visual cells.
3. Strengthen the national SOC-group decomposition visuals.
4. Define the builder-script outputs and move recurring QA there.
5. Only then resume deeper H2 and H3 buildout.

## 1.2 What has to be true before any number means anything

Two upstream problems can invalidate everything downstream without announcing themselves.

**SOC vintage.** Felten's scores are built on one SOC vintage; OEWS may be on another.
- Felten basis: `2010 SOC` with a managed `2010 ↔ 2018` bridge carried into the notebook rebuild
- OEWS basis: live `2018 SOC` detailed rows in `silver.bls_oews`
- Crosswalk needed: yes, and now governed through the canonical cleaned SOC output
- Rule for splits: where one `2010` Felten occupation maps to multiple `2018` occupations, carry the scored Felten row forward to the linked `2018` rows
- Rule for merges: where one `2018` occupation points back to multiple `2010` Felten candidates, resolve in the rebuild notebook and keep the selected mapping in the canonical output

**Suppression.** OEWS suppresses cells at CBSA × detailed SOC, wages more than employment. Because exposure is a weighted average over matched rows, suppression can bias the result, not just add noise.
- Coverage measures:
  - primary: share of **published detailed SOC employment** in matched, scored rows
  - secondary QA: share of **all-occupation OEWS employment** represented by published detailed SOC rows
- Immediate implementation note: the rebuilt main notebook must patch its current SOC coverage block to reflect this denominator split before H1 is treated as final
- Threshold: _______ · Below-threshold behavior: flag / drop: _______

> **Both of these get published as methods stats, not kept as internal diagnostics.** A reader who can see your coverage numbers will trust the rest; one who can't, shouldn't.

## 1.3 Constructing the exposure measure

**Employment-weighted** — how much of a metro's *job count* sits in exposed work:

```
E_m = Σ_o (emp_mo / emp_m) × AIOE_o
```

**Wage-weighted** — how much of a metro's *wage bill* sits in exposed work:

```
W_m = Σ_o (emp_mo × wage_mo / payroll_m) × AIOE_o
```

Wage source decision:
- [x] Local wages — captures composition *and* the local wage premium
- [ ] National wages by occupation — isolates composition alone
- [ ] Both, treating the difference as its own result only if we later decide the local wage premium is itself part of the story

> **Current working decision:** use local wages in the main notebook.  
> **Reason:** the question in H1 is whether a metro's exposed *payroll* footprint differs from its exposed *job-count* footprint. Local wages are the right primary choice for that because they reflect the actual wage bill inside that metro.  
> **What the alternative would mean:** national wages would be a composition-only counterfactual, useful only as a later robustness check if we want to strip out local wage premia.

**Interpretation guardrail [settled]:** AIOE is standardized to mean zero across occupations. `E_m` is a *relative position*, not a share of jobs at risk. This matters in the notebook for a reason beyond labeling — a mean-zero score means `E_m` can be negative, so any ratio, growth rate, or multiplicative operation on it is meaningless. Watch for that in the code.

- Reporting form (raw index vs. percentile rank): **[article]** — compute both, decide later

## 1.4 The descriptive baseline

Where the 401 metros actually sit, before any claim is made.

| Exhibit | What it establishes |
|---|---|
| Distribution of `E_m`, Richmond marked | The range, and whether it's tight or sprawling |
| Ranked bar, top and bottom _______ | Who the poles are |
| Choropleth | Whether the pattern is regional or scattered |
| Richmond decomposition: `share_o × AIOE_o` ranked | Which occupations put this market where it is |
| Secondary NAICS comparison cut | Whether industry-structure exposure tells a similar or different metro story than the occupation measure |

> **Prompt:** Write the two-sentence description of this distribution. Is exposure concentrated in a few metros or broadly shared? That answer shapes how much the hypotheses can carry.

### 1.4.1 What the descriptive baseline needs to establish

The baseline is not just scene-setting. It should lock down three facts that the rest of the notebook builds on:

1. **Exposure is geographically uneven.**
   Some metros and regions are structurally much more exposed than others; AI impact will not be evenly shared across places.

2. **Payroll exposure is systematically higher than headcount exposure.**
   The exposed wage bill runs above the exposed job share in most metros, which implies AI exposure is tilted toward higher-wage work.

3. **The sign of "impact" is still unresolved.**
   Felten gives us *where impact concentrates*, not yet whether that impact is net-positive or net-negative for wages, job counts, or local political response.

### 1.4.2 Baseline visuals that should survive

| Visual | Question it answers | Keep / build status |
|---|---|---|
| Histogram / density of `E_m` and `W_m_local` | How wide is the national distribution? | keep |
| `E_m` vs `W_m_local` scatter | Does payroll exposure systematically run above headcount exposure? | keep |
| Rank-shift histogram | How much does the payroll ranking really move? | keep |
| National occupation decomposition table | Which detailed occupations carry the exposure index? | keep |
| National SOC major-group decomposition chart | Which broad occupation families carry the index? | keep |
| National industry weight vs score scatter | Which industries are large, and which are high- or low-score outliers? | secondary comparison |
| Choropleth or regional map | Are the winners and losers regional rather than random? | build later if needed |

### 1.4.3 Post-build review notes and next visual steps

**Descriptive baseline**
- Rebuild the national SOC employment-vs-payroll-share comparison as a `100%` stacked bar chart with `soc_major_group_label` as the fill.
- Add a notebook explainer that distinguishes:
  - `national_employment_share` / `national_payroll_share`
  - `contribution_to_national_e` / `contribution_to_national_w_local`
  - `employment_weighted_felten_score` / `payroll_weighted_felten_score`
- Keep the national contribution chart, but clarify that it is showing which broad occupation groups contribute most to the aggregate exposure index, not a causal statement about the effect of AI on wages.
- Test a combined national SOC chart that overlays group-level weighted Felten scores on top of the employment-share vs payroll-share comparison, likely using a second axis.
- Simplify the national NAICS comparison to `2-digit` NAICS groups for readability.
- Add a comparison frame that helps translate between SOC major groups and `2-digit` NAICS groups, even if the first pass is just conceptual rather than a strict crosswalk.

**H1**
- Treat H1 as provisionally falsified unless a stronger non-rank-based interpretation survives.
- Keep the payroll-weighted measure because it still matters descriptively, even if it does not reorder metros much.
- Preserve the `45°` line and fitted regression in the `E_m` vs `W_m_local` scatter because both are useful for quick interpretation.

**H2**
- Add a second composition pass using broad occupation groups, not just industry shares.
- Keep the current framing open: attainment now looks like a solid but incomplete proxy, not obviously the wrong variable.
- Add notebook-side explanations for:
  - `VIF` as a multicollinearity check on how redundant the predictors are with one another
  - residual tables as the ranking of metros whose observed exposure is above or below what a simpler model would predict
- Do not add regional interactions or broader confounder stacks yet unless the occupation-side comparison still leaves a major unresolved question.

**H3**
- Make the HHI definition explicit: sum of squared exposed-employment shares within the selected exposed occupation set for each metro.
- State clearly that the current notebook is not restricted to the top `10%` of CBSAs; the concentration measure is computed for the metro universe and then compared within `E_m` bins.
- Rework the detailed-vs-major-group sensitivity chart so it shows the relationship more clearly than the current top-left-cluster view.
- Keep the weak-negative-correlation interpretation provisional until the concentration definition and sensitivity framing are stable.

---

# Part 2 — Hypotheses

*Three claims, stated so they could be wrong. Thresholds are set here, before results exist.*

## H1 — The wage bill tells a different story than the job count

> Metros with the same share of *jobs* in exposed occupations differ substantially in the share of *payroll* in exposed occupations, and the gap runs systematically toward knowledge-economy metros.

**Why it matters:** payroll is what drives local tax base, consumer spending, and housing demand. A metro can look mid-pack on headcount exposure and be highly exposed in the terms that actually move its economy.

**Falsified if:** rank ordering is essentially unchanged between the two measures — Spearman ρ ≥ 0.90 **and** mean absolute rank shift < 10 of 401 positions.

## H2 — Educational attainment is the wrong variable

> Most variation in metro exposure occurs *between metros with similar attainment*, and attainment adds little once industry composition is accounted for.

**Why it matters:** nearly all public commentary organizes AI exposure around college share. If attainment is a proxy standing in for industry structure, that framing points at the wrong thing — and two metros with identical degree rates can face different structural risk.

**Falsified if:** η² ≥ 0.30 across attainment tiers, **or** partial R² for attainment over the industry-mix model ≥ 0.25.

**Interpretive extension:** even if higher-attainment metros are more exposed, that does not mean the local political or social experience will track the earnings upside. One working question for H2 is whether the public conversation overstates "college share" while understating the role of occupational and industry composition.

## H3 — Shape distinguishes metros that levels group together

**Reframed working question.** Two metros can land at similar headline exposure levels for different structural reasons. One can have exposure spread across many moderately exposed occupations; another can get to the same headline level because a smaller set of highly exposed occupations carries much more of the load.

The underlying thing we are trying to learn is:

> **Among metros with similar overall `E_m`, is the exposed footprint diffuse or concentrated?**

That matters because equal headline exposure may imply different kinds of local economic vulnerability:
- a **diffuse** footprint suggests AI exposure is embedded broadly across the labor market
- a **concentrated** footprint suggests the metro is more dependent on a narrower exposed occupational base

**[settled]** Keep H3 as a real hypothesis and test whether similarly exposed metros differ in how concentrated that exposure is across occupations.

**Working claim:** *Among metros with similar headline `E_m`, the exposed footprint can be either diffuse or concentrated, and that concentration varies enough to distinguish structurally different labor-market profiles.*

**Working falsification rule:** if concentration is roughly constant within headline-exposure groups, H3 fails and should be treated as descriptive framing rather than a substantive result.

**Interpretive extension:** H3 is the bridge to the unresolved sign question. If two metros have similar exposure levels but different exposure shape, then the downstream consequences of the same Felten score may plausibly differ depending on whether impact lands in a narrow high-wage occupational core or across a broad labor-market base.

## 2.1 Working synthesis across H1-H3

The three hypotheses now read better as one layered argument than as three disconnected tests.

1. **H1 establishes the economic-weight layer.**  
   The metro employment exposure map and the metro payroll exposure map are very closely aligned, but the payroll view amplifies the same geography. That means highly exposed metros are not just places with exposed jobs; they are also places where exposed payroll is economically important. If AI impact is positive, that can intensify upside in already high-exposure places. If AI impact is negative, the same places may face magnified downside because exposed payroll is concentrated there too.

2. **H2 establishes the proxy-versus-structure layer.**  
   Educational attainment is a meaningful proxy for metro exposure, but it is not a complete explanation. The notebook now points toward a more useful framing than "education is wrong": higher-attainment metros are often more exposed, but industry and occupation structure still explain why similarly educated places can differ.

3. **H3 establishes the shape layer.**  
   Even when two metros land near one another on headline exposure, the internal structure of that exposure may differ. The notebook does not yet show a strong, simple concentration pattern across metros, but it does justify looking more closely at whether exposure is broad or narrow inside specific markets rather than making blanket statements from the headline index alone.

**Working cross-hypothesis takeaway:** AI exposure has at least three distinct dimensions that matter for metro interpretation:
- **level** — how exposed a place is overall
- **economic weight** — how much of that exposure sits in payroll rather than just job count
- **structure** — how that exposure is distributed across industries and occupations

That is the bridge into Richmond. The question is not just whether Richmond is exposed, but what kind of exposure it has, how economically important that exposure is, and how it is structured relative to peers.

---

# Part 3 — Testing the hypotheses

## 3.1 Testing H1

**Method**
- Compute `E_m` and `W_m` for all 401 CBSAs
- Rank both; compute Spearman ρ and mean absolute rank shift
- Compare against threshold

**Exhibits** — scatter of `E_m` vs. `W_m` with a 45° line; histogram of rank shifts; the top and bottom 20 movers as a plain table.

**Implementation note:** the reported Spearman statistic is the rank correlation between the metro `E_m` ordering and the metro `W_m_local` ordering. A high value does not mean the two measures are identical; it means the wage-weighted view mostly preserves the same broad ordering while still allowing meaningful reshuffling within it.

> **Prompt:** Before running it, name three metros you expect to rise most on the payroll measure, and why. A prediction you got wrong is informative. No prediction at all isn't.

**Sanity check:** if the biggest movers are small metros with thin OEWS coverage, the wage field is driving noise rather than signal. Cross-reference the movers against the §1.2 coverage numbers before believing anything. Long term, that check should live in the builder-layer QA rather than as a notebook-only artifact.

**What you conclude either way** — one line each, for your own record:
- If supported: ________________
- If falsified: the payroll-weighted measure adds descriptive nuance, but the broad metro ordering is too stable for H1 to stand as a strong inversion claim; wages mostly amplify the same geography rather than overturning it. ________________

## 3.2 Testing H2

**Method — two passes, deliberately**

*Pass 1: variance decomposition.* Bin metros by attainment; split total variation in `E_m` into between-tier and within-tier. Report η².
- Bins: attainment quartiles · Robustness bins: attainment quintiles
- **[settled]** Do not report the F-test. At n = 401 group means differ significantly regardless; the p-value carries no information.

*Pass 2: partial R².* **[settled]** Industry mix first, attainment second.
- Model A: `E_m ~` industry shares. Model B: Model A `+` attainment.
- Report partial R² = (R²_B − R²_A) / (1 − R²_A)
- Diagnostics: VIF, adjusted R², F-test on the single added coefficient
- Weighting: unweighted primary, population-weighted as robustness

*Residuals.* Fit `E_m ~` attainment alone; rank residuals; table the top and bottom `20` metros.

**Exhibits** — strip plot of exposure by attainment tier (the one that shows you the answer before the statistics do); attainment vs. exposure scatter with fit line and residuals labeled; residual tables.

**Notebook inputs required**
- `E_m` at the metro level
- primary CBSA attainment field: `pct_ba_plus`
- metro-level industry composition fields from `gold.economics_industry_wide`
- metro-level broad occupation composition fields from `gold.economics_occupation_wide`
- optional population field for robustness weighting

**Preferred section flow**
1. confirm attainment field and missingness
2. simple attainment vs exposure scatter
3. tiered strip / box plot
4. η² summary
5. industry-first regression comparison
6. residual tables and Richmond / peer interpretation

> **Prompt:** Model A fits well by construction — industry mix determines occupation mix determines exposure. Write the two sentences explaining why that doesn't make the finding circular. If you can't, the whole section is in trouble and better to know now.

**Sanity check:** the residual tables are the best error-detector in the notebook. If a metro shows up as wildly over-exposed and you can't explain why from its occupation decomposition, that's a data problem, not a finding.

**What you conclude either way:**
- If attainment is redundant: ________________
- If attainment survives: attainment is a meaningful proxy for metro exposure, but it still leaves residual variation that composition-based views help explain, especially once we compare metros with similar BA+ shares but different industry and occupation mixes. ________________

## 3.3 Testing H3

**Method**
- Define "exposed" occupations: top AIOE quartile / decile / other: top quartile of detailed Felten scores
- Compute concentration (HHI) of employment across exposed occupations, per metro
- SOC granularity: detailed primary · Sensitivity run at the other level: major-group comparison
- Compare within-exposure-quartile spread in concentration

**Exhibit** — scatter of exposure level (x) against exposed-footprint concentration (y), sized by employment. Quadrant naming is **[article]**; in the notebook just look at whether the cloud actually separates.

**Notebook inputs required**
- detailed SOC metro rows with employment
- Felten score by detailed SOC
- metro-level `E_m`
- a chosen definition of the exposed occupation set

**Preferred section flow**
1. define exposed occupations
2. compute concentration metric
3. plot exposure level vs concentration
4. compare dispersion within exposure bins
5. table example metros that have similar `E_m` but very different concentration

**Why this matters to the broader thesis**
- H1 says payroll and headcount tell very similar geographic stories, but payroll amplifies the same high-exposure metros
- H2 says attainment is a meaningful but incomplete proxy
- H3 asks whether the *distribution* of impact inside a metro changes how that metro experiences AI, even at the same headline exposure level

> **Prompt:** Run this at both SOC granularities before deciding which is primary. If the picture changes materially, the concentration measure is fragile and H3 should probably be demoted to option (b).

**Current interpretation caution:** the first notebook pass suggests the level-vs-concentration relationship may be weak and slightly negative, but that is not yet a stable result. Do not lean on that interpretation until the HHI definition and the major-group sensitivity view are clearer.

---

# Part 4 — Richmond

*Not new analysis. The national work pointed at one market.*

- Richmond's position in each exhibit above, plus D5 peer context
- Peer set: ________________
- Handoff format D6 expects: ________________

> **Prompt:** Write the one sentence about Richmond this entire notebook exists to support. If it isn't writable yet, the analysis isn't finished.

## 4.1 Thesis bridge to eventual writeup

Current working thesis for the broader piece:

1. **AI impacts will not be shared uniformly across cities and regions.**
   The geography of exposure should produce relative winners and losers, not one national experience.

2. **AI appears likely to matter more for earnings than for labor counts alone.**
   The payroll-weighted measure is not a side note; it may be closer to the economic footprint that changes tax base, housing demand, and local consumption.

3. **The political experience may diverge from the earnings experience.**
   High-impact, high-wage occupations may capture disproportionate upside, while lower-impact occupations may still shape the political response because they are numerically larger and may feel bypassed or left behind.

4. **Felten is about intensity of impact, not yet sign of impact.**
   The notebook should keep separating "where impact is concentrated" from "whether that impact is net-positive or net-negative."

### 4.1.1 Current working findings write-up

At the current notebook stage, the strongest cross-metro finding is that AI employment exposure and AI payroll exposure are tightly linked. The payroll-weighted measure does not radically reorder metros, but it does show that the same high-exposure places also carry disproportionately important exposed wage bills. That means the geography of AI impact is likely to matter economically even when the rank ordering itself stays stable.

Educational attainment helps explain that geography, but it does not fully settle it. Higher-BA metros are often more exposed, yet similarly educated metros can still differ because of their underlying industry and occupation structure. That makes attainment a useful starting point rather than a full explanation.

The remaining open question is structural shape. The notebook does not yet show a decisive national pattern in whether high-exposure metros are more diffuse or more concentrated internally. That uncertainty is useful rather than fatal: it gives the Richmond deep dive and future metro work a real analytical job to do instead of forcing a blanket national conclusion too early.

**Implication for later deep dives**
- Once the cross-metro structure is established, we can zoom into specific industries or occupation families and ask what positive-impact and negative-impact interpretations would each imply.
- That is a later interpretive layer, not something H1-H3 alone can settle.

---

# Part 5 — Limitations

*Named plainly, no hedging. Each one names what would resolve it — that list becomes the deferred entry's scope.*

1. Exposure is not displacement. ________________
2. Exposure scores are fixed, so all cross-metro variation is compositional. ________________
3. OEWS suppression and its effect on coverage. ________________
4. The published detailed SOC surface does not fully sum to OEWS all-occupation totals. ________________
5. Cross-section only; no pre-trend established. ________________
6. *Your own — the objection you're least prepared for.* ________________

## 5.1 Sign-of-impact caution

One unresolved issue should be carried explicitly through the notebook:

> Felten identifies occupations and industries likely to be affected by AI, but the score itself does not tell us whether the effect is net-positive, net-negative, labor-saving, wage-enhancing, demand-expanding, or politically destabilizing.

That means:
- H1 can show that earnings exposure differs from labor exposure
- H2 can show that attainment is an incomplete lens
- H3 can show that exposure shape differs across metros
- none of those, by themselves, prove whether AI is "good" or "bad" for the places most exposed

This is not a flaw in the notebook. It is the right boundary of the current analysis.

---

# Deferred — separate entry

**[settled]** Pre-trend test sequences first; it's cheaper and it's a check on A1 itself.

- **Pre-trend test:** 2000-vintage exposure index. Were today's high-exposure metros already on a distinct trajectory before AI?
- **RTI backtest:** Autor & Dorn (2013) long-differences with a shift-share instrument, reported as a calibration benchmark, not a forecast.
- **Blocking data:** historical metro occupation shares 1990–2000 — IPUMS + `occ1990dd` + commuting-zone crosswalk.

---

# What the notebook hands off

The article gets written from these artifacts, not from re-running the notebook. Persist them to disk.

**Tables**
- `metro_exposure.csv` — CBSA, `E_m`, `W_m` (both wage variants if built), percentile ranks, coverage share, flag status
- `metro_exposure.csv` — CBSA, `E_m`, `W_m`, percentile ranks, detailed-SOC coverage share, detailed-vs-total-OEWS share, flag status
- `richmond_decomposition.csv` — occupation, employment share, AIOE, contribution
- `attainment_residuals.csv` — CBSA, attainment, `E_m`, fitted, residual, rank
- `soc_match_table.csv`, `naics_match_table.csv`, and `coverage_audit.csv`

**Numbers to have written down**
- Spearman ρ and mean rank shift (H1)
- η² at each bin structure, and partial R² (H2)
- Concentration spread within exposure quartiles (H3, if run)
- Richmond's value and percentile on every measure

**Prose**
- One paragraph per hypothesis: what the test showed and what you now believe
- The Part 5 limitations, written out
- Every resolved decision, copied to `decisions.md`

---

# Done when

- [ ] Runs end to end on 401 CBSAs; low-coverage metros flagged, not dropped
- [ ] Richmond's `E_m` hand-verified against an independent calculation
- [ ] Each hypothesis evaluated against its pre-registered threshold, including where it fails
- [ ] Every blank in this document resolved
- [ ] Handoff artifacts written to disk
- [ ] Decisions copied to `decisions.md`
