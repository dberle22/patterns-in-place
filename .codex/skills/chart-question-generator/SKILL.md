---
name: chart-question-generator
description: Generate or refine backlog-ready Chart A Day questions for Publisher. Use when Codex needs to propose new question ideas, turn rough user ideas into valid `publisher/chart_a_day/backlog.yaml` entries, extend the queue after the current backlog is exhausted, or sanity-check that a proposed question matches the roadmap's template, geography, and chart-selection rules.
---

# Chart Question Generator

Read the current queue and roadmap before proposing anything. Work from the actual backlog contract, not memory.

## Load Context

- Read `publisher/chart_a_day/backlog.yaml` to find the current highest `q_id`, existing themes, and questions to avoid duplicating.
- Read `publisher/PUBLISHER_ROADMAP.md` for:
  - the backlog entry schema
  - valid `template_id` values
  - geo-level rules
  - chart-type expectations and `produce_alternatives` guidance
- Skim `publisher/chart_a_day/MANUAL_RUN_LOG.md` if you need to avoid overloading one fragile chart type or want to favor question shapes that helped parity review.
- If the user is giving you a rough idea, also read the nearest comparable existing question output under `publisher/chart_a_day/output/` when that will help you match tone or scope.

## Pick The Right Mode

Choose one of these modes based on the user request.

- `idea generation`: propose fresh questions and explain why they are worth adding.
- `queue formatting`: convert one or more user ideas into ready-to-paste YAML backlog entries.
- `hybrid`: propose a small set of options, then emit YAML for the strongest ones.
- `audit`: review a candidate question and call out schema problems, duplication risk, weak framing, or template mismatch.

## Generate Questions Deliberately

When inventing or refining questions:

- Prefer plain-language questions that sound like something a human editor would actually ask out loud.
- Make the story legible before making it clever. Avoid vague prompts like "What does housing look like in the Midwest?"
- Keep one clear analytical job per question: ranking, trend, benchmark, distribution, growth, map, correlation, composition, demographic, or rank change.
- Match `template_id` to the real shape of the expected answer. Do not pick `trend` for a one-year snapshot or `ranking` for a question that is really spatial.
- Keep `geo_level` honest: `cbsa`, `state`, `national`, or `county`.
- Reuse proven filters when they improve signal, such as population thresholds for CBSA rankings, but do not invent arbitrary caveats.
- Avoid near-duplicates of existing backlog entries unless the user explicitly wants a series or variant.
- Favor questions that fit Publisher's current content lane: housing, affordability, demographics, migration, economic mobility, regional divergence, and metro comparison.
- If the queue is light on a template or chart family, bias toward balanced coverage rather than generating five versions of the same ranking chart.

## Write Backlog Entries

Emit YAML that matches `publisher/chart_a_day/backlog.yaml` exactly.

Required fields:

- `id`
- `question`
- `template_id`
- `geo_level`
- `status`
- `platform`
- `produce_alternatives`
- `notes`
- `scheduled`
- `ran_at`
- `posted_at`

Follow these rules:

- Assign the next sequential `q_id` by reading the current backlog. Never reuse or skip silently.
- Default new backlog entries to `status: ready`.
- Default `platform` to `both` unless the user asks for a channel-specific question.
- Default `scheduled`, `ran_at`, and `posted_at` to `null`.
- Set `produce_alternatives: true` only when the roadmap's comparison logic says the fallback chart is genuinely informative.
- Use the `notes` field for concrete execution hints, not generic commentary. Good notes mention filters, named geographies, benchmark context, chart overrides, or known caveats.

Use this exact shape:

```yaml
- id: q029
  question: Which major metros have seen the fastest rent growth since 2019?
  template_id: growth
  geo_level: cbsa
  status: ready
  platform: both
  produce_alternatives: false
  notes: Filter to CBSAs with pop > 250k. Use inflation-adjusted rent growth if that metric is already available; otherwise state the nominal-growth caveat.
  scheduled: null
  ran_at: null
  posted_at: null
```

## Output By Mode

For `idea generation`:

- Start with 3 to 8 candidate questions.
- For each one, include the proposed `template_id`, `geo_level`, and one sentence on why it belongs in the queue now.
- If a candidate is risky because the needed metric may not exist, say so explicitly instead of hiding the uncertainty.

For `queue formatting`:

- Output only the final YAML block unless the user asked for explanation.
- Preserve the user's idea, but tighten wording so the question is specific and operational.
- Add practical notes that make the later SQL and chart steps easier.

For `hybrid`:

- Present a short candidate list first.
- Then emit a `Ready to paste into backlog.yaml` section with the chosen YAML entries.

For `audit`:

- Lead with concrete issues first: duplicate theme, weak template fit, invalid field value, poor notes, or sequencing problem.
- Then provide a corrected YAML version.

## Quality Bar

Before finalizing, check each proposed entry against this list:

- The question is distinct from existing backlog items.
- The `template_id` is one of the roadmap-approved values.
- The `geo_level` matches the wording of the question.
- The `notes` field would actually help the SQL or chart skill later.
- `produce_alternatives` matches the roadmap guidance instead of defaulting randomly.
- The entry is backlog-ready and does not require the user to repair field names or null handling by hand.

## Example Triggers

- "Use $chart-question-generator to give me 10 more Chart A Day ideas focused on housing affordability."
- "Take these three rough post ideas and format them into backlog entries."
- "We exhausted the current queue. Propose the next five questions with balanced chart coverage."
- "Review this draft backlog entry and fix anything that doesn't match the roadmap."
