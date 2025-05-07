import csv
import bs4

# Input and output file paths
input_file = "data/raw/single.html"
output_file = "data/processed/single.csv"


def clean_str(string: str) -> str:
    """
    Remove extra whitespace from a string.

    Strips leading and trailing whitespace and collapses
    multiple spaces, tabs, or newlines into a single space.

    Args:
        string (str): Raw string to be cleaned.

    Returns:
        output (str): Cleaned string with normalized spacing.

    Examples:
        >>> clean_str("   Hello   World   ")
        'Hello World'
        >>> clean_str("Line1\\nLine2\\t\\tLine3")
        'Line1 Line2 Line3'
        >>> clean_str("   Multiple    spaces   and\\nnewlines\\t")
        'Multiple spaces and newlines'
    """
    return " ".join(string.strip().split())


def extract_card(cells: list[bs4.element.Tag]) -> dict[str, str]:
    """
    Extract card data from a list of `<td>` elements in a table row.

    This function parses specific columns from the row of HTML table data,
    extracting structured information such as the card number, name, type, HP,
    and image link. Cell indices correspond to known table structure.

    Args:
        cells (list): List of `<td>` tags representing one table row.

    Returns:
        outpit (dict): Dictionary containing structured card data, with whitespace cleaned.
        The columns of the outputted dict are `{number, name, image, rarity, pack_name,
        type, HP, stage, pack_points, how_to_get}`
    """
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
    how_to_get = cells[10].text

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
        "pack_points": pack_points,
        "how_to_get": how_to_get,
    }

    # Normalize spacing in all fields
    card = {k: clean_str(v) for k, v in card.items()}

    return card


def write_to_csv(card: dict[str, str]):
    """
    Write a dictionary of card data to a CSV file.

    Creates a CSV file at the output path, writes headers based on dictionary keys,
    and inserts one row of card data.

    Args:
        card (dict): A dictionary containing cleaned card attributes.
    """
    fieldnames = card.keys()
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
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
     # Load and parse the raw HTML file
    with open(input_file, "r", encoding="utf-8") as file:
        soup = bs4.BeautifulSoup(file, "lxml")

    # Extract the first table row
    table = soup.find("tr")
    cells = table.find_all("td")

    # Parse the table row into a structured dictionary
    card = extract_card(cells)

    # Export the parsed data to CSV
    write_to_csv(card)

    print(f"CSV file '{output_file}' created successfully!")


if __name__ == "__main__":
    main()
