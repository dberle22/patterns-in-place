# Python vs R Parity Register

## Summary Table
| Chart type | Overall status | Primary gap layer | Blocking gaps | Major gaps | Notes |
|---|---|---:|---:|---:|---|
| `bar_chart` | `major` | `render` | 0 | 2 | Python covers ranked bars but not the deferred grouped/stacked/diverging contract described in the R spec. |
| `line_chart` | `blocking` | `prep` | 1 | 2 | Python prep/render is materially narrower than the R line workflow; Phase 4 also still lacks the planned golden regression test. |
| `scatter` | `major` | `render` | 0 | 2 | Core scatter works, but R's reference-line / quadrant / highlight-mode surface is only partially ported. |
| `slopegraph` | `major` | `prep` | 0 | 2 | Python forces a simple two-endpoint value view and drops the richer R selection and variant logic. |
| `boxplot` | `major` | `prep` | 0 | 2 | Python boxplot is a basic box-plus-highlight overlay without the R benchmark, weighting, or faceting behavior. |
| `heatmap_table` | `major` | `render` | 0 | 2 | Python renders a simple blue matrix; R carries more ordering, highlight, legend, and methodology semantics. |
| `bump_chart` | `major` | `prep` | 0 | 2 | Python computes ranks and draws lines, but R owns the real entity-selection and label strategy. |
| `waterfall` | `major` | `render` | 0 | 2 | Python covers a simple waterfall but not the benchmark-faceted comparison path used by the R tests. |
| `strength_strip` | `major` | `render` | 0 | 2 | Python does not yet express the benchmark-delta and comparison semantics documented in R. |
| `correlation_heatmap` | `major` | `prep` | 0 | 2 | Python supports a single correlation matrix, but the R prep/render path includes faceted comparison workflows. |
| `age_pyramid` | `blocking` | `render` | 1 | 2 | Python omits the benchmark-outline and facet behavior used by the canonical R age-pyramid questions. |
| `choropleth` | `major` | `render` | 0 | 2 | Python renders a continuous map only; R supports continuous, binned, diverging, and faceted map workflows. |
| `hexbin` | `major` | `prep` | 0 | 2 | Python handles a basic density plot, but the R path includes weights, medians, and faceted comparison setups. |
| `highlight_context_map` | `major` | `prep` | 0 | 2 | Python keeps highlight and neighbor flags but not the R variant and benchmark logic. |
| `proportional_symbol_map` | `major` | `render` | 0 | 2 | Python plots circles and labels; R adds scale legends, color-group semantics, and richer note handling. |
| `bivariate_choropleth` | `major` | `render` | 0 | 2 | Python renders one map and one inset key; R supports faceting and a more configurable legend/composition path. |

## Gap Count By Severity
| Severity | Count |
|---|---:|
| `blocking` | 3 |
| `major` | 31 |
| `minor` | 2 |
| `acceptable` | 1 |

## Gap Count By Layer
| Layer | Count |
|---|---:|
| `spec` | 6 |
| `prep` | 8 |
| `render` | 13 |
| `theme` | 1 |
| `export` | 2 |
| `tests` | 7 |
| `docs` | 0 |

## Repeated Cross-Chart Problems

### repeated spec drift
- Shared finding: generated Python specs are intentionally minimal artifacts, but `scripts/generate_chart_specs.py` only preserves front matter plus a one-line body, while the R source specs carry variants, preprocessing rules, QA checks, and example question banks.
- Evidence: [generate_chart_specs.py](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/chart_engine_py/scripts/generate_chart_specs.py), [bar_chart.md](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/chart_engine_py/chart_engine/chart_specs/bar_chart.md), [bar_spec.md](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/charts/bar/bar_spec.md)
- Severity: `major`
- Layer: `spec`

### repeated render drift
- Shared finding: many Python renderers implement the simplest visual form only, while the R shared renderers own benchmark, facet, label-strategy, or variant-specific semantics.
- Evidence examples: [render_line.py](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/chart_engine_py/chart_engine/render/line.py), [render_line.R](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/shared/render/render_line.R), [render_choropleth.py](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/chart_engine_py/chart_engine/render/choropleth.py), [render_choropleth.R](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/shared/render/render_choropleth.R)

### repeated theme drift
- Shared finding: the Python packaged theme sets `fonts.family: "Arial"` while the R standards layer's `visual_font_family()` returns `"Inter"`.
- Evidence: [pip_theme.yml](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/chart_engine_py/chart_engine/pip_theme.yml), [standards.R](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/shared/standards.R)
- Severity: `minor`
- Layer: `theme`

### repeated export/runtime drift
- Shared structural export finding: Altair-backed Python charts store captions in `chart.usermeta` instead of rendering them into the image, while R renderers put source/vintage/notes into the plot caption.
- Evidence: [render_scatter.py](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/chart_engine_py/chart_engine/render/scatter.py), [render_boxplot.py](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/chart_engine_py/chart_engine/render/boxplot.py), [render_scatter.R](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/shared/render/render_scatter.R)
- Severity: `blocking`
- Layer: `export`
- Shared environment/runtime finding: `_vegalite_version_for_altair()` uses a Vega-Lite 5 runtime bridge for Altair 4 specs. That is a compatibility workaround, but the code comments document it as a pragmatic runtime bridge rather than a known semantic drift by itself.
- Evidence: [orchestrator.py](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/chart_engine_py/chart_engine/orchestrator.py)
- Severity: `acceptable`
- Layer: `export`

