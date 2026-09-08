# Metro Deep Dive — Build Sequence

Planning companion to `docs/build_map.html`. This file carries the analysis
notebook sequence; the HTML keeps the reusable component inventory available
for interactive browsing.

Source: `metro-deep-dive-program/mdd_classification_workbook.md` — §2
Issue→Analysis Map, §3 Analysis Inventory, §6 Reusable Component Build Map.

Sequencing rule: stabilize only the Engine or component needed by the next
analysis, build that analysis as a parameterized notebook, and inspect its
outputs. Keep analysis-specific logic in the analysis until another analysis
needs it unchanged; that is the promotion trigger.

Issues come after the analysis layer. They are not part of this build sequence
except as the reason an analysis is worth building.

## Where we are

The initial engine/component work gives us enough underneath the first
Position notebooks:

| Engine or component | Readiness for analyses | Next use |
|---|---|---|
| Intelligence Framework | Ready | Profile, Peers, Candidate Scan, Internal Structure |
| Profile surfaces and notebook | Implemented; interactive review pending | Position / Profile notebook |
| Peer surfaces and notebook | Implemented; interactive review pending | Position / Peers notebook |
| Benchmarking | Ready for the current national and peer comparisons | Profile, Peers, then routed Explanation and Thematic work |
| Time-Series / Trajectory | 50-metric direct recurring panel and notebook implemented; interactive review and contract freeze pending | Position / Trajectory notebook |
| Zone model and geography | Partial; do not widen yet | Position / Internal Structure, then Corridors |

The immediate move is therefore not another program-level design pass. It is
to turn the ready Position capabilities into notebooks with viewable outputs.
The Time-Series pilot is ready to be reviewed through the Trajectory surface,
where metric evidence can be inspected in context.

## Analysis notebook sequence

The order below is a dependency order within each family. After Position runs,
routing can pull a ready Explanation or Thematic analysis forward. Every
notebook should expose tables and simple visual outputs early enough to inspect
the analysis; issue styling waits.

### 3.1 Position

| Order | Analysis notebook | Reuses | Component work opened by this analysis | First outputs to inspect |
|---|---|---|---|---|
| P1 | Profile | Intelligence Framework, Profile surfaces, Benchmarking | None expected | Identity/label table, fingerprint candidate table, frame and topic views |
| P2 | Peers | Intelligence Framework peer outputs, Peer surfaces, Benchmarking | None expected | Cross-frame and frame peers, featured-peer candidates, head-to-head comparison |
| P3 | Trajectory | Intelligence Framework, Time-Series / Trajectory mart | Use the materialized pilot; keep consumer logic as query and interpretation only | Position and momentum paths, tiered signals, turn signals, KPI evidence |
| P4 | Internal structure | Intelligence Framework zone outputs | Open only the tract-first geography/zone slice needed by the notebook | Zone map, composition table, frame-level zone summary |
| P5 | Candidate scan | Profile, Peers, Trajectory | Keep ranking weights analysis-local on the first build | Ranked markets with visible contributing signals |
| P6 | Similarity neighborhood | Intelligence Framework similarity outputs, Peers | Add threshold/network logic only after the top-peer notebook is understood | Threshold sets, peer network, pairwise-rank exploration |

P1–P3 are implemented and ready for interactive review. The remaining work is
to inspect their outputs across markets, reconcile the headless QA runners,
and close the documented contract checks—not to add another Position notebook.
P3 exposes all-market paths and metric evidence rather than treating
`no_standout_trend` or `no_turn_signal` as missing results. P4–P6 then reuse
the same Position base rather than opening unrelated components.

### 3.2 Explanation

Position routing decides which of these runs first for a market. The order
below groups analyses so each one leaves a useful component for the next.

