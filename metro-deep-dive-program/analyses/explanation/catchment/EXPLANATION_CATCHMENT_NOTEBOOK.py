# %% [markdown]
# # Catchment property exploration
#
# Change only the inputs in the next cell to explore another property. This
# notebook writes nothing: all outputs remain in this session as inspectable
# data frames and maps. Euclidean reaches describe distance from the point, not
# travel time or barrier-adjusted access.

# %% Inputs
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd


NOTEBOOK_DIR = Path.cwd() if Path("catchment.py").exists() else Path(__file__).resolve().parent
MODULE_PATH = NOTEBOOK_DIR / "catchment.py"
MODULE_SPEC = importlib.util.spec_from_file_location("explanation_catchment", MODULE_PATH)
if MODULE_SPEC is None or MODULE_SPEC.loader is None:
    raise ImportError(f"Could not load Catchment helpers from {MODULE_PATH}.")
catchment = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = catchment
MODULE_SPEC.loader.exec_module(catchment)


# Jacksonville Baymeadows is the reusable V1 fixture. Supply both coordinates
# to override address geocoding; set both to None to use the Census geocoder.
PROPERTY = catchment.PropertyInput(
    property_id="jacksonville_fl_baymeadows_v0",
    label="Jacksonville Baymeadows",
    address="3832 Baymeadows Road, Jacksonville, FL 32217",
    market_id="27260",
    lat=30.217618577902,
    lon=-81.616679103522,
    reach_distances_mi=(1, 3, 5),
)


def show(value):
    """Use notebook display when available, with a useful script fallback."""

    try:
        from IPython.display import display

        display(value)
    except ImportError:
        print(value)


# %% Resolve the point and construct canonical contribution tables
with catchment.open_connection() as con:
    resolved_point = catchment.resolve_property_point(con, PROPERTY)
    catchment.validate_point_market(con, resolved_point)
    market_tracts = catchment.load_market_tracts(con, PROPERTY.market_id)

bands = catchment.build_band_geometries(resolved_point, PROPERTY.reach_distances_mi)
band_contributions = catchment.build_band_contributions(bands, market_tracts)
cumulative_reach_geometries = catchment.derive_cumulative_reach_geometries(bands)
cumulative_reach_contributions = catchment.derive_cumulative_reach_contributions(band_contributions)

point_provenance = pd.DataFrame([resolved_point.__dict__])
geometry_provenance = pd.DataFrame([{
    "geometry_role": catchment.GEOMETRY_ROLE,
    "geometry_vintage": catchment.GEOMETRY_VINTAGE,
    "tract_identity_vintage": sorted(market_tracts.tract_boundary_vintage.dropna().unique().tolist()),
    "cbsa_identity_vintage": sorted(market_tracts.cbsa_boundary_vintage.dropna().unique().tolist()),
    "market_membership_tract_count": market_tracts.attrs["market_membership_tract_count"],
    "market_geometry_tract_count": market_tracts.attrs["market_geometry_tract_count"],
    "missing_market_geometry_tract_count": market_tracts.attrs["missing_market_geometry_tract_count"],
    "weight_method": "areal",
    "method_warning": "Legacy tract geometry has an unknown vintage; reaches are straight-line Euclidean bands.",
}])

show(point_provenance)
show(geometry_provenance)
show(bands.drop(columns="geometry"))

# %% Map the property, non-overlapping bands, cumulative reaches, and tracts
# The map is deliberately a transparent geometry check rather than a styled
# product graphic. Geometry is projected here, so it is converted only for
# display alongside the WGS84 point and tracts.
fig, axis = plt.subplots(figsize=(10, 10))
market_tracts.boundary.to_crs(catchment.WGS84_CRS).plot(ax=axis, color="0.7", linewidth=0.35)
cumulative_reach_geometries.to_crs(catchment.WGS84_CRS).boundary.plot(ax=axis, color="#205493", linewidth=1.2)
bands.to_crs(catchment.WGS84_CRS).plot(ax=axis, alpha=0.14, edgecolor="#0071bc", cmap="Blues")
axis.scatter(resolved_point.lon, resolved_point.lat, color="#d54309", s=36, zorder=3)
axis.set_title(f"{resolved_point.label}: Euclidean bands and cumulative reaches")
axis.set_axis_off()
plt.show()

# %% Inspect canonical allocation tables and measured geometry QA
band_qa = catchment.contribution_qa(band_contributions, bands)
show(band_contributions)
show(cumulative_reach_contributions)
show(band_qa)

# %% Build the corrected demographic and household profile
with catchment.open_connection() as con:
    metric_inputs = catchment.load_standard_metric_inputs(con, PROPERTY.market_id)
    standard_profile = catchment.aggregate_profile(cumulative_reach_contributions, metric_inputs)
    compatible_benchmarks = catchment.load_compatible_benchmarks(
        con, resolved_point, int(metric_inputs.year.iloc[0])
    )

metric_qa = catchment.metric_join_qa(cumulative_reach_contributions, metric_inputs)
tract_median_evidence = catchment.contributing_tract_medians(cumulative_reach_contributions, metric_inputs)

# Every profile row states the calculation inputs. Counts are apportioned;
# shares/rates reconstruct source numerator / source denominator. No medians
# are aggregated as catchment estimates.
show(standard_profile)
show(compatible_benchmarks)
show(metric_qa)
show(tract_median_evidence)

