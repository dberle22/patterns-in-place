# Patterns in Place — Outreach & Distribution Tracker

*Working doc. Status values: `not started → joined/warming → contacted → responded → relationship`. Update as you go.*

---

## Content Asset Key

Every outreach move leads with a shipped artifact. These are the assets referenced in the tracker below, keyed to your actual pipeline:

| Key | Asset | Status / Unlock |
|---|---|---|
| **AI-1** | AI exposure × Opportunity, sector level (GS scores × QCEW, four-quadrant scatter) | Next up — blocked on QCEW diagnostic |
| **AI-2** | Occupation-level AI exposure deep dive | Blocked on OEWS ingest |
| **A1** | Livability/Opportunity four-quadrant scatter ("the unicorns") | Blocked on Phase 3 + 4 calibration |
| **A4** | Industry mix in 2015 predicted income growth in 2022 (QCEW longitudinal) | Phase 4 hypothesis test |
| **M1** | Methodology piece (frames, scoring, clustering) | After Phase 3/4 |
| **HIB-1** | "How It's Built": DuckDB medallion pipeline for 401 CBSAs | Writable now |
| **HIB-2** | "How We Built a Constrained NL-to-SQL Chatbot" | After chatbot deploys |
| **S1** | Stoop Explore launch post | App built; announce pending |
| **CH** | Individual chart posts (Daily Data Publisher queue) | Live now |

---

## Lane 1 — Urban Economics & Metro Analysis

*Primary audience-building lane. Goal: get cited/shared by people with distribution, build toward grad-school-adjacent credibility.*

