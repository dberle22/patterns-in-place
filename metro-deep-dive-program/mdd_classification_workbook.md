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

The build sequence uses that lineage to decide which Engine or component must
be ready before the next analysis notebook can run. The notebook should expose
viewable outputs early; Issues are assembled later from the analyses that prove
useful.

Scaffold rule for the new build tree:

- scaffold by `engines`, `analyses`, and `issues`
- do not scaffold by acts at the top level
- keep reusable act-level builders inside `analyses/`
- keep `issues/` focused on market-specific assembly, decisions, and output planning
- use `issues/_shared/` for shared issue-facing conventions and specs
- build the new tree first inside `metro-deep-dive-program/` so it stays clearly separated from the legacy `metro-deep-dive/` structure

Working shorthand for the later acts:

- `Act 2` = what this market is and how it works
- `Act 3` = how this market is changing
- `Act 4` = where inside the market the structure and opportunity are

Full act shorthand:

- `Act 1` = who this market is
- `Act 2` = what this market is and how it works
- `Act 3` = how this market is changing
- `Act 4` = where inside the market the structure and opportunity are

One nuance to keep in mind:

- `Act 1` is the identity layer: fingerprint, cluster labels, peer set, and light framework interpretation
- `Act 2` can include regional framing, but it is not primarily a time/trend act
- `Act 3` is where explicit dynamics and trend interpretation belong
- `Act 4` is the intra-CBSA narrowing layer: zones, corridors, and sometimes parcels
- `Act 4` should still be legible through the three Intelligence frames, not just through an opportunity lens

How they fit together:

- `Act 1` gives identity
- `Act 2` gives explanation
- `Act 3` gives change over time
- `Act 4` gives internal geographic targeting

Another useful shorthand:

- `Act 1` = what kind of place is this?
- `Act 2` = why does it work this way?
- `Act 3` = how is it moving?
- `Act 4` = where exactly is the action inside it?

Important nuance:

- the `acts` are best understood as output lenses
- the `questions`, `themes`, `datasets`, and `methods` can cut across multiple acts
- the goal of this workbook is to make those overlaps visible, not to force every question into a single act

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
| `metro-deep-dive/metro-area-explorer/industry/POI_INFRA_PROPOSAL.md` | Current POI and infrastructure proposal state |
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
| Issue | Act 4 / Zone Structures | Corridor/district identification and comparison |  |
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

### Act 2 working asset list

This is the first pass at the reader-facing and analytical assets inside
`Act 2 / Engine and Fabric`.

The organizing idea here is:

- start from `analysis questions`
- map them into `component groups`
- use the component groups as reusable capability buckets

Component groups are not strict ownership buckets. They are the reusable
capabilities that help us answer multiple questions and themes.

Starting component groups:

- `industry / economic engine`
- `regional role`
- `built environment`
- `social fabric`
- `access / amenities`
- shared `comparison / benchmarking` method underneath multiple components

| Act 2 asset | Why it deserves its own lineage | Notes |
|---|---|---|
| Deeper market KPI/profile tables | Core Act 2 baseline that goes deeper than Act 1 identity | Built from component-specific datasets and question-specific cuts |
| Benchmark comparison layer | Shared comparison method used across Act 2 questions and themes | Reuse national, Census Division, peer set, and sometimes nearby-metro comparisons |
| Industry / economic makeup analysis | Explains how the market's industries and economic base are structured | Separate from regional role |
| Regional role analysis | Explains how the market fits into its broader region through commuting, infrastructure, and comparative role | Cross-cutting capability, not just one question |
| Built environment analysis | Explains infrastructure, building types, land use, and physical market form | Can contain multiple sub-components with separate inputs and outputs |
| Access / amenities analysis | Explains what amenities exist and how accessible they are | Closely related to built environment but analytically distinct |
| Social fabric analysis | Explains cultural anchors, civic institutions, neighborhood character, and social capital signals | Keep these subcomponents distinguishable from the start |
| Theme analysis slot | Lets routed thematic analyses sit alongside explanation questions | A1 is the first instance; more can follow |
| Explanation question slot | Lets standardized market questions sit alongside themes | Questions can be market-specific in selection, standardized in build method |

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

- `zone types` = nationally consistent Phase 7 tract classifications built
  from the governed tract feature vector
- `structural candidates` = reproducible within-market groupings with same-zone
  cores, optional bridge tracts, and a corridor or district form
- `featured candidates` = issue-selected corridors or districts interpreted with relevant
  POI, infrastructure, access, trend, or other explanatory evidence

This keeps the zone model distinct from the later narrowing/selection layer.

