# Metro Area Explorer

To build our Metro Deep Dive series I have decided that we should build small Streamlit apps for each data section. These will be tools to help us gather insights, visualize trends, and explore our data more holistically. It's similar to the broader Area Explorer product. We can almost think about it as working MVPs of what will go into the product version. The goal of this will be to outline how we develop using Specs, Visual Templates, Semantic Layers, and the rest of our Foundations.

We are also using this series as our testbed for spec-driven development itself: each section is a unit we can hand to an agent, and we want to be able to measure how well the spec set the agent up to succeed — not just whether the output looks right.

## Folder scaffold

Each section gets its own folder here (`industry/`, and more as we add sections). Everything for that section — spec, data prep, app, and process notes — lives together in that one folder:

```
<section>/
  SPEC.md         # analytical + tool spec of record for this section, in one doc
  data_prep.py    # data pulls and transforms, parameterized by market (CBSA), not hardcoded
  app.py          # the Streamlit app
  decisions.md    # terse running log: decision made, why, when
  notes.md        # rawer in-the-moment observations, friction, surprises — raw material for the retro
  outputs/        # cached exports if needed, per-market
```

Sections are market-parameterized from the start. Richmond is our first Deep Dive market and gets first billing as we build each section, but the spec, data prep, and app should all take a market identifier as an input rather than being written Richmond-only — the point is that section #2's market run costs us a parameter change, not a rebuild.

## Spec-driven development, with measurement

We're treating each section as a small pipeline of agent tasks:

1. **Build the spec** — research available data (Gold/staging tables, existing engines in `foundations/`), draft `SPEC.md` end to end: sections, KPIs, visuals, data sources, and acceptance criteria per deliverable. No code yet. Human reviews before anything is built.
2. **Build data prep**
3. **Build the app**
4. **Log + retro** — `decisions.md` and `notes.md` are kept live during the build; once a section ships, we write up what worked and what didn't as part of the technical-writing series.

`SPEC.md` carries acceptance criteria per deliverable so agent output can be checked pass/fail rather than eyeballed. Effort/iteration tracking and "what was ambiguous, what did the agent have to guess" retro hooks live in `decisions.md`/`notes.md`, not in the spec itself — that keeps the spec purely about the analytical and tool content.

### Logging agent runs in `decisions.md`

Every agent task against a section (spec draft, data prep, app build, revision) gets one entry appended to that section's `decisions.md`. This is the measurement layer — it's what lets us compare how well a spec set an agent up to succeed, across sections and over time, once we have more than one data point. Use this shape:

```markdown
## <date> — <task, e.g. "Draft SPEC.md">
- **Agent / model:** <e.g. claude-opus-4-8, general-purpose agent>
- **Turns / iterations:** <count, or "single-pass" / "N revisions after review">
- **Key decisions made:** <one line per material decision, e.g. "chose employment-share as D1 default view">
- **Notes:** <anything ambiguous the agent had to guess, friction, surprises — link to notes.md if it's long>
```

Keep entries terse — this is a log, not prose. `notes.md` is where the longer, messier version of any entry goes if it's worth capturing for the eventual retro write-up.

The first section we're fleshing out is Industry.

## Running A Section App

For now, standardize on the repo's `.venv312` environment for Metro Area Explorer work. It has the app dependencies we need for Streamlit, DuckDB, and Altair.

Launch the Industry D1 app from the repo root with:

```bash
.venv312/bin/python -m streamlit run metro-deep-dive/metro-area-explorer/industry/app.py
```

The same pattern should hold for future section apps:

```bash
.venv312/bin/python -m streamlit run metro-deep-dive/metro-area-explorer/<section>/app.py
```

## Validating A Section

There are two validation layers we want for these section tools:

1. Programmatic validation: the data prep and chart rendering paths run without error.
2. Visual review: open the Streamlit app, switch markets/views, and inspect whether the charts and copy are actually legible and truthful.

For the Industry D1 section, use:

```bash
.venv312/bin/python -m pytest metro-deep-dive/tests/test_industry_d1.py
```

That test is meant to catch:
- expected latest-year coverage for Richmond
- share totals by basis/year
- successful render of the stacked bar and bump chart
- generation of the takeaway sentence from measured deltas

If `pytest` is not installed yet in `.venv312`, install the test tools there first:

```bash
.venv312/bin/python -m pip install pytest
```

For a lightweight syntax check, use:

```bash
.venv312/bin/python -m py_compile \
  metro-deep-dive/metro-area-explorer/industry/data_prep.py \
  metro-deep-dive/metro-area-explorer/industry/app.py \
  metro-deep-dive/tests/test_industry_d1.py
```
