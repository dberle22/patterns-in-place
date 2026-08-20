import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    # Marimo's native table UI keeps filtering, sorting, and download behavior intact.
    # The Jupyter-style Styler/display path tends to turn tables into static HTML instead.
    def table(
        data,
        *,
        format_mapping=None,
        page_size=10,
        pagination=None,
        label="",
        show_search=True,
        show_download=True,
        **kwargs,
    ):
        if pagination is None:
            try:
                pagination = len(data) > page_size
            except TypeError:
                pagination = True

        return mo.ui.table(
            data,
            format_mapping=format_mapping,
            page_size=page_size,
            pagination=pagination,
            selection=None,
            label=label,
            show_search=show_search,
            show_download=show_download,
            **kwargs,
        )

    def dataframe(
        data,
        *,
        format_mapping=None,
        page_size=10,
        label="",
        show_download=True,
        **kwargs,
    ):
        viewer = mo.ui.dataframe(
            data,
            page_size=page_size,
            show_download=show_download,
            format_mapping=format_mapping,
            **kwargs,
        )
        items = [viewer]
        if label:
            items = [mo.md(f"**{label}**"), viewer]
        return mo.vstack(items)

    return dataframe, table


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # AI Inversion

    This notebook is now the analysis hub for A1. The SOC and NAICS crosswalk construction lives upstream in `soc_crosswalk_rebuild.ipynb` and `naics_crosswalk_rebuild.ipynb`; this file starts from those cleaned outputs and the governed metro employment surfaces.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Notebook Structure

    - Load the cleaned SOC and NAICS Felten join tables.
    - Load the governed CBSA surfaces we need for analysis.
    - Build metro-level SOC and NAICS exposure tables.
    - Start Part 1 of the analysis plan with the descriptive baseline.

    Important source note: `gold` gives us the metro-wide comparison panel we will use later for industry mix, education, and broad occupation context. The detailed SOC and 4-digit NAICS rows still come from the governed BLS layers because Gold does not currently ship detailed code-level surfaces at the grain this analysis needs.
    """)
    return


@app.cell(hide_code=True)
def notebook_setup():
    # Core notebook setup. Keep all paths repo-relative so this notebook can run cleanly
    # across local environments without hardcoded machine-specific references.
    from pathlib import Path

    import duckdb
    import numpy as np
    import pandas as pd
    pd.set_option("display.max_columns", 200)
    pd.set_option("display.max_rows", 200)
    pd.set_option("display.width", 160)

    REPO_ROOT = Path.cwd()
    if not (REPO_ROOT / "foundations").exists():
        for parent in REPO_ROOT.parents:
            if (parent / "foundations").exists():
                REPO_ROOT = parent
                break

    ANALYSIS_ROOT = REPO_ROOT / "metro-deep-dive" / "analysis_program" / "01_ai_inversion"
    OUTPUT_ROOT = ANALYSIS_ROOT / "outputs"
    DB_PATH = REPO_ROOT / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"

    SOC_CROSSWALK_PATH = OUTPUT_ROOT / "soc_felten_join_reference.csv"
    NAICS_CROSSWALK_PATH = OUTPUT_ROOT / "naics_felten_join_reference.csv"

    RICHMOND_CBSA_CODE = "40060"

    pd.DataFrame([
        {"path": "DuckDB", "value": DB_PATH.relative_to(REPO_ROOT)},
        {"path": "Analysis root", "value": ANALYSIS_ROOT.relative_to(REPO_ROOT)},
        {"path": "SOC crosswalk", "value": SOC_CROSSWALK_PATH.relative_to(REPO_ROOT)},
        {"path": "NAICS crosswalk", "value": NAICS_CROSSWALK_PATH.relative_to(REPO_ROOT)},
    ])
    return (
        DB_PATH,
        NAICS_CROSSWALK_PATH,
        RICHMOND_CBSA_CODE,
        SOC_CROSSWALK_PATH,
        duckdb,
        np,
        pd,
    )


@app.cell(hide_code=True)
def part_1(mo):
    mo.md(r"""
    ## 1. Load The Cleaned Felten Crosswalks

    These are the canonical downstream join tables produced by the rebuild notebooks. The analysis notebook should treat them as fixed inputs rather than rebuilding the vintage reconciliation logic here.
    """)
    return


@app.cell(hide_code=True)
def felten_load(
    NAICS_CROSSWALK_PATH,
    SOC_CROSSWALK_PATH,
    dataframe,
    pd,
    table,
):
    # Read the cleaned SOC and NAICS Felten join tables that we will use throughout the analysis.
    # We coerce the score fields to numeric immediately so downstream exposure math is explicit.
    soc_felten_join_reference = pd.read_csv(SOC_CROSSWALK_PATH, dtype=str)
    soc_felten_join_reference["felten_score"] = pd.to_numeric(soc_felten_join_reference["felten_score"], errors="coerce")

    naics_felten_join_reference = pd.read_csv(NAICS_CROSSWALK_PATH, dtype=str)
    naics_felten_join_reference["felten_score"] = pd.to_numeric(naics_felten_join_reference["felten_score"], errors="coerce")

    crosswalk_summary = pd.DataFrame([
        {
            "surface": "SOC",
            "rows": len(soc_felten_join_reference),
            "rows_with_score": int(soc_felten_join_reference["felten_score"].notna().sum()),
            "missing_scores": int(soc_felten_join_reference["felten_score"].isna().sum()),
        },
        {
            "surface": "NAICS",
            "rows": len(naics_felten_join_reference),
            "rows_with_score": int(naics_felten_join_reference["felten_score"].notna().sum()),
            "missing_scores": int(naics_felten_join_reference["felten_score"].isna().sum()),
        },
    ])

    table(crosswalk_summary, page_size=5, pagination=False, label="Crosswalk coverage summary")
    dataframe(soc_felten_join_reference, page_size=10, label="SOC crosswalk")
    dataframe(naics_felten_join_reference, page_size=10, label="NAICS crosswalk")
    return naics_felten_join_reference, soc_felten_join_reference


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Load The Governed Metro Surfaces

    This block does two things.

    First, it loads the CBSA-level comparison panel from Gold that we will use later for the hypotheses in `analysis_program.md`. Second, it loads the detailed SOC and 4-digit NAICS employment surfaces that the exposure math actually runs on.
    """)
    return


