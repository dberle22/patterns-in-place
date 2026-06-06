import json

import pandas as pd

from nyc_property_finder.pipelines.build_curated_poi_v3 import build_dim_user_poi_v3


def test_build_dim_user_poi_v3_promotes_classified_restaurant_fields() -> None:
    source = pd.DataFrame(
        [
            {
                "poi_id": "poi_1",
                "source_system": "google_places",
                "source_systems": '["google_places"]',
                "primary_source_system": "web_scrape",
                "source_record_id": "rec_1",
                "source_list_names": '["NY Mag - 1000 Best"]',
                "category": "restaurants",
                "subcategory": "mixed_restaurants",
                "detail_level_3": pd.NA,
                "categories": '["restaurants"]',
                "primary_category": "restaurants",
                "subcategories": '["mixed_restaurants"]',
                "primary_subcategory": "mixed_restaurants",
                "detail_level_3_values": "[]",
                "primary_detail_level_3": pd.NA,
                "name": "Huertas",
                "input_title": "Huertas",
                "note": pd.NA,
                "tags": pd.NA,
                "comment": pd.NA,
                "source_url": pd.NA,
                "google_place_id": "places/1",
                "match_status": "matched",
                "address": "107 1st Ave, New York, NY",
                "lat": 40.72,
                "lon": -73.98,
                "has_place_details": True,
                "details_fetched_at": pd.Timestamp("2026-05-10 10:00:00+00:00"),
                "rating": 4.5,
                "user_rating_count": 100,
                "business_status": "OPERATIONAL",
                "editorial_summary": pd.NA,
                "editorial_summary_language_code": pd.NA,
                "price_level": pd.NA,
                "website_uri": pd.NA,
            }
        ]
    )
    classified = pd.DataFrame(
        [
            {
                "poi_id": "poi_1",
                "final_category": "restaurants",
                "final_subcategory": "spanish",
                "final_detail_level_3": "tapas",
                "original_category": "restaurants",
                "original_subcategory": "mixed_restaurants",
                "original_detail_level_3": pd.NA,
                "classification_method": "rule_based",
                "classification_confidence": "high",
                "classification_score": 9,
                "classification_run_at": pd.Timestamp("2026-05-11 09:00:00+00:00"),
            }
        ]
    )

    output = build_dim_user_poi_v3(source, classified)
    row = output.iloc[0]

    assert row["subcategory"] == "spanish"
    assert row["primary_subcategory"] == "spanish"
    assert row["detail_level_3"] == "tapas"
    assert row["primary_detail_level_3"] == "tapas"
    assert json.loads(row["subcategories"]) == ["spanish"]
    assert json.loads(row["detail_level_3_values"]) == ["tapas"]
    assert row["original_subcategory"] == "mixed_restaurants"
    assert row["classification_method"] == "rule_based"
