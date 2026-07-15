# Manual Run Log

Use this file as the cross-run learning record for Chart Engine Phase 5 manual runs.

`step_notes.md` inside each `output/{q_id}/` folder is the per-question scratchpad.
This file is where we standardize what we learned across runs so we can improve
the Python package, the Chart-a-Day prompts, and the reviewer workflow.

## 2026-07-12 — q003 — ranking / bar_chart

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q003/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `sql` — q003 result output omitted `source` and `vintage`, which the R bar contract expects
  - `review_process` — CE-2 did not yet have a reproducible R wrapper, so I added `render_r_reference.R` in the output folder for this run
  - `render` — Python matches the story, but long metro labels and subtitle/note treatment are still less readable than the R reference
- Required changes:
  - Update the SQL/prompt contract so ranked-bar CE outputs include `source` and `vintage` when the R reference stack is part of the review path
  - Update the manual chart skill and later runner docs so the canonical Python parity artifact is `chart_py.png`, not `chart.png`
  - Update the social-copy workflow so `post.md` is the default artifact and platform files are only created when the copy actually diverges
  - Revisit Python bar label/caption layout so long CBSA names survive parity review without heavier truncation than R
- Ownership:
  - `chart_a_day` skills
  - `chart_engine_py`
  - reviewer guidance
- Ready to scale this fix to later runs? yes
- Notes:
  - q003 is no longer blocked. It is the first completed dual-render CE-2 proof point and gives us a concrete checklist for `q006`.

## 2026-07-12 — q006 — trend / line_chart

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q006/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `agent_prompt` — the manual render instructions still do not make the `.venv312` requirement explicit enough for Python static export runs
  - `theme` — Python static line-chart export dropped text when the packaged theme resolved to `Inter` on this machine
  - `render` — Python line-chart export keeps a one-series legend that the R reference suppresses
  - `spec` — Python `percent` formatting semantics are ambiguous when the CE result set already stores percentage-point values
- Required changes:
  - Update the Chart-a-Day Python render instructions so manual runs use `.venv312` or another environment that definitely contains `chart_engine` plus `vl-convert`
  - Add a safer static-export font fallback in `chart_engine_py` so Altair PNG output does not depend on `Inter` being installed locally
  - Clarify whether CE trend outputs should carry fractions or percentage points before they hit Python `NumberFormat(unit="percent")`
  - Consider suppressing the line legend automatically when there is only one visible series
- Ownership:
  - `chart_a_day` skills
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q006 is the first completed dual-render trend proof point. The remaining gaps are concentrated enough that we can keep moving, but line-chart static export still needs polish before we call it parity-complete in spirit.

## 2026-07-12 — q024 — map / choropleth

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q024/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `sql` — the geo extract needs `LOAD spatial` because the shared result set exports both `st_asgeojson()` and `st_astext()` geometry payloads
  - `agent_prompt` — Python geo manual runs need explicit `MPLBACKEND=Agg` and writable `MPLCONFIGDIR` guidance instead of assuming the local Matplotlib environment is ready
  - `theme` — Python map export still depends on a local font fallback because the packaged theme resolved to `Inter` on this machine
  - `render` — the Python choropleth matches the story, but palette, spacing, and legend-label treatment still drift from the R reference
- Required changes:
  - Update the Chart-a-Day geo workflow notes so manual map extracts always call out DuckDB `spatial` loading when geometry serialization is part of the SQL
  - Update the Python geo render instructions to include the backend/cache environment requirements for static Matplotlib export
  - Add a safer default font fallback path in `chart_engine_py` for map rendering so parity does not hinge on `Inter`
  - Revisit Python choropleth legend and map composition styling so the output reads as polished social-ready art, not just a correct analytical match
- Ownership:
  - `chart_a_day` skills
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q024 is the first completed geo/manual parity run. The analytical story matches in both stacks, and the remaining issues are now concentrated in environment setup plus Python styling polish.

## 2026-07-12 — q007 — compare_selected / bar_chart

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q007/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `agent_prompt` — compare-selected wrappers need to remind the reviewer to match `time_window` config values exactly to the SQL output
  - `render` — Python still truncates long CBSA labels more aggressively and compresses subtitle/caption treatment compared with the R reference
  - `review_process` — R wrapper conventions like `label_style = "dollar"` still have to be rediscovered by hand instead of being captured in one reusable compare-selected reference
