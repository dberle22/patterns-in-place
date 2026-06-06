# Decision Log — State Vacancy Map

**Insight:** `analysis/vacancy_rates/state_map/`  
**Created:** `2026-05-26`  
**Purpose:** Record the main decisions behind the state vacancy map, what worked,
and what we should improve in future map builds.

---

## Final Editorial Framing

- Primary story: `2024` state vacancy rate is the anchor metric.
- Supporting context: keep `2019` vacancy rate and `2019-2024` percentage-point
  change in the query so the same extract can support follow-on maps.
- Headline framing: low vacancy is interpreted as low housing slack, so darker
  states should represent tighter supply conditions.

## Data Decisions

- Geography scope: use the contiguous `48` states plus `DC`.
- Exclusions: `Alaska`, `Hawaii`, and `Puerto Rico` are excluded from the final
  map footprint.
- Source label in chart footer: simplify to `ACS`.
- Vintage label in chart footer: simplify to `2024`.
- Query output: include map-ready `metric_value` plus helper columns for:
  `vacancy_rate_2019_pct`, `vacancy_rate_2024_pct`, and
  `vacancy_rate_change_pp`.
- Geometry source: join state geometries from `geo.states` as WKT for the
  choropleth renderer.

## EDA Decisions

- Preserve exploration in `eda.sql` because this insight required meaningful
  ranking, distribution, and change checks before final SQL.
- Key EDA finding: the tightest states in `2024` and the states with the
  biggest `2019-2024` declines are related but not the same story.
- Editorial implication: the final map should focus on `2024` levels, while the
  change metric remains available for a separate map rather than being forced
  into the main visual.

## Visual Decisions

- Chart type: single-panel choropleth.
- Composition: contiguous-US national map.
- Scale choice: use a continuous scale rather than bins.
- Palette choice: use a single-hue sequential palette.
- Direction choice: darker fill means lower vacancy, so the most supply-tight
  states carry the strongest visual emphasis.
- Scale handling: cap display values above `17.5%` so a few high-vacancy
  outliers do not flatten the rest of the color range.
- Annotation choice: show `Tightest` and `Loosest` top-5 lists as lightweight
  callout boxes rather than labeling state values directly on the map.
- Footer choice: keep only source, vintage, and a very short interpretive/data
  note.

## What Worked Well

- Anchoring the map on `2024` vacancy rate made the story much clearer than
  trying to combine current levels and change in one visual.
- Keeping `2019` and `2019-2024` change in the query was still valuable because
  it preserved optional follow-on views without complicating the final chart.
- The move from binned fill to continuous fill improved the map immediately.
- The move from red-blue to a single-hue sequential palette made the chart feel
  more descriptive and less rhetorically loaded.
- Reversing the scale so darker means tighter supply aligned the visual with the
  thesis of the post.
- Simplifying the footer materially improved readability.

## What Did Not Work Well

- Binned choropleth styling felt too coarse for this story.
- Red-blue diverging color created unnecessary “good vs bad” interpretation
  baggage for a chart that is really about intensity.
- A hard cap at `15%` compressed the high end too much; `17.5%` worked better.
- Directly labeling state values on the map created clutter, especially in the
  Northeast.
- Attempting to align annotation boxes precisely with the legend using a shared
  side-column layout introduced renderer complexity and did not land cleanly in
  this pass.

## Renderer / Workflow Learnings

- The choropleth renderer needed a custom continuous palette hook because the
  default continuous path was too rigid.
- The renderer also needed support for lightweight annotation blocks.
- There was a regression where map annotations were accidentally disabled when
  `patchwork` was installed. That was fixed.
- The attempted `patchwork` side-panel refactor for legend + annotation
  alignment is incomplete and should be treated as exploratory rather than
  production-ready.

## Suggested Improvements Next Time

- Build a more durable chart-side annotation system using `grid`/`gtable` if we
  want exact alignment between legends and side notes.
- Add a dedicated config pattern for “top/bottom callout lists” so this does
  not require ad hoc chart-local experimentation.
- Consider a shorter footer standard for analysis charts:
  `Source | Vintage | one short note`.
- If we build the companion change map, use the existing query output rather
  than rewriting the extraction logic.
- If we expect repeated manual EDA in this workflow, keep `eda.sql` as a normal
  artifact for non-trivial insights.

## Final Recommendation

- Reuse this map pattern when the story is about the current geographic level of
  a metric.
- Prefer a separate second map or companion chart when the change story is
  analytically important but visually distinct from the level story.
