# AI & Jobs Article Series — Analysis Brief
**Patterns in Place** | Working reference for IDE session
Last updated: 2026-07-12

---

## What We're Building

A three-article series analyzing which US metro areas (CBSAs) are most exposed to
AI-driven job disruption, using industry concentration data from the existing platform
joined to published AI exposure scores.

**Core thesis:** The metros that won the knowledge economy transition — high BA+,
high professional services, high income — may be the most structurally exposed to AI
disruption. This inverts the conventional narrative that Rust Belt / manufacturing
metros are most at risk.

**Framing:** Structural risk, not prediction. These analyses identify where certain
kinds of work are concentrated relative to AI task exposure. They do not forecast
displacement timelines.

---

## The Three Articles

### Article 1 — The Industry Story (build now)
**Exposure measure:** AI Industry Exposure Index (AIIE) by 4-digit NAICS
**Platform data:** QCEW Silver table — employment shares by NAICS industry, by CBSA
**Key question:** Which metros built their economies on AI-exposed industries?
**Central chart:** Four-quadrant scatter — Opportunity percentile (y) × AIIE-weighted
exposure index (x)
**Status:** Buildable now. No new data sources required beyond Felten download.

### Article 2 — The Worker Story (after OES ingestion)
**Exposure measure:** AI Occupational Exposure (AIOE) by 6-digit SOC
**Platform data:** BLS OES — occupation mix by CBSA (not yet ingested)
**Key question:** Which metros have workforces doing AI-exposed tasks — and are those
workers the ones with the fewest buffers?
**Central chart:** AIOE-weighted exposure × labor market vulnerability metrics
(wage levels, education, unemployment)
**Status:** Blocked on OES ingestion. OES is already flagged as the top stack gap.

### Article 3 — The Divergence Story (after both)
**Key question:** Where do industry and worker exposure tell different stories about
the same metro?
**Central finding:** Metros where AIIE and AIOE diverge are the most analytically
interesting — high industry / moderate occupation exposure may signal resilience;
the inverse signals hidden vulnerability.
**Status:** Depends on Articles 1 and 2.

---

## Source Data Decision

### Primary exposure source: Felten, Raj & Seamans (2021)

**Citation:** Felten, E., Raj, M., & Seamans, R. (2021). "Occupational, Industry,
and Geographic Exposure to Artificial Intelligence: A Novel Dataset and Its Potential
Uses." *Strategic Management Journal*, 42(12), 2195–2217.

**GitHub:** `github.com/AIOE-Data/AIOE`

**Why this source over Goldman Sachs:**
The GS paper (Hatzius et al., 2023) produced exposure scores at the **occupational
group** level (SOC major groups like "Legal", "Office and Administrative Support"),
not at the NAICS industry level. The scores GS published are not directly joinable to
QCEW without a manual SOC→NAICS translation using national employment weights — an
approximation that introduces unnecessary imprecision.

Felten et al. already did this translation properly. They constructed industry-level
exposure by taking an employment-weighted average of occupational exposure scores
across all occupations within each 4-digit NAICS industry. The result is a published,
citable dataset at exactly the grain needed for the QCEW join.

GS used the same underlying O*NET data — Felten is simply the cleaner primary source.
EIG, the NY Fed, and the Yale Budget Lab all use Felten as their primary measure.

**Note on the GS framing:** GS remains the right public reference to cite in the
article narrative — their research is what put AI labor exposure into mainstream
discourse and their framing of "25% of tasks automatable" is what readers will
recognize. But the analytical scores driving the index should come from Felten, not GS.

### What to download from the Felten GitHub repo

Three appendices are relevant:

| Appendix | Contents | Use |
|---|---|---|
| Data Appendix A | AIOE scores by occupation, indexed by 6-digit SOC | Article 2 (worker story) |
| Data Appendix B | AIIE scores by industry, indexed by 4-digit NAICS | Article 1 (industry story) |
| Data Appendix C | AIGE scores by geography, indexed by US county FIPS | Optional: validate our CBSA-level index against their county-level geography scores |

**For Article 1: download Data Appendix B.**

---

## Article 1 — Pipeline Design

