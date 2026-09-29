"""Materialize Q2's national, reviewable job-center candidate mart.

The build publishes the strict-core, recommended core-plus-one-hop, and
no-market-share sensitivity constructions at the declared V0 parameters. It
does not promote any one construction as a final center method for every CBSA.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from shapely import wkb
from shapely.strtree import STRtree


METHOD_VERSION = "q2_job_center_v0"
WAC_COVERAGE_THRESHOLD = 0.95
ABSOLUTE_JOB_FLOOR = 2500
MARKET_JOB_SHARE_FLOOR = 0.01
JOBS_TO_WORKERS_FLOOR = 1.5


def resolve_db_path(repo_root: Path) -> str:
    """Use the configured warehouse, falling back to the repository-local DB."""

    return os.environ.get("DB_PATH", "").strip() or str(
        repo_root / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
    )


def read_query(query_dir: Path, name: str) -> str:
    """Keep the mart tied to Q2's named source readers rather than copied SQL."""

    return (query_dir / name).read_text()


def shared_edge_pairs(frame: pd.DataFrame) -> set[tuple[str, str]]:
    """Find shared-boundary pairs with an STRtree, never an all-tracts join.

    A nonzero shared boundary excludes corner-only contact. The tree limits
    exact geometry intersections to nearby candidate tracts within one CBSA.
    """

    if len(frame) < 2:
        return set()

    geometries = frame.geometry.tolist()
    tract_ids = frame.tract_geoid.tolist()
    tree = STRtree(geometries)
    pairs: set[tuple[str, str]] = set()

    for left_index, left_geometry in enumerate(geometries):
        # Shapely 2 returns integer positions here. Limiting comparisons to the
        # upper triangle keeps each shared edge deterministic and unique.
        for right_index in tree.query(left_geometry):
            right_index = int(right_index)
            if right_index <= left_index:
                continue
            shared_boundary = left_geometry.boundary.intersection(
                geometries[right_index].boundary
            )
            if not shared_boundary.is_empty and shared_boundary.length > 0:
                pairs.add(tuple(sorted((tract_ids[left_index], tract_ids[right_index]))))
    return pairs


def component_ids(
    tract_ids: set[str], edge_pairs: set[tuple[str, str]], cbsa_code: str
) -> dict[str, str]:
    """Assign stable, shared-edge component IDs to recommended candidate tracts."""

    neighbors = {tract_id: set() for tract_id in tract_ids}
    for left, right in edge_pairs:
        if left in neighbors and right in neighbors:
            neighbors[left].add(right)
            neighbors[right].add(left)

    result: dict[str, str] = {}
    component_number = 0
    for tract_id in sorted(tract_ids):
        if tract_id in result:
            continue
        component_number += 1
        component_id = f"{cbsa_code}_c{component_number:03d}"
        pending = [tract_id]
        while pending:
            current = pending.pop()
            if current in result:
                continue
            result[current] = component_id
            pending.extend(neighbors[current] - result.keys())
    return result


