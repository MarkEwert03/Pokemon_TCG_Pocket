import argparse
import json
from pathlib import Path
from collections import OrderedDict
from bs4 import BeautifulSoup
from tcg_extract.parser import extract_card
from tcg_extract.io import fetch_html_table


def debug_card_extract(pokemon_id: str) -> dict[str, str]:
    # Pipeline input data directly from page
    pokemon_table = fetch_html_table()
    cards_html = pokemon_table.find("tbody").find_all("tr")

    for row in cards_html:
        bold = row.find("b", class_="a-bold")
        if bold and bold.text.strip() == pokemon_id:
            card = extract_card(row)
            return card

    print(f"[!] No row found for Pokémon ID: {pokemon_id}")


def main():
    parser = argparse.ArgumentParser(description="Debug Pokémon card extraction.")
    parser.add_argument(
        "pokemon_id", nargs="?", default="A1 001", help="Card ID to extract (e.g., 'A1 007')"
    )
    args = parser.parse_args()

    card = debug_card_extract(args.pokemon_id)
    
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
    ordered_card = OrderedDict((key, card.get(key, "N/A")) for key in column_order)
    print(json.dumps(ordered_card, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
