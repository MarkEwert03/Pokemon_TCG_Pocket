import csv
from bs4 import BeautifulSoup

input_file = "data/raw/single.html"
output_file = "data/processed/single.csv"


def main():
    """Run the main function."""
    with open(input_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "lxml")

    table = soup.find("tr")
    cells = table.find_all("td")
    # cell_0 is checkmark (unnecessary)

    # cell_1 is card #
    number = cells[1].text

    # cell_2 is card name, image link
    name = cells[2].find("a").text
    image = cells[2].find("img").get("data-src")

    # cell_3 is rarity
    rarity = cells[3].text

    # cell_4 is exclusive pack
    pack = cells[4].text

    # cell_5 is type
    type = cells[5].find("img")["alt"].split("-")[-1]

    # cell_6 is HP
    HP = cells[6].text

    # cell_7 is stage
    stage = cells[7].text

    # cell_8 is pack points
    pack_points = cells[8].text

    # cell_9 is retreat cost, effect, moves
    # TODO parse and extract

    # cell_10 is how to get
    how_to_get = cells[10].text

    # Create dict to store data
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

    fieldnames = card.keys()
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(card)


if __name__ == "__main__":
    main()