| Act 4 asset | Why it deserves its own lineage | Notes |
|---|---|---|
| Place and zone structure | Establishes how counties, Census Places, tracts, ZCTAs, and national tract types fit together | Preserve allocation basis, unincorporated coverage, and both directions of the Place × Zone relationship |
| Activity and infrastructure structure | Shows where POIs, anchors, employment centers, and physical networks sit in the market geography | Broad exploratory context, not an access, commuting, or causal claim |
| Zone archetype map | Core tract-level presentation of one internal-structure layer | Tract view is required; Place and ZCTA views provide complementary legibility |
| Zone composition benchmark bar | Turns zone composition into a comparative finding | Target national sample if feasible; otherwise use the best practical comparison set |
| Zone interpretation summary | Explains what the market's mix suggests through Character, Livability, and Opportunity lenses | Depends on internal structure plus broader market context |
| Structural candidate pool | Set of potential corridors and districts before editorial narrowing | Built from Phase 7, Geography, governed Infrastructure roles, aggregate POI composition, and conservative bridge rules |
| Corridor Intelligence method | Core engine logic for membership and corridor-versus-district form | Spec and build plan agreed under `engines/corridor_intelligence/`; optional Phase 7 DBSCAN work remains a challenger |
| Structural-candidate stat blocks | Standardized comparable corridor/district summary object | Feels like a lock-once issue asset built on reusable analysis outputs |
| Candidate narrative thesis | One-line explanation of why each selected candidate matters | Should stay readable through the three core frames, not just opportunity |
| Parcel candidate pool | Set of potential parcels within the chosen corridor or district | Conditional on data availability |
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
| Act 2 / Industry Makeup and Regional Role / Deeper market KPI-profile tables | Explanation + Thematic | Component-specific baseline tables across questions and themes | Gives Act 2 a deeper market baseline than Act 1 and feeds multiple question paths | Fixed capability class; exact contents vary by market and question | In progress | Think of this as reusable component datasets rather than one-off issue tables |
| Act 2 / Industry Makeup and Regional Role / Benchmark comparison layer | Explanation + Thematic | Shared comparison and benchmarking method | Reusable comparison layer across Act 2 questions so each analysis does not reinvent regional and peer comparisons | Reusable method; market-specific outputs | In progress | Should support national, Census Division, Act 1 peer set, and sometimes nearby metros; likely points toward shared geo rollup assets |
| Act 2 / Industry Makeup and Regional Role / Industry-economic makeup analysis | Thematic + Explanation | A1 AI inversion + other industry-facing questions/themes | Explains how the market's industries, economic base, and sector structure are organized | Market-specific findings from reusable methods and datasets | In progress | A1 is the first Act 2 theme instance, not a one-off special case |
| Act 2 / Industry Makeup and Regional Role / Regional role analysis | Explanation | Regional role + Q6 One metro? + other region-facing questions | Explains how the market fits its broader region through commuting, infrastructure, trade/base metrics, and comparative role | Reusable capability; market-specific findings | In progress | Broader than industry; likely needs standard region-analysis components such as shared geo rollups |
| Act 2 / Built Environment and Social Fabric / Built environment analysis | Explanation | Q4 Daily-needs access + Q6 One metro? + future built-form questions | Explains infrastructure, building types, land use, and physical market form | Reusable capability; market-specific findings | Planned | Built environment can contain separate sub-components with their own inputs and outputs |
| Act 2 / Built Environment and Social Fabric / Access-amenities analysis | Explanation | Q4 Daily-needs access + related livability questions | Explains what livability amenities exist and how accessible they are | Reusable capability; market-specific findings | In progress | Separate from built environment even when they share inputs and maps |
| Act 2 / Built Environment and Social Fabric / Social fabric analysis | Explanation | Q6 One metro? + character-facing questions + future cultural analyses | Explains cultural anchors, civic institutions, neighborhood character, and social capital signals | Reusable capability; market-specific findings | Planned | Start with those four subcomponents but leave room for additional signals later |
| Act 2 / Built Environment and Social Fabric / Theme analysis slot | Thematic | Routed thematic analyses that land in Act 2 | Allows themes to sit beside explanation questions and reuse the same component capabilities | Market-specific selection from reusable build methods | Planned | The standardized part is how we build and answer the theme, not which theme is chosen for a market |
| Act 2 / Built Environment and Social Fabric / Explanation question slot | Explanation | Q1 Q2 Q4 Q5 Q6 and related market questions | Allows standardized question builds to sit beside themes and feed later acts | Market-specific selection from reusable build methods | In progress | Questions chosen can vary by market, but the datasets, methods, and outputs should standardize |
| Act 3 / Trend Analysis / Trend series candidate pool | Position + Thematic | Trajectory + routed theme context | Base pool of time-series measures that can support the market's dynamics read | Fixed candidate pool structure; actual selected series vary by market | In progress | Start with `population`, `permits`, `home prices`, `rents`, `employment`, `wages`, `income`; organize by data family |
| Act 3 / Trend Analysis / Lead trend panel set | Position + Thematic | Trajectory + routed theme context | Reader-facing 4 to 6 panel set that turns the broader trend pool into the market's main dynamics story | Market-specific selection from the candidate pool | Planned | Select by strongest explanatory value for the market rather than one-per-family rules |
| Act 3 / Trend Analysis / Converging-diverging-inflecting classifications | Position | Trajectory | Useful framing layer for interpreting series consistently across markets | Market-specific output from a reusable method | Planned | Helpful but not the primary Act 3 asset; avoid reducing the whole act to this classification alone |
| Act 3 / Trend Analysis / Inflection flags | Position | Trajectory | Programmatic signal for where recent slope changes are strong enough to matter | Reusable method; market-specific outputs | In progress | Treat as engine output rather than pure issue packaging |
| Act 3 / Trend Analysis / Regional context comparison | Position + Thematic | Trajectory + routed theme context | Every dynamic read should show whether the market follows or bucks its broader region and peer context | Required context class; exact comparison values vary by market | In progress | Lives underneath each trend or dynamic read rather than as a standalone section; default to Census Division plus nearby and similar metros |
| Act 3 / Trend Analysis / Theme-specific dynamic read | Thematic | Routed theme read over time | Shows how the routed Act 2 theme is changing over time rather than only how it looks today | Conditional on routed theme strength | Planned | Example shape: current industry structure in Act 2, then strengthening/weakening/shifting in Act 3 |
| Act 3 / Trend Analysis / Diverging peer or forward-analog interpretation | Position + Thematic | Peers + Trajectory + routed theme context | Higher-order comparative dynamics layer explaining where the market may be heading or why similar metros are splitting apart | Conditional; present only when signal is strong enough | Planned | Main reusable component is the comparison method; reuse Act 1 peer sets |
| Act 3 / Data Take Sidebar / Data Take candidate pool | Position + Thematic + Explanation | Analysis/question-derived findings | Pool of possible short findings that emerge from actual analyses rather than generic outlier scanning | Market-specific | In progress | Data Takes should come from what proves interesting in the analyses and question bank work |
| Act 3 / Data Take Sidebar / Data Take selected asset | Position + Thematic + Explanation | Selected analysis/question-derived finding | Final boxed finding when a market yields a genuinely interesting short take | Conditional | Planned | Do not manufacture these; only include when there is a real reason |
| Act 4 / Zone Archetypes / Zone archetype map | Position | Internal structure | Core tract-level structure asset that lets us see one layer of how the metro organizes internally | Required tract view with complementary Place and ZCTA context | In progress | Align to the Intelligence Framework at a lower geography level rather than inventing a disconnected typology |
| Act 4 / Zone Archetypes / Zone composition benchmark bar | Position | Internal structure | Converts the zone mix into a comparative finding rather than a legend | Fixed comparison asset; benchmark values vary by market | Planned | Target a national sample if technically feasible; otherwise use a practical comparison baseline |
| Act 4 / Zone Archetypes / Zone interpretation summary | Position + Explanation | Internal structure + routed explanatory context | Interprets what the market's internal structure means through Character, Livability, and Opportunity lenses | Market-specific interpretation on top of a reusable zone model | Planned | Not just opportunity concentration; this is where the three-frame geography becomes legible |
| Act 4 / Market Anatomy / Place and zone structure | Position | Internal structure | Shows how counties, Census Places, tracts, ZCTAs, and Phase 7 zone types fit together | Broad exploratory surface; issue selects only the useful parts | Planned | Preserve unincorporated coverage and both directions of the Place × Zone relationship |
| Act 4 / Market Anatomy / Activity and infrastructure structure | Position + Explanation | Internal structure plus existing job-center evidence | Shows how POIs, anchors, employment centers, and physical networks relate to Places and zones | Broad exploratory surface; not an access or integration claim | Planned | Compare POI counts, valid normalized measures, and composition rather than relying on raw density alone |
| Act 4 / Zone Structures / Structural candidate pool | Position | Internal structure using Corridor Intelligence | Creates the broader set of reproducible corridor and district candidates before editorial narrowing | Market-specific pool from a reusable engine method | Planned | Build same-zone cores with governed Infrastructure and aggregate POI evidence; keep bridge tracts explicit |
| Act 4 / Zone Structures / Corridor Intelligence method | Position | Internal structure using the Corridor Intelligence Engine | Defines how tract-derived intelligence becomes reproducible membership and corridor/district form | Reusable engine; market-specific outputs | Planned | Spec and build plan are agreed; Jacksonville calibration and Richmond validation remain. Keep distinct from national zone classification and editorial naming. |
| Act 4 / Zone Structures / Candidate stat blocks | Issue | Selected Internal Structure candidates | Standard comparable summary object for selected corridors or districts | Fixed issue asset built from market-specific structural outputs | Planned | Lock-once packaging remains downstream of exploratory candidate identification |
| Act 4 / Zone Structures / Candidate narrative thesis | Explanation + Issue | Selected corridor or district + Q2 Job-proximity gradient + Q4 Daily-needs access where routed | Explains why a selected candidate matters using the strongest relevant structure, access, role, and trend signals | Market-specific | Planned | Downstream evidence can deepen a candidate without rewriting its engine-owned membership |
| Act 4 / Parcel Watch / Parcel candidate pool | Explanation | Parcel watch | Creates the optional set of parcels worth deeper review inside a selected corridor or district | Conditional and market-specific | Planned | Downstream extension of structural-candidate logic rather than a co-equal required component |
| Act 4 / Parcel Watch / Parcel screening logic | Explanation | Parcel watch | Reusable logic for identifying underutilized parcels once candidate scope exists | Reusable method; conditional outputs | Planned | Can align to ROF/shared parcel logic as an input but still allow MDD-specific customization |
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
| Act 4 / Zone Structures / candidate identification | Partial | Reproducible candidates use Phase 7 cores, Geography, governed Infrastructure roles, aggregate POI composition, and conservative bridges; later selection and interpretation can reuse access, trajectory, and job-center context |  |
| Act 4 / Zone Structures / candidate narrative | Yes | Narrative will likely reuse Act 2 findings on industry, social fabric, access, and regional role |  |
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
| Profile | Intelligence Framework outputs, `mart_intelligence`, notebook-first Act 1 profile data frame, Research Tool Overview tab, frame review artifacts/notebooks | Fingerprint-style profile tables, scorecards, frame/topic summaries, cluster-label assets, radar charts, and future identity visuals such as KPI strips, frame-balance scatters, or compact peer-position plots | Public sharing should stay mindful of framework validation and universe-consistency questions | Start with a thinner notebook data frame while the KPI shape stabilizes; likely promote later into broader MDD marts rather than a one-off Act 1 mart; this is one of the strongest bridges from Research Tool surfaces into Marimo notebook analyses |
| Peers | Cross-frame cosine similarity outputs plus frame-specific similarity outputs; Intelligence Framework peer artifacts; Research Tool Peers tab | Peer tables, featured peer comparisons, similarity views/tables, head-to-head KPI comparisons, supporting Act 1 and Act 3 comparative assets, and future peer-network visuals | Peer outputs should carry the same framework-method caveats as other public Position assets | Make it explicit that both cross-frame and frame-specific peer sources are used; peer tables and similarity views may consolidate later if they stay structurally similar |
| Trajectory | Existing trajectory outputs and candidate-list artifacts where available; Research Tool Trajectory tab; future trajectory data frame or mart rather than assuming one fixed parquet dependency | Trend leads, direction/distribution summaries, turn signals, Act 3 inputs, notebook-first comparison views, and future slope/distribution visuals if they prove easy and useful | Direction-style outputs may need caution if presented too simply before method review is complete | If `trajectory_scores.parquet` already exists, review and reuse it, but the scalable target is a queryable mart/data frame; avoid overcommitting to dynamic charting early |
| Internal structure | Phase 7 tract/ZCTA outputs, Geography Place relationships, POI and Infrastructure runs, existing D3 job centers, and Corridor Intelligence | Part 1: market geography, Place inventory, tract/ZCTA zone views, and Place × Zone structure. Part 2: POI/activity patterns, anchors, employment centers, Infrastructure, a corridor/district section, and market synthesis. | Internal analysis; selected assets move downstream only after engine and issue review | Keep one Marimo notebook with two explicit parts. Corridors remain one structural lens and do not block the broader Place/zone review. |
| Candidate scan | Research Tool Candidate List plus current Profile and Time-Series contracts | Filterable all-market ranking, visible contributing signals, selected-market explanation, and shortlist comparison | Internal market-selection support | Port and update the existing workflow as one Marimo-only notebook; keep the ranking transparent and analysis-local. |

