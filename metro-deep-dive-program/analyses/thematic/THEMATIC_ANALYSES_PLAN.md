# Metro Deep Dive — Thematic Analyses Plan

**Status:** Directional family plan; ten provisional child specs scaffolded

**Updated:** 2026-09-20

**Program home:** `metro-deep-dive-program/metro_deep_dive_program.md`,
Section 3.3

**Legacy inventory:** `metro-deep-dive/docs/analysis_program.md`

## 1. Purpose

This document defines the first build direction for the ten Thematic analyses
in the Metro Deep Dive program:

- A1 — The AI Inversion
- A2 — Does Building Actually Lower Prices?
- A3 — Are Americans Moving Toward Harm?
- A4 — Did Remote Work Permanently Rewire Metro Geography?
- A5 — How Many Downtowns Does a Metro Have?
- A6 — Does Specialization Predict Growth?
- A7 — Who Is Actually Squeezed?
- A8 — The Geography of Life Expectancy
- A9 — Are Metros Converging or Diverging?
- A10 — Polarization: Are Growing Sectors High-Wage or Low-Wage?

The family starts with national research. Each entry tests a cross-theme claim
across metros and develops a broad narrative from the national evidence. Each
entry also provides a standard, parameterized market deep dive so the same
question can be inspected consistently for any covered CBSA.

This plan is one level above implementation. It establishes:

- what belongs in the Thematic family
- the separate roles of national, reusable market, and issue notebooks
- the initial audit of all ten entries against current repository assets
- the shared notebook and handoff expectations
- the dependency-aware build sequence
- the decisions each provisional child spec must settle after its audit

It does not lock equations, causal designs, thresholds, final visuals,
featured markets, or issue narratives. Those decisions require evidence from
the entry-level audit and, where reader-facing, belong in `issues/`.

## 2. Family Model

### 2.1 What makes an analysis Thematic

A Thematic analysis begins with a national question that crosses at least two
subject themes. Its primary result is a national finding, comparison, typology,
or test that is worth reading on its own.

The family is distinguished by the source and scale of the question:

- Position asks where a metro sits.
- Explanation asks why a selected metro sits there, usually from sub-CBSA
  evidence.
- Thematic asks whether a broader cross-theme claim holds across metros, then
  shows how that national pattern appears inside a selected market.

National scope does not require CBSA-only evidence. A5, for example, needs
tract-level employment centers inside many CBSAs before it can produce a
national metro typology. The national claim, rather than the finest input
grain, determines family membership.

### 2.2 Three notebook roles

Earlier program and classification-workbook language described one notebook
with `market: all` and `market: <cbsa>` modes. That execution model is
superseded by three clearer roles:

| Notebook role | Location | Required? | Job |
|---|---|---:|---|
| National analysis notebook | `analyses/thematic/<entry>/` | Yes | Develop and narrate the cross-metro claim, test alternatives, report coverage, and identify market hooks |
| Parameterized market notebook | `analyses/thematic/<entry>/` | Yes | Apply a standard deep-dive sequence to any selected CBSA and expose local components, comparisons, and candidate findings |
| Issue-specific market notebook | `issues/<market>/` | Only when selected for an issue | Assemble the strongest findings for a real market, combine them with other analyses, and make issue-owned editorial and presentation choices |

The national and parameterized market notebooks are separate notebooks because
they answer different questions and need different narrative sequences. They
should still share governed inputs, analysis-owned queries, metric definitions,
and method notes wherever those are genuinely common.

The parameterized market notebook is not the Richmond notebook. It uses a CBSA
selector and demonstrates the standard market read. A Richmond issue notebook
may later pull only two of its findings, combine them with Position or
Explanation evidence, and rebuild selected visuals for publication.

### 2.3 National-first sequence

The canonical order within each entry is:

1. audit prior work, live data, contracts, and the provisional spec
2. state a falsifiable national claim and its alternatives
3. build and review the national notebook
4. identify which national findings have meaningful local decompositions
5. build the parameterized market notebook around those standard deep-dive
   paths
6. hand candidate findings, caveats, and reusable surfaces to `issues/`

The market notebook should not be designed in detail before the national work
shows which local questions are actually useful. Its existence is required;
its final content is learned from the national analysis.

### 2.4 Narrative standard

Both analysis-layer notebooks are internal thinking tools. They should be easy
for an analyst to read as an argument:

`question -> evidence contract -> baseline -> test -> alternatives -> finding -> limitations -> next questions`

They do not need publication polish. Default plotting is acceptable. More
useful exhibits are preferable to fewer styled exhibits. The durable outputs
are the reasoning, the reviewed method, the reusable data surfaces, and the
candidate findings—not finished issue copy.

