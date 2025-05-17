from bs4 import BeautifulSoup
from pathlib import Path
from tcg_extract.parser import extract_card
from tcg_extract.io import write_to_csv


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
    raw_dir = PROJ_ROOT / "data" / "raw"
    processed_dir = PROJ_ROOT / "data" / "processed"
    # Choose input file and generate matching output file path
    input_file = raw_dir / "large.html"
    output_file = processed_dir / input_file.with_suffix(".csv").name

    # Validate input and create output dir if needed
    if not input_file.is_file():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Load and parse the raw HTML file
    with open(input_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "lxml")

    # Extract the main table from the HTML file
    table = soup.find("table", class_="a-table")
    if table is None:
        raise ValueError(f"Table with class 'a-table' not found in {input_file}")

    # Extract all <tr> elements of the <tbody>
    cards_html = table.find("tbody").find_all("tr")
    if not cards_html:
        raise ValueError(f"No <tr> elements found int <tbody> {input_file}")

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
