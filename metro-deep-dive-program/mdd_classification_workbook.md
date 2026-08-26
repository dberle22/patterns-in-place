# Metro Deep Dive — Program-Aligned Workbook

Working workbook for organizing Metro Deep Dive in the same order that
[metro_deep_dive_program.md](./metro_deep_dive_program.md) describes it.

The core logic is:

1. `Issues` define the output shape.
2. `Analyses` fill those outputs.
3. `Engines` support those analyses.
4. Existing notes, specs, apps, and partial builds are audited as source material for the above.

So yes: the right backward path is a combination of `issue contents` and
`analysis families / questions / themes`, and then we identify what parts of the
`engine` layer are required to support them.

The intended flow for this workbook is:

`Issue section / output`
-> `Analysis family`
-> `Specific analysis, question, or theme`
-> `Required engine pieces`
-> `Current notes / builds / queries`
-> `Promotion path if reused`

## Source map

Use these when we do not know an answer and need to audit what already exists.

| Source Doc | Primary use |
|---|---|
| `metro-deep-dive-program/metro_deep_dive_program.md` | Canonical program shape: layers, families, routing, engines, acts |
| `metro-deep-dive/templates/metro_deep_dive_template_guidance.md` | Issue acts, sections, and fixed delivery spine |
| `metro-deep-dive/metro_deep_dive_build_approach.md` | Build order, lock-once decisions, engine framing |
| `metro-deep-dive/docs/analysis_program.md` | Thematic analyses |
| `metro-deep-dive/docs/deep_dive_question_bank.md` | Explanation questions |
| `metro-deep-dive/docs/intelligence_framework_review_question_bank.md` | Framework review and unresolved method questions |
| `metro-deep-dive/RESEARCH_TOOL_ROADMAP.md` | Existing Position-oriented builds and tabs |
| `metro-deep-dive/metro-area-explorer/industry/SPEC_INDUSTRY.md` | Current industry-specific build state and deliverables |
| `metro-deep-dive/metro-area-explorer/industry/POI_INFRA_PROPOSAL.md` | Current spatial / POI proposal state |
| `metro-deep-dive/metro-area-explorer/place_intelligence/SPEC_PLACE_INTELLIGENCE.md` | Place Intelligence use/product framing |
| `metro-deep-dive/metro-area-explorer/place_intelligence/METHODS_MEMO.md` | Place Intelligence methods and open tradeoffs |
| `metro-deep-dive/metro-area-explorer/place_intelligence/TECHNICAL_ARCHITECTURE.md` | Place Intelligence pipeline and architecture |

## 1. Issue Spine

This is the output side of the program. Start here.

| Issue Layer | Act / Section | Reader-facing output | Notes |
|---|---|---|---|
| Issue | Opening / Market Verdict | Opening synthesis |  |
| Issue | Act 1 / Identity | Overall identity act |  |
| Issue | Act 1 / Market Fingerprint | Fingerprint KPIs, radar, percentile table, stat boxes |  |
| Issue | Act 1 / History Box | Historical context |  |
| Issue | Act 1 / Peer Markets | Peer list and comparison framing |  |
| Issue | Act 2 / Engine and Fabric | Overall engine/fabric act |  |
| Issue | Act 2 / Industry Makeup and Regional Role | Sector structure and regional role |  |
| Issue | Act 2 / Built Environment and Social Fabric | Built environment and social fabric interpretation |  |
| Issue | Act 3 / Dynamics | Overall dynamics act |  |
| Issue | Act 3 / Trend Analysis | Reader-facing change and direction |  |
| Issue | Act 3 / Data Take Sidebar | Small boxed finding |  |
| Issue | Act 4 / Opportunity Funnel | Overall funnel act |  |
| Issue | Act 4 / Zone Archetypes | Internal structure and zone interpretation |  |
| Issue | Act 4 / Zone Corridors | Corridor identification and comparison |  |
| Issue | Act 4 / Parcel Watch | Parcel-level follow-through |  |

## 2. Issue -> Analysis Map

This is the main planning table.

For each issue output, ask:

- which analysis family does it come from?
- what specific analysis, question, or theme supplies it?
- what still needs to be discovered per market?

### Act 1 working asset list

We agreed to split `Act 1` into explicit reader-facing assets rather than keep
`Market Fingerprint` bundled as a single row.

