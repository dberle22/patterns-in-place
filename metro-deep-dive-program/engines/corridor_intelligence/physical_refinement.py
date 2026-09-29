"""Physical, aggregate-place, bridge, and form refinement for Epic 3."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd
from pyproj import Transformer
from shapely import from_wkb
from shapely.ops import transform, unary_union
from shapely.strtree import STRtree

from corridor_baseline import candidate_id, connected_components, cosine_similarity


def refine_candidates(tracts: pd.DataFrame, relationships: list[dict[str, Any]], infrastructure: pd.DataFrame, poi_counts: pd.DataFrame, baseline: dict[str, Any], evidence: dict[str, Any], market: str, run_id: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Refine only borderline same-zone edges, then test auditable bridge tracts."""
    project = Transformer.from_crs("EPSG:4326", baseline["spatial"]["projected_crs"][market], always_xy=True).transform
    geometries = {row.tract_geoid: transform(project, from_wkb(bytes(row.geometry_wkb))) for row in tracts.itertuples()}
    feature_geometries = [transform(project, from_wkb(bytes(row.geometry_wkb))) for row in infrastructure.itertuples()]
    feature_tree = STRtree(feature_geometries)
    feature_rows = list(infrastructure.itertuples())
    poi_vectors = _poi_vectors(tracts, poi_counts, evidence["poi"]["eligible_categories"])

    edge_rows, accepted_edges = [], []
    for relationship in relationships:
        if relationship["geographic_relation"] == "dbscan_nearby":
            continue
        left, right = relationship["tract_geoid_low"], relationship["tract_geoid_high"]
        spine_count, separator_overlap = _physical_evidence(geometries[left], geometries[right], feature_tree, feature_geometries, feature_rows, evidence["infrastructure"])
        place_similarity, combined_places = _place_evidence(left, right, poi_vectors)
        baseline_accepted = relationship["strict_accepted"]
        similarity = relationship["phase7_similarity"]
        decision, reason = baseline_accepted, "same_zone_baseline"
        if baseline_accepted and separator_overlap >= evidence["infrastructure"]["separator_minimum_overlap_m"] and not spine_count:
            decision, reason = False, "infrastructure_separator"
        elif not baseline_accepted and similarity >= evidence["borderline_similarity_minimum"] and spine_count:
            decision, reason = True, "infrastructure_spine_borderline"
        elif not baseline_accepted and place_similarity is not None and similarity >= evidence["poi"]["minimum_similarity_for_poi_refinement"] and combined_places >= evidence["poi"]["minimum_combined_places"] and place_similarity >= evidence["poi"]["minimum_composition_similarity"]:
            # This branch still requires a geographic relationship and a
            # declared Phase 7 borderline case; aggregate POIs never stand alone.
            decision, reason = True, "poi_composition_borderline"
        if decision:
            accepted_edges.append((left, right))
        edge_rows.append({"run_id": run_id, "method_variant": "physical_evidence", **relationship, "spine_feature_count": spine_count, "separator_overlap_m": round(separator_overlap, 3), "poi_composition_similarity": None if place_similarity is None else round(place_similarity, 6), "poi_combined_places": combined_places, "same_zone_baseline_decision": "accepted" if baseline_accepted else "rejected_similarity", "infrastructure_evidence": f"spine_features={spine_count}; separator_overlap_m={separator_overlap:.3f}", "poi_evidence": f"combined_places={combined_places}; composition_similarity={place_similarity}" if place_similarity is not None else "insufficient_eligible_aggregate_poi", "final_decision": "accepted" if decision else "rejected", "decision_stage": reason})

    core_components = _core_components(tracts, accepted_edges)
    bridges = _bridge_assignments(tracts, geometries, core_components, feature_tree, feature_geometries, feature_rows, evidence["bridge"], evidence["infrastructure"])
    return _final_products(tracts, geometries, core_components, bridges, edge_rows, run_id, evidence["form"])


def _physical_evidence(left, right, tree, geometries, rows, settings: dict[str, Any]) -> tuple[int, float]:
    """Count shared spine features and measure only separator features aligned to the border."""
    pair = left.union(right)
    shared_boundary = left.boundary.intersection(right.boundary)
    spine_count, separator_overlap = 0, 0.0
    for index in tree.query(pair):
        feature, row = geometries[index], rows[index]
        if row.feature_type in settings["spine_types"]:
            buffered = feature.buffer(settings["spine_buffer_m"])
            if buffered.intersects(left) and buffered.intersects(right):
                spine_count += 1
        if row.feature_type in settings["separator_types"] and not shared_boundary.is_empty:
            separator_overlap += feature.intersection(shared_boundary.buffer(settings["separator_boundary_buffer_m"])).length
    return spine_count, separator_overlap


def _poi_vectors(tracts: pd.DataFrame, poi_counts: pd.DataFrame, categories: list[str]) -> dict[str, tuple[np.ndarray, int]]:
    """Produce tract-level category vectors; source records are never retained here."""
    counts = {(row.tract_geoid, row.governed_category): row.place_count for row in poi_counts.itertuples()}
    return {tract.tract_geoid: (np.array([counts.get((tract.tract_geoid, category), 0) for category in categories], dtype=float), sum(counts.get((tract.tract_geoid, category), 0) for category in categories)) for tract in tracts.itertuples()}


