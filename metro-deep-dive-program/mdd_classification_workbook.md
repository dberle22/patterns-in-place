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

#### Questions for 3.1 Position

Use these to fill the Position table while keeping the level light and useful.

1. For `Profile`, what are the core current sources we should name?
   Likely candidates: Intelligence Framework outputs, `mart_intelligence`, Research Tool Overview tab, frame review notebooks/artifacts.

2. For `Profile`, what rough outputs should we name?
   Examples: fingerprint-style profile tables, frame/topic summaries, cluster label assets, scorecards, identity visuals.

3. For `Peers`, should we explicitly list both cross-frame cosine similarity outputs and frame-specific similarity outputs as separate current sources?

4. For `Peers`, what outputs do we want to call out now?
   Examples: peer tables, featured peer comparisons, similarity views, head-to-head KPI comparisons.

5. For `Trajectory`, what do we see as the main current build/source?
   Likely candidates: Phase 6 trajectory outputs, `trajectory_scores.parquet`, candidate-list outputs, Research Tool Trajectory tab.

6. For `Trajectory`, what rough outputs should we list?
   Examples: trend leads, direction classifications, turn signals, dynamic comparison charts, Act 3 inputs.

7. For `Internal structure`, do we want to list the current sources as Phase 7 zone model outputs, tract assignments, ZCTA rollups, Research Tool Zone Map tab, plus place-intelligence overlap where relevant?

8. For `Internal structure`, what outputs should we name?
   Examples: zone maps, composition bars, zone summaries, Act 4 zone inputs.

9. For `Candidate scan`, do we want to treat it as a real Position analysis in this table, or more as a market-selection artifact built from Position outputs?

10. If we keep `Candidate scan`, what sources should we name?
    Likely candidates: `phase6_candidate_list.csv`, Research Tool Candidate List tab, cross-frame divergence flags, trajectory outputs.

11. For `Candidate scan`, what outputs should we list?
    Examples: market ranking tables, candidate shortlists, market-selection views.

12. For `Similarity neighborhood`, since it is not built yet, should the Current build/source field emphasize `not built` plus the existing similarity matrices and peer outputs it would build on?

13. For `Similarity neighborhood`, what do we imagine as the rough outputs?
    Examples: peer networks, threshold-based neighbor sets, pairwise similarity exploration, beyond-top-10 comparison surfaces.

14. Across all Position analyses, do we want to explicitly note that these are the strongest existing bridge from Research Tool surfaces into Marimo notebook analyses?

15. Are there any Position analyses that should already carry a public-sharing caution note because of framework validation or universe-consistency concerns?

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

#### Questions for 3.2 Explanation

Use these to fill the Explanation table while keeping the level light and useful.

1. For each explanation question, what current sources should we name:
   existing data assets, partial notebooks, specs, app surfaces, or methods notes?

2. For `Q1 Supply or demand`, what sources do we already know or expect to need?
   Likely candidates: housing stock composition, vacancy, permits, HPI, related housing engine work.

3. For `Q1 Supply or demand`, what rough outputs should we name?
   Examples: submarket comparison tables, supply-vs-demand diagnostic views, housing pressure maps, explanation notes that can feed Act 2 or Act 3.

4. For `Q2 Job-proximity gradient`, what current build/source should we name now?
   Likely candidates: Industry D3 job centers, tract price data, any existing job-center mapping work.

5. For `Q2 Job-proximity gradient`, what rough outputs should we list?
   Examples: gradient charts, tract-distance comparisons, corridor-supporting inputs, internal opportunity comparisons.

6. For `Q3 Where growth lands`, what sources do we already know or expect to need?
   Likely candidates: tract housing-unit change, tract population change, tract vintage handling, geography helpers.

7. For `Q3 Where growth lands`, what outputs should we name?
   Examples: infill-vs-greenfield views, growth maps, tract change summaries, Act 3 or Act 4 supporting inputs.

8. For `Q4 Daily-needs access`, what sources should we name now?
   Likely candidates: Overture POIs, OSM, POI taxonomy work, Place Intelligence methods, Richmond/Jacksonville ingest work.

9. For `Q4 Daily-needs access`, what outputs should we list?
   Examples: amenity access maps, tract access scores, livability summaries, corridor-supporting access overlays.

10. For `Q5 Afford to live near jobs`, what sources do we already know or expect to need?
    Likely candidates: LODES RAC/WAC, tract income, OEWS, workplace/residence comparisons.

11. For `Q5 Afford to live near jobs`, what outputs should we name?
    Examples: affordability-to-jobs comparisons, mismatch summaries, tract or corridor overlays, Act 4 supporting inputs.

12. For `Q6 One metro?`, what should the current sources emphasize?
    Likely candidates: LODES WAC/RAC integration, county industry mix, polycentricity ideas, market-structure and character context.

13. For `Q6 One metro?`, what rough outputs should we list?
    Examples: commuting integration views, polycentricity comparisons, sub-center maps, market-structure summaries that can feed Act 2 and Act 4.

14. For `Regional role`, what current sources should we name?
    Likely candidates: WAC/RAC, deferred OD, IRS flows, infrastructure context, geo rollups, regional comparison logic.