The notebooks must support a claim being weakened, rejected, or left
unresolved. A thematic entry is not required to manufacture a strong result.

### 2.5 Architecture boundary

The intended path is:

`governed datasets and engine outputs`
-> `analysis-owned method and reusable query surfaces`
-> `national notebook`
-> `parameterized market notebook`
-> `issue-owned selection and presentation`

Thematic analyses may own derived measures and classifications that exist to
answer their question. They must not locally rewrite governed geography,
benchmark, trajectory, taxonomy, or source contracts.

There is no requirement to create a generic Theme Engine before the analyses
exist. Promote a component only when two consumers reuse it unchanged or when
the program has already identified multiple concrete consumers with the same
interface. The shared artifact may be a method or mart rather than an engine.

## 3. Family Audit

### 3.1 Existing strengths

The audit reviewed the current program documents, engine contracts, Position
and Explanation families, the legacy Analysis Program, the A1 notebook/spec,
the Industry Explorer spec, and the live DuckDB surfaces available on
2026-09-20.

The current platform already provides substantial coverage:

- recurring 2012–2024 national CBSA panels for population, housing, income,
  commuting mode, and broad industry structure
- QCEW employment, wages, and broad-sector LQs in
  `gold.economics_industry_wide`
- detailed 2025 CBSA OEWS occupation and wage-distribution records for 393
  CBSAs in `silver.bls_oews`
- national county-first QWI history with demographic and industry cuts in
  `silver.lehd_qwi`, plus headline Gold labor fields
- national 2023 LODES WAC/RAC at tract and CBSA grains, but no managed OD
  flows and no multi-year WAC/RAC panel
- 2016–2025 health and environmental marts, with important source-specific
  vintage limits inside those tables
- governed Benchmarking, Geography, Intelligence Framework, and Time-Series
  surfaces
- a mature Q1 housing analysis that A2 and A7 can audit for reuse
- a substantial legacy A1 research notebook, two crosswalk rebuild notebooks,
  reviewed crosswalk artifacts, and a V3 analysis plan

### 3.2 Entry audit summary

| Entry | Current posture | Strongest existing assets | Main audit or method gate |
|---|---|---|---|
| A1 AI Inversion | Active legacy analysis; migrate after audit | Detailed OEWS, reviewed SOC/NAICS crosswalks, full H1–H3 Marimo work | Reconcile legacy findings and artifacts; split national and parameterized market roles; govern the crosswalk handoff |
| A2 Building Lowers Prices | High data readiness | Q1 mart/method notes, permits, housing stock, FHFA HPI, rent measures, population | Define a credible longitudinal design and avoid turning association into a causal building claim |
| A3 Moving Toward Harm | High source availability, mixed vintages | FEMA NRI at tract/county/CBSA, environment mart, population and housing growth | Align hazard exposure with movement/growth periods and distinguish exposure, realized loss, and causation |
| A4 Remote Work Rewired | Partial | 2012–2024 ACS WFH/commute panel, housing and industry panels, 2023 WAC/RAC | Decide what “rewired” means without historical LODES or OD; name the blocker if workplace-residence change is essential |
| A5 How Many Downtowns | Partial static foundation | 2023 tract WAC, existing D3 job-center work, Geography, Internal Structure/Q2/Q6 plans | Define center, subcenter, and dispersion rules; a time claim is not currently supported by LODES |
| A6 Specialization Predicts Growth | High data readiness | 2012–2024 QCEW broad-sector LQs, employment, wages, Benchmarking | Lock lag structure, sector grain, balanced-panel rules, and a design that separates persistence from mean reversion |
| A7 Who Is Squeezed | High data readiness | Q1 affordability work, ACS burden, CHAS, housing prices, income and wage context | Define “who” and separate household burden, market-entry cost, and local wage purchasing power |
| A8 Life Expectancy Geography | Moderate | County/CBSA health mart, income, housing, social fabric, food access | Replace causal “place effect” language unless the design supports it; reconcile county and CBSA inference |
| A9 Converging or Diverging | High panel readiness | 2012–2024 demographic/income panels, migration, Time-Series and Peers | Define convergence, nominal/real treatment, stable universe, endpoints, and whether national dispersion or peer divergence leads |
| A10 Polarization | Partial but improved | QCEW sector wages, detailed OEWS wage percentiles, QWI demographic/industry history, LODES earnings bands | Decide whether the claim concerns jobs, occupations, industries, or workers; broad sector averages alone cannot prove wage-distribution hollowing |

### 3.3 Boundary findings

The audit narrows the family to A1–A10.

- The Housing satellite is a supporting diagnostic workbench and possible
  shared component for Q1, A2, and A7. It is not an eleventh Thematic entry.
- The CBSA similarity study is a methods study attached to the Intelligence
  Framework and Position/Peers. It may become a methods article, but it is not
  part of the A1–A10 thematic build queue.
