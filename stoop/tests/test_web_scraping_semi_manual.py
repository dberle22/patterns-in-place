from dataclasses import replace
from pathlib import Path

import pytest

from nyc_property_finder.curated_poi.web_scraping.base import ScrapedArticleRow
from nyc_property_finder.curated_poi.web_scraping.normalize import build_normalized_scrape_dataframe
from nyc_property_finder.curated_poi.web_scraping.registry import get_article
from nyc_property_finder.curated_poi.web_scraping import semi_manual
from nyc_property_finder.curated_poi.web_scraping.semi_manual import (
    SemiManualExtractionError,
    SemiManualHtmlExtractor,
    SemiManualTextExtractor,
    preferred_input_suffix,
    raw_capture_path,
)
from nyc_property_finder.pipelines.export_curated_poi_semi_manual_article import main


def test_wanderlog_registry_exposes_sparse_semi_manual_hints() -> None:
    article = get_article("Wanderlog", "best-food-halls-market-halls-and-food-courts-in-new-york-city")

    assert article.capture_mode == "semi_manual"
    assert article.semi_manual_hints == {
        "preferred_input": "html",
        "extractor_family": "wanderlog",
        "infer_item_urls": True,
        "min_candidate_rows": 10,
    }
    assert preferred_input_suffix(article) == "html"
    assert raw_capture_path(article, "2026-04-29") == Path(
        "data/raw/scraped/raw/wanderlog/best-food-halls-market-halls-and-food-courts-in-new-york-city_2026-04-29.html"
    )


def test_semi_manual_html_extractor_uses_wanderlog_guidance_and_jsonld() -> None:
    article = get_article("Wanderlog", "best-food-halls-market-halls-and-food-courts-in-new-york-city")
    html = """
    <html>
      <body>
        <div id="BoardPlaceView__place-1">
          <h2><span>1</span><a class="color-gray-900" href="/place/details/chelsea-market">Chelsea Market</a></h2>
          <div class="col p-0 minw-0">75 9th Ave, New York, NY 10011, USA<span class="font-weight-bold mx-2">•</span><a href="/place/details/chelsea-market">Tips and more reviews for Chelsea Market</a></div>
        </div>
        <div id="BoardPlaceView__place-2">
          <h2><span>2</span><a class="color-gray-900" href="/place/details/urban-hawker">Urban Hawker</a></h2>
          <div class="col p-0 minw-0">135 W 50th St, New York, NY 10020, USA<span class="font-weight-bold mx-2">•</span><a href="/place/details/urban-hawker">Tips and more reviews for Urban Hawker</a></div>
        </div>
        <div id="BoardPlaceView__place-3"><h2><span>3</span><a class="color-gray-900" href="/place/details/essex-market">Essex Market</a></h2><div class="col p-0 minw-0">88 Essex St, New York, NY 10002, USA<span class="font-weight-bold mx-2">•</span></div></div>
        <div id="BoardPlaceView__place-4"><h2><span>4</span><a class="color-gray-900" href="/place/details/market-57">Market 57</a></h2><div class="col p-0 minw-0">25 11th Ave, New York, NY 10011, USA<span class="font-weight-bold mx-2">•</span></div></div>
        <div id="BoardPlaceView__place-5"><h2><span>5</span><a class="color-gray-900" href="/place/details/dekalb-market-hall">Dekalb Market Hall</a></h2><div class="col p-0 minw-0">445 Albee Sq W, Brooklyn, NY 11201, USA<span class="font-weight-bold mx-2">•</span></div></div>
        <div id="BoardPlaceView__place-6"><h2><span>6</span><a class="color-gray-900" href="/place/details/tin-building">Tin Building</a></h2><div class="col p-0 minw-0">96 South St, New York, NY 10038, USA<span class="font-weight-bold mx-2">•</span></div></div>
        <div id="BoardPlaceView__place-7"><h2><span>7</span><a class="color-gray-900" href="/place/details/canal-st-market">Canal Street Market</a></h2><div class="col p-0 minw-0">265 Canal St, New York, NY 10013, USA<span class="font-weight-bold mx-2">•</span></div></div>
        <div id="BoardPlaceView__place-8"><h2><span>8</span><a class="color-gray-900" href="/place/details/japan-village">Japan Village</a></h2><div class="col p-0 minw-0">934 3rd Ave, Brooklyn, NY 11232, USA<span class="font-weight-bold mx-2">•</span></div></div>
        <div id="BoardPlaceView__place-9"><h2><span>9</span><a class="color-gray-900" href="/place/details/gansevoort-liberty-market">Gansevoort Liberty Market</a></h2><div class="col p-0 minw-0">4 World Trade Center, New York, NY 10007, USA<span class="font-weight-bold mx-2">•</span></div></div>
        <div id="BoardPlaceView__place-10"><h2><span>10</span><a class="color-gray-900" href="/place/details/turnstyle-marketplace">Turnstyle Underground Market</a></h2><div class="col p-0 minw-0">1000 8th Ave, New York, NY 10019, USA<span class="font-weight-bold mx-2">•</span></div></div>
      </body>
    </html>
    """

    result = SemiManualHtmlExtractor(article).extract(html)

    assert len(result.rows) == 10
    assert result.rows[0].item_name == "Chelsea Market"
    assert result.rows[0].item_url.endswith("/place/details/chelsea-market")
    assert result.rows[0].raw_address == "75 9th Ave, New York, NY 10011, USA"
    assert "wanderlog_anchor_candidates" in result.guidance_notes