@app.cell(hide_code=True)
def load_metro(DB_PATH, dataframe, duckdb, pd, table):
    # Gold holds the wide comparison panel for later analysis. The detailed code-level exposure work
    # still has to come from the governed BLS layers because Gold is intentionally rolled up.
    industry_wide_sql = """
    SELECT *
    FROM gold.economics_industry_wide
    WHERE geo_level = 'cbsa'
    ORDER BY geo_id, year
    """

    occupation_wide_sql = """
    SELECT *
    FROM gold.economics_occupation_wide
    WHERE geo_level = 'cbsa'
    ORDER BY geo_id, year
    """

    population_sql = """
    SELECT *
    FROM gold.population_demographics
    WHERE geo_level = 'cbsa'
    ORDER BY geo_id, year
    """

    soc_cbsa_sql = """
    WITH cbsa_totals AS (
        SELECT
            geo_id,
            geo_name,
            year,
            employment AS cbsa_total_employment
        FROM silver.bls_oews
        WHERE geo_level = 'cbsa'
          AND is_total_occupation
    ), detailed_rows AS (
        SELECT
            geo_id,
            geo_name,
            year,
            soc_code,
            soc_title,
            occupation_bucket,
            is_stem,
            employment,
            annual_mean_wage,
            location_quotient
        FROM silver.bls_oews
        WHERE geo_level = 'cbsa'
          AND o_group = 'detailed'
    )
    SELECT
        d.geo_id AS cbsa_code,
        d.geo_name AS cbsa_name,
        d.year,
        d.soc_code,
        d.soc_title,
        d.occupation_bucket,
        d.is_stem,
        d.employment,
        d.annual_mean_wage,
        d.location_quotient,
        t.cbsa_total_employment
    FROM detailed_rows d
    LEFT JOIN cbsa_totals t
      ON d.geo_id = t.geo_id
     AND d.year = t.year
    ORDER BY cbsa_code, year, employment DESC, soc_code
    """

    naics_cbsa_sql = """
    WITH detailed_rows AS (
        SELECT
            x.cbsa_code AS cbsa_code,
            x.cbsa_name AS cbsa_name,
            c.period AS year,
            c.industry_code AS naics_code,
            any_value(c.industry_title) AS naics_title,
            SUM(c.annual_avg_emplvl) AS employment
        FROM staging.bls_qcew_county c
        INNER JOIN silver.xwalk_cbsa_county x
            ON c.county_fips_code = x.county_fips
        INNER JOIN silver.bls_qcew_industry_map m
            ON c.industry_code = m.industry_code
        WHERE c.own_code = '5'
          AND m.code_type = 'naics_industry_group'
        GROUP BY 1, 2, 3, 4
    )
    SELECT
        cbsa_code,
        cbsa_name,
        year,
        naics_code,
        naics_title,
        employment,
        SUM(employment) OVER (PARTITION BY cbsa_code, year) AS cbsa_total_employment
    FROM detailed_rows
    ORDER BY cbsa_code, year, employment DESC, naics_code
    """

    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        industry_wide_cbsa = con.execute(industry_wide_sql).fetchdf()
        occupation_wide_cbsa = con.execute(occupation_wide_sql).fetchdf()
        population_cbsa = con.execute(population_sql).fetchdf()
        soc_cbsa_base = con.execute(soc_cbsa_sql).fetchdf()
        naics_cbsa_base = con.execute(naics_cbsa_sql).fetchdf()

    for _frame_name, _numeric_cols in {
        "soc_cbsa_base": ["employment", "annual_mean_wage", "location_quotient", "cbsa_total_employment"],
        "naics_cbsa_base": ["employment", "cbsa_total_employment"],
    }.items():
        _frame = locals()[_frame_name]
        for _col in _numeric_cols:
            _frame[_col] = pd.to_numeric(_frame[_col], errors="coerce")

    surface_summary = pd.DataFrame([
        {
            "surface": "gold.economics_industry_wide",
            "rows": len(industry_wide_cbsa),
            "cbsas": industry_wide_cbsa["geo_id"].nunique(),
            "year_min": int(industry_wide_cbsa["year"].min()),
            "year_max": int(industry_wide_cbsa["year"].max()),
        },
        {
            "surface": "gold.economics_occupation_wide",
            "rows": len(occupation_wide_cbsa),
            "cbsas": occupation_wide_cbsa["geo_id"].nunique(),
            "year_min": int(occupation_wide_cbsa["year"].min()),
            "year_max": int(occupation_wide_cbsa["year"].max()),
        },
        {
            "surface": "gold.population_demographics",
            "rows": len(population_cbsa),
            "cbsas": population_cbsa["geo_id"].nunique(),
            "year_min": int(population_cbsa["year"].min()),
            "year_max": int(population_cbsa["year"].max()),
        },
        {
            "surface": "Detailed SOC CBSA rows",
            "rows": len(soc_cbsa_base),
            "cbsas": soc_cbsa_base["cbsa_code"].nunique(),
            "year_min": int(soc_cbsa_base["year"].min()),
            "year_max": int(soc_cbsa_base["year"].max()),
        },
        {
            "surface": "Detailed NAICS CBSA rows",
            "rows": len(naics_cbsa_base),
            "cbsas": naics_cbsa_base["cbsa_code"].nunique(),
            "year_min": int(naics_cbsa_base["year"].min()),
            "year_max": int(naics_cbsa_base["year"].max()),
        },
    ])

    table(surface_summary, page_size=10, pagination=False, label="Governed surface summary")
    dataframe(soc_cbsa_base, page_size=10, label="Detailed SOC CBSA rows")
    dataframe(naics_cbsa_base, page_size=10, label="Detailed NAICS CBSA rows")
    return (
        industry_wide_cbsa,
        naics_cbsa_base,
        occupation_wide_cbsa,
        population_cbsa,
        soc_cbsa_base,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Build Metro Exposure Tables

    This is the first real analytical step. We join the cleaned Felten scores onto the governed metro code surfaces and compute the employment-weighted exposure measures we will use throughout the rest of the notebook.
    """)
    return


@app.cell(hide_code=True)
def build_metro_exposure(
    dataframe,
    naics_cbsa_base,
    naics_felten_join_reference,
    np,
    pd,
    soc_cbsa_base,
    soc_felten_join_reference,
    table,
):
    # Join the cleaned Felten scores onto the detailed SOC and NAICS CBSA surfaces, then compute
    # the metro-level exposure measures. We keep coverage stats alongside the index because low
    # coverage metros should be flagged before we interpret any ranking or comparison.
    soc_cbsa_scored = soc_cbsa_base.merge(
        soc_felten_join_reference[["our_soc_code", "felten_score"]].rename(columns={"our_soc_code": "soc_code"}),
        on="soc_code",
        how="left",
        validate="many_to_one",
    )
    soc_cbsa_scored["matched_flag"] = soc_cbsa_scored["felten_score"].notna()

    # The SOC inversion measure only lives on the published detailed-SOC surface. That means the
    # primary employment denominator for both `E_m` and the scored coverage stats has to be the sum
    # of detailed rows, not the OEWS all-occupation total. We keep the detailed-vs-total gap as a
    # separate QA field because it reflects OEWS publication coverage rather than Felten matching.
    soc_cbsa_scored["detailed_employment_share"] = soc_cbsa_scored.groupby(["cbsa_code", "year"])["employment"].transform(
        lambda values: values / values.sum()
    )
    soc_cbsa_scored["exposure_contribution"] = soc_cbsa_scored["detailed_employment_share"] * soc_cbsa_scored["felten_score"]
    soc_cbsa_scored["wage_bill"] = soc_cbsa_scored["employment"] * soc_cbsa_scored["annual_mean_wage"]
    soc_cbsa_scored["matched_wage_bill"] = np.where(soc_cbsa_scored["matched_flag"], soc_cbsa_scored["wage_bill"], np.nan)
    soc_cbsa_scored["wage_exposure_component"] = np.where(
        soc_cbsa_scored["matched_flag"],
        soc_cbsa_scored["wage_bill"] * soc_cbsa_scored["felten_score"],
        np.nan,
    )

    soc_metro_exposure = (
        soc_cbsa_scored.groupby(["cbsa_code", "cbsa_name", "year"], as_index=False)
        .agg(
            cbsa_total_employment=("cbsa_total_employment", "max"),
            cbsa_detailed_employment=("employment", "sum"),
            matched_employment=("employment", lambda values: float(values[soc_cbsa_scored.loc[values.index, "matched_flag"]].sum())),
            total_soc_rows=("soc_code", "count"),
            matched_soc_rows=("matched_flag", "sum"),
            e_m=("exposure_contribution", "sum"),
            cbsa_total_payroll=("wage_bill", "sum"),
            matched_payroll=("matched_wage_bill", "sum"),
            w_m_local_numerator=("wage_exposure_component", "sum"),
        )
    )
    soc_metro_exposure["coverage_share"] = soc_metro_exposure["matched_employment"] / soc_metro_exposure["cbsa_detailed_employment"]
    soc_metro_exposure["detailed_share_of_total_oe_ws"] = soc_metro_exposure["cbsa_detailed_employment"] / soc_metro_exposure["cbsa_total_employment"]
    soc_metro_exposure["payroll_coverage_share"] = soc_metro_exposure["matched_payroll"] / soc_metro_exposure["cbsa_total_payroll"]
    soc_metro_exposure["w_m_local"] = soc_metro_exposure["w_m_local_numerator"] / soc_metro_exposure["matched_payroll"]

    naics_cbsa_scored = naics_cbsa_base.merge(
        naics_felten_join_reference[["our_naics_code", "felten_score"]].rename(columns={"our_naics_code": "naics_code"}),
        on="naics_code",
        how="left",
        validate="many_to_one",
    )
    naics_cbsa_scored["matched_flag"] = naics_cbsa_scored["felten_score"].notna()
    naics_cbsa_scored["employment_share_total"] = naics_cbsa_scored["employment"] / naics_cbsa_scored["cbsa_total_employment"]
    naics_cbsa_scored["exposure_contribution"] = naics_cbsa_scored["employment_share_total"] * naics_cbsa_scored["felten_score"]

    naics_metro_exposure = (
        naics_cbsa_scored.groupby(["cbsa_code", "cbsa_name", "year"], as_index=False)
        .agg(
            cbsa_total_employment=("cbsa_total_employment", "max"),
            matched_employment=("employment", lambda values: float(values[naics_cbsa_scored.loc[values.index, "matched_flag"]].sum())),
            total_naics_rows=("naics_code", "count"),
            matched_naics_rows=("matched_flag", "sum"),
            naics_exposure_index=("exposure_contribution", "sum"),
        )
    )
    naics_metro_exposure["coverage_share"] = naics_metro_exposure["matched_employment"] / naics_metro_exposure["cbsa_total_employment"]

    latest_soc_year = int(soc_metro_exposure["year"].max())
    latest_naics_year = int(naics_metro_exposure["year"].max())

    soc_exposure_summary = pd.DataFrame([
        {
            "surface": "SOC metro exposure",
            "latest_year": latest_soc_year,
            "metros": soc_metro_exposure.loc[soc_metro_exposure["year"] == latest_soc_year, "cbsa_code"].nunique(),
            "mean_coverage_share": soc_metro_exposure.loc[soc_metro_exposure["year"] == latest_soc_year, "coverage_share"].mean(),
            "employment_weighted_coverage_share": soc_metro_exposure.loc[soc_metro_exposure["year"] == latest_soc_year, "matched_employment"].sum() / soc_metro_exposure.loc[soc_metro_exposure["year"] == latest_soc_year, "cbsa_detailed_employment"].sum(),
            "employment_weighted_detailed_share_of_total_oe_ws": soc_metro_exposure.loc[soc_metro_exposure["year"] == latest_soc_year, "cbsa_detailed_employment"].sum() / soc_metro_exposure.loc[soc_metro_exposure["year"] == latest_soc_year, "cbsa_total_employment"].sum(),
            "mean_e_m": soc_metro_exposure.loc[soc_metro_exposure["year"] == latest_soc_year, "e_m"].mean(),
        },
        {
            "surface": "NAICS metro exposure",
            "latest_year": latest_naics_year,
            "metros": naics_metro_exposure.loc[naics_metro_exposure["year"] == latest_naics_year, "cbsa_code"].nunique(),
            "mean_coverage_share": naics_metro_exposure.loc[naics_metro_exposure["year"] == latest_naics_year, "coverage_share"].mean(),
            "employment_weighted_coverage_share": naics_metro_exposure.loc[naics_metro_exposure["year"] == latest_naics_year, "matched_employment"].sum() / naics_metro_exposure.loc[naics_metro_exposure["year"] == latest_naics_year, "cbsa_total_employment"].sum(),
            "mean_e_m": naics_metro_exposure.loc[naics_metro_exposure["year"] == latest_naics_year, "naics_exposure_index"].mean(),
        },
    ])

    table(
        soc_exposure_summary,
        format_mapping={
            "mean_coverage_share": "{:.1%}",
            "employment_weighted_coverage_share": "{:.1%}",
            "employment_weighted_detailed_share_of_total_oe_ws": "{:.1%}",
            "mean_e_m": "{:.3f}",
        },
        page_size=5,
        pagination=False,
        label="Metro exposure summary",
    )
    dataframe(soc_metro_exposure, page_size=10, label="SOC metro exposure")
    dataframe(naics_metro_exposure, page_size=10, label="NAICS metro exposure")
    return (
        latest_naics_year,
        latest_soc_year,
        naics_cbsa_scored,
        naics_metro_exposure,
        soc_cbsa_scored,
        soc_metro_exposure,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Build A Comparison Base For The Hypotheses

    This is the metro-wide table we will use later when we test the claim against education, industry mix, and broad occupation context. For now we keep the latest row from each governed surface and document the vintage that each source contributes.
    """)
    return


