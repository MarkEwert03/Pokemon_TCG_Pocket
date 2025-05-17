from bs4 import BeautifulSoup
from pathlib import Path
from tcg_extract.parser import extract_card
from tcg_extract.io import fetch_html_table, write_to_csv


# Raw data found at
# https://game8.co/games/Pokemon-TCG-Pocket/archives/482685


def main():
    """
    Main driver function for HTML parsing and CSV writing.

    This function:
    - Opens the raw HTML file
    - Parses it with BeautifulSoup
    - Extracts rows from the main table
    - Converts it to a structured dictionary
    - Writes it to a CSV file
    """
    # Define project root as two levels up from this file
    driver_file = Path(__file__).resolve()
    PROJ_ROOT = driver_file.parent.parent
    
    # Define input/output folders using absolute paths
    data_dir = PROJ_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Define output path
    output_file = data_dir / "full.csv"
    
    # Pipeline input data directly from page
    pokemon_table = fetch_html_table()

    # Extract all <tr> elements of the <tbody>
    cards_html = pokemon_table.find("tbody").find_all("tr")
    if not cards_html:
        raise ValueError("No <tr> elements found int <tbody>")

    # Create list to store dict of cleaned card data
    cards_data = []

    # Iterate over each <tr> element representing all metadata for one card
    for card_html in cards_html:
        row = extract_card(card_html)
        cards_data.append(row)

    # Export the parsed data to CSV
    write_to_csv(cards_data, output_file)

    print(f"CSV file created: {output_file.relative_to(PROJ_ROOT)}")


if __name__ == "__main__":
    main()
