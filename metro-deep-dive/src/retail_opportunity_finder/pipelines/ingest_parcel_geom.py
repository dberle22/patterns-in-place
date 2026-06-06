"""
Parcel geometry ingest pipeline.

Two-step workflow:
  Step 1 (--keys-only): Write retail join_keys to CSV so the R script can
                         filter each county .rds before the expensive reproject.
  Step 2 (default):     Read GeoParquet files written by the R script,
                         extract WKT + centroid + area, write to rof_gold.parcel_geometry,
                         and backfill parcel_area_sqmi in rof_gold.parcel_shortlist.

Full workflow:
    # Step 1 — write key list
    .venv/bin/python -m retail_opportunity_finder.pipelines.ingest_parcel_geom --keys-only

    # Step 2 — run R export
    Rscript scripts/export_parcel_geometry.R

    # Step 3 — ingest GeoParquets into DuckDB
    .venv/bin/python -m retail_opportunity_finder.pipelines.ingest_parcel_geom
"""

import argparse
import sys
import time
from pathlib import Path

import duckdb
import pandas as pd
from shapely import wkt as shapely_wkt

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from retail_opportunity_finder.utils.config import get_db_path
from retail_opportunity_finder.utils.geo import wkt_to_area_sqmi

# Jacksonville county GeoParquet file stems — must match R script output names.
COUNTY_STEMS = [
    "baker_fl",
    "clay_fl",
    "duval_fl",
    "nassau_fl",
    "stjohns_fl",
]


def write_key_csv(db_path: Path, out_dir: Path) -> None:
    """
    Reads retail join_keys from rof_gold.retail_parcels and writes them
    to a CSV file. The R script reads this CSV to pre-filter each county
    .rds before the expensive CRS reprojection step.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "retail_join_keys.csv"

    con = duckdb.connect(str(db_path))
    keys = con.execute("SELECT DISTINCT join_key FROM rof_gold.retail_parcels WHERE join_key IS NOT NULL").df()
    con.close()

    keys.to_csv(csv_path, index=False)
    print(f"✓ Wrote {len(keys):,} retail join_keys → {csv_path}")
    print("  Next: Rscript scripts/export_parcel_geometry.R")


def ingest_geoparquets(db_path: Path, geom_dir: Path) -> None:
    """
    Reads one GeoParquet per county, converts polygons to WKT, computes
    centroid and area, then writes to rof_gold.parcel_geometry in DuckDB.
    Also backfills parcel_area_sqmi in rof_gold.parcel_shortlist.
    """
    con = duckdb.connect(str(db_path))

    # Clear the geometry table before reload so re-runs are safe.
    con.execute("DELETE FROM rof_gold.parcel_geometry")

    total_rows = 0
    t0 = time.time()

    for stem in COUNTY_STEMS:
        parquet_path = geom_dir / f"{stem}_geom.parquet"
        if not parquet_path.exists():
            print(f"  SKIP {stem} — GeoParquet not found (run R export first)")
            continue

        print(f"\n  Reading {stem}_geom.parquet ...")
        # The R script writes plain Parquet with geometry stored as WKT text.
        df = pd.read_parquet(parquet_path)

        if df.empty:
            print(f"  SKIP {stem} — empty parquet")
            continue

        rows = []
        for _, row in df.iterrows():
            geom_wkt = row.get("geom_wkt")
            if not geom_wkt:
                continue

            try:
                geom = shapely_wkt.loads(geom_wkt)
            except Exception:
                continue

            if geom is None or geom.is_empty:
                continue

            # Centroid for fallback ScatterplotLayer and label placement.
            centroid = geom.centroid
            centroid_lat = centroid.y
            centroid_lon = centroid.x

            # Area in sq mi — reprojects internally to Conus Albers for accuracy.
            area_sqmi = wkt_to_area_sqmi(geom_wkt)

            rows.append({
                "join_key": row["join_key"],
                "geom_wkt": geom_wkt,
                "centroid_lat": centroid_lat,
                "centroid_lon": centroid_lon,
                "area_sqmi": area_sqmi,
            })

        if not rows:
            print(f"  {stem}: no valid geometries")
            continue

        df = pd.DataFrame(rows)

        # Deduplicate on join_key — a join_key should map to exactly one geometry.
        # Also skip join_keys already ingested from a previous county file.
        existing = con.execute("SELECT join_key FROM rof_gold.parcel_geometry").df()["join_key"]
        df = df[~df["join_key"].isin(existing)].drop_duplicates(subset=["join_key"])

        if df.empty:
            print(f"  {stem}: all join_keys already ingested or duplicated — skipping")
            continue

        con.execute("INSERT INTO rof_gold.parcel_geometry SELECT * FROM df")
        total_rows += len(df)
        print(f"  {stem}: {len(df):,} parcels ingested")

    # Backfill parcel_area_sqmi in the serving shortlist table using the
    # geometry we just ingested, so filters/sorting on area work in the app.
    con.execute("""
        UPDATE rof_gold.parcel_shortlist sl
        SET parcel_area_sqmi = pg.area_sqmi
        FROM rof_gold.parcel_geometry pg
        WHERE sl.parcel_uid LIKE '%::' || pg.join_key
           OR sl.parcel_uid = pg.join_key
    """)

    # Check how many shortlist rows got an area filled in.
    filled = con.execute(
        "SELECT COUNT(*) FROM rof_gold.parcel_shortlist WHERE parcel_area_sqmi IS NOT NULL"
    ).fetchone()[0]
    total_shortlist = con.execute("SELECT COUNT(*) FROM rof_gold.parcel_shortlist").fetchone()[0]

    con.close()

    elapsed = time.time() - t0
    print(f"\n✓ Ingest complete — {total_rows:,} geometries in {elapsed:.1f}s")
    print(f"  parcel_area_sqmi filled: {filled:,} / {total_shortlist:,} shortlist rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest parcel geometry into rof_app.duckdb")
    parser.add_argument(
        "--keys-only",
        action="store_true",
        help="Only write the retail_join_keys.csv for the R export step; skip GeoParquet ingest.",
    )
    args = parser.parse_args()

    db_path = get_db_path()
    geom_dir = Path(__file__).parent.parent.parent.parent / "data" / "processed" / "parcel_geom"

    if args.keys_only:
        write_key_csv(db_path, geom_dir)
    else:
        ingest_geoparquets(db_path, geom_dir)