`Similarity neighborhood` is retired. Its CBSA-level similarity questions
overlap with Peers and the similarity-method study, while its tract/ZCTA and
within-market language belongs to the Intelligence Framework, Corridor
Intelligence, and Internal Structure.

### 3.2 Explanation

| Analysis / Question | Current build/source | Main outputs it can feed | Routed by what signal? | Notes / audit needs |
|---|---|---|---|---|
| Q1 Supply or demand | Thin existing foundation so far; start from relevant Gold tables or MDD marts plus any housing notebooks, apps, and notes; supply side should include housing stock composition, vacancy, permits, HPI; demand side should include population growth, HPI, costs, and migration | Submarket comparison tables, supply-vs-demand diagnostic views, housing pressure maps, housing stock maps, permitting maps, population-growth maps, possible commuting-pattern context, and explanation notes that can feed Act 2 or Act 3 | Livability divergence and other housing-related market signals | One of the more reusable explanation questions; can likely standardize before some of the heavier POI/network-dependent questions |
| Q2 Job-proximity gradient | Industry D3 job centers, tract price data, existing job-center mapping work, and future Infrastructure Engine layers so the method is not based only on geographic proximity | Gradient charts, tract-distance comparisons, corridor-supporting inputs, internal opportunity comparisons | Opportunity and internal-structure signals; likely helpful when corridor questions emerge | One of the more reusable explanation questions; likely needs network-analysis follow-on to reach its better form |
| Q3 Where growth lands | Tract housing-unit change, tract population change, tract vintage handling, geography helpers, plus any relevant tract-change notebooks or notes | Infill-vs-greenfield views, growth maps, tract change summaries, Act 3 or Act 4 supporting inputs | Livability and internal-structure signals tied to growth placement | One of the more reusable explanation questions; vintage handling remains the known hazard |
| Q4 Daily-needs access | POI Engine outputs, Infrastructure Engine context where needed, Place Intelligence methods, Richmond/Jacksonville ingest work, plus any related notes/specs/apps | Amenity access maps, tract access scores, livability summaries, corridor-supporting access overlays | Livability divergence and related place-access signals | More setup-heavy than some other explanation questions because it depends on POI data, taxonomy quality, and a separately defined access method; network analysis remains a later choice |
| Q5 Afford to live near jobs | LODES RAC/WAC, tract income, OEWS, workplace/residence comparisons, plus any supporting labor or affordability notes | Affordability-to-jobs comparisons, mismatch summaries, tract or corridor overlays, Act 4 supporting inputs | Opportunity divergence and labor/housing tension signals | Reusable eventually, but depends on more setup than the simpler regional/housing structure questions |
| Q6 One metro? | LODES WAC/RAC integration, county industry mix, polycentricity ideas, market-structure context, character context, and any relevant regional notes | Commuting integration views, polycentricity comparisons, sub-center maps, market-structure summaries that can feed Act 2 and Act 4 | Character divergence and broader market-structure or regional-fit signals | One of the most reusable bridge questions; spans regional role, character explanation, polycentricity, and internal market structure |
| Regional role | WAC/RAC, deferred OD, IRS flows, infrastructure context, geo rollups, regional comparison logic, and any related notebooks/specs/notes | Commute-shed summaries, inflow/outflow views, regional benchmark tables, metro-within-region interpretation assets | Broad regional-fit and comparison signals across multiple frames | One of the most reusable explanation capabilities; likely points toward shared region-analysis components and cleaner geo rollups |
| Corridor opportunity read | Internal Structure structural candidates plus Q2, Q4, Trajectory, POI, or Infrastructure evidence when the selected market calls for it | Selected-candidate comparisons, candidate-level theses, and Act 4 stat-block inputs | A strong structural candidate that needs deeper explanation before issue selection | Conditional downstream interpretation; candidate identification itself belongs to Corridor Intelligence and Position / Internal Structure |
| Parcel watch | Regrid or county parcels, selected-candidate scope, parcel screening logic, ROF/shared parcel methods where relevant, and any market-specific parcel prep work | Parcel candidate tables, parcel maps, underutilized-site screens, selected-area follow-through assets | Conditional on structural-candidate selection and parcel-data readiness | Reusable eventually, but strongly conditional and setup-heavy; should not be treated as required for every market |
| Catchment | Place Intelligence D1-D3, apportionment methods, barriers, daytime population, site-level artifact builds, and related methods/architecture notes | Site catchment maps, tract-apportionment summaries, access/barrier diagnostics, place-level supporting views | Place/site-centered questions rather than classic metro routing alone | Built already in a place-intelligence context; methods look promotable even if the app/product surface itself is not the direct target here |