@app.cell(hide_code=True)
def build_hypotheses_base(
    dataframe,
    industry_wide_cbsa,
    latest_naics_year,
    latest_soc_year,
    naics_metro_exposure,
    occupation_wide_cbsa,
    pd,
    population_cbsa,
    soc_metro_exposure,
    table,
):
    # Build one latest-row comparison base. The detailed exposure surface is current to OEWS 2025,
    # while the Gold comparison panel is mostly current to 2024. We keep the source-year fields so
    # any later hypothesis test stays explicit about the vintage mix instead of hiding it.
    soc_latest = (
        soc_metro_exposure.loc[soc_metro_exposure["year"] == latest_soc_year]
        .rename(columns={"year": "soc_exposure_year"})
        .copy()
    )

    naics_latest = (
        naics_metro_exposure.loc[naics_metro_exposure["year"] == latest_naics_year, ["cbsa_code", "year", "naics_exposure_index", "coverage_share"]]
        .rename(columns={"year": "naics_exposure_year", "coverage_share": "naics_coverage_share"})
        .copy()
    )

    industry_wide_latest_year = int(industry_wide_cbsa["year"].max())
    occupation_wide_latest_year = int(occupation_wide_cbsa["year"].max())
    population_latest_year = int(population_cbsa["year"].max())

    industry_wide_latest = (
        industry_wide_cbsa.loc[industry_wide_cbsa["year"] == industry_wide_latest_year]
        .drop(columns=["geo_level", "geo_name"])
        .rename(columns={"geo_id": "cbsa_code", "year": "industry_panel_year"})
    )

    occupation_wide_latest = (
        occupation_wide_cbsa.loc[occupation_wide_cbsa["year"] == occupation_wide_latest_year]
        .drop(columns=["geo_level", "geo_name"])
        .rename(columns={"geo_id": "cbsa_code", "year": "occupation_panel_year"})
    )

    population_latest = (
        population_cbsa.loc[population_cbsa["year"] == population_latest_year]
        .drop(columns=["geo_level", "geo_name"])
        .rename(columns={"geo_id": "cbsa_code", "year": "population_year"})
    )

    metro_analysis_base = (
        soc_latest
        .merge(naics_latest, on="cbsa_code", how="left", validate="one_to_one")
        .merge(industry_wide_latest, on="cbsa_code", how="left", validate="one_to_one")
        .merge(occupation_wide_latest, on="cbsa_code", how="left", validate="one_to_one", suffixes=("", "_occwide"))
        .merge(population_latest, on="cbsa_code", how="left", validate="one_to_one", suffixes=("", "_pop"))
    )

    comparison_summary = pd.DataFrame([
        {"metric": "Latest SOC exposure year", "value": latest_soc_year},
        {"metric": "Latest NAICS exposure year", "value": latest_naics_year},
        {"metric": "Latest industry panel year", "value": industry_wide_latest_year},
        {"metric": "Latest occupation-wide panel year", "value": occupation_wide_latest_year},
        {"metric": "Latest population panel year", "value": population_latest_year},
        {"metric": "Metro analysis base rows", "value": len(metro_analysis_base)},
    ])

    table(comparison_summary, page_size=10, pagination=False, label="Comparison base summary")
    dataframe(metro_analysis_base[[
        "cbsa_code", "cbsa_name", "soc_exposure_year", "e_m", "w_m_local", "coverage_share",
        "naics_exposure_year", "naics_exposure_index", "naics_coverage_share",
        "population_year", "pct_ba_plus", "industry_panel_year", "pct_qcew_private_emp_professional"
    ]], page_size=15, label="Comparison base")
    return metro_analysis_base, soc_latest


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Part 1 Descriptive Baseline

    This starts the first section of `analysis_program.md`. The goal here is not to test a claim yet. It is to see the national distribution, the poles, and Richmond's decomposition before we move into H1, H2, and H3.
    """)
    return


@app.cell(hide_code=True)
def _(
    RICHMOND_CBSA_CODE,
    latest_soc_year,
    np,
    pd,
    soc_cbsa_scored,
    soc_latest,
):
    # Build the first baseline artifacts for the notebook: national distributions for the metro
    # exposure measures, simple ranking tables, and a national SOC major-group decomposition.
    import matplotlib.pyplot as plt

    soc_latest_ranked = soc_latest.sort_values(['e_m', 'cbsa_name'], ascending=[False, True]).reset_index(drop=True)
    soc_latest_ranked['e_m_rank'] = np.arange(1, len(soc_latest_ranked) + 1)
    soc_latest_ranked['e_m_percentile'] = soc_latest_ranked['e_m'].rank(pct=True, method='average')
    soc_latest_ranked['w_m_local_rank'] = soc_latest_ranked['w_m_local'].rank(method='first', ascending=False)
    soc_latest_ranked['w_m_local_percentile'] = soc_latest_ranked['w_m_local'].rank(pct=True, method='average')
    soc_latest_ranked['w_minus_e'] = soc_latest_ranked['w_m_local'] - soc_latest_ranked['e_m']
    baseline_distribution_summary = pd.DataFrame([{'measure': 'E_m', 'metric': 'Metros', 'value': int(len(soc_latest_ranked))}, {'measure': 'E_m', 'metric': 'Mean', 'value': soc_latest_ranked['e_m'].mean()}, {'measure': 'E_m', 'metric': 'Median', 'value': soc_latest_ranked['e_m'].median()}, {'measure': 'E_m', 'metric': 'P10', 'value': soc_latest_ranked['e_m'].quantile(0.1)}, {'measure': 'E_m', 'metric': 'P90', 'value': soc_latest_ranked['e_m'].quantile(0.9)}, {'measure': 'E_m', 'metric': 'Minimum', 'value': soc_latest_ranked['e_m'].min()}, {'measure': 'E_m', 'metric': 'Maximum', 'value': soc_latest_ranked['e_m'].max()}, {'measure': 'W_m_local', 'metric': 'Metros', 'value': int(len(soc_latest_ranked))}, {'measure': 'W_m_local', 'metric': 'Mean', 'value': soc_latest_ranked['w_m_local'].mean()}, {'measure': 'W_m_local', 'metric': 'Median', 'value': soc_latest_ranked['w_m_local'].median()}, {'measure': 'W_m_local', 'metric': 'P10', 'value': soc_latest_ranked['w_m_local'].quantile(0.1)}, {'measure': 'W_m_local', 'metric': 'P90', 'value': soc_latest_ranked['w_m_local'].quantile(0.9)}, {'measure': 'W_m_local', 'metric': 'Minimum', 'value': soc_latest_ranked['w_m_local'].min()}, {'measure': 'W_m_local', 'metric': 'Maximum', 'value': soc_latest_ranked['w_m_local'].max()}])
    baseline_gap_summary = pd.DataFrame([{'metric': 'Mean W_m_local - E_m', 'value': soc_latest_ranked['w_minus_e'].mean()}, {'metric': 'Median W_m_local - E_m', 'value': soc_latest_ranked['w_minus_e'].median()}, {'metric': 'Share of metros where W_m_local > E_m', 'value': soc_latest_ranked['w_minus_e'].gt(0).mean()}, {'metric': 'Pearson correlation of metro measures', 'value': np.corrcoef(soc_latest_ranked['e_m'], soc_latest_ranked['w_m_local'])[0, 1]}])
    top_15_exposure = soc_latest_ranked.head(15)[['e_m_rank', 'cbsa_name', 'e_m', 'w_m_local', 'w_minus_e', 'coverage_share', 'payroll_coverage_share']]
    bottom_15_exposure = soc_latest_ranked.tail(15).sort_values(['e_m', 'cbsa_name'], ascending=[True, True])[['cbsa_name', 'e_m', 'w_m_local', 'w_minus_e', 'coverage_share', 'payroll_coverage_share']]
    soc_major_group_labels = {'11': 'Management', '13': 'Business and Financial Operations', '15': 'Computer and Mathematical', '17': 'Architecture and Engineering', '19': 'Life, Physical, and Social Science', '21': 'Community and Social Service', '23': 'Legal', '25': 'Educational Instruction and Library', '27': 'Arts, Design, Entertainment, Sports, and Media', '29': 'Healthcare Practitioners and Technical', '31': 'Healthcare Support', '33': 'Protective Service', '35': 'Food Preparation and Serving Related', '37': 'Building and Grounds Cleaning and Maintenance', '39': 'Personal Care and Service', '41': 'Sales and Related', '43': 'Office and Administrative Support', '45': 'Farming, Fishing, and Forestry', '47': 'Construction and Extraction', '49': 'Installation, Maintenance, and Repair', '51': 'Production', '53': 'Transportation and Material Moving', '55': 'Military Specific'}
    national_soc_detail = soc_cbsa_scored.loc[(soc_cbsa_scored['year'] == latest_soc_year) & soc_cbsa_scored['matched_flag']].copy()
    national_soc_detail['soc_major_group'] = national_soc_detail['soc_code'].str.slice(0, 2)
    national_soc_detail['soc_major_group_label'] = national_soc_detail['soc_major_group'].map(soc_major_group_labels).fillna('Other / Unmapped')
    national_detailed_employment = soc_cbsa_scored.loc[soc_cbsa_scored['year'] == latest_soc_year, 'employment'].sum()
    national_matched_payroll = national_soc_detail['wage_bill'].sum()
    national_soc_detail['national_employment_share'] = national_soc_detail['employment'] / national_detailed_employment
    national_soc_detail['national_payroll_share'] = national_soc_detail['wage_bill'] / national_matched_payroll
    national_soc_detail['employment_weighted_score_component'] = national_soc_detail['employment'] * national_soc_detail['felten_score']
    national_soc_detail['payroll_weighted_score_component'] = national_soc_detail['wage_bill'] * national_soc_detail['felten_score']
    national_soc_detail['contribution_to_national_e'] = national_soc_detail['national_employment_share'] * national_soc_detail['felten_score']
    national_soc_detail['contribution_to_national_w_local'] = national_soc_detail['national_payroll_share'] * national_soc_detail['felten_score']
    national_soc_group_decomposition = national_soc_detail.groupby(['soc_major_group', 'soc_major_group_label'], as_index=False).agg(employment=('employment', 'sum'), wage_bill=('wage_bill', 'sum'), national_employment_share=('national_employment_share', 'sum'), national_payroll_share=('national_payroll_share', 'sum'), contribution_to_national_e=('contribution_to_national_e', 'sum'), contribution_to_national_w_local=('contribution_to_national_w_local', 'sum'), employment_weighted_score_component=('employment_weighted_score_component', 'sum'), payroll_weighted_score_component=('payroll_weighted_score_component', 'sum'))
    national_soc_group_decomposition['employment_weighted_felten_score'] = national_soc_group_decomposition['employment_weighted_score_component'] / national_soc_group_decomposition['employment']
    national_soc_group_decomposition['payroll_weighted_felten_score'] = national_soc_group_decomposition['payroll_weighted_score_component'] / national_soc_group_decomposition['wage_bill']
    national_soc_group_decomposition = national_soc_group_decomposition.sort_values(['contribution_to_national_e', 'national_employment_share'], ascending=[False, False]).reset_index(drop=True)
    richmond_summary = soc_latest_ranked.loc[soc_latest_ranked['cbsa_code'] == RICHMOND_CBSA_CODE, ['cbsa_code', 'cbsa_name', 'e_m_rank', 'e_m_percentile', 'e_m', 'w_m_local', 'coverage_share', 'payroll_coverage_share']]
    return (
        baseline_distribution_summary,
        baseline_gap_summary,
        bottom_15_exposure,
        national_soc_detail,
        national_soc_group_decomposition,
        plt,
        richmond_summary,
        soc_latest_ranked,
        top_15_exposure,
    )


@app.cell
def _(
    baseline_distribution_summary,
    baseline_gap_summary,
    bottom_15_exposure,
    national_soc_group_decomposition,
    richmond_summary,
    table,
    top_15_exposure,
):
    # Keep the descriptive tables together before the charts so the narrative reads top-down.
    table(
        baseline_distribution_summary,
        format_mapping={'value': '{:.3f}'},
        page_size=20,
        pagination=False,
        label="Baseline distribution summary",
    )
    # This gap summary makes the baseline relationship explicit: exposed payroll usually runs
    # higher than exposed headcount, which implies AI exposure tilts toward higher-wage work.
    table(
        baseline_gap_summary,
        format_mapping={'value': '{:.3f}'},
        page_size=10,
        pagination=False,
        label="Baseline gap summary",
    )
    table(
        top_15_exposure,
        format_mapping={'e_m': '{:.3f}', 'w_m_local': '{:.3f}', 'w_minus_e': '{:.3f}', 'coverage_share': '{:.1%}', 'payroll_coverage_share': '{:.1%}'},
        page_size=15,
        pagination=False,
        label="Top 15 metros by E_m",
    )
    table(
        bottom_15_exposure,
        format_mapping={'e_m': '{:.3f}', 'w_m_local': '{:.3f}', 'w_minus_e': '{:.3f}', 'coverage_share': '{:.1%}', 'payroll_coverage_share': '{:.1%}'},
        page_size=15,
        pagination=False,
        label="Bottom 15 metros by E_m",
    )
    table(
        richmond_summary,
        format_mapping={'e_m_percentile': '{:.1%}', 'e_m': '{:.3f}', 'w_m_local': '{:.3f}', 'coverage_share': '{:.1%}', 'payroll_coverage_share': '{:.1%}'},
        page_size=5,
        pagination=False,
        label="Richmond snapshot",
    )
    table(
        national_soc_group_decomposition[['soc_major_group_label', 'national_employment_share', 'national_payroll_share', 'contribution_to_national_e', 'contribution_to_national_w_local', 'employment_weighted_felten_score', 'payroll_weighted_felten_score']].head(15),
        format_mapping={'national_employment_share': '{:.2%}', 'national_payroll_share': '{:.2%}', 'contribution_to_national_e': '{:.4f}', 'contribution_to_national_w_local': '{:.4f}', 'employment_weighted_felten_score': '{:.3f}', 'payroll_weighted_felten_score': '{:.3f}'},
        page_size=15,
        pagination=False,
        label="National SOC group decomposition",
    )
    return


@app.cell
def _(np, plt, soc_latest_ranked):
    # Start the baseline visuals with the raw national metro distributions before showing how the
    # two measures line up against each other.
    _fig, _ax = plt.subplots(figsize=(8.5, 4.8))
    _ax.hist(soc_latest_ranked['e_m'], bins=28, alpha=0.7, label='E_m')
    _ax.hist(soc_latest_ranked['w_m_local'], bins=28, alpha=0.55, label='W_m_local')
    _ax.set_title('Baseline: Metro distributions of E_m and W_m_local')
    _ax.set_xlabel('Exposure value')
    _ax.set_ylabel('Metros')
    _ax.legend(frameon=False)
    _ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(plt, soc_latest_ranked):
    # Follow the distributions with the direct comparison so the notebook shows how often payroll
    # exposure exceeds headcount exposure and by how much.
    _fig, _ax = plt.subplots(figsize=(7.5, 6))
    _ax.scatter(soc_latest_ranked['e_m'], soc_latest_ranked['w_m_local'], alpha=0.65, s=20)
    _line_floor = min(soc_latest_ranked['e_m'].min(), soc_latest_ranked['w_m_local'].min())
    _line_ceiling = max(soc_latest_ranked['e_m'].max(), soc_latest_ranked['w_m_local'].max())
    _regression_coefficients = np.polyfit(soc_latest_ranked['e_m'], soc_latest_ranked['w_m_local'], 1)
    _x_grid = np.linspace(soc_latest_ranked['e_m'].min(), soc_latest_ranked['e_m'].max(), 200)
    _ax.plot([_line_floor, _line_ceiling], [_line_floor, _line_ceiling], color='black', linewidth=1, linestyle='--')
    _ax.plot(_x_grid, _regression_coefficients[0] * _x_grid + _regression_coefficients[1], color='tab:orange', linewidth=1.2)
    _ax.set_title('Baseline: Payroll exposure versus headcount exposure')
    _ax.set_xlabel('E_m')
    _ax.set_ylabel('W_m_local')
    _ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(national_soc_group_decomposition, np, plt):
    # Make the broad occupation story easier to read by leading with contribution bars first.
    _national_soc_group_plot = national_soc_group_decomposition.sort_values('contribution_to_national_e', ascending=True)
    _fig, _ax = plt.subplots(figsize=(10, 7))
    _y_positions = np.arange(len(_national_soc_group_plot))
    _bar_height = 0.38
    _ax.barh(_y_positions - _bar_height / 2, _national_soc_group_plot['contribution_to_national_e'], height=_bar_height, label='Employment-weighted contribution')
    _ax.barh(_y_positions + _bar_height / 2, _national_soc_group_plot['contribution_to_national_w_local'], height=_bar_height, label='Wage-weighted contribution')
    _ax.set_yticks(_y_positions)
    _ax.set_yticklabels(_national_soc_group_plot['soc_major_group_label'])
    _ax.set_title('Baseline: National AI exposure contribution by SOC major group')
    _ax.set_xlabel('Contribution to national exposure index')
    _ax.legend(frameon=False)
    _ax.grid(alpha=0.2, axis='x')
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(national_soc_group_decomposition, np, plt):
    # Recast the share comparison as stacked bars so the weight shift reads as a compositional
    # comparison between the employment surface and the payroll surface.
    _share_plot = national_soc_group_decomposition.sort_values('national_employment_share', ascending=False).reset_index(drop=True)
    _fig, _ax = plt.subplots(figsize=(11.5, 3.8))
    _left_emp = 0.0
    _left_pay = 0.0
    _cmap = plt.get_cmap('tab20')
    _colors = [_cmap(_idx % 20) for _idx in range(len(_share_plot))]
    for _idx, _row in _share_plot.iterrows():
        _ax.barh('Employment share', _row['national_employment_share'], left=_left_emp, color=_colors[_idx], edgecolor='white', linewidth=0.4)
        _ax.barh('Payroll share', _row['national_payroll_share'], left=_left_pay, color=_colors[_idx], edgecolor='white', linewidth=0.4)
        _left_emp += _row['national_employment_share']
        _left_pay += _row['national_payroll_share']
    _ax.set_xlim(0, 1)
    _ax.set_title('Baseline: National employment share versus payroll share by SOC group')
    _ax.set_xlabel('Share of national matched surface')
    _ax.grid(alpha=0.2, axis='x')
    _legend_handles = [
        plt.Line2D([0], [0], color=_colors[_idx], linewidth=6, label=_row['soc_major_group_label'])
        for _idx, _row in _share_plot.iterrows()
    ]
    _ax.legend(handles=_legend_handles, bbox_to_anchor=(1.01, 1), loc='upper left', frameon=False, fontsize=8)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Baseline Decomposition Notes

    The decomposition variables answer two different questions.

    `contribution_to_national_e` and `contribution_to_national_w_local` ask: "how much does this group add to the national exposure index?" Their math is:

    `group share × group Felten score`

    So a group can contribute a lot because it is large, because it has a high score, or because both are true.

    `employment_weighted_felten_score` and `payroll_weighted_felten_score` ask a different question: "how exposed is this group on average after weighting by employment or payroll?" Their math is:

    `sum(weight × Felten score) / sum(weight)`

    So the weighted Felten score is an average exposure level inside the group, while the contribution fields also incorporate how much of the national surface that group occupies.
    """)
    return