### repeated test drift
- Shared finding: Python now has regression coverage across the Altair analytical family, but the geo chart tests are still structural-only and skipped when matplotlib is unavailable.
- Evidence: [PLAN.md](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/chart_engine_py/PLAN.md), [test_regression.py](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/chart_engine_py/tests/test_regression.py), [test_geo_render.py](/Users/danberle/Documents/projects/patterns_in_place/foundations/visual_library/chart_engine_py/tests/test_geo_render.py)
- Severity: `major`
- Layer: `tests`

## Structural vs Export/Environment Issues
- Structural parity gaps: spec compression, narrowed prep logic, missing render variants, benchmark handling, facet behavior, and question-pattern coverage gaps.
- Export/environment issues: invisible Altair captions in exported artifacts, runtime dependence on `vl-convert`, and geo render tests that skip when matplotlib is absent.

## Audit Assumptions And Known Limits
- Assumption: the current R visual library is the parity reference unless an intentional deviation is already documented in repo docs.
- Assumption: missing behavior was logged as a gap rather than inferred from comments or roadmap intent alone.
- Verification run: `python3 -m unittest discover foundations/visual_library/chart_engine_py/tests` passed on 2026-07-11 with `38` tests run and `5` skips.
- Known limit: this pass compared source, specs, and tests directly; it did not run the R chart test scripts or build side-by-side manual artifacts for all 16 chart types.

## Progress Update 2026-07-12
- Shared fixes closed in code:
  - generated Python specs now preserve the source spec body and question coverage body instead of front-matter-only stubs
  - packaged Python theme now matches the R default font family (`Inter`)
  - Altair regression coverage now includes `line_chart`
  - visible caption/source/vintage handling now ships through the Altair title/subtitle block for `line_chart`, `scatter`, `slopegraph`, `boxplot`, `heatmap_table`, `bump_chart`, `waterfall`, `strength_strip`, `correlation_heatmap`, and `age_pyramid`
- Chart-specific blockers closed in code:
  - `line_chart`: prep now covers indexed, rolling, completed-period, benchmark, and highlight paths; render now covers benchmark and facet semantics; regression golden added
  - `age_pyramid`: prep now distinguishes selected vs benchmark rows more faithfully; render now supports benchmark outlines and automatic facet layouts; regression golden updated
  - `slopegraph`: prep now supports explicit periods, indexed/rank variants, endpoint completeness checks, curated entity selection, and display ordering; render now adds variant-aware subtitles/y-axis titles plus richer endpoint delta labels
  - `bump_chart`: prep now supports request-driven entity selection strategies, peer/highlight retention, endpoint metadata, and rank-source fields; render now separates context/peer/highlight lines and richer endpoint labels
  - `strength_strip`: prep now preserves benchmark inputs, computes normalized and benchmark-normalized positions, and exposes benchmark deltas; render now supports benchmark markers and multi-window comparison composition
  - `boxplot`: prep now supports request-driven filtering, group median ordering, benchmark propagation, and trimmed display handling; render now supports benchmark overlays plus richer highlight/label behavior
  - `heatmap_table`: prep now supports variant-aware matrix completion, polarity-aware normalization, explicit row/column ordering, and richer cell labels; render now supports highlight outlines plus diverging percentile fills
  - `waterfall`: prep now supports grouped cumulative paths, total rows, additive metadata, and benchmark-panel grouping; render now supports comparison panels, connector lines, and value labels
  - `correlation_heatmap`: prep now supports group-split/faceted correlation matrices, weak-correlation masking, and method metadata; render now supports comparison panels and richer methodology subtitles
  - `choropleth`: prep now supports request-driven fill variants, benchmark-relative fills, and bin derivation; render now supports continuous, binned, diverging, and faceted map panels
  - `highlight_context_map`: prep now supports focus-only vs analytical variants, explicit highlight requirements, and role metadata; render now supports role-aware fills and faceted panels
  - `proportional_symbol_map`: prep now supports Top-N decluttering, rank/share metadata, and label strategies; render now supports explicit size and color legends
  - `bivariate_choropleth`: prep now supports grouped bin metadata and request-driven bin recomputation; render now supports faceted comparison panels and a more flexible bivariate key layout
  - `hexbin`: prep now supports request-driven filtering, non-negative weight validation, and quantile trimming hooks; render now supports weighted density labels, faceted comparison panels, and optional reference lines
- Verification on the updated tranche:
  - `python3 -m unittest foundations.visual_library.chart_engine_py.tests.test_regression` passed on 2026-07-12 with `11` tests
  - `python3 -m unittest discover foundations/visual_library/chart_engine_py/tests` passed on 2026-07-12 with `52` tests and `5` skips
- Remaining parity caution:
  - the summary tables above reflect the baseline audit snapshot, not a recomputed post-fix scorecard
  - geo render coverage is still stronger structurally than it is visually; golden-style map regression remains a later QA/refinement task
