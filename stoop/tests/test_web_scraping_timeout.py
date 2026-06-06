from pathlib import Path

from nyc_property_finder.curated_poi.web_scraping.base import normalized_output_path
from nyc_property_finder.curated_poi.web_scraping.normalize import build_normalized_scrape_dataframe
from nyc_property_finder.curated_poi.web_scraping.publications.timeout import parse_article
from nyc_property_finder.curated_poi.web_scraping.registry import get_article, list_articles


def test_timeout_registry_contains_locked_articles() -> None:
    articles = list_articles("time out")

    assert [article.article_slug for article in articles] == [
        "best-live-music-venues-in-new-york-city",
        "the-best-thrift-stores-in-new-york",
        "the-best-vintage-clothes-shops-in-new-york",
        "100-best-new-york-restaurants",
    ]
    assert get_article("Time Out", "the-best-thrift-stores-in-new-york").subcategory == "thrift"
    assert get_article("Time Out", "best-live-music-venues-in-new-york-city").status == "loaded"


def test_parse_timeout_article_extracts_ranked_rows_neighborhoods_and_summary() -> None:
    article = get_article("Time Out", "the-best-thrift-stores-in-new-york")
    html = """
    <html>
      <body>
        <div data-zone-name="large_list" data-testid="zone-large-list_testID">
          <h2 data-testid="zone-title_testID"><span>Best thrift stores in New York</span></h2>
          <div class="zoneItems">
            <article data-testid="tile-zone-large-list_testID">
              <div class="articleContent">
                <div class="title">
                  <a href="/newyork/shopping/auh20-thriftique" data-testid="tile-link_testID">
                    <h3 data-testid="tile-title_testID"><span>1.</span>&nbsp;2nd Street</h3>
                  </a>
                </div>
                <section data-testid="tags_testID">
                  <ul>
                    <li class="_tag_1"><span>Shopping</span></li>
                    <li class="_tag_2"><span>East Village</span></li>
                    <li class="_tagBare_3"><span>Recommended</span></li>
                  </ul>
                </section>
                <div data-testid="summary_testID">
                  <p>Find designer castoffs and everyday staples.</p>
                </div>
              </div>
            </article>
            <article data-testid="tile-zone-large-list_testID">
              <div class="articleContent">
                <div class="title">
                  <a href="/newyork/shopping/housing-works-thrift-shop" data-testid="tile-link_testID">
                    <h3 data-testid="tile-title_testID"><span>9.</span>&nbsp;Housing Works</h3>
                  </a>
                </div>
                <section data-testid="tags_testID">
                  <ul>
                    <li class="_tag_1"><span>Shopping</span></li>
                    <li class="_tag_2"><span>Thrift stores</span></li>
                    <li class="_tag_3"><span>Kips Bay</span></li>
                  </ul>
                </section>
                <div data-testid="summary_testID">
                  <p>Quality stock and a mission-driven thrift operation.</p>
                </div>
              </div>
            </article>
          </div>
        </div>
        <div data-zone-name="large_list" data-testid="zone-large-list_testID">
          <h2><span>Recommended</span></h2>
          <article data-testid="tile-zone-large-list_testID">
            <a href="/newyork/shopping/not-part-of-the-main-list" data-testid="tile-link_testID">
              <h3 data-testid="tile-title_testID">Should Not Parse</h3>
            </a>
          </article>
        </div>
      </body>
    </html>
    """

    rows = parse_article(html, article)

    assert len(rows) == 2
    assert rows[0].item_name == "2nd Street"
    assert rows[0].item_rank == 1
    assert rows[0].item_url == "https://www.timeout.com/newyork/shopping/auh20-thriftique"
    assert rows[0].raw_description == "Find designer castoffs and everyday staples."
    assert rows[0].raw_neighborhood == "East Village"
    assert rows[1].item_name == "Housing Works"
    assert rows[1].item_rank == 9
    assert rows[1].raw_neighborhood == "Kips Bay"


def test_build_normalized_scrape_dataframe_for_timeout_maps_to_shared_contract() -> None:
    article = get_article("Time Out", "best-live-music-venues-in-new-york-city")
    html = """
    <html>
      <body>
        <div data-zone-name="large_list" data-testid="zone-large-list_testID">
          <div class="zoneItems">
            <article data-testid="tile-zone-large-list_testID">
              <a href="/newyork/music/music-hall-of-williamsburg" data-testid="tile-link_testID">
                <h3 data-testid="tile-title_testID"><span>1.</span>&nbsp;Music Hall of Williamsburg</h3>
              </a>
              <section data-testid="tags_testID">
                <ul>
                  <li class="_tag_1"><span>Music</span></li>
                  <li class="_tag_2"><span>Music venues</span></li>
                  <li class="_tag_3"><span>Williamsburg</span></li>
                </ul>
              </section>
              <div data-testid="summary_testID">
                <p>One of the best rooms in New York to see a show.</p>
              </div>
            </article>
          </div>
        </div>
      </body>
    </html>
    """

    rows = parse_article(html, article)
    frame = build_normalized_scrape_dataframe(article, rows, source_file="best-live-music-venues-in-new-york-city.html")

    assert len(frame) == 1
    row = frame.iloc[0]
    assert row["publisher"] == "Time Out"
    assert row["category"] == "music_venues"
    assert row["subcategory"] == "music_venues"
    assert row["input_title"] == "Music Hall of Williamsburg"
    assert row["comment"] == "One of the best rooms in New York to see a show."
    assert row["source_url"] == "https://www.timeout.com/newyork/music/music-hall-of-williamsburg"
    assert row["search_query"] == "Music Hall of Williamsburg Williamsburg New York, NY"


def test_timeout_normalized_output_path_uses_locked_naming_convention() -> None:
    article = get_article("Time Out", "the-best-vintage-clothes-shops-in-new-york")

    path = normalized_output_path(article, "2026-04-29")

    assert path == Path(
        "data/raw/scraped/normalized/shopping_time_out_the-best-vintage-clothes-shops-in-new-york_2026-04-29.csv"
    )