def _place_evidence(left: str, right: str, vectors: dict[str, tuple[np.ndarray, int]]) -> tuple[float | None, int]:
    """Compare aggregate category composition only when both tracts have a signal."""
    left_vector, left_count = vectors[left]
    right_vector, right_count = vectors[right]
    if not left_count or not right_count:
        return None, left_count + right_count
    return cosine_similarity(left_vector, right_vector), left_count + right_count


def _core_components(tracts: pd.DataFrame, accepted_edges: list[tuple[str, str]]) -> dict[str, list[list[str]]]:
    """Keep only multi-tract same-zone components as candidate core sections."""
    result = {}
    for zone_type, zone_tracts in tracts.groupby("zone_type", sort=True):
        nodes = sorted(zone_tracts.tract_geoid.tolist())
        zone_edges = [edge for edge in accepted_edges if edge[0] in set(nodes)]
        result[zone_type] = [component for component in connected_components(nodes, zone_edges) if len(component) >= 2]
    return result


def _bridge_assignments(tracts: pd.DataFrame, geometries: dict[str, Any], components: dict[str, list[list[str]]], tree, feature_geometries, feature_rows, bridge_settings: dict[str, Any], infrastructure_settings: dict[str, Any]) -> list[dict[str, Any]]:
    """Admit a different-zone tract only when it joins two separate core sections."""
    zone_lookup = dict(zip(tracts.tract_geoid, tracts.zone_type))
    assignments = []
    used_section_joins: set[tuple[str, tuple[str, ...], tuple[str, ...]]] = set()
    for bridge_geoid, bridge_zone in sorted(zone_lookup.items()):
        bridge_geometry = geometries[bridge_geoid]
        choices = []
        for primary_zone, sections in components.items():
            if primary_zone == bridge_zone or len(sections) < 2:
                continue
            touched_sections = []
            spine_count = 0
            for section in sections:
                touched = [core_geoid for core_geoid in section if bridge_geometry.boundary.intersection(geometries[core_geoid].boundary).length >= bridge_settings["minimum_shared_boundary_m"]]
                if touched:
                    touched_sections.append((section, touched))
                    for core_geoid in touched:
                        spine_count += _physical_evidence(bridge_geometry, geometries[core_geoid], tree, feature_geometries, feature_rows, infrastructure_settings)[0]
            neighbors = sum(len(touched) for _, touched in touched_sections)
            if len(touched_sections) >= 2 and neighbors >= bridge_settings["minimum_core_neighbors"] and (not bridge_settings["require_spine_evidence"] or spine_count > 0):
                choices.append((neighbors, spine_count, primary_zone, touched_sections))
        if choices:
            neighbors, spine_count, primary_zone, touched_sections = sorted(choices, key=lambda value: (-value[0], -value[1], value[2]))[0]
            section_keys = [tuple(section) for section, _ in touched_sections]
            joins = [(primary_zone, *sorted(pair)) for pair in combinations(section_keys, 2)]
            # Multiple different-type tracts can touch the same pair of core
            # sections. Retaining all of them inflates bridge share without
            # adding a new connection, so keep one deterministic bridge only.
            if any(join in used_section_joins for join in joins):
                continue
            used_section_joins.update(joins)
            assignments.append({"bridge_geoid": bridge_geoid, "bridge_zone": bridge_zone, "primary_zone": primary_zone, "touched_sections": touched_sections, "core_neighbors": neighbors, "spine_feature_count": spine_count})
    return assignments


