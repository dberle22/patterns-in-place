from pathlib import Path

from nyc_property_finder.curated_poi.web_scraping.base import normalized_output_path
from nyc_property_finder.curated_poi.web_scraping.normalize import build_normalized_scrape_dataframe
from nyc_property_finder.curated_poi.web_scraping.publications.eater import parse_article
from nyc_property_finder.curated_poi.web_scraping.registry import get_article, list_articles


def test_eater_registry_contains_locked_articles() -> None:
    articles = list_articles("eater")

    assert [article.article_slug for article in articles] == [
        "best-bakeries-nyc",
        "best-babka-rugelach-jewish-bakeries-nyc",
        "best-jewish-appetizing-shop-deli-nyc",
        "best-live-music-restaurants-bars-nyc",
        "best-cocktail-bars-nyc-essential-bars-manhattan-brooklyn",
        "nyc-best-new-cocktail-bars-heatmap",
        "best-wine-lists-restaurants-bars-nyc",
        "best-natural-wine-bars-nyc",
        "best-hidden-bars-speakeasies-nyc",
        "best-outdoor-bars-drinking-nyc",
        "best-new-york-restaurants-38-map",
    ]
    assert get_article("eater", "best-jewish-appetizing-shop-deli-nyc").subcategory == "jewish"
    assert get_article("eater", "best-live-music-restaurants-bars-nyc").detail_level_3 == "live_music"
    assert get_article("eater", "best-cocktail-bars-nyc-essential-bars-manhattan-brooklyn").subcategory == "cocktail"
    assert get_article("eater", "best-natural-wine-bars-nyc").subcategory == "wine_bar"
    assert get_article("eater", "best-outdoor-bars-drinking-nyc").subcategory == "bars"
    assert get_article("eater", "best-outdoor-bars-drinking-nyc").detail_level_3 == "outdoor"
    assert get_article("eater", "best-bakeries-nyc").status == "loaded"


def test_parse_eater_article_extracts_rows_and_splits_multi_address_mentions() -> None:
    article = get_article("eater", "best-bakeries-nyc")
    html = """
    <html>
      <head>
        <script type="application/ld+json">
          {
            "@type": "ItemList",
            "itemListElement": [
              {
                "@type": "ListItem",
                "position": 1,
                "item": {
                  "name": "Maman",
                  "url": "https://ny.eater.com/maps/best-bakeries-nyc#maman"
                }
              },
              {
                "@type": "ListItem",
                "position": 2,
                "item": {
                  "name": "Orwashers Bakery",
                  "url": "https://ny.eater.com/maps/best-bakeries-nyc#orwashers-bakery"
                }
              }
            ]
          }
        </script>
      </head>
      <body>
        <h2 id="maman">Maman</h2>
        <p>Location 239 Centre St, New York, NY 10013; 375 Hudson St, New York, NY 10014</p>
        <p>Why we love it: Rustic pastries and coffee.</p>
        <h2 id="orwashers-bakery">Orwashers Bakery</h2>
        <p>Location 308 E 78th St, New York, NY 10075</p>
        <p>Why we love it: Old-school bakery with great breads.</p>
      </body>
    </html>
    """

    rows = parse_article(html, article)

    assert len(rows) == 3
    assert [row.item_name for row in rows] == ["Maman", "Maman", "Orwashers Bakery"]
    assert rows[0].raw_address == "239 Centre St, New York, NY 10013"
    assert rows[1].raw_address == "375 Hudson St, New York, NY 10014"
    assert rows[0].raw_description == "Rustic pastries and coffee."
    assert rows[2].raw_description == "Old-school bakery with great breads."


def test_build_normalized_scrape_dataframe_maps_to_shared_contract() -> None:
    article = get_article("eater", "best-jewish-appetizing-shop-deli-nyc")
    html = """
    <html>
      <head>
        <script type="application/ld+json">
          {
            "@type": "ItemList",
            "itemListElement": [
              {
                "@type": "ListItem",
                "position": 1,
                "item": {
                  "name": "Russ & Daughters",
                  "url": "https://ny.eater.com/maps/best-jewish-appetizing-shop-deli-nyc#russ-daughters"
                }
              }
            ]
          }
        </script>
      </head>
      <body>
        <h2 id="russ-daughters">Russ &amp; Daughters</h2>
        <p>Location 179 E Houston St, New York, NY 10002</p>
        <p>Why we love it: An iconic appetizing shop.</p>
      </body>
    </html>
    """

    rows = parse_article(html, article)
    frame = build_normalized_scrape_dataframe(article, rows, source_file="best-jewish-appetizing-shop-deli-nyc.html")

    assert len(frame) == 1
    row = frame.iloc[0]
    assert row["publisher"] == "Eater"
    assert row["category"] == "restaurants"
    assert row["subcategory"] == "jewish"
    assert row["input_title"] == "Russ & Daughters"
    assert row["note"] == "179 E Houston St, New York, NY 10002"
    assert row["comment"] == "An iconic appetizing shop."
    assert row["search_query"] == "Russ & Daughters 179 E Houston St, New York, NY 10002 New York, NY"
    assert row["source_record_id"].startswith("src_")


def test_parse_eater_article_reads_next_data_map_points_when_live_html_uses_react_payload() -> None:
    article = get_article("eater", "best-bakeries-nyc")
    html = """
    <html>
      <head>
        <script type="application/ld+json">
          {
            "@type": "ItemList",
            "itemListElement": [
              {
                "@type": "ListItem",
                "position": 1,
                "item": {
                  "name": "Orwasher’s Bakery",
                  "url": "https://ny.eater.com/maps/best-bakeries-nyc#orwashers-bakery"
                }
              }
            ]
          }
        </script>
        <script id="__NEXT_DATA__" type="application/json">
          {
            "props": {
              "pageProps": {
                "hydration": {
                  "responses": [
                    {
                      "data": {
                        "node": {
                          "mapPoints": [
                            {
                              "name": "Orwasher’s Bakery",
                              "address": "308 E 78th St, New York, NY 10075, USA",
                              "description": [
                                {"plaintext": "Historic Upper East Side bakery known for breads and babka."}
                              ],
                              "venue": {
                                "slug": "orwashers-bakery"
                              }
                            }
                          ]
                        }
                      }
                    }
                  ]
                }
              }
            }
          }
        </script>
      </head>
      <body></body>
    </html>
    """

    rows = parse_article(html, article)

    assert len(rows) == 1
    assert rows[0].item_name == "Orwasher’s Bakery"
    assert rows[0].raw_address == "308 E 78th St, New York, NY 10075, USA"
    assert rows[0].raw_description == "Historic Upper East Side bakery known for breads and babka."


def test_normalized_output_path_uses_locked_naming_convention() -> None:
    article = get_article("eater", "best-new-york-restaurants-38-map")

    path = normalized_output_path(article, "2026-04-28")

    assert path == Path(
        "data/raw/scraped/normalized/restaurants_eater_best-new-york-restaurants-38-map_2026-04-28.csv"
    )
