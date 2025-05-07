import os
from bs4 import BeautifulSoup
from parser import extract_card
from writer import write_to_csv


# Raw data found at
# https://game8.co/games/Pokemon-TCG-Pocket/archives/482685

# Input and output file paths
input_file = "data/raw/medium.html"
output_file = "data/processed/medium.csv"


def main():
    """
    Main driver function for HTML parsing and CSV writing.

    This function:
    - Opens the raw HTML file
    - Parses it with BeautifulSoup
    - Extracts one row from a table
    - Converts it to a structured dictionary
    - Writes it to a CSV file
    """
    # Check path exists
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' does not exist.")

    # Load and parse the raw HTML file
    with open(input_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "lxml")

    # Create list to store dict of cleaned card data
    cards_data = []

    # Extract the main table from the HTML file
    table = soup.find("table", class_="a-table")
    if table is None:
        raise ValueError(f"Table with class 'a-table' not found in {input_file}")

    # Extract all <tr> elements of the <tbody>
    cards_html = table.find("tbody").find_all("tr")
    if not cards_html:
        raise ValueError(f"No <tr> elements found int <tbody> {input_file}")

    # Iterate over each <tr> element representing all metadata for one card
    for card_html in cards_html:
        row = extract_card(card_html)
        cards_data.append(row)

    # Export the parsed data to CSV
    write_to_csv(cards_data, output_file)

    print(f"CSV file '{output_file}' created successfully!")


if __name__ == "__main__":
    main()
