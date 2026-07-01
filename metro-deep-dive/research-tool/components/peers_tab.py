"""Peers tab — cross-frame + per-frame similarity comparison."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from dd_db import get_cross_frame_peers, get_frame_peers, get_cbsa_key_stats_batch
from components.ui_helpers import pct_rank


def render_peers(cbsa_code: str, cbsa_name: str, cf: dict) -> None:
    st.subheader("Peer Analysis")

    # Three-column per-frame peer tables
    st.markdown("#### Frame-by-Frame Peers")
    fc1, fc2, fc3 = st.columns(3)

    for col, frame in [(fc1, "livability"), (fc2, "opportunity"), (fc3, "character")]:
        with col:
            st.markdown(f"**{frame.title()} Peers**")
            peers = get_frame_peers(cbsa_code, frame)
            if not peers.empty:
                display = peers[["peer_rank", "cbsa_name", "similarity"]].copy()
                display["similarity"] = display["similarity"].map(lambda x: f"{x:.3f}" if x is not None else "—")
                display.columns = ["#", "Metro", "Sim"]
                st.dataframe(display, use_container_width=True, hide_index=True, height=350)
            else:
                st.caption("Unavailable")

    st.divider()

    # Cross-frame peers
    st.markdown("#### Cross-Frame Combined Peers")
    xf_peers = get_cross_frame_peers(cbsa_code)
    if not xf_peers.empty:
        display = xf_peers[["peer_rank", "cbsa_name", "similarity"]].copy()
        display["similarity"] = display["similarity"].map(lambda x: f"{x:.3f}" if x is not None else "—")
        display.columns = ["Rank", "Metro", "Cosine Similarity"]
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.caption("No cross-frame peer data available.")

    st.divider()

    # Diverging peers — similar on one frame, diverge on another
    st.markdown("#### Diverging Peers")
    st.caption(
        "Metros that are cosine-similar on one frame but have the largest percentile gap on another. "
        "These are the most analytically interesting comparisons."
    )

    try:
        _render_diverging_peers(cbsa_code, cbsa_name, xf_peers)
    except Exception as e:
        st.caption(f"Diverging peer analysis unavailable: {e}")

    st.divider()

    # Head-to-head comparison
    st.markdown("#### Head-to-Head Comparison")
    all_peers = pd.concat([
        get_frame_peers(cbsa_code, "livability")[["cbsa_code", "cbsa_name"]],
        get_frame_peers(cbsa_code, "opportunity")[["cbsa_code", "cbsa_name"]],
        get_frame_peers(cbsa_code, "character")[["cbsa_code", "cbsa_name"]],
        xf_peers[["cbsa_code", "cbsa_name"]] if not xf_peers.empty else pd.DataFrame(),
    ], ignore_index=True).drop_duplicates("cbsa_code")

    if not all_peers.empty:
        peer_options = list(zip(all_peers["cbsa_name"] + " (" + all_peers["cbsa_code"] + ")", all_peers["cbsa_code"]))
        peer_labels = [lbl for lbl, _ in peer_options]
        peer_label_to_code = {lbl: code for lbl, code in peer_options}

        selected_peer_label = st.selectbox("Compare against peer metro", options=[""] + peer_labels)
        if selected_peer_label:
            peer_code = peer_label_to_code[selected_peer_label]
            _render_h2h(cbsa_code, cbsa_name, peer_code, selected_peer_label)


def _render_diverging_peers(cbsa_code: str, cbsa_name: str, xf_peers: pd.DataFrame) -> None:
    if xf_peers.empty:
        st.caption("No peers available for divergence analysis.")
        return

    from shared.db import get_connection
    peer_codes = xf_peers["cbsa_code"].tolist()[:10]
    placeholders = ", ".join("?" for _ in peer_codes)

    con = get_connection()
    try:
        peer_profiles = con.execute(f"""
            SELECT
                cbsa_code, cbsa_name,
                livability__livability_percentile AS liv_pct,
                opportunity__opportunity_percentile AS opp_pct,
                character__character_percentile AS char_pct
            FROM mart_intelligence.intelligence_cross_frame
            WHERE cbsa_code IN ({placeholders})
        """, peer_codes).fetchdf()

        selected_row = con.execute("""
            SELECT
                livability__livability_percentile AS liv_pct,
                opportunity__opportunity_percentile AS opp_pct,
                character__character_percentile AS char_pct
            FROM mart_intelligence.intelligence_cross_frame
            WHERE cbsa_code = ?
        """, [cbsa_code]).fetchone()
    finally:
        con.close()

    if peer_profiles.empty or not selected_row:
        return

    sel_liv, sel_opp, sel_char = selected_row

    # Fetch key stats for all peers
    all_codes = peer_codes + [cbsa_code]
    stats_df = get_cbsa_key_stats_batch(all_codes)
    stats_index = stats_df.set_index("cbsa_code") if not stats_df.empty else pd.DataFrame()

    def _stat(code: str, col: str, fmt: str = "") -> str:
        if stats_index.empty or code not in stats_index.index:
            return "—"
        v = stats_index.loc[code, col] if col in stats_index.columns else None
        if v is None or pd.isna(v):
            return "—"
        if fmt == "pop":
            return f"{v:,.0f}"
        if fmt == "income":
            return f"${v:,.0f}"
        if fmt == "pct":
            return f"{v * 100:.1f}%"
        return f"{v:.1f}"

    rows = []
    for _, r in peer_profiles.iterrows():
        code = r["cbsa_code"]
        max_gap = max(
            abs((r["liv_pct"] or 0) - (sel_liv or 0)),
            abs((r["opp_pct"] or 0) - (sel_opp or 0)),
            abs((r["char_pct"] or 0) - (sel_char or 0)),
        )
        rows.append({
            "Metro": r["cbsa_name"],
            "Liv": f"{r['liv_pct']:.0f}" if r["liv_pct"] is not None else "—",
            "Opp": f"{r['opp_pct']:.0f}" if r["opp_pct"] is not None else "—",
            "Char": f"{r['char_pct']:.0f}" if r["char_pct"] is not None else "—",
            "Population": _stat(code, "pop_total", "pop"),
            "Med HH Income": _stat(code, "median_hh_income", "income"),
            "5yr Growth": _stat(code, "pop_growth_5yr", "pct"),
            "Max Gap": f"{max_gap:.0f}",
        })

    rows.sort(key=lambda x: float(x["Max Gap"]) if x["Max Gap"] != "—" else -1, reverse=True)
    rows.insert(0, {
        "Metro": f"★ {cbsa_name}",
        "Liv": f"{sel_liv:.0f}" if sel_liv else "—",
        "Opp": f"{sel_opp:.0f}" if sel_opp else "—",
        "Char": f"{sel_char:.0f}" if sel_char else "—",
        "Population": _stat(cbsa_code, "pop_total", "pop"),
        "Med HH Income": _stat(cbsa_code, "median_hh_income", "income"),
        "5yr Growth": _stat(cbsa_code, "pop_growth_5yr", "pct"),
        "Max Gap": "—",
    })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_h2h(code_a: str, name_a: str, code_b: str, name_b: str) -> None:
    from shared.db import get_connection
    con = get_connection()
    try:
        df = con.execute("""
            SELECT
                cbsa_code, cbsa_name,
                livability__livability_percentile AS liv_pct,
                opportunity__opportunity_percentile AS opp_pct,
                character__character_percentile AS char_pct,
                livability__livability_cluster_name AS liv_cluster,
                opportunity__opportunity_cluster_name AS opp_cluster,
                character__character_cluster_name AS char_cluster,
                cross_frame_cluster_name AS xf_cluster,
                cross_frame_percentile AS xf_pct
            FROM mart_intelligence.intelligence_cross_frame
            WHERE cbsa_code IN (?, ?)
        """, [code_a, code_b]).fetchdf()
    finally:
        con.close()

    if df.empty or len(df) < 2:
        st.caption("Could not load comparison data.")
        return

    a = df[df["cbsa_code"] == code_a].iloc[0]
    b = df[df["cbsa_code"] == code_b].iloc[0]

    # Key stats
    stats_df = get_cbsa_key_stats_batch([code_a, code_b])
    stats_idx = stats_df.set_index("cbsa_code") if not stats_df.empty else pd.DataFrame()

    def _kstat(code: str, col: str, fmt: str = "") -> str:
        if stats_idx.empty or code not in stats_idx.index:
            return "—"
        v = stats_idx.loc[code, col] if col in stats_idx.columns else None
        if v is None or pd.isna(v):
            return "—"
        if fmt == "pop":
            return f"{v:,.0f}"
        if fmt == "income":
            return f"${v:,.0f}"
        if fmt == "pct":
            return f"{v * 100:.1f}%"
        if fmt == "ratio":
            return f"{v:.1f}×"
        return f"{v:.1f}"

    name_a_short = name_a.split(",")[0]
    name_b_short = name_b.split(",")[0]

    rows = [
        # Intelligence frame percentiles
        {"Dimension": "Livability Percentile", name_a_short: f"{a['liv_pct']:.0f}th" if a['liv_pct'] else "—", name_b_short: f"{b['liv_pct']:.0f}th" if b['liv_pct'] else "—"},
        {"Dimension": "Opportunity Percentile", name_a_short: f"{a['opp_pct']:.0f}th" if a['opp_pct'] else "—", name_b_short: f"{b['opp_pct']:.0f}th" if b['opp_pct'] else "—"},
        {"Dimension": "Character Percentile", name_a_short: f"{a['char_pct']:.0f}th" if a['char_pct'] else "—", name_b_short: f"{b['char_pct']:.0f}th" if b['char_pct'] else "—"},
        {"Dimension": "Cross-Frame Percentile", name_a_short: f"{a['xf_pct']:.0f}th" if a['xf_pct'] else "—", name_b_short: f"{b['xf_pct']:.0f}th" if b['xf_pct'] else "—"},
        # Clusters
        {"Dimension": "Livability Cluster", name_a_short: a['liv_cluster'] or "—", name_b_short: b['liv_cluster'] or "—"},
        {"Dimension": "Opportunity Cluster", name_a_short: a['opp_cluster'] or "—", name_b_short: b['opp_cluster'] or "—"},
        {"Dimension": "Character Cluster", name_a_short: a['char_cluster'] or "—", name_b_short: b['char_cluster'] or "—"},
        {"Dimension": "Cross-Frame Type", name_a_short: a['xf_cluster'] or "—", name_b_short: b['xf_cluster'] or "—"},
        # Key stats
        {"Dimension": "Population", name_a_short: _kstat(code_a, "pop_total", "pop"), name_b_short: _kstat(code_b, "pop_total", "pop")},
        {"Dimension": "Median Age", name_a_short: _kstat(code_a, "median_age"), name_b_short: _kstat(code_b, "median_age")},
        {"Dimension": "5yr Pop Growth", name_a_short: _kstat(code_a, "pop_growth_5yr", "pct"), name_b_short: _kstat(code_b, "pop_growth_5yr", "pct")},
        {"Dimension": "Median HH Income", name_a_short: _kstat(code_a, "median_hh_income", "income"), name_b_short: _kstat(code_b, "median_hh_income", "income")},
        {"Dimension": "Home Value / Income", name_a_short: _kstat(code_a, "value_to_income", "ratio"), name_b_short: _kstat(code_b, "value_to_income", "ratio")},
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
