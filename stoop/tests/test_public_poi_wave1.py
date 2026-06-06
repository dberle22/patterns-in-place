import json
import zipfile

import pandas as pd
import pytest

from nyc_property_finder.public_poi.pipeline import run as run_public_poi
from nyc_property_finder.public_poi.sources import (
    gbfs_citibike,
    mta_bus,
    mta_subway,
    nyc_open_data,
    nypl_api,
    osm,
)
from nyc_property_finder.services.duckdb_service import DuckDBService


def test_mta_subway_loads_stations_entrances_and_shapes(tmp_path) -> None:
    gtfs_path = tmp_path / "subway.zip"
    with zipfile.ZipFile(gtfs_path, "w") as gtfs:
        gtfs.writestr(
            "stops.txt",
            "\n".join(
                [
                    "stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station",
                    "101,Main St,40.7,-73.9,1,",
                    "101N,Main St,40.7,-73.9,,101",
                    "E01,Main St Entrance,40.701,-73.901,2,101",
                ]
            ),
        )
        gtfs.writestr("routes.txt", "route_id,route_short_name\nA,A\n")
        gtfs.writestr("trips.txt", "trip_id,route_id\ntrip_a,A\n")
        gtfs.writestr("stop_times.txt", "trip_id,stop_id\ntrip_a,101N\n")
        gtfs.writestr(
            "shapes.txt",
            "\n".join(
                [
                    "shape_id,shape_pt_sequence,shape_pt_lat,shape_pt_lon",
                    "shape_a,1,40.0,-74.0",
                    "shape_a,2,41.0,-73.0",
                ]
            ),
        )

    rows = mta_subway.load(gtfs_path)

    assert rows["category"].tolist() == ["subway_station", "subway_entrance", "subway_line"]
    station = rows.loc[rows["category"] == "subway_station"].iloc[0]
    entrance = rows.loc[rows["category"] == "subway_entrance"].iloc[0]
    shape = rows.loc[rows["category"] == "subway_line"].iloc[0]
    assert json.loads(station["attributes"])["lines"] == ["A"]
    assert json.loads(entrance["attributes"])["parent_station"] == "101"
    assert shape["lat"] == 40.5
    assert json.loads(shape["attributes"])["point_count"] == 2


def test_mta_bus_load_dedupes_stops_across_borough_feeds(tmp_path) -> None:
    paths = {}
    for borough in ("bronx", "queens"):
        path = tmp_path / f"{borough}.zip"
        with zipfile.ZipFile(path, "w") as gtfs:
            gtfs.writestr(
                "stops.txt",
                "\n".join(
                    [
                        "stop_id,stop_name,stop_lat,stop_lon,location_type",
                        "M1,Boundary Stop,40.7,-73.9,",
                    ]
                ),
            )
        paths[borough] = path

    rows = mta_bus.load(paths)

    assert len(rows) == 1
    assert rows.iloc[0]["category"] == "bus_stop"
    assert rows.iloc[0]["source_id"] == "bus_stop:M1"


