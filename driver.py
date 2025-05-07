import csv
import os
import bs4

# Raw data found at
# https://game8.co/games/Pokemon-TCG-Pocket/archives/482685

# Input and output file paths
input_file = "data/raw/medium.html"
output_file = "data/processed/medium.csv"


def clean_str(string: str, empty_val : str = "N/A") -> str:
    """
    Remove extra whitespace from a string.

    Strips leading and trailing whitespace and collapses
    multiple spaces, tabs, or newlines into a single space.
    
    If final output is empty, returns empty_val parameter.

    Args:
        string (str): Raw string to be cleaned.
        empty_vap (str): The value to replace empty strings
            (optional defaults to `''`)

    Returns:
        output (str): Cleaned string with normalized spacing.

    Examples:
        >>> clean_str("   Hello   World   ")
        'Hello World'
        >>> clean_str("Line1\\nLine2\\t\\tLine3")
        'Line1 Line2 Line3'
        >>> clean_str("   Multiple    spaces   and\\nnewlines\\t")
        'Multiple spaces and newlines'
        >>> clean_str("\\t \\n   \\t", empty_val="N/A")
        'N/A'
    """
    output = " ".join(string.strip().split())
    if output == "":
        return empty_val
    else:
        return output


def extract_card(card_html: bs4.element.Tag) -> dict[str, str]:
    """
    Extract card data `<tr>` element into a dict.

    This function parses specific columns from the row of HTML table data,
    extracting structured information such as the card number, name, type, HP,
    and image link. Cell indices correspond to known table structure.

    Args:
        card_html (Tag): Tag containing list of `<td>` tags representing one table row.

    Returns:
        output (dict): Dictionary containing structured card data, with whitespace cleaned.
        The columns of the outputted dict are `{number, name, image, rarity, pack_name,
        type, HP, stage, pack_points}`
    """
    cells = card_html.find_all("td")
    # cell_0 is checkmark (ignored)

    # Extract card data from each cell
    number = cells[1].text
    name = cells[2].find("a").text
    image = cells[2].find("img").get("data-src")
    rarity = cells[3].text
    pack = cells[4].text
    type = cells[5].find("img")["alt"].split("-")[-1]
    HP = cells[6].text
    stage = cells[7].text
    pack_points = cells[8].text
    # cell 9 contains retreat cost, effect, and moves data
    # TODO parse and extract cell_9

    # Create dictionary with raw data
    card = {
        "number": number,
        "name": name,
        "image": image,
        "rarity": rarity,
        "pack_name": pack,
        "type": type,
        "HP": HP,
        "stage": stage,
        "pack_points": pack_points
    }

    # Normalize spacing in all fields and replace empty string with empty
    card = {k: clean_str(v) for k, v in card.items()}

    return card


def write_to_csv(cards_data: list[dict[str, str]]):
    """
    Writes a list of dictionaries containing card data to a CSV file.

    Creates a CSV file at the output path, writes headers based on dictionary keys,
    and writes elements of `cards_data` as rows.

    Args:
        cards_data (list): A list full of dictionaries containing cleaned card attributes.
    """
    # Use the first entry to get the column names
    column_names = cards_data[0].keys()

    # Iterate through list and write each dict as a new row
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=column_names)
        writer.writeheader()
        for card in cards_data:
            writer.writerow(card)


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
        soup = bs4.BeautifulSoup(file, "lxml")

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
    write_to_csv(cards_data)

    print(f"CSV file '{output_file}' created successfully!")


if __name__ == "__main__":
    main()
