"""Export one registered curated article into the normalized scrape CSV contract."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys

import pandas as pd
import requests

from nyc_property_finder.curated_poi.web_scraping.base import normalized_output_path
from nyc_property_finder.curated_poi.web_scraping.normalize import (
    build_normalized_scrape_dataframe,
    write_normalized_scrape_csv,
)
from nyc_property_finder.curated_poi.web_scraping.publications import get_parser
from nyc_property_finder.curated_poi.web_scraping.registry import get_article, get_article_by_slug, list_articles


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export one registered curated article into the normalized scrape CSV contract."
    )
    parser.add_argument("--publisher", help="Registered publisher name, for example 'Eater'.")
    parser.add_argument("--article-slug", help="Registered article slug to export.")
    parser.add_argument("--html", help="Local saved HTML file to parse.")
    parser.add_argument("--url", help="Override URL to fetch instead of the registry URL.")
    parser.add_argument("--out", help="Explicit output CSV path.")
    parser.add_argument(
        "--list-articles",
        action="store_true",
        help="Print the registered article slugs and exit.",
    )
    parser.add_argument(
        "--publisher-filter",
        help="Optional publisher filter for --list-articles.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.list_articles:
        for article in list_articles(args.publisher_filter):
            print(
                f"{article.publisher}\t{article.article_slug}\t{article.article_title}\t"
                f"{article.category}/{article.subcategory}\t{article.status}"
            )
        return 0

    if not args.article_slug:
        raise SystemExit("--article-slug is required unless --list-articles is used.")
    if not args.html and not args.url:
        raise SystemExit("Provide --html or --url.")

    article = get_article(args.publisher, args.article_slug) if args.publisher else get_article_by_slug(args.article_slug)
    parser = get_parser(article.parser_name)
    html = Path(args.html).read_text(encoding="utf-8") if args.html else fetch_html(args.url or article.article_url)
    rows = parser(html, article)
    source_file = Path(args.html).name if args.html else ""
    frame = build_normalized_scrape_dataframe(article=article, rows=rows, source_file=source_file)
    output_path = Path(args.out) if args.out else normalized_output_path(article, run_date=datetime.now().date().isoformat())
    write_normalized_scrape_csv(frame, output_path)
    print_summary(frame, output_path)
    return 0


def fetch_html(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def print_summary(frame: pd.DataFrame, output_path: Path) -> None:
    address_count = int(frame["raw_address"].fillna("").astype(str).str.strip().ne("").sum()) if not frame.empty else 0
    print(f"Wrote {len(frame)} rows to {output_path}")
    print(f"Rows with addresses: {address_count}")
    if not frame.empty:
        duplicate_count = int(frame.duplicated(subset=["item_name", "raw_address"]).sum())
        print(f"Duplicate name+address rows: {duplicate_count}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
