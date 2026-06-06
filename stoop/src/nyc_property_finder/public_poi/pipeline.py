"""High-level public baseline POI pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from nyc_property_finder.public_poi.build_dim import build_dim_public_poi
from nyc_property_finder.public_poi.config import ensure_snapshot_dirs
from nyc_property_finder.public_poi.sources import (
    ferry_path,
    gbfs_citibike,
    mta_bus,
    mta_subway,
    nyc_open_data,
    nypl_api,
    osm,
)
from nyc_property_finder.services.config import load_config
from nyc_property_finder.services.duckdb_service import DuckDBService


@dataclass(frozen=True)
class PublicPoiPipelineReport:
    """Summary of a public POI pipeline run."""

    dim_rows: int
    dim_with_coordinates: int
    database_path: str | None
    table_name: str
    source_count: int

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dict for logging, notebooks, or future CLI output."""

        return asdict(self)


def run(
    database_path: str | Path | None = None,
    write_database: bool = True,
    table_name: str = "dim_public_poi",
    schema: str = "property_explorer_gold",
) -> PublicPoiPipelineReport:
    """Fetch/load public POI sources and optionally write dim_public_poi."""

    snapshot_dirs = ensure_snapshot_dirs()
    bus_snapshots = mta_bus.fetch_snapshot(snapshot_dirs["mta_bus"])
    citi_bike_snapshot = gbfs_citibike.fetch_snapshot(snapshot_dirs["citi_bike"])
    bike_lane_snapshot = nyc_open_data.fetch_snapshot("bike_lanes", snapshot_dirs["nyc_open_data"])
    parks_snapshot = nyc_open_data.fetch_snapshot("parks", snapshot_dirs["nyc_open_data"])
    dog_runs_snapshot = nyc_open_data.fetch_snapshot("dog_runs", snapshot_dirs["nyc_open_data"])
    playgrounds_snapshot = nyc_open_data.fetch_snapshot(
        "playgrounds",
        snapshot_dirs["nyc_open_data"],
    )
    grocery_snapshot = nyc_open_data.fetch_json_snapshot(
        "grocery_stores",
        snapshot_dirs["nyc_open_data"],
    )
    dcwp_snapshot = nyc_open_data.fetch_json_snapshot(
        "dcwp_issued_licenses",
        snapshot_dirs["nyc_open_data"],
    )
    nypl_snapshot = nypl_api.fetch_snapshot(snapshot_dirs["nypl"])
    bpl_snapshot = nyc_open_data.fetch_json_snapshot(
        "bpl_libraries",
        snapshot_dirs["nyc_open_data"],
    )
    qpl_snapshot = snapshot_dirs["nyc_open_data"] / "qpl_branches.csv"
    if not qpl_snapshot.exists():
        qpl_snapshot = nyc_open_data.fetch_json_snapshot(
            "qpl_branches",
            snapshot_dirs["nyc_open_data"],
        )
    school_snapshot = nyc_open_data.fetch_json_snapshot(
        "public_schools",
        snapshot_dirs["nyc_open_data"],
    )
    farmers_market_snapshot = nyc_open_data.fetch_json_snapshot(
        "farmers_markets",
        snapshot_dirs["nyc_open_data"],
    )
    facilities_snapshot = nyc_open_data.fetch_json_snapshot(
        "facilities",
        snapshot_dirs["nyc_open_data"],
    )
    individual_landmarks_snapshot = nyc_open_data.fetch_snapshot(
        "individual_landmarks",
        snapshot_dirs["nyc_open_data"],
    )
    historic_districts_snapshot = nyc_open_data.fetch_snapshot(
        "historic_districts",
        snapshot_dirs["nyc_open_data"],
    )
    dcla_cultural_organizations_snapshot = nyc_open_data.fetch_json_snapshot(
        "dcla_cultural_organizations",
        snapshot_dirs["nyc_open_data"],
    )
    public_art_snapshot = nyc_open_data.fetch_json_snapshot(
        "public_art",
        snapshot_dirs["nyc_open_data"],
    )
    pharmacy_snapshot = osm.fetch_snapshot("pharmacies", snapshot_dirs["osm"])
    bank_snapshot = osm.fetch_snapshot("banks", snapshot_dirs["osm"])
    atm_snapshot = osm.fetch_snapshot("atms", snapshot_dirs["osm"])
    hardware_snapshot = osm.fetch_snapshot("hardware_stores", snapshot_dirs["osm"])
    post_office_snapshot = osm.fetch_snapshot("post_offices", snapshot_dirs["osm"])
    urgent_care_snapshot = osm.fetch_snapshot("urgent_care", snapshot_dirs["osm"])
    gym_snapshot = osm.fetch_snapshot("gyms", snapshot_dirs["osm"])
    hotel_snapshot = osm.fetch_snapshot("hotels", snapshot_dirs["osm"])

    frames = [
        mta_subway.load(),
        mta_bus.load(bus_snapshots),
        gbfs_citibike.load(citi_bike_snapshot),
        ferry_path.load(snapshot_dirs["ferry_path"] / "terminals.csv"),
        nyc_open_data.load_bike_lanes(bike_lane_snapshot),
        nyc_open_data.load_parks(parks_snapshot),
        nyc_open_data.load_dog_runs(dog_runs_snapshot),
        nyc_open_data.load_playgrounds(playgrounds_snapshot),
        nyc_open_data.load_grocery_stores(grocery_snapshot),
        nyc_open_data.load_laundromats(dcwp_snapshot),
        nyc_open_data.load_dry_cleaners(dcwp_snapshot),
        nypl_api.load(nypl_snapshot),
        nyc_open_data.load_bpl_branches(bpl_snapshot),
        nyc_open_data.load_qpl_branches(qpl_snapshot),
        nyc_open_data.load_public_schools(school_snapshot),
        nyc_open_data.load_farmers_markets(farmers_market_snapshot),
        nyc_open_data.load_hospitals(facilities_snapshot),
        nyc_open_data.load_individual_landmarks(individual_landmarks_snapshot),
        nyc_open_data.load_historic_districts(historic_districts_snapshot),
        nyc_open_data.load_dcla_museums(dcla_cultural_organizations_snapshot),
        nyc_open_data.load_public_art(public_art_snapshot),
        osm.load(pharmacy_snapshot, "pharmacies"),
        osm.load(bank_snapshot, "banks"),
        osm.load(atm_snapshot, "atms"),
        osm.load(hardware_snapshot, "hardware_stores"),
        osm.load(post_office_snapshot, "post_offices"),
        osm.load(urgent_care_snapshot, "urgent_care"),
        osm.load(gym_snapshot, "gyms"),
        osm.load(hotel_snapshot, "hotels"),
    ]
    dim_public_poi = build_dim_public_poi(frames)

    resolved_database_path = str(database_path) if database_path is not None else None
    if write_database:
        if database_path is None:
            database_path = load_config()["settings"]["database_path"]
        resolved_database_path = str(database_path)
        with DuckDBService(database_path) as duckdb_service:
            duckdb_service.write_dataframe(
                dim_public_poi,
                table_name=table_name,
                schema=schema,
                if_exists="replace",
            )

    return PublicPoiPipelineReport(
        dim_rows=len(dim_public_poi),
        dim_with_coordinates=int(dim_public_poi[["lat", "lon"]].notna().all(axis=1).sum()),
        database_path=resolved_database_path,
        table_name=f"{schema}.{table_name}",
        source_count=len(frames),
    )