def test_semi_manual_html_extractor_fails_fast_when_too_few_candidates() -> None:
    article = get_article("Wanderlog", "best-food-halls-market-halls-and-food-courts-in-new-york-city")
    html = """
    <html>
      <body>
        <div id="BoardPlaceView__place-1">
          <h2><span>1</span><a class="color-gray-900" href="/place/details/chelsea-market">Chelsea Market</a></h2>
        </div>
      </body>
    </html>
    """

    with pytest.raises(SemiManualExtractionError):
        SemiManualHtmlExtractor(article).extract(html)


def test_semi_manual_text_extractor_builds_ranked_rows() -> None:
    article = replace(
        get_article("Michelin Guide", "new-york-restaurants"),
        semi_manual_hints={"extractor_family": "michelin", "min_candidate_rows": 1},
    )
    text = """
    1. Le Bernardin
    2. Tatiana
    3. Dame
    """

    result = SemiManualTextExtractor(article).extract(text)

    assert [row.item_name for row in result.rows] == ["Le Bernardin", "Tatiana", "Dame"]
    assert [row.item_rank for row in result.rows] == [1, 2, 3]


def test_michelin_html_extractor_uses_rendered_restaurant_cards() -> None:
    article = replace(
        get_article("Michelin Guide", "new-york-restaurants"),
        semi_manual_hints={"extractor_family": "michelin", "min_candidate_rows": 1},
    )
    html = """
    <html>
      <body>
        <div class="card__menu selection-card  js-restaurant__list_item js-match-height js-map"
             data-index="0" data-id="1" data-lat="40.7" data-lng="-73.9" data-view="restaurant">
          <div class="flex-fill">
            <div class="card__menu-content card__menu-content--flex js-match-height-content">
              <div class="row">
                <div class="col col-12">
                  <h3 class="card__menu-content--title pl-text pl-big js-match-height-title">
                    <a href="/us/en/new-york-state/new-york/restaurant/icca" target="_self">Icca</a>
                  </h3>
                </div>
              </div>
              <div class="row flex-fill">
                <div class="col col-12">
                  <div class="align-items-end js-match-height-bottom">
                    <div class="card__menu-footer--score pl-text">New York, NY, USA</div>
                    <div class="card__menu-footer--score pl-text ">$$$$ · Japanese</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <a href="/us/en/new-york-state/new-york/restaurant/icca" class="link" target="_self" aria-label="Open Icca"></a>
        </div>
        <div class="card__menu selection-card  js-restaurant__list_item js-match-height js-map"
             data-index="1" data-id="2" data-lat="40.7" data-lng="-73.9" data-view="restaurant">
          <div class="flex-fill">
            <div class="card__menu-content card__menu-content--flex js-match-height-content">
              <div class="row">
                <div class="col col-12">
                  <h3 class="card__menu-content--title pl-text pl-big js-match-height-title">
                    <a href="/us/en/new-york-state/new-york/restaurant/chambers" target="_self">Chambers</a>
                  </h3>
                </div>
              </div>
              <div class="row flex-fill">
                <div class="col col-12">
                  <div class="align-items-end js-match-height-bottom">
                    <div class="card__menu-footer--score pl-text">Brooklyn, NY, USA</div>
                    <div class="card__menu-footer--score pl-text ">$$$ · Contemporary</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <a href="/us/en/new-york-state/new-york/restaurant/chambers" class="link" target="_self" aria-label="Open Chambers"></a>
        </div>
      </body>
    </html>
    """

    result = SemiManualHtmlExtractor(article).extract(html)

    assert [row.item_name for row in result.rows] == ["Icca", "Chambers"]
    assert result.rows[0].item_url.endswith("/restaurant/icca")
    assert result.rows[0].raw_description == "$$$$ - Japanese"
    assert result.rows[0].raw_neighborhood == ""
    assert result.rows[1].raw_neighborhood == "Brooklyn, NY, USA"
    assert "michelin_card_blocks" in result.guidance_notes


