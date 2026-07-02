#!/usr/bin/env python3
"""Book of Hours text scraper — Rowenarium → structured JSONL.

Usage:
    python src/scraper_boh.py                          # Scrape all, output to data/raw/boh/
    python src/scraper_boh.py --output ./boh_data      # Custom output dir
    python src/scraper_boh.py --limit 10               # Test: scrape only 10 elements

Requires: requests, beautifulsoup4, tqdm
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL = "https://uadaf.theevilroot.xyz/rowenarium"
REQUEST_DELAY = 0.5  # Be polite to the server


def get_element_list() -> list[str]:
    """Scrape the full list of element IDs from Rowenarium index pages."""
    element_ids = set()

    # The main index lists elements grouped by source JSON file
    resp = requests.get(BASE_URL + "/")
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Find all links matching /rowenarium/element/{id}
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/rowenarium/element/" in href:
            elem_id = href.split("/rowenarium/element/")[-1]
            if elem_id and not elem_id.endswith(".json"):
                element_ids.add(elem_id)

    print(f"Found {len(element_ids)} unique element IDs")
    return sorted(element_ids)


def fetch_element(element_id: str) -> dict | None:
    """Fetch and parse a single element page."""
    url = f"{BASE_URL}/element/{element_id}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  Failed to fetch {element_id}: {e}", file=sys.stderr)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    data = {"id": element_id}

    # Extract Label from page heading
    h1 = soup.find("h1")
    if h1:
        data["label"] = h1.text.strip()

    # Extract Description from blockquote or detail section
    desc_elem = soup.find("blockquote") or soup.find(class_="desc")
    if desc_elem:
        data["desc"] = desc_elem.text.strip()

    # Extract Aspects table
    aspects_table = soup.find("table")
    if aspects_table:
        aspects = {}
        for row in aspects_table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                key = cells[0].text.strip()
                val = cells[1].text.strip()
                try:
                    val = int(val)
                except ValueError:
                    pass
                aspects[key] = val
        if aspects:
            data["aspects"] = aspects

    # Extract extended texts (xexts) — reading text, etc.
    xexts = {}
    for section in soup.find_all(["div", "section"], class_=re.compile(r"xext|reading|text")):
        key_elem = section.find(["h3", "h4", "strong"])
        val_elem = section.find(["p", "blockquote", "div"])
        if key_elem and val_elem:
            xexts[key_elem.text.strip()] = val_elem.text.strip()
    if xexts:
        data["xexts"] = xexts

    # Extract triggers
    triggers = []
    for trigger_section in soup.find_all(["div", "section"], class_="trigger"):
        trigger_text = trigger_section.text.strip()
        if trigger_text:
            triggers.append(trigger_text)
    if triggers:
        data["triggers"] = triggers

    time.sleep(REQUEST_DELAY)
    return data


def scrape_all(output_dir: Path, limit: int = 0) -> int:
    """Scrape all elements and save as individual markdown files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    element_ids = get_element_list()
    if limit:
        element_ids = element_ids[:limit]
        print(f"Limited to {limit} elements")

    success = 0
    for elem_id in tqdm(element_ids, desc="Scraping elements"):
        data = fetch_element(elem_id)
        if data is None:
            continue

        # Write as individual JSON file for easy inspection
        out_path = output_dir / f"{elem_id}.json"
        out_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        success += 1

    return success


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Book of Hours text data from Rowenarium"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "raw" / "boh",
        help="Output directory (default: data/raw/boh/)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of elements to scrape (0 = all)",
    )
    args = parser.parse_args()

    print(f"Output directory: {args.output}")
    print(f"Source: {BASE_URL}")
    print()

    count = scrape_all(args.output, args.limit)

    print(f"\nDone. Scraped {count} elements to {args.output}")
    print(f"Next step: run src/cleaner/ pipeline on {args.output} to produce structured JSONL")


if __name__ == "__main__":
    main()
