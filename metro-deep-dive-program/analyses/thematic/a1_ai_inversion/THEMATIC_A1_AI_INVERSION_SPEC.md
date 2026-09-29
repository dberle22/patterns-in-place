# Thematic A1 — AI Inversion Spec

**Status:** Provisional; revise after Epic 1 audit

**Updated:** 2026-09-20

**Family plan:** [THEMATIC_ANALYSES_PLAN.md](../THEMATIC_ANALYSES_PLAN.md)

## 1. Question and purpose

Are the metros that benefited most from the knowledge-economy transition also
the most structurally exposed to AI-related task change?

This analysis should establish the national geography and internal structure
of occupational AI exposure. It must keep exposure separate from job loss,
automation, adoption, productivity, and net economic effect.

**Themes crossed:** Industry & Labor × People & Movement.

## 2. Provisional claim and alternatives

**Claim direction to review:** Metros with more highly educated and
knowledge-intensive workforces tend to carry higher measured AI task exposure,
but industry and occupation composition create meaningful differences among
otherwise similar metros.

Evidence that would weaken or change the claim includes:

- little relationship between exposure and education/knowledge-economy
  structure
- rankings dominated by crosswalk or suppression artifacts
- no interpretable compositional differences among similarly exposed metros
- results that reverse under reasonable exposure, coverage, or weighting
  choices

The analysis must permit the original “inversion” framing to be rejected even
if the exposure measure remains useful.

## 3. Analytical unit and universe

- National unit: CBSA.
- Primary exposure input: CBSA × detailed SOC, latest governed OEWS year.
- Secondary structural input: CBSA × detailed NAICS.
- Current runnable occupation universe: 393 CBSAs in 2025, subject to audit.
- Market unit: selected CBSA with occupation and industry decompositions;
  sub-CBSA claims are optional and require a separately governed input.

## 4. Notebook contracts

### National notebook

The national notebook should:

1. establish source, crosswalk, denominator, suppression, and coverage rules
2. show the national occupation and industry decomposition of exposure
3. compare employment-weighted and payroll-weighted exposure
4. test the relationship with educational attainment and economic structure
5. test whether similar headline levels hide different concentration shapes
6. record supported, weakened, and rejected hypotheses explicitly
7. produce a finding ledger and candidate market hooks

The existing H1–H3 sequence is prior art, not automatically the final sequence.

### Parameterized market notebook

The market notebook should:

- use a searchable CBSA selector
- show the selected CBSA’s national rank/percentile and coverage
- compare national, Census Division, and Act 1 peer context
- decompose exposure by detailed occupation, broad occupation family, and
  relevant industry groups
- show employment- versus payroll-weighted differences
- show concentration/shape and attainment residual context if those survive
  national review
- end with candidate findings and a valid `no distinctive local finding` path

It must not predict whether AI will help or harm the selected metro.

## 5. Current repository assets

- legacy V3 spec and Marimo analysis in
  `metro-deep-dive/analysis_program/01_ai_inversion/`
- dedicated SOC and NAICS crosswalk rebuild notebooks
- reviewed crosswalk CSV artifacts under the legacy `outputs/` folder
- `silver.bls_oews` detailed employment and wage fields
- `gold.economics_occupation_wide`, `gold.economics_industry_wide`, and
  `gold.population_demographics`
- Industry Explorer D1–D6 prior art in
  `metro-deep-dive/metro-area-explorer/industry/SPEC_INDUSTRY.md`
- Benchmarking and Intelligence peer surfaces

## 6. Audit findings to verify

The legacy work is advanced but not yet a clean program-layer contract:

- the main notebook combines national analysis and a Richmond hook
- the spec still contains unresolved blanks and a 401-CBSA done condition even
  though the live 2025 OEWS universe is 393 CBSAs
- reviewed crosswalk artifacts exist, but their long-term governed home is open
- notebook build logic, reusable result surfaces, and issue handoff are not yet
  separated
- H1 appears weaker than proposed, H2 needs reframing, and H3 remains promising
  but method-sensitive

Epic 1 must decide what is migrated, referenced, archived, or rewritten. The
legacy files must not be silently copied into this folder.

## 7. Provisional outputs

- national metro exposure and coverage table
- national SOC and NAICS decomposition tables
- hypothesis result/sensitivity tables
- selected-market exposure summary and component tables
- comparison rows for nation, division, and peers
- finding ledger with interpretation limits
- versioned method note for the exposure and crosswalk choices

## 8. Decisions Epic 1 must prepare

- primary exposure source/version and citation
- SOC and NAICS crosswalk ownership and versioning
- coverage threshold and treatment of suppressed rows
- employment versus payroll weighting roles
- final national claim and hypothesis sequence
- stable national universe and comparison cohort
- which A1 measures are valid reusable market views
- whether any result surface should become a shared industry mart

## 9. Non-goals

- estimating net employment loss, adoption timing, productivity, or local GDP
  impact
- treating an exposure index as a probability or share of jobs at risk
- rebuilding the Felten crosswalk inside the analysis notebooks
- publishing Richmond-specific narrative from this folder

