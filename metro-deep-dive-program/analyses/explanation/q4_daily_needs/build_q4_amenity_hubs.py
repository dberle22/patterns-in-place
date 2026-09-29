#!/usr/bin/env python3
"""Build reviewable POI-density amenity-hub candidates for Q4's two pilots.

The build deliberately clusters governed POI points rather than tracts. It uses
projected square cells as a transparent density screen, then joins qualifying
cells only when they share an edge. This produces stable, inspectable candidate
hubs and avoids implying that a routing, travel-time, or resident-access method
exists. A later reviewer may promote, reject, or replace a candidate version.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import duckdb
import pandas as pd
from pyproj import Transformer
from shapely import wkb
from shapely.geometry import box, mapping
from shapely.ops import transform, unary_union


METHOD_VERSION = "q4_amenity_hub_grid_v1"
RUN_DATE = "2026-09-22"
MARKETS = {
    "richmond_va": {"cbsa_code": "40060", "crs": "EPSG:26918"},
    "jacksonville_fl": {"cbsa_code": "27260", "crs": "EPSG:26917"},
}


@dataclass(frozen=True)
class CandidateVersion:
    """Declare one visible point-density sensitivity, not a final hub rule."""

    name: str
    cell_size_meters: int
    min_pois_per_cell: int
    recommended_for_review: bool = False


CANDIDATE_VERSIONS = (
    CandidateVersion("grid_250m_min_20", 250, 20, recommended_for_review=True),
    CandidateVersion("grid_500m_min_60", 500, 60),
)


def repo_root() -> Path:
    """Resolve the repository from this analysis folder without local paths."""

    return Path(__file__).resolve().parents[4]


def latest_run(output_root: Path, market: str) -> Path:
    """Select the only current POI run by its deterministic run-directory name."""

    candidates = sorted(path for path in (output_root / market).iterdir() if path.is_dir())
    if not candidates:
        raise FileNotFoundError(f"No POI output run found for {market}.")
    return candidates[-1]


def load_mapped_pois(path: Path) -> pd.DataFrame:
    """Read mapped points only while preserving all source and category evidence."""

    query = """
        SELECT
            source_record_key,
            source_run_id,
            mapping_version,
            category,
            sub_category,
            longitude,
            latitude
        FROM read_parquet(?)
        WHERE record_status = 'retained'
          AND mapping_status = 'mapped'
          AND longitude IS NOT NULL
          AND latitude IS NOT NULL
    """
    with duckdb.connect() as con:
        frame = con.execute(query, [str(path)]).fetchdf()

    if frame.empty:
        raise ValueError(f"No retained mapped POIs available in {path}.")
    if frame.source_record_key.duplicated().any():
        raise ValueError(f"Mapped POI source keys are not unique in {path}.")
    return frame


def assign_grid_cells(frame: pd.DataFrame, crs: str, cell_size: int) -> pd.DataFrame:
    """Project points, then assign a stable grid coordinate for density screening."""

    transformer = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    x, y = transformer.transform(frame.longitude.to_numpy(), frame.latitude.to_numpy())
    result = frame.copy()
    result["x_meters"] = x
    result["y_meters"] = y
    # Floor-based coordinates are deterministic in the declared local CRS and
    # avoid round-off-dependent string bins at cell boundaries.
    result["grid_x"] = [math.floor(value / cell_size) for value in x]
    result["grid_y"] = [math.floor(value / cell_size) for value in y]
    return result


def connected_components(cells: set[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    """Return shared-edge components, excluding diagonal-only bridges by design."""

    remaining = set(cells)
    components: list[list[tuple[int, int]]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        stack = [seed]
        component = [seed]
        while stack:
            x, y = stack.pop()
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
                    component.append(neighbor)
        components.append(sorted(component))
    return sorted(components, key=lambda cells: cells[0])


def build_candidate(
    frame: pd.DataFrame, market: str, version: CandidateVersion
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Construct one candidate version and its hub, membership, and mix surfaces."""

    candidate_status = (
        "selected_for_workbench" if version.recommended_for_review else "sensitivity"
    )
    projected = assign_grid_cells(frame, MARKETS[market]["crs"], version.cell_size_meters)
    cell_counts = projected.groupby(["grid_x", "grid_y"], sort=True).size()
    qualifying_cells = {
        (int(grid_x), int(grid_y))
        for (grid_x, grid_y), count in cell_counts.items()
        if count >= version.min_pois_per_cell
    }
    components = connected_components(qualifying_cells)
    cell_to_hub: dict[tuple[int, int], str] = {}
    hub_rows: list[dict[str, object]] = []

    for position, component in enumerate(components, start=1):
        hub_id = f"{MARKETS[market]['cbsa_code']}_{version.name}_{position:03d}"
        for cell in component:
            cell_to_hub[cell] = hub_id
        polygons = [
            box(
                grid_x * version.cell_size_meters,
                grid_y * version.cell_size_meters,
                (grid_x + 1) * version.cell_size_meters,
                (grid_y + 1) * version.cell_size_meters,
            )
            for grid_x, grid_y in component
        ]
        geometry = unary_union(polygons)
        hub_rows.append(
            {
                "method_version": METHOD_VERSION,
                "candidate_version": version.name,
                "candidate_status": candidate_status,
                "recommended_for_review": version.recommended_for_review,
                "cbsa_code": MARKETS[market]["cbsa_code"],
                "market_slug": market,
                "amenity_hub_id": hub_id,
                "cell_size_meters": version.cell_size_meters,
                "min_pois_per_cell": version.min_pois_per_cell,
                "cell_count": len(component),
                "cluster_area_sq_km": geometry.area / 1_000_000,
                "geometry_wkb": geometry.wkb,
                "geometry_geojson": json.dumps(mapping(geometry), separators=(",", ":")),
            }
        )

    # Sparse basket sensitivities may have no qualifying cells. That is a
    # visible candidate result, not an assignment failure or a zero-amenity claim.
    if not hub_rows:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    memberships = projected.loc[
        projected.apply(lambda row: (int(row.grid_x), int(row.grid_y)) in cell_to_hub, axis=1)
    ].copy()
    memberships["amenity_hub_id"] = memberships.apply(
        lambda row: cell_to_hub[(int(row.grid_x), int(row.grid_y))], axis=1
    )
    memberships["method_version"] = METHOD_VERSION
    memberships["candidate_version"] = version.name
    memberships["cbsa_code"] = MARKETS[market]["cbsa_code"]
    memberships["market_slug"] = market
    memberships["candidate_status"] = candidate_status
    memberships["recommended_for_review"] = version.recommended_for_review
    memberships = memberships.drop(columns=["x_meters", "y_meters", "grid_x", "grid_y"])

    if memberships.empty:
        return pd.DataFrame(hub_rows), memberships, pd.DataFrame()

    hub_counts = memberships.groupby("amenity_hub_id").agg(
        poi_count=("source_record_key", "size"),
        category_count=("category", "nunique"),
        sub_category_count=("sub_category", "nunique"),
        centroid_longitude=("longitude", "mean"),
        centroid_latitude=("latitude", "mean"),
    ).reset_index()
    hubs = pd.DataFrame(hub_rows).merge(hub_counts, on="amenity_hub_id", how="left")
    hubs["poi_density_per_sq_km"] = hubs.poi_count / hubs.cluster_area_sq_km
    category_mix = memberships.groupby(["amenity_hub_id", "category"], as_index=False).agg(
        poi_count=("source_record_key", "size")
    )
    category_mix["hub_poi_count"] = category_mix.amenity_hub_id.map(
        hub_counts.set_index("amenity_hub_id").poi_count
    )
    category_mix["poi_share"] = category_mix.poi_count / category_mix.hub_poi_count
    category_mix["method_version"] = METHOD_VERSION
    category_mix["candidate_version"] = version.name
    category_mix["cbsa_code"] = MARKETS[market]["cbsa_code"]
    category_mix["market_slug"] = market
    return hubs, memberships, category_mix


