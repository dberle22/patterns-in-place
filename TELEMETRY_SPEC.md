# AI Coding Benchmarking Framework

**Version:** 1.0  
**Owner:** Dan Berle  
**Project:** Patterns in Place

---

# Objective

Develop a repeatable benchmarking framework to measure the productivity, cost, and quality of AI coding assistants used during software development.

Initial focus:

- OpenAI Codex
- Claude Code

The framework should answer:

1. Which model produces the highest quality output?
2. Which model completes tasks the fastest?
3. Which model requires the fewest follow-up prompts?
4. Which model uses the fewest tokens?
5. What is the effective cost per completed engineering task?
6. Which workflow scales best over time?

---

# Success Metrics

Primary KPIs

- Time to completion
- Successful task completion rate
- Tokens consumed
- Cost
- Human edits required
- Number of prompts
- Tests passing
- Overall quality score

Secondary KPIs

- LOC added
- LOC removed
- Files modified
- Context window utilization
- Cache hit rate (when available)

---

# Benchmark Task Library

Every benchmark should come from a standardized library of engineering tasks.

Example tasks:

## Architecture

- Explain project architecture
- Explain data flow
- Identify dependencies

## Feature Development

- Implement small feature
- Extend existing component
- Add configuration option

## Refactoring

- Simplify module
- Improve readability
- Remove duplicate code

## Testing

- Add unit tests
- Increase coverage
- Fix failing tests

## Debugging

- Fix known bug
- Explain stack trace
- Diagnose failing test

## Documentation

- Generate README updates
- Create API documentation
- Explain module behavior

---

# Benchmark Dataset

Each benchmark run should capture the following metadata.

| Field | Description |
|---------|-------------|
| Date | Benchmark date |
| Tool | Codex / Claude Code |
| Model | Model name |
| Task ID | Unique benchmark identifier |
| Task Category | Debug / Feature / Tests / Docs |
| Prompt Version | Prompt revision |
| Repository | Project name |
| Branch | Git branch |
| Commit | Starting commit SHA |

---

# Execution Metrics

| Field |
|--------|
| Start Time |
| End Time |
| Wall Clock Minutes |
| Number of Prompts |
| Number of Responses |
| Files Modified |
| Lines Added |
| Lines Removed |

---

# Token Metrics

Whenever available:

| Field |
|--------|
| Input Tokens |
| Cached Tokens |
| Output Tokens |
| Reasoning Tokens |
| Total Tokens |
| Estimated Cost |

---

# Quality Metrics

After completion, manually evaluate:

| Metric | Scale |
|---------|-------|
| Correctness | 1-5 |
| Code Quality | 1-5 |
| Readability | 1-5 |
| Required Human Edits | 1-5 |
| Overall Confidence | 1-5 |

Additional binary fields:

- Tests Passed
- Linter Passed
- Build Passed
- Shippable Without Modification

---

# Productivity Metrics

Derived metrics:

```
Minutes per Task

= Wall Minutes
```

```
Tokens per Task

= Total Tokens
```

```
Cost per Task

= Estimated Cost
```

```
Prompts per Task

= Number of Prompts
```

```
Manual Edit Ratio

= Human Edit Minutes / Total Minutes
```

```
Acceptance Rate

= Shippable Tasks / Total Tasks
```

```
Cost per Successful Task

= Total Cost / Successful Tasks
```

---

# Data Collection

## Codex

Preferred methods:

- `/status`
- `codex exec --json`

Capture:

- usage
- cached tokens
- reasoning tokens
- input/output tokens

Store raw JSON alongside benchmark results.

---

## Claude Code

Preferred methods:

```
claude -p "<prompt>" --output-format json
```

or

```
stream-json
```

Capture:

- usage
- estimated cost
- token counts
- session metadata

Store raw JSON alongside benchmark results.

---

# Repository Structure

```
benchmarks/

    benchmark_results.csv

    benchmark_results.parquet

    raw/

        codex/

        claude/

    prompts/

    reports/

    notebooks/

```

---

# Analysis

Generate periodic reports comparing:

- Average completion time
- Average cost
- Average prompt count
- Average quality score
- Average manual edits
- Average tokens
- Success rate

Visualizations:

- Tokens vs Quality
- Cost vs Time
- Time vs Quality
- Tool Comparison
- Quality Distribution
- Prompt Count Distribution

---

# Dashboard (Future)

Potential dashboard views:

## Executive Summary

- Tasks Completed
- Total Cost
- Average Time
- Average Quality
- Success Rate

## Tool Comparison

| Metric | Codex | Claude |
|---------|--------|---------|
| Avg Time | | |
| Avg Tokens | | |
| Avg Cost | | |
| Avg Quality | | |
| Avg Prompts | | |

## Trend Analysis

- Weekly productivity
- Monthly productivity
- Cost over time
- Quality over time

---

# Future Enhancements

- Automatic benchmark execution
- Git integration
- VSCode extension
- OpenTelemetry ingestion
- SQLite or DuckDB backend
- Grafana dashboards
- Prompt versioning
- Multi-model benchmarking (GPT, Gemini, etc.)
- A/B testing for prompt engineering

---

# Long-Term Goal

Create a reproducible AI engineering benchmark that evaluates coding assistants using objective measures of:

- Speed
- Cost
- Accuracy
- Code quality
- Developer effort

The framework should support continuous benchmarking across projects and provide historical performance trends as models improve.