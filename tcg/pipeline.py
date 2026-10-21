"""
The whole pipeline, in order:

    1. fetch.ensure_raw_json      raw JSON  -> data/raw/cards.json
    2. from_json.convert_all      JSON      -> one dict per card (JSON fields only)
    3. scrape_extras              card page -> generation, illustrator, weakness, ...
    4. merge + overrides          fix known-bad cards
    5. write_csv                  -> data/full.csv
"""

import csv
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tcg import fetch
from tcg.card_page import parse_card_page
from tcg.config import (
    COLUMNS,
    FAILED_PAGES_PATH,
    OUTPUT_CSV_PATH,
    PAGE_FIELDS,
    RAW_JSON_PATH,
)
from tcg.from_json import convert_all, load_raw_cards
from tcg.overrides import apply_overrides
from tcg.utils import is_trainer_type


def scrape_extras(
    cards: list[dict],
    refresh: bool = False,
    workers: int = 4,
    delay: float = 0.25,
) -> tuple[dict[str, dict], dict[str, str]]:
    """
    Fetch + parse the card page of every card.

    Returns
    -------
    extras : {card number: parsed page fields}
    failures : {card number: reason}
    """
    extras: dict[str, dict] = {}
    failures: dict[str, str] = {}

    def work(card: dict):
        number = card["number"]
        if not card["url"]:
            return number, None, "no archive_url in JSON"
        try:
            html = fetch.get_card_html(card["url"], refresh=refresh, delay=delay)
            if html is None:
                return number, None, "page returned 404"
            parsed = parse_card_page(
                html,
                is_trainer=is_trainer_type(card["type"]),
                ability_name=card["ability_name"],
            )
            return number, parsed, None
        except Exception as e:  # keep going; report at the end
            return number, None, f"{type(e).__name__}: {e}"

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for i, (number, parsed, error) in enumerate(pool.map(work, cards), start=1):
            if error:
                failures[number] = error
                print(f"  ! {number}: {error}")
            else:
                extras[number] = parsed
            if i % 100 == 0 or i == len(cards):
                print(f"  scraped {i}/{len(cards)} cards")

    return extras, failures


def merge_extras(card: dict, extra: dict | None) -> None:
    """Copy page fields into `card`, never overwriting a value the JSON already had."""
    if not extra:
        return
    for field in PAGE_FIELDS:
        if card[field] is None and extra.get(field) is not None:
            card[field] = extra[field]


def write_csv(cards: list[dict], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(cards)


def print_report(cards: list[dict]) -> None:
    """Non-empty count per column — a quick way to spot a broken parser."""
    print(f"\n{len(cards)} cards. Filled values per column:")
    for col in COLUMNS:
        filled = sum(1 for c in cards if c[col] is not None)
        print(f"  {col:<15} {filled:>5}/{len(cards)}")

    numbers = [c["number"] for c in cards]
    dupes = {n for n in numbers if numbers.count(n) > 1}
    if dupes:
        print(f"\nWARNING: duplicate card numbers: {sorted(dupes)}")


def build_cards(
    json_path: Path = RAW_JSON_PATH,
    refresh_json: bool = False,
    refresh_pages: bool = False,
    skip_pages: bool = False,
    limit: int | None = None,
    only: str | None = None,
    workers: int = 4,
    delay: float = 0.25,
) -> list[dict]:
    """Run stages 1-4 and return the finished card dicts (`only` = a single card number)."""
    fetch.ensure_raw_json(json_path, refresh=refresh_json)
    cards = convert_all(load_raw_cards(json_path))
    if only:
        cards = [c for c in cards if c["number"] == only]
    if limit:
        cards = cards[:limit]

    if not skip_pages:
        print(f"Scraping {len(cards)} card pages (cached pages are reused)...")
        extras, failures = scrape_extras(cards, refresh_pages, workers, delay)
        for card in cards:
            merge_extras(card, extras.get(card["number"]))

        if failures:
            FAILED_PAGES_PATH.parent.mkdir(parents=True, exist_ok=True)
            FAILED_PAGES_PATH.write_text(
                "\n".join(f"{n}\t{why}" for n, why in failures.items()), encoding="utf-8"
            )
            print(f"{len(failures)} pages failed -> {FAILED_PAGES_PATH}")
        elif FAILED_PAGES_PATH.exists():
            FAILED_PAGES_PATH.unlink()

    for card in cards:
        apply_overrides(card)
    return cards


def run(output_file: Path = OUTPUT_CSV_PATH, **kwargs) -> None:
    cards = build_cards(**kwargs)
    write_csv(cards, output_file)
    print_report(cards)
    print(f"\nCSV file created: {output_file}")
