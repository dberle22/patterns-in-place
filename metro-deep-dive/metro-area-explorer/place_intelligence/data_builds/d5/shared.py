"""Shared helpers for split D5 market and site products."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import geopandas as gpd
import pandas as pd


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from site_prep import (
    D5_NRI_CORE_COLUMNS,
    D5_NRI_HAZARD_LABELS,
    Site,
    _apportion_metric_series,
    _build_cumulative_weight_table,
    _empty_nfhl_ring_share_table,
    _empty_nfhl_site_lookup,
    _empty_nri_top_hazards,
    _load_nfhl_zone_geometries,
    _query_nri_surface,
    _resolve_site_coordinates,
    build_cumulative_rings_for_site,
    build_nfhl_ring_share_table,
    lookup_nfhl_site_flood_zone,
)


def normalize_weight_table(weight_table: pd.DataFrame) -> pd.DataFrame:
    """Keep tract ids string-typed so D5 staged joins are stable."""

    if weight_table.empty:
        return weight_table.copy()
    normalized = weight_table.copy()
    if "tract_geoid" in normalized.columns:
        normalized["tract_geoid"] = normalized["tract_geoid"].astype(str).str.zfill(11)
    return normalized


def build_market_nri_inputs(site: Site) -> pd.DataFrame:
    """Stage tract and CBSA NRI rows once per market."""

    frame = _query_nri_surface(site.market_id).copy()
    if frame.empty:
        return pd.DataFrame()
    if "geo_id" in frame.columns:
        frame["geo_id"] = frame["geo_id"].astype(str)
    return frame.sort_values(["geo_level", "geo_id"], kind="mergesort").reset_index(drop=True)


def build_nri_scores_payload(site: Site, weight_table: pd.DataFrame, nri_surface: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Aggregate staged NRI rows into site catchment and CBSA benchmark outputs."""

    catchment_score_columns = [
        "site_id",
        "ring_mi",
        "year",
        "risk_score",
        "eal_score",
        "social_vulnerability_score",
        "community_resilience_score",
        "coastal_flooding_risk_score",
        "inland_flooding_risk_score",
        "hurricane_risk_score",
    ]
    if weight_table.empty or nri_surface.empty:
        return {
            "catchment_scores": pd.DataFrame(columns=catchment_score_columns),
            "catchment_top_hazards": _empty_nri_top_hazards(),
            "cbsa_benchmark": pd.DataFrame(columns=["site_id", "market_id", "geo_name", "year", *D5_NRI_CORE_COLUMNS]),
            "cbsa_top_hazards": _empty_nri_top_hazards(),
        }

    tract_rows = nri_surface.loc[nri_surface["geo_level"] == "tract"].copy()
    cbsa_rows = nri_surface.loc[(nri_surface["geo_level"] == "cbsa") & (nri_surface["geo_id"] == str(site.market_id))].copy()
    if tract_rows.empty:
        return {
            "catchment_scores": pd.DataFrame(columns=catchment_score_columns),
            "catchment_top_hazards": _empty_nri_top_hazards(),
            "cbsa_benchmark": pd.DataFrame(columns=["site_id", "market_id", "geo_name", "year", *D5_NRI_CORE_COLUMNS]),
            "cbsa_top_hazards": _empty_nri_top_hazards(),
        }

    cumulative_weights = _build_cumulative_weight_table(normalize_weight_table(weight_table), site.rings_mi)
    hazard_columns = [column for column in D5_NRI_HAZARD_LABELS if column in tract_rows.columns]
    metric_columns = [column for column in D5_NRI_CORE_COLUMNS if column in tract_rows.columns]

    metric_results: dict[str, pd.Series] = {}
    for column in [*metric_columns, *hazard_columns]:
        metric_values = tract_rows[["geo_id", column]].dropna()
        if metric_values.empty:
            continue
        metric_values["geo_id"] = metric_values["geo_id"].astype(str).str.zfill(11)
        metric_results[column] = _apportion_metric_series(
            column,
            "intensive",
            metric_values.set_index("geo_id")[column],
            cumulative_weights,
        )

    catchment_rows: list[dict[str, Any]] = []
    catchment_top_hazards: list[dict[str, Any]] = []
    catchment_year = int(tract_rows["year"].max())
    for ring_mi in sorted(site.rings_mi):
        row = {"site_id": site.site_id, "ring_mi": int(ring_mi), "year": catchment_year}
        for column in metric_columns:
            result = metric_results.get(column)
            row[column] = float(result.loc[ring_mi]) if result is not None and ring_mi in result.index else None
        catchment_rows.append(row)

        top_scores = {
            column: float(result.loc[ring_mi])
            for column, result in metric_results.items()
            if column in hazard_columns and ring_mi in result.index and pd.notna(result.loc[ring_mi])
        }
        for rank, (hazard_id, score) in enumerate(
            sorted(top_scores.items(), key=lambda item: item[1], reverse=True)[:3],
            start=1,
        ):
            catchment_top_hazards.append(
                {
                    "site_id": site.site_id,
                    "geography": f"{ring_mi}-mile ring",
                    "ring_mi": int(ring_mi),
                    "rank": rank,
                    "hazard_id": hazard_id,
                    "hazard_label": D5_NRI_HAZARD_LABELS.get(hazard_id, hazard_id),
                    "risk_score": score,
                }
            )

    cbsa_benchmark = pd.DataFrame(columns=["site_id", "market_id", "geo_name", "year", *D5_NRI_CORE_COLUMNS])
    cbsa_top_hazards = _empty_nri_top_hazards()
    if not cbsa_rows.empty:
        cbsa_row = cbsa_rows.sort_values("year", ascending=False, kind="mergesort").iloc[0]
        benchmark_row = {
            "site_id": site.site_id,
            "market_id": str(site.market_id),
            "geo_name": cbsa_row.get("geo_name"),
            "year": int(cbsa_row["year"]),
        }
        for column in metric_columns:
            benchmark_row[column] = float(cbsa_row[column]) if pd.notna(cbsa_row[column]) else None
        cbsa_benchmark = pd.DataFrame([benchmark_row])

        cbsa_scores = {
            column: float(cbsa_row[column])
            for column in hazard_columns
            if pd.notna(cbsa_row.get(column))
        }
        cbsa_top_hazards = pd.DataFrame(
            [
                {
                    "site_id": site.site_id,
                    "geography": str(cbsa_row.get("geo_name") or site.market_id),
                    "ring_mi": None,
                    "rank": rank,
                    "hazard_id": hazard_id,
                    "hazard_label": D5_NRI_HAZARD_LABELS.get(hazard_id, hazard_id),
                    "risk_score": score,
                }
                for rank, (hazard_id, score) in enumerate(
                    sorted(cbsa_scores.items(), key=lambda item: item[1], reverse=True)[:3],
                    start=1,
                )
            ]
        )

    return {
        "catchment_scores": pd.DataFrame(catchment_rows),
        "catchment_top_hazards": pd.DataFrame(catchment_top_hazards) if catchment_top_hazards else _empty_nri_top_hazards(),
        "cbsa_benchmark": cbsa_benchmark,
        "cbsa_top_hazards": cbsa_top_hazards,
    }


