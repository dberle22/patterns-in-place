import json
from pathlib import Path
import pytest

from nyc_property_finder.curated_poi.google_takeout.build_dim import build_dim_user_poi_v2
from nyc_property_finder.curated_poi.google_takeout.cache import read_details_cache, read_resolution_cache
from nyc_property_finder.curated_poi.google_takeout.client import (
    PLACE_DETAILS_CACHE_SCHEMA_VERSION,
    PLACE_DETAILS_FIELD_MASK,
    TEXT_SEARCH_ID_FIELD_MASK,
    build_place_details_request,
    build_text_search_id_request,
)
from nyc_property_finder.curated_poi.google_takeout.config import (
    get_google_maps_api_key,
    read_api_keys_file,
    read_env_file,
)
from nyc_property_finder.curated_poi.google_takeout.dry_run import (
    plan_directory_dry_run,
    plan_dry_run,
    read_details_cache_place_ids,
)
from nyc_property_finder.curated_poi.google_takeout.enrich import enrich_place_details
from nyc_property_finder.curated_poi.google_takeout.parse_takeout import (
    build_search_query,
    clean_list_category,
    normalize_curated_taxonomy,
    parse_google_places_saved_list_csv,
)
from nyc_property_finder.curated_poi.google_takeout.pipeline import (
    run as run_google_places_poi,
    run_input_dir,
)
from nyc_property_finder.curated_poi.google_takeout.resolve import resolve_place_ids
from nyc_property_finder.curated_poi.google_takeout.summary import build_summary
from nyc_property_finder.services.duckdb_service import DuckDBService


def _current_details_cache_row(
    google_place_id: str,
    payload: dict[str, object] | None = None,
    fetched_at: str = "2026-04-20T00:00:00+00:00",
) -> dict[str, object]:
    return {
        "google_place_id": google_place_id,
        "fetched_at": fetched_at,
        "field_mask": PLACE_DETAILS_FIELD_MASK,
        "cache_schema_version": PLACE_DETAILS_CACHE_SCHEMA_VERSION,
        "payload": payload or {},
    }


def test_parse_google_places_saved_list_csv_preserves_takeout_metadata(tmp_path) -> None:
    export_path = tmp_path / "New York - Bookstores.csv"
    export_path.write_text(
        "\n".join(
            [
                "Title,Note,URL,Tags,Comment",
                ",,,,",
                "Ursula Bookshop,near the park,https://www.google.com/maps/place/Ursula+Bookshop,books,check hours",
            ]
        ),
        encoding="utf-8",
    )

    parsed = parse_google_places_saved_list_csv(export_path)

    assert len(parsed) == 1
    row = parsed.iloc[0]
    assert row["source_record_id"].startswith("src_")
    assert row["source_system"] == "google_maps_takeout"
    assert row["source_file"] == "New York - Bookstores.csv"
    assert row["source_list_name"] == "New York - Bookstores"
    assert row["category"] == "bookstores"
    assert row["subcategory"] == "bookstores"
    assert row["detail_level_3"] == ""
    assert row["input_title"] == "Ursula Bookshop"
    assert row["note"] == "near the park"
    assert row["tags"] == "books"
    assert row["comment"] == "check hours"
    assert row["source_url"] == "https://www.google.com/maps/place/Ursula+Bookshop"
    assert row["search_query"] == "Ursula Bookshop New York, NY"


def test_parse_google_places_saved_list_csv_accepts_one_line_offset_header(tmp_path) -> None:
    export_path = tmp_path / "Restaurants.csv"
    export_path.write_text(
        "\n".join(
            [
                "Saved places",
                "Title,Note,URL,Tags,Comment",
                "Donovan's Pub,,https://www.google.com/maps/place/Donovan%27s+Pub,,",
            ]
        ),
        encoding="utf-8",
    )

    parsed = parse_google_places_saved_list_csv(export_path)

    assert parsed.iloc[0]["input_title"] == "Donovan's Pub"
    assert parsed.iloc[0]["category"] == "restaurants"
    assert parsed.iloc[0]["subcategory"] == "restaurants"
    assert parsed.iloc[0]["source_url"] == "https://www.google.com/maps/place/Donovan's+Pub"