| Act 1 asset | Why it deserves its own lineage | Notes |
|---|---|---|
| Top-line stat boxes | Headline market facts and locked summary fields |  |
| Fingerprint KPI set | Canonical selected KPI set underneath multiple Act 1 outputs | Curated subset from the three-frame intelligence framework, then promoted into a locked fingerprint asset |
| Fingerprint radar | Specific visual packaging of the fingerprint KPI set |  |
| Fingerprint percentile table | Tabular packaging of the fingerprint KPI set |  |
| Intelligence Cluster Label | Core identity asset and framework-facing presentation object |  |
| Frame/topic interpretation summary | Reader-facing interpretation of what the framework says | Keep this lighter than the full underlying scaffolding for now |
| History Box | Historical context and market-specific angle |  |
| Peer set | Standard peer list asset |  |
| Featured peer comparison | Standard comparison asset used to make the peer set concrete | Required |
| Diverging peer / forward-analog candidate | Higher-signal peer interpretation and future comparison lead |  |
| Similarity / framework methods caveat | Required caveat layer for framework-backed claims |  |

| Issue Section / Output | Analysis Family | Specific analysis / question / theme | Why this belongs here | Market-specific or fixed? | Status | Notes / questions |
|---|---|---|---|---|---|---|
| Opening / Market Verdict |  |  |  |  |  |  |
| Act 1 / Market Fingerprint / Top-line stat boxes |  |  |  |  |  |  |
| Act 1 / Market Fingerprint / Fingerprint KPI set | Position | Profile |  |  |  |  |
| Act 1 / Market Fingerprint / Fingerprint radar | Position | Profile |  |  |  |  |
| Act 1 / Market Fingerprint / Fingerprint percentile table | Position | Profile |  |  |  |  |
| Act 1 / Market Fingerprint / Intelligence Cluster Label | Position | Profile |  |  |  |  |
| Act 1 / Market Fingerprint / Frame-topic interpretation summary | Position | Profile |  |  |  |  |
| Act 1 / History Box |  |  |  |  |  |  |
| Act 1 / Peer Markets / Peer set | Position | Peers |  |  |  |  |
| Act 1 / Peer Markets / Featured peer comparison | Position | Peers |  |  |  |  |
| Act 1 / Peer Markets / Diverging peer or forward-analog candidate | Position | Peers |  |  |  |  |
| Act 1 / Peer Markets / Similarity-framework methods caveat | Position | Peers |  |  |  |  |
| Act 2 / Industry Makeup and Regional Role | Thematic | A1 AI inversion |  |  |  |  |
| Act 2 / Industry Makeup and Regional Role | Explanation | Regional role |  |  |  |  |
| Act 2 / Built Environment and Social Fabric | Explanation | Q4 Daily-needs access |  |  |  |  |
| Act 2 / Built Environment and Social Fabric | Explanation | Q6 One metro? |  |  |  |  |
| Act 3 / Trend Analysis | Position | Trajectory |  |  |  |  |
| Act 3 / Trend Analysis | Thematic | Theme-specific dynamic read if routed |  |  |  |  |
| Act 3 / Data Take Sidebar |  |  |  |  |  |  |
| Act 4 / Zone Archetypes | Position | Internal structure |  |  |  |  |
| Act 4 / Zone Corridors | Explanation | Corridors |  |  |  |  |
| Act 4 / Zone Corridors | Explanation | Q2 Job-proximity gradient |  |  |  |  |
| Act 4 / Parcel Watch | Explanation | Parcel watch |  |  |  |  |

## 2.1 Act 3 and Act 4 dependency sketch

This is an intentionally light first pass.

The purpose is to identify which later-act assets likely depend on work that is
first assembled or interpreted in `Act 2`, so we can design `Act 2` as an
upstream analytical layer rather than just a standalone editorial section.

| Later-act asset | Likely depends on Act 2? | Why / what likely carries forward | Notes to confirm later |
|---|---|---|---|
| Act 3 / Trend Analysis / trajectory read | Yes | Trend interpretation likely needs context from industry structure, regional role, and built environment constraints |  |
| Act 3 / Trend Analysis / theme-specific dynamic read | Yes | A routed theme may begin in Act 2 and then deepen into temporal change in Act 3 |  |
| Act 3 / Trend Analysis / diverging peer or forward-analog logic | Yes | Peer interpretation from Act 1 likely needs Act 2 context plus trend machinery |  |
| Act 3 / Data Take Sidebar | Yes | Best short finding may come from an Act 2 analysis result or an Act 3 trend result built on Act 2 context |  |
| Act 4 / Zone Archetypes / interpretation | Partial | Zone labels come from Position / Internal structure, but the interpretation of what they mean may rely on Act 2 market context |  |
| Act 4 / Zone Corridors / corridor identification | Yes | Corridor selection likely depends on built environment, amenity access, infrastructure, and job-center logic developed earlier |  |
| Act 4 / Zone Corridors / corridor narrative | Yes | Narrative will likely reuse Act 2 findings on industry, social fabric, access, and regional role |  |
| Act 4 / Parcel Watch / parcel targeting logic | Yes | Parcel targeting likely depends on which corridor or zone logic emerges from earlier acts |  |
| Act 4 / Parcel Watch / parcel narrative | Yes | Parcel opportunity story likely depends on prior explanations of access, job proximity, industry role, and social fabric |  |