def test_gbfs_citibike_load_parses_station_information(tmp_path) -> None:
    snapshot = tmp_path / "station_information.json"
    snapshot.write_text(
        json.dumps(
            {
                "data": {
                    "stations": [
                        {
                            "station_id": "abc",
                            "name": "Dock A",
                            "lat": 40.7,
                            "lon": -73.9,
                            "capacity": 10,
                            "region_id": "71",
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    rows = gbfs_citibike.load(snapshot)

    assert len(rows) == 1
    assert rows.iloc[0]["source_id"] == "citi_bike_station:abc"
    assert json.loads(rows.iloc[0]["attributes"])["capacity"] == 10


def test_nyc_open_data_load_parks_filters_typecategory_and_centroids(tmp_path) -> None:
    snapshot = tmp_path / "parks.geojson"
    snapshot.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "gispropnum": "M010",
                            "signname": "Square Park",
                            "typecategory": "Neighborhood Park",
                            "acres": "2.5",
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [-73.99, 40.70],
                                    [-73.98, 40.70],
                                    [-73.98, 40.71],
                                    [-73.99, 40.71],
                                    [-73.99, 40.70],
                                ]
                            ],
                        },
                    },
                    {
                        "type": "Feature",
                        "properties": {
                            "gispropnum": "Q999",
                            "signname": "Maintenance Strip",
                            "typecategory": "Parkway",
                            "acres": "1",
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-73.8, 40.7],
                        },
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    rows = nyc_open_data.load_parks(snapshot)

    assert len(rows) == 1
    row = rows.iloc[0]
    assert row["category"] == "park"
    assert row["subcategory"] == "Neighborhood Park"
    assert row["source_id"] == "park:M010"
    assert row["name"] == "Square Park"
    assert row["lat"] == pytest.approx(40.705, abs=0.001)
    assert row["lon"] == pytest.approx(-73.985, abs=0.001)
    assert json.loads(row["attributes"]) == {
        "acres": 2.5,
        "gispropnum": "M010",
        "typecategory": "Neighborhood Park",
    }


def test_nyc_open_data_load_dog_runs_and_playgrounds(tmp_path) -> None:
    dog_runs_snapshot = tmp_path / "dog_runs.geojson"
    dog_runs_snapshot.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "objectid": "10",
                            "name": "Run A",
                            "fenced": "Yes",
                            "on_leash": "No",
                            "gispropnum": "B001",
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-73.95, 40.68],
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    playgrounds_snapshot = tmp_path / "playgrounds.geojson"
    playgrounds_snapshot.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "objectid": "20",
                            "name": "Play A",
                            "type": "Children's Play Area",
                            "gispropnum": "X002",
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-73.90, 40.82],
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    dog_runs = nyc_open_data.load_dog_runs(dog_runs_snapshot)
    playgrounds = nyc_open_data.load_playgrounds(playgrounds_snapshot)

    assert dog_runs.iloc[0]["source_id"] == "dog_run:10"
    assert dog_runs.iloc[0]["category"] == "dog_run"
    assert json.loads(dog_runs.iloc[0]["attributes"]) == {
        "fenced": True,
        "gispropnum": "B001",
        "on_leash": False,
    }
    assert playgrounds.iloc[0]["source_id"] == "playground:20"
    assert playgrounds.iloc[0]["category"] == "playground"
    assert playgrounds.iloc[0]["subcategory"] == "Children's Play Area"
    assert json.loads(playgrounds.iloc[0]["attributes"]) == {
        "gispropnum": "X002",
        "type": "Children's Play Area",
    }


def test_nyc_open_data_load_grocery_stores_filters_to_nyc_supermarkets(tmp_path) -> None:
    snapshot = tmp_path / "grocery.json"
    snapshot.write_text(
        json.dumps(
            [
                {
                    "county": "KINGS",
                    "license_number": "123",
                    "operation_type": "Store",
                    "estab_type": "AC",
                    "entity_name": "Good Food Corp",
                    "dba_name": "Good Food Supermarket",
                    "street_number": "10",
                    "street_name": "Main St",
                    "city": "BROOKLYN",
                    "state": "NY",
                    "zip_code": "11201",
                    "square_footage": "2000",
                    "georeference": {"type": "Point", "coordinates": [-73.99, 40.7]},
                },
                {
                    "county": "KINGS",
                    "license_number": "124",
                    "entity_name": "Tiny Grocery",
                    "dba_name": "Tiny Grocery",
                    "square_footage": "900",
                    "georeference": {"type": "Point", "coordinates": [-73.98, 40.71]},
                },
                {
                    "county": "ERIE",
                    "license_number": "125",
                    "dba_name": "Buffalo Supermarket",
                    "square_footage": "10000",
                    "georeference": {"type": "Point", "coordinates": [-78.8, 42.9]},
                },
            ]
        ),
        encoding="utf-8",
    )

    rows = nyc_open_data.load_grocery_stores(snapshot)

    assert len(rows) == 1
    row = rows.iloc[0]
    assert row["source_id"] == "grocery_store:123"
    assert row["category"] == "grocery_store"
    assert row["subcategory"] == "supermarket"
    assert row["address"] == "10 Main St BROOKLYN NY 11201"
    assert row["lat"] == 40.7
    assert row["lon"] == -73.99
    assert json.loads(row["attributes"])["square_footage"] == 2000