def _final_products(tracts: pd.DataFrame, geometries: dict[str, Any], components: dict[str, list[list[str]]], bridges: list[dict[str, Any]], edges: list[dict[str, Any]], run_id: str, form_settings: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Merge bridge-linked sections, classify spatial form, and account for all tracts."""
    membership_rows, candidate_rows = [], []
    assignment_by_tract: dict[str, tuple[str, list[str], bool, dict[str, Any] | None]] = {}
    bridges_by_zone: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for bridge in bridges:
        bridges_by_zone[bridge["primary_zone"]].append(bridge)
        # A bridge is not just a membership label: preserve every core contact
        # that justified it, including the different original zone type.
        for _, touched_geoids in bridge["touched_sections"]:
            for core_geoid in touched_geoids:
                low, high = sorted((bridge["bridge_geoid"], core_geoid))
                edges.append({"run_id": run_id, "method_variant": "physical_evidence", "tract_geoid_low": low, "tract_geoid_high": high, "zone_type": bridge["primary_zone"], "shared_boundary_m": round(geometries[bridge["bridge_geoid"]].boundary.intersection(geometries[core_geoid].boundary).length, 3), "centroid_distance_m": round(geometries[bridge["bridge_geoid"]].centroid.distance(geometries[core_geoid].centroid), 3), "geographic_relation": "strict_adjacency", "phase7_similarity": None, "strict_accepted": None, "bounded_accepted": None, "spine_feature_count": bridge["spine_feature_count"], "separator_overlap_m": None, "poi_composition_similarity": None, "poi_combined_places": None, "same_zone_baseline_decision": "not_applicable_different_zone", "infrastructure_evidence": f"bridge_spine_features={bridge['spine_feature_count']}", "poi_evidence": "not_used_for_bridge", "final_decision": "accepted", "decision_stage": "conservative_bridge"})
    for zone_type, sections in components.items():
        groups = [set(section) for section in sections]
        for bridge in bridges_by_zone[zone_type]:
            touched = [set(section) for section, _ in bridge["touched_sections"]]
            joined = set().union(*touched, {bridge["bridge_geoid"]})
            touched_core_geoids = set().union(*touched)
            retained = []
            for group in groups:
                # A prior bridge may already have merged one of these sections.
                # Merge by shared core membership, not full-set equality, to
                # prevent overlapping candidate groups in chained bridges.
                if group & touched_core_geoids:
                    joined.update(group)
                else:
                    retained.append(group)
            retained.append(joined)
            groups = retained
        for group in groups:
            core_geoids = sorted(geoid for geoid in group if tracts.loc[tracts.tract_geoid == geoid, "zone_type"].iloc[0] == zone_type)
            bridge_geoids = sorted(group - set(core_geoids))
            identifier = candidate_id(str(tracts.cbsa_code.iloc[0]), zone_type, sorted(group))
            form, aspect_ratio, spine_edges = _classify_form(group, geometries, edges, form_settings)
            candidate_rows.append({"run_id": run_id, "method_variant": "physical_evidence", "candidate_id": identifier, "cbsa_code": str(tracts.cbsa_code.iloc[0]), "primary_zone_type": zone_type, "candidate_form": form, "core_tract_count": len(core_geoids), "bridge_tract_count": len(bridge_geoids), "total_tract_count": len(group), "coherence_status": "physical_evidence_unreviewed", "aspect_ratio": aspect_ratio, "spine_edge_count": spine_edges})
            for geoid in core_geoids:
                assignment_by_tract[geoid] = (identifier, sorted(group), False, None)
            for geoid in bridge_geoids:
                bridge = next(item for item in bridges if item["bridge_geoid"] == geoid and item["primary_zone"] == zone_type)
                assignment_by_tract[geoid] = (identifier, sorted(group), True, bridge)
    for tract in tracts.itertuples():
        assignment = assignment_by_tract.get(tract.tract_geoid)
        if assignment:
            identifier, group, is_bridge, bridge = assignment
            summary = f"bridge_core_neighbors={bridge['core_neighbors']}; bridge_spine_features={bridge['spine_feature_count']}" if is_bridge else f"physical_evidence; candidate_size={len(group)}"
            membership_rows.append({"run_id": run_id, "method_variant": "physical_evidence", "tract_geoid": tract.tract_geoid, "cbsa_code": str(tract.cbsa_code), "original_zone_type": tract.zone_type, "membership_status": "bridge" if is_bridge else "core", "candidate_id": identifier, "membership_stage": "physical_evidence_bridge" if is_bridge else "physical_evidence", "exclusion_reason": None, "evidence_summary": summary})
        else:
            membership_rows.append({"run_id": run_id, "method_variant": "physical_evidence", "tract_geoid": tract.tract_geoid, "cbsa_code": str(tract.cbsa_code), "original_zone_type": tract.zone_type, "membership_status": "unassigned", "candidate_id": None, "membership_stage": "physical_evidence", "exclusion_reason": None, "evidence_summary": "no qualifying same-zone component or bridge rule"})
    return pd.DataFrame(membership_rows), pd.DataFrame(candidate_rows), pd.DataFrame(edges)


def _classify_form(group: set[str], geometries: dict[str, Any], edges: list[dict[str, Any]], settings: dict[str, Any]) -> tuple[str, float | None, int]:
    """Use geometry compactness plus declared spine evidence; never editorial naming."""
    union = unary_union([geometries[geoid] for geoid in group])
    rectangle = union.minimum_rotated_rectangle
    coordinates = list(rectangle.exterior.coords)
    sides = [((coordinates[index][0] - coordinates[index + 1][0]) ** 2 + (coordinates[index][1] - coordinates[index + 1][1]) ** 2) ** 0.5 for index in range(4)]
    nonzero = [side for side in sides if side > 0]
    aspect_ratio = max(nonzero) / min(nonzero) if nonzero else None
    spine_edges = sum(1 for edge in edges if edge["final_decision"] == "accepted" and edge.get("spine_feature_count", 0) > 0 and edge["tract_geoid_low"] in group and edge["tract_geoid_high"] in group)
    if aspect_ratio is not None and aspect_ratio >= settings["corridor_minimum_aspect_ratio"] and spine_edges >= settings["corridor_minimum_spine_edges"]:
        return "corridor", round(aspect_ratio, 3), spine_edges
    if aspect_ratio is not None and aspect_ratio <= settings["district_maximum_aspect_ratio"]:
        return "district", round(aspect_ratio, 3), spine_edges
    return "unclassified", None if aspect_ratio is None else round(aspect_ratio, 3), spine_edges
