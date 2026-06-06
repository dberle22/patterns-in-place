import json
from pathlib import Path

import pandas as pd

from nyc_property_finder.curated_poi.google_takeout.build_dim import DIM_USER_POI_V2_COLUMNS
from nyc_property_finder.curated_poi.shared.places import build_canonical_dim_from_stages
from nyc_property_finder.curated_poi.web_scraping.pipeline import run
from nyc_property_finder.services.duckdb_service import DuckDBService
from nyc_property_finder.services.schema import initialize_database


def _stage_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "poi_id": "poi_1",
        "source_system": "google_places",
        "source_systems": "[]",
        "primary_source_system": "",
        "source_record_id": "[]",
        "source_list_names": "[]",
        "category": "",
        "subcategory": "",
        "detail_level_3": "",
        "categories": "[]",
        "primary_category": "",
        "subcategories": "[]",
        "primary_subcategory": "",
        "detail_level_3_values": "[]",
        "primary_detail_level_3": "",
        "name": "",
        "input_title": "",
        "note": "[]",
        "tags": "[]",
        "comment": "[]",
        "source_url": "[]",
        "google_place_id": "",
        "match_status": "",
        "address": "",
        "lat": None,
        "lon": None,
        "has_place_details": False,
        "details_fetched_at": "",
        "rating": None,
        "user_rating_count": None,
        "business_status": None,
        "editorial_summary": None,
        "editorial_summary_language_code": None,
        "price_level": None,
        "website_uri": None,
    }
    row.update(overrides)
    return row


def test_web_scrape_pipeline_resolves_and_writes_stage_and_dim(tmp_path) -> None:
    csv_path = tmp_path / "bakeries.csv"
    csv_path.write_text(
        "\n".join(
            [
                "source_record_id,source_system,source_file,publisher,article_slug,article_title,article_url,source_list_name,capture_mode,parser_name,category,subcategory,detail_level_3,item_rank,item_name,item_url,raw_address,raw_description,raw_neighborhood,raw_borough,scraped_at,input_title,note,tags,comment,source_url,search_query",
                "src_a,web_scrape,bakeries.html,Eater,best-bakeries-nyc,Best Bakeries,https://ny.eater.com/maps/best-bakeries-nyc,Eater NYC - Best Bakeries,parser,eater,bakeries,bakeries,,1,Orwasher's Bakery,https://ny.eater.com/maps/best-bakeries-nyc#orwashers-bakery,\"308 E 78th St, New York, NY 10075, USA\",Historic bakery,,,2026-04-28T00:00:00+00:00,Orwasher's Bakery,\"308 E 78th St, New York, NY 10075, USA\",,Historic bakery,https://ny.eater.com/maps/best-bakeries-nyc#orwashers-bakery,\"Orwasher's Bakery 308 E 78th St, New York, NY 10075, USA New York, NY\"",
            ]
        ),
        encoding="utf-8",
    )
    database_path = tmp_path / "test.duckdb"
    initialize_database(database_path)

    def fake_search(query: str, api_key: str) -> dict[str, str]:
        assert "Orwasher" in query
        assert api_key == "test-key"
        return {"google_place_id": "places/orwashers", "match_status": "top_candidate"}

    def fake_details(place_id: str, api_key: str) -> dict[str, object]:
        assert place_id == "places/orwashers"
        assert api_key == "test-key"
        return {
            "displayName": {"text": "Orwashers Bakery"},
            "formattedAddress": "308 E 78th St, New York, NY 10075, USA",
            "location": {"latitude": 40.772297, "longitude": -73.954948},
        }

    report = run(
        csv_path=csv_path,
        database_path=database_path,
        resolution_cache_path=tmp_path / "resolution.csv",
        details_cache_path=tmp_path / "details.jsonl",
        api_key="test-key",
        resolution_fetcher=fake_search,
        details_fetcher=fake_details,
    )

    assert report.resolve.resolved == 1
    assert report.enrich.attempted_details_calls == 1
    assert report.dim_rows == 1
    assert report.dim_with_coordinates == 1

    resolution_cache = (tmp_path / "resolution.csv").read_text(encoding="utf-8")
    assert "places/orwashers" in resolution_cache

    details_rows = [json.loads(line) for line in (tmp_path / "details.jsonl").read_text(encoding="utf-8").splitlines()]
    assert details_rows[0]["google_place_id"] == "places/orwashers"


