# Source Cooperative Application Draft

## Why do you want to publish your data on Source Cooperative?

Patterns in Place is publishing a small, versioned public dataset designed to be read directly
by data tools, especially DuckDB. Source Cooperative's public catalog and HTTP-accessible object
storage fit that use case: researchers and practitioners can query Parquet without a login or a
manual download, while the project retains clear documentation, versioning, and provenance. We
also value a data-focused public home rather than treating the files as incidental software
release attachments. Zenodo will preserve the citable archival version; Source Cooperative would
be the canonical, query-friendly distribution location.

## Brief description of dataset

Patterns in Place: Metro & Micro Panel is a county-first public panel for all current US
metropolitan and micropolitan statistical areas (CBSAs). The first release includes three files:
a static county-to-CBSA crosswalk and two annual CBSA-year tables covering 2012–2024. The
crosswalk uses the 2023 Office of Management and Budget delineation vintage and identifies each
member county, state, CBSA type, central or outlying role, and a deterministic primary state.

The economics table combines American Community Survey five-year employment-composition measures
with real GDP measures constructed from county-level Bureau of Economic Analysis inputs. The
affordability table combines ACS rent, home value, and household-income measures with
population-weighted county Fair Market Rents from the US Department of Housing and Urban
Development. Public CBSA values are created by applying the static crosswalk to governed county
inputs; the release does not simply republish a vendor's metro table.

Each version includes compressed Parquet files, a bundled DuckDB database, a machine-readable
manifest with hashes and field provenance, and a coverage report. The data are intended for
regional research, journalism, local policy analysis, and reproducible analysis of metro and
micro-area economic and housing conditions. The initial version excludes proprietary Zillow
data and documents source vintages, formulas, and source-specific missingness for every field.

## Size of dataset in GB

Approximately **0.004 GB** (about 4 MB) for v2026.1, including three Parquet files, one bundled
DuckDB file, manifest, and coverage report.

## Growth rate of dataset in GB per year

Approximately **0.001 GB or less per year**. The crosswalk is static within a release, and each
annual refresh adds one CBSA-year of observations for roughly 935 areas plus release metadata.

## Dataset file format(s)

Parquet (ZSTD-compressed), DuckDB, JSON manifest, Markdown documentation, and CSV field-lineage
ledger.

## Dataset license

Creative Commons Attribution 4.0 International (CC BY 4.0). The public build code is MIT
licensed. The release includes derived data from US federal sources and provides agency
attribution; source agencies do not endorse the release.

## How will this data be used?

The primary workflow is direct querying with DuckDB: a user can open a remote Parquet table,
filter to a year or CBSA, join county data through the crosswalk, and reproduce a chart or
analysis without maintaining a local database. Likely users include regional researchers,
journalists, planners, civic-data practitioners, and developers building analysis tools. Example
uses include comparing rent-to-income across micropolitan and metropolitan areas, aggregating a
county dataset to current CBSAs, and examining employment or GDP industry composition with its
published coverage constraints. It may also support teaching and lightweight data-app prototypes.

## What companies or institutions are already using this data?

None yet. This is the first public release of a previously private research and data-production
workflow. The dataset is being published specifically to invite independent use, feedback, and
reuse.