def test_bon_appetit_html_extractor_uses_jsonld_article_body_and_entry_links() -> None:
    article = replace(
        get_article("Bon Appetit", "nyc100"),
        semi_manual_hints={
            "preferred_input": "html",
            "extractor_family": "bon_appetit",
            "infer_item_urls": True,
            "min_candidate_rows": 1,
        },
    )
    html = """
    <html>
      <head>
        <script type="application/ld+json">
          {
            "@context": "http://schema.org",
            "@type": "NewsArticle",
            "articleBody": "Intro text\\n\\n1. The Place for Old-School Vibes That Are Actually Old-School\\nBarney Greengrass\\nUpper West Side, Manhattan\\nThe average age of a Barney Greengrass patron probably hovers around 67.\\n✵ Order: latkes and whitefish salad.\\n2. The Place for the Opposite of Brunch: Japanese Breakfast\\nOkonomi\\nWilliamsburg, Brooklyn\\nAt this tiny 12-seat spot, there is only one order.\\n✵ Order: the breakfast set."
          }
        </script>
      </head>
      <body>
        <p><a href="https://www.barneygreengrass.com/"><strong>Barney Greengrass</strong></a><br/><em>Upper West Side, Manhattan</em><br/>The average age of a Barney Greengrass patron probably hovers around 67.</p>
        <p><a href="http://www.okonomibk.com/"><strong>Okonomi</strong></a><br/><em>Williamsburg, Brooklyn</em><br/>At this tiny 12-seat spot, there is only one order.</p>
      </body>
    </html>
    """

    result = SemiManualHtmlExtractor(article).extract(html)

    assert [row.item_name for row in result.rows] == ["Barney Greengrass", "Okonomi"]
    assert [row.item_rank for row in result.rows] == [1, 2]
    assert result.rows[0].item_url == "https://www.barneygreengrass.com/"
    assert result.rows[0].raw_neighborhood == "Upper West Side"
    assert result.rows[0].raw_borough == "Manhattan"
    assert "Order: latkes and whitefish salad." in result.rows[0].raw_description
    assert result.rows[1].item_url == "http://www.okonomibk.com/"
    assert "bon_appetit_article_body" in result.guidance_notes


def test_ny_mag_html_extractor_uses_swiftype_listing_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    article = replace(
        get_article("NY Mag", "search-listings"),
        semi_manual_hints={
            "preferred_input": "html",
            "extractor_family": "ny_mag",
            "listing_type": "restaurant",
            "min_candidate_rows": 1,
        },
    )
    html = """
    <html>
      <body>
        <script>
          window.modules["287"] = [function(require,module,exports){
            function querySwiftype(e){
              return swiftype.query(e,{host:"https://host-2v4v9v.api.swiftype.com",token:"search-token",engine:"restaurant-and-bar-listings"})
            }
          }];
        </script>
      </body>
    </html>
    """

    def fake_fetch(*, host: str, token: str, engine: str, listing_type: str) -> list[dict[str, object]]:
        assert host == "https://host-2v4v9v.api.swiftype.com"
        assert token == "search-token"
        assert engine == "restaurant-and-bar-listings"
        assert listing_type == "restaurant"
        return [
            {
                "name": {"raw": "Le Bernardin"},
                "canonical_url": {"raw": "http://nymag.com/listings/restaurant/le-bernardin/"},
                "neighborhood": {"raw": "Theater District"},
                "borough": {"raw": "Manhattan"},
                "cuisines": {"raw": ["French", "Seafood"]},
                "teaser": {"raw": "A classic seafood palace."},
                "price": {"raw": "very expensive"},
            },
            {
                "name": {"raw": "Blue Hill at Stone Barns"},
                "canonical_url": {"raw": "http://nymag.com/listings/restaurant/blue-hill-at-stone-barns/"},
                "neighborhood": {"raw": "Westchester"},
                "borough": {"raw": ""},
                "cuisines": {"raw": ["Fine Dining", "Farm-to-Table"]},
                "teaser": {"raw": "Worth the trip."},
                "price": {"raw": "very expensive"},
            },
        ]

    monkeypatch.setattr(semi_manual, "_fetch_ny_mag_listings", fake_fetch)

    result = SemiManualHtmlExtractor(article).extract(html)

    assert [row.item_name for row in result.rows] == ["Le Bernardin", "Blue Hill at Stone Barns"]
    assert [row.item_rank for row in result.rows] == [1, 2]
    assert result.rows[0].item_url == "https://nymag.com/listings/restaurant/le-bernardin/"
    assert result.rows[0].raw_neighborhood == "Theater District"
    assert result.rows[0].raw_borough == "Manhattan"
    assert "Cuisines: French, Seafood" in result.rows[0].raw_description
    assert "ny_mag_swiftype_search" in result.guidance_notes