### 3.3 Thematic

Every thematic builder runs in `market: all` mode first. The national pass is
where the claim, comparison distribution, method, and QA visuals are tested.
Only after that gate passes does the same builder run in `market: <cbsa>` mode
and hand selected findings to an issue.

| Theme / Entry | Current build/source | Main outputs it can feed | Runs in market mode, all-market mode, or both? | Notes / audit needs |
|---|---|---|---|---|
| A1 AI inversion | Existing A1 Marimo notebook, industry engine work, NAICS-to-AIOE crosswalk, `SPEC_INDUSTRY.md`, and underlying industry input datasets already in progress | All-market analysis notebooks first, later market-mode sections, exposure scorecards, sector comparisons, change-over-time views, possible within-market AI impact reads, comparative charts, and reusable visual packages | Both | Closest thematic analysis to done; useful as the first instance of the standard Act 2 theme build method |
| A2 Building lowers prices? | Housing engine ideas, permits, price/burden data, housing satellite overlaps, and any housing input datasets already available | All-market notebooks, later market-mode sections, comparative charts, housing burden vs supply views, scorecards, maps, and reusable housing analysis packages | Both | Likely has much of the data already; should connect closely to Q1 and broader housing-pressure logic |
| A3 Moving toward harm? | EPA data, FEMA data, building growth, population growth, environment/livability inputs, and related hazard/growth precursor work | All-market notebooks, later market-mode sections, hazard-growth comparisons, risk scorecards, maps, and reusable environment-growth analysis packages | Both | Data foundation appears mostly present; should explicitly connect hazard data to growth and built environment dynamics |
| A4 Remote work rewired? | Work-geography concepts, LODES, ACS commute and WFH series, housing context, industry context, and related work-geography precursor datasets | All-market notebooks, later market-mode sections, commute/WFH comparison views, housing-industry context charts, regional/work-geography analyses, and reusable comparative visuals | Both | Analytic approach still needs definition; work geography here means understanding how jobs, commuting burden, remote-work eligibility, and housing patterns reshape market structure |
| A5 How many downtowns? | WAC, polycentricity ideas, Q6 overlap, internal-structure work, job-density ideas, shopping/transit density ideas, and 15-minute-city literature/method references | All-market notebooks, later market-mode sections, polycentricity comparisons, sub-center maps, downtown typology views, density/time-series comparisons, and reusable place-structure visuals | Both | Needs analytic approach definition more than raw data discovery; should distinguish major downtowns, smaller suburban downtowns, and walkable strip/station-area centers |
| A6 Specialization predicts growth? | LQ panels, growth series, industry engine work, benchmarking methods, and related industry-growth precursor datasets | All-market notebooks, later market-mode sections, specialization vs growth comparisons, benchmarking tables, scorecards, and reusable industry-growth visuals | Both | Data likely mostly available; method design is more important than data discovery at this stage |
| A7 Who is squeezed? | Housing burden, price levels, income and wage context, overlaps with Q1 and Q5, and related affordability precursor datasets | All-market notebooks, later market-mode sections, burden vs income comparisons, affordability scorecards, maps, and reusable housing-pressure visuals | Both | Likely has most of the needed data; analytic framing still needs design |
| A8 Geography of life expectancy | `health_wide`, housing context, social-fabric context, health/livability inputs, POIs, food-desert data, and related health precursor work | All-market notebooks, later market-mode sections, health-geography comparisons, scorecards, maps, and reusable health-context visuals | Both | Data appears broadly present; could benefit from stronger POI/food-access integration |
| A9 Converging or diverging? | Long-panel dispersion work, trend-series families, Act 3 methods, peer comparisons, and related convergence precursor datasets | All-market notebooks, later market-mode sections, long-run divergence charts, peer comparisons, trend scorecards, and reusable dynamics visuals | Both | Data likely mostly present; analytic approach still needs definition |
| A10 Polarization | Sector wage distributions, industry and people context, growth/structure comparisons, and any additional needed labor or earnings datasets | All-market notebooks, later market-mode sections, wage-distribution views, sector-demographic comparisons, scorecards, and reusable labor-structure visuals | Both | Needs more data than many of the other themes; interesting lens may combine sector, industry, demographics, and political/economic sorting questions later |
| Housing satellite | Vacancy, costs, supply character, overheating heuristic, overlaps with A2, A7, and Q1, plus underlying housing input datasets | All-market notebooks, later market-mode sections, housing scorecards, comparison tables, maps, and reusable housing diagnostics | Both | Revisit the housing overheating heuristic and decide whether it should be reused as-is or reviewed/rebuilt |
| CBSA similarity study | Cross-frame cosine method, methods memo, framework review questions, peer outputs, similarity artifacts, and broader Intelligence Framework data assets | All-market methods/analysis notebook first, later comparative article or supporting market-mode interpretation, similarity scorecards/tables, comparison visuals, and reusable methods outputs | Both | Cross-analysis extension of the Intelligence Framework; much of the data should already exist even if the framing still needs tightening |

## 4. Analysis -> Reusable Component Audit

Only after we know which analyses feed which outputs do we ask what reusable
components are required underneath.

This section should stay disciplined about distinguishing between:

- `engine`
- `shared method`
- `shared dataset / mart`
- `supporting infrastructure`

Working boundary:

