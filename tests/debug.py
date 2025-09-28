import argparse
import json
import os
from collections import OrderedDict
from tcg.utils import COLUMN_NAMES
from tcg.io import fetch_html_table
from tcg.parser import extract_card

GAME8_BASE_LINK = "https://game8.co/games/Pokemon-TCG-Pocket/archives/"

def debug_card_extract(pokemon_id: str) -> dict[str, str]:
    """
    Extract metadata for a specific Pokémon card based on its ID.

    This function retrieves the HTML table of cards (either freshly fetched or passed in),
    searches for a row matching the given Pokémon ID (e.g., "A1 007"),
    and returns a dictionary of parsed card information.

    Args
    ----
        pokemon_id : str
            The Pokémon card ID to search for (e.g., "A1 001").

    Returns
    -------
        out : dict[str, str]
            A dictionary containing the extracted metadata fields for the card.

    Raises
    ------
        Exception: If no matching card row is found for the given ID.

    Example
    -------
        >>> debug_card_extract("A1 001")
        {
            "number": "A1 001",
            "name": "Bulbasaur",
            "rarity": "◇",
            "stage": "Basic",
            "HP": "70",
            "type": "Grass",
            "weakness": "Fire",
            "retreat_cost": "1",
            "generation": "Gen 1",
            "illustrator": "Narumi Sato",
            "pack_name": "Genetic Apex (A1) Mewtwo",
            "pack_points": "35",
            "ability_name": null,
            "ability_effect": null,
            "move1_name": "Vine Whip",
            "move1_cost": "🟢*️⃣",
            "move1_damage": "40",
            "move1_effect": null,
            "move2_name": null,
            "move2_cost": null,
            "move2_damage": null,
            "move2_effect": null,
            "image": "https://img.game8.co/3998332/91c4f79b2b3b4206205bf69db8dd3d1e.png/show",
            "url": "https://game8.co/games/Pokemon-TCG-Pocket/archives/476002"
        }
    """
    json_path = os.path.join(os.path.dirname(
        __file__), "..", "data", "page_mappings.json")
    with open(json_path, "r", encoding="utf-8") as f:
        page_mappings = json.load(f)
        good_exts = page_mappings["GOOD_EXTS"]
        try:
            page_ext = good_exts[pokemon_id]
            page_url = GAME8_BASE_LINK + str(page_ext)
        except KeyError as e:
            raise Exception(f"[!] No row found for Pokémon ID: {pokemon_id}")

        card = extract_card(page_url)
        return card


def main():
    """Runs main debug function by printing card dict."""
    parser = argparse.ArgumentParser(
        description="Debug Pokémon card extraction.")
    parser.add_argument(
        "pokemon_id", nargs="?", default="A1 001", help="Card ID to extract (e.g., 'A1 007')"
    )
    args = parser.parse_args()

    # Get HTML table from url
    card = debug_card_extract(args.pokemon_id)

    ordered_card = OrderedDict((key, card.get(key, "N/A")) for key in COLUMN_NAMES)
    print(json.dumps(ordered_card, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