- Required changes:
  - Add a small compare-selected bar example or checklist to the manual render guidance so `time_window`, currency label style, and benchmark setup are less trial-and-error
  - Revisit Python horizontal bar label/caption layout for long CBSA names and benchmark callouts
  - Consider storing a reusable R compare-selected wrapper template alongside the existing per-question artifacts
- Ownership:
  - `chart_a_day` skills
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q007 is a solid proof point that the environment cleanup worked. This was the first run in the new tranche using `.venv312` for both extraction and Python render.

## 2026-07-12 — q011 — benchmark / bar_chart

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q011/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `agent_prompt` — manual wrapper order still matters; the Python step assumes `result.csv` already exists and fails noisily if it is launched too early
  - `render` — Python benchmark charts still compress subtitle/caption text and benchmark annotation treatment compared with R
  - `review_process` — single-bar benchmark questions make it easier to notice layout differences, so they are a good regression checkpoint for benchmark styling polish
- Required changes:
  - Update the manual run instructions so the SQL extract is always treated as a required completed step before either render wrapper is launched
  - Revisit Python benchmark label/caption spacing on sparse bar charts
  - Consider adding a reusable benchmark-bar reference wrapper so later runs do not repeat the same scaffold work
- Ownership:
  - `chart_a_day` skills
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q011 is a useful proof point for the benchmark path because it stays analytically simple while still exercising benchmark labeling and single-bar composition.

## 2026-07-12 — q008 — compare_selected / line_chart

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q008/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `sql` — the first draft failed on a final alias mismatch, which is minor but reinforces the need to validate the query before rendering
  - `render` — Python line-chart parity still drifts in legend placement, title/caption density, and y-scale emphasis
- Required changes:
  - Add a quick SQL sanity step to the manual line-chart workflow before rendering
  - Revisit Python multi-series line legend placement and vertical range defaults so clustered lines retain more visual differentiation
- Ownership:
  - `chart_a_day` skills
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q008 is a good proof point for indexed multi-series comparison. The main remaining issues are visual polish rather than contract shape.

## 2026-07-12 — q009 — distribution / boxplot

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q009/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `agent_prompt` — Python boxplot wrappers must preserve canonical `metric_value`; remapping it away breaks the prep path
  - `render` — Python and R differ in orientation and metadata density, though the distribution story matches
  - `sql` — excluding Puerto Rico produced a cleaner “US metros” distribution view for this question
- Required changes:
  - Clarify in the manual chart instructions that some Python preps depend on canonical field names surviving, even when other chart types lean more on `column_mapping`
  - Decide whether vertical or horizontal should be the default presentation for single-group boxplots in parity review
- Ownership:
  - `chart_a_day` skills
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q009 is the first completed distribution proof point and gives us a concrete contract example for later boxplot and heatmap-table questions.

## 2026-07-12 — q025 — map / highlight_context_map

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q025/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `sql` — the geo extract still depends on `LOAD spatial`, and `.venv312` does not yet have the DuckDB `spatial` extension installed locally
  - `agent_prompt` — the map workflow still needs separate guidance for “Python environment works” versus “DuckDB spatial extension is available in this interpreter”
  - `theme` — Python emitted a font-cache warning pattern on this Matplotlib map path even though the render succeeded
  - `render` — the first Python highlight-context map had a compressed footprint and under-explained legend structure; the shared renderer now reserves legend space, labels the highlighted geography, and separates tier and role semantics
- Required changes:
  - Decide whether to install DuckDB `spatial` into `.venv312` or formally document a split extraction/render interpreter path for geo runs
  - Improve the environment guidance so geo extraction and geo rendering requirements are documented separately
  - Capture the font-cache prerequisite more explicitly for Matplotlib geo exports
- Ownership:
  - `chart_a_day` skills
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q025 started as the clearest blocker in the first tranche and is now a usable parity candidate after the shared geo-renderer fix pass.