def test_build_search_query_uses_simple_nyc_context() -> None:
    assert build_search_query("  Donovan's   Pub  ") == "Donovan's Pub New York, NY"
    assert build_search_query("Donovan's Pub", search_context="") == "Donovan's Pub"
    assert (
        build_search_query("Donovan's Pub", address="57-24 Roosevelt Ave, Queens, NY")
        == "Donovan's Pub 57-24 Roosevelt Ave, Queens, NY New York, NY"
    )


def test_clean_list_category_uses_list_name() -> None:
    assert clean_list_category("New York - Cocktail Bars") == "cocktail_bars"
    assert clean_list_category("NYC Museums") == "museums"
    assert clean_list_category("") == "other"


def test_normalize_curated_taxonomy_uses_file_rules_and_tags() -> None:
    assert normalize_curated_taxonomy("poi_pizza_nyc.csv", "Pizza") == {
        "category": "restaurants",
        "subcategory": "pizza",
        "detail_level_3": "",
    }
    assert normalize_curated_taxonomy(
        "poi_restaurants_nyc.csv",
        "Restaurants",
        tags="Bagels; Thai",
    ) == {
        "category": "restaurants",
        "subcategory": "bagels",
        "detail_level_3": "bagels|thai",
    }
    assert normalize_curated_taxonomy(
        "poi_bars_nyc.csv",
        "Bars",
        tags="Irish",
    ) == {
        "category": "bars",
        "subcategory": "irish_pub",
        "detail_level_3": "",
    }
    assert normalize_curated_taxonomy(
        "poi_sandwich_nyc.csv",
        "Sandwiches",
        tags="Deli; Italian",
    ) == {
        "category": "restaurants",
        "subcategory": "sandwiches",
        "detail_level_3": "deli|italian",
    }


