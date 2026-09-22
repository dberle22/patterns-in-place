# Explanation Regional Role Spec

**Status:** V1 contract aligned after Epic 1 audit; Epics 2–5 implementation
complete

**Build order:** E4 — independent track; does not depend on the access spine

**Default market:** Richmond, VA (`40060`)

**Initial method:** `regional_role_v1`

**National posture:** market scoped. The method should scale across markets, but
this is not a national ranking or coverage-table product.

## Goal

Establish how a selected market fits into its broader region economically,
demographically, and functionally. Regional Role is a workbench: it runs the
same evidence through several declared regional boundaries so an analyst can
see both the market's role and how that read changes with the boundary.

It extends, rather than recreates, Position. Profile supplies market identity
and governed KPIs; Peers supplies similarity peers; Trajectory supplies stored
time-series context. Regional Role adds regional membership, division of labor,
jobs-versus-workers context, and migration exchange.

## V1 boundary: what we will and will not build

V1 establishes four repeatable regional lenses, a reusable Geography-owned
membership interface, and an analyst workbench for one selected CBSA. Role
labels remain manual conclusions drawn from visible component evidence; V1 does
not create a market-role score or automatic typology.

V1 does not claim commuting flows or functional integration. LODES WAC/RAC
describe jobs located in a geography and workers living there; they do not link
workers to workplaces. LODES OD is materialized at county-pair grain with
explicit coverage, but remains a V2 dependency until its method is declared.

## Region lenses

Each lens returns a set of comparable CBSAs that includes the target CBSA. The
same regional comparison surfaces run against each lens.

| Lens ID | Lens | V1 membership rule | Why it belongs in V1 |
|---|---|---|---|
| `census_division` | Census division | All metropolitan CBSAs in the target's Census division. | Governed identity fields already support it; it is legible and stable. |
| `primary_state` | Primary state | All metropolitan CBSAs in the target's primary state. | A clear, familiar comparison boundary. |
| `primary_state_adjacent` | Primary state plus adjacent states | All metropolitan CBSAs in the target's primary state and every state sharing a boundary with it. | Tests a broader, state-legible regional orbit without choosing a radius. |
| `cbsa_centroid_250mi` | 250-mile CBSA proximity | All metropolitan CBSAs whose declared centroid is at most 250 great-circle miles from the target CBSA's declared centroid. | A transparent, repeatable proximity challenger to state boundaries. |

For a multi-state target CBSA, **primary state** is the first state abbreviation
in the official CBSA name after the comma. For example, `Wheeling, WV-OH` has
West Virginia as its primary state. This is already the rule used by the
Geography-owned `gold.dim_geo.state_fips` field; it is not based on county
count or population. The adjacent-state lens starts from that one primary
state, not every state touched by the CBSA.

The 250-mile lens is a geographic-proximity measure, not a travel-time or
day-drive claim. The stored membership must retain the calculated distance so
V1 can inspect 200-, 250-, and 300-mile sensitivity without redefining the
method for one market.

**Deferred lenses:** megaregions require a sourced, versioned layer and are
out of V1. Functional labor sheds are an eventual output from LODES OD, not an
input lens.

## Proposed reusable Geography interfaces

These are proposed V1 data-mart interfaces, not tables created by this spec.
They belong to Geography because Regional Role, Q6, and later regional
comparisons can reuse the same boundary definitions. Their builders must use
approved analytical geometry; existing display geometry is not approved for
distance or adjacency calculations.

| Proposed surface | Grain | Core fields | Purpose |
|---|---|---|---|
| `mart_geography.state_adjacency` | state × adjacent state × boundary vintage | `state_fips`, `adjacent_state_fips`, `boundary_vintage`, `source`, `method_version` | Reusable, symmetric land-boundary relationship for the adjacent-state lens. Adjacency requires a shared border line of nonzero length: a river boundary counts; ocean, Great Lake, and point-only contact do not. |
| `mart_geography.cbsa_centroids` | CBSA × boundary vintage × centroid method | `cbsa_code`, `boundary_vintage`, `centroid_method`, `longitude`, `latitude`, `source`, `method_version` | Declared reference point for reproducible geographic-proximity calculations. |
| `mart_geography.region_lens_membership` | target CBSA × lens × parameter set × member CBSA | `target_cbsa_code`, `lens_id`, `lens_version`, `parameter_name`, `parameter_value`, `member_cbsa_code`, `member_role`, `distance_miles`, `membership_source` | One auditable membership surface for all four lenses. `distance_miles` is populated only for centroid-radius membership. |

