"""Same-zone graph and DBSCAN-challenger logic for Corridor Intelligence."""

from __future__ import annotations

import hashlib
from collections import deque
from typing import Any

import numpy as np
import pandas as pd
from pyproj import Transformer
from shapely import from_wkb
from shapely.ops import transform


def cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    """Return a stable cosine score for the declared Phase 7 score vector."""
    denominator = np.linalg.norm(left) * np.linalg.norm(right)
    return float(np.dot(left, right) / denominator) if denominator else 0.0


def candidate_id(cbsa_code: str, zone_type: str, tract_geoids: list[str]) -> str:
    """Derive a membership-sensitive ID without ranks, names, or market tuning."""
    digest = hashlib.sha256("|".join(sorted(tract_geoids)).encode()).hexdigest()[:12]
    slug = "".join(character.lower() if character.isalnum() else "-" for character in zone_type).strip("-")
    return f"ci-{cbsa_code}-{slug}-{digest}"


def connected_components(nodes: list[str], edges: list[tuple[str, str]]) -> list[list[str]]:
    """Return sorted components so results do not depend on source-row order."""
    neighbors = {node: set() for node in nodes}
    for left, right in edges:
        neighbors[left].add(right)
        neighbors[right].add(left)
    components, seen = [], set()
    for node in sorted(nodes):
        if node in seen:
            continue
        queue, component = deque([node]), []
        seen.add(node)
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in sorted(neighbors[current]):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component))
    return components


def dbscan(nodes: list[str], neighbors: dict[str, set[str]], min_samples: int) -> list[list[str]]:
    """Implement the small declared DBSCAN challenger without hidden defaults."""
    labels: dict[str, int | None] = {node: None for node in nodes}
    cluster_number = 0
    for seed in sorted(nodes):
        if labels[seed] is not None:
            continue
        if len(neighbors[seed]) + 1 < min_samples:  # DBSCAN counts the seed.
            labels[seed] = -1
            continue
        cluster_number += 1
        labels[seed] = cluster_number
        frontier = deque(sorted(neighbors[seed]))
        while frontier:
            point = frontier.popleft()
            if labels[point] == -1:
                labels[point] = cluster_number
            if labels[point] is not None:
                continue
            labels[point] = cluster_number
            if len(neighbors[point]) + 1 >= min_samples:
                frontier.extend(sorted(neighbors[point]))
    return [sorted(node for node, label in labels.items() if label == number) for number in range(1, cluster_number + 1)]


def evaluate_relationships(tracts: pd.DataFrame, profile: dict[str, Any], market: str) -> list[dict[str, Any]]:
    """Evaluate only declared same-zone, adjacent-or-nearby relationships."""
    spatial = profile["spatial"]
    project = Transformer.from_crs("EPSG:4326", spatial["projected_crs"][market], always_xy=True).transform
    # DuckDB returns BLOB values as bytearrays through pandas; Shapely expects
    # an immutable bytes object for its WKB reader.
    geometries = {row.tract_geoid: transform(project, from_wkb(bytes(row.geometry_wkb))) for row in tracts.itertuples()}
    score_fields = profile["similarity"]["fields"]
    vectors = {row.tract_geoid: np.array([getattr(row, field) for field in score_fields], dtype=float) for row in tracts.itertuples()}
    rows = []
    for zone_type, zone_tracts in tracts.groupby("zone_type", sort=True):
        geoids = sorted(zone_tracts.tract_geoid.tolist())
        for right_index, right in enumerate(geoids):
            for left in geoids[:right_index]:
                shared_boundary_m = geometries[left].boundary.intersection(geometries[right].boundary).length
                centroid_distance_m = geometries[left].centroid.distance(geometries[right].centroid)
                strict = shared_boundary_m >= spatial["minimum_shared_boundary_m"]
                nearby = centroid_distance_m <= spatial["bounded_nearby_centroid_distance_m"]
                dbscan_nearby = centroid_distance_m <= profile["dbscan_challenger"]["maximum_centroid_distance_m"]
                if not strict and not nearby and not dbscan_nearby:
                    continue
                similarity = cosine_similarity(vectors[left], vectors[right])
                rows.append({
                    "tract_geoid_low": left,
                    "tract_geoid_high": right,
                    "zone_type": zone_type,
                    "shared_boundary_m": round(shared_boundary_m, 3),
                    "centroid_distance_m": round(centroid_distance_m, 3),
                    "geographic_relation": "strict_adjacency" if strict else "bounded_nearby" if nearby else "dbscan_nearby",
                    "phase7_similarity": round(similarity, 6),
                    "strict_accepted": strict and similarity >= profile["similarity"]["minimum_similarity"],
                    # The relaxed graph adds near pairs to the strict baseline;
                    # it never drops a qualifying shared-boundary connection.
                    "bounded_accepted": (strict or nearby) and similarity >= profile["similarity"]["minimum_similarity"],
                })
    return rows


