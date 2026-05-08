# Visual Design Standards

## Purpose

This document defines the visual identity rules for Patterns in Place. Every chart, map, dashboard, header image, and Streamlit deployment carries this identity. Visual consistency is one of the most under-rated credibility signals in data publishing — readers recognize a Patterns in Place chart in a forwarded screenshot, in a slide deck excerpt, in a newsletter quote.

If you're about to make a chart, a map, or a tool deployment, read this document first.

---

## Why This Standard Exists

The publication's analytical credibility depends on the visual layer behaving consistently. Three things go wrong without a standard:

1. **Pieces look amateur.** Default Matplotlib or Streamlit theming under the Patterns in Place masthead actively damages the brand.
2. **Pieces look inconsistent.** A Sun Belt comparison from January doesn't match a Sun Belt comparison from June, even though both are "Patterns in Place."
3. **Cross-platform recognition fails.** A chart screenshot forwarded into a Slack channel doesn't trigger "oh, that's Patterns in Place" recognition.

This standard is the publication's visual operating manual. The visual library piece (Move 7 in `../publication_playbook.md`) is the public version of this doc.

---

## The Visual Identity at a Glance

Patterns in Place visuals are:

- **Newsprint-inspired** — calm, off-white backgrounds; warm neutral accents; one strong accent color
- **Type-led** — typography does as much work as the chart itself; clear hierarchy
- **Anchored** — every chart has one anchoring number or one anchoring trendline; readers' eyes land in one obvious place
- **Sourced** — every chart cites its source explicitly in a small footer
- **Recognizable** — the wordmark appears on every chart, every map, every tool

---

## Color System

### Core palette

| Token | Hex | Usage |
|---|---|---|
| Ink | `#0f0f0f` | Primary text, axis lines, anchor marks |
| Paper | `#f5f2eb` | Backgrounds (charts, page, exports) |
| Accent | `#c84b2f` | Primary accent (the one strong color) |
| Accent dim | `#e8d5cf` | Secondary accent (for de-emphasized series) |
| Rule | `#d4cfc4` | Gridlines, dividers |
| Mid | `#6b6660` | Secondary text, captions, source citations |
| Tag | `#e8e4db` | Tag and label backgrounds |

### Color rules

1. **One accent color per chart.** The accent (`#c84b2f`) marks the focal series, the focal point, the call-out. Everything else is in neutrals.
2. **Background is always Paper.** Never pure white, never gray. Paper is the publication's surface.
3. **Text is always Ink or Mid.** Pure black is never used; Ink is slightly softened.
4. **Gridlines are Rule.** Subtle, never competing with the data.
5. **Categorical palettes** (when more than one series matters) extend from the accent into a sequential or diverging scale — never use rainbow palettes, never use default Matplotlib categorical sets.

### Accessibility

- Accent on Paper meets WCAG AA contrast for text and large graphics
- Don't rely on color alone for distinction in categorical charts — use shape, position, or labeling as a backup
- Maps with sequential color ramps must have at least 5 visually distinct steps and a legend

---

## Typography

### Typefaces

| Role | Typeface | Notes |
|---|---|---|
| Display (headlines, chart titles) | Playfair Display (serif, 700 italic for emphasis) | Used at large sizes only |
| Body (long-form prose, captions) | IBM Plex Sans (sans-serif, 300/400) | The default reading face |
| Mono (data, labels, source citations) | IBM Plex Mono (mono, 400/500) | Used for chart labels, tags, axis ticks |

All three are open-source and Google-Fonts-hosted. No paid fonts in v1.

### Hierarchy rules

- **Headlines** in Playfair Display, large
- **Subheads and chart titles** in IBM Plex Sans Medium, smaller
- **Body** in IBM Plex Sans Light, optimized for long reading
- **Chart labels and ticks** in IBM Plex Mono, small, low-emphasis
- **Source citations** in IBM Plex Mono, very small, in Mid color

### Hierarchy violations to watch for

- Default Matplotlib labels (DejaVu Sans) — replace
- All-caps without letter-spacing — adjust
- Headlines in sans-serif — that's the body face; use Playfair Display
- Mixed weights within a single block — pick one weight per role and stick to it