| Target | Who/What | Lead With | Channel & First Move | When | Status |
|---|---|---|---|---|---|
| **Jay Parsons** | Rent/housing economist, large X following, actively engages independent analysts | **AI-1** or **CH** housing charts | X: reply to his posts with relevant charts 2–3x before any DM. Then DM with one finding. | Warming now; DM after AI-1 ships | not started |
| **Joe Cortright** | City Observatory — closest editorial model to a one-person metro publication | **A1** | Email via City Observatory contact. One paragraph + chart + link. Frame: "ran this across 401 CBSAs, thought of your work on [specific post]." | After A1 ships | not started |
| **Economic Innovation Group** (Connor O'Brien, Kenan Fikri) | Think tank; publishes metro-level economic analysis; very active on X; created the OZ program research base | **AI-1** (their beat exactly) and later OZ-overlay findings from Phase 4 | X engagement first — they reply to good charts. Then email research team with the AI exposure finding. | Warming now; email after AI-1 | not started |
| **Lyman Stone** | Demographics, migration, fertility; contrarian, engages replies | **CH** migration/demographic charts; later Character archetypes (A2) | X replies with charts. No email needed — he engages publicly. | Now | not started |
| **Jed Kolko** | Your stated model. Former Indeed/Commerce Dept | **A1** or **AI-1** | Email. He's known to respond to serious independent work. One finding, one chart, one specific question about method. | After A1 — your strongest single artifact | not started |
| **Aaron Renn** | Urbanist newsletter (Heartland/mid-sized metro focus) | **A7** hidden Livability winners angle, or **AI-1** | Email/Substack note. His audience = your "overlooked metros" content. | After AI-1 | not started |
| **Brookings Metro** | Institutional; slower; cites outside analysts in roundups | **M1** + a published finding | Email a specific researcher whose work overlaps (find via their metro monitor bylines), not a general inbox. | After 2–3 articles are live | not started |
| **Regional Feds (Cleveland, Atlanta)** | Both publish accessible metro research; Atlanta has strong data-tools culture | **A4** (longitudinal QCEW work is their language) | Email the regional economist team; reference their published work on industry composition. | After A4 | not started |

**Communities to join (this lane):**
- **X**: Build a list of urban econ / housing accounts (Parsons, Stone, EIG, Cortright, Darrell Owens, Alex Armlovich, M. Nolan Gray). Engage daily from the PiP account. *Join now.*
- **APPAM** (Assoc. for Public Policy Analysis & Management) — student/associate membership; directly serves the grad school path; annual conference is where SIPA/Wagner faculty are. *Join before applications (late 2026).*
- **NARSC / Regional Science Association** — the academic home of exactly your research interest (how places change over time). Student membership cheap. *Join when grad apps start.*
- **Urban Affairs Association** — same category, more sociology-flavored. *Optional.*

---

## Lane 2 — Data Engineering & Analytics Stack

*Goal: distribution via companies/communities that showcase user work. Highest ROI per effort because MotherDuck et al. actively want your story.*

| Target | Who/What | Lead With | Channel & First Move | When | Status |
|---|---|---|---|---|---|
| **MotherDuck** | Publishes community showcases, case studies, ecosystem posts. You're migrating to them anyway. | **HIB-1** + the chatbot (**HIB-2**) | Join their Slack community now. When migration happens, post about it there, then email devrel: "solo urban data platform, 43M-row QCEW, local→MotherDuck story." They will likely amplify. | Slack now; pitch at migration | not started |
| **DuckDB community** | Discord + GitHub discussions; small, technical, enthusiastic | **HIB-1** | Join Discord. Share the pipeline post when written. DuckDB Labs retweets good community projects. | Discord now; share at HIB-1 | not started |
| **Hacker News** | Show HN for the chatbot or Stoop; HIB-1 as a regular submission | **HIB-2** (Show HN: constrained NL-to-SQL) or **S1** | Submit Tuesday–Thursday, 8–10am ET. Constrained NL-to-SQL is a genuinely HN-shaped topic (reliability-over-openness contrarianism plays well). | At chatbot deploy | not started |
| **Locally Optimistic** | Slack community of data practitioners; job boards, show-and-tell channels | **HIB-1**, semantic layer design | Join Slack, lurk 2 weeks, then share in #show-and-tell equivalent. | Join now | not started |
| **dbt Community Slack** | Huge; your "MetricFlow-spec-without-dbt" decision is a conversation starter there | Semantic layer post (part of **HIB-1** or standalone) | Join; the semantic-layer channels debate exactly your architecture choices. | Join now | not started |
| **Streamlit forum/showcase** | Streamlit features community apps; you have two deployed | **S1**, ROF, chatbot | Submit Stoop Explore to their gallery/forum at launch. | At S1 | not started |

---

## Lane 3 — Data Viz & R Community

*Goal: steady chart-level distribution; feeds the Daily Data Publisher flywheel.*

| Target | Who/What | Lead With | Channel & First Move | When | Status |
|---|---|---|---|---|---|
| **R-bloggers** | Aggregator; syndicates R posts to a large audience free | Any Quarto/R post with code | Submit your Substack/Quarto RSS feed once you have 2–3 R-flavored posts. | After 2–3 posts | not started |
| **#rstats (Bluesky + X)** | The R community largely moved to Bluesky; ggplot2 work lands well there | **CH** charts with ggplot2 process notes | Create Bluesky account; post charts with brief method notes. Kyle Walker (tidycensus author) is active there — engaging him is natural given your stack. | Now | not started |
| **Kyle Walker** | Author of tidycensus — your core ingest tool | **HIB-1** (tidycensus at 401-CBSA scale) | Tag/mention when HIB-1 ships. He amplifies serious tidycensus use cases regularly. | At HIB-1 | not started |
| **r/dataisbeautiful** | Per your distribution plan: selective chart posts | **CH** — your strongest single-image charts (four-quadrant scatters do well) | [OC] posts, weekday mornings ET. Link to Substack in comments only. | Now, per publisher cadence | not started |
| **Posit Community / posit::conf** | Forum + annual conference; talks from independent analysts welcome | **HIB-1**; a posit::conf talk proposal (R + DuckDB + Quarto publication stack) | Forum now; conference CFP typically opens ~Jan for fall. A talk = instant credibility artifact for grad apps. | Forum now; CFP 2027 | not started |

---

## Lane 4 — NYC / Civic Tech (Stoop)

*Goal: launch amplification + in-person network. This lane doubles as grad-school network building (NYU/Columbia people are in these rooms).*

| Target | Who/What | Lead With | Channel & First Move | When | Status |
|---|---|---|---|---|---|
| **BetaNYC** | NYC's civic tech org; regular events, School of Data conference (annual, ~March) | **S1** demo | Join Slack + attend an event *before* launch so you're not a stranger. Demo Stoop at an event post-launch. | Join now; demo at S1 | not started |
| **NYC Open Data community** | Open Data Week (March), NYC Open Data team amplifies projects using their data | **S1** (uses NTA boundaries, equivalency tables, public POI) | Tag NYC Open Data at launch; apply for Open Data Week 2027 programming. | S1 + March 2027 | not started |
| **NYC data journalists** | Hell Gate, Curbed NY, THE CITY (data desk) | **S1** | Email at launch: 2 sentences + link + one screenshot. THE CITY's data team specifically covers neighborhood data tools. | At S1 | not started |
| **r/nyc** | Per your distribution plan | **S1** + Stoop-derived neighborhood charts | Launch post framed as "I built a free tool," not marketing. | At S1 | not started |
| **Data Through Design** | NYC data art/viz annual exhibition tied to Open Data Week | Stoop maps / choropleths as exhibition submission | Submission cycle ~winter. Long shot, high visibility. | Winter 2026–27 | not started |

---

## Lane 5 — Data Journalism & Newsletter Ecosystem

| Target | Who/What | Lead With | Channel & First Move | When | Status |
|---|---|---|---|---|---|
| **Data Is Plural** (Jeremy Singer-Vine) | Weekly datasets newsletter, ~40k+ subscribers; accepts submissions | A public dataset release — e.g., publish the calibrated frame scores or AI exposure index as downloadable data | Submit via the form on data-is-plural.com. Key move: release something *as data*, not just charts. | When frame scores or AI index are public | not started |
| **FlowingData** (Nathan Yau) | Features strong single visualizations | Best single chart from **A1** or **AI-1** | Email with the image inline. He features independent work regularly. | At A1/AI-1 | not started |
| **The Pudding** | Visual essays; accepts pitches; pays | A full visual-essay treatment (Character archetypes / "a new map of American metros" is the natural fit) | Pitch via their form — pitch the *idea* before building the custom treatment. | After A2 exists as evidence | not started |
| **APDU** (Assoc. of Public Data Users) | Legacy org for Census/BLS/BEA data users; conference + newsletter | **M1** / **HIB-1** | Join (~$100 individual). Their community is the professional home of your data sources; conference talks accessible to non-academics. | Join this year | not started |
| **ACS Data Users Group** | Free; run with Census Bureau; webinars + online community | **HIB-1** (tidycensus/ACS at scale) | Join free; propose a webinar once HIB-1 exists — they actively seek practitioner presentations. | Join now | not started |

---

## Sequenced Action Plan

**This month (no dependencies — join/warm only):**
1. Join: MotherDuck Slack, DuckDB Discord, Locally Optimistic, dbt Slack, BetaNYC Slack, ACS Data Users Group, Bluesky (#rstats)
2. Build the urban-econ X list; start daily engagement from the PiP account (replies with charts > original posts for reach right now)
3. Attend one BetaNYC event before Stoop launches
4. Draft **HIB-1** — it's writable today and unlocks Lane 2 + Kyle Walker + ACS DUG

**At AI-1 ship (first big article):**
- DM Jay Parsons; email EIG research team; email Aaron Renn
- FlowingData submission if the scatter is strong
- r/dataisbeautiful chart post

**At Stoop launch (S1):**
- BetaNYC demo, NYC Open Data tag, THE CITY / Hell Gate emails, r/nyc post, Streamlit gallery

**At A1 ship (L/O scatter):**
- Email Jed Kolko and Joe Cortright — this is the artifact that earns those emails
- Second FlowingData submission

**At chatbot deploy:**
- Show HN, MotherDuck devrel pitch, LinkedIn launch post (per your distribution plan)

**Late 2026 (grad app season):**
- Join APPAM + NARSC; posit::conf CFP watch; Data Through Design submission

---

## Outreach Template Principles

- One finding, one chart, one link. Never "I built a platform."
- Reference something specific they published. Generic praise reads as spam.
- The ask is implicit (they share if it's good) — never ask for a share directly on first contact.
- X/Bluesky: 2–3 substantive public interactions before any DM.
- Every contact gets a shipped artifact. If the artifact isn't live, the outreach waits.