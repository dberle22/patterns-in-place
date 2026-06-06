"""CLI entry point for curated POI ingestion from Google Takeout exports."""

from __future__ import annotations

from nyc_property_finder.pipelines.ingest_google_places_poi import main


if __name__ == "__main__":
    main()