@app.cell
def _(dataframe, national_soc_detail):
    # Show the detailed occupation decomposition directly so we can inspect which occupations carry
    # the national index, then keep the grouped view for the higher-level graphical summary.
    national_occupation_decomposition = (
        national_soc_detail.groupby(["soc_code", "soc_title", "soc_major_group_label"], as_index=False)
        .agg(
            employment=("employment", "sum"),
            wage_bill=("wage_bill", "sum"),
            felten_score=("felten_score", "first"),
            national_employment_share=("national_employment_share", "sum"),
            national_payroll_share=("national_payroll_share", "sum"),
            contribution_to_national_e=("contribution_to_national_e", "sum"),
            contribution_to_national_w_local=("contribution_to_national_w_local", "sum"),
        )
        .sort_values(["contribution_to_national_e", "national_employment_share"], ascending=[False, False])
        .reset_index(drop=True)
    )

    dataframe(national_occupation_decomposition[[
        "soc_code", "soc_title", "soc_major_group_label", "national_employment_share",
        "national_payroll_share", "felten_score", "contribution_to_national_e",
        "contribution_to_national_w_local"
    ]],
    format_mapping={
        "national_employment_share": "{:.2%}", "national_payroll_share": "{:.2%}",
        "felten_score": "{:.3f}", "contribution_to_national_e": "{:.4f}",
        "contribution_to_national_w_local": "{:.4f}"
    },
    page_size=25,
    label="National occupation decomposition")
    return


