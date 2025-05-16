import argparse
import json
from pathlib import Path
from collections import OrderedDict
from bs4 import BeautifulSoup
from tcg_extract.parser import extract_card


def debug_card_extract(html: str, pokemon_id: str):
    soup = BeautifulSoup(html, "lxml")
    rows = soup.find_all("tr")

    column_order = [
        "number",
        "name",
        "rarity",
        "stage",
        "HP",
        "type",
        "ability_name",
        "ability_effect",
        "move1_name",
        "move1_cost",
        "move1_damage",
        "move1_effect",
        "move2_name",
        "move2_cost",
        "move2_damage",
        "move2_effect",
        "retreat_cost",
        "pack_name",
        "pack_points",
        "image",
    ]
    for row in rows:
        bold = row.find("b", class_="a-bold")
        if bold and bold.text.strip() == pokemon_id:
            card = extract_card(row)
            ordered_card = OrderedDict((key, card.get(key, "N/A")) for key in column_order)
            print(json.dumps(ordered_card, indent=2, ensure_ascii=False))
            return

    print(f"[!] No row found for Pokémon ID: {pokemon_id}")


def main():
    default_html = Path(__file__).parent.parent / "data" / "raw" / "large.html"

    parser = argparse.ArgumentParser(description="Debug Pokémon card extraction.")
    parser.add_argument(
        "pokemon_id", nargs="?", default="A1 001", help="Card ID to extract (e.g., 'A1 007')"
    )
    parser.add_argument("--html", type=Path, default=default_html, help="Path to the HTML file.")
    args = parser.parse_args()

    if not args.html.exists():
        print(f"[!] HTML file not found: {args.html}")
        return

    html = args.html.read_text(encoding="utf-8")
    debug_card_extract(html, args.pokemon_id)


if __name__ == "__main__":
    main()
