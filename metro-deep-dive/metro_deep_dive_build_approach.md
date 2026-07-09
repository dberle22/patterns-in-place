# Metro Deep Dive — Build Approach

*Decision record. How we build the Deep Dive series: the template is the starting point, markets adjust it from there. Companion to `metro_deep_dive_template_guidance.md` (the format spec) and `INTELLIGENCE_LAYER_ROADMAP.md` (the scoring layer).*

**Status:** Decided
**Last updated:** 2026-07-09

---

## The Decision

**The Metro Deep Dive is the flagship series.** Not Housing, not technical writing. It is the one output that demonstrates the whole apparatus applied end to end, rather than proving competence on a single subject. It is no longer blocked on the Intelligence Layer.

**`metro_deep_dive_template_guidance.md` is the base for every market.** Its four-Act structure and its Fixed Spine are adopted as-is. Each market inherits the spine unchanged and adapts only the flex slots.

**Per-market adjustment is bounded, not open-ended.** As we work each Act for a given market we evaluate which metrics are most interesting there — but that evaluation only ever changes *flex* content. The spine does not move market to market. This is the difference between a comparable series and a pile of one-off city reports.

**Reuse over rebuild.** The platform already contains most of what an issue needs — visual library, semantic layer, Gold tables, frame scores, ROF zone methodology, Stoop POI pipeline, publisher. Issue 1 is composition work. Build new only where nothing fits, and when you do, build it upstream as a reusable engine.

**Published issues are dated artifacts.** No automatic backfill of old markets when new theme engines land.

---

## Why the Spine Is Non-Negotiable

The Fixed Spine is the entire reason this is a product rather than a blog:

- Readers build pattern recognition issue to issue. A radar shape only means something if the axes are in the same order every time.
- Benchmarking requires a baseline. "An unusually high share of transitioning zones" is only a finding if the zone archetypes are the same labels across every market run to date.
- Market #3 must compound on market #1. Without shared structure, it doesn't.

Fixed Spine elements (per the template): Market Verdict, fingerprint radar + locked axis order + percentile table, LQ quadrant + exposure scorecard, benchmarked zone composition bar, corridor stat blocks.

---

## Lock Once vs. Discover Per Market

Every Act has two kinds of work. Do the locks deliberately. If market #1 is allowed to pick the fingerprint KPIs by convenience, it has set the standard for all future markets by accident. The below tables are some examples of what get locked and what get discovered per Act.

| Act | Lock once (propagates forever) | Discover per market |
|---|---|---|
| **1 — Identity** | Radar KPI selection + axis order | History box angle; which peer to feature; forward-analog |
| **2 — Engine & Fabric** | LQ quadrant chart; exposure scorecard *structure* | Which specializations to narrate; which exposure theme to deep dive; commute geography treatment |
| **3 — Dynamics** | Converging / diverging / inflecting framing | Which series lead; the Data Take pick |
| **4 — Opportunity Funnel** | Archetype names; Investment Score threshold; zone method | Which corridors get named |

All per-market analytical freedom lives in the right column. Market #1 is therefore partly a consolidation exercise: it forces the thematic work to firm up into reusable engines.

---

## Build Order: Act 2 → 1 → 3 → 4

Not sequential by act number. Ordered by leverage.

1. **Act 2 (Engine & Fabric)** — the analytical heart. Highest downstream reuse. The LQ quadrant and scorecard shell get built once here; whichever exposure theme market #1's data motivates becomes the first entry in the theme library.
2. **Act 1 (Identity)** — the radar is quick once the KPIs are chosen. The work is editorial (locking axis order), not analytical.
3. **Act 3 (Dynamics)** — the time-series engine; indexed metro-vs-national + programmatic inflection detection.
4. **Act 4 (Opportunity Funnel)** — last. Carries the open methodology (zone clustering, Investment Score threshold). Ship serialized without it if it isn't ready; debut it on market #2 if needed.

**Corollary:** Act 4 being unbuilt does not gate the report. Overview + Acts 1–3 is a valid first issue.

---

## What We're Actually Building: Engines, Not Sections

The durable output of each Act is a reusable engine, not a one-market section. The template names three; each Act is mostly composition on top of them.

| Engine | Serves | What it is |
|---|---|---|
| **Distance** | §3 peers, §8 cluster interpretation | z-scored feature vectors + cosine similarity |
| **Spatial** | §5, §8, §9 | OSM/Overpass ingestion + adjacency graph + per-zone metrics |
| **Time series** | §6, §7, trend inputs to §9 | indexed metro-vs-national + inflection detection |

---

## Themes: Chosen Per Market, Reused Across Markets

The spine sets the core KPIs and structures. **Which theme gets deep-dived is a per-market decision made when we see the data.** One market's story is AI exposure; another's is migration; another's is housing supply. We don't pre-assign.

Once a theme engine is built for one market, it joins a library available to every subsequent market. **The library accretes. Nothing is front-loaded.**

| Theme | Engine it produces | Spine section it feeds |
|---|---|---|
| AI & Jobs | NAICS → exposure crosswalk | §4 exposure scorecard |
| Housing | Supply/burden benchmark distributions; overheating heuristic | §1 housing pillars; §6 permits vs. pop growth |
| Migration & Population | Flow decomposition; origin breadth | §1 fingerprint; §8 archetypes |
| Investment | Investment Score | §8–§10 (the Funnel) |

**The transpose relationship.** A national thematic piece and a per-market deep dive are the same computation at two grains:

- National = one theme across all 401 CBSAs
- Market = one CBSA across all themes

So the theme engine built because market #1's data demanded it also yields the standalone national thematic post, *and* is available to market #2 onward. **Build once, ship three ways.** This dissolves the build-vs-write tension: thematic work and market work are the same work.