def apply_method(tracts: pd.DataFrame, geometry: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply all V0 constructions and return tract and component mart frames."""

    candidates = tracts.copy()
    candidates["market_job_share"] = candidates.jobs_total / candidates.market_jobs_total
    candidates["jobs_to_workers_ratio"] = candidates.jobs_total / candidates.workers_total.where(
        candidates.workers_total > 0
    )
    candidates["passes_absolute_job_floor"] = candidates.jobs_total >= ABSOLUTE_JOB_FLOOR
    candidates["passes_market_job_share"] = candidates.market_job_share >= MARKET_JOB_SHARE_FLOOR
    candidates["passes_jobs_to_workers"] = (
        candidates.jobs_to_workers_ratio >= JOBS_TO_WORKERS_FLOOR
    )
    candidates["is_strict_core_seed"] = (
        candidates.passes_absolute_job_floor
        & candidates.passes_market_job_share
        & candidates.passes_jobs_to_workers
    )
    candidates["is_no_share_sensitivity"] = (
        candidates.passes_absolute_job_floor & candidates.passes_jobs_to_workers
    )
    candidates["is_one_hop_extension"] = False
    candidates["is_recommended_center"] = candidates.is_strict_core_seed
    candidates["recommended_cluster_id"] = pd.NA

    geometry_by_tract = geometry.set_index("tract_geoid")["geometry"]
    cluster_rows: list[dict[str, object]] = []

    for cbsa_code, market in candidates.groupby("cbsa_code", sort=True):
        # Only no-share tracts can be a core or an extension. Restricting the
        # geometry tree to this subset makes the national build practical.
        eligible_ids = set(market.loc[market.is_no_share_sensitivity, "tract_geoid"])
        local_geometry = pd.DataFrame({
            "tract_geoid": sorted(eligible_ids),
        })
        local_geometry["geometry"] = local_geometry.tract_geoid.map(geometry_by_tract)
        local_geometry = local_geometry.dropna(subset=["geometry"])
        edge_pairs = shared_edge_pairs(local_geometry)

        core_ids = set(market.loc[market.is_strict_core_seed, "tract_geoid"])
        adjacent_to_core = {
            right if left in core_ids else left
            for left, right in edge_pairs
            if left in core_ids or right in core_ids
        }
        extension_ids = (adjacent_to_core & eligible_ids) - core_ids
        recommended_ids = core_ids | extension_ids

        candidates.loc[
            candidates.tract_geoid.isin(extension_ids), "is_one_hop_extension"
        ] = True
        candidates.loc[
            candidates.tract_geoid.isin(recommended_ids), "is_recommended_center"
        ] = True

        cluster_by_tract = component_ids(recommended_ids, edge_pairs, cbsa_code)
        candidates.loc[
            candidates.tract_geoid.isin(cluster_by_tract), "recommended_cluster_id"
        ] = candidates.loc[
            candidates.tract_geoid.isin(cluster_by_tract), "tract_geoid"
        ].map(cluster_by_tract)

        recommended = candidates.loc[
            candidates.tract_geoid.isin(recommended_ids)
        ].copy()
        for component_id, component in recommended.groupby("recommended_cluster_id", dropna=False):
            cluster_rows.append({
                "method_version": METHOD_VERSION,
                "cbsa_code": cbsa_code,
                "cbsa_name": component.cbsa_name.iloc[0],
                "recommended_cluster_id": component_id,
                "tract_count": len(component),
                "core_seed_count": int(component.is_strict_core_seed.sum()),
                "one_hop_extension_count": int(component.is_one_hop_extension.sum()),
                "workplace_jobs": int(component.jobs_total.sum()),
                "market_job_share": component.market_job_share.sum(),
                "is_shared_edge_cluster": len(component) >= 2,
            })

    candidates["method_version"] = METHOD_VERSION
    candidates["wac_year"] = candidates.wac_year.astype("int64")
    candidates["absolute_job_floor"] = ABSOLUTE_JOB_FLOOR
    candidates["market_job_share_floor"] = MARKET_JOB_SHARE_FLOOR
    candidates["jobs_to_workers_floor"] = JOBS_TO_WORKERS_FLOOR
    candidates["wac_coverage_threshold"] = WAC_COVERAGE_THRESHOLD
    candidates["center_role"] = "not_selected"
    candidates.loc[candidates.is_strict_core_seed, "center_role"] = "core_seed"
    candidates.loc[candidates.is_one_hop_extension, "center_role"] = "one_hop_extension"

    cluster_frame = pd.DataFrame(cluster_rows)
    return candidates, cluster_frame


def nearest_haversine_miles(
    tract_latitude: np.ndarray,
    tract_longitude: np.ndarray,
    center_latitude: np.ndarray,
    center_longitude: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return nearest-center positions and great-circle miles for one CBSA.

    This is deliberately a physical-proximity surface. It is not a routed
    travel-time or 15-minute-access measure.
    """

    earth_radius_miles = 3958.7613
    tract_latitude = np.radians(tract_latitude)[:, None]
    tract_longitude = np.radians(tract_longitude)[:, None]
    center_latitude = np.radians(center_latitude)[None, :]
    center_longitude = np.radians(center_longitude)[None, :]
    delta_latitude = center_latitude - tract_latitude
    delta_longitude = center_longitude - tract_longitude
    haversine_term = (
        np.sin(delta_latitude / 2) ** 2
        + np.cos(tract_latitude)
        * np.cos(center_latitude)
        * np.sin(delta_longitude / 2) ** 2
    )
    distances = 2 * earth_radius_miles * np.arcsin(np.sqrt(haversine_term))
    nearest_position = distances.argmin(axis=1)
    return nearest_position, distances[np.arange(len(distances)), nearest_position]


def build_proximity_mart(
    candidates: pd.DataFrame, geometry: pd.DataFrame
) -> pd.DataFrame:
    """Publish nearest-center distance for every tract and every candidate version."""

    geometry_by_tract = geometry.set_index("tract_geoid")["geometry"]
    versions = {
        "strict_core": "is_strict_core_seed",
        "recommended_core_one_hop": "is_recommended_center",
        "no_share_sensitivity": "is_no_share_sensitivity",
    }
    rows: list[pd.DataFrame] = []

    for cbsa_code, market in candidates.groupby("cbsa_code", sort=True):
        market = market.copy()
        market["geometry"] = market.tract_geoid.map(geometry_by_tract)
        market = market.dropna(subset=["geometry"])
        market["centroid_lon"] = market.geometry.map(lambda shape: shape.centroid.x)
        market["centroid_lat"] = market.geometry.map(lambda shape: shape.centroid.y)

        for version_name, flag_column in versions.items():
            centers = market.loc[market[flag_column]].copy()
            result = market[["cbsa_code", "tract_geoid"]].copy()
            result["method_version"] = METHOD_VERSION
            result["center_version"] = version_name
            result["center_count"] = len(centers)
            result["has_center_candidate"] = len(centers) > 0

            if centers.empty:
                result["nearest_center_tract_geoid"] = pd.NA
                result["distance_to_nearest_center_miles"] = np.nan
            else:
                nearest_position, distance_miles = nearest_haversine_miles(
                    market.centroid_lat.to_numpy(),
                    market.centroid_lon.to_numpy(),
                    centers.centroid_lat.to_numpy(),
                    centers.centroid_lon.to_numpy(),
                )
                result["nearest_center_tract_geoid"] = centers.tract_geoid.iloc[
                    nearest_position
                ].to_numpy()
                result["distance_to_nearest_center_miles"] = distance_miles
            rows.append(result)

    return pd.concat(rows, ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db-path",
        help="Override DB_PATH and the repository-local DuckDB warehouse.",
    )
    args = parser.parse_args()

    analysis_dir = Path(__file__).resolve().parent
    repo_root = analysis_dir.parents[3]
    query_dir = analysis_dir / "queries"
    db_path = args.db_path or resolve_db_path(repo_root)

    with duckdb.connect(db_path) as con:
        # The coverage cohort comes from the same named readers displayed in the
        # national notebook. Excluded WAC markets are not treated as zero-job.
        coverage = con.sql(read_query(query_dir, "q2_job_concentration_coverage.sql")).df()
        coverage["is_wac_coverage_eligible"] = (
            coverage.wac_geometry_coverage >= WAC_COVERAGE_THRESHOLD
        )
        eligible_codes = set(
            coverage.loc[coverage.is_wac_coverage_eligible, "cbsa_code"]
        )
        tracts = con.sql(read_query(query_dir, "q2_job_concentration_tracts.sql")).df()
        tracts = tracts.loc[tracts.cbsa_code.isin(eligible_codes)].copy()
        tracts["market_jobs_total"] = tracts.groupby("cbsa_code")["jobs_total"].transform("sum")

        # Geometry is needed only for tracts that could participate in the
        # no-share sensitivity, which bounds the national adjacency workload.
        prefilter = tracts.loc[
            (tracts.jobs_total >= ABSOLUTE_JOB_FLOOR)
            & (tracts.jobs_total / tracts.workers_total.where(tracts.workers_total > 0) >= JOBS_TO_WORKERS_FLOOR),
            ["tract_geoid"],
        ].drop_duplicates()
        con.register("q2_geometry_keys", prefilter)
        candidate_geometry = con.sql("""
            select keys.tract_geoid, tracts.geom_wkb
            from q2_geometry_keys keys
            join geo.tracts_all_us tracts
              on keys.tract_geoid = tracts.tract_geoid
        """).df()
        candidate_geometry["geometry"] = candidate_geometry.geom_wkb.map(
            lambda value: wkb.loads(bytes(value))
        )

        candidate_mart, cluster_mart = apply_method(tracts, candidate_geometry)
        # Distance needs every eligible tract origin, not only tracts that can
        # be centers. Decode governed WKB once, then calculate distances within
        # each CBSA and each published center version.
        con.register("q2_all_tract_keys", tracts[["tract_geoid"]].drop_duplicates())
        all_geometry = con.sql("""
            select keys.tract_geoid, tracts.geom_wkb
            from q2_all_tract_keys keys
            join geo.tracts_all_us tracts
              on keys.tract_geoid = tracts.tract_geoid
        """).df()
        all_geometry["geometry"] = all_geometry.geom_wkb.map(
            lambda value: wkb.loads(bytes(value))
        )
        proximity_mart = build_proximity_mart(candidate_mart, all_geometry)
        coverage_mart = coverage.loc[
            coverage.cbsa_code.isin(eligible_codes),
            [
                "cbsa_code",
                "cbsa_name",
                "governed_tract_count",
                "wac_tract_count",
                "rac_tract_count",
                "wac_geometry_coverage",
                "rac_geometry_coverage",
                "is_wac_coverage_eligible",
            ],
        ]
        candidate_mart = candidate_mart.merge(coverage_mart, on=["cbsa_code", "cbsa_name"], how="left")

        # A wide candidate table publishes all three constructions without
        # duplicating every tract three times. Consumers filter the boolean
        # version fields they need and always retain the method parameters.
        con.execute("create schema if not exists mart_explanation_q2")
        con.register("q2_job_center_candidates_frame", candidate_mart)
        con.register("q2_job_center_clusters_frame", cluster_mart)
        con.register("q2_job_center_proximity_frame", proximity_mart)
        con.execute("""
            create or replace table mart_explanation_q2.job_center_candidates_v0 as
            select * from q2_job_center_candidates_frame
        """)
        con.execute("""
            create or replace table mart_explanation_q2.job_center_clusters_v0 as
            select * from q2_job_center_clusters_frame
        """)
        con.execute("""
            create or replace table mart_explanation_q2.job_center_proximity_v0 as
            select * from q2_job_center_proximity_frame
        """)
        con.execute(f"""
            create or replace table mart_explanation_q2.job_center_method_catalog_v0 as
            select
                '{METHOD_VERSION}' as method_version,
                2023 as wac_year,
                {WAC_COVERAGE_THRESHOLD} as wac_coverage_threshold,
                {ABSOLUTE_JOB_FLOOR} as absolute_job_floor,
                {MARKET_JOB_SHARE_FLOOR} as market_job_share_floor,
                {JOBS_TO_WORKERS_FLOOR} as jobs_to_workers_floor,
                'strict core: all three gates' as strict_core_definition,
                'recommended: strict core plus one shared-edge extension hop' as recommended_definition,
                'sensitivity: absolute-job and jobs-to-workers gates; market share omitted' as no_share_definition,
                'candidate baseline pending per-market reviewer approval' as promotion_status
        """)

    print(
        "Materialized mart_explanation_q2.job_center_candidates_v0 "
        f"({len(candidate_mart):,} tract rows) and "
        "mart_explanation_q2.job_center_clusters_v0 "
        f"({len(cluster_mart):,} components), plus "
        "mart_explanation_q2.job_center_proximity_v0 "
        f"({len(proximity_mart):,} tract-version rows)."
    )


if __name__ == "__main__":
    main()