def test_build_canonical_dim_from_stages_preserves_source_lineage_for_overlaps() -> None:
    google_takeout_stage = pd.DataFrame(
        [
            _stage_row(
                source_systems='["google_maps_takeout"]',
                primary_source_system="google_maps_takeout",
                source_record_id='["src_takeout"]',
                source_list_names='["NYC Bakeries"]',
                category="bakeries",
                subcategory="bakeries",
                categories='["bakeries"]',
                primary_category="bakeries",
                subcategories='["bakeries"]',
                primary_subcategory="bakeries",
                name="Breads Bakery",
                input_title="Breads Bakery",
                note='["Union Square"]',
                source_url='["https://maps.google.com/breads"]',
                google_place_id="places/breads",
                match_status="top_candidate",
                address="18 E 16th St, New York, NY 10003, USA",
                lat=40.736601,
                lon=-73.991795,
                has_place_details=True,
                details_fetched_at="2026-04-28T00:00:00+00:00",
            )
        ]
    )[DIM_USER_POI_V2_COLUMNS]
    web_scrape_stage = pd.DataFrame(
        [
            _stage_row(
                source_systems='["web_scrape"]',
                primary_source_system="web_scrape",
                source_record_id='["src_scrape"]',
                source_list_names='["Eater NYC - Best Bakeries"]',
                category="bakeries",
                subcategory="bakeries",
                categories='["bakeries"]',
                primary_category="bakeries",
                subcategories='["bakeries"]',
                primary_subcategory="bakeries",
                name="Breads Bakery",
                input_title="Breads Bakery",
                note='["18 E 16th St, New York, NY 10003, USA"]',
                comment='["Known for babka"]',
                source_url='["https://ny.eater.com/maps/best-bakeries-nyc#breads-bakery"]',
                google_place_id="places/breads",
                match_status="top_candidate",
                address="18 E 16th St, New York, NY 10003, USA",
                lat=40.736601,
                lon=-73.991795,
                has_place_details=True,
                details_fetched_at="2026-04-29T00:00:00+00:00",
            )
        ]
    )[DIM_USER_POI_V2_COLUMNS]

    merged = build_canonical_dim_from_stages(
        [google_takeout_stage, web_scrape_stage],
        canonical_columns=DIM_USER_POI_V2_COLUMNS,
    )

    assert len(merged) == 1
    row = merged.iloc[0]
    assert row["primary_source_system"] == "google_maps_takeout"
    assert json.loads(row["source_systems"]) == ["google_maps_takeout", "web_scrape"]
    assert json.loads(row["source_record_id"]) == ["src_takeout", "src_scrape"]
    assert json.loads(row["source_list_names"]) == ["NYC Bakeries", "Eater NYC - Best Bakeries"]