- `engine` = the reusable computational system that produces a class of derived outputs
- `shared method` = the reusable analytical logic or comparison approach applied across questions/themes
- `shared dataset / mart` = the reusable queryable output layer that stores prepared inputs or derived results for downstream notebook work
- `supporting infrastructure` = enabling inputs or platform pieces that make methods and marts possible but are not themselves the main analytical product

The purpose here is to audit overlap from Sections `2` and `3`, make the
dependencies clearer, and only then decide what should become a promoted engine
or foundation-owned asset.

| Analysis / Question / Theme | Required reusable component | Component type | Why required | Current state | Existing source/build | Used by other analyses? | Promote to foundations later? | Notes |
|---|---|---|---|---|---|---|---|---|
| Profile | Intelligence Framework outputs | engine | Supplies the scored frame outputs, cluster labels, peer context, and other identity-layer signals used in Act 1 | Exists | Phase 2-7 Intelligence Framework outputs, `mart_intelligence`, Research Tool consumers | Yes | Yes | Core dependency for most Position work |
| Profile | Act 1 profile data frame or broader MDD profile mart | shared dataset / mart | Provides a notebook-first reusable base for fingerprint KPIs, scorecards, and related identity assets | Partial | Notebook-first profile work to be built from `mart_intelligence` | Yes | Yes | Start thin, then promote into broader MDD marts once shape stabilizes |
| Peers | Similarity outputs and peer tables | engine | Supplies cross-frame and frame-specific peer relationships | Exists | Cosine-similarity outputs, peer artifacts, Research Tool Peers tab | Yes | Yes | Should keep both cross-frame and frame-specific peer paths explicit |
| Trajectory | Time-series / trajectory engine and mart | engine | Computes reusable trend, momentum, salience, and turn signals and materializes them in a queryable DuckDB mart | Partial | Existing trajectory outputs, candidate-list artifacts, Research Tool Trajectory tab | Yes | Yes | The engine owns the method and mart; Position / Trajectory remains a thin parameterized consumer |
| Internal structure | Zone model outputs | engine | Supplies nationally consistent tract-derived intelligence for the Place/zone and small-area review | Exists; consumer contract review pending | Phase 7 zone outputs, tract assignments, ZCTA rollup, Zone Map tab | Yes | Yes | The notebook does not rerun the national model or treat zones as local Place names |
| Internal structure | Shared geo mart and rollups | shared dataset / mart | Supports CBSA, county, Census Place, tract, and ZCTA identities, allocations, and declared relationships | Exists; consumer adoption pending | `silver.dim_geo`, `mart_geography`, and geography-engine contracts | Yes | Yes | Place allocation basis, unincorporated coverage, and on-demand display geometry must remain explicit |
| Internal structure | POI Engine | engine | Supplies governed place records for Place/zone activity comparisons, major-anchor context, and optional Corridor membership evidence | Ready for first analysis | POI contract and declared market source runs | Yes | Yes | Internal Structure compares counts, valid normalized measures, and composition; it does not define daily-needs access or rewrite taxonomy |
| Internal structure | Existing job-center evidence | shared dataset / method | Adds an employment-center lens to the broad market anatomy | Exists in Industry D3; consumer interface review needed | Industry D3 tract job-center work | Yes | Maybe | Reuse as descriptive orientation; commuting integration and job-proximity claims remain downstream |
| Internal structure | Infrastructure Engine | engine | Supplies governed physical features for the market's infrastructure skeleton and Corridor membership evidence | Ready for analysis integration; promotion gated | Infrastructure contract and read-only consumer handoff | Yes | Maybe | The source engine does not infer routing, access, universal barriers, or candidate membership |
| Internal structure | Corridor Intelligence Engine | engine | Produces reproducible within-market corridors and districts for one dedicated section | Epic 1 interfaces locked; analytical tract geometry gated | Optional Phase 7 Stage 2 challenger plus `engines/corridor_intelligence/` | Yes | Maybe | The engine owns candidate membership, form, evidence, and QA; its absence does not block the broader market-anatomy review |
| Candidate scan | Candidate ranking method | shared method | Produces a lightweight market-selection artifact from current Position signals | Legacy baseline exists; update planned | Research Tool Candidate List, Phase 6 logic, current Profile and Time-Series outputs | Somewhat | Maybe | Keep notebook-only and analysis-local until another consumer needs the same method unchanged |
| Q1 Supply or demand | Housing structure and demand comparison method | shared method | Standardizes how supply-side and demand-side housing signals are compared within a market | Partial | Gold housing data, housing notebooks/notes, housing satellite overlaps | Yes | Yes | One of the strongest reusable explanation questions |
| Q1 Supply or demand | Housing component datasets | shared dataset / mart | Provides reusable supply-side and demand-side housing inputs for the method | Partial | Housing stock, vacancy, permits, HPI, population growth, costs, migration inputs | Yes | Yes | Good candidate for broader MDD housing marts |
| Q2 Job-proximity gradient | Job-center proximity method | shared method | Computes the relationship between jobs and prices within the market | Partial | Industry D3 job centers, tract price data, mapping work | Yes | Maybe | Better version likely needs road or network layers |
| Q2 Job-proximity gradient | Infrastructure Engine | engine | Supplies validated candidate road, rail, and river/canal geometry for a named physical-context experiment beyond pure geographic proximity | Ready for analysis integration; promotion gated | `engines/infrastructure/` Epics 1–5: reproducible runs, narrow mappings, geometry QA, and consumer handoff | Yes | Maybe | Start Q2 with straight-line proximity; the contract intentionally stops before routing or travel-time modeling. |
| Q3 Where growth lands | Tract growth-change method | shared method | Standardizes how in-market growth location is classified and compared | Partial | Tract housing-unit change, tract population change, geography helpers | Yes | Maybe | Vintage handling is the key known hazard |
| Q4 Daily-needs access | Daily-needs access method | shared method | Defines the amenity basket and standardizes how access is measured and summarized | Partial | POI counts, Place Intelligence methods, and future Q4 notebook work | Yes | Yes | Analytical use case built from engine outputs; straight-line, network, and scoring choices remain outside the POI contract |
| Q4 Daily-needs access | POI Engine | engine | Supplies classified, provenance-rich place points with a governed category/sub-category, tract/county assignment, and source-address postal-ZIP evidence | Ready for first analysis | `engines/poi/` Epics 1–5: Overture acquisition, normalization, governed taxonomy, QA, and Richmond/Jacksonville assignments | Yes | Yes | Point preparation is reusable; Q4 decides the daily-needs basket and access method. Basket categories resolve by name against the governed taxonomy (see `engines/poi/taxonomy/TAXONOMY.md`). Postal ZIP is not a Census ZCTA assignment; governed ZCTA geometry remains a Geography dependency. |
| Q4 Daily-needs access | Infrastructure Engine | engine | Supplies validated candidate roads, rail, and river/canal context only when the access method needs it | Ready for analysis integration; promotion gated | `engines/infrastructure/` Epic 5 consumer handoff | Yes | Maybe | Q4 owns its basket, reach, and any barrier behavior; no physical context is presumed. |
| Q5 Afford to live near jobs | Jobs-housing affordability method | shared method | Compares where people live, what they earn, and what it costs near job concentrations | Partial | LODES RAC/WAC, tract income, OEWS | Yes | Maybe | Reusable eventually, but needs more setup than the simpler housing or regional methods |
| Q6 One metro? | Polycentricity and integration method | shared method | Standardizes how to test whether a metro functions as one system or several linked centers | Partial | LODES WAC/RAC, county mix, polycentricity ideas, market-structure context | Yes | Yes | One of the strongest bridge questions across acts |
| Regional role | Regional comparison and role method | shared method | Standardizes how a market is compared to its region and how its role is interpreted | Partial | WAC/RAC, OD plans, IRS flows, geo rollups, regional comparison logic | Yes | Yes | Broader than industry; should align to the same shared comparison/benchmarking stack rather than diverging into a separate method family |
| Regional role | Regional rollup datasets | shared dataset / mart | Makes region, division, state, and nearby-metro comparisons reusable across questions | Partial | `dim_geo`, geo rollups, regional comparison inputs | Yes | Yes | Strong overlap with shared geo investment |
| Internal structure | Structural candidate datasets | shared dataset / mart | Stores reproducible membership, corridor/district form, edge evidence, and QA fields for notebook use | Not built | Future Corridor Intelligence DuckDB outputs | Yes | Maybe | Build after the method contract, not from notebook-authored IDs |
| Parcel watch | Parcel screening logic | shared method | Standardizes how underutilized parcels are identified once structural-candidate scope is defined | Partial | Parcel methods, selected-candidate scope, ROF/shared parcel logic | Yes | Maybe | Reusable, but conditional and market-specific in activation |
| Catchment | Catchment, apportionment, and barrier method | shared method | Standardizes point-centered tract weighting, reach variants, barrier interpretation, and daytime-population logic | Exists | Place Intelligence D1-D3, methods memo, architecture notes | Yes | Yes | Analytical method that consumes Geography, POI, and Infrastructure outputs; not part of those engines |
| A1 AI inversion | Theme engine interface | engine | Standardizes how thematic analyses run in all-market and market modes | Partial | A1 notebook, industry engine work, theme build pattern | Yes | Yes | A1 is the first real test case for this interface |
| A1 AI inversion | Industry theme datasets and crosswalks | shared dataset / mart | Provides reusable sector, employment, and exposure inputs for industry themes | Partial | NAICS-to-AIOE crosswalk, industry data products, SPEC work | Yes | Yes | Strong thematic candidate for promotion |
| A2-A10 thematic analyses | Standard thematic build method | shared method | Standardizes how themes are built, compared, and rendered across entries | Partial | Emerging from A1 plus analysis program structure | Yes | Yes | The reusable part is the build method, not the specific chosen theme |
| A2-A10 thematic analyses | Shared comparison and benchmarking method | shared method | Reuses one common comparison and benchmarking logic across full-market themes, market-mode themes, and cross-act analyses | Partial | Benchmarking ideas and comparison logic emerging across Sections 2 and 3 | Yes | Yes | Theme comparison, regional comparison, and peer benchmarking should be treated as variations of the same shared method family |
| Act 2 components broadly | Shared benchmark and comparison datasets | shared dataset / mart | Stores reusable comparison-ready reference data for national, Census Division, peer-set, and other recurring benchmark cuts | Partial | Emerging from geo rollups, peer logic, and benchmark inputs across Sections 2 and 3 | Yes | Yes | Distinct from the comparison method itself; likely a major reusable data-product layer |
| Market-wide notebook config | Registries and notebook config | supporting infrastructure | Centralizes market constants and lock-once notebook inputs | Not built | Proposed `market.yaml` and related registry ideas | Yes | Maybe | Useful enabling layer, but probably not a foundation asset by itself |

