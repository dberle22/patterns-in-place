"""Character frame tab."""

from __future__ import annotations

from components.frame_tab_base import render_frame_tab
from components.ui_helpers import fmt_num


def render_character(cbsa_code: str, cbsa_name: str, p: dict) -> None:
    subjects = {
        "demographics": p.get("subject_score_demographics") or p.get("demographics_score"),
        "social_fabric": p.get("subject_score_social_fabric") or p.get("social_fabric_score"),
    }

    topics = {
        k.replace("topic_score_", ""): v
        for k, v in p.items()
        if k.startswith("topic_score_")
    }

    kpi_cols = [
        "diversity_index", "pct_black_nh", "pct_asian_nh", "pct_hispanic",
        "pct_age_over_64", "pct_ba_plus", "pct_foreign_born",
        "pop_weighted_density_sqmi", "friending_bias",
        "civic_engagement_volunteering_rate", "civic_organizations_per_1000",
        "nonprofits_per_100k", "irs_net_migration_rate",
        "pct_moved_diff_st", "pct_moved_abroad",
        "social_associations_per_10k", "pct_struct_multifam",
    ]

    kpis = {}
    for col in kpi_cols:
        raw = p.get(col)
        scored = p.get(f"scored_{col}")
        flag = p.get(f"imputed_flag_{col}", False)
        kpis[col] = {"raw": fmt_num(raw) if raw is not None else "—", "_raw_num": raw, "scored": scored, "imputed_flag": flag}

    # GMM soft memberships — map cluster integers to names
    CHARACTER_CLUSTER_NAMES = {
        1: "Retirement & Lifestyle Havens",
        2: "Global Knowledge Capitals",
        3: "Rooted Heartland Centers",
        4: "College & Civic Anchors",
        5: "Established Community Anchors",
        6: "Immigrant Growth Corridors",
        7: "Interior Family Opportunity Hubs",
    }
    gmm_probs = {
        CHARACTER_CLUSTER_NAMES.get(i, f"Cluster {i}"): p.get(f"character_prob_cluster_{i}")
        for i in range(1, 8)
    }

    render_frame_tab(
        cbsa_code=cbsa_code,
        cbsa_name=cbsa_name,
        frame="character",
        profile=p,
        subjects=subjects,
        topics=topics,
        kpis=kpis,
        gmm_probs=gmm_probs,
    )
