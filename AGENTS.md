# AGENTS.md

Behavioral guidelines for AI coding agents working in this repo. Merge with task-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

---

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

---

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

---

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

---

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

---

## 5. Update Planning Docs

**Tick off tasks as you complete them.**

When working on a sprint or series of tasks:
- Tick off tasks as you complete them.
- Add any unplanned tasks that were required and tick them off once done.
- Add a short summary of completed work to the planning doc for easy review.

---

## 5.1 ETL Workflow Commands

**Build data layer work one step at a time.**

When adding a new source or table:
- Stage first. Only download, parse, normalize, and land the raw table.
- Inspect staging before writing Silver. Check row counts, columns, obvious nulls, and source quirks first.
- Keep staging source-faithful. Do tract/backbone validation, geographic joins, and contract enforcement in Silver unless the user asks otherwise.
- Build Silver next. Standardize grain, validate keys, and test joins only after staging looks right.
- Build Gold last. Do not design downstream rollups before the Silver shape is confirmed.
- Update docs and pipeline wiring after the code for that layer is working.
- Do not run parallel DuckDB writes. Materialize staging, Silver, and Gold steps sequentially.

---

## 6. Documentation Safety

**Never write machine-specific absolute paths into committed files.**

Do not hardcode paths like:
- `/Users/<name>/...`
- `/home/<name>/...`
- `C:\Users\<name>\...`
- Local OneDrive, Dropbox, iCloud, Desktop, Documents paths

**Exception — cross-folder references within this monorepo:** When a product folder (e.g. `publisher/`) must reference a sibling folder (e.g. `foundations/visual_library/`), use a `FOUNDATIONS_PATH` or `MONOREPO_ROOT` env var rather than a hardcoded absolute path. Document the expected env var in the folder's README.

Use repo-relative paths everywhere else:
- `foundations/etl/create_DB.R`
- `publisher/app/main.py`
- `<monorepo-root>/foundations/visual_library/shared/render`

Before finalizing any documentation change, scan changed markdown, YAML, JSON, SQL, Python, R, and shell files for local absolute paths.

---

## 7. Monorepo Orientation

This is the `patterns-in-place` monorepo. Top-level folders are independent product areas:

| Folder | Purpose |
|---|---|
| `foundations/` | Semantic layer, visual library, data dictionary, ETL pipeline |
| `publisher/` | NL→SQL engine, Insights Generator, Chatbot frontend |
| `stoop/` | Stoop Explore + Stoop Search |
| `metro-deep-dive/` | Long-form market reports, notebooks, R utilities |
| `area-explorer/` | Interactive CBSA tool (new) |
| `exploration/` | Ad hoc analysis and notebooks — never ships |
| `notes/` | Obsidian vault, roadmap, product notes |

**`foundations/` is a dependency, not a product.** Product folders reference it for the semantic layer, visual library, and DuckDB output. Do not embed copies of foundations assets inside product folders.

Each folder may have its own `README.md` and language-specific tooling (R, Python, etc.). When working in a specific folder, check for a local README before assuming project-wide conventions apply.

## 8. Inline Notes Style

When adding inline code comments, prefer richer explanatory notes over terse labels.
Comments should help a human quickly understand:
- what the block is doing
- why it exists
- any important business rule, exclusion, or modeling choice
- how the output of the block is used downstream

Favor section headers and brief walkthrough-style comments in the style of `foundations/etl/silver/acs_age_silver.R`.
Do not comment every line; focus on the parts that would otherwise take time to reason through.