15. For `Regional role`, what outputs should we list?
    Examples: commute-shed summaries, inflow/outflow views, regional benchmark tables, metro-within-region interpretation assets.

16. For `Corridors`, what current sources should we name even though the method is unsettled?
    Likely candidates: Internal structure outputs, Q4 access work, OSM infrastructure, possible trend overlays.

17. For `Corridors`, what rough outputs should we list?
    Examples: corridor candidate pools, selected corridor summaries, corridor-level theses, Act 4 stat-block inputs.

18. For `Parcel watch`, what sources should we name now?
    Likely candidates: Regrid or county parcels, corridor scope, parcel screening logic, ROF/shared parcel methods where relevant.

19. For `Parcel watch`, what outputs should we list?
    Examples: parcel candidate tables, parcel maps, underutilized-site screens, corridor follow-through assets.

20. For `Catchment`, what current sources should we name?
    Likely candidates: Place Intelligence D1-D3, apportionment methods, barriers, daytime population, site-level artifact builds.

21. For `Catchment`, what outputs should we list?
    Examples: site catchment maps, tract-apportionment summaries, access/barrier diagnostics, place-level supporting views.

22. Across the Explanation family, do we want to explicitly note that many of these questions can feed multiple acts, especially Act 2, Act 3, and Act 4?

23. Which Explanation questions already look most reusable as standard methods, even if their exact market selection will vary?

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

#### Questions for 3.3 Thematic

Use these to fill the Thematic table while keeping the level light and useful.

1. For each thematic entry, what current sources should we name:
   existing notebooks, specs, marts, draft engines, or known input datasets?

2. For `A1 AI inversion`, what sources should we explicitly call out?
   Likely candidates: A1 Marimo notebook, Industry engine work, NAICS-to-AIOE crosswalk, `SPEC_INDUSTRY.md`, industry data products already in progress.

3. For `A1 AI inversion`, what rough outputs should we list?
   Examples: market-mode section outputs, all-market article outputs, exposure scorecards, sector comparisons, regional or peer comparisons.

4. For `A2 Building lowers prices?`, what current sources or precursor work should we name even if it is still banked?
   Likely candidates: housing engine ideas, permits, price/burden data, housing satellite overlaps.

5. For `A3 Moving toward harm?`, what sources or precursor work should we name?
   Likely candidates: hazard data, growth series, environment/livability inputs, Act 3 overlap.

6. For `A4 Remote work rewired?`, what sources or precursor work should we name?
   Likely candidates: work-geography concepts, LODES, WFH series, housing and industry context.

7. For `A5 How many downtowns?`, what sources or precursor work should we name?
   Likely candidates: WAC, polycentricity ideas, Q6 overlap, internal-structure work.

8. For `A6 Specialization predicts growth?`, what sources or precursor work should we name?
   Likely candidates: LQ panels, growth series, industry engine, benchmarking methods.

9. For `A7 Who is squeezed?`, what sources or precursor work should we name?
   Likely candidates: housing burden, price levels, income or wage context, overlap with Q1 and Q5.

10. For `A8 Geography of life expectancy`, what sources or precursor work should we name?
    Likely candidates: `health_wide`, housing/social-fabric context, health/livability inputs.

11. For `A9 Converging or diverging?`, what sources or precursor work should we name?
    Likely candidates: long-panel dispersion work, trend series families, Act 3 methods, peer comparisons.

12. For `A10 Polarization`, what sources or precursor work should we name?
    Likely candidates: sector wage distributions, industry and people context, growth/structure comparisons.

13. For `Housing satellite`, what should the current-source row emphasize?
    Likely candidates: vacancy, costs, supply character, overheating heuristic, overlaps with A2, A7, and Q1.

14. For `CBSA similarity study`, what should the current-source row emphasize?
    Likely candidates: cross-frame cosine method, methods memo, framework review questions, peer outputs, similarity artifacts.

15. Across the thematic entries, what rough output types do we want to name repeatedly?
    Examples: market-mode notebook sections, all-market articles, comparative charts, scorecards, maps, reusable visual packages.

16. For the `Runs in market mode, all-market mode, or both?` column, do we want to default most entries to `both` unless a theme is clearly one-sided?

17. Which thematic entries already look closest to real build readiness, and which are still mostly placeholders or concept stubs?

18. Across the Thematic family, do we want to explicitly note that the reusable part is the standard build method and theme-engine interface, while the specific selected theme remains market-dependent?

19. Which thematic entries look most likely to feed more than one act once built, rather than staying isolated inside Act 2?

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

## 7. Decisions Captured So Far

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
| Act 2 organizing rule | Start from analysis questions, map into reusable component-group capabilities, then trace upstream inputs needed to answer them | Component groups are capability buckets, not strict ownership buckets |
| Act 2 standardization rule | The reusable part is how we build and answer questions and themes; the market-specific part is which ones we choose to pursue | Standardize datasets, methods, workflows, and outputs where possible |
| Shared comparison method | Treat comparison and benchmarking as a shared method reused across multiple Act 2 components and later acts | Support national, Census Division, Act 1 peer set, and sometimes nearby-metro comparisons |
| Regional role scope | Treat regional role as a broader cross-cutting capability, not just an industry sub-question | Includes commuting, infrastructure, trade/base metrics, and comparative regional fit |