def validate_outputs(hubs: pd.DataFrame, memberships: pd.DataFrame) -> None:
    """Fail loudly on broken membership, threshold, or geometry accounting."""

    if memberships.duplicated(["candidate_version", "source_record_key"]).any():
        raise ValueError("A POI received multiple memberships in one candidate version.")
    member_counts = memberships.groupby("amenity_hub_id").size()
    expected_counts = hubs.set_index("amenity_hub_id").poi_count.astype(int)
    if not member_counts.sort_index().equals(expected_counts.sort_index()):
        raise ValueError("Hub POI counts do not reconcile to the membership table.")
    if (hubs.cell_count < 1).any() or (hubs.cluster_area_sq_km <= 0).any():
        raise ValueError("A candidate hub has an invalid cell count or geometry area.")


def write_parquet(frame: pd.DataFrame, destination: Path) -> None:
    """Write portable local review artifacts without creating a managed mart."""

    with duckdb.connect() as con:
        con.register("frame", frame)
        con.execute("COPY frame TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(destination)])


def write_geojson(hubs: pd.DataFrame, destination: Path) -> None:
    """Expose candidate geometry for map review without a GIS-specific reader."""

    features = []
    for row in hubs.itertuples(index=False):
        properties = {
            key: value
            for key, value in row._asdict().items()
            if key not in {"geometry_wkb", "geometry_geojson"}
        }
        features.append({"type": "Feature", "geometry": json.loads(row.geometry_geojson), "properties": properties})
    destination.write_text(json.dumps({"type": "FeatureCollection", "features": features}) + "\n")


def write_review_maps(hubs: pd.DataFrame, memberships: pd.DataFrame, output_dir: Path) -> None:
    """Write dependency-free hub-outline maps for the required human review step."""

    for (market, version), candidate_hubs in hubs.groupby(["market_slug", "candidate_version"]):
        candidate_members = memberships.loc[
            (memberships.market_slug == market)
            & (memberships.candidate_version == version)
        ]
        inverse = Transformer.from_crs(MARKETS[market]["crs"], "EPSG:4326", always_xy=True)
        geometries = []
        for row in candidate_hubs.itertuples(index=False):
            geometries.append(transform(inverse.transform, wkb.loads(bytes(row.geometry_wkb))))
        west = min(geometry.bounds[0] for geometry in geometries)
        south = min(geometry.bounds[1] for geometry in geometries)
        east = max(geometry.bounds[2] for geometry in geometries)
        north = max(geometry.bounds[3] for geometry in geometries)
        padding = max(east - west, north - south) * 0.03
        west, south, east, north = west - padding, south - padding, east + padding, north + padding
        width, height = 1000, 1000

        def point_to_svg(longitude: float, latitude: float) -> tuple[float, float]:
            x = 30 + (longitude - west) / (east - west) * (width - 60)
            y = height - 30 - (latitude - south) / (north - south) * (height - 60)
            return x, y

        paths = []
        for geometry in geometries:
            polygons = geometry.geoms if geometry.geom_type == "MultiPolygon" else [geometry]
            for polygon in polygons:
                coordinates = [point_to_svg(longitude, latitude) for longitude, latitude in polygon.exterior.coords]
                path = " ".join(
                    f"{'M' if index == 0 else 'L'}{x:.1f},{y:.1f}"
                    for index, (x, y) in enumerate(coordinates)
                ) + " Z"
                paths.append(f'<path d="{path}"/>')
        points = "".join(
            f'<circle cx="{point_to_svg(row.longitude, row.latitude)[0]:.1f}" '
            f'cy="{point_to_svg(row.longitude, row.latitude)[1]:.1f}" r="0.7"/>'
            for row in candidate_members.itertuples(index=False)
        )
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>'
            f'<g fill="#5e3c99" fill-opacity="0.25">{points}</g>'
            f'<g fill="none" stroke="#e66101" stroke-width="1.2">{"".join(paths)}</g>'
            f'<text x="30" y="28" font-family="sans-serif" font-size="18">{market} — {version}</text></svg>\n'
        )
        (output_dir / f"q4_amenity_hub_review_{market}_{version}.svg").write_text(svg)


