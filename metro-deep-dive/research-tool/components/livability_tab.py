"""Livability frame tab."""

from __future__ import annotations

import streamlit as st

from components.frame_tab_base import render_frame_tab
from components.ui_helpers import fmt_num


def render_livability(cbsa_code: str, cbsa_name: str, p: dict) -> None:
    subjects = {
        "affordability": p.get("subject_score_affordability") or p.get("affordability_score"),
        "health_and_safety": p.get("subject_score_health_and_safety") or p.get("health_and_safety_score"),
        "access_and_infrastructure": p.get("subject_score_access_and_infrastructure") or p.get("access_and_infrastructure_score"),
        "physical_environment": p.get("subject_score_physical_environment") or p.get("physical_environment_score"),
    }

    topics = {
        k.replace("topic_score_", ""): v
        for k, v in p.items()
        if k.startswith("topic_score_")
    }

    kpi_cols = [
        "value_to_income", "pct_rent_burden_30plus", "pov_rate",
        "permits_per_1000_housing_units", "permits_share_units_5_plus",
        "pct_struct_mobile", "pct_struct_small_mf", "pct_struct_mid_mf",
        "premature_death_rate", "mental_health_provider_ratio",
        "drug_overdose_death_rate", "pct_uninsured_adults",
        "preventable_hospital_stay_rate", "firearm_fatality_rate",
        "motor_vehicle_crash_rate", "pct_commute_walk", "pct_commute_wfh",
        "vacancy_rate", "pct_hh_0_vehicles", "pct_no_internet_access",
        "walkability_index", "jobs_access_45min_transit",
        "pct_population_low_income_low_access_1_10",
        "pop_weighted_density_sqmi", "aqi_median", "fema_risk_score",
    ]

    kpis = {}
    for col in kpi_cols:
        raw = p.get(col)
        scored = p.get(f"scored_{col}")
        flag = p.get(f"imputed_flag_{col}", False)
        kpis[col] = {"raw": fmt_num(raw) if raw is not None else "—", "_raw_num": raw, "scored": scored, "imputed_flag": flag}

    LIVABILITY_CLUSTER_NAMES = {
        1: "Healthy Affordable Havens",
        2: "Knowledge & Care Hubs",
        3: "High-Access Prosperous Hubs",
        4: "Strained Interior Markets",
        5: "Amenity Growth Markets",
        6: "Megametro Extremes",
    }
    gmm_probs = {
        LIVABILITY_CLUSTER_NAMES.get(i, f"Cluster {i}"): p.get(f"livability_prob_cluster_{i}")
        for i in range(1, 7)
    }

    render_frame_tab(
        cbsa_code=cbsa_code,
        cbsa_name=cbsa_name,
        frame="livability",
        profile=p,
        subjects=subjects,
        topics=topics,
        kpis=kpis,
        gmm_probs=gmm_probs,
    )
