"""Command-line entry point. See README.md for usage."""

import argparse
import json
from pathlib import Path

from tcg.config import OUTPUT_CSV_PATH, RAW_JSON_PATH
from tcg.pipeline import build_cards, run


def main() -> None:
    p = argparse.ArgumentParser(description="Build data/full.csv from game8's card database.")
    p.add_argument("--json", type=Path, default=RAW_JSON_PATH, help="Raw JSON path (default: data/raw/cards.json)")
    p.add_argument("--out", type=Path, default=OUTPUT_CSV_PATH, help="Output CSV path")
    p.add_argument("--refresh-json", action="store_true", help="Re-download the raw JSON")
    p.add_argument("--refresh-pages", action="store_true", help="Ignore the page cache and re-download every card page")
    p.add_argument("--no-pages", action="store_true", help="JSON only: skip scraping card pages (page-only columns stay blank)")
    p.add_argument("--limit", type=int, help="Only process the first N cards (for testing)")
    p.add_argument("--workers", type=int, default=4, help="Parallel page downloads (default 4)")
    p.add_argument("--delay", type=float, default=0.25, help="Seconds to wait after each download (default 0.25)")
    p.add_argument("--debug", metavar="CARD_ID", help='Print one finished card as JSON, e.g. --debug "A1 001"')
    args = p.parse_args()

    common = dict(
        json_path=args.json,
        refresh_json=args.refresh_json,
        refresh_pages=args.refresh_pages,
        skip_pages=args.no_pages,
        workers=args.workers,
        delay=args.delay,
    )

    if args.debug:
        cards = build_cards(only=args.debug, **common)
        if not cards:
            raise SystemExit(f"No card with id {args.debug!r}")
        print(json.dumps(cards[0], ensure_ascii=False, indent=2))
    else:
        run(output_file=args.out, limit=args.limit, **common)


if __name__ == "__main__":
    main()
