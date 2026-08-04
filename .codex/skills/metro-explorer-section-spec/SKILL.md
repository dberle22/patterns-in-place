---
name: metro-explorer-section-spec
description: Draft SPEC.md for a new Metro Area Explorer section from the user's raw notes. Use when the user gives you rough notes/ideas for a new section (e.g. Industry, Housing, Demographics) and wants a spec drafted before any code is written. Requires the user's notes as input — this skill grounds and structures those notes against real repo state, it does not invent section scope from a topic name alone.
---

# Metro Area Explorer — Section Spec Drafter

Turn a user's rough notes into a `metro-deep-dive/metro-area-explorer/<section>/SPEC.md` that's grounded in real data and real prior decisions, not just reformatted notes. The value of this skill is the grounding step, not the template — do not skip straight to drafting.

**Requires the user's notes as input.** If the user asks to spec out a section by topic name only ("spec out Housing"), ask them for their notes/starting point first rather than inventing scope from scratch.

## 1. Load context before drafting anything

Read, in order:

- `metro-deep-dive/metro-area-explorer/README.md` — the folder scaffold and process contract every section must follow (SPEC.md / data_prep.py / app.py / decisions.md / notes.md, market-parameterized).
- `notes/patterns_in_place_notes/Products/Metro Deep Dive.md` and `metro-deep-dive/metro_deep_dive_build_approach.md` — the Acts/Fixed-Spine structure and what's already locked for the Deep Dive track.
- `metro-deep-dive/markets/richmond_va/SPEC.md` (or whichever market has the most developed spec) — check whether this section's topic already has locked spine content in an Act. Overlap is common; the Deep Dive spec stays the analytical spec of record for anything already locked there.
- Any relevant strategic-context or roadmap memory/notes for the topic.

Then verify data availability against real source, not memory:

- Grep `foundations/etl/gold/*.sql` for tables plausibly related to the topic. Read enough of each matching file to cite real column names — never assert a Gold column exists without having read it in the SQL.
- Grep `foundations/visual_library/chart_engine_py/chart_engine/{prep,render}/*.py` for existing chart types. For every visual the notes imply, determine: reuse existing chart engine module / net-new build / stretch-blocked on a missing data source.

## 2. Surface tensions before drafting — do not assume

Compare the user's notes against what Step 1 turned up. If there's a mismatch, stop and ask the user rather than silently resolving it:

- The topic overlaps existing Deep Dive Act content (e.g. the notes describe something already specified in a market's SPEC.md under a different structure or visual set).
- The notes imply an architectural choice not yet settled for this section (e.g. which market to spotlight, whether a doc is spec-of-record vs. a narrower companion, how this section's spec relates to the Deep Dive spec).
- A visual or data source the notes ask for has no clear Gold table or existing chart engine support — flag it as a real gap, don't paper over it with an assumed source.

Use targeted questions (2-4 options each, one recommended) rather than open-ended ones. Resolve every material tension before writing SPEC.md.

## 3. Draft `<section>/SPEC.md`

Create the folder if it doesn't exist: `metro-deep-dive/metro-area-explorer/<section>/`. Write only `SPEC.md` — do not create `data_prep.py`, `app.py`, or touch `README.md`. This skill's output is the spec only; building and logging are separate, later steps.

Use this structure:

```markdown
---
section: <section>
status: draft
spotlight_market: <market_name> (CBSA <geoid>)
last_updated: <date>
---

# <Section> — Section Spec

One-paragraph pointer: this is the spec of record for this section; data_prep.py and app.py are built to satisfy it.

## Purpose
Written market-agnostic. What question(s) this section answers, for any market — not just the spotlight market.

## Data sources
Table: source | Gold table | grain | notes (real column names, verified against SQL, with any caveats — sparsity, vintage lag, coarse grain).

## Deliverables
One subsection per deliverable. Each has:
- **What it produces** — the visual(s) and any narrative/stat output
- **Data source** — specific table + columns
- **Acceptance criteria** — a checklist of concrete, checkable conditions (renders for any valid market_id, handles sparse data without crashing, output matches an existing convention) — never just a restatement of what it produces
- **Build status** — reuse (names the existing chart_engine module) / net-new (first library addition) / stretch-blocked (names the missing dependency, explicitly says don't block ship on it)

## Tool requirements (Streamlit app)
Inputs, toggles, layout — the interactive surface, kept separate from the analytical deliverables above.

## Open decisions
Table: decision | blocks (which deliverable) | status. Anything deliberately left unresolved so it doesn't get decided by accident mid-build.

## Relationship to the Deep Dive
How this section's engines feed the corresponding market's `.qmd` Act section, and which existing Deep Dive spec content (if any) remains the locked spine this section must not contradict.
```

Every deliverable must be written market-agnostic: parameterized by a `market_id`, not hardcoded to the spotlight market. The spotlight market is a first-run choice, not a scope boundary.

## 4. Do not write code

This skill produces `SPEC.md` only. No `data_prep.py`, no `app.py`, no chart engine code — those are separate follow-on agent tasks once the user has reviewed and approved the spec.

## 5. Log the run in `decisions.md`

Append one entry to `<section>/decisions.md` (create the file if it doesn't exist) using the format defined in `metro-deep-dive/metro-area-explorer/README.md` under "Logging agent runs in decisions.md":

```markdown
## <today's date> — Draft SPEC.md
- **Agent / model:** <the model/agent identity you are running as>
- **Turns / iterations:** <how many back-and-forths it took to reach a spec the user could review — count clarifying questions asked as part of this>
- **Key decisions made:** <one line per material call you made in Steps 2-3 — e.g. spotlight market chosen, which visuals are reuse vs. net-new, any tension resolved by asking>
- **Notes:** <anything you had to guess or infer because the notes or repo context didn't specify it; anything that felt ambiguous about the spec-writing task itself>
```

This entry is the measurement data — it's what makes it possible to compare, across sections, whether the spec-drafting process is getting easier or harder as the pattern repeats. Keep it honest and terse; do not skip it even if the run was straightforward.

## 6. Hand back for review

End with a short, direct list of what needs the user's sign-off before building starts — the open decisions table plus any tension you resolved via a question during Step 2. Don't just say "let me know what you think" — name the specific items.