def test_vogue_vintage_html_extractor_uses_article_body_and_direct_store_links() -> None:
    article = replace(
        get_article("Vogue", "best-vintage-stores-in-new-york-city"),
        semi_manual_hints={
            "preferred_input": "html",
            "extractor_family": "vogue",
            "infer_item_urls": True,
            "min_candidate_rows": 1,
        },
    )
    html = """
    <html>
      <head>
        <script type="application/ld+json">
          {
            "@context": "http://schema.org",
            "@type": "NewsArticle",
            "articleBody": "Intro line.\\nAnother intro line.\\nJames Veloria\\nIt is a vintage rite of passage.\\nAddress: 75 East Broadway #225, Manhattan\\nWomen\\u2019s History Museum Vintage\\nIt\\u2019s impossible to know what you\\u2019ll find inside.\\nMark your calendars: the Vogue Vintage Market is back."
          }
        </script>
      </head>
      <body>
        <a href="https://www.jamesveloria.com/">James Veloria</a>
        <a href="https://womenshistorymuseum.co/vintage/">Women’s History Museum Vintage</a>
      </body>
    </html>
    """

    result = SemiManualHtmlExtractor(article).extract(html)

    assert [row.item_name for row in result.rows] == ["James Veloria", "Women’s History Museum Vintage"]
    assert result.rows[0].item_url == "https://www.jamesveloria.com/"
    assert result.rows[0].raw_address == "75 East Broadway #225, Manhattan"
    assert result.rows[0].raw_borough == "Manhattan"
    assert result.rows[1].item_url == "https://womenshistorymuseum.co/vintage/"
    assert result.rows[1].raw_address == ""
    assert "Vogue Vintage Market" not in result.rows[1].raw_description
    assert "vogue_article_body" in result.guidance_notes


def test_vogue_shopping_html_extractor_preserves_multiple_addresses() -> None:
    article = replace(
        get_article("Vogue", "the-best-shopping-in-nyc-according-to-vogue-staffers"),
        semi_manual_hints={
            "preferred_input": "html",
            "extractor_family": "vogue",
            "infer_item_urls": True,
            "min_candidate_rows": 1,
        },
    )
    html = """
    <html>
      <head>
        <script type="application/ld+json">
          {
            "@context": "http://schema.org",
            "@type": "NewsArticle",
            "articleBody": "Shopping intro.\\n\\n1. Salter House\\n119 Atlantic Ave, Brooklyn, NY 11201\\n34 E 2nd St, New York, NY 10003\\nA beautiful store for linens and home goods. \\u2014Chloe Schama\\n2. Lockwood\\n485 Driggs Ave, Brooklyn, NY 11211\\n33-06 Broadway, Astoria, NY 11106\\nA reliable neighborhood gift store."
          }
        </script>
      </head>
      <body>
        <a href="https://www.instagram.com/salter.house/?hl=en">Salter House</a>
        <a href="https://www.instagram.com/lockwoodshop/?hl=en">Lockwood</a>
      </body>
    </html>
    """

    result = SemiManualHtmlExtractor(article).extract(html)

    assert [row.item_name for row in result.rows] == ["Salter House", "Salter House", "Lockwood", "Lockwood"]
    assert [row.item_rank for row in result.rows] == [1, 1, 2, 2]
    assert result.rows[0].raw_address == "119 Atlantic Ave, Brooklyn, NY 11201"
    assert result.rows[1].raw_address == "34 E 2nd St, New York, NY 10003"
    assert result.rows[0].raw_borough == "Brooklyn"
    assert result.rows[1].raw_borough == ""
    assert result.rows[0].item_url == "https://www.instagram.com/salter.house/?hl=en"
    assert "Chloe Schama" not in result.rows[0].raw_description