---

## Chart Standards

### Every chart must include

1. **Title** — descriptive, sentence case, in Plex Sans Medium
2. **Subtitle** (if needed) — context or what to focus on, in Plex Sans Light
3. **Axis labels** with units (no "Y-axis: 0–500K" — say "Population, 2024")
4. **Source citation** in the footer — which dataset, which year, the URL or shortform attribution
5. **The Patterns in Place wordmark** in the bottom corner (subtle, not loud)
6. **One anchor** — a single highlighted data point, label, or annotation that tells the reader what to focus on

### Chart types — when to use each

| Chart type | Use for |
|---|---|
| Line chart | Time series; one or two series at most |
| Small multiples | Comparing the same metric across many places |
| Bar chart (horizontal) | Rankings of 5–15 items |
| Dot plot | Comparing one metric across many places at one point in time |
| Scatter plot | Two-dimensional comparison; always with quadrants labeled or callouts |
| Choropleth map | Geographic distributions; always with a clear legend and a clean projection |
| Stacked area | Composition over time; sparingly |
| Pie chart | Almost never |

### Chart types to avoid

- Pie charts (use stacked bars or a labeled callout)
- 3D bar or 3D pie (never)
- Dual-axis charts (almost never; if you need them, the piece is asking the wrong question)
- Color-coded line charts with more than four series (use small multiples instead)

### Chart export sizes

- **Standard chart:** 1600px × 900px (16:9 aspect ratio); used for Medium and LinkedIn
- **Square chart:** 1200px × 1200px; used for LinkedIn carousels and Instagram
- **Tall chart:** 1200px × 1800px; used for vertical charts (rankings of 12+ items)
- **Map (full-width):** 1600px × 1100px; used for geographic visuals

All exports are PNG at 2x DPI for retina-quality on social.

---

## Map Standards

Maps deserve their own standards because they are the publication's most distinctive visual asset.

### Projection