def write_method_record(output_dir: Path, source_runs: dict[str, Path], hubs: pd.DataFrame) -> None:
    """Record candidate intent and observed scale before a human promotes a rule."""

    lines = [
        "# Q4 Amenity-Hub Candidate Method Record",
        "",
        f"**Method version:** `{METHOD_VERSION}`  ",
        f"**Built:** {RUN_DATE}  ",
        "**Promotion status:** `grid_250m_min_20` is selected for the first Q4",
        "workbench review; `grid_500m_min_60` remains a retained sensitivity. Neither",
        "is a basket-specific or cross-analysis promoted classification.",
        "",
        "## Candidate universe",
        "",
        "All retained POIs with `mapping_status = 'mapped'` are included. Epic 2 has",
        "not yet declared broad-livability or errands/essentials baskets, so this is a",
        "spatial inventory candidate rather than a basket-specific livability result.",
        "Unmapped POIs are excluded from membership but remain a documented coverage state.",
        "",
        "## Construction",
        "",
        "Each point is projected into the market's declared local CRS and assigned to a",
        "square cell. A cell qualifies only when it meets the version's POI count. Only",
        "qualifying cells that share an edge join one hub; diagonal contact never joins",
        "a hub. Hub geometry is the union of qualifying cells. This is a reviewable",
        "density construction, not a route, travel-time, barrier, or resident-access model.",
        "",
        "| Candidate version | Cell size | Minimum POIs/cell | Role |",
        "|---|---:|---:|---|",
    ]
    for version in CANDIDATE_VERSIONS:
        role = "recommended for first review" if version.recommended_for_review else "compact sensitivity"
        lines.append(
            f"| `{version.name}` | {version.cell_size_meters} m | {version.min_pois_per_cell} | {role} |"
        )
    lines.extend(["", "## Inputs", ""])
    for market, path in source_runs.items():
        lines.append(f"- `{MARKETS[market]['cbsa_code']}`: `{path.relative_to(repo_root())}`")
    lines.extend(["", "## Observed candidate counts", "", "| Market | Version | Hubs | Member POIs |", "|---|---|---:|---:|"])
    summary = hubs.groupby(["market_slug", "candidate_version"], as_index=False).agg(
        hubs=("amenity_hub_id", "size"), member_pois=("poi_count", "sum")
    )
    for row in summary.itertuples(index=False):
        lines.append(f"| {row.market_slug} | `{row.candidate_version}` | {row.hubs:,} | {row.member_pois:,} |")
    lines.extend([
        "",
        "## Required review",
        "",
        "- inspect membership and category mix for fragmented hubs and implausible bridges;",
        "- compare both sensitivity versions before treating the selected workbench",
        "  candidate as stable;",
        "- replace the all-mapped universe with declared basket variants in later work; and",
        "- keep Infrastructure as map context only until a separate barrier/network method exists.",
        "",
    ])
    (output_dir / "EXPLANATION_Q4_AMENITY_HUB_METHOD_RECORD.md").write_text("\n".join(lines))