@app.cell
def _(dataframe, latest_naics_year, naics_cbsa_scored, pd):
    # Pair the occupation decomposition with a national industry-weight view. This makes it easier
    # to spot industries that are small in total employment but unusually high or low on the score.
    # We collapse to 2-digit NAICS groups here because the 4-digit surface is too noisy for a
    # quick national comparison chart.
    national_naics_detail = naics_cbsa_scored.loc[(naics_cbsa_scored['year'] == latest_naics_year) & naics_cbsa_scored['matched_flag']].copy()
    national_naics_total_employment = naics_cbsa_scored.loc[naics_cbsa_scored['year'] == latest_naics_year, 'employment'].sum()
    national_naics_detail['national_employment_share'] = national_naics_detail['employment'] / national_naics_total_employment
    national_naics_detail['contribution_to_national_naics_exposure'] = national_naics_detail['national_employment_share'] * national_naics_detail['felten_score']
    national_naics_detail['naics_2_digit'] = national_naics_detail['naics_code'].str.slice(0, 2)
    national_naics_detail['felten_weighted_employment'] = national_naics_detail['employment'] * national_naics_detail['felten_score']
    national_naics_detail['top_title_rank'] = national_naics_detail.groupby('naics_2_digit')['employment'].rank(method='first', ascending=False)
    national_naics_2_digit = (
        national_naics_detail.groupby(['naics_2_digit'], as_index=False)
        .agg(
            employment=('employment', 'sum'),
            national_employment_share=('national_employment_share', 'sum'),
            contribution_to_national_naics_exposure=('contribution_to_national_naics_exposure', 'sum'),
            felten_weighted_employment=('felten_weighted_employment', 'sum'),
        )
    )
    national_naics_titles = (
        national_naics_detail.loc[national_naics_detail['top_title_rank'] == 1, ['naics_2_digit', 'naics_title']]
        .drop_duplicates(subset=['naics_2_digit'])
        .rename(columns={'naics_title': 'naics_2_digit_title'})
    )
    national_naics_industry_decomposition = (
        national_naics_2_digit
        .merge(national_naics_titles, on='naics_2_digit', how='left', validate='one_to_one')
        .sort_values(['national_employment_share', 'contribution_to_national_naics_exposure'], ascending=[False, False])
        .reset_index(drop=True)
    )
    national_naics_industry_decomposition['employment_weighted_felten_score'] = national_naics_industry_decomposition['felten_weighted_employment'] / national_naics_industry_decomposition['employment']
    dataframe(
        national_naics_industry_decomposition[['naics_2_digit', 'naics_2_digit_title', 'national_employment_share', 'employment_weighted_felten_score', 'contribution_to_national_naics_exposure']],
        format_mapping={'national_employment_share': '{:.2%}', 'employment_weighted_felten_score': '{:.3f}', 'contribution_to_national_naics_exposure': '{:.4f}'},
        page_size=25,
        label="National 2-digit NAICS decomposition",
    )
    return national_naics_industry_decomposition


@app.cell
def _(national_naics_industry_decomposition, plt):
    # Keep the industry comparison as a secondary view after the SOC decomposition lead.
    _fig, _ax = plt.subplots(figsize=(8, 6))
    _ax.scatter(national_naics_industry_decomposition['national_employment_share'], national_naics_industry_decomposition['employment_weighted_felten_score'], s=35, alpha=0.65)
    for _, _row in national_naics_industry_decomposition.head(12).iterrows():
        _ax.text(_row['national_employment_share'], _row['employment_weighted_felten_score'], _row['naics_2_digit'], fontsize=7, alpha=0.8)
    _ax.set_title('Baseline: National 2-digit industry weights versus Felten score')
    _ax.set_xlabel('National employment share')
    _ax.set_ylabel('Felten score')
    _ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### SOC And NAICS Comparison Note

    The SOC charts and the `2-digit` NAICS comparison are parallel lenses, not a direct crosswalk. SOC tells us which occupation families carry exposure. NAICS tells us which broad industry structures are large and high-score. They meet at the metro, not at a shared code hierarchy.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. H1 Wage-Weighted Vs Employment-Weighted Exposure

    H1 asks whether the metro ranking changes meaningfully when we weight exposure by the local wage bill instead of job counts. We use the existing metro-level SOC table, keep `W_m_local` as the primary wage-weighted measure, and leave the detailed-SOC coverage denominator unchanged.
    """)
    return


@app.cell
def _(np, pd, soc_latest):
    # Start H1 from the metro-level SOC exposure table already built above. This cell only builds
    # the shared comparison objects; the displays live in smaller cells below.
    h1_comparison = soc_latest[['cbsa_code', 'cbsa_name', 'e_m', 'w_m_local', 'coverage_share', 'payroll_coverage_share', 'detailed_share_of_total_oe_ws', 'matched_employment', 'cbsa_detailed_employment', 'matched_payroll', 'cbsa_total_payroll']].dropna(subset=['e_m', 'w_m_local']).copy()
    h1_comparison['e_m_rank'] = h1_comparison['e_m'].rank(method='first', ascending=False)
    h1_comparison['w_m_local_rank'] = h1_comparison['w_m_local'].rank(method='first', ascending=False)
    h1_comparison['e_m_percentile'] = h1_comparison['e_m'].rank(pct=True, method='average')
    h1_comparison['w_m_local_percentile'] = h1_comparison['w_m_local'].rank(pct=True, method='average')
    h1_comparison['rank_shift'] = h1_comparison['e_m_rank'] - h1_comparison['w_m_local_rank']
    h1_comparison['absolute_rank_shift'] = h1_comparison['rank_shift'].abs()
    h1_ranked_e_m = h1_comparison.sort_values(['e_m_rank', 'cbsa_name']).reset_index(drop=True)
    h1_ranked_w_m_local = h1_comparison.sort_values(['w_m_local_rank', 'cbsa_name']).reset_index(drop=True)
    h1_spearman = np.corrcoef(h1_comparison['e_m_rank'], h1_comparison['w_m_local_rank'])[0, 1]
    h1_mean_absolute_rank_shift = h1_comparison['absolute_rank_shift'].mean()
    h1_metrics = pd.DataFrame([{'metric': 'Metros in H1 comparison', 'value': len(h1_comparison)}, {'metric': 'Spearman correlation of ranks', 'value': h1_spearman}, {'metric': 'Mean absolute rank shift', 'value': h1_mean_absolute_rank_shift}, {'metric': 'Median absolute rank shift', 'value': h1_comparison['absolute_rank_shift'].median()}])
    h1_top_risers = h1_comparison.sort_values(['rank_shift', 'absolute_rank_shift', 'cbsa_name'], ascending=[False, False, True]).head(20)[['cbsa_name', 'e_m', 'w_m_local', 'e_m_rank', 'w_m_local_rank', 'rank_shift', 'absolute_rank_shift', 'e_m_percentile', 'w_m_local_percentile', 'coverage_share', 'payroll_coverage_share', 'detailed_share_of_total_oe_ws']]
    h1_top_fallers = h1_comparison.sort_values(['rank_shift', 'absolute_rank_shift', 'cbsa_name'], ascending=[True, False, True]).head(20)[['cbsa_name', 'e_m', 'w_m_local', 'e_m_rank', 'w_m_local_rank', 'rank_shift', 'absolute_rank_shift', 'e_m_percentile', 'w_m_local_percentile', 'coverage_share', 'payroll_coverage_share', 'detailed_share_of_total_oe_ws']]
    h1_mover_sample = pd.concat([h1_top_risers, h1_top_fallers], ignore_index=True)
    h1_top_decile_cutoff = h1_comparison['absolute_rank_shift'].quantile(0.9)
    h1_top_decile_movers = h1_comparison.loc[h1_comparison['absolute_rank_shift'] >= h1_top_decile_cutoff].copy()
    # Spearman is just the Pearson correlation of the rank vectors, so we can compute it directly
    # without adding a SciPy dependency to the notebook environment.
    # The mover QA checks whether large rank changes are concentrated in low-coverage metros.
    h1_coverage_qa = pd.DataFrame([{'group': 'All metros', 'metros': len(h1_comparison), 'mean_coverage_share': h1_comparison['coverage_share'].mean(), 'median_coverage_share': h1_comparison['coverage_share'].median(), 'mean_payroll_coverage_share': h1_comparison['payroll_coverage_share'].mean(), 'share_below_90pct_coverage': h1_comparison['coverage_share'].lt(0.9).mean(), 'share_below_90pct_payroll_coverage': h1_comparison['payroll_coverage_share'].lt(0.9).mean(), 'mean_absolute_rank_shift': h1_comparison['absolute_rank_shift'].mean()}, {'group': 'Top/bottom 20 movers', 'metros': len(h1_mover_sample), 'mean_coverage_share': h1_mover_sample['coverage_share'].mean(), 'median_coverage_share': h1_mover_sample['coverage_share'].median(), 'mean_payroll_coverage_share': h1_mover_sample['payroll_coverage_share'].mean(), 'share_below_90pct_coverage': h1_mover_sample['coverage_share'].lt(0.9).mean(), 'share_below_90pct_payroll_coverage': h1_mover_sample['payroll_coverage_share'].lt(0.9).mean(), 'mean_absolute_rank_shift': h1_mover_sample['absolute_rank_shift'].mean()}, {'group': 'Top decile absolute movers', 'metros': len(h1_top_decile_movers), 'mean_coverage_share': h1_top_decile_movers['coverage_share'].mean(), 'median_coverage_share': h1_top_decile_movers['coverage_share'].median(), 'mean_payroll_coverage_share': h1_top_decile_movers['payroll_coverage_share'].mean(), 'share_below_90pct_coverage': h1_top_decile_movers['coverage_share'].lt(0.9).mean(), 'share_below_90pct_payroll_coverage': h1_top_decile_movers['payroll_coverage_share'].lt(0.9).mean(), 'mean_absolute_rank_shift': h1_top_decile_movers['absolute_rank_shift'].mean()}])
    return (
        h1_comparison,
        h1_coverage_qa,
        h1_metrics,
        h1_ranked_e_m,
        h1_ranked_w_m_local,
        h1_top_fallers,
        h1_top_risers,
    )


@app.cell
def _(h1_metrics, table):
    # Put the headline numbers first so the H1 answer is visible before the detail tables.
    table(h1_metrics, format_mapping={'value': '{:.3f}'}, page_size=10, pagination=False, label="H1 headline metrics")
    return


@app.cell
def _(h1_comparison, np, plt):
    # Keep the H1 scatter alone so the headline relationship reads before the shift distribution.
    _fig, _ax = plt.subplots(figsize=(7.5, 6))
    _ax.scatter(h1_comparison['e_m'], h1_comparison['w_m_local'], alpha=0.7, s=20)
    _regression_coefficients = np.polyfit(h1_comparison['e_m'], h1_comparison['w_m_local'], 1)
    _x_grid = np.linspace(h1_comparison['e_m'].min(), h1_comparison['e_m'].max(), 200)
    _ax.plot(_x_grid, _regression_coefficients[0] * _x_grid + _regression_coefficients[1], color='black', linewidth=1)
    _ax.set_title('H1: Metro exposure by headcount versus local wage bill')
    _ax.set_xlabel('E_m')
    _ax.set_ylabel('W_m_local')
    _ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(h1_comparison, plt):
    # The rank-shift histogram stands on its own because it is the core reshuffling exhibit.
    _fig, _ax = plt.subplots(figsize=(8.5, 4.8))
    _ax.hist(h1_comparison['rank_shift'], bins=30, alpha=0.75)
    _ax.axvline(0, color='black', linewidth=1, linestyle='--')
    _ax.set_title('H1: Distribution of metro rank shifts')
    _ax.set_xlabel('Rank shift: E_m rank - W_m_local rank')
    _ax.set_ylabel('Metros')
    _ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(dataframe, h1_coverage_qa, h1_top_fallers, h1_top_risers, table):
    # Show the metros that move most once we switch from headcount to payroll weighting, then
    # follow immediately with the coverage QA that tells us whether those movers look credible.
    dataframe(h1_top_risers, format_mapping={
        "e_m": "{:.3f}", "w_m_local": "{:.3f}", "e_m_percentile": "{:.1%}",
        "w_m_local_percentile": "{:.1%}", "coverage_share": "{:.1%}",
        "payroll_coverage_share": "{:.1%}", "detailed_share_of_total_oe_ws": "{:.1%}"
    }, page_size=20, label="Top 20 metros rising on W_m_local rank")
    dataframe(h1_top_fallers, format_mapping={
        "e_m": "{:.3f}", "w_m_local": "{:.3f}", "e_m_percentile": "{:.1%}",
        "w_m_local_percentile": "{:.1%}", "coverage_share": "{:.1%}",
        "payroll_coverage_share": "{:.1%}", "detailed_share_of_total_oe_ws": "{:.1%}"
    }, page_size=20, label="Top 20 metros falling on W_m_local rank")
    table(h1_coverage_qa, format_mapping={
        "mean_coverage_share": "{:.1%}", "median_coverage_share": "{:.1%}",
        "mean_payroll_coverage_share": "{:.1%}", "share_below_90pct_coverage": "{:.1%}",
        "share_below_90pct_payroll_coverage": "{:.1%}", "mean_absolute_rank_shift": "{:.1f}"
    }, page_size=10, pagination=False, label="H1 coverage QA")
    return


@app.cell
def _(dataframe, h1_ranked_e_m, h1_ranked_w_m_local):
    # Keep the raw top-ranked lists at the end of H1. They are useful reference tables, but they
    # are less important than the metrics, plots, movers, and coverage diagnostics above.
    dataframe(h1_ranked_e_m, format_mapping={
        "e_m": "{:.3f}", "w_m_local": "{:.3f}", "e_m_percentile": "{:.1%}",
        "w_m_local_percentile": "{:.1%}", "coverage_share": "{:.1%}",
        "payroll_coverage_share": "{:.1%}", "detailed_share_of_total_oe_ws": "{:.1%}"
    }, page_size=20, label="Ranked E_m metros")
    dataframe(h1_ranked_w_m_local, format_mapping={
        "e_m": "{:.3f}", "w_m_local": "{:.3f}", "e_m_percentile": "{:.1%}",
        "w_m_local_percentile": "{:.1%}", "coverage_share": "{:.1%}",
        "payroll_coverage_share": "{:.1%}", "detailed_share_of_total_oe_ws": "{:.1%}"
    }, page_size=20, label="Ranked W_m_local metros")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. H2 Exposure, Attainment, And Industry Mix

    H2 tests whether attainment is doing real explanatory work or mostly standing in for metro industry structure. We keep `pct_ba_plus` as the primary attainment field, use quartiles as the main binning choice, and run quintiles plus population-weighted regression as robustness checks.
    """)
    return