## 5. Existing Builds and Notes Audit

This is where we trace current material back into the program.

| Existing artifact | Best mapped to | Layer in program | Useful as-is, reference only, or needs translation? | What to audit for | Notes |
|---|---|---|---|---|---|
| `exploration/intelligence_framework/docs/intelligence_framework_overview.md` | Intelligence Framework system reference | Engine / Analysis | Useful as-is | Canonical outputs, build sequence, frame structure, trajectory/zones extensions, known limitations | Strongest current reference for what the framework actually is; essential for aligning Position work and for honest caveat language |
| `RESEARCH_TOOL_ROADMAP.md` | Position source material | Analysis | Reference only, with selective translation | Which tab logic should become notebook analyses versus remain legacy UI framing | Very useful as a map of existing Position surfaces; not the long-term structure itself |
| `Overview tab` | Profile / fingerprint source material | Analysis | Needs translation | Current query logic, scorecard structure, cluster-label display, what can become notebook-first identity assets | One of the clearest bridges from legacy app outputs into Act 1 notebook work |
| `Peers tab` | Peers source material | Analysis | Needs translation | Cross-frame vs frame-specific peer behavior, current comparison layout, what should become reusable peer tables/views | Strong source for Act 1 and Act 3 comparative outputs, but should move out of app-specific framing |
| `Trajectory tab` | Trajectory source material | Analysis | Needs translation | What trajectory signals already exist, how they are surfaced today, and what should become a queryable trajectory mart | Useful starting point, but current outputs likely need stronger treatment of magnitude/distribution |
| `Zone Map tab` | Internal structure source material | Analysis | Needs translation | Zone labels, rollups, map behavior, tract-first assumptions, and what can feed Act 4 zone assets | Good source for tract-first zone work; current app issues do not invalidate the underlying analytical value |
| `Candidate List tab` | Candidate scan source material | Analysis | Useful as-is for planning, needs translation for productization | Candidate-score logic, ranking usefulness, and what should remain a simple market-selection artifact | Better treated as planning/selection support than as a major user-facing analysis surface |
| `analysis_program.md` | Thematic inventory | Analysis | Useful as-is | Theme list, claim framing, status vocabulary, and which entries are close to readiness | Strong inventory of thematic intent; pairs well with Section 3.3 but does not yet encode shared build methods |
| `deep_dive_question_bank.md` | Explanation inventory | Analysis | Useful as-is | Question boundaries, act pairings, and whether question definitions still match current act thinking | Strongest current reference for explanation-question scope; should continue to inform cross-act reuse rather than rigid act placement |
| `SPEC_INDUSTRY.md` | A1 / industry implementation source | Analysis / Engine | Useful as-is, with selective translation | Which deliverables already imply reusable datasets, methods, benchmarks, and visuals | Best-developed thematic implementation artifact; likely the first real template for a reusable theme build path |
| `POI_INFRA_PROPOSAL.md` | POI and Infrastructure engine source | Engine | Useful as-is | Source-role decisions, storage recommendations, and what should become reusable engine infrastructure versus market-specific cache work | Strong guidance for splitting Overture place points from OSM physical geometry; helps shape both engine plans |
| `SPEC_PLACE_INTELLIGENCE.md` | Catchment / place-use source | Analysis / Engine | Useful as-is, with selective translation | Which place-intelligence outputs are directly reusable for MDD versus which remain site-product specific | Valuable for understanding catchment and place-context outputs; some pieces promote well even if the app itself is not the target |
| `METHODS_MEMO.md` | Catchment / barrier / node methods | Analysis / Shared method | Useful as-is | Shipped methods versus deferred methods, barrier logic, POI classification, and what is ready to reuse | One of the strongest method audit docs in the repo; especially useful for separating engine inputs from analytical interpretation |
| `TECHNICAL_ARCHITECTURE.md` | Place Intelligence pipeline source | Supporting infrastructure / Engine | Useful as-is for architecture, needs translation for MDD reuse | Which analytical bases, app-facing surfaces, and cached artifacts are reusable beyond the original app | Strong architectural audit; especially useful for distinguishing analytical base products from app/render layers |
| `metro_deep_dive_build_approach.md` | Build order / lock-once / engine framing | Issue / Engine | Useful as-is | Build sequence, lock-once decisions, reuse-first logic, and what should be treated as engine work rather than section writing | Still one of the best guides for execution order and anti-overbuilding discipline |
| `metro_deep_dive_template_guidance.md` | Issue spine | Issue | Useful as-is | Fixed spine, act/section shape, and where issue packaging should stay separate from analysis logic | Strongest current reference for the issue/output layer; should remain stable even as analytical methods evolve |
| `intelligence_framework_review_question_bank.md` | Method audit and publishability constraints | Engine / Audit | Useful as-is | Which methodological issues block external confidence in peer sets, rankings, zones, and related outputs | Crucial caveat and audit artifact; should directly inform what Position claims are treated cautiously in public outputs |

