# NY Regions Spec

**Status:** Active
**Updated:** 2026-10-18

How the NY State of Mind series divides the state: the 10 official REDC regions, and three nested definitions of Downstate. The data lives in one seed, `foundations/etl/reference/ny_county_regions.csv` (62 rows, one per county). Articles can link to this doc or quote it, and the debate over where "upstate" starts draws on it.

---

## REDC regions

The series' base regional definition (D1). Each of the 10 Regional Economic Development Councils covers a fixed set of whole counties, published by Empire State Development at [regionalcouncils.ny.gov](https://regionalcouncils.ny.gov/). Checked against each region's page on 2026-10-18. The Capital Region page doesn't list its counties, so its last two (Saratoga, Washington) are assigned by elimination; every other region's list is quoted from its page.

| Region | Counties | 2024 population |
|---|---|---|
| New York City | Bronx, Kings, New York, Queens, Richmond | 8.48M |
| Long Island | Nassau, Suffolk | 2.92M |
| Mid-Hudson | Dutchess, Orange, Putnam, Rockland, Sullivan, Ulster, Westchester | 2.41M |
| Western New York | Allegany, Cattaraugus, Chautauqua, Erie, Niagara | 1.41M |
| Finger Lakes | Genesee, Livingston, Monroe, Ontario, Orleans, Seneca, Wayne, Wyoming, Yates | 1.21M |
| Capital Region | Albany, Columbia, Greene, Rensselaer, Saratoga, Schenectady, Warren, Washington | 1.11M |
| Central New York | Cayuga, Cortland, Madison, Onondaga, Oswego | 0.78M |
| Southern Tier | Broome, Chemung, Chenango, Delaware, Schuyler, Steuben, Tioga, Tompkins | 0.63M |
| Mohawk Valley | Fulton, Herkimer, Montgomery, Oneida, Otsego, Schoharie | 0.48M |
| North Country | Clinton, Essex, Franklin, Hamilton, Jefferson, Lewis, St. Lawrence | 0.42M |

Population is ACS 2020–24 5-year, summed from counties (NY total 19.85M).

**Where REDC and common usage disagree** (for the text, not the map): Rochester sits in the Finger Lakes region, though it's often called Western New York. Delaware County is in the Southern Tier region, though it's usually thought of as Catskills. Sullivan and Ulster are in Mid-Hudson, which most people would not call Downstate.

---

## Downstate definitions

"Downstate" has no official boundary. The series keeps three definitions, each a boolean column in the seed. Each one contains the one before it.

| Definition | Counties | Adds | 2024 population | Share of NY |
|---|---|---|---|---|
| `downstate_core` | 10 | NYC (5), Nassau, Suffolk, Westchester, Rockland, Putnam | 12.84M | 64.7% |
| `downstate_mta` | 12 | Orange, Dutchess | 13.55M | 68.2% |
| `downstate_redc` | 14 | Ulster, Sullivan | 13.81M | 69.6% |

### `downstate_core` (10 counties)

**Reasoning.** This is the NY part of the New York-Newark-Jersey City metro under the 2023 CBSA delineations, so it's the federal statistical definition of the city's commuting core. It also matches the everyday meaning: the city, Long Island and the inner suburbs.

**Leaves out.** Orange and Dutchess, which have strong rail commuting ties to the city but form their own metro (Kiryas Joel-Poughkeepsie-Newburgh) since 2023.

**Used in.** The default for the "How New York Stacks Up" benchmark, and the dashed Downstate line on Map 1.

### `downstate_mta` (12 counties)

**Reasoning.** The 12 counties of the MTA's service district: the core plus Orange and Dutchess, served by Metro-North's Port Jervis and Hudson/Harlem lines. It's the NYC-funded transit shed, and it adds exactly the Kiryas Joel-Poughkeepsie-Newburgh metro, so it is also "the NYC metro plus its closest neighbor metro."

**Leaves out.** Ulster and Sullivan, which have no MTA commuter rail.

**Used in.** The alternative benchmark run and the Carto version of Map 1.

### `downstate_redc` (14 counties)

**Reasoning.** The three southernmost REDC regions: New York City, Long Island and Mid-Hudson. It's the only definition built from official state regions, so it lines up with the REDC map.

**Leaves out.** Nothing in the Hudson Valley south of the Capital Region. It includes Ulster and Sullivan, which are Catskills counties most people would call upstate, so it's the most generous line.

**Used in.** The alternative benchmark run and the Carto version of Map 1.

### Where "upstate" starts

The three lines are the ends of an argument the articles can make. On the narrow reading, upstate starts at the northern edge of Westchester, Rockland and Putnam. On the broad reading, it starts at the Capital Region. The population shares barely move (64.7% to 69.6%) because the counties in between are lightly populated, so the "two New Yorks" split holds under any of them.

---

## Seed

`foundations/etl/reference/ny_county_regions.csv`

| Column | Meaning |
|---|---|
| `county_geoid`, `county_name` | County identity, matching `geo.counties` |
| `redc_region` | One of the 10 REDC regions |
| `downstate_core`, `downstate_mta`, `downstate_redc` | `true` or `false` per definition |
| `source_url` | The region's ESD page |
| `as_of` | Date the assignment was checked |

**Checks** (run in `primer/series_intro/WHAT_NY_IS_VISUALS.py` through `check_seed`): 62 rows, each county once, matches the NY counties in `geo.counties`, 10 regions, 10 / 12 / 14 Downstate counties, and `core ⊂ mta ⊂ redc`.