| Order | Analysis notebook | Reuses | New or widened component, if required | First outputs to inspect |
|---|---|---|---|---|
| E1 | Regional role | Benchmarking, WAC/RAC, existing geo labels | Regional comparison method; minimal regional rollups | Regional comparison table, inflow/outflow and market-role views |
| E2 | Q6 One metro? | Regional role components, WAC/RAC | Integration/polycentricity method | County integration table, sub-center comparison, market-structure map |
| E3 | Q4 Daily-needs access | POI Engine; Infrastructure Engine only where needed | Define the narrow daily-needs basket and access method in the analysis | Amenity inventory, tract access distribution, Richmond access map |
| E4 | Q1 Supply or demand | Existing housing inputs, Benchmarking | Housing structure/demand comparison method and reusable housing cut | Supply/demand quadrant, submarket comparison, diagnostic table |
| E5 | Q3 Where growth lands | Existing tract population/housing histories | Tract vintage handling and growth-change method | Infill/greenfield classification table and tract map |
| E6 | Q2 Job-proximity gradient | Existing job centers and tract prices; Infrastructure Engine when needed | First distance-based proximity method; routing stays optional | Price-distance curve, tract residuals, job-center map |
| E7 | Q5 Afford to live near jobs | Q2, housing and labor inputs | Jobs-housing affordability method; close OEWS gap if still required | Residence/workplace mismatch table and affordability map |
| E8 | Corridors | Internal Structure, Q4, Q2, Trajectory, POI and Infrastructure engines | Open the Corridor Intelligence Engine and candidate dataset | Corridor candidates, overlays, comparable corridor summaries |
| E9 | Parcel watch | Corridors, existing ROF parcel logic | MDD-specific screening only after a corridor is selected | Parcel candidate table and selected-corridor map |
| E10 | Catchment | Existing Place Intelligence catchment, apportionment, and barrier method | No promotion work until an MDD analysis actually reuses it unchanged | Weighted catchment map and tract contribution table |

For Richmond, E1–E3 are the current first-wave candidates, subject to the
Position notebooks. E8 and E9 stay late because they depend on several earlier
analyses rather than on one large up-front spatial build.

### 3.3 Thematic

Every theme runs nationally first and then in market mode. The order follows
shared component families so the first notebook in a family pays most of the
setup cost.

| Order | Analysis notebook | Reuses | New or widened component, if required | First outputs to inspect |
|---|---|---|---|---|
| T1 | A1 AI inversion | Industry datasets, Benchmarking | Theme-engine interface and governed exposure crosswalk | National exposure distribution, sector comparison, Richmond read |
| T2 | A6 Specialization predicts growth? | A1 industry surfaces, Benchmarking | Lagged LQ/growth method | National specialization-growth relationship and market cases |
| T3 | A10 Polarization | A1 industry surfaces | Wage-distribution inputs and method | Sector wage distributions and metro comparison |
| T4 | Housing satellite | Existing housing inputs, Benchmarking | Reusable housing component dataset | National housing diagnostic set and market scorecard |
| T5 | A2 Building lowers prices? | Housing satellite, Q1 method | Supply-response panel method | Permitting/price relationship and market cases |
| T6 | A7 Who is squeezed? | Housing satellite, Q1/Q5 inputs | Burden-versus-income comparison | National squeeze typology and Richmond read |
| T7 | A9 Converging or diverging? | Time-Series engine, Trajectory, Peers | Long-panel dispersion method | National convergence/divergence paths and peer cases |
| T8 | A4 Remote work rewired? | WAC/RAC, industry and housing surfaces | WFH/work-geography panel | National WFH shifts and selected market structure views |
| T9 | A5 How many downtowns? | Q6 integration/polycentricity, zone context | Downtown/sub-center typology | National center-count comparison and market maps |
| T10 | A3 Moving toward harm? | Q3 growth-change, existing hazard inputs | Hazard-growth comparison method | National hazard/growth quadrants and market maps |
| T11 | A8 Geography of life expectancy | Health inputs, Q4 access context | Health-context comparison method | National health distribution and within-market context |
| T12 | CBSA similarity study | Intelligence Framework, Peers | Methods review rather than a new data engine | Similarity distributions, sensitivity tables, peer-network examples |