def test_web_scrape_pipeline_accumulates_existing_web_scrape_stage_rows(tmp_path) -> None:
    csv_path = tmp_path / "music.csv"
    csv_path.write_text(
        "\n".join(
            [
                "source_record_id,source_system,source_file,publisher,article_slug,article_title,article_url,source_list_name,capture_mode,parser_name,category,subcategory,detail_level_3,item_rank,item_name,item_url,raw_address,raw_description,raw_neighborhood,raw_borough,scraped_at,input_title,note,tags,comment,source_url,search_query",
                "src_timeout,web_scrape,music.html,Time Out,best-live-music-venues-in-new-york-city,Top Music Venues,https://www.timeout.com/newyork/music/best-live-music-venues-in-new-york-city,Time Out NYC - Top Music Venues,parser,timeout,music_venues,music_venues,,1,Blue Note,https://www.timeout.com/newyork/music/blue-note,\"131 W 3rd St, New York, NY 10012, USA\",Jazz club,,,2026-04-29T00:00:00+00:00,Blue Note,\"131 W 3rd St, New York, NY 10012, USA\",,Jazz club,https://www.timeout.com/newyork/music/blue-note,\"Blue Note 131 W 3rd St, New York, NY 10012, USA New York, NY\"",
            ]
        ),
        encoding="utf-8",
    )
    database_path = tmp_path / "test.duckdb"
    initialize_database(database_path)

    existing_web_scrape_stage = pd.DataFrame(
        [
            _stage_row(
                poi_id="poi_breads",
                source_systems='["web_scrape"]',
                primary_source_system="web_scrape",
                source_record_id='["src_eater"]',
                source_list_names='["Eater NYC - Best Bakeries"]',
                category="bakeries",
                subcategory="bakeries",
                categories='["bakeries"]',
                primary_category="bakeries",
                subcategories='["bakeries"]',
                primary_subcategory="bakeries",
                name="Breads Bakery",
                input_title="Breads Bakery",
                note='["18 E 16th St, New York, NY 10003, USA"]',
                comment='["Known for babka"]',
                source_url='["https://ny.eater.com/maps/best-bakeries-nyc#breads-bakery"]',
                google_place_id="places/breads",
                match_status="top_candidate",
                address="18 E 16th St, New York, NY 10003, USA",
                lat=40.736601,
                lon=-73.991795,
                has_place_details=True,
                details_fetched_at="2026-04-28T00:00:00+00:00",
            )
        ]
    )[DIM_USER_POI_V2_COLUMNS]
    with DuckDBService(database_path) as duckdb_service:
        duckdb_service.write_dataframe(
            existing_web_scrape_stage,
            "stg_user_poi_web_scrape",
            schema="property_explorer_gold",
        )

    def fake_search(query: str, api_key: str) -> dict[str, str]:
        assert "Blue Note" in query
        return {"google_place_id": "places/blue-note", "match_status": "top_candidate"}

    def fake_details(place_id: str, api_key: str) -> dict[str, object]:
        assert place_id == "places/blue-note"
        return {
            "displayName": {"text": "Blue Note Jazz Club"},
            "formattedAddress": "131 W 3rd St, New York, NY 10012, USA",
            "location": {"latitude": 40.73084, "longitude": -74.0007},
        }

    report = run(
        csv_path=csv_path,
        database_path=database_path,
        resolution_cache_path=tmp_path / "resolution.csv",
        details_cache_path=tmp_path / "details.jsonl",
        api_key="test-key",
        resolution_fetcher=fake_search,
        details_fetcher=fake_details,
    )

    assert report.resolve.resolved == 1

    with DuckDBService(database_path) as duckdb_service:
        stage = duckdb_service.query_df(
            "select input_title, source_list_names from property_explorer_gold.stg_user_poi_web_scrape order by input_title"
        )
        dim = duckdb_service.query_df(
            "select input_title, source_list_names from property_explorer_gold.dim_user_poi_v2 where primary_source_system = 'web_scrape' order by input_title"
        )

    assert stage["input_title"].tolist() == ["Blue Note", "Breads Bakery"]
    assert dim["input_title"].tolist() == ["Blue Note", "Breads Bakery"]


