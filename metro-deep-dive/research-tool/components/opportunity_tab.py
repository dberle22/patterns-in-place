"""Opportunity frame tab."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from components.frame_tab_base import render_frame_tab
from components.ui_helpers import fmt_num
from dd_db import get_industry_profile, get_occupation_profile


def _oz_section(cbsa_code: str) -> None:
    """Show Opportunity Zone exposure from gold.dim_policy_designations."""
    try:
        from shared.db import get_connection as gc
        con = gc()
        row = con.execute("""
            SELECT
                pct_oz_tracts,
                pct_population_in_oz,
                oz_tract_count,
                total_tract_count
            FROM gold.dim_policy_designations
            WHERE geo_level = 'cbsa'
              AND geo_id = ?
            LIMIT 1
        """, [cbsa_code]).fetchone()
        con.close()
        if row and row[3] and row[3] > 0:
            pct_tracts, pct_pop, oz_tracts, total_tracts = row
            st.subheader("Opportunity Zone Exposure")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("OZ Tract Share", f"{(pct_tracts or 0) * 100:.1f}%", help=f"{oz_tracts:,} of {total_tracts:,} tracts")
            with c2:
                st.metric("OZ Population Share", f"{(pct_pop or 0) * 100:.1f}%")
    except Exception:
        pass


def _industry_occupation_section(cbsa_code: str) -> None:
    st.subheader("Industry & Occupation Mix")
    with st.expander("What is a Location Quotient (LQ)?", expanded=False):
        st.markdown(
            "**LQ = Metro % ÷ National %**. An LQ of 1.0 means the metro matches the national average "
            "share of employment in that sector. LQ > 1.0 means the sector is over-represented locally "
            "(a regional specialization); LQ < 1.0 means it's under-represented. "
            "For example, LQ of 2.0 means twice the national concentration."
        )

    ind = get_industry_profile(cbsa_code)
    occ = get_occupation_profile(cbsa_code)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Industry Employment Share**")
        if not ind.empty:
            ind_display = ind.copy()
            for pct_col in ["Metro %", "National %"]:
                if pct_col in ind_display.columns:
                    ind_display[pct_col] = ind_display[pct_col].map(
                        lambda x: f"{x:.1f}%" if pd.notna(x) else "—"
                    )
            if "LQ" in ind_display.columns:
                ind_display["LQ"] = ind_display["LQ"].map(
                    lambda x: f"{x:.2f}" if pd.notna(x) else "—"
                )
            st.dataframe(ind_display, use_container_width=True, hide_index=True)
        else:
            st.caption("Industry data unavailable.")

    with col2:
        st.markdown("**Occupation Mix**")
        if not occ.empty:
            occ_display = occ.copy()
            for pct_col in ["Metro %", "National %"]:
                if pct_col in occ_display.columns:
                    occ_display[pct_col] = occ_display[pct_col].map(
                        lambda x: f"{x:.1f}%" if pd.notna(x) else "—"
                    )
            if "LQ" in occ_display.columns:
                occ_display["LQ"] = occ_display["LQ"].map(
                    lambda x: f"{x:.2f}" if pd.notna(x) else "—"
                )
            st.dataframe(occ_display, use_container_width=True, hide_index=True)
        else:
            st.caption("Occupation data unavailable.")


def render_opportunity(cbsa_code: str, cbsa_name: str, p: dict) -> None:
    subjects = {
        "resident_opportunity": p.get("subject_score_resident_opportunity") or p.get("resident_opportunity_score"),
        "market_opportunity": p.get("subject_score_market_opportunity") or p.get("market_opportunity_score"),
        "business_and_industry_opportunity": p.get("subject_score_business_and_industry_opportunity") or p.get("business_and_industry_score"),
    }

    topics = {
        k.replace("topic_score_", ""): v
        for k, v in p.items()
        if k.startswith("topic_score_")
    }

    kpi_cols = [
        "income_pc_growth_5yr", "pct_unemployment_rate", "lfpr",
        "pov_rate_change_5yr", "qcew_private_avg_wkly_wage",
        "hpi_5yr_pct", "hpi_yoy_pct", "zori_annual_avg_yoy_pct",
        "pop_growth_5yr", "irs_net_migration_rate", "irs_net_agi",
        "permits_per_1000_housing_units", "permits_share_units_5_plus",
        "productivity_growth_5yr", "industry_concentration_hhi",
        "bfs_business_application_rate_per_1000_establishments",
        "cbp_estabs_per_1000_residents", "pct_ba_plus_change_5yr",
        "lq_professional", "lq_information", "lq_manufacturing",
        "pct_real_gdp_information", "economic_connectedness",
    ]

    kpis = {}
    for col in kpi_cols:
        raw = p.get(col)
        scored = p.get(f"scored_{col}")
        flag = p.get(f"imputed_flag_{col}", False)
        kpis[col] = {"raw": fmt_num(raw) if raw is not None else "—", "_raw_num": raw, "scored": scored, "imputed_flag": flag}

    OPPORTUNITY_CLUSTER_NAMES = {
        1: "Uneven Transition Markets",
        2: "Superstar Knowledge Capitals",
        3: "Emerging Momentum Markets",
        4: "Industrial Rebound Markets",
        5: "Broad-Based Opportunity Hubs",
        6: "Thin-Base Distressed Markets",
    }
    gmm_probs = {
        OPPORTUNITY_CLUSTER_NAMES.get(i, f"Cluster {i}"): p.get(f"opportunity_prob_cluster_{i}")
        for i in range(1, 7)
    }

    def extra():
        _oz_section(cbsa_code)
        st.divider()
        _industry_occupation_section(cbsa_code)

    render_frame_tab(
        cbsa_code=cbsa_code,
        cbsa_name=cbsa_name,
        frame="opportunity",
        profile=p,
        subjects=subjects,
        topics=topics,
        kpis=kpis,
        gmm_probs=gmm_probs,
        extra_section=extra,
    )
