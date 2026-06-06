"""
Export pipeline: metro_deep_dive.duckdb → rof_app.duckdb (rof_gold schema).

Reads a market-scoped slice from the upstream analytical DuckDB and writes
app-ready tables into the local rof_app.duckdb. Safe to re-run — each table
is truncated and reloaded. User-authored tables (user_shortlist) are never
touched here.

Usage:
    python -m retail_opportunity_finder.pipelines.export_from_metro
    python -m retail_opportunity_finder.pipelines.export_from_metro --market jacksonville_fl
"""

import argparse
import sys
import time
from pathlib import Path

import duckdb

# Bring in our config helpers.
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from retail_opportunity_finder.utils.config import get_db_path, load_data_sources, load_settings

# ── Jacksonville county GEOIDs — used to filter parcels ────────────────────
JAX_COUNTY_GEOIDS = ("12003", "12019", "12031", "12089", "12109")


def _attach_metro(app_con: duckdb.DuckDBPyConnection, metro_path: str) -> None:
    """Attaches metro_deep_dive.duckdb as a read-only alias 'metro'."""
    app_con.execute(f"ATTACH '{metro_path}' AS metro (READ_ONLY)")


def _bootstrap_schema(app_con: duckdb.DuckDBPyConnection, ddl_path: Path) -> None:
    """Runs the DDL file to create rof_gold schema and tables if missing."""
    ddl = ddl_path.read_text()
    app_con.execute(ddl)
    print("  ✓ rof_gold schema bootstrapped")


def _copy_table(
    app_con: duckdb.DuckDBPyConnection,
    dest_table: str,
    select_sql: str,
) -> int:
    """Truncates dest_table and inserts rows returned by select_sql."""
    app_con.execute(f"DELETE FROM {dest_table}")
    app_con.execute(f"INSERT INTO {dest_table} {select_sql}")
    count = app_con.execute(f"SELECT COUNT(*) FROM {dest_table}").fetchone()[0]
    return count