# %% Add cumulative LODES workplace and resident-worker context
def load_lodes_context(con, contributions: pd.DataFrame) -> pd.DataFrame:
    """Apportion 2023 tract LODES counts to each cumulative reach."""

    latest_year = con.execute(
        """SELECT LEAST(MAX(w.year), MAX(r.year))
           FROM patterns_in_place.silver.lehd_lodes_wac w
           JOIN patterns_in_place.silver.lehd_lodes_rac r
             ON r.geo_id = w.geo_id AND r.geo_level = w.geo_level AND r.year = w.year
           JOIN patterns_in_place.mart_geography.rollup_tract_to_cbsa m ON m.tract_geoid = w.geo_id
           WHERE w.geo_level = 'tract' AND m.cbsa_code = ?""",
        [PROPERTY.market_id],
    ).fetchone()[0]
    source = con.execute(
        """SELECT w.geo_id AS tract_geoid, w.jobs_total, w.jobs_ind_retail,
                  w.jobs_ind_health_care_social_assistance, w.jobs_ind_accommodation_food,
                  r.workers_total
           FROM patterns_in_place.silver.lehd_lodes_wac w
           JOIN patterns_in_place.silver.lehd_lodes_rac r
             ON r.geo_id = w.geo_id AND r.geo_level = w.geo_level AND r.year = w.year
           JOIN patterns_in_place.mart_geography.rollup_tract_to_cbsa m ON m.tract_geoid = w.geo_id
           WHERE w.geo_level = 'tract' AND w.year = ? AND m.cbsa_code = ?""",
        [latest_year, PROPERTY.market_id],
    ).fetchdf()
    joined = contributions.merge(source, on="tract_geoid", how="left", validate="many_to_one")
    count_columns = [column for column in source.columns if column != "tract_geoid"]
    rows = []
    for reach, values in joined.groupby("reach_outer_mi", sort=True):
        totals = {column: (values[column] * values.tract_share).sum() for column in count_columns}
        rows.append({"property_id": PROPERTY.property_id, "market_id": PROPERTY.market_id,
                     "reach_outer_mi": reach, "year": int(latest_year), **totals,
                     "jobs_to_resident_workers_ratio": totals["jobs_total"] / totals["workers_total"]
                     if totals["workers_total"] else None})
    return pd.DataFrame(rows)


with catchment.open_connection() as con:
    lodes_context = load_lodes_context(con, cumulative_reach_contributions)
show(lodes_context)

# %% Count governed POIs within each cumulative reach
AMENITY_BASKET = ("Food & Drink", "Healthcare", "Parks & Nature", "Retail", "Education")


def load_poi_counts(con, reaches, categories: tuple[str, ...]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return direct point-in-reach counts or an explicit unavailable result."""

    available = con.execute(
        """SELECT COUNT(*) FROM patterns_in_place.mart_poi.poi_classified_place
           WHERE cbsa_code = ? AND record_status = 'retained' AND is_within_market_boundary""",
        [PROPERTY.market_id],
    ).fetchone()[0]
    if not available:
        status = pd.DataFrame([{"availability": "unavailable", "reason": "No governed retained POI materialization for this market."}])
        return status, pd.DataFrame()

    placeholders = ", ".join("?" for _ in categories)
    rows = []
    provenance = []
    for reach in reaches.itertuples(index=False):
        geometry_wkb = bytes(reach.geometry.wkb)
        query = f"""SELECT category, sub_category, COUNT(*) AS poi_count,
                            MIN(source_release) AS source_release, MIN(mapping_version) AS mapping_version
                     FROM patterns_in_place.mart_poi.poi_classified_place
                     WHERE cbsa_code = ? AND record_status = 'retained' AND is_within_market_boundary
                       AND category IN ({placeholders})
                       AND ST_Contains(ST_GeomFromWKB(?), geometry)
                     GROUP BY category, sub_category ORDER BY category, sub_category"""
        result = con.execute(query, [PROPERTY.market_id, *categories, geometry_wkb]).fetchdf()
        if not result.empty:
            result.insert(0, "reach_outer_mi", reach.reach_outer_mi)
            rows.append(result)
        provenance.append({"reach_outer_mi": reach.reach_outer_mi, "availability": "available",
                           "governed_market_place_count": int(available), "method": "direct_point_in_cumulative_reach",
                           "source_relation": "mart_poi.poi_classified_place"})
    return pd.DataFrame(provenance), pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


with catchment.open_connection() as con:
    poi_availability, poi_counts = load_poi_counts(con, cumulative_reach_geometries, AMENITY_BASKET)
show(poi_availability)
show(poi_counts)

# %% Final session inventory and interpretation limits
outputs = {
    "resolved_point": point_provenance,
    "geometry_provenance": geometry_provenance,
    "bands": bands,
    "band_contributions": band_contributions,
    "cumulative_reach_geometries": cumulative_reach_geometries,
    "cumulative_reach_contributions": cumulative_reach_contributions,
    "band_qa": band_qa,
    "standard_profile": standard_profile,
    "compatible_benchmarks": compatible_benchmarks,
    "metric_qa": metric_qa,
    "tract_median_evidence": tract_median_evidence,
    "lodes_context": lodes_context,
    "poi_availability": poi_availability,
    "poi_counts": poi_counts,
}

limitations = pd.DataFrame({"limitation": [
    "Bands are straight-line Euclidean distances, not travel-time or routed catchments.",
    "Areal weighting allocates tract measures by land-area intersection; it is not dasymetric.",
    "V1 tract geometry is legacy_unclassified with an unknown geometry vintage.",
    "Median-like tract measures are evidence only and are not aggregated into catchment medians.",
]})
show(limitations)
