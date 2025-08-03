import csv
import requests
from bs4 import BeautifulSoup, element
from tcg_extract.parser import extract_card
from tcg_extract.utils import COLUMNS, clean_str


def fetch_html_table(page_url: str, page_type: str = "") -> element.Tag:
    """
    Fetch the HTML table from the given URL. This table should either be:
    - The table on the [Pokémon TCG Pocket main page](https://game8.co/games/Pokemon-TCG-Pocket/archives/482685) which contains links to each pack page
    - A table on one of the pack pages containing all the informaiton for cards in that pack

    Parameters
    ----------
    page_url : str
        The URL for the Game8 page containing the table of card information.
    table_type : str
        The type of page containing tables. It is one of:
        - 'main' for the initial page with the table of packs
        - 'pack' for each pack page with the tables of cards

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
    if page_type == "main":
        table = soup.find("table", {"class": "a-table a-table table--fixed"})
    elif page_type == "pack":
        tables = soup.find_all("table", class_=["a-table", "table--fixed", "flexible-cell"])
        # Find the correct table
        table = None
        for t in tables:
            thead = t.find("thead")
            if not thead:
                continue

            first_row = thead.find("tr")
            if not first_row:
                continue

            first_cell = first_row.find(["th", "td"])
            if not first_cell:
                continue

            # The table with card info has first cell with a checkmark
            if first_cell.get_text(strip=True) == "✔":
                table = t
                break
    else:
        raise ValueError("Please use on of ['main', 'mode'] for `page_type`")

    if table is None:
        raise RuntimeError(
            f"Could not find the card-dex table with `{page_type}` on page {page_url}"
        )

    return table


def get_pack_names_and_urls() -> dict[str, str]:
    """
    Looks through the [Pokémon TCG Pocket main page](https://game8.co/games/Pokemon-TCG-Pocket/archives/482685) to extract the urls for each of the packs.

    Returns
    -------
    pack_names_urls : dict[str, str]
        A dict for all the packs where:
        - the key is the pack ID (like A1 or A3b)
        - the value is the url of the pack pages (containing the big pokemon table)
    """
    MAIN_URL = "https://game8.co/games/Pokemon-TCG-Pocket/archives/482685"
    # Download main page
    pack_pages_tables = fetch_html_table(MAIN_URL, page_type="main")

    # List to store pack urls to return
    pack_names_urls = {}

    for row in pack_pages_tables.find_all("tr"):
        first_cell = row.find("td")
        # Skip if row doesn't have <td>
        if not first_cell:
            continue

        pack_raw_name = clean_str(first_cell.text)
        pack_id = pack_raw_name[pack_raw_name.find("(") + 1 : pack_raw_name.rfind(")")]
        # Edge case for promo ID
        pack_id = "P-A" if pack_id == "Promo-" else pack_id

        # Find <a-link> containing the href (pack url)
        a_tag = first_cell.find("a", class_="a-link")
        pack_url = "https://game8.co" + a_tag["href"]
        # Add key-value pair to dict
        pack_names_urls[pack_id] = pack_url

    return pack_names_urls


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
    pokemon_table = fetch_html_table(page_url=pack_url, page_type="pack")

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