### Provisional takeaway

At a high level, `Act 3` and `Act 4` look less like isolated acts and more like:

- `Act 3` = trend and direction layer built on top of Act 1 identity plus Act 2 explanation
- `Act 4` = narrowing and targeting layer built on top of Act 1 structure plus Act 2 explanation

This suggests `Act 2` should probably be designed as the main reusable
explanatory workbench, with later acts consuming and recombining its outputs.

## 3. Analysis Inventory By Family

This is the program layer in its own terms.

### 3.1 Position

| Analysis | Current build/source | Main outputs it can feed | Still internal-only? | Notes / audit needs |
|---|---|---|---|---|
| Profile |  |  |  |  |
| Peers |  |  |  |  |
| Trajectory |  |  |  |  |
| Internal structure |  |  |  |  |
| Candidate scan |  |  |  |  |
| Similarity neighborhood |  |  |  |  |

### 3.2 Explanation

| Analysis / Question | Current build/source | Main outputs it can feed | Routed by what signal? | Notes / audit needs |
|---|---|---|---|---|
| Q1 Supply or demand |  |  |  |  |
| Q2 Job-proximity gradient |  |  |  |  |
| Q3 Where growth lands |  |  |  |  |
| Q4 Daily-needs access |  |  |  |  |
| Q5 Afford to live near jobs |  |  |  |  |
| Q6 One metro? |  |  |  |  |
| Regional role |  |  |  |  |
| Corridors |  |  |  |  |
| Parcel watch |  |  |  |  |
| Catchment |  |  |  |  |

### 3.3 Thematic

| Theme / Entry | Current build/source | Main outputs it can feed | Runs in market mode, all-market mode, or both? | Notes / audit needs |
|---|---|---|---|---|
| A1 AI inversion |  |  |  |  |
| A2 Building lowers prices? |  |  |  |  |
| A3 Moving toward harm? |  |  |  |  |
| A4 Remote work rewired? |  |  |  |  |
| A5 How many downtowns? |  |  |  |  |
| A6 Specialization predicts growth? |  |  |  |  |
| A7 Who is squeezed? |  |  |  |  |
| A8 Geography of life expectancy |  |  |  |  |
| A9 Converging or diverging? |  |  |  |  |
| A10 Polarization |  |  |  |  |
| Housing satellite |  |  |  |  |
| CBSA similarity study |  |  |  |  |

## 4. Analysis -> Engine Requirements

Only after we know which analyses feed which outputs do we ask what engines are
required underneath.

| Analysis / Question / Theme | Required engine piece | Why required | Current state | Existing source/build | Promote to foundations later? | Notes |
|---|---|---|---|---|---|---|
| Profile | Intelligence Framework |  |  |  |  |  |
| Peers | Intelligence Framework |  |  |  |  |  |
| Trajectory | Intelligence Framework |  |  |  |  |  |
| Internal structure | Intelligence Framework |  |  |  |  |  |
| Q4 Daily-needs access | Spatial / POI |  |  |  |  |  |
| Q6 One metro? | Benchmarking / geography / workforce logic |  |  |  |  |  |
| Regional role | Benchmarking / geography / workforce logic |  |  |  |  |  |
| Corridors | Spatial / POI |  |  |  |  |  |
| Corridors | Geography |  |  |  |  |  |
| Parcel watch | Spatial / POI |  |  |  |  |  |
| Parcel watch | Geography |  |  |  |  |  |
| A1 AI inversion | Theme engine interface |  |  |  |  |  |
| A1 AI inversion | Benchmarking |  |  |  |  |  |
| Trend Analysis | Time series |  |  |  |  |  |
| Market-wide notebook config | Registries |  |  |  |  |  |

## 5. Existing Builds and Notes Audit

This is where we trace current material back into the program.