## 2026-07-12 — q016 — correlation / scatter

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q016/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `chart_alt.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `agent_prompt` — the optional `hexbin` fallback is Matplotlib-backed, so it needs the same backend/cache setup guidance as geo renders
  - `render` — Python scatter is analytically right, but the R reference is still more polished on palette, legend treatment, and caption hierarchy
- Required changes:
  - Update the manual-run instructions so Matplotlib backend and `MPLCONFIGDIR` guidance applies to all Matplotlib-backed fallback charts, not just maps
  - Revisit Python scatter defaults for region palette, legend cleanliness, and presentation-mode caption density
- Ownership:
  - `chart_a_day` skills
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q016 is the first completed `correlation` proof point and the first run where the alternative Python artifact (`hexbin`) materially improved our environment guidance.

## 2026-07-12 — q017 — rank_change / slopegraph

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q017/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `prep` — the shared R `prep_slopegraph()` merge path duplicated `delta_value` into `.x/.y` columns when source rows already included deltas
  - `render` — the Python output is clearer than the R reference for this question because clustered endpoint labels still crowd in the R slopegraph
- Required changes:
  - Keep the new shared `prep_slopegraph()` delta normalization in place and treat it as part of the baseline two-period slopegraph contract
  - Revisit R slopegraph endpoint-label behavior when many highlighted metros finish at similar values
- Ownership:
  - `chart_engine_py` parity review docs
  - `foundations/visual_library/shared`
- Ready to scale this fix to later runs? yes
- Notes:
  - q017 is a valuable reminder that the R renderer is the reference implementation, but not always the stronger communication artifact on every question.

## 2026-07-12 — q018 — rank_change / bump_chart

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q018/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `review_process` — bump-chart questions need the fixed comparison-universe choice called out explicitly or rank movement is easy to misread
  - `render` — both outputs tell the same story, but Python currently produces the cleaner label and contrast treatment for the highlighted movers
- Required changes:
  - Keep the fixed-universe explanation visible in SQL notes and subtitle/caption guidance for future rank-change runs
  - Continue using bump-chart manual runs as a parity check for label contrast and endpoint readability
- Ownership:
  - `chart_a_day` skills
  - reviewer guidance
- Ready to scale this fix to later runs? yes
- Notes:
  - q018 closes the first `bump_chart` parity proof point without introducing new shared prep bugs, which is a strong sign for the remaining chart-type coverage run.

## Tranche Summary — Initial Manual Runs

## 2026-07-12 — q019 — composition / heatmap_table

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q019/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `render` — Python tells the same story, but ordering, spacing, and caption density still drift from the R reference on matrix-style layouts
  - `export` — the first Python static export failed because the shared heatmap-table label layer used a `scale=None` color encoding that `vl-convert` could not serialize reliably
- Required changes:
  - Keep the shared Python heatmap-table color-encoding fix in place so label text uses an explicit palette mapping during static export
  - Revisit Python heatmap-table row/column emphasis and spacing so highlighted entities read more intentionally in parity review
- Ownership:
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q019 closes the `heatmap_table` proof point for the composition family. The contract is stable; the remaining work is presentation polish.

## 2026-07-12 — q020 — composition / waterfall

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q020/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `render` — both outputs match analytically, but the R reference shows noticeably rougher axis/label composition than the Python result on this vacancy-tier share chart
- Required changes:
  - Treat q020 as a reminder that parity review should compare communication quality, not assume the R artifact is always the stronger presentation
  - Revisit whether the R waterfall renderer needs a small cleanup pass for axis-label treatment before it remains the visual benchmark for this chart family
- Ownership:
  - `foundations/visual_library/shared`
  - reviewer guidance
- Ready to scale this fix to later runs? yes
- Notes:
  - q020 is the clearest early case where the Python chart is already the more polished social-ready artifact.

## 2026-07-12 — q021 — composition / strength_strip

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q021/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `export` — the first Python static export failed because the shared strength-strip renderer mixed constant-value x encodings with field-based `x2`, which `vl-convert` rejected
  - `agent_prompt` — benchmark questions need an explicit fallback rule when the requested national comparison row does not exist in the live Gold table
  - `render` — Python is cleaner than the R reference here, but benchmark labeling assumptions still need to be made more explicit in the workflow notes
- Required changes:
  - Keep the shared Python strength-strip x/x2 fix in place for future benchmark and composition runs
  - Update the manual-run guidance so benchmark questions record whether the comparison is a literal national row, a peer median, or another derived reference
- Ownership:
  - `chart_engine_py`
  - `chart_a_day` skills
- Ready to scale this fix to later runs? yes
- Notes:
  - q021 closes the `strength_strip` proof point and adds a useful benchmark-assumption rule for later content work.

- Stable now:
  - The dual-render artifact contract is working across ranked bar, single-series line, and choropleth runs.
  - `chart_py.png` plus `chart_r.png` is a good review surface for deciding whether a question is truly parity-complete.
  - A single canonical `post.md` is enough for the default social-copy workflow unless platform-specific copy genuinely diverges.
- Repeated failure modes:
  - Environment assumptions still leak into manual runs: `.venv312`, `vl-convert`, DuckDB `spatial`, Matplotlib backend/cache setup, and local font availability.
  - Python outputs are analytically correct more often than they are socially polished; the recurring drift is in captions, legends, label layout, and spacing.
  - Result-set semantics still need tighter prompt guidance, especially around percent formatting and required metadata fields like `source` and `vintage`.
- Prompt changes adopted:
  - Keep the canonical social artifact as `post.md`, with platform override files only when the copy actually differs.
  - Treat `chart_py.png` and `chart_r.png` as the required Phase 5 parity artifacts.
  - Use `MANUAL_RUN_LOG.md` as the durable cross-run learning record, with `step_notes.md` staying local to the question folder.
- Code changes adopted:
  - None repo-wide from q024 alone; this tranche mostly clarified where the remaining fixes belong.
- Reviewer checks that caught real issues:
  - Comparing Python and R side by side exposed missing metadata fields, ambiguous percent semantics, one-series legend behavior, and map-specific environment assumptions that a Python-only review would have missed.

## 2026-07-12 — q022 — correlation / correlation_heatmap

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q022/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `prep` — the shared R correlation-heatmap prep failed when it pushed a tibble slice directly into the reshape/correlation path
  - `render` — Python is analytically right, but R still has the stronger title/caption hierarchy for presentation review
- Required changes:
  - Keep the shared R prep coercion to a base data frame in place so correlation-matrix questions do not fail on tibble inputs
  - Revisit Python matrix caption hierarchy and spacing during the later visual polish pass
- Ownership:
  - `foundations/visual_library/shared`
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q022 closes the `correlation_heatmap` proof point and resolves a genuine shared R prep bug.

## 2026-07-12 — q023 — demographic / age_pyramid

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q023/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `prep` — the shared Python prep was dropping `facet_label`, which blocked the intended selected-vs-benchmark overlay path
  - `render` — both outputs match the story, but the R benchmark overlay is visually denser than the cleaner Python comparison
- Required changes:
  - Keep the shared Python `facet_label` preservation in place for benchmark-overlay age-pyramid runs
  - Treat overlaid benchmark age pyramids as a strong Python proof point rather than assuming the R reference is automatically clearer
- Ownership:
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q023 closes the `age_pyramid` proof point and confirms the Miami-vs-US benchmark workflow.

## 2026-07-12 — q026 — map / proportional_symbol_map

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q026/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `sql` — geometry extracts still require DuckDB `spatial`, including a one-time extension install in `.venv312` before `LOAD spatial` works
  - `render` — the shared Python proportional-symbol renderer failed when a color-group value was missing from its hard-coded palette mapping
  - `agent_prompt` — Matplotlib-backed geo wrappers still need explicit writable cache guidance so Python does not appear to hang or quit during font-cache setup
  - `render` — Python remains materially rougher than R on legend placement and label composition for dense bubble maps
- Required changes:
  - Keep the Python color-group palette fix in `render_proportional_symbol_map.py`
  - Document the `INSTALL spatial` plus `LOAD spatial` requirement for geometry SQL on fresh Python interpreters
  - Carry the writable cache environment pattern into future Matplotlib-backed wrapper templates
- Ownership:
  - `chart_engine_py`
  - `chart_a_day` skills
- Ready to scale this fix to later runs? yes
- Notes:
  - q026 closes the `proportional_symbol_map` proof point, but it should be a priority candidate in the next visual-polish pass.

## 2026-07-12 — q027 — map / bivariate_choropleth

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q027/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `render` — Python renders correctly, but the R reference allocates more room to the national map and the bivariate key, making the quadrant decoding easier
  - `review_process` — bivariate maps require the inversion/binning assumption to be called out explicitly or the legend semantics are easy to misread
- Required changes:
  - Keep the inversion explanation visible in subtitle/caption guidance for future bivariate housing-stress maps
  - Revisit Python bivariate legend and map-footprint composition during the later style pass
- Ownership:
  - `chart_engine_py`
  - reviewer guidance
- Ready to scale this fix to later runs? yes
- Notes:
  - q027 closes the `bivariate_choropleth` proof point without introducing new shared prep failures.

## 2026-07-12 — q028 — correlation / hexbin

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q028/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `agent_prompt` — Matplotlib-backed wrappers still need explicit writable cache guidance so first-run font-cache work does not look like a silent Python failure
  - `render` — both outputs tell the same density story, but the R reference is still more polished on spacing and caption hierarchy
- Required changes:
  - Carry the `XDG_CACHE_HOME` plus `MPLCONFIGDIR` pattern into future Matplotlib-backed manual render templates
  - Revisit Python hexbin title/caption spacing during the visual-polish pass
- Ownership:
  - `chart_a_day` skills
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q028 closes the `hexbin` proof point and gives us a clearer explanation for the earlier intermittent Python-run concern.

## Cross-Run Visual QA Review — 2026-07-12

Reviewed against `foundations/visual_library/docs/visual_style_guide_and_standards.md`,
with emphasis on clarity first, comparison-first hierarchy, restrained non-data ink,
subtitle usefulness, legend placement, and presentation-mode polish.

### High-severity findings

- `q025` `highlight_context_map` — Python is not parity-ready as a communication asset.
  - The rendered map footprint is too small relative to the canvas, which breaks the
    style-guide expectation that maps read as first-class visuals rather than side assets.
  - The legend explains outline roles, but not the fill-color tiers that carry the story,
    so the encoding is not self-decoding.
  - The role legend sits on top of the plotted map area, which violates the guidance to
    preserve chart area and keep legend placement from hurting readability.
  - Recommended fix:
    - Rework extent and subplot layout so the contiguous-US map uses the available frame.
    - Add a tier legend for the fill colors and separate it cleanly from any highlight-role legend.
    - Reserve legend space outside the data footprint.

- `q024` `choropleth` — Python color semantics drift from the stated analytical framing.
  - The Python subtitle/note says darker states indicate higher renter cost burden, but the
    actual scale reads as `viridis`-like with bright yellow at the high end.
  - This creates a direct mismatch between text, style-guide emphasis rules, and visual encoding.
  - Recommended fix:
    - Either reverse the palette so darker means higher, or rewrite the subtitle/note and
      legend language so the encoding is truthful and consistent.
    - Prefer aligning to the R reference and the style-guide wording rather than changing copy.

### Medium-severity findings

- `q009` `boxplot` — Python tells the distribution story, but the presentation is much weaker than R.
  - The vertical orientation creates a large mostly empty plotting area around a single box.
  - The subtitle/caption stack is compressed into the top margin instead of feeling like a clear hierarchy.
  - The rotated category label is awkward for a one-group distribution view.
  - Recommended fix:
    - Default single-group boxplots to horizontal orientation, matching the stronger R composition.
    - Give the plot more horizontal emphasis and move metadata into a clearer caption block.

- `q008` `line_chart` — Python under-emphasizes variation across tightly clustered series.
  - The y-scale spans much more than the signal range, so the five lines read flatter than they should.
  - The legend is pushed outside the plot in a way that competes with the chart width and title area.
  - Recommended fix:
    - Tighten default y-range logic for indexed comparison lines when the question is about relative separation.
    - Revisit multi-series legend placement so it supports comparison without stealing plot width.

- `q003`, `q007`, `q011` `bar_chart` family — Python is analytically solid but too cramped for presentation mode.
  - Long labels are truncated harder than R.
  - Subtitle and source/note text feels mechanically packed instead of deliberately layered.
  - Sparse benchmark compositions do not yet have the breathing room the style guide calls for.
  - Recommended fix:
    - Increase default title/subtitle/caption spacing and improve long-label handling for horizontal bars.

### Low-severity findings

- `q006` `line_chart` — the one-series legend should be suppressed by default.
  - It adds non-data ink without helping interpretation.

- Cross-run typography/export drift
  - Python outputs are still more sensitive to local font availability than the review workflow should allow.
  - Recommended fix:
    - Keep the current `Inter` preference, but make fallback behavior deterministic enough that text hierarchy survives export cleanly.

### Shared design themes from this review

- The R outputs more consistently satisfy the style-guide hierarchy:
  - stronger title/subtitle separation
  - clearer caption treatment
  - better use of available canvas
  - more intentional legend placement

- The Python outputs are usually analytically correct, but often miss presentation-mode polish in four repeated ways:
  - too much unused whitespace
  - captions packed into chart margins instead of reading as a true footer
  - legends placed for implementation convenience rather than reading flow
  - map encodings that are technically drawn but not fully explained

### Recommended fix order before the next big tranche

1. Fix geo legend and color semantics in `choropleth` and `highlight_context_map`.
2. Improve single-group `boxplot` presentation defaults.
3. Tighten cross-chart title, subtitle, and caption spacing for presentation exports.
4. Revisit multi-series line-scale defaults and one-series legend suppression.

## Follow-Up Fix Pass — 2026-07-12

- Implemented in `chart_engine_py`:
  - `choropleth` now uses a darker-high sequential blue scale and figure-level title/subtitle treatment that keeps the encoding truthful to the subtitle copy.
  - `highlight_context_map` now uses explicit map bounds, separate vacancy-tier and map-role legends, and direct highlight labeling.
  - `boxplot` now defaults single-group views to a horizontal layout, which materially improves the one-group distribution presentation.
  - `line_chart` now suppresses one-series legends and tightens indexed multi-series y-range defaults so clustered series retain more visual separation.
- Parity status after rerender:
  - `q009` improved from a visibly weaker Python presentation to a reasonable parity candidate with only minor remaining polish drift.
  - `q024` no longer has the subtitle-vs-color-scale semantic mismatch that originally failed the style-guide check.
  - `q025` moved from `blocked` to `match_with_minor_drift` after the shared geo-renderer changes.

## 2026-07-12 — q010 — distribution / boxplot

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q010/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `render` — Python still carries denser caption/title stacking and busier axis ticks than the R reference
- Required changes:
  - Keep tightening the Python presentation-mode text hierarchy for single-group boxplots
- Ownership:
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q010 is a useful confirmation that the single-group horizontal boxplot fix generalizes beyond rent-to-income.

## 2026-07-12 — q012 — benchmark / bar_chart

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q012/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `render` — Python benchmark annotation still feels slightly tighter and less spacious than the R reference
- Required changes:
  - Revisit benchmark spacing defaults once we have a few more single-bar benchmark examples
- Ownership:
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q012 is another clean benchmark proof point and did not surface a new renderer class of bug.

## 2026-07-12 — q013 — growth / bar_chart

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q013/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `render` — Python still truncates long metro labels more aggressively and packs metadata more tightly than the R reference
- Required changes:
  - Continue improving long-label handling and title/caption spacing on larger ranked bar charts
- Ownership:
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q013 extends the bar-family proof set into the growth template without introducing a new contract issue.

## 2026-07-12 — q004 — trend / line_chart

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q004/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `chart_alt.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `render` — Python still packs subtitle/caption text more tightly than the R reference on dense multi-series trend charts
  - `review_process` — multi-series metro trends need a manual display-label pass when full CBSA names would overwhelm the legend in social-sized exports