def test_read_env_file_and_google_maps_api_key_fallback(tmp_path, monkeypatch) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join(
            [
                "NYC_PROPERTY_FINDER_ENV=local",
                "GOOGLE_MAPS_API_KEY='from-file'",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    assert read_env_file(env_path)["GOOGLE_MAPS_API_KEY"] == "from-file"
    assert get_google_maps_api_key(env_path=env_path) == "from-file"

    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "from-env")
    assert get_google_maps_api_key(env_path=env_path) == "from-env"


def test_read_api_keys_file_supports_scalar_and_mapping(tmp_path, monkeypatch) -> None:
    api_keys_path = tmp_path / "api_keys.yaml"

    api_keys_path.write_text("from-scalar", encoding="utf-8")
    assert read_api_keys_file(api_keys_path) == "from-scalar"

    api_keys_path.write_text("google_maps_api_key: from-mapping", encoding="utf-8")
    assert read_api_keys_file(api_keys_path) == "from-mapping"

    api_keys_path.write_text("keys:\n  places_api_key: from-nested", encoding="utf-8")
    assert read_api_keys_file(api_keys_path) == "from-nested"

    api_keys_path.write_text("keys:\n  places_api_key:\n    key: from-wrapper", encoding="utf-8")
    assert read_api_keys_file(api_keys_path) == "from-wrapper"

    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    assert (
        get_google_maps_api_key(
            env_path=tmp_path / "missing.env",
            api_keys_path=api_keys_path,
        )
        == "from-wrapper"
    )


def test_plan_dry_run_estimates_calls_without_cache(tmp_path) -> None:
    export_path = tmp_path / "Restaurants.csv"
    export_path.write_text(
        "\n".join(
            [
                "Title,Note,URL,Tags,Comment",
                "Donovan's Pub,,https://www.google.com/maps/place/Donovan%27s+Pub,,",
                "Rolo's,,https://www.google.com/maps/place/Rolo%27s,,",
            ]
        ),
        encoding="utf-8",
    )

    report = plan_dry_run(
        export_path,
        resolution_cache_path=tmp_path / "missing_resolution.csv",
        details_cache_path=tmp_path / "missing_details.jsonl",
    )

    assert report.input_rows == 2
    assert report.unique_source_records == 2
    assert report.resolution_cache_hits == 0
    assert report.resolution_cache_misses == 2
    assert report.estimated_text_search_calls == 2
    assert report.estimated_place_details_calls == 2
    assert report.categories == ["restaurants"]
    assert report.subcategories == ["restaurants"]
    assert report.detail_level_3_values == []
    assert report.to_dict()["search_context"] == "New York, NY"


def test_plan_dry_run_uses_resolution_and_details_caches(tmp_path) -> None:
    export_path = tmp_path / "Restaurants.csv"
    export_path.write_text(
        "\n".join(
            [
                "Title,Note,URL,Tags,Comment",
                "Donovan's Pub,,https://www.google.com/maps/place/Donovan%27s+Pub,,",
                "Rolo's,,https://www.google.com/maps/place/Rolo%27s,,",
            ]
        ),
        encoding="utf-8",
    )
    parsed = parse_google_places_saved_list_csv(export_path)
    first_source_id = parsed.iloc[0]["source_record_id"]

    resolution_cache_path = tmp_path / "place_resolution_cache.csv"
    resolution_cache_path.write_text(
        "\n".join(
            [
                "source_record_id,google_place_id",
                f"{first_source_id},places/donovans",
            ]
        ),
        encoding="utf-8",
    )
    details_cache_path = tmp_path / "place_details_cache.jsonl"
    details_cache_path.write_text(
        json.dumps(_current_details_cache_row("places/donovans", {"displayName": {"text": "Donovan's Pub"}})),
        encoding="utf-8",
    )

    report = plan_dry_run(
        export_path,
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
    )

    assert report.resolution_cache_hits == 1
    assert report.resolution_cache_misses == 1
    assert report.cached_google_place_ids == 1
    assert report.details_cache_hits == 1
    assert report.details_cache_misses_for_cached_places == 0
    assert report.estimated_text_search_calls == 1
    assert report.estimated_place_details_calls == 1


def test_plan_directory_dry_run_reports_per_file_assignments(tmp_path) -> None:
    input_dir = tmp_path / "poi_nyc"
    input_dir.mkdir()
    (input_dir / "poi_pizza_nyc.csv").write_text(
        "Title,Note,URL,Tags,Comment\nLucali,,,,\n",
        encoding="utf-8",
    )
    (input_dir / "poi_bars_nyc.csv").write_text(
        "Title,Note,URL,Tags,Comment\nThe Quays Pub,,,Irish,\n",
        encoding="utf-8",
    )

    report = plan_directory_dry_run(
        input_dir=input_dir,
        resolution_cache_path=tmp_path / "missing_resolution.csv",
        details_cache_path=tmp_path / "missing_details.jsonl",
    )

    assert report.file_count == 2
    assert report.input_rows == 2
    assert report.estimated_text_search_calls == 2
    assert [Path(file.input_path).name for file in report.files] == [
        "poi_bars_nyc.csv",
        "poi_pizza_nyc.csv",
    ]
    assert report.files[0].subcategories == ["irish_pub"]
    assert report.files[1].categories == ["restaurants"]


def test_read_details_cache_place_ids_accepts_wrapped_and_nested_payloads(tmp_path) -> None:
    details_cache_path = tmp_path / "place_details_cache.jsonl"
    details_cache_path.write_text(
        "\n".join(
            [
                json.dumps(_current_details_cache_row("places/direct")),
                json.dumps(
                    {
                        "google_place_id": "places/nested",
                        "field_mask": PLACE_DETAILS_FIELD_MASK,
                        "cache_schema_version": PLACE_DETAILS_CACHE_SCHEMA_VERSION,
                        "payload": {"id": "places/nested"},
                    }
                ),
                "not json",
            ]
        ),
        encoding="utf-8",
    )

    assert read_details_cache_place_ids(details_cache_path) == {"places/direct", "places/nested"}


def test_text_search_request_only_requests_place_ids() -> None:
    request = build_text_search_id_request("Ursula Bookshop New York, NY", api_key="secret")

    assert request.full_url == "https://places.googleapis.com/v1/places:searchText"
    assert request.get_method() == "POST"
    assert request.headers["X-goog-fieldmask"] == TEXT_SEARCH_ID_FIELD_MASK
    assert request.headers["X-goog-api-key"] == "secret"
    assert json.loads(request.data.decode("utf-8")) == {
        "textQuery": "Ursula Bookshop New York, NY"
    }


def test_place_details_request_only_requests_mapping_fields() -> None:
    request = build_place_details_request("places/abc 123", api_key="secret")

    assert request.full_url == "https://places.googleapis.com/v1/places/places%2Fabc%20123"
    assert request.get_method() == "GET"
    assert request.headers["X-goog-fieldmask"] == PLACE_DETAILS_FIELD_MASK
    assert request.headers["X-goog-api-key"] == "secret"


def test_resolve_place_ids_writes_cache_and_respects_existing_hits(tmp_path) -> None:
    export_path = tmp_path / "New York - Bookstores.csv"
    export_path.write_text(
        "\n".join(
            [
                "Title,Note,URL,Tags,Comment",
                "Ursula Bookshop,,https://www.google.com/maps/place/Ursula+Bookshop,,",
                "Books Are Magic,,https://www.google.com/maps/place/Books+Are+Magic,,",
            ]
        ),
        encoding="utf-8",
    )
    parsed = parse_google_places_saved_list_csv(export_path)
    first_source_id = parsed.iloc[0]["source_record_id"]

    resolution_cache_path = tmp_path / "place_resolution_cache.csv"
    resolution_cache_path.write_text(
        "\n".join(
            [
                "source_record_id,source_system,source_file,source_list_name,input_title,source_url,search_query,google_place_id,match_status",
                f"{first_source_id},google_maps_takeout,New York - Bookstores.csv,New York - Bookstores,Ursula Bookshop,,,places/ursula,top_candidate",
            ]
        ),
        encoding="utf-8",
    )
    calls = []

    def fetcher(query: str, api_key: str):
        calls.append((query, api_key))
        return {"google_place_id": "places/booksaremagic", "match_status": "top_candidate"}

    report = resolve_place_ids(
        export_path,
        api_key="secret",
        resolution_cache_path=resolution_cache_path,
        max_text_search_calls=1,
        fetcher=fetcher,
    )
    cache = read_resolution_cache(resolution_cache_path)

    assert calls == [("Books Are Magic New York, NY", "secret")]
    assert report.input_cache_hits == 1
    assert report.existing_resolved_cache_rows == 1
    assert report.attempted_text_search_calls == 1
    assert report.resolved == 1
    assert set(cache["google_place_id"]) == {"places/ursula", "places/booksaremagic"}


def test_resolve_place_ids_stops_before_exceeding_call_cap(tmp_path) -> None:
    export_path = tmp_path / "New York - Bookstores.csv"
    export_path.write_text(
        "\n".join(
            [
                "Title,Note,URL,Tags,Comment",
                "Ursula Bookshop,,https://www.google.com/maps/place/Ursula+Bookshop,,",
                "Books Are Magic,,https://www.google.com/maps/place/Books+Are+Magic,,",
            ]
        ),
        encoding="utf-8",
    )

    def fetcher(query: str, api_key: str):
        raise AssertionError("Fetcher should not be called when cap is exceeded.")

    with pytest.raises(ValueError, match="exceed max_text_search_calls"):
        resolve_place_ids(
            export_path,
            api_key="secret",
            resolution_cache_path=tmp_path / "place_resolution_cache.csv",
            max_text_search_calls=1,
            fetcher=fetcher,
        )


def test_resolve_place_ids_requires_api_key(tmp_path, monkeypatch) -> None:
    export_path = tmp_path / "New York - Bookstores.csv"
    export_path.write_text("Title,Note,URL,Tags,Comment\nUrsula Bookshop,,,,", encoding="utf-8")

    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GOOGLE_MAPS_API_KEY"):
        resolve_place_ids(
            export_path,
            api_key=None,
            resolution_cache_path=tmp_path / "place_resolution_cache.csv",
            env_path=tmp_path / "missing.env",
            api_keys_path=tmp_path / "missing_api_keys.yaml",
        )


def test_enrich_place_details_writes_jsonl_cache_and_respects_hits(tmp_path) -> None:
    resolution_cache_path = tmp_path / "place_resolution_cache.csv"
    resolution_cache_path.write_text(
        "\n".join(
            [
                "source_record_id,source_system,source_file,source_list_name,category,subcategory,detail_level_3,input_title,note,tags,comment,source_url,search_query,google_place_id,match_status",
                "src_1,google_maps_takeout,Bookstores.csv,Bookstores,bookstores,independent_bookstores,,Ursula,,,,url,query,places/ursula,top_candidate",
                "src_2,google_maps_takeout,Bookstores.csv,Bookstores,bookstores,independent_bookstores,,Books Are Magic,,,,url,query,places/books,top_candidate",
            ]
        ),
        encoding="utf-8",
    )
    details_cache_path = tmp_path / "place_details_cache.jsonl"
    details_cache_path.write_text(
        json.dumps(_current_details_cache_row("places/ursula", {"displayName": {"text": "Ursula Bookshop"}}))
        + "\n",
        encoding="utf-8",
    )
    calls = []

    def fetcher(place_id: str, api_key: str):
        calls.append((place_id, api_key))
        return {
            "displayName": {"text": "Books Are Magic"},
            "formattedAddress": "122 Montague St, Brooklyn, NY",
            "location": {"latitude": 40.694, "longitude": -73.992},
        }

    report = enrich_place_details(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        api_key="secret",
        max_details_calls=1,
        fetcher=fetcher,
    )
    cache = read_details_cache(details_cache_path)

    assert calls == [("places/books", "secret")]
    assert report.details_cache_hits == 1
    assert report.attempted_details_calls == 1
    assert set(cache) == {"places/ursula", "places/books"}


def test_build_dim_user_poi_v2_uses_details_and_json_arrays(tmp_path) -> None:
    resolution_cache_path = tmp_path / "place_resolution_cache.csv"
    resolution_cache_path.write_text(
        "\n".join(
            [
                "source_record_id,source_system,source_file,source_list_name,category,subcategory,detail_level_3,input_title,note,tags,comment,source_url,search_query,google_place_id,match_status",
                "src_1,google_maps_takeout,Bookstores.csv,Bookstores,bookstores,independent_bookstores,deli|italian,Ursula,quiet,tag,note,url1,query,places/ursula,top_candidate",
                "src_2,google_maps_takeout,Bookstores.csv,Favorites,bookstores,staff_picks,staff_pick,Ursula,cozy,,,url2,query,places/ursula,top_candidate",
            ]
        ),
        encoding="utf-8",
    )
    details_cache_path = tmp_path / "place_details_cache.jsonl"
    details_cache_path.write_text(
        json.dumps(
            _current_details_cache_row(
                "places/ursula",
                {
                    "displayName": {"text": "Ursula Bookshop"},
                    "formattedAddress": "1016 Union St, Brooklyn, NY",
                    "location": {"latitude": 40.674, "longitude": -73.963},
                    "rating": 4.7,
                    "userRatingCount": 812,
                    "businessStatus": "OPERATIONAL",
                    "editorialSummary": {"text": "Neighborhood favorite.", "languageCode": "en"},
                    "priceLevel": "PRICE_LEVEL_MODERATE",
                    "websiteUri": "https://ursulabookshop.com",
                },
            )
        )
        + "\n",
        encoding="utf-8",
    )

    dim = build_dim_user_poi_v2(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
    )
    row = dim.iloc[0]

    assert len(dim) == 1
    assert row["poi_id"].startswith("poi_")
    assert row["name"] == "Ursula Bookshop"
    assert row["address"] == "1016 Union St, Brooklyn, NY"
    assert row["lat"] == 40.674
    assert row["lon"] == -73.963
    assert json.loads(row["source_systems"]) == ["google_maps_takeout"]
    assert row["primary_source_system"] == "google_maps_takeout"
    assert row["category"] == "bookstores"
    assert row["subcategory"] == "independent_bookstores"
    assert row["detail_level_3"] == "deli"
    assert json.loads(row["source_list_names"]) == ["Bookstores", "Favorites"]
    assert json.loads(row["categories"]) == ["bookstores"]
    assert json.loads(row["subcategories"]) == ["independent_bookstores", "staff_picks"]
    assert row["primary_subcategory"] == "independent_bookstores"
    assert json.loads(row["detail_level_3_values"]) == ["deli", "italian", "staff_pick"]
    assert row["primary_detail_level_3"] == "deli"
    assert json.loads(row["note"]) == ["quiet", "cozy"]
    assert bool(row["has_place_details"]) is True
    assert row["rating"] == 4.7
    assert row["user_rating_count"] == 812
    assert row["business_status"] == "OPERATIONAL"
    assert row["editorial_summary"] == "Neighborhood favorite."
    assert row["editorial_summary_language_code"] == "en"
    assert row["price_level"] == "PRICE_LEVEL_MODERATE"
    assert row["website_uri"] == "https://ursulabookshop.com"


def test_pipeline_writes_dim_user_poi_v2(tmp_path) -> None:
    export_path = tmp_path / "Bookstores.csv"
    export_path.write_text(
        "Title,Note,URL,Tags,Comment\nUrsula Bookshop,quiet,url,tag,comment\n",
        encoding="utf-8",
    )
    database_path = tmp_path / "nyc_property_finder.duckdb"
    summary_path = tmp_path / "place_pipeline_summary.json"
    qa_path = tmp_path / "place_pipeline_qa.csv"

    def resolve_fetcher(query: str, api_key: str):
        return {"google_place_id": "places/ursula", "match_status": "top_candidate"}

    def details_fetcher(place_id: str, api_key: str):
        return {
            "displayName": {"text": "Ursula Bookshop"},
            "formattedAddress": "1016 Union St, Brooklyn, NY",
            "location": {"latitude": 40.674, "longitude": -73.963},
        }

    # Run the lower-level pieces with fakes, then let the pipeline build/write
    # from those caches without making additional calls.
    resolution_cache_path = tmp_path / "place_resolution_cache.csv"
    details_cache_path = tmp_path / "place_details_cache.jsonl"
    resolve_place_ids(
        export_path,
        api_key="secret",
        resolution_cache_path=resolution_cache_path,
        fetcher=resolve_fetcher,
    )
    enrich_place_details(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        api_key="secret",
        fetcher=details_fetcher,
    )

    report = run_google_places_poi(
        export_path,
        database_path=database_path,
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        max_text_search_calls=0,
        max_details_calls=0,
        api_key="secret",
        summary_path=summary_path,
        qa_path=qa_path,
    )

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        rows = duckdb_service.query_df("SELECT name, address, lat, lon FROM property_explorer_gold.dim_user_poi_v2")

    assert report.dim_rows == 1
    assert report.dim_with_coordinates == 1
    assert report.stage_table_name == "property_explorer_gold.stg_user_poi_google_takeout"
    assert report.summary_path == str(summary_path)
    assert report.qa_path == str(qa_path)
    assert summary_path.exists()
    assert qa_path.exists()
    assert rows.iloc[0]["name"] == "Ursula Bookshop"


def test_run_input_dir_writes_one_combined_dim_user_poi_v2(tmp_path) -> None:
    input_dir = tmp_path / "poi_nyc"
    input_dir.mkdir()
    (input_dir / "poi_pizza_nyc.csv").write_text(
        "Title,Note,URL,Tags,Comment\nLucali,,,,\n",
        encoding="utf-8",
    )
    (input_dir / "poi_bars_nyc.csv").write_text(
        "Title,Note,URL,Tags,Comment\nThe Quays Pub,,,Irish,\n",
        encoding="utf-8",
    )
    database_path = tmp_path / "nyc_property_finder.duckdb"
    summary_path = tmp_path / "place_pipeline_summary.json"
    qa_path = tmp_path / "place_pipeline_qa.csv"

    resolution_map = {
        "Lucali New York, NY": {"google_place_id": "places/lucali", "match_status": "top_candidate"},
        "The Quays Pub New York, NY": {"google_place_id": "places/quays", "match_status": "top_candidate"},
    }
    details_map = {
        "places/lucali": {
            "displayName": {"text": "Lucali"},
            "formattedAddress": "575 Henry St, Brooklyn, NY",
            "location": {"latitude": 40.681, "longitude": -74.000},
        },
        "places/quays": {
            "displayName": {"text": "The Quays Pub"},
            "formattedAddress": "84-09 Grand Ave, Queens, NY",
            "location": {"latitude": 40.713, "longitude": -73.882},
        },
    }

    def resolve_fetcher(query: str, api_key: str):
        return resolution_map[query]

    def details_fetcher(place_id: str, api_key: str):
        return details_map[place_id]

    # Seed caches file-by-file, then let the batch runner build/write once.
    from nyc_property_finder.curated_poi.google_takeout.resolve import resolve_place_ids
    from nyc_property_finder.curated_poi.google_takeout.enrich import enrich_place_details

    resolution_cache_path = tmp_path / "place_resolution_cache.csv"
    details_cache_path = tmp_path / "place_details_cache.jsonl"
    for csv_path in sorted(input_dir.glob("*.csv")):
        resolve_place_ids(
            csv_path,
            api_key="secret",
            resolution_cache_path=resolution_cache_path,
            fetcher=resolve_fetcher,
        )
    enrich_place_details(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        api_key="secret",
        fetcher=details_fetcher,
    )

    report = run_input_dir(
        input_dir=input_dir,
        database_path=database_path,
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        max_text_search_calls=0,
        max_details_calls=0,
        api_key="secret",
        summary_path=summary_path,
        qa_path=qa_path,
    )

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        rows = duckdb_service.query_df(
            """
            SELECT name, primary_category, primary_subcategory
            FROM property_explorer_gold.dim_user_poi_v2
            ORDER BY name
            """
        )

    assert report.resolve.input_path == str(input_dir)
    assert report.resolve.parsed_rows == 2
    assert report.dim_rows == 2
    assert report.summary["source_rows"] == 2
    assert report.summary["unique_google_place_ids"] == 2
    assert rows["name"].tolist() == ["Lucali", "The Quays Pub"]
    assert rows["primary_category"].tolist() == ["restaurants", "bars"]
    assert rows["primary_subcategory"].tolist() == ["pizza", "irish_pub"]

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        stage_rows = duckdb_service.query_df(
            "SELECT name FROM property_explorer_gold.stg_user_poi_google_takeout ORDER BY name"
        )

    assert stage_rows["name"].tolist() == ["Lucali", "The Quays Pub"]


def test_build_dim_user_poi_v2_falls_back_blank_subcategory_to_category(tmp_path) -> None:
    resolution_cache_path = tmp_path / "place_resolution_cache.csv"
    resolution_cache_path.write_text(
        "\n".join(
            [
                "source_record_id,source_system,source_file,source_list_name,category,subcategory,detail_level_3,input_title,note,tags,comment,source_url,search_query,google_place_id,match_status",
                "src_1,google_maps_takeout,Markets.csv,Markets,food_markets,,,Essex Market,,,,url,query,places/essex,top_candidate",
            ]
        ),
        encoding="utf-8",
    )
    details_cache_path = tmp_path / "place_details_cache.jsonl"
    details_cache_path.write_text(
        json.dumps(
            _current_details_cache_row(
                "places/essex",
                {
                    "displayName": {"text": "Essex Market"},
                    "formattedAddress": "88 Essex St, New York, NY",
                    "location": {"latitude": 40.718, "longitude": -73.988},
                },
            )
        )
        + "\n",
        encoding="utf-8",
    )

    dim = build_dim_user_poi_v2(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
    )
    row = dim.iloc[0]

    assert row["category"] == "food_markets"
    assert row["subcategory"] == "food_markets"
    assert row["primary_subcategory"] == "food_markets"
    assert json.loads(row["subcategories"]) == ["food_markets"]


def test_build_summary_flags_duplicate_place_ids(tmp_path) -> None:
    resolution_cache_path = tmp_path / "place_resolution_cache.csv"
    resolution_cache_path.write_text(
        "\n".join(
            [
                "source_record_id,source_system,source_file,source_list_name,category,subcategory,detail_level_3,input_title,note,tags,comment,source_url,search_query,google_place_id,match_status",
                "src_1,google_maps_takeout,Bookstores.csv,Bookstores,bookstores,independent_bookstores,,Book Club,,,,url,query,places/bookclub,top_candidate",
                "src_2,google_maps_takeout,Bookstores.csv,Bookstores,bookstores,independent_bookstores,,Bluestockings,,,,url,query,places/bookclub,top_candidate",
            ]
        ),
        encoding="utf-8",
    )
    details_cache_path = tmp_path / "place_details_cache.jsonl"
    details_cache_path.write_text(
        json.dumps(
            _current_details_cache_row(
                "places/bookclub",
                {
                    "displayName": {"text": "Book Club Bar"},
                    "formattedAddress": "197 E 3rd St, New York, NY",
                    "location": {"latitude": 40.723, "longitude": -73.983},
                },
            )
        )
        + "\n",
        encoding="utf-8",
    )

    summary = build_summary(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
    )

    assert summary["source_rows"] == 2
    assert summary["unique_google_place_ids"] == 1
    assert summary["duplicate_place_groups"] == 1
    assert summary["duplicate_source_rows"] == 2
    assert summary["missing_coordinate_rows"] == 0


def test_build_summary_can_filter_to_current_source_record_ids(tmp_path) -> None:
    resolution_cache_path = tmp_path / "place_resolution_cache.csv"
    resolution_cache_path.write_text(
        "\n".join(
            [
                "source_record_id,source_system,source_file,source_list_name,category,subcategory,detail_level_3,input_title,note,tags,comment,source_url,search_query,google_place_id,match_status",
                "src_current,google_maps_takeout,Bookstores.csv,Bookstores,bookstores,independent_bookstores,,Ursula,,,,url,query,places/ursula,top_candidate",
                "src_legacy,google_maps_takeout,Legacy.csv,Legacy,bookstores,independent_bookstores,,Legacy Books,,,,url,query,places/legacy,top_candidate",
            ]
        ),
        encoding="utf-8",
    )
    details_cache_path = tmp_path / "place_details_cache.jsonl"
    details_cache_path.write_text(
        "\n".join(
            [
                json.dumps(
                    _current_details_cache_row(
                        "places/ursula",
                        {
                            "displayName": {"text": "Ursula Bookshop"},
                            "formattedAddress": "1016 Union St, Brooklyn, NY",
                            "location": {"latitude": 40.674, "longitude": -73.963},
                        },
                    )
                ),
                json.dumps(
                    _current_details_cache_row(
                        "places/legacy",
                        {
                            "displayName": {"text": "Legacy Books"},
                            "formattedAddress": "1 Legacy St, Brooklyn, NY",
                            "location": {"latitude": 40.670, "longitude": -73.960},
                        },
                    )
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = build_summary(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        source_record_ids={"src_current"},
    )

    assert summary["source_rows"] == 1
    assert summary["resolved_source_rows"] == 1
    assert summary["unique_google_place_ids"] == 1
    assert summary["dim_rows"] == 1


def test_enrich_place_details_refreshes_stale_cache_rows(tmp_path) -> None:
    resolution_cache_path = tmp_path / "place_resolution_cache.csv"
    resolution_cache_path.write_text(
        "\n".join(
            [
                "source_record_id,source_system,source_file,source_list_name,category,subcategory,detail_level_3,input_title,note,tags,comment,source_url,search_query,google_place_id,match_status",
                "src_1,google_maps_takeout,Restaurants.csv,Restaurants,restaurants,restaurants,,Lucali,,,,url,query,places/lucali,top_candidate",
            ]
        ),
        encoding="utf-8",
    )
    details_cache_path = tmp_path / "place_details_cache.jsonl"
    details_cache_path.write_text(
        json.dumps(
            {
                "google_place_id": "places/lucali",
                "fetched_at": "2026-04-20T00:00:00+00:00",
                "payload": {"displayName": {"text": "Lucali"}},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    calls = []

    def fetcher(place_id: str, api_key: str):
        calls.append((place_id, api_key))
        return {
            "displayName": {"text": "Lucali"},
            "formattedAddress": "575 Henry St, Brooklyn, NY",
            "location": {"latitude": 40.681, "longitude": -74.0},
            "rating": 4.8,
        }

    report = enrich_place_details(
        resolution_cache_path=resolution_cache_path,
        details_cache_path=details_cache_path,
        api_key="secret",
        max_details_calls=1,
        fetcher=fetcher,
    )
    cache = read_details_cache(details_cache_path)

    assert calls == [("places/lucali", "secret")]
    assert report.details_cache_hits == 0
    assert report.attempted_details_calls == 1
    assert cache["places/lucali"]["field_mask"] == PLACE_DETAILS_FIELD_MASK
    assert cache["places/lucali"]["cache_schema_version"] == PLACE_DETAILS_CACHE_SCHEMA_VERSION
