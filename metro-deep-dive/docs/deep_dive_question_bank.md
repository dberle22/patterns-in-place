# Deep Dive — Market Question Bank

**Last updated:** 2026-08-04
**Scope:** Candidate questions for Metro Deep Dive acts, where the unit of comparison is *within* a market
**Companion to:** the split-out pipeline in `V1_REVIEW_PLAN.md`

## The distinction this file exists to hold

Two classes of question, distinguished by what is being compared.

| | Split-out pipeline | This file |
|---|---|---|
| Compares | Metros to each other | Places within one metro |
| Built as | A national method, instantiated per market | A market-native investigation |
| Reader learns about | Metros generally, illustrated by this one | This market specifically |
| Lives in | Its own report | A Deep Dive act |

**The useful consequence:** the national methods establish *where a market sits*. The market questions explain *why*. That is a Deep Dive act structure — position, then explanation — and most acts probably want one of each.

**The trap to avoid:** several questions here could be run nationally. That is not the test. The test is whether the reader comes away knowing something about this market or something about metros in general. "Housing mix and prices" run across 401 CBSAs is a split-out; run across Richmond's submarkets it is an act.

## Selection criteria

- The interesting variation is internal to the market
- The answer would differ meaningfully for a similar-sized peer
- It is answerable at tract, place, or county grain from existing Gold or a bounded addition
- It produces a claim, not a description

## Scope warning

**This file is broader than Industry.** Several entries below are Livability and housing questions, not economics. That is intentional and good — but it means this bank is not theme-one work and must not be pulled into the industry theme's two-week timebox. Questions here are scheduled against Deep Dive acts, not against the current theme.

---

## Q6 — Is this actually one metro?

**Question:** CBSA boundaries are administrative. Are the outlying counties functionally part of this metro, or merely attached to it?

**Why it is market-native:** the answer is a fact about this market's internal integration and cannot be inferred from its size or region.

**Draws on:** LODES commuting and employment integration, county-level industry mix, `gold.economics_lodes_wide`

**Frame:** Character

**Recommended placement:** **opener.** This establishes what is even being talked about before anything characterizes it — and it is a question most metro writing skips entirely, which makes it a strong differentiator for the first act a reader encounters.

**Produces:** a defensible statement about which parts of the CBSA behave as one labor market, and which do not.

**Open issues:** needs an integration threshold that is defensible and consistently applied; commuting-share cutoffs are conventional but arbitrary and the choice should be stated rather than buried.

---

## Q1 — Is housing cheap here because of supply, or because of weak demand?

**Question:** Where a market's housing is inexpensive, is that abundant supply or absent demand?

**Why it is market-native:** the decomposition only resolves at submarket grain. A metro with cheap housing and strong demand and one with cheap housing and no demand look identical in a median-price table.

**Draws on:** ACS housing stock composition, age, type, tenure; vacancy; permits; Zillow and FHFA HPI for level and appreciation

**Frame:** Livability, with Opportunity implications

**Produces:** a supply-versus-demand read per submarket rather than a price ranking. This is the entry that most reads as economics rather than description.

**Open issues:** permits data source and grain need confirming; appreciation and level must be treated as separate signals, not combined into one index.

---

## Q2 — What does proximity to jobs cost?

**Question:** How steep is the housing price gradient moving away from employment concentrations?

**Why it is market-native:** gradient steepness is a property of this metro's internal geography. A flat gradient and a steep one are genuinely different places to live.

**Draws on:** D3 job centers (already built), housing prices by tract or ZIP, tract geography

**Frame:** Character and Livability

**Produces:** bid-rent stated empirically for one market. Reuses existing D3 work rather than requiring new analytical machinery.

**Open issues:** requires the tract→place crosswalk from the fix plan Phase 3 to be readable; price data grain may not match tract grain and the join needs a stated method.

---

## Q3 — Where is growth actually landing?

**Question:** Is housing-unit and population growth going to greenfield edges, to infill, or nowhere?

**Why it is market-native:** inherently a question about internal distribution.

**Draws on:** ACS housing units and population change by tract, tract geography

**Frame:** Character, with Opportunity implications

**Produces:** the sprawl question stated so it can be answered rather than argued.

**Open issues:** tract boundary changes across vintages must be handled explicitly or the change series is unreliable.

---

## Q4 — What can you actually reach on foot here?

**Question:** Which parts of the metro have daily-needs access, and which do not?

**Why it is market-native:** amenity distribution is the definition of an internal question.

**Draws on:** Overture POIs, OSM, tract geography

**Frame:** Livability — which is otherwise the thinnest frame in the current work

**Produces:** an access read per tract.

**Why this one is worth prioritizing:** roughly `76,913` Overture POIs are already ingested for Richmond and **currently do nothing.** D4 renders them unusably and no analysis consumes them. This question is what would justify that ingestion retroactively. Note that the ingestion has only been run for Richmond, so this is Richmond-first by necessity.

**Open issues:** POI category taxonomy needs a defensible daily-needs definition; straight-line access is not walkable access and the copy must not overclaim, consistent with the D4 guardrail.

---

## Q5 — Who can afford to live near the good jobs?

**Question:** How does residence-side household income compare to workplace-side wages across the metro?

**Why it is market-native:** the mismatch is a spatial relationship inside one labor market.

**Draws on:** LODES RAC and WAC, ACS income by tract, OEWS wages

**Frame:** Opportunity

**Produces:** a spatial mismatch read with an equity lens.

**Relationship to the split-out pipeline:** pairs with split-out #3 (where people work vs. where they live) without duplicating it. The split-out asks which industries pull workers across metros generally; this asks who in this metro can afford proximity. Build the split-out method first if both are wanted, then instantiate here.

**Open issues:** workplace wages and residence incomes are different units and the comparison needs a stated normalization.

---

## Suggested act pairing

Not a schedule — a starting hypothesis for how these distribute.

| Act theme | National method (position) | Market question (explanation) |
|---|---|---|
| Identity / what this place is | Metro employment structure | Q6 — is this one metro? |
| Engine fabric (industry, Act 2) | AI exposure; does specialization predict growth | — |
| Housing | Where people work vs. where they live | Q1, Q2 |
| Conditions / livability | — | Q3, Q4 |
| Trajectory / opportunity | Same job, different pay | Q5 |

Gaps in this table are real and worth noting rather than filling for symmetry.

## Status

All entries are candidates. None is committed. Nothing here is in scope for the Industry section fix plan or the current theme timebox.