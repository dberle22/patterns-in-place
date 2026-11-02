"""Core-detail map layers for E1c from OpenStreetMap: the airport, hospitals, campuses and parks in the core box.

Fetch (Overpass, 2026-10-27), saved as data/osm_core_detail.json:
    [out:json][timeout:120];
    ( nwr["aeroway"="aerodrome"](42.60,-74.00,42.86,-73.64);
      nwr["amenity"="hospital"](42.60,-74.00,42.86,-73.64);
      nwr["amenity"~"^(university|college)$"](42.60,-74.00,42.86,-73.64);
      nwr["leisure"~"^(park|nature_reserve)$"](42.60,-74.00,42.86,-73.64);
      nwr["boundary"="protected_area"](42.60,-74.00,42.86,-73.64); );
    out geom;

Run: python data/build_osm_core_detail.py  ->  data/osm_core_detail.geojson (polygons only, EPSG:4326).
"""
import json
from pathlib import Path

import geopandas as gpd
import shapely
from shapely.ops import polygonize, unary_union

HERE = Path(__file__).resolve().parent
# The features drawn, by OSM name. Campuses of the College of Saint Rose are left out: it closed in 2024.
KEEP = {
    "airport": ["Albany International Airport"],
    "hospital": ["Albany Medical Center", "Saint Peter's Hospital", "Samaritan Hospital", "Ellis Hospital", "Saint Mary's Hospital",
                 "Samuel S. Stratton Veterans Affairs Medical Center", "Samaritan Hospital Albany Memorial Campus", "Bellevue Woman's Center",
                 "Sunnyview Rehibilitation Hospital", "Capital District Psychiatric Center"],
    "campus": ["University at Albany, The State University of New York", "University at Albany Downtown Campus",
               "University at Albany Health Sciences Campus", "Colleges of Nanoscale Science and Engineering at the University at Albany",
               "Rensselaer Polytechnic Institute", "Union College", "Siena University", "Hudson Valley Community College",
               "Albany Medical College", "Albany Law School", "Albany College of Pharmacy and Health Sciences",
               "Russell Sage College Albany Campus", "Russell Sage College Troy Campus", "SUNY Schenectady County Community College",
               "Maria College"],
}
PARK_MIN_ACRES = 10


def geometry(element):
    if element["type"] == "way" and "geometry" in element:
        coords = [(p["lon"], p["lat"]) for p in element["geometry"]]
        return shapely.Polygon(coords) if len(coords) >= 4 and coords[0] == coords[-1] else None
    if element["type"] == "relation":
        outers = [shapely.LineString([(p["lon"], p["lat"]) for p in m["geometry"]])
                  for m in element.get("members", []) if m.get("role") in ("outer", "") and m.get("geometry")]
        polygons = list(polygonize(unary_union(outers))) if outers else []
        return unary_union(polygons) if polygons else None
    return None


rows = []
for element in json.loads((HERE / "osm_core_detail.json").read_text())["elements"]:
    tags = element.get("tags", {})
    name = tags.get("name")
    layer = next((k for k, names in KEEP.items() if name in names), None)
    if layer is None and (tags.get("leisure") in ("park", "nature_reserve") or tags.get("boundary") == "protected_area"):
        layer = "park"
    geom = geometry(element) if layer else None
    if geom is None or geom.is_empty:
        continue
    rows.append({"osm_id": f"{element['type']}/{element['id']}", "name": name, "layer": layer, "geometry": shapely.make_valid(geom)})

out = gpd.GeoDataFrame(rows, crs="EPSG:4326")
acres = out.to_crs("EPSG:32618").area / 4046.86
out = out.loc[(out["layer"] != "park") | (acres >= PARK_MIN_ACRES)]
out.to_file(HERE / "osm_core_detail.geojson", driver="GeoJSON")
print(out["layer"].value_counts().to_dict())
missing = {n for names in KEEP.values() for n in names} - set(out["name"])
print("missing:", missing)
