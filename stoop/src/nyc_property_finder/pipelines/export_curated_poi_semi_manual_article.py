"""Export one registered semi-manual curated article into the normalized scrape CSV contract."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys

import pandas as pd

from nyc_property_finder.curated_poi.web_scraping.base import normalized_output_path
from nyc_property_finder.curated_poi.web_scraping.normalize import (
    build_normalized_scrape_dataframe,
    write_normalized_scrape_csv,
)
from nyc_property_finder.curated_poi.web_scraping.registry import get_article, get_article_by_slug, list_articles
from nyc_property_finder.curated_poi.web_scraping.semi_manual import (
    SemiManualExtractionError,
    build_semi_manual_rows,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export one registered semi-manual curated article into the normalized scrape CSV contract."
    )
    parser.add_argument("--publisher", help="Registered publisher name, for example 'Wanderlog'.")
    parser.add_argument("--article-slug", help="Registered article slug to export.")
    parser.add_argument("--html", help="Local saved HTML file to normalize.")
    parser.add_argument("--text", help="Local saved text or markdown file to normalize.")
    parser.add_argument("--out", help="Explicit output CSV path.")
    parser.add_argument(
        "--list-articles",
        action="store_true",
        help="Print the registered semi-manual article slugs and exit.",
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
            if article.capture_mode != "semi_manual":
                continue
            print(
                f"{article.publisher}\t{article.article_slug}\t{article.article_title}\t"
                f"{article.category}/{article.subcategory}\t{article.status}"
            )
        return 0

    if not args.article_slug:
        raise SystemExit("--article-slug is required unless --list-articles is used.")
    if not args.html and not args.text:
        raise SystemExit("Provide --html or --text.")

    article = get_article(args.publisher, args.article_slug) if args.publisher else get_article_by_slug(args.article_slug)
    if article.capture_mode != "semi_manual":
        raise SystemExit(
            f"Article {article.publisher} / {article.article_slug} is not registered as capture_mode=semi_manual."
        )

    html = _read_input_file(args.html) if args.html else None
    text = _read_input_file(args.text) if not args.html and args.text else None
    source_file = Path(args.html or args.text).name

    try:
        extraction = build_semi_manual_rows(article, html=html, text=text)
    except SemiManualExtractionError as exc:
        raise SystemExit(f"ALERT: {exc}") from exc

    frame = build_normalized_scrape_dataframe(article=article, rows=extraction.rows, source_file=source_file)
    output_path = Path(args.out) if args.out else normalized_output_path(article, run_date=datetime.now().date().isoformat())
    write_normalized_scrape_csv(frame, output_path)
    print_summary(frame, output_path, extraction.extractor_name, extraction.guidance_notes)
    return 0


def _read_input_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def print_summary(
    frame: pd.DataFrame,
    output_path: Path,
    extractor_name: str,
    guidance_notes: list[str],
) -> None:
    address_count = int(frame["raw_address"].fillna("").astype(str).str.strip().ne("").sum()) if not frame.empty else 0
    neighborhood_count = int(frame["raw_neighborhood"].fillna("").astype(str).str.strip().ne("").sum()) if not frame.empty else 0
    print(f"Wrote {len(frame)} rows to {output_path}")
    print(f"Extractor: {extractor_name}")
    print(f"Guidance: {', '.join(guidance_notes)}")
    print(f"Rows with addresses: {address_count}")
    print(f"Rows with neighborhoods: {neighborhood_count}")
    if not frame.empty:
        duplicate_count = int(frame.duplicated(subset=["item_name", "raw_address"]).sum())
        print(f"Duplicate name+address rows: {duplicate_count}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