This is not a promise to finish all Thematic work before returning to
Explanation. It is the reuse-aware order within the family. Routing and current
issue needs decide how the two families interleave.

## Time-series / trajectory — expanded panel ready for analytics review

The detailed method, initial KPI inventory, build checklist, DuckDB table
contracts, and review-output layout live in the
[Time-Series / Trajectory Engine build plan](../engines/time_series/TIME_SERIES_ENGINE_BUILD_PLAN.md).

The current single trajectory method is materialized in DuckDB under
`mart_intelligence`:
`intelligence_trajectory_series`, `intelligence_trajectory_metric`,
`intelligence_trajectory_frame`, and `intelligence_trajectory_turn_signals`.
It covers 50 direct recurring KPIs, a stable 396-CBSA universe, and a common
2023 end vintage. The eight derived-change candidates are documented for later
review and are not scored. Review exports are available under
`engines/time_series/outputs/review/`; DuckDB remains canonical.

The quick national check found coherent nested p80/p90/p95 signal tiers and a
deliberately selective turn layer (8 confirmed turns and 23 emerging watches).
Most metros have `no_turn_signal`, which means no unusually strong reversal
under the fixed-panel rule—not that they lack a trajectory. The Position /
Trajectory notebook is the next review point before the contract is frozen.

Not globally ordered as standalone work (correctly Partial/Not-built, each is
activated by a routed vertical slice): Theme engine interface, Industry
theme datasets and crosswalks, POI Engine, Infrastructure Engine, daily-needs
access method, Housing structure/demand method, Housing component datasets,
Standard thematic build method, Q6 polycentricity method, Tract growth-change
method, Job-center proximity method, Corridor Intelligence Engine, corridor
candidate datasets, Parcel screening logic, catchment/apportionment/barrier
method, Zone model outputs, Regional comparison and role method, Shared
benchmark and comparison datasets, Market-wide notebook config.

## All components (§6, full list)

Type legend: **engine** = reusable computational system · **method** =
reusable analytical logic · **mart** = queryable dataset layer · **infra** =
enabling input, not itself the analytical product.