def build_nfhl_site_zone_payload(site: Site) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Look up the site's FEMA flood zone and return both rows and service status."""

    try:
        return lookup_nfhl_site_flood_zone(site), {"nfhl_service_status": "ok", "nfhl_service_error": None}
    except Exception as exc:
        return _empty_nfhl_site_lookup(site), {"nfhl_service_status": "unavailable", "nfhl_service_error": str(exc)}


def build_nfhl_ring_shares_payload(site: Site) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Compute ring-area shares by FEMA flood zone and return both rows and service status."""

    try:
        rings = build_cumulative_rings_for_site(site)
        return build_nfhl_ring_share_table(site, rings), {"nfhl_service_status": "ok", "nfhl_service_error": None}
    except Exception as exc:
        return _empty_nfhl_ring_share_table(site), {"nfhl_service_status": "unavailable", "nfhl_service_error": str(exc)}


def build_d5_meta(nfhl_status: dict[str, Any]) -> dict[str, Any]:
    """Build the small D5 meta contract from NFHL service status."""

    return {
        "nfhl_service_status": nfhl_status.get("nfhl_service_status"),
        "nfhl_service_error": nfhl_status.get("nfhl_service_error"),
        "copy_note": (
            "NFHL answers the parcel-level map question: which FEMA flood zone the site sits in today. "
            "NRI answers the broader catchment-risk question by summarizing modeled hazard scores across nearby tracts. "
            "This is a screening-level read from published FEMA mapping, not a flood determination, elevation certificate, or insurance rating."
        ),
    }