| Existing artifact | Best mapped to | Layer in program | Useful as-is, reference only, or needs translation? | What to audit for | Notes |
|---|---|---|---|---|---|
| `RESEARCH_TOOL_ROADMAP.md` | Position source material | Analysis |  |  |  |
| `Overview tab` | Profile / fingerprint source material | Analysis |  |  |  |
| `Peers tab` | Peers source material | Analysis |  |  |  |
| `Trajectory tab` | Trajectory source material | Analysis |  |  |  |
| `Zone Map tab` | Internal structure source material | Analysis |  |  |  |
| `Candidate List tab` | Candidate scan source material | Analysis |  |  |  |
| `analysis_program.md` | Thematic inventory | Analysis |  |  |  |
| `deep_dive_question_bank.md` | Explanation inventory | Analysis |  |  |  |
| `SPEC_INDUSTRY.md` | A1 / industry implementation source | Analysis / Engine |  |  |  |
| `POI_INFRA_PROPOSAL.md` | Spatial / POI source | Engine |  |  |  |
| `SPEC_PLACE_INTELLIGENCE.md` | Catchment / place-use source | Analysis / Engine |  |  |  |
| `METHODS_MEMO.md` | Catchment / barrier / node methods | Engine |  |  |  |
| `TECHNICAL_ARCHITECTURE.md` | Place Intelligence pipeline source | Engine |  |  |  |
| `metro_deep_dive_build_approach.md` | Build order / lock-once / engine framing | Issue / Engine |  |  |  |
| `metro_deep_dive_template_guidance.md` | Issue spine | Issue |  |  |  |
| `intelligence_framework_review_question_bank.md` | Method audit and publishability constraints | Engine / Audit |  |  |  |

## 6. Reuse and Promotion Ledger

When something is needed by more than one analysis or output, track it here.

| Reusable piece | First discovered from | Used by | Current home | Desired home | Promotion trigger | Notes |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

## 7. Working Questions

These are the first questions I think we should answer together.

1. For `Act 1 / Market Fingerprint`, do we want to treat these as separate assets:
   `Fingerprint KPIs`
   `Radar`
   `Percentile table`
   `Top-line stat boxes`
   or keep them bundled for now under one fingerprint row?

2. For `Act 1 / Peer Markets`, what is the first-pass output we care about most:
   `peer list`
   `featured peer comparison`
   `diverging peer logic`
   `full similarity audit trail`

3. For `Act 3 / Trend Analysis`, do we want it to be driven primarily by:
   `Trajectory`
   or
   `Trajectory + time-series engine outputs`
   from the start?

4. For `Act 4 / Zone Corridors`, do we want to treat corridor detection as:
   `an Explanation analysis method`
   first,
   and only later promote it into an engine if reused?

5. Which issue section should we fully work backward first:
   `Market Fingerprint`
   `Peer Markets`
   `Trend Analysis`
   or
   `Zone Corridors`

## 8. Decisions Captured So Far

| Decision area | Current decision | Notes |
|---|---|---|
| Act 1 structure | Split Act 1 into separate assets rather than bundling Market Fingerprint and Peer Markets |  |
| Intelligence Cluster Label | Treat as its own Act 1 asset | Important enough to deserve its own lineage |
| Featured peer comparison | Required Act 1 asset | Standard intro to the intelligence framework |
| Fingerprint KPI lineage | Define from framework structure first, then trace to current query outputs, then package for readers | Do not start from presentation slots |
| Fingerprint KPI definition | Curated subset of KPIs from across the three intelligence frames, then promoted into a locked fingerprint asset | See `exploration/intelligence_framework/docs/intelligence_framework_overview.md` |
| Fingerprint KPI organization | Organize as `frame -> topic -> KPI`, then choose market-specific subsets for radar/table packaging | Do not force even representation across frames |
| Fingerprint asset packaging | Keep a broader core KPI pool in the fingerprint set; radar and tables can select the best KPIs for a given market | Presentation can vary by market while staying grounded in the same pool |
| Fingerprint KPI pool boundary | Define a governed `Act 1 candidate pool` that is smaller than the full framework but broad enough to support any KPI we would realistically use in Act 1 | This can become a reusable base data frame across multiple Act 1 assets |
| Intelligence Cluster Label structure | Use `primary label + supporting label set` | Likely cross-frame headline with frame-level supporting labels, but final display choice can wait until build |
| Intelligence Cluster Label lineage | Track both `phase build artifacts` and `promoted mart_intelligence outputs` | Preserve the distinction between build truth and product read layer while promotions are still in motion |
| Peer set structure | Default to primary peers from cross-frame cosine similarity, with secondary peer sets for each individual frame | Cross-frame peers are the main Act 1 identity peer surface |
| Diverging peer / forward-analog placement | Treat as a light higher-order interpretation in Act 1, but define the real analytical logic in Act 3 / Trend Analysis | Most of the actual work belongs with trend and trajectory machinery |