def test_nyc_open_data_load_laundromats_and_dry_cleaners_from_dcwp(tmp_path) -> None:
    snapshot = tmp_path / "dcwp.json"
    snapshot.write_text(
        json.dumps(
            [
                {
                    "license_nbr": "L1",
                    "business_name": "Sparkle Laundromat Inc",
                    "business_category": "Industrial Laundry",
                    "license_status": "Active",
                    "license_type": "Premises",
                    "address_building": "20",
                    "address_street_name": "Wash Ave",
                    "address_city": "BROOKLYN",
                    "address_state": "NY",
                    "address_zip": "11211",
                    "latitude": "40.7",
                    "longitude": "-73.9",
                },
                {
                    "license_nbr": "D1",
                    "business_name": "Fresh Dry Cleaners",
                    "business_category": "Industrial Laundry",
                    "license_status": "Ready for Renewal",
                    "latitude": "40.71",
                    "longitude": "-73.91",
                },
                {
                    "license_nbr": "X1",
                    "business_name": "Expired Laundromat",
                    "business_category": "Industrial Laundry",
                    "license_status": "Expired",
                    "latitude": "40.72",
                    "longitude": "-73.92",
                },
            ]
        ),
        encoding="utf-8",
    )

    laundromats = nyc_open_data.load_laundromats(snapshot)
    dry_cleaners = nyc_open_data.load_dry_cleaners(snapshot)

    assert laundromats["source_id"].tolist() == ["laundromat:L1"]
    assert dry_cleaners["source_id"].tolist() == ["dry_cleaner:D1"]
    assert laundromats.iloc[0]["address"] == "20 Wash Ave BROOKLYN NY 11211"


def test_osm_load_parses_geojson_features(tmp_path) -> None:
    snapshot = tmp_path / "osm.geojson"
    snapshot.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [-73.95, 40.72]},
                        "properties": {
                            "osm_id": "node/1",
                            "tag_value": "pharmacy",
                            "name": "Corner Pharmacy",
                            "amenity": "pharmacy",
                            "addr:housenumber": "1",
                            "addr:street": "Main St",
                            "addr:city": "Brooklyn",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    rows = osm.load(snapshot, "pharmacies")

    assert len(rows) == 1
    row = rows.iloc[0]
    assert row["source_id"] == "pharmacy:node/1"
    assert row["category"] == "pharmacy"
    assert row["address"] == "1 Main St Brooklyn"
    assert json.loads(row["attributes"])["amenity"] == "pharmacy"


def test_osm_hotel_load_parses_geojson_features(tmp_path) -> None:
    snapshot = tmp_path / "hotels.geojson"
    snapshot.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [-73.9855, 40.758]},
                        "properties": {
                            "osm_id": "node/99",
                            "tag_value": "hotel",
                            "name": "Hotel Example",
                            "tourism": "hotel",
                            "addr:housenumber": "123",
                            "addr:street": "Broadway",
                            "addr:city": "New York",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    rows = osm.load(snapshot, "hotels")

    assert len(rows) == 1
    row = rows.iloc[0]
    assert row["source_id"] == "hotel:node/99"
    assert row["category"] == "hotel"
    assert row["subcategory"] == "hotel"
    assert row["address"] == "123 Broadway New York"
    assert json.loads(row["attributes"])["tourism"] == "hotel"


def test_osm_urgent_care_load_applies_manual_curation(tmp_path) -> None:
    snapshot = tmp_path / "urgent_care.geojson"
    snapshot.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [-73.95, 40.72]},
                        "properties": {
                            "osm_id": "node/1",
                            "tag_value": "clinic",
                            "name": "CityMD",
                            "amenity": "clinic",
                        },
                    },
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [-73.96, 40.73]},
                        "properties": {
                            "osm_id": "node/2",
                            "tag_value": "clinic",
                            "name": "Downtown Dialysis Clinic",
                            "amenity": "clinic",
                        },
                    },
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [-73.97, 40.74]},
                        "properties": {
                            "osm_id": "node/3",
                            "tag_value": "clinic",
                            "name": "Neighborhood Family Practice",
                            "amenity": "clinic",
                        },
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    rows = osm.load(snapshot, "urgent_care")

    assert rows["source_id"].tolist() == ["urgent_care:node/1"]
    assert rows.iloc[0]["name"] == "CityMD"


