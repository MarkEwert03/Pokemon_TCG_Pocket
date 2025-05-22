import argparse
import json
from collections import OrderedDict
import bs4
from tcg_extract.utils import COLUMNS
from tcg_extract.io import fetch_html_table
from tcg_extract.parser import extract_card


def debug_card_extract(pokemon_id: str, html: bs4.element.Tag | None = None) -> dict[str, str]:
    """
    Extract metadata for a specific Pokémon card based on its ID.

    This function retrieves the HTML table of cards (either freshly fetched or passed in),
    searches for a row matching the given Pokémon ID (e.g., "A1 007"),
    and returns a dictionary of parsed card information.

    Args
    ----------
        pokemon_id : str
            The Pokémon card ID to search for (e.g., "A1 001").
        html : bs4.element.Tag | None
            Optional cached HTML table of cards.
            If None, the HTML will be fetched from the source using `fetch_html_table()`.

    Returns
    ----------
        out : dict[str, str]
            A dictionary containing the extracted metadata fields for the card.

    Raises
    ----------
        Exception: If no matching card row is found for the given ID.

    Example
    ----------
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
    if html is None:
        # Pipeline input data directly from page
        pokemon_table = fetch_html_table()
    else:
        # Use cached HTML table
        pokemon_table = html

    cards_html = pokemon_table.find("tbody").find_all("tr")

    for row in cards_html:
        bold = row.find("b", class_="a-bold")
        if bold and bold.text.strip() == pokemon_id:
            card = extract_card(row)
            return card

    raise Exception(f"[!] No row found for Pokémon ID: {pokemon_id}")


def main():
    """Runs main debug function by printing card dict."""
    parser = argparse.ArgumentParser(description="Debug Pokémon card extraction.")
    parser.add_argument(
        "pokemon_id", nargs="?", default="A1 001", help="Card ID to extract (e.g., 'A1 007')"
    )
    args = parser.parse_args()

    # Get HTML table from url
    card = debug_card_extract(args.pokemon_id)

    ordered_card = OrderedDict((key, card.get(key, "N/A")) for key in COLUMNS)
    print(json.dumps(ordered_card, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