@app.cell
def _(metro_analysis_base, np, pd):
    # H2 starts from the merged metro comparison base so the source-year mix stays explicit.
    # We use `pct_ba_plus` as the primary attainment field, then construct mutually exclusive
    # QCEW sector shares from the covered-employment counts to avoid mixing incompatible bases.
    industry_count_map = {
        "ag_mining": "qcew_private_emp_ag_mining",
        "construction": "qcew_private_emp_construction",
        "manufacturing": "qcew_private_emp_manufacturing",
        "wholesale": "qcew_private_emp_wholesale",
        "retail": "qcew_private_emp_retail",
        "transport_util": "qcew_private_emp_transport_util",
        "information": "qcew_private_emp_information",
        "finance_real": "qcew_private_emp_finance_real",
        "professional": "qcew_private_emp_professional",
        "educ_health": "qcew_private_emp_educ_health",
        "arts_accomm_food": "qcew_private_emp_arts_accomm_food",
        "other_services": "qcew_private_emp_other_services",
        "public_admin": "qcew_public_admin_emp",
    }
    occupation_share_cols = [
        "oews_pct_emp_stem",
        "oews_pct_emp_management_professional",
        "oews_pct_emp_service",
        "oews_pct_emp_production_transportation",
        "oews_pct_emp_other",
    ]

    h2_base = metro_analysis_base.copy()
    _numeric_cols = ["e_m", "pct_ba_plus", "pop_total"] + list(industry_count_map.values()) + occupation_share_cols
    for _col in _numeric_cols:
        h2_base[_col] = pd.to_numeric(h2_base[_col], errors="coerce")

    h2_base = h2_base.rename(columns={"pct_ba_plus": "attainment_measure", "pop_total": "metro_population"})
    h2_base = h2_base.dropna(subset=["e_m", "attainment_measure", "metro_population"]).copy()

    sector_total = pd.Series(0.0, index=h2_base.index)
    for _count_col in industry_count_map.values():
        sector_total = sector_total.add(h2_base[_count_col].fillna(0), fill_value=0)
    h2_base["qcew_sector_total_for_h2"] = sector_total

    industry_share_cols = []
    for sector_label, count_col in industry_count_map.items():
        share_col = f"industry_share_{sector_label}"
        h2_base[share_col] = h2_base[count_col] / h2_base["qcew_sector_total_for_h2"]
        industry_share_cols.append(share_col)

    h2_base = h2_base.replace([np.inf, -np.inf], np.nan)
    h2_base = h2_base.dropna(subset=industry_share_cols + ["e_m", "attainment_measure"]).copy()

    quartile_labels = ["Q1 lowest BA+", "Q2", "Q3", "Q4 highest BA+"]
    quintile_labels = ["Q1", "Q2", "Q3", "Q4", "Q5"]
    h2_base["attainment_quartile"] = pd.qcut(
        h2_base["attainment_measure"],
        q=4,
        labels=quartile_labels,
        duplicates="drop",
    )
    h2_base["attainment_quintile"] = pd.qcut(
        h2_base["attainment_measure"],
        q=5,
        labels=quintile_labels,
        duplicates="drop",
    )

    def eta_squared(frame, group_col, value_col):
        grouped = frame.groupby(group_col, observed=True)[value_col]
        grand_mean = frame[value_col].mean()
        between_ss = sum(len(group) * (group.mean() - grand_mean) ** 2 for _, group in grouped)
        total_ss = ((frame[value_col] - grand_mean) ** 2).sum()
        return between_ss / total_ss if total_ss else np.nan

    def fit_linear_model(frame, y_col, x_cols, weights_col=None):
        clean = frame[[y_col] + x_cols + ([weights_col] if weights_col else [])].dropna().copy()
        y = clean[y_col].to_numpy(dtype=float)
        X = clean[x_cols].to_numpy(dtype=float)
        X_design = np.column_stack([np.ones(len(clean)), X])

        if weights_col:
            weights = clean[weights_col].to_numpy(dtype=float)
            weight_root = np.sqrt(weights)
            beta = np.linalg.lstsq(X_design * weight_root[:, None], y * weight_root, rcond=None)[0]
            y_hat = X_design @ beta
            residuals = y - y_hat
            y_bar = np.average(y, weights=weights)
            sse = np.sum(weights * residuals ** 2)
            sst = np.sum(weights * (y - y_bar) ** 2)
        else:
            beta = np.linalg.lstsq(X_design, y, rcond=None)[0]
            y_hat = X_design @ beta
            residuals = y - y_hat
            y_bar = y.mean()
            sse = np.sum(residuals ** 2)
            sst = np.sum((y - y_bar) ** 2)

        r2 = 1 - (sse / sst) if sst else np.nan
        n_obs = len(clean)
        n_predictors = len(x_cols)
        adj_r2 = 1 - (1 - r2) * (n_obs - 1) / (n_obs - n_predictors - 1) if n_obs > n_predictors + 1 else np.nan

        fitted = clean.copy()
        fitted["fitted_value"] = y_hat
        fitted["residual"] = residuals
        return {
            "frame": fitted,
            "beta": beta,
            "r2": r2,
            "adj_r2": adj_r2,
            "sse": sse,
            "n_obs": n_obs,
            "n_predictors": n_predictors,
        }

    def compute_vif(frame, x_cols):
        vif_rows = []
        for target_col in x_cols:
            _other_cols = [_col for _col in x_cols if _col != target_col]
            other_fit = fit_linear_model(frame, target_col, _other_cols)
            r2_other = other_fit["r2"]
            vif_rows.append({
                "predictor": target_col,
                "vif": np.inf if r2_other >= 0.999999 else 1 / (1 - r2_other),
            })
        return pd.DataFrame(vif_rows).sort_values("vif", ascending=False).reset_index(drop=True)

    regression_cols = industry_share_cols[:-1]
    occupation_regression_cols = occupation_share_cols[:-1]
    h2_model_a = fit_linear_model(h2_base, "e_m", regression_cols)
    h2_model_b = fit_linear_model(h2_base, "e_m", regression_cols + ["attainment_measure"])
    h2_model_b_weighted = fit_linear_model(h2_base, "e_m", regression_cols + ["attainment_measure"], weights_col="metro_population")
    h2_attainment_only = fit_linear_model(h2_base, "e_m", ["attainment_measure"])
    h2_occupation_model_a = fit_linear_model(h2_base, "e_m", occupation_regression_cols)
    h2_occupation_model_b = fit_linear_model(h2_base, "e_m", occupation_regression_cols + ["attainment_measure"])

    partial_r2 = (h2_model_b["r2"] - h2_model_a["r2"]) / (1 - h2_model_a["r2"])
    partial_r2_weighted = (h2_model_b_weighted["r2"] - fit_linear_model(h2_base, "e_m", regression_cols, weights_col="metro_population")["r2"]) / (1 - fit_linear_model(h2_base, "e_m", regression_cols, weights_col="metro_population")["r2"])
    occupation_partial_r2 = (h2_occupation_model_b["r2"] - h2_occupation_model_a["r2"]) / (1 - h2_occupation_model_a["r2"])

    added_df_num = h2_model_b["n_predictors"] - h2_model_a["n_predictors"]
    added_df_den = h2_model_b["n_obs"] - h2_model_b["n_predictors"] - 1
    added_variable_f = ((h2_model_a["sse"] - h2_model_b["sse"]) / added_df_num) / (h2_model_b["sse"] / added_df_den)

    h2_vif = compute_vif(h2_base, regression_cols + ["attainment_measure"])

    h2_base["attainment_only_fitted"] = h2_attainment_only["frame"]["fitted_value"].to_numpy()
    h2_base["attainment_only_residual"] = h2_attainment_only["frame"]["residual"].to_numpy()

    h2_attainment_summary = pd.DataFrame([
        {"metric": "Primary attainment field", "value": "pct_ba_plus"},
        {"metric": "Metros in H2 base", "value": len(h2_base)},
        {"metric": "Mean BA+ share", "value": h2_base["attainment_measure"].mean()},
        {"metric": "Median BA+ share", "value": h2_base["attainment_measure"].median()},
        {"metric": "Missing BA+ share after merge", "value": metro_analysis_base["pct_ba_plus"].isna().mean()},
    ])

    h2_eta_summary = pd.DataFrame([
        {"binning": "Attainment quartiles", "groups": h2_base["attainment_quartile"].nunique(), "eta_squared": eta_squared(h2_base, "attainment_quartile", "e_m")},
        {"binning": "Attainment quintiles", "groups": h2_base["attainment_quintile"].nunique(), "eta_squared": eta_squared(h2_base, "attainment_quintile", "e_m")},
    ])

    h2_regression_summary = pd.DataFrame([
        {"model": "Model A: industry shares only", "r_squared": h2_model_a["r2"], "adjusted_r_squared": h2_model_a["adj_r2"]},
        {"model": "Model B: industry shares + BA+", "r_squared": h2_model_b["r2"], "adjusted_r_squared": h2_model_b["adj_r2"]},
        {"model": "Occupation model A: broad occupation shares only", "r_squared": h2_occupation_model_a["r2"], "adjusted_r_squared": h2_occupation_model_a["adj_r2"]},
        {"model": "Occupation model B: broad occupation shares + BA+", "r_squared": h2_occupation_model_b["r2"], "adjusted_r_squared": h2_occupation_model_b["adj_r2"]},
        {"model": "Model B weighted by population", "r_squared": h2_model_b_weighted["r2"], "adjusted_r_squared": h2_model_b_weighted["adj_r2"]},
        {"model": "Partial R^2 for BA+ over Model A", "r_squared": partial_r2, "adjusted_r_squared": partial_r2_weighted},
    ])

    h2_diagnostics = pd.DataFrame([
        {"metric": "Partial R^2 for BA+ (unweighted)", "value": partial_r2},
        {"metric": "Partial R^2 for BA+ (population weighted)", "value": partial_r2_weighted},
        {"metric": "Partial R^2 for BA+ over occupation model", "value": occupation_partial_r2},
        {"metric": "Added-variable F statistic for BA+", "value": added_variable_f},
        {"metric": "Max VIF in Model B", "value": h2_vif["vif"].replace(np.inf, np.nan).max()},
    ])

    h2_top_positive_residuals = h2_base.sort_values(["attainment_only_residual", "cbsa_name"], ascending=[False, True]).head(20)[[
        "cbsa_name", "e_m", "attainment_measure", "attainment_only_fitted", "attainment_only_residual",
        "industry_share_professional", "industry_share_information", "industry_share_finance_real",
    ]]
    h2_top_negative_residuals = h2_base.sort_values(["attainment_only_residual", "cbsa_name"], ascending=[True, True]).head(20)[[
        "cbsa_name", "e_m", "attainment_measure", "attainment_only_fitted", "attainment_only_residual",
        "industry_share_professional", "industry_share_information", "industry_share_finance_real",
    ]]

    return (
        h2_attainment_summary,
        h2_base,
        h2_diagnostics,
        h2_eta_summary,
        h2_regression_summary,
        h2_top_negative_residuals,
        h2_top_positive_residuals,
        h2_vif,
        regression_cols,
    )


