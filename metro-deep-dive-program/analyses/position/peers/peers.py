#!/usr/bin/env python3
"""Build validation visuals from reusable peer query surfaces."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px


REPO_ROOT = Path(__file__).resolve().parents[4]
ANALYSIS_DIR = Path(__file__).resolve().parent
QUERY_DIR = ANALYSIS_DIR / "queries"
FIGURE_DIR = ANALYSIS_DIR / "figures"


def load_db_path() -> str:
    """Resolve DB_PATH from the environment or repo-level .Renviron."""
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
    return (QUERY_DIR / query_name).read_text()


def run_query(con: duckdb.DuckDBPyConnection, sql: str, cbsa_code: str) -> pd.DataFrame:
    """Run a parameterized query by replacing the starter CBSA placeholder."""
    return con.sql(sql.replace("'__CBSA_CODE__'", f"'{cbsa_code}'")).df()


def build_similarity_chart(peer_list_long: pd.DataFrame, output_path: Path) -> None:
    """Render a simple chart to inspect whether the cross-frame ranking looks reasonable."""
    cross_frame = peer_list_long[peer_list_long["peer_type"] == "cross_frame"].copy().head(10)
    fig = px.bar(
        cross_frame,
        x="similarity",
        y="peer_cbsa_name",
        orientation="h",
        text="similarity",
        title="Cross-frame peer similarity check",
    )
    fig.update_layout(template="plotly_white", yaxis_title="")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path), include_plotlyjs="cdn")


def build_compare_heatmap(compare_df: pd.DataFrame, output_path: Path) -> None:
    """Render a compact percentile heatmap for the target metro and selected peers."""
    heatmap_df = compare_df.melt(
        id_vars=["cbsa_code", "cbsa_name"],
        value_vars=[
            "character_percentile_rank",
            "livability_percentile_rank",
            "opportunity_percentile_rank",
            "cross_frame_percentile_rank",
        ],
        var_name="metric_id",
        value_name="metric_value",
    )
    fig = px.density_heatmap(
        heatmap_df,
        x="metric_id",
        y="cbsa_name",
        z="metric_value",
        text_auto=True,
        color_continuous_scale="Blues",
        title="Peer percentile comparison check",
    )
    fig.update_layout(template="plotly_white", xaxis_title="", yaxis_title="")
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
        peer_list_long = run_query(con, read_sql("peer_list.sql"), args.cbsa_code)
        peer_compare_surface = run_query(con, read_sql("peer_benchmark_top5.sql"), args.cbsa_code)

    if peer_list_long.empty or peer_compare_surface.empty:
        raise RuntimeError(f"No peer rows found for cbsa_code={args.cbsa_code}.")

    build_similarity_chart(peer_list_long, cbsa_figure_dir / "peer_similarity_bars.html")
    build_compare_heatmap(peer_compare_surface, cbsa_figure_dir / "peer_compare_heatmap.html")

    print(f"Loaded peer query surfaces for CBSA {args.cbsa_code}:")
    print(f"  peer rows: {len(peer_list_long)}")
    print(f"  benchmark rows: {len(peer_compare_surface)}")
    print(f"Wrote peer validation figures to {cbsa_figure_dir}")


if __name__ == "__main__":
    main()
