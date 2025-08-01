import csv
import requests
from bs4 import BeautifulSoup, element
from tcg_extract.parser import extract_card
from tcg_extract.utils import COLUMNS


def fetch_html_table(page_url: str, table_class: str) -> element.Tag:
    """
    Fetch the HTML table from the given URL. This table should either be:
    - The table on the [Pokémon TCG Pocket main page](https://game8.co/games/Pokemon-TCG-Pocket/archives/482685) which contains links to each pack page
    - A table on one of the pack pages containing all the informaiton for cards in that pack

    Parameters
    ----------
    page_url : str
        The URL for the Game8 page containing the table of card information.
    table_class : str
        The class of the table to look for and return

    Returns
    -------
    bs4.element.Tag
            The `<table>` element with class `table_class`

    Raises
    ------
    requests.HTTPError
        If the HTTP request to `url` returns a bad status.
    RuntimeError
        If no `<table>` is found in the fetched HTML.
    """
    # Download pack page
    response = requests.get(page_url)
    response.raise_for_status()

    # Parse total HTML with BeautifulSoup
    soup = BeautifulSoup(response.text, "lxml")

    # Locate the table we want
    # "table.a-table.table--fixed.flexible-cell"
    table = soup.find("table", {"class": table_class})
    if table is None:
        raise RuntimeError(f"Could not find the card-dex table with `{table_class}`")

    return table


def get_pack_url_pages() -> list[str]:
    """
    Looks through the [Pokémon TCG Pocket main page](https://game8.co/games/Pokemon-TCG-Pocket/archives/482685) to extract the urls for each of the packs.

    Returns
    -------
    pack_urls : list[str]
        A list of the urls for each of the pack pages (containing the big pokemon table)
    """
    MAIN_URL = "https://game8.co/games/Pokemon-TCG-Pocket/archives/482685"
    # Download main page
    pack_pages_tables = fetch_html_table(MAIN_URL, "a-table a-table table--fixed")

    # List to store pack urls to return
    pack_urls = []

    for row in pack_pages_tables.find_all("tr"):
        first_cell = row.find("td")
        # Skip if row doesn't have <td>
        if not first_cell:
            continue

        a_tag = first_cell.find("a", class_="a-link")
        pack_url = a_tag["href"]
        pack_urls.append(pack_url)

    return pack_urls


def extract_pack(pack_url: str) -> list[dict]:
    """
    Appends json card information to list for all cards in the pack

    Parameters
    ----------
    pack_url : str
        The URL for the Game8 page containing the `table.a-table.table--fixed.flexible-cell` table of Pokemon

    Returns
    -------
    pack_data : list[dict]
        The list containing all dictionaries representing cards in the pack
    """
    # Pipeline input data directly from page
    print(f"Fetching HTML Table from {pack_url}")
    pokemon_table = fetch_html_table()

    # Extract all <tr> elements of the <tbody>
    card_tr_elements = pokemon_table.find("tbody").find_all("tr")
    if not card_tr_elements:
        raise ValueError("No <tr> elements found int <tbody>")

    # Create list to store dict of cleaned card data
    pack_data = []

    # Iterate over each <tr> element representing all metadata for one card
    for card_html in card_tr_elements:
        try:
            id = card_html.find_all("td")[1].text
            row = extract_card(card_html)
            print(f"  Extracted card <{id}>")
            pack_data.append(row)
        except Exception as e:
            print(f"! ERROR FOR CARD <{id}> !")

    return pack_data


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