def test_normalized_dataframe_appends_neighborhood_to_search_query_when_address_is_blank() -> None:
    article = get_article("Michelin Guide", "new-york-restaurants")
    frame = build_normalized_scrape_dataframe(
        article=article,
        rows=[
            ScrapedArticleRow(
                item_name="Dame",
                item_rank=1,
                item_url="",
                raw_address="",
                raw_description="Seafood spot",
                raw_neighborhood="Greenpoint",
                raw_borough="Brooklyn",
            )
        ],
        source_file="michelin.txt",
    )

    row = frame.iloc[0]
    assert row["raw_neighborhood"] == "Greenpoint"
    assert row["search_query"] == "Dame Greenpoint New York, NY"


def test_semi_manual_cli_prefers_html_and_writes_normalized_csv(tmp_path) -> None:
    article_slug = "best-food-halls-market-halls-and-food-courts-in-new-york-city"
    html_path = tmp_path / "wanderlog.html"
    text_path = tmp_path / "wanderlog.txt"
    out_path = tmp_path / "wanderlog.csv"

    html_path.write_text(
        """
        <html>
          <body>
            <div id="BoardPlaceView__place-1"><h2><span>1</span><a class="color-gray-900" href="/place/details/chelsea-market">Chelsea Market</a></h2><div class="col p-0 minw-0">75 9th Ave, New York, NY 10011, USA<span class="font-weight-bold mx-2">•</span></div></div>
            <div id="BoardPlaceView__place-2"><h2><span>2</span><a class="color-gray-900" href="/place/details/urban-hawker">Urban Hawker</a></h2><div class="col p-0 minw-0">135 W 50th St, New York, NY 10020, USA<span class="font-weight-bold mx-2">•</span></div></div>
            <div id="BoardPlaceView__place-3"><h2><span>3</span><a class="color-gray-900" href="/place/details/essex-market">Essex Market</a></h2><div class="col p-0 minw-0">88 Essex St, New York, NY 10002, USA<span class="font-weight-bold mx-2">•</span></div></div>
            <div id="BoardPlaceView__place-4"><h2><span>4</span><a class="color-gray-900" href="/place/details/market-57">Market 57</a></h2><div class="col p-0 minw-0">25 11th Ave, New York, NY 10011, USA<span class="font-weight-bold mx-2">•</span></div></div>
            <div id="BoardPlaceView__place-5"><h2><span>5</span><a class="color-gray-900" href="/place/details/dekalb-market-hall">Dekalb Market Hall</a></h2><div class="col p-0 minw-0">445 Albee Sq W, Brooklyn, NY 11201, USA<span class="font-weight-bold mx-2">•</span></div></div>
            <div id="BoardPlaceView__place-6"><h2><span>6</span><a class="color-gray-900" href="/place/details/tin-building">Tin Building</a></h2><div class="col p-0 minw-0">96 South St, New York, NY 10038, USA<span class="font-weight-bold mx-2">•</span></div></div>
            <div id="BoardPlaceView__place-7"><h2><span>7</span><a class="color-gray-900" href="/place/details/canal-st-market">Canal Street Market</a></h2><div class="col p-0 minw-0">265 Canal St, New York, NY 10013, USA<span class="font-weight-bold mx-2">•</span></div></div>
            <div id="BoardPlaceView__place-8"><h2><span>8</span><a class="color-gray-900" href="/place/details/japan-village">Japan Village</a></h2><div class="col p-0 minw-0">934 3rd Ave, Brooklyn, NY 11232, USA<span class="font-weight-bold mx-2">•</span></div></div>
            <div id="BoardPlaceView__place-9"><h2><span>9</span><a class="color-gray-900" href="/place/details/gansevoort-liberty-market">Gansevoort Liberty Market</a></h2><div class="col p-0 minw-0">4 World Trade Center, New York, NY 10007, USA<span class="font-weight-bold mx-2">•</span></div></div>
            <div id="BoardPlaceView__place-10"><h2><span>10</span><a class="color-gray-900" href="/place/details/turnstyle-marketplace">Turnstyle Underground Market</a></h2><div class="col p-0 minw-0">1000 8th Ave, New York, NY 10019, USA<span class="font-weight-bold mx-2">•</span></div></div>
          </body>
        </html>
        """,
        encoding="utf-8",
    )
    text_path.write_text("1. This text fallback should not be used\n", encoding="utf-8")

    exit_code = main(
        [
            "--publisher",
            "Wanderlog",
            "--article-slug",
            article_slug,
            "--html",
            str(html_path),
            "--text",
            str(text_path),
            "--out",
            str(out_path),
        ]
    )

    assert exit_code == 0
    output = out_path.read_text(encoding="utf-8")
    assert "Chelsea Market" in output
    assert "This text fallback should not be used" not in output
