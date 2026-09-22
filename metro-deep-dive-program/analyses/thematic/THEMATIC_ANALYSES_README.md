# Thematic Analyses

`thematic/` holds national, cross-theme research analyses and their reusable
market deep dives.

Each entry starts with an interesting national question, develops a broad
cross-metro narrative, and then provides a standard way to inspect that
question for any covered CBSA. The notebooks are internal research instruments:
they should be clear and narrative, but they do not need publication styling.

**Planning source:**
[THEMATIC_ANALYSES_PLAN.md](THEMATIC_ANALYSES_PLAN.md) is authoritative for
family scope, architecture, sequence, and readiness. The child specs are
provisional until their Epic 1 audits are complete.

## Notebook roles

Every entry is designed for three distinct notebook roles:

| Role | Owner | Purpose |
|---|---|---|
| National analysis | Thematic entry | Test and narrate the national claim |
| Parameterized market deep dive | Thematic entry | Apply standard local views to a selected CBSA |
| Actual market story | Issue folder | Select and combine the relevant findings for Richmond or another published market |

The first two are separate notebooks that share reviewed inputs and methods.
The third is not part of this folder.

## Status

All ten entries have documentation-only scaffolds. Their specs and build plans
are deliberately provisional. No notebook implementation is authorized by the
scaffold itself.

| Order | Entry | Initial readiness | Primary audit concern |
|---|---|---|---|
| T1 | [A1 AI Inversion](a1_ai_inversion/) | Advanced legacy work | Reconcile and split the existing analysis |
| T2 | [A6 Specialization Predicts Growth](a6_specialization_predicts_growth/) | Strong panel | Lag and sector-grain design |
| T3 | [A10 Polarization](a10_polarization/) | Partial | Match the claim to QWI/OEWS evidence |
| T4 | [A2 Building Lowers Prices](a2_building_lowers_prices/) | Strong inputs | Causal versus associational design |
| T5 | [A7 Who Is Squeezed](a7_who_is_squeezed/) | Strong inputs | Define who and which affordability concept |
| T6 | [A9 Converging or Diverging](a9_converging_or_diverging/) | Strong panel | Convergence definition and stable cohort |
| T7 | [A4 Remote Work Rewired](a4_remote_work_rewired/) | Partial | Historical workplace geography gap |
| T8 | [A5 How Many Downtowns](a5_how_many_downtowns/) | Partial static base | Center definition and typology |
| T9 | [A3 Moving Toward Harm](a3_moving_toward_harm/) | Strong mixed-vintage inputs | Hazard/growth alignment and causal restraint |
| T10 | [A8 Geography of Life Expectancy](a8_geography_of_life_expectancy/) | Moderate | Place-effect framing and geographic inference |

## Build rule

Every build plan begins with Epic 1: audit prior art, profile live inputs,
review the provisional claim and method, and revise the spec and plan. Only
then should implementation files be added.

The eventual entry shape is:

```text
<entry>/
├── README.md
├── THEMATIC_<ENTRY>_SPEC.md
├── THEMATIC_<ENTRY>_BUILD_PLAN.md
├── THEMATIC_<ENTRY>_NATIONAL_NOTEBOOK.py
├── THEMATIC_<ENTRY>_MARKET_NOTEBOOK.py
├── queries/
└── figures/
    ├── national/
    └── market/<cbsa_code>/
```

The national notebook establishes the claim and findings. The market notebook
uses a searchable CBSA selector and shows the selected market’s position,
components, comparisons, and appropriate sub-CBSA evidence. Both must support
an inconclusive or no-distinctive-finding result.

## Family boundary

- The ten A-entries are the Thematic family.
- The Housing satellite is supporting work for Q1, A2, and A7, not a separate
  entry.
- The CBSA similarity study is an Intelligence/Position methods study, not a
  Thematic entry.
- Final market synthesis and presentation belong in `issues/`.

## What not to do here

- do not build the actual Richmond issue notebook here
- do not force national and market reasoning into one mode-switched notebook
- do not create a generic theme engine before reuse establishes a stable
  interface
- do not restyle exploratory visuals for publication
- do not claim causation, commuting flows, or historical change from inputs
  that support only association, stock, or one-year evidence