- Required changes:
  - Add explicit display-label guidance to the Chart-a-Day trend workflow for long-metro-name questions
  - Revisit whether high-series trend questions should prefer `line_chart` over `slopegraph` as the default publishable artifact when the fallback labels crowd together
- Ownership:
  - `chart_a_day` skills
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q004 is a solid proof point that the Python trend path works better when the workflow treats concise display labels as part of presentation polish, not as a data change.

## 2026-07-12 — q005 — trend / line_chart

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q005/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `chart_alt.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `render` — Python remains slightly denser than R in subtitle/caption treatment on multi-series trends
  - `review_process` — the fallback slopegraph is still a weaker communication chart when too many series converge at the right edge
- Required changes:
  - Keep the concise display-label rule in the manual trend workflow for long-name metro comparisons
  - Treat `chart_alt.png` as optional comparison evidence rather than the preferred final artifact when slopegraph labels crowd
- Ownership:
  - `chart_a_day` skills
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q005 confirms the q004 label-handling fix generalizes to another multi-series trend set without introducing a new renderer bug.

## 2026-07-12 — q014 — growth / bar_chart

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q014/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `render` — Python still truncates a few long metro labels more aggressively and carries denser metadata stacking than the R reference
- Required changes:
  - Continue tightening long-label handling and presentation-mode text spacing on ranked bars as more growth questions come through
- Ownership:
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q014 extends the growth template coverage cleanly and did not surface a new SQL or contract issue.

## 2026-07-12 — q001 — ranking / bar_chart

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q001/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `review_process` — the inherited q001 artifact set was answering the wrong question, so legacy pre-CE outputs cannot be assumed to match the current backlog entry
  - `render` — Python still truncates long metro labels and packs title/note text more tightly than the R reference
- Required changes:
  - Add a quick “does the existing result metric actually match the backlog question?” check whenever we reuse a legacy question folder
  - Keep tightening long-label handling on ranked bars, but this is now polish rather than a blocking parity gap
- Ownership:
  - `chart_a_day` skills
  - reviewer guidance
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q001 closes cleanly once refreshed. The key lesson is workflow hygiene, not chart logic.

## 2026-07-12 — q002 — ranking / bar_chart

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q002/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `render` — Python remains slightly denser than R in the caption block on ranked bars
- Required changes:
  - Continue tightening presentation-mode spacing on ranked bars, but no new workflow or contract fix is required from q002
- Ownership:
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q002 is a straightforward proof point that the ranked-bar workflow now works cleanly for state-grain income questions too.

## 2026-07-12 — q015 — ranking / bar_chart

- Run scope: both
- Artifact status: complete
- Parity verdict: match_with_minor_drift
- Output folder: `publisher/chart_a_day/output/q015/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `render` — Python still abbreviates some long metro labels more aggressively and compresses notes relative to the R reference
- Required changes:
  - Keep the ranked-bar polish work going, but q015 did not reveal a new chart-family bug or workflow gap