@app.cell
def _(h2_attainment_summary, h2_diagnostics, h2_eta_summary, h2_regression_summary, h2_vif, table):
    # Put the H2 summary objects up front so the section answers the hypothesis before the plots.
    table(
        h2_attainment_summary,
        page_size=10,
        pagination=False,
        label="H2 attainment field check",
    )
    table(
        h2_eta_summary,
        format_mapping={"eta_squared": "{:.3f}"},
        page_size=10,
        pagination=False,
        label="H2 variance decomposition",
    )
    table(
        h2_regression_summary,
        format_mapping={"r_squared": "{:.3f}", "adjusted_r_squared": "{:.3f}"},
        page_size=10,
        pagination=False,
        label="H2 industry-first regression summary",
    )
    table(
        h2_diagnostics,
        format_mapping={"value": "{:.3f}"},
        page_size=10,
        pagination=False,
        label="H2 diagnostics",
    )
    table(
        h2_vif.head(10),
        format_mapping={"vif": "{:.2f}"},
        page_size=10,
        pagination=False,
        label="H2 VIF check",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### H2 Model Notes

    `VIF` means variance inflation factor. It is a multicollinearity diagnostic: it tells us whether a predictor is mostly duplicating information already carried by the other predictors.

    The residual tables are ranked model misses. We first fit `E_m ~ BA+ share`, then compute:

    `residual = observed E_m - fitted E_m`

    Positive residuals are metros that are more exposed than the simple attainment model predicts. Negative residuals are metros that are less exposed than the model predicts.
    """)
    return


@app.cell
def _(h2_base, np, plt):
    # Lead H2 with the simple relationship before moving to the within-tier spread.
    _fig, _ax = plt.subplots(figsize=(7.5, 6))
    _ax.scatter(h2_base["attainment_measure"], h2_base["e_m"], alpha=0.65, s=22)
    _scatter_fit = np.polyfit(h2_base["attainment_measure"], h2_base["e_m"], 1)
    _x_grid = np.linspace(h2_base["attainment_measure"].min(), h2_base["attainment_measure"].max(), 200)
    _ax.plot(_x_grid, _scatter_fit[0] * _x_grid + _scatter_fit[1], color="black", linewidth=1)
    _ax.set_title("H2: BA+ share versus metro AI exposure")
    _ax.set_xlabel("BA+ share")
    _ax.set_ylabel("E_m")
    _ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(h2_base, np, plt):
    # Then show how much exposure variation still survives once metros are grouped by attainment.
    _quartile_order = [label for label in ["Q1 lowest BA+", "Q2", "Q3", "Q4 highest BA+"] if label in set(h2_base["attainment_quartile"].astype(str))]
    _grouped_values = [
        h2_base.loc[h2_base["attainment_quartile"].astype(str) == label, "e_m"].to_numpy()
        for label in _quartile_order
    ]
    _fig, _ax = plt.subplots(figsize=(9, 5))
    _ax.boxplot(_grouped_values, tick_labels=_quartile_order, patch_artist=False)
    for _x_pos, _label in enumerate(_quartile_order, start=1):
        _group = h2_base.loc[h2_base["attainment_quartile"].astype(str) == _label, "e_m"]
        _jitter = np.random.default_rng(42).uniform(-0.12, 0.12, len(_group))
        _ax.scatter(np.full(len(_group), _x_pos) + _jitter, _group, alpha=0.35, s=14)
    _ax.set_title("H2: Exposure spread within BA+ tiers")
    _ax.set_xlabel("Attainment quartile")
    _ax.set_ylabel("E_m")
    _ax.grid(alpha=0.2, axis="y")
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(dataframe, h2_top_negative_residuals, h2_top_positive_residuals):
    # Residual tables are the best H2 error detector because they force us to explain the metros
    # that sit far from a simple attainment story.
    dataframe(
        h2_top_positive_residuals,
        format_mapping={
            "e_m": "{:.3f}",
            "attainment_measure": "{:.1%}",
            "attainment_only_fitted": "{:.3f}",
            "attainment_only_residual": "{:.3f}",
            "industry_share_professional": "{:.1%}",
            "industry_share_information": "{:.1%}",
            "industry_share_finance_real": "{:.1%}",
        },
        page_size=20,
        label="H2 metros most over-exposed relative to attainment alone",
    )
    dataframe(
        h2_top_negative_residuals,
        format_mapping={
            "e_m": "{:.3f}",
            "attainment_measure": "{:.1%}",
            "attainment_only_fitted": "{:.3f}",
            "attainment_only_residual": "{:.3f}",
            "industry_share_professional": "{:.1%}",
            "industry_share_information": "{:.1%}",
            "industry_share_finance_real": "{:.1%}",
        },
        page_size=20,
        label="H2 metros most under-exposed relative to attainment alone",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. H3 Exposure Level Versus Exposure Shape

    H3 asks whether metros with similar headline `E_m` can still have materially different exposure shapes. The primary construction uses detailed SOC occupations and defines the exposed set as the top quartile of detailed Felten scores; a major-group sensitivity run checks whether that conclusion depends on granularity.
    """)
    return


