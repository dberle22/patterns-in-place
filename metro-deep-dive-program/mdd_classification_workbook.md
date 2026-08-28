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

Working shorthand for the later acts:

- `Act 2` = what this market is and how it works
- `Act 3` = how this market is changing
- `Act 4` = where inside the market the structure and opportunity are

One nuance to keep in mind:

- `Act 2` can include regional framing, but it is not primarily a time/trend act
- `Act 3` is where explicit dynamics and trend interpretation belong
- `Act 4` is the intra-CBSA narrowing layer: zones, corridors, and sometimes parcels
- `Act 4` should still be legible through the three Intelligence frames, not just through an opportunity lens

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
| Top-line stat boxes | Headline market facts and locked summary fields | Presentation subset of the Fingerprint KPI set; likely locked later at the issue layer |
| Fingerprint KPI set | Canonical selected KPI set underneath multiple Act 1 outputs | Curated subset from the three-frame intelligence framework, organized as `frame -> topic -> KPI`, then promoted into a locked fingerprint asset |
| Fingerprint radar | Specific visual packaging of the fingerprint KPI set | Market-specific selection from the broader Act 1 candidate pool |
| Fingerprint percentile table | Tabular packaging of the fingerprint KPI set | Market-specific selection from the broader Act 1 candidate pool |
| Intelligence Cluster Label | Core identity asset and framework-facing presentation object | Use `primary label + supporting label set`; likely cross-frame headline with frame-level supporting labels |
| Frame/topic interpretation summary | Reader-facing interpretation of what the framework says | Keep this lighter than the full underlying scaffolding for now |
| History Box | Historical context and market-specific angle | Editorial/research asset rather than framework-derived data asset |
| Peer set | Standard peer list asset | Primary peers from cross-frame cosine similarity, with frame-specific peers as supporting surfaces |
| Featured peer comparison | Standard comparison asset used to make the peer set concrete | Required |
| Diverging peer / forward-analog candidate | Higher-signal peer interpretation and future comparison lead | Light Act 1 interpretation; real analytical home is Act 3 |
| Similarity / framework methods caveat | Required caveat layer for framework-backed claims | Needed because peer and cluster claims inherit open framework-method questions |

### Act 3 working asset list

This is the first pass at the reader-facing assets inside `Act 3 / Dynamics`.

The goal here is to separate:

- the reusable dynamic analysis layer
- the specific editorial packaging we may choose issue by issue

| Act 3 asset | Why it deserves its own lineage | Notes |
|---|---|---|
| Trend series candidate pool | Base pool of time-series measures that could lead the act | Likely broader than what appears in the final issue |
| Lead trend panel set | The selected 4 to 6 small-multiple panels for the issue | Presentation subset from the candidate pool |
| Converging / diverging / inflecting classifications | Core interpretation layer that keeps the act from becoming generic line charts | Should likely be reusable across multiple themes and markets |
| Inflection flags | Programmatic detection of meaningful recent slope changes | Feels like a direct engine output rather than just editorial packaging |
| Regional context comparison | Explains whether the metro is following or bucking its region | May reuse peer or division context rather than only national benchmarking |
| Theme-specific dynamic read | Trend interpretation tied to the routed thematic analysis | Likely inherits context from Act 2 |
| Diverging peer / forward-analog interpretation | More advanced comparative reading of trend paths | Light mention in Act 1, real analytical home here |
| Data Take candidate pool | Pool of weird / surprising outlier candidates | Could become a repeatable promotion path into themes or recurring spines |
| Data Take selected asset | The specific boxed weird-on-X finding chosen for the issue | Editorial selection from the candidate pool |

### Act 4 working asset list

This is the first pass at the reader-facing assets inside
`Act 4 / Opportunity Funnel`.

Working distinction:

- `zones` = clustered tract structures built from tract similarity plus geographic proximity
- `corridors` = selected, opportunity-relevant or otherwise analytically meaningful zone groupings that are close and related, but not necessarily strictly contiguous

This keeps the zone model distinct from the later narrowing/selection layer.

| Act 4 asset | Why it deserves its own lineage | Notes |
|---|---|---|
| Zone archetype map | Core spatial presentation of internal structure | Tract view is required; ZCTA and place rollups are desirable future legibility layers |
| Zone composition benchmark bar | Turns zone composition into a comparative finding | Target national sample if feasible; otherwise use the best practical comparison set |
| Zone interpretation summary | Explains what the market's mix suggests through Character, Livability, and Opportunity lenses | Depends on internal structure plus broader market context |
| Corridor candidate pool | Set of potential corridors before editorial narrowing | Likely built from zones + infrastructure + access + trend signals |
| Corridor identification method | Core logic for what counts as a corridor | Start with tract similarity + geographic proximity; infrastructure can enter later as overlay or model input |
| Corridor stat blocks | Standardized comparable corridor summary object | Feels like a lock-once issue asset built on reusable analysis outputs |
| Corridor narrative thesis | One-line explanation of why each corridor matters | Should stay readable through the three core frames, not just opportunity |
| Parcel candidate pool | Set of potential parcels within the chosen corridor(s) | Conditional on data availability |
| Parcel screening logic | Reusable logic for underutilized parcel identification | May connect to ROF and other downstream products later |
| Parcel Watch table/map asset | Final parcel-level presentation output | Conditional presentation asset |