def graph_products(tracts: pd.DataFrame, relationships: list[dict[str, Any]], run_id: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build two same-zone variants and retain each isolated tract as unassigned."""
    memberships, candidates, edges = [], [], []
    for variant, acceptance_field in {"strict_adjacency": "strict_accepted", "bounded_nearby": "bounded_accepted"}.items():
        component_by_tract: dict[str, list[str]] = {}
        for zone_type, zone_tracts in tracts.groupby("zone_type", sort=True):
            nodes = sorted(zone_tracts.tract_geoid.tolist())
            accepted = [(row["tract_geoid_low"], row["tract_geoid_high"]) for row in relationships if row["zone_type"] == zone_type and row[acceptance_field]]
            for component in connected_components(nodes, accepted):
                if len(component) < 2:
                    continue
                identifier = candidate_id(str(zone_tracts.cbsa_code.iloc[0]), zone_type, component)
                component_by_tract.update({geoid: component for geoid in component})
                candidates.append(_candidate_row(run_id, variant, identifier, zone_tracts, zone_type, component, "same_zone_baseline_unreviewed"))
        memberships.extend(_membership_rows(tracts, run_id, variant, component_by_tract, "same_zone_baseline"))
        for relationship in relationships:
            accepted = relationship[acceptance_field]
            edges.append({"run_id": run_id, "method_variant": variant, **relationship, "same_zone_baseline_decision": "accepted" if accepted else "rejected_similarity", "infrastructure_evidence": None, "poi_evidence": None, "final_decision": "accepted" if accepted else "rejected", "decision_stage": "same_zone_baseline"})
    return pd.DataFrame(memberships), pd.DataFrame(candidates), pd.DataFrame(edges)


def dbscan_products(tracts: pd.DataFrame, relationships: list[dict[str, Any]], run_id: str, profile: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run the hybrid challenger separately within each zone type."""
    challenger = profile["dbscan_challenger"]
    component_by_tract, candidates, edges = {}, [], []
    for zone_type, zone_tracts in tracts.groupby("zone_type", sort=True):
        nodes = sorted(zone_tracts.tract_geoid.tolist())
        neighbors = {node: set() for node in nodes}
        for relationship in relationships:
            if relationship["zone_type"] != zone_type:
                continue
            feature_distance = 1 - relationship["phase7_similarity"]
            spatial_distance = relationship["centroid_distance_m"] / challenger["maximum_centroid_distance_m"]
            hybrid_distance = challenger["alpha_feature_distance"] * feature_distance + (1 - challenger["alpha_feature_distance"]) * spatial_distance
            accepted = relationship["centroid_distance_m"] <= challenger["maximum_centroid_distance_m"] and hybrid_distance <= challenger["epsilon"]
            # Preserve the calculated hybrid distance on every evaluated pair,
            # including a rejected pair, so the challenger is reviewable.
            edges.append({"run_id": run_id, "method_variant": "dbscan_challenger", **relationship, "hybrid_distance": round(hybrid_distance, 6), "same_zone_baseline_decision": None, "infrastructure_evidence": None, "poi_evidence": None, "final_decision": "accepted" if accepted else "rejected", "decision_stage": "dbscan_challenger"})
            if accepted:
                neighbors[relationship["tract_geoid_low"]].add(relationship["tract_geoid_high"])
                neighbors[relationship["tract_geoid_high"]].add(relationship["tract_geoid_low"])
        for component in dbscan(nodes, neighbors, challenger["min_samples"]):
            identifier = candidate_id(str(zone_tracts.cbsa_code.iloc[0]), zone_type, component)
            component_by_tract.update({geoid: component for geoid in component})
            candidates.append(_candidate_row(run_id, "dbscan_challenger", identifier, zone_tracts, zone_type, component, "dbscan_challenger_unreviewed"))
    return pd.DataFrame(_membership_rows(tracts, run_id, "dbscan_challenger", component_by_tract, "dbscan_challenger")), pd.DataFrame(candidates), pd.DataFrame(edges)


def _candidate_row(run_id: str, variant: str, identifier: str, zone_tracts: pd.DataFrame, zone_type: str, component: list[str], coherence_status: str) -> dict[str, Any]:
    """Create the shared, intentionally form-unclassified Epic 2 candidate row."""
    return {"run_id": run_id, "method_variant": variant, "candidate_id": identifier, "cbsa_code": str(zone_tracts.cbsa_code.iloc[0]), "primary_zone_type": zone_type, "candidate_form": "unclassified", "core_tract_count": len(component), "bridge_tract_count": 0, "total_tract_count": len(component), "coherence_status": coherence_status}


def _membership_rows(tracts: pd.DataFrame, run_id: str, variant: str, components: dict[str, list[str]], stage: str) -> list[dict[str, Any]]:
    """Account for all Phase 7 inputs, including isolated same-zone tracts."""
    rows = []
    for tract in tracts.itertuples():
        component = components.get(tract.tract_geoid)
        rows.append({"run_id": run_id, "method_variant": variant, "tract_geoid": tract.tract_geoid, "cbsa_code": str(tract.cbsa_code), "original_zone_type": tract.zone_type, "membership_status": "core" if component else "unassigned", "candidate_id": candidate_id(str(tract.cbsa_code), tract.zone_type, component) if component else None, "membership_stage": stage, "exclusion_reason": None, "evidence_summary": f"{variant}; component_size={len(component) if component else 1}"})
    return rows
