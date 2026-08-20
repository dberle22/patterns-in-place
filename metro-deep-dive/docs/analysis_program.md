# Analysis Program

**Last updated:** 2026-08-04
**Status:** shape only — hypotheses, methods, and outputs are deliberately unfilled
**Supersedes:** the split-out pipeline table in `V1_REVIEW_PLAN.md`

## What this is

The standing list of cross-theme analyses. One entry per analysis. Each entry is a body of inquiry that can carry multiple published pieces, not a single chart.

**Entry criterion:** an analysis crosses at least two themes. A question confined to one theme is descriptive — that is legitimate work with its own value, but it belongs in the Daily Data Publisher queue or a workbench, not here.

**Themes referenced:** Industry & Labor, Work Geography, Housing & Affordability, People & Movement, Health & Wellbeing, Environment & Risk, Social Fabric, Places & Amenities.

## Working rules

- **Write the claim before running the analysis.** A falsifiable sentence first, then the test. This is the difference between research and a tour of charts.
- **One analysis active at a time.** Others stay in the bank. The bank keeps; half-finished analyses do not.
- **Notebook is the default vehicle.** An app is an escalation that has to be argued for, not the assumed endpoint.
- **Workbenches are the methods section, not the product.** They are what gets described; the analysis is what gets published.
- **Cross-theme is the filter, not a bonus.** If an entry collapses to one theme on inspection, move it out.

## Status vocabulary

| Status | Meaning |
|---|---|
| `active` | Currently being worked. Only one at a time. |
| `ready` | Claim written, data confirmed available, could start today. |
| `banked` | Question identified, claim not yet written. |
| `blocked` | Waiting on named data or upstream work. |
| `parked` | Attempted, not concluded, reason recorded. |
| `shipped` | Published. Link recorded. |

## Entry template

Every entry carries these fields. Fields marked → are filled collaboratively before work begins.

```
### [Name]

Themes crossed:
Question:
→ Claim:
→ What would falsify it:
Grain and universe:
Primary data:
→ Method sketch:
→ First output:
Publication form:
Dependencies:
Status:
```

---

## Entries

### A1 — The AI inversion

- **Themes crossed:** Industry & Labor × People & Movement (educational attainment, knowledge-economy composition)
- **Question:** Are the metros that won the knowledge-economy transition the most structurally exposed to AI task displacement?
- **→ Claim:**
- **→ What would falsify it:**
- **Grain and universe:** CBSA, national; Richmond as the case
- **Primary data:** Felten AIIE / AIOE appendices, `economics_industry_wide`, `economics_occupation_wide` (OEWS), `population_demographics`, D5 peer set
- **→ Method sketch:**
- **→ First output:**
- **Publication form:** Report with a geographic arc — regional, then market, then submarket
- **Dependencies:** `V1_REVIEW_PLAN.md` Phase 1 correctness on D6; Phase 4 extraction; peer benchmarking
- **Status:** `active`

### A2 — Does building actually lower prices?

- **Themes crossed:** Housing & Affordability × People & Movement
- **Question:** Do metros that permit more housing see slower price and rent growth?
- **→ Claim:**
- **→ What would falsify it:**
- **Grain and universe:** CBSA, national, decade-scale panel
- **Primary data:** `housing_core_wide` (permits, structure mix, vacancy), `housing_market_wide` (HPI, ZORI), `affordability_wide`, `population_demographics`
- **→ Method sketch:**
- **→ First output:**
- **Publication form:** Standalone national piece
- **Dependencies:** none identified
- **Status:** `banked`

### A3 — Are Americans moving toward harm?

- **Themes crossed:** Environment & Risk × People & Movement × Housing & Affordability
- **Question:** Is population and housing growth concentrating in high-hazard metros?
- **→ Claim:**
- **→ What would falsify it:**
- **Grain and universe:** CBSA, national
- **Primary data:** `environment_wide` (FEMA NRI, per-hazard scores), `population_demographics`, `housing_core_wide` permits
- **→ Method sketch:**
- **→ First output:**
- **Publication form:** Standalone national piece
- **Dependencies:** none identified
- **Status:** `banked`

### A4 — Did remote work permanently rewire metro geography?

- **Themes crossed:** Work Geography × Housing & Affordability × Industry & Labor
- **Question:** Has the workplace-residence structure of metros durably changed, and did housing costs follow?
- **→ Claim:**
- **→ What would falsify it:**
- **Grain and universe:** CBSA and tract; national with market cases
- **Primary data:** `transport_built_form_wide` (`pct_commute_wfh` series), `economics_lodes_wide` WAC/RAC, `housing_market_wide`
- **→ Method sketch:**
- **→ First output:**
- **Publication form:** Standalone national piece
- **Dependencies:** LODES vintage coverage across the shift period needs confirming
- **Status:** `banked`

