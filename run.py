"""Command-line entry point. See README.md for usage."""

import argparse
import json
from pathlib import Path

from tcg.config import (
    FINAL_VALIDATION_LOG_PATH,
    NO_PAGES_OUTPUT_CSV_PATH,
    OVERRIDE_AUDIT_LOG_PATH,
    OUTPUT_CSV_PATH,
    RAW_JSON_PATH,
)
from tcg.pipeline import build_cards, run
from tcg.validation import audit_overrides, validate_csv_file


def main() -> None:
    p = argparse.ArgumentParser(description="Build data/full.csv from game8's card database.")
    p.add_argument("--json", type=Path, default=RAW_JSON_PATH, help="Raw JSON path (default: data/raw/cards.json)")
    p.add_argument("--out", type=Path, help="Output CSV path")
    p.add_argument("--refresh-json", action="store_true", help="Re-download the raw JSON")
    p.add_argument("--refresh-pages", action="store_true", help="Ignore the page cache and re-download every card page")
    p.add_argument("--no-pages", action="store_true", help="JSON only: skip scraping card pages (page-only columns stay blank)")
    p.add_argument("--limit", type=int, help="Only process the first N cards (for testing)")
    p.add_argument("--workers", type=int, default=4, help="Parallel page downloads (default 4)")
    p.add_argument("--delay", type=float, default=0.25, help="Seconds to wait after each download (default 0.25)")
    p.add_argument("--debug", metavar="CARD_ID", help='Print one finished card as JSON, e.g. --debug "A1 001"')
    p.add_argument(
        "--validate",
        action="store_true",
        help="Validate the final CSV and write a timestamped report in logs/",
    )
    p.add_argument(
        "--audit-overrides",
        action="store_true",
        help="Audit all overrides against the complete pre-override source data",
    )
    args = p.parse_args()

    if args.validate:
        findings = validate_csv_file(OUTPUT_CSV_PATH, FINAL_VALIDATION_LOG_PATH)
        if findings:
            print(
                f"Final validation found {len(findings)} required-field gaps. "
                f"See {FINAL_VALIDATION_LOG_PATH}."
            )
            for card_id, name, field in findings:
                print(f"  {card_id}\t{name}\t{field}")
            raise SystemExit(1)
        print("Final validation passed: no required-field gaps found.")
        return

    if args.audit_overrides:
        cards = build_cards(
            json_path=args.json,
            refresh_json=args.refresh_json,
            refresh_pages=args.refresh_pages,
            skip_pages=args.no_pages,
            workers=args.workers,
            delay=args.delay,
            apply_manual_overrides=False,
        )
        counts = audit_overrides(cards, OVERRIDE_AUDIT_LOG_PATH)
        print(
            f"Override audit complete: {counts['REDUNDANT']} redundant, "
            f"{counts['FILLING_MISSING']} filling missing, "
            f"{counts['ACTIVE_CORRECTION']} active corrections, "
            f"{counts['CARD_NOT_FOUND']} cards not found."
        )
        print(f"See {OVERRIDE_AUDIT_LOG_PATH}.")
        return

    common = dict(
        json_path=args.json,
        refresh_json=args.refresh_json,
        refresh_pages=args.refresh_pages,
        skip_pages=args.no_pages,
        workers=args.workers,
        delay=args.delay,
    )

    if args.debug:
        cards = build_cards(only=args.debug, write_reports=False, quiet=True, **common)
        if not cards:
            raise SystemExit(f"No card with id {args.debug!r}")
        print(json.dumps(cards[0], ensure_ascii=False, indent=2))
    else:
        output_file = args.out or (
            NO_PAGES_OUTPUT_CSV_PATH if args.no_pages else OUTPUT_CSV_PATH
        )
        run(output_file=output_file, limit=args.limit, **common)


if __name__ == "__main__":
    main()