The existing `gold.dim_geo`, `silver.xwalk_cbsa_state`, and
`silver.xwalk_cbsa_county` remain the identity and containment inputs. Their
current crosswalk vintage is 2023. The membership surface should not copy or
replace those governed relationships.

## V1 evidence inputs

| Input | V1 use | Constraint |
|---|---|---|
| Position Profile, Peers, and Trajectory | Identity, governed KPIs, peer context, and stored time-series context. | Consume existing outputs; do not recompute labels, peers, or trajectories. |
| Benchmarking | National, division, and peer comparison context. | The national metro-CBSA benchmark is the highest-level baseline above the regional lenses. Do not use the current Benchmarking `state_primary` set for this analysis until it adopts Geography's first-named-state rule; it currently derives primary state from county count. Regional-lens membership is separate. |
| `gold.economics_industry_wide` | Broad-sector employment, LQs, concentration, wages, establishments, and GDP context. | Use consistent sector definitions and source vintages in a comparison. |
| `gold.economics_lodes_wide` and LODES WAC/RAC | 2023 workplace jobs, resident workers, earnings bands, and broad industry composition. | Describe jobs-versus-workers only; never call the difference inflow or outflow. WAC coverage is less complete than RAC in some geographies. |
| `gold.migration_wide` and `silver.irs_migration_summary` | Existing county, CBSA, and state IRS inflow, outflow, and net-migration context. | Coverage is 2012–2022; these summary surfaces do not identify partner CBSAs. |
| `silver.irs_migration_flows` | County origin-destination migration flows, rollable to origin-CBSA × destination-CBSA for partner-metro exchange: returns, exemptions/people, and AGI. | Coverage is 2012–2022; values can be suppressed or null, especially AGI. Clearly label it as household tax-return migration, not commuting. |
| Infrastructure consumer interface | Market-scoped roads, rail, and water-network context from a validated Infrastructure run. | V1 may use it for a contextual map once Geography supplies the approved analytical CBSA boundary required to promote the serving candidate. It is not a routing or access input. |
| Geography display geometry | Maps of declared result surfaces. | Display only; do not use for adjacency, distance, or area calculations. |

## V1 workbench structure

Two notebooks separate reusable boundary setup from market interpretation.
Neither writes a Regional Role mart; both query the governed and proposed
read-only surfaces above.

| Surface | Purpose | Primary controls | Main result |
|---|---|---|---|
| `EXPLANATION_REGIONAL_ROLE_SETUP_NOTEBOOK.py` | Inspect how each lens is constructed before role evidence is interpreted. | Target CBSA; lens; radius sensitivity. | Lens provenance, membership table, membership overlap, and boundary map. |
| `EXPLANATION_REGIONAL_ROLE_NOTEBOOK.py` | Run the selected market's role evidence against the declared lens. | Target CBSA; active lens; selected KPI/sector; migration year and measure. | Comparison, industry, jobs/workers, migration, and manual-hypothesis evidence surfaces. |

The setup notebook should be built first. It must make an incorrect or
surprising membership set visible before the role notebook uses it.

## V1 comparison and analysis surfaces

Regional comparison uses CBSA as its consistent comparison unit. County is the
native unit for IRS migration flows and is not mixed into the CBSA comparison
table.

| Surface | Grain | V1 calculation / interpretation |
|---|---|---|
| National metro baseline | target CBSA × KPI × year | Target value, national metropolitan-CBSA median/mean, percentile/rank where supported, and source provenance from Benchmarking. This is the highest-level context above division and the regional lenses. |
| Lens comparison panel | target CBSA × lens | Membership count, total population/economic scale where supported, and target versus active-set median/mean for a small declared KPI set. It displays all four lenses side by side. |
| Active regional comparison | target CBSA × active lens × member CBSA | Sortable CBSA table of selected Position/Benchmarking and labor/industry metrics, with source year and membership provenance. |
| Industry-role comparison | target CBSA × active lens × broad sector | Compare the target's sector share and LQ with the aggregate of the other member CBSAs. The purpose is visible specialization evidence, not an automatic role label. |
| Jobs-versus-workers balance | target CBSA × active lens × member CBSA | `jobs_total`, `workers_total`, absolute difference, and ratio from 2023 LODES. It is descriptive workplace/residence balance, not commuting flow. |
| IRS migration exchange | target CBSA × origin/destination CBSA × year, with county detail available | Roll detailed county flows to partner-CBSA exchange, retaining within-target-CBSA moves as a separate category. Keep county endpoints outside any CBSA in an explicit `non_cbsa_county` category rather than dropping them. Classify partner CBSAs as inside or outside the active lens; retain the largest outside-lens partners so distant relationships remain visible. |
| Infrastructure context | target CBSA × validated source run × feature | Display roads, rail, and water network as a contextual map layer once the approved Geography boundary is available. It is not a role score or national coverage product. |
| Manual hypothesis evidence | selected market × run | A small analyst-authored notes/table surface that links a proposed role statement to the visible metrics and their caveats. It does not generate a label. |

