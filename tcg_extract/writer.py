import csv


def write_to_csv(cards_data: list[dict[str, str]], output_file: str):
    """
    Writes a list of dictionaries containing card data to a CSV file.

    Creates a CSV file at the output path, writes headers based on dictionary keys,
    and writes elements of `cards_data` as rows.

    Args:
        cards_data (list): A list full of dictionaries containing cleaned card attributes.
        output_file (str): The path to save the created csv to.
    """
    # Use the first entry to get the column names
    column_names = cards_data[0].keys()

    # Iterate through list and write each dict as a new row
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=column_names)
        writer.writeheader()
        for card in cards_data:
            writer.writerow(card)