def run_export(market_key: str = "jacksonville_fl") -> None:
    sources = load_data_sources()
    if sources is None:
        raise RuntimeError("data_sources.yaml not found — cannot run export pipeline locally.")

    metro_path = sources["metro_duckdb_path"]
    app_db_path = get_db_path()
    app_db_path.parent.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).parent.parent.parent.parent
    ddl_path = repo_root / "sql" / "ddl" / "001_rof_gold_tables.sql"

    print(f"\nExporting market: {market_key}")
    print(f"  Source: {metro_path}")
    print(f"  Dest:   {app_db_path}\n")

    # Load settings to get cbsa_code and county list for this market.
    settings = load_settings()
    market_cfg = settings["markets"][market_key]
    cbsa_code = market_cfg["cbsa_code"]
    county_geoids = tuple(market_cfg["county_geoids"])
    county_placeholders = ", ".join(f"'{g}'" for g in county_geoids)

    app_con = duckdb.connect(str(app_db_path))
    _attach_metro(app_con, metro_path)
    _bootstrap_schema(app_con, ddl_path)

    steps: list[tuple[str, str]] = [
        # ── Market reference ────────────────────────────────────────────────
        (
            "rof_gold.market_profiles",
            f"""
            SELECT
                market_key, cbsa_code, state_scope,
                cbsa_name, cbsa_name_full, market_name,
                target_flag, build_source, run_timestamp
            FROM metro.ref.market_profiles
            WHERE market_key = '{market_key}'
            """,
        ),
        # ── Geography / geometry ────────────────────────────────────────────
        (
            "rof_gold.cbsa_geometry",
            f"""
            SELECT cbsa_code, geom_wkt
            FROM metro.foundation.market_cbsa_geometry
            WHERE cbsa_code = '{cbsa_code}'
            """,
        ),
        (
            "rof_gold.county_geometry",
            f"""
            SELECT cbsa_code, county_geoid, geom_wkt
            FROM metro.foundation.market_county_geometry
            WHERE cbsa_code = '{cbsa_code}'
              AND county_geoid IN ({county_placeholders})
            """,
        ),
        (
            "rof_gold.tract_geometry",
            f"""
            SELECT cbsa_code, tract_geoid, geom_wkt
            FROM metro.foundation.market_tract_geometry
            WHERE cbsa_code = '{cbsa_code}'
            """,
        ),
        # ── Tract features and scores ───────────────────────────────────────
        (
            "rof_gold.tract_features",
            f"""
            SELECT
                cbsa_code, county_geoid, tract_geoid, year,
                pop_total, pop_growth_3yr, pop_growth_pctl, pop_growth_5yr,
                median_hh_income, per_capita_income, pov_rate, income_pctl,
                median_gross_rent, median_home_value, rent_pctl, value_pctl,
                price_proxy_pctl, pct_commute_wfh, mean_travel_time,
                commute_intensity_b, total_units_3yr_avg, units_per_1k_3yr,
                pop_density, land_area_sqmi, density_pctl,
                gate_pop, gate_price, gate_density, eligible_v1
            FROM metro.rof_features.tract_features
            WHERE cbsa_code = '{cbsa_code}'
            """,
        ),
        (
            "rof_gold.tract_scores",
            f"""
            SELECT
                market_key, cbsa_code, county_geoid, tract_geoid, year,
                eligible_v1, gate_pop, gate_price, gate_density,
                tract_score, tract_rank, is_scored, why_tags,
                z_growth, z_units, z_headroom, z_price, z_commute, z_income
            FROM metro.scoring.tract_scores
            WHERE market_key = '{market_key}'
            """,
        ),
        # ── Zone tables (cluster) ───────────────────────────────────────────
        (
            "rof_gold.cluster_assignments",
            f"""
            SELECT
                market_key, cbsa_code, tract_geoid,
                cluster_id, cluster_label, cluster_order,
                tract_score, zone_method
            FROM metro.zones.cluster_assignments
            WHERE market_key = '{market_key}'
            """,
        ),
        (
            "rof_gold.cluster_zone_summary",
            f"""
            SELECT
                market_key, cbsa_code, cluster_id, cluster_label, cluster_order,
                tracts, total_population, pop_growth_3yr_wtd, pop_density_median,
                units_per_1k_3yr_wtd, price_proxy_pctl_median, mean_tract_score,
                zone_area_sq_mi, zone_method
            FROM metro.zones.cluster_zone_summary
            WHERE market_key = '{market_key}'
            """,
        ),
        (
            "rof_gold.cluster_zone_geometries",
            f"""
            SELECT
                market_key, cbsa_code, cluster_id, cluster_label, cluster_order,
                zone_area_sq_mi, label_lon, label_lat, geom_wkt, zone_method
            FROM metro.zones.cluster_zone_geometries
            WHERE market_key = '{market_key}'
            """,
        ),
        # ── Zone tables (contiguity) ────────────────────────────────────────
        (
            "rof_gold.contiguity_zone_summary",
            f"""
            SELECT
                market_key, cbsa_code, zone_id, zone_label, zone_order,
                tracts, total_population, pop_growth_3yr_wtd, pop_density_median,
                units_per_1k_3yr_wtd, price_proxy_pctl_median, mean_tract_score,
                zone_area_sq_mi, zone_method
            FROM metro.zones.contiguity_zone_summary
            WHERE market_key = '{market_key}'
            """,
        ),
        (
            "rof_gold.contiguity_zone_geometries",
            f"""
            SELECT
                market_key, cbsa_code, zone_id, zone_label, zone_order,
                zone_area_sq_mi, label_lon, label_lat, geom_wkt, zone_method
            FROM metro.zones.contiguity_zone_geometries
            WHERE market_key = '{market_key}'
            """,
        ),
        # ── Serving tables (pre-joined, app-ready) ──────────────────────────
        (
            "rof_gold.parcel_shortlist",
            f"""
            SELECT
                market_key, cbsa_code,
                -- zone_system distinguishes cluster vs contiguity rows
                zone_system, zone_id, zone_label,
                shortlist_rank_system, shortlist_rank_zone,
                parcel_uid, parcel_id, tract_geoid,
                county_geoid, county_name, state_abbr,
                land_use_code, retail_subtype,
                owner_name, site_addr,
                parcel_area_sqmi,   -- NULL until parcel geometry is ingested
                just_value, last_sale_date, last_sale_price,
                local_retail_context_score, mean_tract_score,
                zone_quality_score, parcel_characteristics_score, shortlist_score
            FROM metro.serving.parcel_shortlist
            WHERE market_key = '{market_key}'
            """,
        ),
        (
            "rof_gold.parcel_zone_overlay",
            f"""
            SELECT
                market_key, cbsa_code, zone_system, zone_id, zone_label, zone_order,
                tracts, total_population, zone_area_sq_mi,
                retail_parcel_count, retail_area, retail_area_density,
                local_retail_context_score, mean_tract_score, zone_quality_score
            FROM metro.serving.parcel_zone_overlay
            WHERE market_key = '{market_key}'
            """,
        ),
        (
            "rof_gold.retail_intensity_by_tract",
            f"""
            SELECT
                market_key, cbsa_code, county_geoid, tract_geoid,
                retail_parcel_count, retail_area, retail_area_density,
                pctl_tract_retail_parcel_count, pctl_tract_retail_area_density,
                local_retail_context_score
            FROM metro.serving.retail_intensity_by_tract
            WHERE market_key = '{market_key}'
              AND tract_geoid IS NOT NULL
            """,
        ),
        (
            "rof_gold.retail_parcel_tract_assignment",
            f"""
            SELECT
                market_key, cbsa_code, county_geoid, county_name,
                parcel_uid, join_key, land_use_code, retail_subtype,
                tract_geoid, assignment_method, assignment_status
            FROM metro.serving.retail_parcel_tract_assignment
            WHERE market_key = '{market_key}'
            """,
        ),
        # ── Retail parcels (tabular attributes, no geometry) ────────────────
        (
            "rof_gold.retail_parcels",
            f"""
            SELECT
                market_key, cbsa_code, county_geoid, county_name,
                parcel_uid, join_key,
                land_use_code, land_use_category, land_use_description,
                retail_flag, retail_subtype,
                owner_name, site_addr,
                living_area_sqft, just_value, land_value, impro_value, total_value,
                last_sale_price, last_sale_date
            FROM metro.parcel.parcels_canonical
            WHERE county_geoid IN ({county_placeholders})
              AND retail_flag = TRUE
            """,
        ),
    ]

    total_rows = 0
    t0 = time.time()

    for dest_table, select_sql in steps:
        t_step = time.time()
        count = _copy_table(app_con, dest_table, select_sql)
        elapsed = time.time() - t_step
        total_rows += count
        print(f"  {dest_table:<45}  {count:>7,} rows  ({elapsed:.1f}s)")

    app_con.close()

    elapsed_total = time.time() - t0
    print(f"\n✓ Export complete — {total_rows:,} total rows in {elapsed_total:.1f}s")
    print(f"  DB written to: {app_db_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export a market slice into rof_app.duckdb")
    parser.add_argument(
        "--market",
        default="jacksonville_fl",
        help="market_key to export (must exist in config/settings.yaml)",
    )
    args = parser.parse_args()
    run_export(market_key=args.market)