- **National maps:** Albers Equal Area, conic
- **Metro/CBSA maps:** Web Mercator at the metro level (close enough at metro scale that the projection distortion doesn't matter)
- **Tract maps:** Web Mercator
- **State and regional maps:** Albers Equal Area

### Color ramps

- **Sequential:** white-to-Accent ramp for single-variable choropleths
- **Diverging:** Accent-to-Mid-to-blue-toned-neutral for variables with a meaningful midpoint (e.g., year-over-year change with positive and negative values)
- **Categorical:** discrete categorical palette derived from the core palette, used only when the categories are truly nominal

### Map elements

- **Always include:** title, subtitle (if needed), legend, source citation, North arrow (for state and regional maps; optional at metro/tract scale), scale bar (when distance matters)
- **Never include:** unnecessary basemap detail (no Google Maps street labels under a choropleth), hard rainbow palettes, watermarks other than the Patterns in Place wordmark

### Basemaps

- For tract and metro maps, use a minimal basemap (e.g., CARTO Positron at low opacity, or a custom Patterns in Place basemap derived from TIGER lines)
- Don't use OpenStreetMap default tiles (too busy)
- Don't use satellite imagery as a basemap (distracting and rarely helps the analysis)

---

## Dashboard and Streamlit Standards

Tools deployed under Patterns in Place follow the same visual rules, with extensions for interactive surfaces.

### Header

- Wordmark in the top-left
- Tool name in Playfair Display, smaller than the wordmark
- One-line subtitle in Plex Sans Light explaining what the tool does
- Color: Ink on Paper background

### Layout

- Maximum width: 1200px content area
- Left rail (when present) for filters and controls in Plex Sans Light
- Right rail (when present) for context and source citations in Plex Mono small
- Generous whitespace; never crowd controls

### Controls

- Buttons in Accent (`#c84b2f`) for primary actions, Mid for secondary
- Inputs in Paper background with Rule borders
- Hover states use Accent dim (`#e8d5cf`)

### Footer

- Source citations in Plex Mono, Mid color
- "Built by Patterns in Place" with a link to the publication
- Last-updated timestamp

### Mobile

- Every tool must function on a 375px-wide viewport
- Filters collapse into a top drawer on mobile
- Charts re-render at narrower widths; never rely on horizontal scrolling

---

## Wordmark and Logo

The wordmark is the publication's signature mark. It appears on every chart, every map, every tool, every Medium piece header.

### Wordmark variations

- **Full wordmark:** "Patterns in Place" in Playfair Display, with "in" italicized in Accent
- **Compact wordmark:** "Patterns in Place" in Plex Sans Medium, single color (Ink or Paper depending on background)
- **Mark only:** the geometric "PiP" monogram (to be designed) for very small applications (favicons, social profile circles)

### Wordmark usage rules

- Always set on Paper or Ink background; never on a busy or competing surface
- Minimum size: 80px wide for the full wordmark; 40px for the compact wordmark
- Clear space: at least the height of the "P" on all sides
- Never stretch, recolor outside the palette, rotate, or animate

---

## Export Naming Conventions

Visual exports get filenamed consistently so they're discoverable later.

`<piece-slug>_<chart-type>_<sequence>.png`

Examples:
- `jacksonville-deep-dive_population-trend_01.png`
- `overheating-index-launch_score-distribution_01.png`
- `florida-parcel-tool_screenshot_01.png`

Save originals (the source files: Datawrapper exports, Quarto outputs, Figma frames) in a parallel `originals/` folder per piece.

---

## Visual Anti-Patterns

Things that will degrade the visual identity over time:

1. **Default chart styling.** Default Matplotlib, default ggplot, default Streamlit, default Datawrapper — none are acceptable as final output.
2. **Stock photos.** Never. Every header image is a chart, a map, or a wordmark composition.
3. **Inconsistent fonts.** A piece that uses DejaVu Sans in one chart and Plex Sans in another reads as careless.
4. **Inconsistent color.** Two different shades of orange across two charts in the same piece reads as careless.
5. **Loud annotations.** Annotations in Accent should be the *anchor* of the chart, not background noise. One anchor per chart.
6. **Watermarks beyond the wordmark.** No "© 2026 Patterns in Place" plastered across a chart. The wordmark is the watermark.
7. **Dashboards that look different from the publication.** A Streamlit tool with default theming undoes the credibility of the Medium piece that links to it.

---

## Visual Library — What Exists Today

The visual library currently exists as drafted style tokens and chart templates. To formalize:

- [ ] CSS variable token file (`tokens.css`) committed to the public `visual-library` repo
- [ ] Quarto theme that applies the standards to all Quarto-rendered notebooks
- [ ] Streamlit theme (`config.toml`) that applies the standards to all deployed tools
- [ ] Datawrapper template applied as the default for all new charts
- [ ] Figma file with the wordmark, chart frames, and example layouts
- [ ] Public repository at `github.com/PatternsInPlace/visual-library` with all of the above

The visual library piece (Move 7) is what publicly explains this system; the public repo is what makes it reproducible.

---

## Visual Library — Future Additions

- **Animated chart standards** — when (if) the publication starts producing motion content for social
- **Print export standards** — for any future newsletter PDF, conference handout, or printed material
- **Accessibility audit checklist** — every piece passes a quick accessibility review before publishing
- **Sound and video standards** — only if podcast or video content launches

These are illustrative, not committed.

---

## How This Doc Sits Alongside the Others

- `../publication_playbook.md` — operational setup; references this doc as the visual identity layer
- `../editorial_strategy.md` — defines what to publish; this doc defines how it looks
- `../distribution_strategy.md` — defines where pieces go; the visual identity travels with each piece across platforms
- `../asset_inventory.md` — the visual library is itself a Layer A infrastructure asset
- `editorial_pillars.md` — what each piece is about
- `format_standards.md` — the structure; this doc defines the surface
- `data_pipeline_standards.md` — the data; this doc renders it
- `visual_design_standards.md` — *this doc.* The recognizable surface.

When in doubt about a visual choice, the order is: this doc → check the visual library repo → mimic the closest published piece.

The single most important discipline this doc enforces is *no piece ships without the visual identity applied*. A piece in default Matplotlib styling is a draft, not a piece.
