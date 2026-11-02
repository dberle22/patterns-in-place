#!/usr/bin/env python3
"""IRS direction fix rerun (2026-10): compare control and fixed outputs.

Usage, from the repository root, after the control and fixed runs of
irs_fix_rerun_phase.R (phases 2, 4, 5) and irs_fix_rerun_engine.py:
    .venv-marimo/bin/python exploration/intelligence_framework/irs_fix_rerun_2026-10/irs_fix_rerun_compare.py [gdp_frozen]

With gdp_frozen, compares control_gdp_frozen and fixed_gdp_frozen (the
promotion runs) for Opportunity, cross-frame and the engine; Character has no
GDP input and always uses control and fixed. Detail tables go to compare_gdp_frozen/.

Control and fixed share every input except the IRS columns, so any difference
here is the effect of the fix alone. Prints a summary and writes the detail
tables to irs_fix_rerun_2026-10/compare/ for IRS_FIX_RERUN_REVIEW.md.

Spec: foundations/etl/IRS_MIGRATION_DIRECTION_FIX_SPEC.md, Part B step 10.
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
FRAMEWORK = REPO_ROOT / "exploration" / "intelligence_framework"
RERUN = "outputs_irs_fix_2026-10"
SUFFIX = "_gdp_frozen" if sys.argv[1:] == ["gdp_frozen"] else ""
OUT = Path(__file__).resolve().parent / f"compare{SUFFIX}"
ENGINE = REPO_ROOT / "metro-deep-dive-program" / "engines" / "time_series" / RERUN
ENGINE_CONTROL, ENGINE_FIXED = f"control{SUFFIX}", f"fixed{SUFFIX}"
ALBANY = "10580"

# One entry per clustered frame: where its outputs live and what they're called.
FRAMES = {
    "character": {
        "dir": FRAMEWORK / "phase_2_character_calibration" / RERUN,
        "scores": "character_scores.parquet",
        "peers": "character_phase2_similarity_top10.csv",
        "extremes": "character_phase2_cluster_metric_extremes.csv",
        "score": "character_score",
        "percentile": "character_percentile",
        "clusters": ["character_hclust_cluster", "character_kmeans_cluster", "character_gmm_cluster", "character_cluster_name"],
        "topics": ["topic_score_residential_stability", "subject_score_demographics"],
    },
    "opportunity": {
        "dir": FRAMEWORK / "phase_4_opportunity_calibration" / RERUN,
        "scores": "opportunity_scores.parquet",
        "peers": "opportunity_phase4_similarity_top10.csv",
        "extremes": "opportunity_phase4_cluster_metric_extremes.csv",
        "score": "opportunity_score",
        "percentile": "opportunity_percentile",
        "clusters": ["opportunity_hclust_cluster", "opportunity_kmeans_cluster", "opportunity_gmm_cluster", "opportunity_cluster_label", "opportunity_cluster_name"],
        "topics": ["topic_score_migration_and_wealth_flows", "subject_score_market_opportunity", "subject_score_resident_opportunity"],
    },
    "cross_frame": {
        "dir": FRAMEWORK / "phase_5_cross_frame_integration" / RERUN,
        "scores": "cross_frame_scores.parquet",
        "peers": "cross_frame_phase5_similarity_top10.csv",
        "extremes": "cross_frame_phase5_cluster_metric_extremes.csv",
        "score": "cross_frame_score",
        "percentile": "cross_frame_percentile",
        "clusters": ["cross_frame_hclust_cluster", "cross_frame_kmeans_cluster", "cross_frame_gmm_cluster", "cross_frame_cluster_label", "cross_frame_cluster_name"],
        "topics": [],
    },
}


def read(frame: dict, mode: str, name: str) -> pd.DataFrame:
    folder = mode if frame["dir"].parent.name == "phase_2_character_calibration" else f"{mode}{SUFFIX}"
    path = frame["dir"] / folder / name
    return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path, dtype={"cbsa_code": str})


def compare_clusters(frame_id: str, frame: dict) -> list[dict]:
    """Assignment agreement per clustering method, and k per method."""

    ctl = read(frame, "control", frame["scores"]).set_index("cbsa_code")
    fix = read(frame, "fixed", frame["scores"]).set_index("cbsa_code")
    rows = []
    for col in frame["clusters"]:
        if col not in ctl.columns:
            continue
        same = (ctl[col].astype(str) == fix.loc[ctl.index, col].astype(str)).mean()
        rows.append({
            "frame": frame_id,
            "cluster_column": col,
            "agreement_pct": round(100 * same, 2),
            "k_control": ctl[col].nunique(),
            "k_fixed": fix[col].nunique(),
            "albany_control": ctl.loc[ALBANY, col],
            "albany_fixed": fix.loc[ALBANY, col],
        })
    return rows


def compare_peers(frame_id: str, frame: dict) -> tuple[dict, pd.DataFrame]:
    """Share of metros whose ordered top-10 peer list is unchanged."""

    ctl = read(frame, "control", frame["peers"])
    fix = read(frame, "fixed", frame["peers"])
    # Column names differ a little by phase; find the anchor, rank and peer code.
    anchor, rank, peer = ctl.columns[0], ctl.columns[2], ctl.columns[3]
    sim = ctl.columns[-1]

    def lists(df: pd.DataFrame) -> pd.Series:
        return df.sort_values([anchor, rank]).groupby(anchor)[peer].apply(tuple)

    lc, lf = lists(ctl), lists(fix)
    joined = pd.concat([lc.rename("control"), lf.rename("fixed")], axis=1)
    merged = ctl.merge(fix, on=[anchor, rank], suffixes=("_control", "_fixed"))
    summary = {
        "frame": frame_id,
        "metros": len(joined),
        "ordered_list_unchanged_pct": round(100 * (joined["control"] == joined["fixed"]).mean(), 2),
        "peer_set_unchanged_pct": round(100 * joined.apply(lambda r: set(r["control"]) == set(r["fixed"]), axis=1).mean(), 2),
        "max_abs_similarity_change": float((merged[f"{sim}_control"] - merged[f"{sim}_fixed"]).abs().max()),
    }
    albany = merged[merged[anchor].astype(str) == ALBANY].assign(frame=frame_id)
    return summary, albany


def compare_extremes(frame_id: str, frame: dict) -> pd.DataFrame:
    """Top and bottom metric lists per cluster, control vs fixed."""

    ctl = read(frame, "control", frame["extremes"]).assign(run="control")
    fix = read(frame, "fixed", frame["extremes"]).assign(run="fixed")
    both = pd.concat([ctl, fix])
    cluster_col, metric_col, side_col = both.columns[0], both.columns[1], both.columns[3]
    sets = both.groupby(["run", cluster_col, side_col])[metric_col].apply(lambda s: tuple(sorted(s))).unstack("run").reset_index()
    sets["changed"] = sets["control"] != sets["fixed"]
    sets["irs_in_control"] = sets["control"].apply(lambda t: [m for m in t if m.startswith("irs_")])
    sets["irs_in_fixed"] = sets["fixed"].apply(lambda t: [m for m in t if m.startswith("irs_")])
    sets.insert(0, "frame", frame_id)
    return sets


def compare_scores(frame_id: str, frame: dict) -> tuple[list[dict], pd.DataFrame]:
    """Percentile movement for the frame score and the IRS-bearing topic scores."""

    ctl = read(frame, "control", frame["scores"]).set_index("cbsa_code")
    fix = read(frame, "fixed", frame["scores"]).set_index("cbsa_code")
    rows, movers = [], []
    for col in [frame["percentile"], frame["score"], *frame["topics"]]:
        # Percentiles are already 0-100; rank scores to percentiles so every
        # column is compared on the same points scale.
        if col == frame["percentile"]:
            c, f = ctl[col], fix.loc[ctl.index, col]
        else:
            c, f = ctl[col].rank(pct=True) * 100, fix.loc[ctl.index, col].rank(pct=True) * 100
        change = f - c
        rows.append({
            "frame": frame_id,
            "column": col,
            "basis": "percentile" if col == frame["percentile"] else "rank percentile of score",
            "median_abs_change_pts": round(change.abs().median(), 2),
            "share_moving_gt_10pts_pct": round(100 * (change.abs() > 10).mean(), 1),
            "max_abs_change_pts": round(change.abs().max(), 1),
            "albany_control": round(c.loc[ALBANY], 1),
            "albany_fixed": round(f.loc[ALBANY], 1),
        })
        if col == frame["percentile"]:
            m = pd.DataFrame({"cbsa_name": ctl["cbsa_name"], "control": c, "fixed": f, "change": change})
            m = pd.concat([m.nlargest(20, "change").assign(direction="up"), m.nsmallest(20, "change").assign(direction="down")])
            movers.append(m.reset_index().assign(frame=frame_id))
    return rows, pd.concat(movers)


def compare_trajectory() -> dict[str, pd.DataFrame]:
    """Trajectory label, tier and turn-status changes, and IRS metric direction flips."""

    con = duckdb.connect()
    out = {}
    out["frame_changes"] = con.sql(f"""
        select c.frame_id, c.window_name, count(*) as cbsas,
               count(*) filter (where c.trajectory_label is distinct from f.trajectory_label) as label_changed,
               count(*) filter (where c.movement_direction is distinct from f.movement_direction) as direction_changed,
               count(*) filter (where c.signal_tier is distinct from f.signal_tier) as tier_changed,
               round(median(abs(f.trajectory_salience_percentile - c.trajectory_salience_percentile)), 2) as median_abs_salience_change,
               round(max(abs(f.frame_momentum_score - c.frame_momentum_score)), 3) as max_abs_momentum_change
        from '{ENGINE / ENGINE_CONTROL / "intelligence_trajectory_frame.parquet"}' c
        join '{ENGINE / ENGINE_FIXED / "intelligence_trajectory_frame.parquet"}' f using (cbsa_code, frame_id, window_name)
        group by 1, 2 order by 1, 2
    """).df()
    out["frame_movers"] = con.sql(f"""
        select c.cbsa_code, c.cbsa_name, c.frame_id, c.window_name,
               c.trajectory_label as label_control, f.trajectory_label as label_fixed,
               round(c.trajectory_salience_percentile, 1) as salience_control,
               round(f.trajectory_salience_percentile, 1) as salience_fixed,
               round(f.frame_momentum_score - c.frame_momentum_score, 3) as momentum_change
        from '{ENGINE / ENGINE_CONTROL / "intelligence_trajectory_frame.parquet"}' c
        join '{ENGINE / ENGINE_FIXED / "intelligence_trajectory_frame.parquet"}' f using (cbsa_code, frame_id, window_name)
        where c.trajectory_label is distinct from f.trajectory_label
           or abs(f.frame_momentum_score - c.frame_momentum_score) > 0
        order by abs(f.frame_momentum_score - c.frame_momentum_score) desc
    """).df()
    out["turn_changes"] = con.sql(f"""
        select c.frame_id, c.turn_status as status_control, f.turn_status as status_fixed, count(*) as cbsas
        from '{ENGINE / ENGINE_CONTROL / "intelligence_trajectory_turn_signals.parquet"}' c
        join '{ENGINE / ENGINE_FIXED / "intelligence_trajectory_turn_signals.parquet"}' f using (cbsa_code, frame_id)
        group by 1, 2, 3 order by 1, 4 desc
    """).df()
    out["turn_changed_cbsas"] = con.sql(f"""
        select c.cbsa_code, c.cbsa_name, c.frame_id, c.turn_status as status_control, f.turn_status as status_fixed
        from '{ENGINE / ENGINE_CONTROL / "intelligence_trajectory_turn_signals.parquet"}' c
        join '{ENGINE / ENGINE_FIXED / "intelligence_trajectory_turn_signals.parquet"}' f using (cbsa_code, frame_id)
        where c.turn_status is distinct from f.turn_status
        order by c.cbsa_name
    """).df()
    out["irs_metric_changes"] = con.sql(f"""
        select c.metric_id, c.window_name, count(*) as cbsas,
               count(*) filter (where c.absolute_direction is distinct from f.absolute_direction) as direction_changed,
               count(*) filter (where c.signal_tier is distinct from f.signal_tier) as tier_changed,
               count(*) filter (where c.end_raw_value is not distinct from -f.end_raw_value) as end_value_negated
        from '{ENGINE / ENGINE_CONTROL / "intelligence_trajectory_metric.parquet"}' c
        join '{ENGINE / ENGINE_FIXED / "intelligence_trajectory_metric.parquet"}' f using (cbsa_code, metric_id, window_name)
        where c.source_column like 'irs_%'
        group by 1, 2 order by 1, 2
    """).df()
    out["non_irs_metric_rows_changed"] = con.sql(f"""
        select count(*) as rows_changed
        from '{ENGINE / ENGINE_CONTROL / "intelligence_trajectory_metric.parquet"}' c
        join '{ENGINE / ENGINE_FIXED / "intelligence_trajectory_metric.parquet"}' f using (cbsa_code, metric_id, window_name)
        where c.source_column not like 'irs_%'
          and (c.end_raw_value is distinct from f.end_raw_value or c.momentum_percentile is distinct from f.momentum_percentile)
    """).df()
    out["albany"] = con.sql(f"""
        select c.frame_id, c.window_name, c.trajectory_label as label_control, f.trajectory_label as label_fixed,
               round(c.trajectory_salience_percentile, 1) as salience_control, round(f.trajectory_salience_percentile, 1) as salience_fixed
        from '{ENGINE / ENGINE_CONTROL / "intelligence_trajectory_frame.parquet"}' c
        join '{ENGINE / ENGINE_FIXED / "intelligence_trajectory_frame.parquet"}' f using (cbsa_code, frame_id, window_name)
        where c.cbsa_code = '{ALBANY}' order by 1, 2
    """).df()
    return out


def main() -> None:
    OUT.mkdir(exist_ok=True)
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)

    clusters, peers, albany_peers, extremes, scores, movers = [], [], [], [], [], []
    for frame_id, frame in FRAMES.items():
        clusters += compare_clusters(frame_id, frame)
        p, a = compare_peers(frame_id, frame)
        peers.append(p)
        albany_peers.append(a)
        extremes.append(compare_extremes(frame_id, frame))
        s, m = compare_scores(frame_id, frame)
        scores += s
        movers.append(m)

    tables = {
        "clusters": pd.DataFrame(clusters),
        "peers": pd.DataFrame(peers),
        "albany_peers": pd.concat(albany_peers),
        "cluster_extremes": pd.concat(extremes),
        "scores": pd.DataFrame(scores),
        "score_movers": pd.concat(movers),
        **{f"trajectory_{k}": v for k, v in compare_trajectory().items()},
    }
    for name, table in tables.items():
        table.to_csv(OUT / f"{name}.csv", index=False)

    for name in ["clusters", "peers", "scores", "trajectory_frame_changes", "trajectory_turn_changes",
                 "trajectory_irs_metric_changes", "trajectory_non_irs_metric_rows_changed", "trajectory_albany"]:
        print(f"\n== {name}")
        print(tables[name].to_string(index=False))
    changed = tables["cluster_extremes"]
    print("\n== cluster_extremes: lists that changed")
    print(changed[changed["changed"]].to_string(index=False))
    print(f"\nDetail tables written to {OUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