- The “also raised” candidates in the legacy Analysis Program remain a bank.
  They do not receive folders until they meet the cross-theme entry criterion
  and have a proposed claim.

## 4. Shared Requirements

### 4.1 Folder shape

Each entry starts with documentation only:

```text
thematic/<entry>/
├── README.md
├── THEMATIC_<ENTRY>_SPEC.md
└── THEMATIC_<ENTRY>_BUILD_PLAN.md
```

After Epic 1 approves the entry, the intended working shape is:

```text
thematic/<entry>/
├── README.md
├── THEMATIC_<ENTRY>_SPEC.md
├── THEMATIC_<ENTRY>_BUILD_PLAN.md
├── THEMATIC_<ENTRY>_NATIONAL_NOTEBOOK.py
├── THEMATIC_<ENTRY>_MARKET_NOTEBOOK.py
├── queries/
└── figures/
    ├── national/
    └── market/
        └── <cbsa_code>/
```

Do not add empty implementation directories merely to complete the tree. Add
them when the approved spec names their first artifact.

### 4.2 National notebook minimum surfaces

Every national notebook should include:

- the question, provisional claim, and falsification or alternative-result
  conditions before substantive results
- source, vintage, universe, exclusions, and coverage
- a descriptive baseline in native units
- the primary test plus at least one serious alternative explanation or
  sensitivity view
- distributions and component evidence, not only a ranked metro table
- a clear result status: `supported`, `mixed`, `not supported`, `insufficient
  evidence`, or an equally explicit analysis-specific vocabulary
- examples selected from the evidence rather than preselected only for
  editorial convenience
- a finding ledger with national findings, candidate market hooks, caveats,
  and unresolved questions

### 4.3 Parameterized market notebook minimum surfaces

Every market notebook should include:

- a searchable CBSA selector, with Richmond (`40060`) as a convenient default
  but no Richmond-specific logic
- the selected market’s position in the national result
- national, Census Division, and Act 1 peer comparisons when meaningful
- the components that explain the market’s result
- sub-CBSA evidence when the question and governed data support it
- standard deep-dive paths identified by the national notebook
- a visible `no distinctive local finding` outcome
- a concise candidate-findings table for issue review

The market notebook may omit a map when the question is not spatial. It should
not add a map merely because tract data exist.

### 4.4 Shared controls and data rules

- Read DuckDB in read-only mode from repository environment configuration.
- Resolve repository-relative paths from the notebook file, never from a
  machine-specific absolute path.
- Preserve native grain, source year, release vintage, and method version.
- Do not silently substitute the nearest available year across source families.
- Keep counts, shares, rates, medians, indices, and modeled classifications
  distinct.
- Report excluded markets and missing components rather than narrowing the
  universe silently.
- Use governed Geography, Benchmarking, Intelligence, and Time-Series outputs
  without recomputing their methods locally.
- Keep analysis visuals simple. Publication styling and final chart selection
  belong in `issues/`.

### 4.5 Handoff contract

The analysis layer should hand the issue layer:

- reviewed result tables or named query surfaces
- a finding ledger with evidence and caveats
- reproducible national context for any selected market claim
- a market component table and comparison rows
- method/version and source/vintage notes
- a list of candidate visuals, not final issue graphics

The issue layer owns the actual market notebook, cross-analysis synthesis,
reader-facing prose, publication visuals, featured comparisons, and all
lock-once editorial decisions.

## 5. Dependency and Reuse Map

| Shared capability | First likely Thematic consumer | Later reuse |
|---|---|---|
| Reviewed AI exposure crosswalk and exposure surface | A1 | Later AI/industry pieces and issue notebooks |
| Industry panel and sector taxonomy | A1 or A6 | A6, A10, A4, market industry reads |
| Lagged-panel analysis pattern | A6 | A2, A3, A9, A10 where appropriate |
| Housing component surface | Q1, then A2 | A7 and issue housing reads |
| Burden/market-access distinction | Q1, then A7 | A2 context and market affordability narratives |
| Stable longitudinal CBSA cohort rules | A6 or A9 | A2, A3, A4, A10 |
| Tract job-center surface | Q2 / Industry D3, then A5 | A4 and market structure reads |
| Hazard-growth comparison surface | A3 | Issue environment/growth reads |
| Health-context comparison surface | A8 | Issue health and social-fabric reads |

The table identifies likely reuse, not pre-authorization for new engines.
First-use logic remains analysis-owned until the interface is proven.

## 6. Proposed Build Sequence

All entries begin with Epic 1 audit and spec review. Completing an audit does
not make every entry active at once; the one-active-analysis discipline from
the legacy Analysis Program still applies to substantive notebook builds.

