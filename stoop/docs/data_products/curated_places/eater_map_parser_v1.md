# Eater Map Parser V1

## Goal

Build a Python script that takes an Eater map URL, downloads the HTML, extracts the ranked restaurant list, extracts addresses, and exports a clean CSV for use in the NYC Area Researcher / Curated POI workflow.

Example input:

```bash
python parse_eater_map.py --url "https://ny.eater.com/maps/best-bakeries-nyc" --out outputs/bakeries.csv
```

Example output:

```csv
rank,name,address,source_url,item_url
1,Orwasher’s Bakery,"308 E 78th St, New York, NY 10075",https://ny.eater.com/maps/best-bakeries-nyc,https://ny.eater.com/maps/best-bakeries-nyc#orwashers-bakery
```

## Core Approach

Eater map pages usually include a structured JSON-LD block with an `ItemList`. This is the best source for the ranked restaurant names and item URLs. Addresses may not appear in the JSON-LD, so the script should extract them from nearby HTML around each restaurant section.

Use stable signals instead of CSS classes:

1. JSON-LD `ItemList`
2. Restaurant name
3. Restaurant URL / anchor slug
4. Address-like text near each slug
5. Optional fallback search through embedded JSON

## Dependencies

```bash
pip install requests beautifulsoup4 lxml pandas
```

Optional later:

```bash
pip install extruct w3lib
```

## Script Structure

```text
parse_eater_map.py
  parse_args()
  fetch_html()
  load_html_from_file()
  extract_items_from_jsonld()
  extract_address_near_item()
  clean_address()
  build_records()
  export_csv()
  print_qa_summary()
  main()
```

## Pseudo-code

```python
import argparse
import json
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from html import unescape
from urllib.parse import urlparse


ADDRESS_PATTERN = re.compile(
    r"\d{1,5}\s+[A-Za-z0-9 .'\-]+"
    r"(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Broadway|Sq|Square|Pl|Place|Dr|Drive|Ln|Lane|Ct|Court)"
    r"[^<,\"]*(?:,\s*New York,\s*NY\s*\d{5})?",
    re.IGNORECASE
)


def parse_args():
    # Accept either a live URL or a saved HTML file
    # Require output path
    return args


def fetch_html(url):
    # Send browser-like user agent
    # Raise error if request fails
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def load_html_from_file(path):
    # Read saved HTML from disk
    return html


def extract_items_from_jsonld(html):
    soup = BeautifulSoup(html, "lxml")
    records = []

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
        except Exception:
            continue

        if data.get("@type") != "ItemList":
            continue

        for item in data.get("itemListElement", []):
            restaurant = item.get("item", {})

            records.append({
                "rank": item.get("position"),
                "name": restaurant.get("name"),
                "item_url": restaurant.get("url")
            })

    return records


def get_slug_from_item_url(item_url):
    # Example:
    # https://ny.eater.com/maps/best-bakeries-nyc#orwashers-bakery
    # returns: orwashers-bakery
    parsed = urlparse(item_url)
    return parsed.fragment


def extract_address_near_item(html, item):
    slug = get_slug_from_item_url(item["item_url"])

    search_terms = [
        slug,
        item["name"]
    ]

    for term in search_terms:
        start = html.find(term)
        if start == -1:
            continue

        # Look around the restaurant-specific section
        window = html[start:start + 10000]
        matches = ADDRESS_PATTERN.findall(unescape(window))

        if matches:
            return clean_address(matches[0])

    return None


def clean_address(address):
    # Normalize whitespace
    # Remove HTML artifacts
    # Strip trailing punctuation
    address = re.sub(r"\s+", " ", address)
    address = address.strip(" ,.;")
    return address


def build_records(html, source_url):
    items = extract_items_from_jsonld(html)

    output = []

    for item in items:
        address = extract_address_near_item(html, item)

        output.append({
            "rank": item["rank"],
            "name": item["name"],
            "address": address,
            "source_url": source_url,
            "item_url": item["item_url"]
        })

    return output


def export_csv(records, out_path):
    df = pd.DataFrame(records)
    df.to_csv(out_path, index=False)


def print_qa_summary(records):
    total = len(records)
    missing = [r for r in records if not r["address"]]

    print(f"Found {total} restaurants")
    print(f"Found {total - len(missing)} addresses")

    if missing:
        print("Missing addresses:")
        for r in missing:
            print(f"- {r['name']}")


def main():
    args = parse_args()

    if args.url:
        html = fetch_html(args.url)
        source_url = args.url
    else:
        html = load_html_from_file(args.html)
        source_url = args.source_url or ""

    records = build_records(html, source_url)

    print_qa_summary(records)
    export_csv(records, args.out)


if __name__ == "__main__":
    main()
```

## CLI Requirements

```bash
# Live URL
python parse_eater_map.py \
  --url "https://ny.eater.com/maps/best-bakeries-nyc" \
  --out outputs/bakeries.csv

# Saved HTML
python parse_eater_map.py \
  --html "data/raw/eater_bakeries.html" \
  --source-url "https://ny.eater.com/maps/best-bakeries-nyc" \
  --out outputs/bakeries.csv
```

## Acceptance Criteria

The script should:

1. Accept an Eater map URL or local HTML file.
2. Extract ranked restaurant names from JSON-LD.
3. Extract addresses from nearby HTML sections.
4. Export `rank`, `name`, `address`, `source_url`, and `item_url`.
5. Print a QA summary with total restaurants, address match count, and missing addresses.
6. Avoid relying on Eater CSS class names.

## Known Limitation

V1 may miss addresses if the HTML structure changes or if the address is only available in JavaScript state. If address coverage is low, V2 should recursively parse embedded JSON / Next.js data and search for fields like `address`, `streetAddress`, `postalCode`, `latitude`, and `longitude`.
