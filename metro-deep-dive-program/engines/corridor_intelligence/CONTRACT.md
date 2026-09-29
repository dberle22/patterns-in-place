# Corridor Intelligence Engine Contract

**Status:** Prototype contract, paused 2026-09-09. The input/output
declarations and pilot artifacts remain for method reference only.

This contract preserves the proposed boundaries for the first engine build.
The Jacksonville and Richmond pilots did not establish a publishable local
geography, so this is not an active consumer contract.

## Contract boundary

The engine converts one declared Phase 7 tract surface, governed tract
geometry, approved infrastructure features, and an eligible aggregate POI
surface into reproducible structural candidates for one CBSA.

The engine owns:

- the shared grouping method and its version;
- the Corridor-specific interpretation of governed infrastructure features;
- the controlled use of aggregated POI evidence;
- core and bridge membership decisions;
- corridor, district, and unclassified form decisions;
- explicit parameter profiles and pilot overrides;
- complete tract assignment accounting;
- deterministic systematic candidate IDs; and
- structural, provenance, and sensitivity QA.

The engine does not own:

- the national Phase 7 tract model or its zone labels;
- geography identities, boundaries, vintages, or source geometry preparation;
- POI or Infrastructure source classifications;
- access, travel-time, catchment, trajectory, or parcel methods; or
- editorial names, candidate selection, opportunity framing, or publication
  styling.

No consumer may use this contract to publish or promote pilot outputs while
the engine is paused. Local-neighborhood mappings are the next geographic
priority; corridor work is analysis-local unless a future product decision
reopens this contract.

## Candidate concepts

| Concept | Definition |
|---|---|
| `primary_zone_type` | The Phase 7 type shared by all core tracts in a candidate |
| `core` member | A tract whose Phase 7 type exactly matches the candidate's primary type |
| `bridge` member | A different-type tract admitted under the conservative bridge rule |
| `corridor` | A linear or branched candidate organized around a shared physical spine or connected sequence |
| `district` | A compact, contiguous or near-contiguous candidate with no dominant physical spine |
| `unclassified` | A valid structural candidate whose form is not clear enough to call during review |

Corridor and district are two forms of the same structural-candidate object,
not separate engines or independently edited layers.

## Membership invariants

Every published run must satisfy all of the following:

1. A candidate is contained within exactly one `cbsa_code` but may cross county
   lines.
2. Every candidate has one primary Phase 7 zone type, and every core member has
   that exact type.
3. A bridge tract retains its original zone type and is explicitly labeled as
   a bridge; it is never silently relabeled.
4. A bridge must connect otherwise separated core sections, be structurally
   compatible with the core, and have supporting infrastructure continuity.
   POI evidence cannot justify a bridge by itself.
5. A tract has at most one candidate assignment in a run.
6. Every eligible tract is represented as a core member, bridge member,
   unassigned/noise tract, or explicit input exclusion.
7. Infrastructure and POI evidence can affect membership only through the
   declared, versioned method. Refreshing either input requires a new run; it
   never silently overwrites prior results.
8. The same inputs, method version, parameters, and code version reproduce the
   same assignments and IDs.
9. No manual tract reassignment is allowed. A bad result triggers method
   review, a visible parameter profile, or an accepted limitation.

The engine preserves the same-zone-only result as a comparison baseline so a
reviewer can see exactly what Infrastructure, POI, and bridge logic changed.

## Input contracts

### Phase 7 and Geography

The engine consumes the promoted Phase 7 tract surface and one governed,
market-scoped analytical geometry per tract. Every run identifies the Phase 7
build, tract universe, boundary vintage, geometry role, and distance-safe
spatial convention used.

The engine does not rerun or redesign Phase 7 and does not repair undocumented
geometry locally.

### Infrastructure

Infrastructure supplies governed source features, geometry, mapping status,
and run provenance. Corridor Intelligence assigns only the method-specific
roles needed for grouping, such as:

- spine or connector;
- separator;
- structural anchor; or
- ignored for this method.

