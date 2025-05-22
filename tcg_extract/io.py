import csv
import requests
from bs4 import BeautifulSoup, element
from tcg_extract.utils import COLUMNS

def fetch_html_table() -> element.Tag:
    """
    Fetch the Pokémon TCG Pocket "Complete Card Dex" table from a Game8 archive page.
    The url is [here](https://game8.co/games/Pokemon-TCG-Pocket/archives/482685).

    Returns
    -------
    bs4.element.Tag
            The `<table>` element with classes
            "a-table", "table--fixed", and "flexible-cell".

    Raises
    ------
    requests.HTTPError
        If the HTTP request to `url` returns a bad status.
    RuntimeError
        If no `<table>` is found in the fetched HTML.
    """
    url = "https://game8.co/games/Pokemon-TCG-Pocket/archives/482685"
    
    # Download page
    response = requests.get(url)
    response.raise_for_status()

    # Parse total HTML with BeautifulSoup
    soup = BeautifulSoup(response.text, "lxml")

    # Locate the table we want
    table = soup.select_one("table.a-table.table--fixed.flexible-cell")
    if table is None:
        raise RuntimeError(
            "Could not find the card-dex table with "
            "classes 'a-table', 'table--fixed', 'flexible-cell' on page: "
            f"{url}"
        )

    return table
    

def write_to_csv(cards_data: list[dict[str, str]], output_file: str):
    """
    Writes a list of dictionaries containing card data to a CSV file.

    Creates a CSV file at the output path, writes headers based on dictionary keys,
    and writes elements of `cards_data` as rows.

    Args:
        cards_data (list): A list full of dictionaries containing cleaned card attributes.
        output_file (str): The path to save the created csv to.
    """

    # Iterate through list and write each dict as a new row
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        for card in cards_data:
            writer.writerow(card)
