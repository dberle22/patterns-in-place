#!/usr/bin/env python3
"""Build validation visuals for the reusable Act 1 profile query surfaces."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px


# `profile/` sits four directory levels below the monorepo root.  This keeps
# the QA runner aligned with the notebook when resolving the repo `.Renviron`.
REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_DIR = Path(__file__).resolve().parent
QUERY_DIR = ANALYSIS_DIR / "queries"
FIGURE_DIR = ANALYSIS_DIR / "figures"


def load_db_path() -> str:
    """Resolve DB_PATH from the environment or the repo-level .Renviron file."""
    db_path = os.environ.get("DB_PATH", "").strip()
    if db_path:
        return db_path

    renviron_path = REPO_ROOT / ".Renviron"
    if renviron_path.exists():
        for raw_line in renviron_path.read_text().splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "DB_PATH":
                return value.strip()

    raise RuntimeError("DB_PATH is not set and could not be found in .Renviron.")


def read_sql(query_name: str) -> str:
    """Read a query file from the local analysis query folder."""
    query_path = QUERY_DIR / query_name
    return query_path.read_text()


def run_query(con: duckdb.DuckDBPyConnection, sql: str, cbsa_code: str) -> pd.DataFrame:
    """Run a parameterized query by replacing the starter CBSA placeholder."""
    return con.sql(sql.replace("'__CBSA_CODE__'", f"'{cbsa_code}'")).df()


def build_interpretation_candidates(topic_scores_df: pd.DataFrame) -> pd.DataFrame:
    """Rank topic and subject scores so the strongest and weakest surfaces are obvious."""
    scored = topic_scores_df.copy()
    scored["metric_value"] = pd.to_numeric(scored["metric_value"], errors="coerce")
    scored = scored.dropna(subset=["metric_value"])
    scored = scored.sort_values("metric_value", ascending=False).reset_index(drop=True)
    scored["strength_rank"] = scored["metric_value"].rank(ascending=False, method="dense")
    scored["weakness_rank"] = scored["metric_value"].rank(ascending=True, method="dense")
    return scored


def build_frame_percentile_chart(percentiles_df: pd.DataFrame, output_path: Path) -> None:
    """Render a small validation chart for the headline percentile surface."""
    chart_df = percentiles_df.copy()
    chart_df["frame"] = chart_df["frame_id"].str.replace("_", " ").str.title()
    fig = px.bar(
        chart_df,
        x="frame",
        y="percentile_rank",
        text="percentile_rank",
        title=f"{chart_df.loc[0, 'cbsa_name']} frame percentile check",
    )
    fig.update_yaxes(range=[0, 100], title="Percentile rank")
    fig.update_layout(template="plotly_white")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path), include_plotlyjs="cdn")


def build_topic_strength_chart(interpretation_df: pd.DataFrame, output_path: Path) -> None:
    """Render a compact validation chart for topic and subject strengths."""
    top = interpretation_df.head(6)
    bottom = interpretation_df.tail(6)
    chart_df = pd.concat([top, bottom]).copy()
    chart_df["metric_label"] = chart_df["metric_id"].str.replace("_", " ", regex=False)
    fig = px.bar(
        chart_df,
        x="metric_value",
        y="metric_label",
        color="metric_type",
        orientation="h",
        title="Profile topic and subject score check",
    )
    fig.update_layout(template="plotly_white", yaxis_title="")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path), include_plotlyjs="cdn")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cbsa-code", default="40060", help="Target CBSA code.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = load_db_path()
    cbsa_figure_dir = FIGURE_DIR / args.cbsa_code

    with duckdb.connect(db_path, read_only=True) as con:
        identity_df = run_query(con, read_sql("profile_identity.sql"), args.cbsa_code)
        percentiles_df = run_query(con, read_sql("profile_percentiles.sql"), args.cbsa_code)
        topic_scores_df = run_query(con, read_sql("profile_topic_scores.sql"), args.cbsa_code)
        raw_kpis_df = run_query(con, read_sql("profile_raw_kpis.sql"), args.cbsa_code)

    if identity_df.empty or percentiles_df.empty or topic_scores_df.empty or raw_kpis_df.empty:
        raise RuntimeError(f"No profile rows found for cbsa_code={args.cbsa_code}.")

    interpretation_df = build_interpretation_candidates(topic_scores_df)

    build_frame_percentile_chart(percentiles_df, cbsa_figure_dir / "profile_frame_percentiles.html")
    build_topic_strength_chart(interpretation_df, cbsa_figure_dir / "profile_topic_strengths.html")

    print(f"Loaded profile query surfaces for CBSA {args.cbsa_code}:")
    print(f"  identity rows: {len(identity_df)}")
    print(f"  percentile rows: {len(percentiles_df)}")
    print(f"  topic score rows: {len(topic_scores_df)}")
    print(f"  raw KPI rows: {len(raw_kpis_df)}")
    print(f"Wrote profile validation figures to {cbsa_figure_dir}")


if __name__ == "__main__":
    main()
