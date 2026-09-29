# What each frame answers

**Status:** Active
**Updated:** 2026-09-29

The questions each Intelligence frame is meant to answer, from high-level ("is this a good place to live?") down to direct metric lookups. They come from the frame notes written in June 2026, before calibration, and are kept here as the question-side view of the frames. The actual KPIs and models are in `foundations/semantic_layer/intelligence_catalog.yml`; how they were built is in [intelligence_framework_overview.md](intelligence_framework_overview.md).

The levels follow the question hierarchy in [docs/OVERVIEW.md](../../OVERVIEW.md#how-we-think-about-a-question).

---

## Character

Character captures who lives in a place, what it feels like to be there, and what makes it distinct. It is not one of these alone — demographic reality, cultural expression, and differentiation are all part of it. A place's Character is the combination of the people who live there, the life they've built, and what sets it apart from everywhere else.

### High-level
- What kind of place is this?
- What is the cultural identity of this neighborhood / city?
- How does this place compare to others like it?

### Mid-level
- Who lives here — age, race, education profile?
- How diverse is this place, and in what dimensions?
- How rooted vs. transient is the population?
- What does the cultural and commercial life look like (restaurants, arts, nightlife, retail)?
- Is this a college town, an immigrant community, a creative hub, a family suburb?

### Low-level
- What is the median age?
- What is the diversity index?
- What share of residents were born outside the US?
- What share of residents have a college degree?
- What is the restaurant / bar / cultural venue density per capita?
- What is the 5-year population change and net migration rate?

---

## Livability

Livability captures quality of life — the full picture of what living in a place is actually like day to day. It goes beyond affordability alone to include transit, health, safety, schools, and the built environment. A high-livability place is one where basic needs are met, daily life is functional, and the environment supports wellbeing.

### High-level
- Is this a good place to live?
- Does this place support a good quality of life?
- Where would I get the most for my money as a resident?

### Mid-level
- Can the average person afford to live here?
- How easy is it to get around without a car?
- How healthy is the population, and how accessible is healthcare?
- How good are the schools?
- Is this a safe place to live?

### Low-level
- What is the rent-to-income ratio?
- What share of renters are cost-burdened?
- What is the transit commute share?
- What is the average commute time?
- What is the county-level life expectancy?
- What is the uninsured rate?
- What is the violent crime rate per 100k?
- What share of adults have some college or more?

---

## Opportunity

Opportunity captures the economic prospects of a place — for residents building a career, for investors evaluating a market, and for businesses considering where to locate or expand. All three lenses matter and are related: a strong resident labor market and a strong investment market tend to move together, but they diverge in interesting ways that are worth surfacing separately.

### High-level
- Is this a good place to build a career?
- Is this a good market to invest in?
- Is this a good place to open or grow a business?

### Mid-level (Resident lens)
- Are wages growing here?
- Is unemployment low and the labor market tight?
- What industries are dominant — and are they growing or contracting?
- Is this a good market for someone early in their career vs. later?

### Mid-level (Investor / market lens)
- Is this market appreciating faster than peers?
- Where are home values undervalued relative to income and growth?
- Which markets have the most economic momentum?
- Are Opportunity Zones here active and investable?

### Mid-level (Business lens)
- Is there a strong labor pool?
- Is the economy diversified or concentrated in one sector?
- Is the market growing in population and purchasing power?

### Low-level
- What is the unemployment rate and trend?
- What is the median wage and 5-year wage growth?
- What is the GDP growth rate?
- What is the industry concentration (HHI or top-sector share)?
- What is the per capita income growth over 5 years?
- What is the home value appreciation rate (FHFA HPI)?
- Are there federally designated Opportunity Zones in this tract?