## 6. Reusable Component Build Map

Use this section as a fresh reusable-component-first view of the program.

The goal is not to repeat Sections `4` and `5`. The goal is to say:

- what reusable component we think needs to exist
- what it should broadly enable
- how ready it is
- whether we have strong references already or need to build from scratch

This section should stay focused on build direction first. Existing notes, specs,
or apps are supporting evidence, not the main organizing principle.

| Reusable component | Component type | What it should enable | Build priority | Current readiness | Reference strength | Likely starting point | Likely destination | Notes |
|---|---|---|---|---|---|---|---|---|
| Intelligence Framework outputs | engine | Act 1 identity assets, peer logic, trajectory context, internal-structure base, candidate scan | High | Exists | Strong | Reuse and stabilize current framework outputs and marts | foundations | Core system already exists; main work is contract clarity and downstream reuse |
| Act 1 profile data frame and broader MDD profile marts | shared dataset / mart | Fingerprint KPI set, scorecards, radar/table inputs, deeper profile views | High | Partial | Strong | Start with notebook-first profile data frame from `mart_intelligence` | shared platform asset | Promote into broader MDD marts once KPI shape stabilizes |
| Shared comparison and benchmarking method | shared method | Regional comparisons, peer comparisons, theme comparisons, scorecards, benchmark tables across acts | High | Partial | Medium | Consolidate existing comparison logic into one reusable method family | shared platform asset | Strong overlap across Acts 1-4 and thematic work |
| Shared benchmark and comparison datasets | shared dataset / mart | Queryable benchmark-ready cuts for national, Census Division, peer sets, and related comparison contexts | High | Partial | Medium | Build on geo rollups, peer logic, and benchmark inputs already identified | shared platform asset | Natural partner to the shared comparison method |
| Shared geo mart and rollups | shared dataset / mart | CBSA, county, Census Place, tract, ZCTA, regional, and other geography identities, joins, allocations, labels, and declared relationship types across the program | High | Exists; consumer adoption pending | Strong | `silver.dim_geo` plus `mart_geography` | foundations | Internal Structure is the first explicit Place × Zone allocation consumer; display geometry remains on-demand |
| Time-series / trajectory engine and mart | engine | Act 3 trend work, turn signals, candidate scan support, dynamic reads | High | Partial | Medium | Audit Phase 6, then build the reusable method and materialize its four DuckDB trajectory tables | shared platform asset | Engine owns shared computation and mart materialization; analysis folders consume it without rebuilding |
| Zone model outputs | engine | Place/zone composition, tract and ZCTA views, Act 4 zone archetypes, and corridor substrate | High | Exists; consumer contract review pending | Strong | Review and expose the current Phase 7 tract/ZCTA contract for Internal Structure | foundations | National tract and ZCTA model outputs remain owned by the Intelligence Framework |
| Regional comparison and role method | shared method | Regional role analyses, Q6 support, market-within-region interpretation, later comparative notes | High | Partial | Medium | Standardize WAC/RAC, geo rollups, IRS/OD extensions, and regional comparison logic | shared platform asset | Should align to the broader comparison stack rather than fork |
| Housing structure and demand comparison method | shared method | Q1, A2, A7, housing diagnostics, pressure maps, housing comparisons over time | High | Partial | Medium | Start from Gold housing inputs and existing housing notes | shared platform asset | One of the clearest reusable explanation methods |
| Housing component datasets | shared dataset / mart | Reusable supply-side and demand-side housing inputs for multiple questions and themes | High | Partial | Medium | Organize stock, vacancy, permits, HPI, costs, migration, and population inputs into reusable datasets | shared platform asset | Supports both explanation questions and thematic analyses |
| Daily-needs access method | shared method | Q4, livability summaries, and corridor-supporting access evidence | High | Partial | Strong | Build in Q4 from POI Engine outputs and only the Infrastructure context the method needs | shared platform asset | Keep amenity selection, reach, and scoring decisions outside the POI contract |
| POI Engine | engine | Classified, provenance-rich, geographically assigned place points for Q4 plus Internal Structure activity, Place/zone, and anchor views | High | Ready for first analysis; taxonomy stable across two markets | Strong | Consume a declared run in Q4 and Internal Structure Part 2 | shared platform asset | Owns points and taxonomy, not access interpretation, functional-center claims, barriers, or editorial Places. Category and sub-category names are stable identifiers; renaming one is a breaking change for consumers selecting by name. |
| Theme engine interface | engine | Standard all-market and market-mode thematic builds | High | Partial | Strong | Use A1 as the first real template | shared platform asset | One of the most important scaling components for the thematic family |
| Industry theme datasets and crosswalks | shared dataset / mart | A1, A6, A10, industry comparisons, exposure analyses, growth-specialization work | High | Partial | Strong | Build from current industry spec and crosswalk work | shared platform asset | Probably the strongest current thematic data-product candidate |
| Standard thematic build method | shared method | Reusable workflow for A1-A10 and future themes | High | Partial | Medium | Generalize from A1 and the analysis program | shared platform asset | Standardize method and outputs, not theme choice |
| Q6 polycentricity and integration method | shared method | One Metro, market-structure interpretation, internal-center logic, support for downtown-related themes | Medium | Partial | Medium | Build from LODES integration and polycentricity ideas already identified | shared platform asset | Important bridge question across Acts 2 and 4 |
| Tract growth-change method | shared method | Q3, growth maps, infill-vs-greenfield views, Act 3 and Act 4 support | Medium | Partial | Medium | Start from tract housing/population change plus geography helpers | shared platform asset | Main risk is tract vintage handling |
| Job-center proximity method | shared method | Q2, corridor-supporting inputs, internal opportunity comparisons, and Internal Structure employment-center orientation | Medium | Partial | Medium | Start from D3 job centers and tract price data | shared platform asset | Internal Structure can reuse the center locations descriptively; price gradients and integration claims remain downstream |
| Infrastructure Engine | engine | Validated candidate roads, rail, and river/canal geometry for Internal Structure's physical skeleton and other named consumers | Medium | Ready for analysis integration; promotion gated | Strong | Use Internal Structure, Q4, or Q2 as contract tests; Geography must supply analytical CBSA geometry before authoritative serving or promotion | shared platform asset | Stops before routing, access, barrier interpretation, catchments, and corridors; do not widen to broad water or exploratory features without a named consumer. |
| Corridor Intelligence Engine | engine | Reproducible within-market corridors and districts for one Internal Structure section and later issue selection | Medium | Epic 1 in progress; analytical tract geometry gated | Medium | Use `engines/corridor_intelligence/`; retain optional Phase 7 Stage 2 as a challenger | shared platform asset | Same-zone cores may gain explicit bridge tracts; Infrastructure and aggregate POI composition are versioned membership evidence; editorial names remain downstream |
| Structural candidate datasets | shared dataset / mart | Reusable membership, spatial form, edge evidence, and QA fields | Medium | Not built | Weak | Materialize versioned results in DuckDB after the Corridor Intelligence method stabilizes | shared platform asset | Primary first consumer is Position / Internal Structure |
| Parcel screening logic | shared method | Parcel Watch and later parcel-level follow-through inside selected corridors or districts | Medium | Partial | Medium | Align to ROF/shared parcel logic, then customize for MDD | shared platform asset | Conditional component, not required for every market |
| Catchment, apportionment, and barrier method | shared method | Catchment maps, tract weighting, barrier-aware variants, and site-level supporting views | Medium | Exists | Strong | Reuse and evaluate the Place Intelligence method in the next site-centered analysis | shared platform asset | Analytical method consuming Geography, POI, and Infrastructure outputs; not part of those engines |
| Market-wide notebook config | supporting infrastructure | Shared market constants and lock-once notebook inputs across analyses | Low | Not built | Medium | Start simple with `market.yaml` or similar config layer | stay in MDD | Useful enabler, but not a core promoted analytical asset yet |

