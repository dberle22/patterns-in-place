# Thematic A10 — Polarization Spec

**Status:** Provisional; revise after Epic 1 audit

**Updated:** 2026-09-20

**Family plan:** [THEMATIC_ANALYSES_PLAN.md](../THEMATIC_ANALYSES_PLAN.md)

## 1. Question and purpose

Are growing parts of metro labor markets concentrated at the high and low ends
of the wage distribution while middle-wage work loses share, and how does that
pattern differ across places?

The analysis must decide whether its evidence concerns industries, occupations,
jobs, or workers. Those are related but not interchangeable units.

**Themes crossed:** Industry & Labor × People & Movement.

## 2. Provisional claim and alternatives

**Claim direction to review:** Many metros show employment growth concentrated
in high- and low-wage work rather than the middle, but the shape differs by
industry structure, occupation mix, and worker composition.

The claim is weakened if employment growth is broadly distributed across wage
tiers, if results disappear after inflation and changing occupational/industry
mix are handled, or if available history cannot measure distributional change.

## 3. Analytical unit and universe

Candidate units to resolve in the audit:

- CBSA × broad industry × year using QCEW employment and average wages
- CBSA × detailed occupation for 2025 OEWS employment and wage percentiles
- county/CBSA × industry × demographic group × year using QWI average earnings
- tract/CBSA earnings bands from 2023 LODES as current composition context

The final national unit must match the retained polarization claim. The market
unit is the selected CBSA with the same reviewed sector/occupation/tier evidence.

## 4. Notebook contracts

### National notebook

The national notebook should:

1. define polarization and the unit whose distribution is changing
2. document wage measures, inflation adjustment, bins/tiers, and history
3. separate sector-average wage position from within-sector wage distribution
4. distinguish employment growth, employment-share change, and wage change
5. test tier boundaries, sector/occupation grain, region, and metro-size
   sensitivity
6. use QWI demographic cuts only when they answer a declared worker question
7. state clearly when a cross-sectional lens cannot establish hollowing over
   time

### Parameterized market notebook

The market notebook should:

- show the selected CBSA’s reviewed job/wage structure and change
- compare nation, division, and peers
- identify which industries or occupations drive high-, middle-, and low-wage
  outcomes
- preserve employment scale alongside shares and wage position
- show worker demographic/education context only when aligned to the method
- provide standard deep dives for polarized, upgrading, broad middle growth,
  low-wage concentration, and inconclusive cases

## 5. Current repository assets

- 2012–2024 broad-sector QCEW employment and average wages
- detailed 2025 `silver.bls_oews` employment plus p10/p25/median/p75/p90 wages
- `gold.economics_occupation_wide` occupation-family employment and mean wages
- national `silver.lehd_qwi` history by industry and selected age/education
  groups, plus headline Gold QWI measures
- 2023 LODES workplace/resident earnings bands
- Industry Explorer, A1, A6, Benchmarking, and Time-Series prior art

## 6. Audit findings to verify

- Broad QCEW sector averages do not describe the wage distribution inside each
  sector.
- Detailed OEWS wage percentiles are currently a one-year metro surface, so
  they describe structure rather than change.
- QWI supplies historical average earnings and worker composition, not a full
  wage percentile distribution.
- LODES earnings bands are a current stock and use source-defined thresholds.
- A valid longitudinal design may need to classify industries/occupations by
  base-period national wage and then track employment shares, rather than claim
  observed within-unit wage-distribution change.
- “Hollowing out,” “bifurcation,” job quality, and inequality are not synonyms.

## 7. Provisional outputs

- source/unit evidence matrix and coverage table
- reviewed wage-tier or distribution construction
- national employment growth/share change by wage position
- sector/occupation and metro sensitivity views
- selected-market driver and comparison tables
- finding ledger with explicit limits on distributional inference

## 8. Decisions Epic 1 must prepare

- precise polarization definition and unit of analysis
- longitudinal versus cross-sectional role of each source
- wage measure, inflation adjustment, and tier/bin construction
- base-period versus contemporaneous wage classification
- industry and occupation taxonomy
- minimum employment and suppression rules
- demographic/education role from QWI
- standard market deep-dive paths

## 9. Non-goals

- claiming wage-distribution change from sector-average wages alone
- merging industry and occupation evidence into one unlabeled measure
- treating LODES earnings bands as universal job-quality tiers without review
- equating polarization with inequality or economic harm automatically
- publishing worker-level causal claims from aggregate metro data