### A5 — How many downtowns does a metro have?

- **Themes crossed:** Work Geography × Housing & Affordability
- **Question:** Are metros monocentric, polycentric, or dispersed — and what does employment structure predict?
- **→ Claim:**
- **→ What would falsify it:**
- **Grain and universe:** Tract within CBSA, national
- **Primary data:** `economics_lodes_wide` WAC, tract geography, D3 job-center work
- **→ Method sketch:**
- **→ First output:**
- **Publication form:** Standalone national piece; strongest urban-economics positioning of the set
- **Dependencies:** tract→place crosswalk for readability
- **Status:** `banked`

### A6 — Does specialization predict growth?

- **Themes crossed:** Industry & Labor × People & Movement
- **Question:** Does high location quotient in a sector predict subsequent employment growth in that sector, or is mean reversion the norm?
- **→ Claim:**
- **→ What would falsify it:**
- **Grain and universe:** CBSA, national, lagged panel
- **Primary data:** `economics_industry_wide` LQ columns and QCEW history
- **→ Method sketch:**
- **→ First output:**
- **Publication form:** Standalone national piece; the most econometric entry in the set
- **Dependencies:** none identified
- **Status:** `banked`

### A7 — Who is actually squeezed?

- **Themes crossed:** Housing & Affordability × Industry & Labor
- **Question:** Where do price level and cost burden diverge, and what explains the gap?
- **→ Claim:**
- **→ What would falsify it:**
- **Grain and universe:** CBSA, national
- **Primary data:** `affordability_wide` (burden, RPP), `housing_market_wide`, `economics_income_wide`, sector wage columns in `economics_industry_wide`
- **→ Method sketch:**
- **→ First output:**
- **Publication form:** Standalone national piece
- **Dependencies:** none identified
- **Status:** `banked`

### A8 — The geography of life expectancy

- **Themes crossed:** Health & Wellbeing × Housing & Affordability × Social Fabric
- **Question:** How much variation in health outcomes is place rather than income?
- **→ Claim:**
- **→ What would falsify it:**
- **Grain and universe:** County and CBSA, national
- **Primary data:** `health_wide` (36 metrics, currently unused), `affordability_wide` RPP, `economics_income_wide`, `social_fabric_wide`
- **→ Method sketch:**
- **→ First output:**
- **Publication form:** Standalone national piece
- **Dependencies:** `health_wide` is missing from `table_catalog.yml` — recorded, not blocking
- **Status:** `banked`

### A9 — Are metros converging or diverging?

- **Themes crossed:** People & Movement × Industry & Labor × Housing & Affordability
- **Question:** Are metros becoming more alike or sorting apart on education, age, and income?
- **→ Claim:**
- **→ What would falsify it:**
- **Grain and universe:** CBSA, national, long panel
- **Primary data:** `population_demographics`, `migration_wide` (including `irs_net_agi`), `economics_income_wide`
- **→ Method sketch:**
- **→ First output:**
- **Publication form:** Standalone national piece
- **Dependencies:** none identified
- **Status:** `banked`

### A10 — Polarization: are growing sectors high-wage or low-wage?

- **Themes crossed:** Industry & Labor × People & Movement
- **Question:** Is the middle of the wage distribution hollowing out, and where?
- **→ Claim:**
- **→ What would falsify it:**
- **Grain and universe:** CBSA, national
- **Primary data:** `economics_industry_wide` sector wage columns and employment shares, `economics_occupation_wide`
- **→ Method sketch:**
- **→ First output:**
- **Publication form:** Standalone national piece; natural companion to A1
- **Dependencies:** none identified
- **Status:** `banked`

---

## Also raised, not yet entries

These were identified but either collapse to a single theme or need more shaping before they earn an entry.

| Candidate | Note |
|---|---|
| Concentration and fragility | Industry-only unless paired with a shock or recovery measure |
| Growth without jobs (GDP–employment decoupling) | Needs the GDP↔employment sector crosswalk to be credible |
| Same job, different pay | Strong, but currently Industry-only; pairs with A7 |
| Deaths of despair as spatial cluster | Health-only as posed; needs a second theme |
| Who bears environmental burden | Environment × People; close to an entry, needs a claim |
| Does connectedness predict opportunity? | Social Fabric × People; Chetty-adjacent, needs differentiation |
| Spatial mismatch | Overlaps A5 and A7; may be a section rather than an entry |

## Next step

Fill A1's `→` fields together. Nothing else moves until it ships.