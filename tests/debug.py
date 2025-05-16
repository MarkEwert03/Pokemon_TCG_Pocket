import argparse
import json
from bs4 import BeautifulSoup
from tcg_extract.parser import extract_card

def debug_card_extract(html: str, pokemon_id: str):
    """
    Finds the row for a given Pokémon ID and prints the extracted card info as JSON.

    Parameters:
        html (str):
            Full HTML content containing one or more <tr> rows with Pokémon cards.
        pokemon_id (str):
            The card ID (e.g., "A1 007") to search for.
    """
    soup = BeautifulSoup(html, "lxml")
    rows = soup.find_all("tr")

    for row in rows:
        bold = row.find("b", class_="a-bold")
        if bold and bold.text.strip() == pokemon_id:
            card = extract_card(row)
            print(json.dumps(card, indent=2, ensure_ascii=False))
            return

    print(f"[!] No row found for Pokémon ID: {pokemon_id}")

def main():
    parser = argparse.ArgumentParser(description="Debug Pokémon card extraction.")
    parser.add_argument("pokemon_id", nargs="?", default="A1 001", help="Pokémon card ID (e.g., 'A1 007')")
    parser.add_argument("--html", default="sample_cards.html", help="Path to the HTML file containing card data.")
    args = parser.parse_args()

    try:
        with open(args.html, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print(f"[!] HTML file not found: {args.html}")
        return

    debug_card_extract(html, args.pokemon_id)

if __name__ == "__main__":
    main()