Those roles are interpretations inside this engine, not new Infrastructure
source classifications. The first method uses a narrow approved feature set
and does not imply routability, travel time, or universal barrier behavior.

### POI

POI supplies classified place records, geography assignments, mapping status,
and source-run provenance. Corridor Intelligence aggregates eligible governed
categories into tract-level counts, rates, or composition shares.

Only categories that pass declared coverage and mapping checks may influence
membership. Aggregate POI evidence may refine a borderline connection, but it
cannot create a connection without a Phase 7, geographic, and structural case.
Individual establishments never create or break a candidate.

## Logical products

Canonical products will be written to the `mart_corridor_intelligence` schema.
The v1 fields and keys are fixed in
[`outputs/corridor_duckdb_contract_v1.yml`](outputs/corridor_duckdb_contract_v1.yml).

| Product | Grain | Purpose |
|---|---|---|
| `corridor_run` | one market × declared input set × method version | Reproduce the inputs, parameters, code, timing, and row accounting |
| `structural_membership` | one eligible tract × run | Record core, bridge, unassigned, or excluded status with evidence |
| `structural_candidate` | one candidate × run | Record primary zone type, spatial form, size, composition, and coherence |
| `structural_edge_evidence` | one evaluated tract relationship × run | Explain the geographic, Phase 7, Infrastructure, and POI evidence used |
| `corridor_qa_*` | run × applicable review group | Expose coverage, determinism, sensitivity, fragmentation, and portability |

The membership product is canonical. Candidate geometry may be stored when it
is needed repeatedly, but maps and display simplifications remain derived
artifacts.

## Identity and versioning

Each run records:

- market and Phase 7 input version;
- geography boundary and geometry version;
- Infrastructure source run and mapping version;
- POI source run and mapping version;
- grouping method, parameter profile, and code version; and
- input, assigned, bridge, unassigned, and excluded tract counts.

The systematic candidate ID is derived from the CBSA, primary zone type, and
sorted member tract set. It never contains a county rank, editorial place
name, or opportunity label. A membership change produces a new ID; the run
record explains why.

## Shared-method rule

- One shared method processes every represented zone type in a market.
- Jacksonville is used to calibrate the shared defaults.
- Richmond is then run as the first unchanged-method validation.
- Market-specific parameters are allowed only when the shared method cannot
  handle a documented physical condition. Any override remains visible to
  consumers and is never a manual membership edit.
- Results from different input, method, or parameter versions are not combined
  as if they were one run.

## QA requirements

Before a run is consumable, QA must show:

- unique Phase 7 inputs and one-to-one governed geometry coverage;
- source and method versions for every membership-affecting input;
- complete assigned, bridge, unassigned, and excluded tract accounting;
- primary-zone homogeneity among core members;
- no cross-CBSA or duplicate tract assignment;
- the effect of every bridge tract and every Infrastructure- or POI-sensitive
  connection;
- deterministic rerun equality for membership and systematic IDs;
- candidate size, form, fragmentation, and noise by market and zone type;
- comparison with the same-zone-only baseline and Phase 7 DBSCAN challenger;
- sensitivity across a small declared parameter range; and
- Jacksonville-to-Richmond portability without hidden tuning.

Visual review is required for the pilots, but local familiarity cannot justify
hand-editing tracts.

## Consumer rules

- Internal Structure reads engine outputs in its corridor/district section and
  does not use them as the master market geography or invent or rewrite IDs.
- Context overlays may explain a selected run, but changing an overlay does not
  mutate that run. Updated source evidence requires a new engine run.
- Corridor opportunity analysis may compare or shortlist existing candidates,
  but it does not merge, split, or reassign them.
- The issue layer owns editorial names and featured-candidate choices while
  retaining the engine ID for lineage.
- A structural candidate is evidence about market form, not an investment
  claim.

## Promotion

The first implementation stays in Metro Deep Dive. Promotion to `foundations/`
occurs only after two consumers use the same interface unchanged.
