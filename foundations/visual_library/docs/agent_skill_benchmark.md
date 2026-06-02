# Agent vs Skill Benchmark

## What Can Be Measured

There are two different performance questions:

1. Context payload: how much instruction text we ask Codex to consider.
2. End-to-end delivery time: how long it takes to produce usable chart artifacts.

The first can be approximated locally. The second needs repeated runs with similar chart tasks, because most wall time comes from tool calls, file reads, R execution, image inspection, and iteration decisions.

## Current Context Size Check

Run:

```sh
Rscript scripts/visual/benchmark_visual_context_size.R
```

This reports bytes, words, and rough token estimates for:

- `visual_library/agent.md`
- `~/.codex/skills/visual-chart-builder/SKILL.md`
- the narrower supporting visual skills
- the large common visual docs that are usually read during chart work

As of the first check:

- `visual_library/agent.md`: about 1,405 words
- `visual-chart-builder` skill: about 684 words
- primary plus supporting visual skills: about 1,128 words
- `sample_library.md`: about 12,289 words
- `visual_style_guide_and_standards.md`: about 3,797 words

That means the core skill is not larger than the old agent file. If the skill workflow feels slower, the likely cause is broader behavior: more document reads, more validation steps, more chart QA, or more complete artifact generation.

## A/B Benchmark Protocol

Use two chart tasks with similar difficulty and run each condition at least three times.

Recommended conditions:

- Agent-file condition: prompt Codex to use `visual_library/agent.md` as the only workflow context.
- Skill condition: prompt Codex to use `visual-chart-builder`.

Use the same starting branch or a clean copy of the chart folder for each run.

Record these fields manually for now:

| Field | Notes |
| --- | --- |
| condition | `agent_file` or `skill` |
| chart_type | chart folder being built or refined |
| start_time | wall-clock start |
| first_edit_time | when the first file edit happens |
| first_render_time | when first PNG outputs are generated |
| finish_time | when Codex says the work is done |
| tool_calls | approximate count from the transcript |
| files_changed | from `git status --short` |
| r_runtime_seconds | time spent in the chart runner |
| rendered_png_count | number of review outputs generated |
| pass_fail | whether the result met the requested scope |
| notes | blockers, unexpected errors, extra review loops |

## Suggested Prompts

Agent-file condition:

```text
Use visual_library/agent.md as the workflow context. Build/refine <chart_type> from its spec and question coverage, update shared prep/render functions as needed, build DuckDB-backed sample SQL, render review PNGs, and stop after the first complete render pass.
```

Skill condition:

```text
Use the visual-chart-builder skill. Build/refine <chart_type> from its spec and question coverage, update shared prep/render functions as needed, build DuckDB-backed sample SQL, render review PNGs, and stop after the first complete render pass.
```

The final clause matters. Without it, the skill workflow may continue deeper into QA and iteration, which is useful for quality but makes the wall-clock comparison unfair.

## Interpreting Results

If context payload is similar but the skill condition is slower, inspect:

- whether it read `sample_library.md` or standards more often
- whether it invoked supporting skills
- whether it ran broader R checks
- whether it inspected and revised PNGs more aggressively
- whether the chart itself had more missing infrastructure than prior examples

If the agent-file condition is faster but produces thinner artifacts, compare quality separately from speed:

- did it validate the contract?
- did it save one sample query per canonical question?
- did it render all expected PNGs?
- did it update shared functions instead of patching only the runner?
- did the result rerun cleanly?

## Practical Recommendation

For speed runs, ask for:

```text
Use visual-chart-builder, but do a lean first pass: read only the chart spec, question coverage, standards sections needed for this chart, and nearby pattern files. Stop after the first successful render set and summarize remaining QA items instead of iterating.
```

For production-quality chart work, keep the full skill workflow.