def main() -> None:
    """Build both pilot markets into local, versioned Q4 review artifacts."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "outputs" / METHOD_VERSION,
        help="Directory for local review artifacts.",
    )
    args = parser.parse_args()
    poi_output_root = repo_root() / "metro-deep-dive-program" / "engines" / "poi" / "outputs"
    args.output_dir.mkdir(parents=True, exist_ok=True)

    hub_frames: list[pd.DataFrame] = []
    membership_frames: list[pd.DataFrame] = []
    mix_frames: list[pd.DataFrame] = []
    source_runs: dict[str, Path] = {}
    for market in MARKETS:
        source_run = latest_run(poi_output_root, market)
        source_runs[market] = source_run
        source = source_run / "classified" / "poi_classified_place.parquet"
        points = load_mapped_pois(source)
        for version in CANDIDATE_VERSIONS:
            hubs, memberships, category_mix = build_candidate(points, market, version)
            hub_frames.append(hubs)
            membership_frames.append(memberships)
            mix_frames.append(category_mix)

    hubs = pd.concat(hub_frames, ignore_index=True)
    memberships = pd.concat(membership_frames, ignore_index=True)
    category_mix = pd.concat(mix_frames, ignore_index=True)
    validate_outputs(hubs, memberships)
    write_parquet(hubs, args.output_dir / "q4_amenity_hub_candidates.parquet")
    write_parquet(memberships, args.output_dir / "q4_amenity_hub_membership.parquet")
    write_parquet(category_mix, args.output_dir / "q4_amenity_hub_category_mix.parquet")
    write_geojson(hubs, args.output_dir / "q4_amenity_hub_candidates.geojson")
    write_review_maps(hubs, memberships, args.output_dir)
    write_method_record(args.output_dir, source_runs, hubs)

    artifact_checksums = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(args.output_dir.glob("q4_amenity_hub_*"))
        if path.is_file()
    }
    manifest = {
        "method_version": METHOD_VERSION,
        "built": RUN_DATE,
        "candidate_status": "selected_for_workbench_with_sensitivity",
        "candidate_universe": "retained mapped POIs; no analysis basket declared yet",
        "source_runs": {market: str(path.relative_to(repo_root())) for market, path in source_runs.items()},
        "artifacts": artifact_checksums,
        "hub_count": int(len(hubs)),
        "membership_count": int(len(memberships)),
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"output_dir": str(args.output_dir), **manifest}, indent=2))


if __name__ == "__main__":
    main()