| Issue Section / Output | Analysis Family | Specific analysis / question / theme | Why this belongs here | Market-specific or fixed? | Status | Notes / questions |
|---|---|---|---|---|---|---|
| Opening / Market Verdict |  |  |  |  |  |  |
| Act 1 / Market Fingerprint / Top-line stat boxes | Position | Profile | Headline presentation subset of the fingerprint data asset | Likely fixed subset later; do not over-lock yet | Planned | Treat as packaging of the fingerprint pool rather than a separate data class |
| Act 1 / Market Fingerprint / Fingerprint KPI set | Position | Profile | Governing Act 1 candidate pool that supports multiple identity assets | Fixed base pool; displayed subset can vary by market | In progress | Define from framework structure first, then trace to current query outputs |
| Act 1 / Market Fingerprint / Fingerprint radar | Position | Profile | Visual expression of the fingerprint for quick pattern recognition | Market-specific selection from fixed candidate pool | Planned | Do not define from presentation slots first |
| Act 1 / Market Fingerprint / Fingerprint percentile table | Position | Profile | Tabular expression of the fingerprint for more precise comparison | Market-specific selection from fixed candidate pool | Planned | Likely shares the same base data frame as radar and stat boxes |
| Act 1 / Market Fingerprint / Intelligence Cluster Label | Position | Profile | Core identity label connecting Act 1 to the Intelligence Framework | Fixed asset structure; final display choice can wait | In progress | Track both phase-build truth and promoted mart read layer |
| Act 1 / Market Fingerprint / Frame-topic interpretation summary | Position | Profile | Reader-facing interpretation of what the framework says without exposing the full scaffolding | Market-specific interpretation on top of fixed framework structure | Planned | Keep lighter than full frame/topic machinery for now |
| Act 1 / History Box | Editorial research | External research and writing | Adds market-specific historical context that does not come from the framework | Market-specific | Planned | Keep outside the modeled data lineage |
| Act 1 / Peer Markets / Peer set | Position | Peers | Standard identity peer surface for showing what else is like this metro | Fixed structure; actual peers vary by market | In progress | Use cross-frame cosine similarity as primary; frame peers as secondary |
| Act 1 / Peer Markets / Featured peer comparison | Position | Peers | Makes the peer set concrete with one comparison the reader can hold onto | Market-specific within a required asset slot | Planned | Exact selection rule can wait until build |
| Act 1 / Peer Markets / Diverging peer or forward-analog candidate | Position | Peers | Adds higher-order interpretation beyond the plain peer list | Market-specific | Planned | Light Act 1 interpretation; fuller logic should be defined in Act 3 |
| Act 1 / Peer Markets / Similarity-framework methods caveat | Position | Peers | Preserves honesty about open framework-method questions behind peer claims | Fixed caveat class; wording may lock later | In progress | Needed until similarity validation and universe questions are resolved |
| Act 2 / Industry Makeup and Regional Role | Thematic | A1 AI inversion |  |  |  |  |
| Act 2 / Industry Makeup and Regional Role | Explanation | Regional role |  |  |  |  |
| Act 2 / Built Environment and Social Fabric | Explanation | Q4 Daily-needs access |  |  |  |  |
| Act 2 / Built Environment and Social Fabric | Explanation | Q6 One metro? |  |  |  |  |
| Act 3 / Trend Analysis / Trend series candidate pool | Position + Thematic | Trajectory + routed theme context | Base pool of time-series measures that can support the market's dynamics read | Fixed candidate pool structure; actual selected series vary by market | In progress | Start with `population`, `permits`, `home prices`, `rents`, `employment`, `wages`, `income`; organize by data family |
| Act 3 / Trend Analysis / Lead trend panel set | Position + Thematic | Trajectory + routed theme context | Reader-facing 4 to 6 panel set that turns the broader trend pool into the market's main dynamics story | Market-specific selection from the candidate pool | Planned | Select by strongest explanatory value for the market rather than one-per-family rules |
| Act 3 / Trend Analysis / Converging-diverging-inflecting classifications | Position | Trajectory | Useful framing layer for interpreting series consistently across markets | Market-specific output from a reusable method | Planned | Helpful but not the primary Act 3 asset; avoid reducing the whole act to this classification alone |
| Act 3 / Trend Analysis / Inflection flags | Position | Trajectory | Programmatic signal for where recent slope changes are strong enough to matter | Reusable method; market-specific outputs | In progress | Treat as engine output rather than pure issue packaging |
| Act 3 / Trend Analysis / Regional context comparison | Position + Thematic | Trajectory + routed theme context | Every dynamic read should show whether the market follows or bucks its broader region and peer context | Required context class; exact comparison values vary by market | In progress | Lives underneath each trend or dynamic read rather than as a standalone section; default to Census Division plus nearby and similar metros |
| Act 3 / Trend Analysis / Theme-specific dynamic read | Thematic | Routed theme read over time | Shows how the routed Act 2 theme is changing over time rather than only how it looks today | Conditional on routed theme strength | Planned | Example shape: current industry structure in Act 2, then strengthening/weakening/shifting in Act 3 |
| Act 3 / Trend Analysis / Diverging peer or forward-analog interpretation | Position + Thematic | Peers + Trajectory + routed theme context | Higher-order comparative dynamics layer explaining where the market may be heading or why similar metros are splitting apart | Conditional; present only when signal is strong enough | Planned | Main reusable component is the comparison method; reuse Act 1 peer sets |
| Act 3 / Data Take Sidebar / Data Take candidate pool | Position + Thematic + Explanation | Analysis/question-derived findings | Pool of possible short findings that emerge from actual analyses rather than generic outlier scanning | Market-specific | In progress | Data Takes should come from what proves interesting in the analyses and question bank work |
| Act 3 / Data Take Sidebar / Data Take selected asset | Position + Thematic + Explanation | Selected analysis/question-derived finding | Final boxed finding when a market yields a genuinely interesting short take | Conditional | Planned | Do not manufacture these; only include when there is a real reason |
| Act 4 / Zone Archetypes / Zone archetype map | Position | Internal structure | Core tract-level structure asset that lets us see how the metro organizes internally | Required tract view; ZCTA/place rollups are future extensions | In progress | Align to the Intelligence Framework at a lower geography level rather than inventing a disconnected typology |
| Act 4 / Zone Archetypes / Zone composition benchmark bar | Position | Internal structure | Converts the zone mix into a comparative finding rather than a legend | Fixed comparison asset; benchmark values vary by market | Planned | Target a national sample if technically feasible; otherwise use a practical comparison baseline |
| Act 4 / Zone Archetypes / Zone interpretation summary | Position + Explanation | Internal structure + routed explanatory context | Interprets what the market's internal structure means through Character, Livability, and Opportunity lenses | Market-specific interpretation on top of a reusable zone model | Planned | Not just opportunity concentration; this is where the three-frame geography becomes legible |
| Act 4 / Zone Corridors / Corridor candidate pool | Explanation | Corridors | Creates the broader set of plausible corridor-level opportunity or structure targets before narrowing | Market-specific pool from reusable methods | Planned | Built from zones plus proximity, with infrastructure/access/trend overlays as available |
| Act 4 / Zone Corridors / Corridor identification method | Explanation | Corridors | Defines how tract-derived zones become meaningful higher-order groupings | Reusable method; market-specific outputs | In progress | Distinguish from zone model: corridors are selected related groupings, not necessarily strictly contiguous |
| Act 4 / Zone Corridors / Corridor stat blocks | Explanation | Corridors | Standard comparable summary object for selected corridors | Fixed issue asset built from market-specific corridor outputs | Planned | Feels like a lock-once packaging layer on top of reusable corridor logic |
| Act 4 / Zone Corridors / Corridor narrative thesis | Explanation | Corridors + Q2 Job-proximity gradient + Q4 Daily-needs access | Explains why a corridor matters using the strongest combination of structure, access, role, and trend signals | Market-specific | Planned | Should remain interpretable through the three Intelligence frames, not just pure investment language |
| Act 4 / Parcel Watch / Parcel candidate pool | Explanation | Parcel watch | Creates the optional set of parcels worth deeper review inside selected corridors | Conditional and market-specific | Planned | Downstream extension of corridor logic rather than a co-equal required component |
| Act 4 / Parcel Watch / Parcel screening logic | Explanation | Parcel watch | Reusable logic for identifying underutilized parcels once corridor scope exists | Reusable method; conditional outputs | Planned | Can align to ROF/shared parcel logic as an input but still allow MDD-specific customization |
| Act 4 / Parcel Watch / Parcel Watch table-map asset | Explanation | Parcel watch | Final parcel-level presentation asset when parcel data and signal are strong enough | Conditional | Planned | Only run when warranted; do not force parcel work into every market |

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

6. For `Act 3 / Trend Analysis`, do we want the base unit to be:
   `series`
   `framing classification`
   or
   `panel`
   My instinct is `series` first, because the panels are downstream packaging.

7. For `Act 4 / Zone Corridors`, do we want to keep:
   `corridor candidate pool`
   and
   `corridor stat blocks`
   separate from the start?
   My instinct is yes, because one is reusable analytical output and the other is a standardized issue asset.

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
