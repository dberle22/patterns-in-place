# Visual Library

## Purpose

This folder is the home of the reusable visual system for shared Patterns in Place analysis. It combines:
- chart specifications
- shared R prep and render functions
- data-contract standards
- benchmark defaults
- sample SQL and sample outputs
- workflow guidance for building new chart types

This `README.md` is the single entry point for the folder. Start here first, then follow the links below based on what you are trying to do.

This repo is intended to live under `projects/patterns_in_place/patterns-foundations` alongside sibling repos such as `patterns-data`. Keep references portable and repo-relative where possible.

## Who This Is For

This entry point is designed to work for:
- you, when you want a quick mental model of the library
- agents, when they need a reliable starting workflow and source-of-truth hierarchy
- new contributors, when they need to find the right doc, chart folder, or shared code path quickly

## Start Here By Task

If you want to understand the library at a high level:
- Read [visual_style_guide_and_standards.md]
- Read [sample_library.md]
- Skim [visual_library_build_plan.md] only for historical context

If you want to build or extend a chart type:
- Read [agent.md]
- Use [templates/chart_spec_template.md]
- Then work in `visual_library/charts/<chart_type>/`

If you want to understand shared implementation:
- Read [shared/standards.R]
- Read [shared/chart_utils.R]
- Read [shared/data_contracts.R]
- Check [shared/standards_implementation_status.md]

If you want benchmark or contract defaults:
- Read [benchmark_defaults.md]
- Read [contracts/data_contract_dictionary.md]

If you want examples and sample outputs:
- Read [sample_library.md]
- Browse `visual_library/charts/*/sample_output/`
- Run [run_visual_library_tests.R]

## Source of Truth Hierarchy

Use this order when docs overlap:

1. [README.md]
2. [visual_style_guide_and_standards.md] for canonical visual rules and implementation defaults.
3. [sample_library.md] for the canonical chart catalog and chart-family organization.
4. [agent.md] for the standard chart-build workflow.
5. [benchmark_defaults.md] and [contracts/data_contract_dictionary.md] for shared analytical defaults.
6. `visual_library/charts/<chart_type>/` docs for chart-specific requirements and decisions.
7. `visual_library/shared/` code for current implementation behavior.

## Folder Map

`charts/`
- One folder per chart type.
- Each chart currently has a spec, question coverage doc, decisions log, `sample_sql/`, and `sample_output/`.

`shared/`
- Reusable prep and render functions plus shared standards and contract helpers.

`contracts/`
- Shared contract vocabulary and review notes.

`templates/`
- Reusable starting template for new chart specs.

Top-level docs:
- `visual_style_guide_and_standards.md`: canonical visual standard
- `sample_library.md`: canonical chart catalog and example question source
- `visual_library_build_plan.md`: archived roadmap and governance history
- `agent.md`: build workflow for Codex and collaborators
- `workflow.md`: example build pattern from prior work
- `benchmark_defaults.md`: default benchmark sets by geography

## Recommended Workflow

When adding a new chart type or upgrading an existing one:

1. Start with [agent.md].
2. Draft or update the chart spec from [templates/chart_spec_template.md].
3. Confirm contract needs against [contracts/data_contract_dictionary.md].
4. Apply shared styling and helper patterns from `shared/`.
5. Build or refresh `sample_sql/` and `sample_output/` assets in the chart folder.
6. Record chart-specific exceptions in that chart's decisions log.

## Current Shape Of The Library

The folder is in good shape structurally:
- all 15 Core-15 chart folders exist
- each chart folder has the expected doc and sample subfolder pattern
- shared prep and render layers are centralized under `shared/`

The main organizational gap is not missing content. It is missing navigation. Important guidance currently lives across multiple top-level docs with overlapping roles.

## Known Cleanup Opportunities

These do not block using this folder, but they are worth cleaning up over time:
- `visual_standards.md` is a compatibility pointer and should stay lightweight.
- Some docs still refer to `visual_style_guide.md`, but the current canonical file is `visual_style_guide_and_standards.md`.
- `Visual Library.docx` is now legacy source material and can be removed once you are comfortable relying on the Markdown catalog.
- `workflow.md` is a useful case study, not the primary operating manual.

## Recommendation

Use this `README.md` as the permanent front door for `visual_library/`.

Why this is the best single entry point:
- `README.md` is the first file people expect in a folder.
- it can route different audiences without competing with the actual standards docs
- it keeps the canonical source-of-truth documents intact instead of forcing one of them to do too many jobs
- it gives agents a reliable document-order and workflow starting point
