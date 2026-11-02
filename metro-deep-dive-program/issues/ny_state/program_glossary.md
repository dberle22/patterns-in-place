# Program Glossary
Metro Deep Dive program terms that the Question Bank and Exhibit Bank use without defining. Definitions marked **(inferred)** were reconstructed from how the banks use the term; confirm or correct them.

## Program Structure
- **Metro Deep Dive (MDD):** the flagship publishing program. Three layers: `engines/` (reusable computation, promoted to `foundations/` on second use), `analyses/` (parameterized Marimo notebooks), `issues/` (publication folders with lock once decisions)
- **Analysis families:**
  - **Position:** where a market stands. Includes Profile, Peers, Trajectory, Internal Structure, and the Candidate Scan
  - **Explanation:** why it stands there. The Q analyses below
  - **Thematic:** cross market themes. The A analyses below. Spec'd and outlined, not all built
- **Frames:** Character, Livability, Opportunity. The three lenses every market is scored on; a cross frame score combines them
- **Frame composite scores:** updated 2026-11-02. Print clearance is open decision 15 in the Series Overview (previously held back from print until the Intelligence Framework review answered Section B and A1)
- **Composite scores** (affordability, overheating, economic strength, investment): built within each analysis as needed (an approach, not a production layer)

## Position Analyses
- **Profile:** frame and topic scores for one market against the nation
- **Peers:** most similar markets by frame and cross frame; cluster labels and peer lists are cleared for print
- **Trajectory:** how a market's position moved over time, with turn signals
- **Internal Structure:** how a metro is assembled internally (zones, downtowns, places). A Python script builds it per market; run it for each metro before use. Albany is done
- **Regional Role** (inferred): what a metro does for its wider region, via commuting and economic comparison. Partial today (LODES WAC/RAC only)

## Explanation Analyses (Q)
- **Q1** Housing supply and demand: is cheap housing a sign of supply or of absent demand
- **Q2** Job proximity: do people live near job centers (straight line distance only today)
- **Q3** (inferred) Where growth lands: greenfield, infill, or nowhere. Gated on tract vintage handling
- **Q4** (inferred) Amenity access: core amenities and access per tract. Uses the NY POI run and its categories; the basket is a pick of categories made at analysis time
- **Q5** (inferred) Can people afford to live near the jobs (uses OEWS)
- **Q6** (inferred) County integration: does an outlying county really belong in its CBSA, based on commuting. Threshold still open (decision 3); Albany Part 1 used OMB's 25% commuting test as a working threshold

## Thematic Analyses (A)
- **A1** AI Inversion: are the metros that won the knowledge economy transition the most exposed to AI task displacement (Felten AIOE scores joined to OEWS)
- **A2** Building Lowers Prices: does building more housing lower prices
- **A3** Moving Toward Harm: are people moving toward hazard exposure
- **A4** Remote Work Rewired: did remote work rewire where work happens
- **A5** (inferred) Downtowns: is there one main downtown or several. Banked
- **A6** Specialization: does industry specialization predict growth
- **A7** Who Is Squeezed: which people in which places carry the worst cost burden
- **A8** Geography of Life Expectancy
- **A9** **OPEN:** not referenced anywhere in the NY series docs. Add the definition
- **A10** Job Polarization: is the wage distribution polarizing, and where

## NY Series IDs
- **S** primer questions (S2 to S6 match Lenses 1 to 5), **R** regional, **M** metro spotlight, **K** rankings, **F** reader framings: all in the Question Bank
- **X** exhibits: Exhibit Bank
- **B** declared builds: Question Bank
- **D** and **E** rules: Approach

## Geography
- **REDC regions:** the 10 official Regional Economic Development Council regions; the series' base regional definition (D1)
- **Vernacular regions:** colloquial regions (Upstate, Downstate, Western NY, Southern Tier, North Country). Where they disagree with REDC is a theme in itself (for example, Rochester is usually called Western NY but the REDC puts it in the Finger Lakes)
- **CBSA:** Core Based Statistical Area, metro or micro, 2023 delineations (D4)
