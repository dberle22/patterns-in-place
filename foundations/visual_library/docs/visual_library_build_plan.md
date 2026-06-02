# Visual Library Build Plan Archive

## Status

This document is no longer the active operating plan for the visual library.

Use these files instead:
- [README.md] for folder navigation
- [visual_style_guide_and_standards.md] for canonical standards
- [sample_library.md] for the canonical chart catalog
- [agent.md] for the current build workflow

Keep this file as a historical roadmap and decision archive only.

## What This File Still Helps With

- understanding the order the library was originally scaffolded
- reviewing early implementation decisions and why they were made
- tracking the original intent behind the registry, benchmark defaults, and shared helper layers

## Current Reality

The original plan has largely been overtaken by the actual folder structure:
- the chart catalog now lives in [sample_library.md]
- the shared implementation lives in `visual_library/shared/`
- the test harness lives in [run_visual_library_tests.R]
- the working chart specs, decisions, and sample assets live in `visual_library/charts/<chart_type>/`

## Historical Decisions Carried Forward

- Keep one folder per chart type under `visual_library/charts/<chart_type>/`
- Centralize reusable prep/render logic under `visual_library/shared/`
- Keep benchmark defaults in [benchmark_defaults.md]
- Treat chart-specific specs as the first business-question source, with the shared catalog as fallback
- Use a registry/test-harness pattern rather than one-off chart scripts only

## Open Cleanup Gaps

- retire `Visual Library.docx` once the Markdown catalog has fully replaced it in practice
- keep references to the old `visual_style_guide.md` name cleaned up as they surface
- decide whether this archive should eventually become a shorter `history.md`