## V1 visuals

The lens comparison is persistent; detailed views are filtered or tabbed by the
active lens. This avoids showing four copies of every visual while keeping
boundary sensitivity inspectable.

| Visual | Surface | Question answered |
|---|---|---|
| Lens membership matrix and overlap view | `region_lens_membership` | Which CBSAs enter or leave as the boundary changes? |
| Active-lens membership map | membership plus display geometry | What geography does the chosen lens actually select? |
| National metro baseline | national metro baseline | How does the target sit in the national metropolitan environment before regional context is applied? |
| Four-lens comparison panel | lens comparison panel | Is the target's basic regional position stable across boundaries? |
| Active regional comparison table and KPI map | active comparison | How does the target compare with the regional set on a selected metric? |
| Industry-role dot/bar comparison | industry role | Which sector differences distinguish the target from the rest of the active region? |
| Jobs-versus-workers map/table | balance | Where are jobs and resident workers relatively concentrated? |
| IRS partner-CBSA exchange map plus all-origin/destination ranking | migration exchange | Which nearby and distant metros exchange migrating households, people, and AGI with the target, and how much movement stays within the target CBSA? |
| Infrastructure context map | infrastructure context | How do the target market's major roads, rail, and water features frame the regional read? |
| Manual role-hypothesis evidence table | manual hypothesis evidence | What observed evidence supports or complicates an analyst's proposed reading? |

## V2 and why it waits

| V2 capability | Why deferred |
|---|---|
| LODES OD commute-shed and cross-boundary commuting surfaces | County-pair OD is available for 2023 provider coverage, with Alaska and Michigan marked unavailable. V2 must declare its functional-integration rule before using OD. |
| Functional labor-shed lens | It must be derived from OD evidence, so it cannot responsibly precede OD ingestion and validation. |
| Megaregion lens | No governed source, membership layer, or coverage decision exists. It is additive once the V1 lens workflow is stable. |
| National infrastructure comparison | Infrastructure is market-scoped today. A cross-market infrastructure comparison needs a separately governed, nationally consistent coverage and feature-comparability decision. |
| Network travel-time regional lens | V1's centroid radius is intentionally geographic proximity. Travel-time requires a routed network and a separately validated reach method. |
| Automated role labels or typology | Manual interpretation is safer while the evidence combination and boundary sensitivity are still being learned. |

## Guardrails

- Do not label WAC/RAC balance as inflow, outflow, commute shed, or functional
  integration.
- Do not claim travel behavior from centroid distance; label the 250-mile lens
  as geographic proximity.
- Do not silently omit migration flows outside the active lens; distinguish
  inside-lens and outside-lens flows.
- Do not silently drop IRS flow endpoints that do not belong to a CBSA; retain
  them as an explicit non-CBSA county category.
- Do not combine county IRS-flow rows and CBSA comparison rows in one rank or
  denominator without first rolling the county flows to an explicit CBSA-pair
  surface.
- Preserve source grain, year, coverage gaps, and suppression/null status.
- Do not rebuild Position identity, peer, benchmark, or trajectory logic.
- Keep final prose and role labels analyst-authored.

## Resolved and remaining decisions

Resolved for V1: first-named-state treatment for multi-state CBSAs; land-only
state adjacency; four listed lenses; 250-mile default with sensitivity review;
megaregions deferred; manual role labels; a national metro baseline; and a
persistent all-lens panel plus active-lens detail views.

Before implementation, select the initial KPI/sector set for the comparison
panel and define the minimum flow-count/suppression disclosure displayed with
IRS migration results. These are presentation and interpretation safeguards,
not automatic classification rules.

## References

- Section 5.1 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
- [EXPLANATION_ANALYSES_FEEDBACK.md](../EXPLANATION_ANALYSES_FEEDBACK.md)
- [EXPLANATION_REGIONAL_ROLE_BUILD_PLAN.md](EXPLANATION_REGIONAL_ROLE_BUILD_PLAN.md)