- Ownership:
  - `chart_engine_py`
- Ready to scale this fix to later runs? yes
- Notes:
  - q015 rounds out the core ranking set by confirming the same bar workflow works for demographic diversity metrics.

## Entry Template

```md
## 2026-07-12 — q003 — ranking / bar_chart

- Run scope: python | r | both
- Artifact status: complete | partial | blocked
- Parity verdict: match | match_with_minor_drift | blocked | not_reviewed
- Output folder: `publisher/chart_a_day/output/q003/`
- Artifacts present: `question.md`, `result.sql`, `result.csv`, `chart_py.png`, `chart_r.png`, `post.md`, `step_notes.md`
- Gap classes:
  - `render` — benchmark annotation missing in Python output
  - `agent_prompt` — chart_request prompt did not tell the reviewer to preserve the same subtitle text as R
- Required changes:
  - Update `chart_engine_py` bar renderer to preserve benchmark labeling
  - Update `chart_a_day/skills/chart_request.md` review checklist to compare subtitle, note, and benchmark text directly against `chart_r.png`
- Ownership:
  - `chart_engine_py`
  - `chart_a_day` skills
- Ready to scale this fix to later runs? yes | no
- Notes:
  - Any short explanation that will help on the next run
```

## Tranche Summary Template

Add a short summary after the first tranche (`q003`, `q006`, `q024`) and update it
again when a new repeated failure pattern appears.

```md
## Tranche Summary — Initial Manual Runs

- Stable now:
  - ...
- Repeated failure modes:
  - ...
- Prompt changes adopted:
  - ...
- Code changes adopted:
  - ...
- Reviewer checks that caught real issues:
  - ...
```