def test_web_scrape_pipeline_primes_exact_canonical_matches_before_text_search(tmp_path) -> None:
    csv_path = tmp_path / "bakeries.csv"
    csv_path.write_text(
        "\n".join(
            [
                "source_record_id,source_system,source_file,publisher,article_slug,article_title,article_url,source_list_name,capture_mode,parser_name,category,subcategory,detail_level_3,item_rank,item_name,item_url,raw_address,raw_description,raw_neighborhood,raw_borough,scraped_at,input_title,note,tags,comment,source_url,search_query",
                "src_dupe,web_scrape,bakeries.html,Eater,best-bakeries-nyc,Best Bakeries,https://ny.eater.com/maps/best-bakeries-nyc,Eater NYC - Best Bakeries,parser,eater,bakeries,bakeries,,1,Breads Bakery,https://ny.eater.com/maps/best-bakeries-nyc#breads-bakery,\"18 E 16th St, New York, NY 10003, USA\",Historic bakery,,,2026-04-28T00:00:00+00:00,Breads Bakery,\"18 E 16th St, New York, NY 10003, USA\",,Historic bakery,https://ny.eater.com/maps/best-bakeries-nyc#breads-bakery,\"Breads Bakery 18 E 16th St, New York, NY 10003, USA New York, NY\"",
            ]
        ),
        encoding="utf-8",
    )
    database_path = tmp_path / "test.duckdb"
    initialize_database(database_path)

    existing_dim = pd.DataFrame(
        [
            _stage_row(
                poi_id="poi_breads",
                source_systems='["google_maps_takeout"]',
                primary_source_system="google_maps_takeout",
                source_record_id='["src_takeout"]',
                source_list_names='["poi_bakeries_nyc"]',
                category="bakeries",
                subcategory="bakeries",
                categories='["bakeries"]',
                primary_category="bakeries",
                subcategories='["bakeries"]',
                primary_subcategory="bakeries",
                name="Breads Bakery",
                input_title="Breads Bakery",
                note='["18 E 16th St, New York, NY 10003, USA"]',
                source_url='["https://maps.google.com/breads"]',
                google_place_id="places/breads",
                match_status="top_candidate",
                address="18 E 16th St, New York, NY 10003, USA",
                lat=40.736601,
                lon=-73.991795,
                has_place_details=True,
                details_fetched_at="2026-04-28T00:00:00+00:00",
            )
        ]
    )[DIM_USER_POI_V2_COLUMNS]
    with DuckDBService(database_path) as duckdb_service:
        duckdb_service.write_dataframe(existing_dim, "dim_user_poi_v2", schema="property_explorer_gold")

    details_cache_path = tmp_path / "details.jsonl"
    details_cache_path.write_text(
        json.dumps(
            {
                "google_place_id": "places/breads",
                "fetched_at": "2026-04-28T00:00:00+00:00",
                "field_mask": "displayName,formattedAddress,location,rating,userRatingCount,businessStatus,editorialSummary,priceLevel,websiteUri",
                "cache_schema_version": "2026-04-29-pro-v1",
                "payload": {
                    "displayName": {"text": "Breads Bakery"},
                    "formattedAddress": "18 E 16th St, New York, NY 10003, USA",
                    "location": {"latitude": 40.736601, "longitude": -73.991795},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    def should_not_search(query: str, api_key: str) -> dict[str, str]:
        raise AssertionError(f"Text Search should have been skipped for duplicate canonical row: {query}")

    report = run(
        csv_path=csv_path,
        database_path=database_path,
        resolution_cache_path=tmp_path / "resolution.csv",
        details_cache_path=details_cache_path,
        api_key="test-key",
        resolution_fetcher=should_not_search,
    )

    assert report.canonical_pre_resolve_matches == 1
    assert report.resolve.input_cache_hits == 1
    assert report.resolve.attempted_text_search_calls == 0
    assert report.enrich.attempted_details_calls == 0

    resolution_cache = (tmp_path / "resolution.csv").read_text(encoding="utf-8")
    assert "canonical_exact_match" in resolution_cache
    assert "places/breads" in resolution_cache


def test_web_scrape_pipeline_writes_qa_only_possible_canonical_duplicate_rows(tmp_path) -> None:
    csv_path = tmp_path / "bakeries.csv"
    csv_path.write_text(
        "\n".join(
            [
                "source_record_id,source_system,source_file,publisher,article_slug,article_title,article_url,source_list_name,capture_mode,parser_name,category,subcategory,detail_level_3,item_rank,item_name,item_url,raw_address,raw_description,raw_neighborhood,raw_borough,scraped_at,input_title,note,tags,comment,source_url,search_query",
                "src_possible,web_scrape,bakeries.html,Eater,best-bakeries-nyc,Best Bakeries,https://ny.eater.com/maps/best-bakeries-nyc,Eater NYC - Best Bakeries,parser,eater,bakeries,bakeries,,1,Breads Bakery Cafe,https://ny.eater.com/maps/best-bakeries-nyc#breads-bakery,\"18 E 16th Street, New York, NY 10003, USA\",Historic bakery,,,2026-04-28T00:00:00+00:00,Breads Bakery Cafe,\"18 E 16th Street, New York, NY 10003, USA\",,Historic bakery,https://ny.eater.com/maps/best-bakeries-nyc#breads-bakery,\"Breads Bakery Cafe 18 E 16th Street, New York, NY 10003, USA New York, NY\"",
            ]
        ),
        encoding="utf-8",
    )
    database_path = tmp_path / "test.duckdb"
    initialize_database(database_path)

    existing_dim = pd.DataFrame(
        [
            _stage_row(
                poi_id="poi_breads",
                source_systems='["google_maps_takeout"]',
                primary_source_system="google_maps_takeout",
                source_record_id='["src_takeout"]',
                source_list_names='["poi_bakeries_nyc"]',
                category="bakeries",
                subcategory="bakeries",
                categories='["bakeries"]',
                primary_category="bakeries",
                subcategories='["bakeries"]',
                primary_subcategory="bakeries",
                name="Breads Bakery",
                input_title="Breads Bakery",
                note='["18 E 16th St, New York, NY 10003, USA"]',
                source_url='["https://maps.google.com/breads"]',
                google_place_id="places/breads",
                match_status="top_candidate",
                address="18 E 16th St, New York, NY 10003, USA",
                lat=40.736601,
                lon=-73.991795,
                has_place_details=True,
                details_fetched_at="2026-04-28T00:00:00+00:00",
            )
        ]
    )[DIM_USER_POI_V2_COLUMNS]
    with DuckDBService(database_path) as duckdb_service:
        duckdb_service.write_dataframe(existing_dim, "dim_user_poi_v2", schema="property_explorer_gold")

    def fake_search(query: str, api_key: str) -> dict[str, str]:
        return {"google_place_id": "places/breads-cafe", "match_status": "top_candidate"}

    def fake_details(place_id: str, api_key: str) -> dict[str, object]:
        return {
            "displayName": {"text": "Breads Bakery Cafe"},
            "formattedAddress": "18 E 16th Street, New York, NY 10003, USA",
            "location": {"latitude": 40.736601, "longitude": -73.991795},
        }

    report = run(
        csv_path=csv_path,
        database_path=database_path,
        resolution_cache_path=tmp_path / "resolution.csv",
        details_cache_path=tmp_path / "details.jsonl",
        api_key="test-key",
        resolution_fetcher=fake_search,
        details_fetcher=fake_details,
        qa_path=tmp_path / "web_scrape_qa.csv",
        summary_path=tmp_path / "web_scrape_summary.json",
    )

    assert report.canonical_pre_resolve_matches == 0
    assert report.resolve.attempted_text_search_calls == 1
    assert report.summary["possible_canonical_duplicate_rows"] == 1
    assert "possible_canonical_duplicate" in (tmp_path / "web_scrape_qa.csv").read_text(encoding="utf-8")
    assert "Review possible_canonical_duplicate rows" in json.loads(
        (tmp_path / "web_scrape_summary.json").read_text(encoding="utf-8")
    )["review_recommendations"][0]
