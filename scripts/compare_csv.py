"""
Compare a freshly built CSV against an older one (e.g. your previous data/full.csv
from the pack-table scraper) and report, per column, how many cards disagree.

    python scripts/compare_csv.py old_full.csv data/full.csv
    python scripts/compare_csv.py old_full.csv data/full.csv --show weakness rc

Only cards present in both files are compared. Expect a few known differences:
- move1_/move2_ columns shift for cards with an ability (the old scraper left
  move1 empty when an ability existed; the new pipeline does not)
- Colorless energy symbol (old: *️⃣, new: 🔘)
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def read(path: Path) -> dict[str, dict[str, str]]:
    with open(path, encoding="utf-8", newline="") as f:
        return {row["id"]: row for row in csv.DictReader(f)}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("old", type=Path)
    p.add_argument("new", type=Path)
    p.add_argument("--show", nargs="*", default=[], help="columns whose mismatches to list")
    p.add_argument("--max-show", type=int, default=15)
    args = p.parse_args()

    old, new = read(args.old), read(args.new)
    shared = sorted(set(old) & set(new))
    print(f"old: {len(old)} cards | new: {len(new)} cards | in both: {len(shared)}")
    print(f"only in new: {len(set(new) - set(old))} | only in old: {len(set(old) - set(new))}\n")

    columns = [c for c in new[shared[0]] if c in old[shared[0]]] if shared else []
    mismatches: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for card_id in shared:
        for col in columns:
            a, b = old[card_id][col], new[card_id][col]
            if a != b:
                mismatches[col].append((card_id, a, b))

    print(f"{'column':<16}{'differences':>12}")
    for col in columns:
        print(f"{col:<16}{len(mismatches[col]):>12}")

    for col in args.show:
        print(f"\n--- {col}: first {args.max_show} differences (card, old, new) ---")
        for card_id, a, b in mismatches[col][: args.max_show]:
            print(f"  {card_id:<10} {a!r:<30} {b!r}")


if __name__ == "__main__":
    main()