| Component | Type | Priority | Readiness | Enables | Consumers (§2 issue outputs → §3 analyses) |
|---|---|---|---|---|---|
| Intelligence Framework outputs | engine | High | Exists | Act 1 identity assets, peer logic, trajectory context, internal-structure base, candidate scan | Act 1 Fingerprint KPI set, Cluster Label, Peer set; Act 4 Zone archetype map → Position: Profile, Peers, Trajectory, Internal structure, Candidate scan |
| Act 1 profile data frame / broader MDD profile marts | mart | High | Partial | Fingerprint KPI set, scorecards, radar/table inputs, deeper profile views | Act 1 Top-line stat boxes, Fingerprint radar, Fingerprint percentile table → Position: Profile |
| Shared comparison and benchmarking method | method | High | Partial | Regional comparisons, peer comparisons, theme comparisons, scorecards, benchmark tables across acts | Act 2 Benchmark comparison layer, Deeper market KPI-profile tables → Thematic A2–A10, Explanation: Regional role, Q6 |
| Shared benchmark and comparison datasets | mart | High | Partial | Queryable benchmark-ready cuts for national, Census Division, peer sets | Act 2 Benchmark comparison layer → (cross-cutting, no single analysis row) |
| Shared geo mart and rollups | mart | High | Partial | Tract, ZCTA, place, regional geography joins and labels program-wide | Act 4 Zone archetype map → Position: Internal structure; Explanation: Q3, Regional role |
| Time-series / trajectory engine and mart | engine | High | Implemented; review/freeze pending | Act 3 trend work, turn signals, candidate scan support, dynamic reads | Act 3 Tiered trajectory classifications, Turn-signal flags → Position: Trajectory |
| Zone model outputs | engine | High | Partial | Act 4 zone archetypes, zone summaries, corridor substrate | Act 4 Zone archetype map, Zone composition benchmark bar, Zone interpretation summary → Position: Internal structure; Explanation: Corridors |
| Regional comparison and role method | method | High | Partial | Regional role analyses, Q6 support, market-within-region interpretation | Act 2 Regional role analysis → Explanation: Regional role, Q6 |
| Housing structure and demand comparison method | method | High | Partial | Q1, A2, A7, housing diagnostics, pressure maps | Act 2 Explanation question slot (Q1) → Explanation: Q1; Thematic: A2, A7, Housing satellite |
| Housing component datasets | mart | High | Partial | Reusable supply/demand-side housing inputs | Act 2 Deeper market KPI-profile tables → Explanation: Q1; Thematic: A2, A7, Housing satellite |
| Daily-needs access method | method | High | Partial | Q4, livability summaries, corridor-supporting access evidence | Act 2 Access-amenities analysis, Built environment analysis → Explanation: Q4, Corridors |
| POI Engine | engine | High | Ready for first analysis | Classified, provenance-rich Richmond place points with tract/county assignment and postal-ZIP evidence; ZCTA geometry remains deferred in Geography | Act 2 Access-amenities analysis → Explanation: Q4, Corridors |
| Theme engine interface | engine | High | Partial | Standard all-market and market-mode thematic builds | Act 2 Theme analysis slot, Industry-economic makeup analysis → Thematic: A1, A2–A10 |
| Industry theme datasets and crosswalks | mart | High | Partial | A1, A6, A10, industry comparisons, exposure analyses | Act 2 Industry-economic makeup analysis → Thematic: A1, A6, A10 |
| Standard thematic build method | method | High | Partial | Reusable workflow for A1–A10 and future themes | Act 2 Theme analysis slot → Thematic: A1–A10 (all) |
| Q6 polycentricity and integration method | method | Medium | Partial | One Metro, market-structure interpretation, internal-center logic | Act 2 Social fabric analysis, Built environment analysis → Explanation: Q6; Thematic: A5 |
| Tract growth-change method | method | Medium | Partial | Q3, growth maps, infill-vs-greenfield views | Act 2 Explanation question slot (Q3) → Explanation: Q3 |
| Job-center proximity method | method | Medium | Partial | Q2, corridor-supporting inputs, internal opportunity comparisons | Act 4 Corridor narrative thesis → Explanation: Q2 |
| Infrastructure Engine | engine | Medium | Partial | Governed roads, rail, waterways, airports, ports, and other physical-network geometry | Act 2 Built environment analysis → Explanation: Q2, Q4, Corridors |
| Corridor Intelligence Engine | engine | Medium | Partial | Corridor candidate pools, selected corridor summaries, stat-block inputs | Act 4 Corridor candidate pool, Corridor Intelligence method → Explanation: Corridors |
| Corridor candidate datasets | mart | Medium | Not built | Reusable corridor-level inputs once zone/access/trend layers stabilize | Act 4 Corridor stat blocks → Explanation: Corridors |
| Parcel screening logic | method | Medium | Partial | Parcel Watch and parcel-level follow-through inside selected corridors | Act 4 Parcel screening logic → Explanation: Parcel watch |
| Catchment, apportionment, and barrier method | method | Medium | Exists | Catchment maps, tract weighting, barrier-aware variants, site-level supporting views | (none in §2) → Explanation: Catchment |
| Market-wide notebook config | infra | Low | Not built | Shared market constants and lock-once notebook inputs | (none in §2) → (cross-cutting, no single analysis row) |

## Notes

- "Consumers" = distinct issue-outputs or analyses in §2/§3 that name this
  component, by text match against the workbook — a rough proxy for reuse
  pressure, not an exact count.
- Promotion trigger (per `metro_deep_dive_program.md` §5): a component moves
  to `foundations/` when two different consumers use it unmodified. One
  consumer is a notebook; two is a library.
- This snapshot reflects the workbook and program doc as of 2026-09-07. If
  either source document changes materially, regenerate this file and
  `docs/build_map.html` together rather than letting them drift.