## 7. Decisions Captured So Far

| Decision area | Current decision | Notes |
|---|---|---|
| Build order vs. publication order | Keep them separate | Build order follows dependencies and routing; publication order follows the strongest completed reader story |
| Thematic execution order | Run `market: all` first, then `market: <cbsa>` | National mode develops and tests the shared analysis; market mode supplies issue candidates |
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
| Similarity Neighborhood | Retire it as a Position analysis | CBSA similarity stays in Peers and the methods study; tract/ZCTA types stay in the Intelligence Framework; within-market grouping moves through Corridor Intelligence into Internal Structure |
| Candidate Scan surface | Port and update the Research Tool Candidate List as one Marimo-only notebook | Ranking logic remains transparent and analysis-local rather than becoming a new engine or mart |
| Internal Structure shape | Build one market-anatomy notebook in two parts: market geography and Place/zone structure first; then POI/activity patterns, employment centers, Infrastructure, and structural patterns | Corridors and districts remain one section rather than the organizing frame; the broader notebook can proceed before that engine is implemented |
| Structural candidate ownership | Corridor Intelligence owns reproducible grouping and corridor/district form; Internal Structure explores it; Issues select and name featured candidates | Opportunity framing, names, and stat blocks remain downstream |
| Structural membership type | Give each candidate one primary Phase 7 type, require matching core tracts, and allow only conservative, explicit bridge tracts | Preserve the same-zone-only baseline and every bridge tract's original type and evidence |
| Corridor geography | Keep candidates inside one CBSA but allow them to cross county lines | County composition is metadata, not a grouping boundary or identifier |
| Corridor calibration | Apply one shared, versioned method market by market | Early-market tuning is allowed only through explicit parameter profiles; no manual tract edits |
| Act 2 organizing rule | Start from analysis questions, map into reusable component-group capabilities, then trace upstream inputs needed to answer them | Component groups are capability buckets, not strict ownership buckets |
| Act 2 standardization rule | The reusable part is how we build and answer questions and themes; the market-specific part is which ones we choose to pursue | Standardize datasets, methods, workflows, and outputs where possible |
| Shared comparison method | Treat comparison and benchmarking as a shared method reused across multiple Act 2 components and later acts | Support national, Census Division, Act 1 peer set, and sometimes nearby-metro comparisons |
| Regional role scope | Treat regional role as a broader cross-cutting capability, not just an industry sub-question | Includes commuting, infrastructure, trade/base metrics, and comparative regional fit |
| Profile build path | Start with a thinner notebook data frame built from `mart_intelligence`, then promote into broader MDD marts once the KPI shape stabilizes | Avoid creating a one-off Act 1 profile mart too early |
| Geography investment direction | Use the implemented shared geo mart with vintaged `dim_geo`, typed relationships, and encoded rollups | New tract, ZCTA, Place, and regional work should start from `mart_geography`; expand only for a named consumer |
| Spatial engine boundary | Do not create one catch-all Spatial engine | Geography owns boundaries; POI owns place points; Infrastructure owns physical line and polygon features |
| Catchment and barrier ownership | Keep them as analytical methods | They interpret Geography, POI, and Infrastructure inputs for a particular origin or use case |
| Corridor ownership | Treat Corridor Intelligence as a separate future Intelligence Framework extension | Build reproducible membership from Phase 7 cores, Geography, Infrastructure, and aggregate POI evidence; keep trajectory, opportunity selection, and editorial framing downstream |
| Explanation cross-act rule | Explanation questions can feed multiple acts, especially Act 2, Act 3, and Act 4 | Do not force them into a single-act mental model |
| Most reusable explanation questions | Regional Role, Supply or Demand, Job-proximity Gradient, One Metro, and Where Growth Lands look most reusable early | Others are still important, but likely require more POI, infrastructure, or network-analysis setup first |
| Reusable component boundary: engine | Treat an engine as the reusable computational system that produces a class of derived outputs | Example shape: Intelligence Framework outputs, zone model outputs, theme engine interface |
| Reusable component boundary: shared method | Treat a shared method as reusable analytical logic applied across multiple questions or themes | Example shape: comparison/benchmarking, regional role, job-proximity logic |
| Reusable component boundary: shared dataset or mart | Treat a shared dataset or mart as the queryable output layer that stores prepared inputs or derived results for downstream notebook work | Example shape: trajectory mart, geo mart, benchmark datasets |
| Reusable component boundary: supporting infrastructure | Treat supporting infrastructure as enabling inputs or platform pieces that make methods and marts possible but are not the main analytical product | Example shape: source extract caches, source registries, market config |