def test_wave4_library_loaders_normalize_three_systems(tmp_path) -> None:
    nypl_snapshot = tmp_path / "nypl.json"
    nypl_snapshot.write_text(
        json.dumps(
            {
                "data": [
                    {
                        "id": "1",
                        "attributes": {
                            "full-name": "115th Street Library",
                            "symbol": "HU",
                            "phone": "(212) 666-9393",
                            "address": {
                                "address1": "203 West 115th Street",
                                "city": "New York",
                                "region": "NY",
                                "postal-code": "10026",
                                "latitude": 40.8028,
                                "longitude": -73.9532,
                            },
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    bpl_snapshot = tmp_path / "bpl.json"
    bpl_snapshot.write_text(
        json.dumps(
            [
                {
                    "name": "Central",
                    "system": "BPL",
                    "housenum": "10",
                    "streetname": "Grand Army Plaza",
                    "city": "Brooklyn",
                    "zip": "11238",
                    "bin": "3029665",
                    "the_geom": {"type": "Point", "coordinates": [-73.9681, 40.6721]},
                }
            ]
        ),
        encoding="utf-8",
    )
    qpl_snapshot = tmp_path / "qpl.json"
    qpl_snapshot.write_text(
        json.dumps(
            [
                {
                    "name": "Bayside",
                    "address": "214-20 Northern Boulevard",
                    "city": "Bayside",
                    "postcode": "11361",
                    "bin": "4073330215",
                    "latitude": "40.760363",
                    "longitude": "-73.768588",
                }
            ]
        ),
        encoding="utf-8",
    )

    rows = pd.concat(
        [
            nypl_api.load(nypl_snapshot),
            nyc_open_data.load_bpl_branches(bpl_snapshot),
            nyc_open_data.load_qpl_branches(qpl_snapshot),
        ],
        ignore_index=True,
    )

    assert rows["category"].tolist() == ["public_library", "public_library", "public_library"]
    assert rows["subcategory"].tolist() == ["nypl", "bpl", "qpl"]
    assert rows["source_id"].tolist() == [
        "public_library:nypl:1",
        "public_library:bpl:3029665",
        "public_library:qpl:4073330215",
    ]


def test_wave4_civic_loaders_normalize_schools_markets_and_hospitals(tmp_path) -> None:
    schools_snapshot = tmp_path / "schools.json"
    schools_snapshot.write_text(
        json.dumps(
            [
                {
                    "fiscal_year": "2025",
                    "location_code": "M015",
                    "location_name": "P.S. 015 Roberto Clemente",
                    "managed_by_name": "DOE",
                    "status_descriptions": "Open",
                    "location_category_description": "Elementary",
                    "primary_address_line_1": "333 EAST 4 STREET",
                    "location_1": {"type": "Point", "coordinates": [-73.978747, 40.722075]},
                },
                {
                    "fiscal_year": "2024",
                    "location_code": "M015",
                    "location_name": "Old P.S. 015",
                    "managed_by_name": "DOE",
                    "status_descriptions": "Open",
                    "location_1": {"type": "Point", "coordinates": [-73.9, 40.7]},
                },
            ]
        ),
        encoding="utf-8",
    )
    markets_snapshot = tmp_path / "markets.json"
    markets_snapshot.write_text(
        json.dumps(
            [
                {
                    "year": "2025",
                    "marketname": "175th Street Greenmarket",
                    "borough": "Manhattan",
                    "streetaddress": "W. 175th St.",
                    "latitude": "40.845948",
                    "longitude": "-73.937811",
                    "accepts_ebt": "Yes",
                    "open_year_round": "No",
                }
            ]
        ),
        encoding="utf-8",
    )
    hospitals_snapshot = tmp_path / "hospitals.json"
    hospitals_snapshot.write_text(
        json.dumps(
            [
                {
                    "uid": "H1",
                    "facname": "Bellevue Hospital Center",
                    "facsubgrp": "HOSPITALS AND CLINICS",
                    "factype": "HOSPITAL",
                    "address": "462 1 AVENUE",
                    "city": "New York",
                    "latitude": "40.739",
                    "longitude": "-73.975",
                },
                {
                    "uid": "C1",
                    "facname": "Extension Clinic",
                    "facsubgrp": "HOSPITALS AND CLINICS",
                    "factype": "HOSPITAL EXTENSION CLINIC",
                    "latitude": "40.7",
                    "longitude": "-73.9",
                },
            ]
        ),
        encoding="utf-8",
    )

    schools = nyc_open_data.load_public_schools(schools_snapshot)
    markets = nyc_open_data.load_farmers_markets(markets_snapshot)
    hospitals = nyc_open_data.load_hospitals(hospitals_snapshot)

    assert schools["source_id"].tolist() == ["public_school:M015"]
    assert schools.iloc[0]["name"] == "P.S. 015 Roberto Clemente"
    assert markets.iloc[0]["source_id"].startswith("farmers_market:2025")
    assert json.loads(markets.iloc[0]["attributes"])["accepts_ebt"] is True
    assert hospitals["source_id"].tolist() == ["hospital:H1"]
    assert hospitals.iloc[0]["subcategory"] == "HOSPITAL"


def test_wave5_culture_heritage_loaders_normalize_sources(tmp_path) -> None:
    individual_landmarks_snapshot = tmp_path / "individual_landmarks.geojson"
    individual_landmarks_snapshot.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "lpc_lpnumb": "LP-00001",
                            "lpc_name": "Sample House",
                            "landmarkty": "Individual Landmark",
                            "address": "1 Sample Street",
                            "borough": "MN",
                            "desdate": "1965-01-01T00:00:00.000",
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [-73.99, 40.70],
                                    [-73.98, 40.70],
                                    [-73.98, 40.71],
                                    [-73.99, 40.71],
                                    [-73.99, 40.70],
                                ]
                            ],
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    historic_districts_snapshot = tmp_path / "historic_districts.geojson"
    historic_districts_snapshot.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "lp_number": "LP-01000",
                            "area_name": "Sample Historic District",
                            "borough": "BK",
                            "status_of_": "DESIGNATED",
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [-73.95, 40.68],
                                    [-73.94, 40.68],
                                    [-73.94, 40.69],
                                    [-73.95, 40.69],
                                    [-73.95, 40.68],
                                ]
                            ],
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    dcla_snapshot = tmp_path / "dcla.json"
    dcla_snapshot.write_text(
        json.dumps(
            [
                {
                    "organization_name": "Sample Museum",
                    "address": "2 Museum Way",
                    "city": "New York",
                    "state": "NY",
                    "postcode": "10001",
                    "discipline": "Museum",
                    "borough": "Manhattan",
                    "latitude": "40.75",
                    "longitude": "-73.98",
                    "bin": "1000001",
                },
                {
                    "organization_name": "Sample Theater",
                    "discipline": "Theater",
                    "latitude": "40.75",
                    "longitude": "-73.98",
                },
            ]
        ),
        encoding="utf-8",
    )
    public_art_snapshot = tmp_path / "public_art.json"
    public_art_snapshot.write_text(
        json.dumps(
            [
                {
                    "title": "Sample Memorial",
                    "artwork_type1": "Sculpture",
                    "location_name": "Sample Park",
                    "address": "3 Park Road",
                    "city": "Brooklyn",
                    "zip_code": "11201",
                    "borough": "Brooklyn",
                    "latitude": "40.714761,",
                    "longitude": "-73.963162",
                    "date_dedicated": "1999",
                }
            ]
        ),
        encoding="utf-8",
    )

    landmarks = nyc_open_data.load_individual_landmarks(individual_landmarks_snapshot)
    districts = nyc_open_data.load_historic_districts(historic_districts_snapshot)
    museums = nyc_open_data.load_dcla_museums(dcla_snapshot)
    art = nyc_open_data.load_public_art(public_art_snapshot)

    assert landmarks.iloc[0]["source_id"] == "landmark:individual:LP-00001"
    assert landmarks.iloc[0]["subcategory"] == "Individual Landmark"
    assert districts.iloc[0]["source_id"] == "landmark:historic_district:LP-01000"
    assert districts.iloc[0]["subcategory"] == "historic_district"
    assert museums["source_id"].tolist() == ["museum_institutional:1000001"]
    assert museums.iloc[0]["subcategory"] == "museum"
    assert art.iloc[0]["category"] == "public_art"
    assert art.iloc[0]["lat"] == pytest.approx(40.714761)


def test_public_poi_pipeline_writes_wave1_sources(monkeypatch, tmp_path) -> None:
    frame = pd.DataFrame(
        [
            {
                "source_system": "test",
                "source_id": "one",
                "category": "bus_stop",
                "subcategory": "test",
                "name": "One",
                "address": "",
                "lat": 40.7,
                "lon": -73.9,
                "attributes": "{}",
            }
        ]
    )

    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.mta_bus.fetch_snapshot",
        lambda path: {},
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.gbfs_citibike.fetch_snapshot",
        lambda path: path,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.fetch_snapshot",
        lambda key, path: path,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.fetch_json_snapshot",
        lambda key, path: path,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nypl_api.fetch_snapshot",
        lambda path: path,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.osm.fetch_snapshot",
        lambda key, path: path,
    )
    monkeypatch.setattr("nyc_property_finder.public_poi.pipeline.mta_subway.load", lambda: frame)
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.mta_bus.load",
        lambda snapshots: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.gbfs_citibike.load",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.ferry_path.load",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_bike_lanes",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_parks",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_dog_runs",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_playgrounds",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_grocery_stores",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_laundromats",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_dry_cleaners",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nypl_api.load",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_bpl_branches",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_qpl_branches",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_public_schools",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_farmers_markets",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_hospitals",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_individual_landmarks",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_historic_districts",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_dcla_museums",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.nyc_open_data.load_public_art",
        lambda snapshot: frame,
    )
    monkeypatch.setattr(
        "nyc_property_finder.public_poi.pipeline.osm.load",
        lambda snapshot, key: frame,
    )

    database_path = tmp_path / "pois.duckdb"
    report = run_public_poi(database_path=database_path)

    assert report.dim_rows == 29
    with DuckDBService(database_path, read_only=True) as duckdb_service:
        rows = duckdb_service.query_df(
            "SELECT COUNT(*) AS row_count FROM property_explorer_gold.dim_public_poi"
        )
    assert rows["row_count"].iloc[0] == 29