### Inputs
- `silver.qcew_*` — employment by NAICS industry × CBSA × year
- `ref.felten_aiie` — AIIE score by 4-digit NAICS (static; built from 2019 employment weights)
- `gold.opportunity_scores` — Opportunity frame percentile by CBSA (from Intelligence Layer)

### Join logic

```sql
-- Step 1: Join QCEW employment shares to Felten AIIE scores
SELECT
    q.cbsa_code,
    q.cbsa_name,
    q.naics_code,
    q.employment_share,
    f.aiie_score
FROM silver.qcew_cbsa q
JOIN ref.felten_aiie f
    ON LEFT(q.naics_code, 4) = f.naics_4digit
WHERE q.year = 2023

-- Step 2: Compute employment-weighted exposure index per CBSA
SELECT
    cbsa_code,
    cbsa_name,
    SUM(employment_share * aiie_score) AS ai_exposure_raw
FROM above
GROUP BY cbsa_code, cbsa_name

-- Step 3: Percentile rank within 401-CBSA universe
-- (consistent with Opportunity and Livability frame scoring)
SELECT
    cbsa_code,
    cbsa_name,
    ai_exposure_raw,
    PERCENT_RANK() OVER (ORDER BY ai_exposure_raw) * 100 AS ai_exposure_pctile
FROM above
```

### Things to confirm before building
1. **NAICS grain in QCEW Silver:** Does it carry 4-digit NAICS codes, or only 2-digit
   supersectors? Felten AIIE is at 4-digit; if you only have 2-digit, the join still
   works but loses precision. Felten also publishes 2-digit aggregations.
2. **Year to use:** Use 2022 or 2023 employment shares from QCEW. Felten's exposure
   weights are static (2019 vintage) — they measure the task content of occupations,
   not a time series. What varies year to year is your metro's industry mix.
3. **CBSA vs. county grain:** Felten's AIGE geography scores are at county level.
   If you need to validate, use your existing county→CBSA crosswalk to aggregate.

### Key output columns per CBSA
- `ai_exposure_raw` — employment-weighted AIIE score
- `ai_exposure_pctile` — 0–100 percentile within 401-CBSA universe
- `opportunity_pctile` — from existing Opportunity frame scoring
- `livability_pctile` — from existing Livability frame scoring (for a three-axis version)
- Quadrant label: derived from exposure and opportunity percentiles

---

## Key Charts

### Chart 1 — The four-quadrant scatter (centerpiece)
- X-axis: AI exposure index (percentile, high = more exposed)
- Y-axis: Opportunity score (percentile, high = stronger fundamentals)
- Each dot: one CBSA, sized by total employment
- Quadrant labels:
  - Top right: **Exposed Winners** — strong economy, high AI exposure
  - Top left: **Resilient Performers** — strong economy, lower exposure
  - Bottom right: **Double Exposure** — weak fundamentals, high exposure (the equity story)
  - Bottom left: **Structural Laggards** — weak economy, lower exposure

### Chart 2 — Top/bottom ranked CBSAs by exposure index
- Simple horizontal bar chart
- Top 20 most exposed and bottom 20 least exposed
- Annotate with Opportunity tier (high / medium / low)

### Chart 3 — Industry composition of most-exposed metros
- Stacked bar showing industry mix for the top-10 most exposed CBSAs
- Highlights which sectors are driving exposure (professional services,
  finance, information)

---

## Honest Limitations to State in the Article

1. **Felten scores are vintage 2019.** AI capabilities have changed since then —
   the scores may understate current exposure in some sectors (legal, finance) where
   LLM adoption has accelerated. Flag as conservative estimate.
2. **Industry-level scores use national occupation mix.** The AIIE averages occupation
   exposure across all workers in a 4-digit industry nationally. A given metro's
   actual occupation mix within that industry may differ. OES (Article 2) corrects this.
3. **Exposure ≠ displacement.** High exposure means the task content of work is
   automatable. Adoption speed, organizational change, and regulatory environment
   all mediate actual displacement. Frame as structural risk, not forecast.
4. **High-exposure metros also have high adaptation capacity.** Knowledge economy
   metros have capital, institutions, and human capital that historically enable
   restructuring. Acknowledge explicitly.