@app.cell
def _(latest_soc_year, np, pd, soc_cbsa_scored, soc_latest):
    # Build concentration on the latest detailed SOC surface first, then rerun the same idea at
    # the SOC major-group level to see whether H3 is robust to a broader aggregation choice.
    h3_detail = soc_cbsa_scored.loc[
        (soc_cbsa_scored["year"] == latest_soc_year) & soc_cbsa_scored["matched_flag"]
    ].copy()
    h3_detail["soc_major_group"] = h3_detail["soc_code"].str.slice(0, 2)
    h3_detail["felten_weighted_employment"] = h3_detail["employment"] * h3_detail["felten_score"]

    detailed_score_reference = (
        h3_detail[["soc_code", "felten_score"]]
        .dropna()
        .drop_duplicates(subset=["soc_code"])
        .copy()
    )
    detailed_exposure_threshold = detailed_score_reference["felten_score"].quantile(0.75)
    exposed_soc_codes = set(
        detailed_score_reference.loc[
            detailed_score_reference["felten_score"] >= detailed_exposure_threshold, "soc_code"
        ]
    )

    h3_detail["is_exposed_detailed"] = h3_detail["soc_code"].isin(exposed_soc_codes)
    exposed_detail = h3_detail.loc[h3_detail["is_exposed_detailed"]].copy()
    exposed_detail["metro_exposed_employment_share"] = exposed_detail["employment"] / exposed_detail.groupby(
        ["cbsa_code", "cbsa_name", "year"]
    )["employment"].transform("sum")

    h3_detailed_concentration = (
        exposed_detail.groupby(["cbsa_code", "cbsa_name", "year"], as_index=False)
        .agg(
            exposed_employment=("employment", "sum"),
            exposed_occupation_count=("soc_code", "nunique"),
            exposed_employment_hhi=("metro_exposed_employment_share", lambda values: float(np.sum(values ** 2))),
        )
    )
    h3_detailed_concentration = h3_detailed_concentration.rename(columns={"year": "soc_exposure_year"})
    h3_detailed_concentration["effective_exposed_occupation_count"] = 1 / h3_detailed_concentration["exposed_employment_hhi"]

    major_group_reference = (
        h3_detail.groupby("soc_major_group", as_index=False)
        .agg(
            employment=("employment", "sum"),
            weighted_score_component=("felten_weighted_employment", "sum"),
        )
    )
    major_group_reference["major_group_felten_score"] = major_group_reference["weighted_score_component"] / major_group_reference["employment"]
    major_group_exposure_threshold = major_group_reference["major_group_felten_score"].quantile(0.75)
    exposed_major_groups = set(
        major_group_reference.loc[
            major_group_reference["major_group_felten_score"] >= major_group_exposure_threshold, "soc_major_group"
        ]
    )

    h3_major_group_detail = (
        h3_detail.groupby(["cbsa_code", "cbsa_name", "year", "soc_major_group"], as_index=False)
        .agg(employment=("employment", "sum"))
    )
    h3_major_group_detail["is_exposed_major_group"] = h3_major_group_detail["soc_major_group"].isin(exposed_major_groups)
    exposed_major_group_detail = h3_major_group_detail.loc[h3_major_group_detail["is_exposed_major_group"]].copy()
    exposed_major_group_detail["metro_exposed_employment_share"] = exposed_major_group_detail["employment"] / exposed_major_group_detail.groupby(
        ["cbsa_code", "cbsa_name", "year"]
    )["employment"].transform("sum")

    h3_major_group_concentration = (
        exposed_major_group_detail.groupby(["cbsa_code", "cbsa_name", "year"], as_index=False)
        .agg(
            exposed_employment_major_group=("employment", "sum"),
            exposed_major_group_count=("soc_major_group", "nunique"),
            exposed_major_group_hhi=("metro_exposed_employment_share", lambda values: float(np.sum(values ** 2))),
        )
    )
    h3_major_group_concentration = h3_major_group_concentration.rename(columns={"year": "soc_exposure_year"})
    h3_major_group_concentration["effective_exposed_major_group_count"] = 1 / h3_major_group_concentration["exposed_major_group_hhi"]

    h3_base = soc_latest.merge(
        h3_detailed_concentration,
        on=["cbsa_code", "cbsa_name", "soc_exposure_year"],
        how="left",
        validate="one_to_one",
    ).merge(
        h3_major_group_concentration,
        on=["cbsa_code", "cbsa_name", "soc_exposure_year"],
        how="left",
        validate="one_to_one",
    )

    h3_base["e_m_quartile"] = pd.qcut(
        h3_base["e_m"],
        q=4,
        labels=["Q1 lowest exposure", "Q2", "Q3", "Q4 highest exposure"],
        duplicates="drop",
    )

    h3_spread_summary = pd.DataFrame([
        {
            "metric": "Detailed-SOC exposed set threshold",
            "value": detailed_exposure_threshold,
        },
        {
            "metric": "Detailed exposed occupations",
            "value": len(exposed_soc_codes),
        },
        {
            "metric": "Major-group exposed set threshold",
            "value": major_group_exposure_threshold,
        },
        {
            "metric": "Exposed major groups",
            "value": len(exposed_major_groups),
        },
    ])

    h3_quartile_spread = (
        h3_base.groupby("e_m_quartile", observed=True, as_index=False)
        .agg(
            metros=("cbsa_code", "count"),
            detailed_hhi_min=("exposed_employment_hhi", "min"),
            detailed_hhi_median=("exposed_employment_hhi", "median"),
            detailed_hhi_max=("exposed_employment_hhi", "max"),
            detailed_hhi_iqr=("exposed_employment_hhi", lambda values: float(values.quantile(0.75) - values.quantile(0.25))),
            major_group_hhi_median=("exposed_major_group_hhi", "median"),
            major_group_hhi_iqr=("exposed_major_group_hhi", lambda values: float(values.quantile(0.75) - values.quantile(0.25))),
        )
    )

    h3_example_low = (
        h3_base.sort_values(["e_m_quartile", "exposed_employment_hhi", "cbsa_name"], ascending=[True, True, True])
        .groupby("e_m_quartile", observed=True, group_keys=False)
        .head(3)
        .assign(example_type="Lowest concentration in quartile")
    )
    h3_example_high = (
        h3_base.sort_values(["e_m_quartile", "exposed_employment_hhi", "cbsa_name"], ascending=[True, False, True])
        .groupby("e_m_quartile", observed=True, group_keys=False)
        .head(3)
        .assign(example_type="Highest concentration in quartile")
    )
    h3_examples = pd.concat([h3_example_low, h3_example_high], ignore_index=True)[[
        "e_m_quartile", "example_type", "cbsa_name", "e_m", "exposed_employment_hhi",
        "effective_exposed_occupation_count", "exposed_major_group_hhi", "cbsa_detailed_employment",
    ]]

    return h3_base, h3_examples, h3_quartile_spread, h3_spread_summary


@app.cell
def _(h3_quartile_spread, h3_spread_summary, table):
    # H3 begins with the exposed-set definition and the within-quartile dispersion summary so we
    # can see whether concentration meaningfully varies among similarly exposed metros.
    table(
        h3_spread_summary,
        format_mapping={"value": "{:.3f}"},
        page_size=10,
        pagination=False,
        label="H3 exposed-set definition",
    )
    table(
        h3_quartile_spread,
        format_mapping={
            "detailed_hhi_min": "{:.3f}",
            "detailed_hhi_median": "{:.3f}",
            "detailed_hhi_max": "{:.3f}",
            "detailed_hhi_iqr": "{:.3f}",
            "major_group_hhi_median": "{:.3f}",
            "major_group_hhi_iqr": "{:.3f}",
        },
        page_size=10,
        pagination=False,
        label="H3 concentration spread within E_m quartiles",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### H3 Metric Notes

    The H3 concentration metric is a Herfindahl-Hirschman Index (`HHI`) computed inside each metro's exposed occupation set:

    `HHI = sum(exposed occupation employment share^2)`

    Higher `HHI` means the metro's exposed footprint is concentrated in fewer occupations. Lower `HHI` means exposure is spread more diffusely across the exposed set.

    This is computed for the metro universe and then compared within `E_m` quartiles. It is not restricted to only the top `10%` of CBSAs.
    """)
    return


@app.cell
def _(h3_base, plt):
    # Keep the main H3 scatter by itself so the level-versus-shape question is visually isolated.
    _fig, _ax = plt.subplots(figsize=(7.5, 6))
    _size_scale = 6 + 70 * (h3_base["cbsa_detailed_employment"] / h3_base["cbsa_detailed_employment"].max())
    _ax.scatter(
        h3_base["e_m"],
        h3_base["exposed_employment_hhi"],
        s=_size_scale,
        alpha=0.55,
    )
    _ax.set_title("H3: Exposure level versus detailed-SOC concentration")
    _ax.set_xlabel("E_m")
    _ax.set_ylabel("Exposed employment HHI")
    _ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(h3_base, plt):
    # The sensitivity view works better as a percentile-rank comparison because the detailed and
    # major-group HHI measures live on different raw scales.
    _h3_sensitivity = h3_base[["exposed_employment_hhi", "exposed_major_group_hhi"]].dropna().copy()
    _h3_sensitivity["detailed_hhi_percentile"] = _h3_sensitivity["exposed_employment_hhi"].rank(pct=True, method="average")
    _h3_sensitivity["major_group_hhi_percentile"] = _h3_sensitivity["exposed_major_group_hhi"].rank(pct=True, method="average")
    _fig, _ax = plt.subplots(figsize=(7.5, 6))
    _ax.scatter(
        _h3_sensitivity["detailed_hhi_percentile"],
        _h3_sensitivity["major_group_hhi_percentile"],
        s=20,
        alpha=0.6,
    )
    _ax.plot(
        [0, 1],
        [0, 1],
        color="black",
        linewidth=1,
        linestyle="--",
    )
    _ax.set_title("H3 sensitivity: percentile rank of detailed versus major-group HHI")
    _ax.set_xlabel("Detailed-SOC HHI percentile")
    _ax.set_ylabel("Major-group HHI percentile")
    _ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(dataframe, h3_examples):
    # Example metros make the shape argument concrete by showing places that sit in the same
    # headline-exposure band but with very different exposed-footprint concentration.
    dataframe(
        h3_examples,
        format_mapping={
            "e_m": "{:.3f}",
            "exposed_employment_hhi": "{:.3f}",
            "effective_exposed_occupation_count": "{:.1f}",
            "exposed_major_group_hhi": "{:.3f}",
        },
        page_size=24,
        label="H3 example metros with similar E_m but different concentration",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Richmond Hook

    With H1 through H3 built, the remaining notebook work is interpretive rather than structural: place Richmond inside the wage-weighted ranking shifts, the attainment residuals, and the concentration-versus-level space, then decide which of those patterns actually matters for the eventual market writeup.
    """)
    return


if __name__ == "__main__":
    app.run()
