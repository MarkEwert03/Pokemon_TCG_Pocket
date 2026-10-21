from bs4 import BeautifulSoup
from pathlib import Path
from tcg.io import get_pack_names_and_urls, extract_pack, write_to_csv


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

    # List to hold all cards
    cards_data = []

    pack_names_urls = get_pack_names_and_urls()

    # Go through all pages and extract all cards from each pack
    for pack_url in pack_names_urls.values():
        pack_data = extract_pack(pack_url)
        cards_data.extend(pack_data)

    # Export the parsed data to CSV
    write_to_csv(cards_data, output_file)

    print(f"CSV file created: {output_file.relative_to(PROJ_ROOT)}")


if __name__ == "__main__":
    main()