---

## The Flywheel

Market-first is the default direction:

```
market data surfaces an interesting theme
    → build the theme engine
        → deep dive section in that issue
            → standalone national thematic post
                → available to every remaining market
```

Themes are neither strictly upstream nor downstream of the markets. A theme can also arrive pre-built (Housing is already in flight) and simply be *available* when a market's data calls for it. Both directions are legitimate; discovery-driven is the default.

---

## Three Tiers of Depth

Not everything interesting in a market deserves the same weight. Three distinct slots, deliberately different sizes:

| Tier | What triggers it | Budget | Output |
|---|---|---|---|
| **Spine** | Every market, always | Fixed format | Comparable series |
| **Theme deep dive** | The market's data makes a theme the story | One substantial section per issue | A reusable engine + a national post |
| **Data Take** | Outlier scan flags something *surprising given the archetype* | One chart, ~100 words, boxed. 1–2 per issue | A hook; possibly the seed of a future theme |

The **Data Take** is the automated outlier scan: flag every Gold KPI where the metro sits in the national top or bottom decile, then hand-pick the one that surprises. (A cheap market being cheap is not a Data Take. A cheap market with top-decile income growth is.) Its strict budget is what keeps ad hoc analysis bounded — unbounded "this metro is interesting on X" is how a comparable series decays back into ad-hoc blogging.

**A Data Take that keeps recurring across markets is a theme candidate.** That's the promotion path between tiers.

Route all market-specific color into rotating slots (theme section, Data Take, History Box, Peer forward-analog). Never into fixed sections. The radar says *nothing else, resist additions* — take that literally.

---

## Published Issues Are Dated Artifacts

The goal is to publish. Once an issue ships, we do not go back and retrofit it with theme engines built for later markets.

This means later issues will be richer on any given dimension than earlier ones. That is accepted, not a defect — the spine is what holds the series comparable, and the spine is present in every issue from the first. Theme depth was never the comparability layer.

A retroactive sweep across published markets is possible eventually, as a deliberate project. It is never automatic and never blocks a new issue.

---

## Reuse First

**Default to existing repo work. Build new only where nothing fits.** Almost every component of the Deep Dive already exists somewhere in the platform; the job is composition, not greenfield construction.

| Need | Reuse |
|---|---|
| Charts | `visual_library/` — 15 chart types, spec + prep/render layer already built |
| Metrics, tables, joins, chart rules | `foundations/semantic_layer/` YAML catalogs |
| Underlying data | Gold layer (14 tables) — no new ingestion for issue 1 |
| Frame scores, clusters, similarity | `exploration/intelligence_framework/outputs/*.parquet` |
| Distance engine (§3 peers) | Cosine similarity already implemented for frame similarity |
| Zone clustering + parcel screen | ROF Jacksonville notebook sequence (`markets/jacksonville/`) |
| POI / spatial layer (§5) | Stoop `rental_area_search` POI pipeline; JAX POI data already exists |
| Daily Insights charts + posts | `publisher/` pipeline and its three skills |
| Theme definitions | `theme_catalog.yml` |

**Corollary on market selection:** Jacksonville's reuse surface is unusually deep — ROF zone/parcel methodology *and* Stoop POI coverage both already exist for it. That is a real argument for it as market #1, independent of narrative appeal.

**Corollary on new engines:** when a theme deep dive does require new work, build it as a reusable engine in the shared layer — not as a one-off notebook inside a market folder. Market folders hold narrative and market-specific parameters. Engines live upstream.

---

## Frames vs. Acts: Keep the Levels Distinct

Two organizational systems are now in play. They are not the same list and must not be silently collapsed:

- **Frames** (Character / Livability / Opportunity) = **how we compute.** The Intelligence Layer, the scoring models, the analytical inputs.
- **Acts** (Identity / Engine & Fabric / Dynamics / Opportunity Funnel) = **how we publish.** The delivery structure of an issue.

Adopting the template means Acts win as the delivery structure and Frames become analytical inputs feeding into sections. This is a deliberate evolution — Acts read better for a general audience — not a renaming.

---

## Publishing Shape

**The market is the series.** Do not publish one 4,000-word monolith. Ship a single market as frame-sized posts over a 6–8 week Substack arc — each standalone, each compounding — then a synthesis that ties them together.

**Daily Insights runs underneath regardless.** The publisher pipeline is the cadence heartbeat; charts pull directly from the market currently under analysis. A figure from the Act 3 work becomes an X post the same week. The flagship feeds the heartbeat instead of competing with it.

**LinkedIn is milestone-triggered, not scheduled.** It fires when there is a shipped thing to narrate — first Area Explorer, Stoop launch, first completed Deep Dive — paired with a methodology piece.

---

## Open Items

- [ ] **Market #1 selection.** Jacksonville (existing ROF work, known data, risk of feeling like old work) vs. a fresh market (Richmond, Louisville, Pittsburgh — more narrative energy, proves the template generalizes). Motivation beats convenience for a solo shop.
- [ ] **Lock the fingerprint KPIs and radar axis order.** Propagates to every future issue.
- [ ] **Source any theme engine from the primary index, not from memory.** For AI exposure that means Felten et al. / Webb / Goldman, cited explicitly in the methodology note. Every subsequent market inherits whatever we build.
- [ ] **Confirm archetype names before publishing.** Renaming later breaks series continuity.
- [ ] **Define the Investment Score threshold** for corridor qualification; document it.
- [ ] **Diagnose the JAX zone clustering failure mode** before committing to a method. HDBSCAN is the leading candidate; rule-calibrated DBSCAN second; SKATER third.
- [ ] **Decide: Zones in issue 1, or debut on market #2?** Overview + Acts 1–3 is a valid first cut.