### Wave 0 — Audit all ten entries

For each entry:

1. inspect prior art and record what is reusable, obsolete, or contradictory
2. profile the live inputs at the required grain and time span
3. reconcile the provisional claim with what the data can actually test
4. separate blocking inputs from optional enrichments
5. revise the spec and build plan before creating notebook code

### Wave 1 — Industry family

1. **T1 / A1 AI Inversion.** Migrate and split the most developed legacy
   analysis; use it to establish the first national/market notebook handoff.
2. **T2 / A6 Specialization Predicts Growth.** Use the existing QCEW panel to
   establish the family’s lagged-panel pattern.
3. **T3 / A10 Polarization.** Audit the newly available QWI and OEWS wage
   surfaces, then narrow the claim to what those data can support.

### Wave 2 — Housing family

4. **T4 / A2 Building Lowers Prices.** Reuse Q1 components while treating the
   causal question as new research, not as a Q1 output.
5. **T5 / A7 Who Is Squeezed.** Separate household burden, market-entry cost,
   and wages before building a national typology.

### Wave 3 — National change and work geography

6. **T6 / A9 Converging or Diverging.** Establish stable-cohort dispersion and
   peer-divergence methods from the broad recurring panels.
7. **T7 / A4 Remote Work Rewired.** Build only the claims supported by the ACS
   panel while the audit decides whether historical workplace geography is a
   blocker.
8. **T8 / A5 How Many Downtowns.** Develop a static national center typology
   from current LODES before proposing any change-over-time story.

### Wave 4 — Environment and health

9. **T9 / A3 Moving Toward Harm.** Align growth windows to hazard vintages and
   keep exposure distinct from realized harm.
10. **T10 / A8 Geography of Life Expectancy.** Reframe or design the “place
    versus income” test so it does not imply an unsupported causal place effect.

This is a reuse-aware requirements order, not a publication schedule. A routed
issue need can pull an audited, ready entry forward.

## 7. Spec Queue and Definition of Ready

An entry is ready to move beyond Epic 1 when:

- its national question and provisional claim are falsifiable
- the claim matches the available grain, history, and universe
- the primary outcome, explanatory measures, and serious alternatives are
  named
- source fields and vintages are identified at contract level
- blocking and optional dependencies are separated
- the national notebook’s first decision sequence is outlined
- at least two standard market deep-dive paths are proposed
- unsupported causal or flow language has been removed or backed by a named
  design/input
- minimum outputs and QA checks are testable
- the spec and build plan have been revised with the audit findings

## 8. Decisions Confirmed

1. **Thematic questions are national in scope.** The national notebook is the
   primary analysis artifact, not only a calibration run for local work.
2. **Use two analysis notebooks.** Every entry has a national notebook and a
   separate parameterized market notebook.
3. **The market notebook is reusable, not issue-specific.** It provides
   standard CBSA deep-dive approaches and a selector. Actual Richmond or other
   market story notebooks belong in `issues/`.
4. **The analysis notebooks are narrative but internal.** They should make the
   reasoning easy to follow without being polished for downstream consumption.
5. **Issues package the findings.** Final selection, synthesis, prose, and
   visuals remain downstream.
6. **All ten entries receive provisional specs now.** Every build plan starts
   with an audit and review epic; no notebook implementation begins before that
   epic revises the provisional documents.

## 9. Explicit Non-Goals

- no notebook or analysis code in this scaffold
- no final equations, weights, thresholds, or typology labels before audits
- no assumption that one generic Theme Engine must power all ten entries
- no issue-specific Richmond notebook under `analyses/thematic/`
- no polished publication graphics or article prose
- no forced strong finding, market hook, or local distinction
- no causal language from cross-sectional association alone
- no silent migration or deletion of the legacy A1 files
- no new folders for the Housing satellite, CBSA similarity study, or banked
  candidate ideas

## 10. Primary References for Child Audits

- `metro-deep-dive-program/metro_deep_dive_program.md`
- `metro-deep-dive-program/mdd_classification_workbook.md`
- `metro-deep-dive-program/docs/build_sequence.md`
- `metro-deep-dive-program/analyses/explanation/EXPLANATION_ANALYSES_PLAN.md`
- `metro-deep-dive-program/analyses/position/POSITION_ANALYSES_README.md`
- `metro-deep-dive-program/engines/benchmarking/CONTRACT.md`
- `metro-deep-dive-program/engines/geography/CONTRACT.md`
- `metro-deep-dive-program/engines/time_series/CONTRACT.md`
- `metro-deep-dive/docs/analysis_program.md`
- `metro-deep-dive/analysis_program/01_ai_inversion/ai_inversion_spec.md`
- `metro-deep-dive/metro-area-explorer/industry/SPEC_INDUSTRY.md`
