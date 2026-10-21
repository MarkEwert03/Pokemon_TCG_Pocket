from bs4 import BeautifulSoup
import argparse
import json
import matplotlib.pyplot as plt
import os
import pandas as pd
import re
import requests


GAMECO_PREFIX = "https://game8.co/games/Pokemon-TCG-Pocket/archives/"
START_EXT = 500000
END_EXT = 1 + 505000

# 1689 cards total
# As of 2025-09-01
STARTING_URLS = {
    "A1": {"url_ext": 476002, "num_cards": 286},  # Bulbasaur (001)
    "A1a": {"url_ext": 491414, "num_cards": 86},  # Exeggcute (001)
    "A2": {"url_ext": 496840, "num_cards": 207},  # Oddish (001)
    "A2a": {"url_ext": 502148, "num_cards": 96},  # Heracross (001)
    "A2b": {"url_ext": 507212, "num_cards": 111},  # Weedle (001)
    "A3": {"url_ext": 518856, "num_cards": 239},  # Exeggcute (001)
    "A3a": {"url_ext": 524061, "num_cards": 103},  # Petilil (001)
    "A3b": {"url_ext": 531867, "num_cards": 107},  # Tropius (001)
    "A4": {"url_ext": 539913, "num_cards": 241},  # Oddish (001)
    "A4a": {"url_ext": 546447, "num_cards": 105},  # Hoppip (001)
    "P-A": {"url_ext": 476288, "num_cards": 108},  # Potion (001)
}

MISSING_PATCHES = {
    "A1a": {"url_ext": 491502, "num_cards": 3},  # Pokemon Flute (064)
    "A2": {"url_ext": 496678, "num_cards": 201},  # Tangela (004)
    "A2a": {"url_ext": 502147, "num_cards": 94},  # Burmy (002)
    "A2b": {"url_ext": 507211, "num_cards": 109},  # Kakuna (002)
    "A3": {"url_ext": 518817, "num_cards": 67},  # Big Malasada (142)
    "A3a": {"url_ext": 523189, "num_cards": 77},  # Buzzwole (006)
    "A3b": {"url_ext": 530267, "num_cards": 79},  # Leafeon (002)
    "A4": {"url_ext": 538910, "num_cards": 226},  # Chickorita (008)
    "A4_2": {"url_ext": 540160, "num_cards": 30},  # Squirt Bottle (152)
    "A4a": {"url_ext": 545809, "num_cards": 68},  # Slugma (008)
    "P-A": {"url_ext": 494595, "num_cards": 100},  # Pokedex (008)
    "P-A_2": {"url_ext": 486640, "num_cards": 200},  # Venusaur (018)
}


def extract_single_card_page(url: str, page_html: str = None) -> dict[str, int]:
    """
    Extracts the metadata for the `game8` page.

    Parameters
    ----------
    url : str
        The url for the page on `game8.co` to use if `page_html` is not provided
    page_html : str
        [optional] The raw HTML of the page to use instead of making a request.

    Returns
    -------
    page_data : dict[str, int]
        A single dicttionary `{<CARD_ID>: <URL_ID>}`
        If an error occurs, or the page is not for a card, then `{}` is returned.

    Examples
    --------
    >>> extract_single_card_page("https://game8.co/games/Pokemon-TCG-Pocket/archives/476002")
    {"A1 001": "476002"}
    """
    if page_html is None:
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            page_html = response.text
        except requests.RequestException as e:
            print(f"Error 404: {url}")
            return {}

    try:
        soup = BeautifulSoup(page_html, "lxml")
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        else:
            print(f"No title found in HTML: {url}")
            return {}
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return {}

    card_id_pattern = r"\b((A|B)\d(a|b)?|P-A) \d{3}\b"
    html_first_line = response.text.partition("\n")[0]
    id_match = re.search(card_id_pattern, html_first_line)
    if id_match:
        card_id = id_match.group()
        url_ext = int(url.split("/")[-1])
        return {card_id: url_ext}
    else:
        # remove both '|' symbols
        cleaned_title = title.split("|")[0].split("\uff5c")[0].strip()
        return {cleaned_title: -1}


def handle_ext(ext: int, page_mappings: dict):
    """
    Determines how to hendle the 6 digit url extention.

    - If `ext` already exists in `GOOD_EXTS`, the lookup is skipped.
    - If `ext` is in `"BAD_EXTS`, the lookup is also skipped
    - Otherwise we attempt to go to the `game8.co/.../ext` page
      - If something goes wrong, `ext` is added to `BAD_EXTS`
      - Otherwise we add `{"<CARD_ID>": ext}` to `GOOD_EXTS`

    Parameters
    ----------
    ext : int
        The 6 digit extention at the end of a `https://game8.co/games/Pokemon-TCG-Pocket/archives/` url
    page_mappings : dict
        The dictionary housing the `"<CARD ID>": "<URL_EXT>"` pairs in `"GOOD_EXTS"` and the `"BAD_EXTS"` list
    """
    # we've already added this card page to the dict
    if ext in page_mappings["GOOD_EXTS"].values():
        pack_code = list(page_mappings["GOOD_EXTS"].keys())[
            list(page_mappings["GOOD_EXTS"].values()).index(ext)
        ]
        print(f"{ext} is a good ext. ({pack_code})")
        return

    # page was not a card page (it didn't have an card in title ID)
    if str(ext) in page_mappings["WRONG_EXTS"]:
        page_title = page_mappings["WRONG_EXTS"][str(ext)]
        print(f"{ext} is not a card page. ({page_title})")
        return

    # page caused an error
    if ext in page_mappings["BAD_EXTS"]:
        # print(f"{ext} is a bad ext.")
        return

    full_url = GAMECO_PREFIX + str(ext)
    current_page_mapping = extract_single_card_page(full_url)
    # If page_data is empty, then we had an error with the page,
    #   so add ext to the list of bad exts
    if not current_page_mapping:
        page_mappings["BAD_EXTS"] += [ext]
        return

    # Append incorrect page ext and title to "WRONG_EXTS"
    if list(current_page_mapping.values())[0] == -1:
        # wrong_page_mapping = {dddddd : page_title}
        wrong_page_mapping = {ext: list(current_page_mapping.keys())[0]}
        print(f"Encountered non-card page:\n  {wrong_page_mapping}")
        page_mappings["WRONG_EXTS"] |= wrong_page_mapping
        return

    # Append new page data to "GOOD_EXTS"
    page_mappings["GOOD_EXTS"] |= current_page_mapping
    print(f"{current_page_mapping} added!")
    return


def update_page_mappings():
    """
    Updates `/data/page_exts.json` with new page data.

    `/data/page_exts.json` looks like:
    ```
        {
            "<CARD_ID>": URL_EXT,
            ...
            "<CARD_ID>": URL_EXT,
            "BAD_URLS" : [ext_1, ... ext_n]
        }
    ```

    Example:
    ```
        {
            "A1 001": "476002",
            "A1 002": "476003",
            "BAD_URLS" : [476000, 476001]
        }
    ```
    """
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "page_mappings.json")

    page_mappings = {}
    # Read existing JSON data
    with open(json_path, "r") as f:
        page_mappings = json.load(f)
        if not "GOOD_EXTS" in page_mappings:
            page_mappings["GOOD_EXTS"] = {}
        if not "WRONG_EXTS" in page_mappings:
            page_mappings["WRONG_EXTS"] = {}
        if not "BAD_EXTS" in page_mappings:
            page_mappings["BAD_EXTS"] = []

        # Catch most of them by starting at card 001 and counting up through num_cards
        # for value in STARTING_URLS.values():
        #     range_start = value["url_ext"]
        #     range_end = value["url_ext"] + value["num_cards"]
        #     for ext in range(range_start, range_end + 1):
        #         handle_ext(ext, page_mappings)

        # # Second pass through different missing matches in range [x0-n, x0+n]
        # for value in MISSING_PATCHES.values():
        #     range_start = value["url_ext"] - value["num_cards"]
        #     range_end = value["url_ext"] + value["num_cards"]
        #     for ext in range(range_start - 1, range_end + 1):
        #         handle_ext(ext, page_mappings)

        for ext in range(START_EXT, END_EXT):
            handle_ext(ext, page_mappings)

            # save every 1000 times
            if ext % 1000 == 0:
                save_page_mappings(page_mappings, filename="page_mappings_temp.json")

        # Remove temp file
        temp_path = json_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "page_mappings_temp.json"
        )
        try:
            os.remove(temp_path)
        except FileNotFoundError:
            pass
        
        # Final save
        save_page_mappings(page_mappings)


def save_page_mappings(page_mappings, filename: str = "page_mappings.json"):
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", filename)

    # Helper sort function for the dict
    def sort_key(item):
        key = item[0]
        if key == "BAD_EXTS":
            # Assign highest possible value to put 'BAD_EXTS' at the end
            return (chr(255), float("inf"))
        code, number = key.split()
        return (code, int(number))

    # Sort and write the updated data back to the file
    page_mappings["BAD_EXTS"] = sorted(page_mappings["BAD_EXTS"])
    page_mappings["WRONG_EXTS"] = dict(
        sorted(page_mappings["WRONG_EXTS"].items(), key=lambda kv: int(kv[0]))
    )
    good_exts = dict(sorted(page_mappings["GOOD_EXTS"].items(), key=sort_key))
    page_mappings["GOOD_EXTS"] = good_exts
    with open(json_path, "w") as f:
        json.dump(page_mappings, f, indent=4)


def find_missing_cards():
    """
    Uses `STARTING_URLS` to determine cards still missing from `page_mappings.json`
    """
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "page_mappings.json")
    with open(json_path, "r") as f:
        page_mappings = json.load(f)
        card_codes = page_mappings["GOOD_EXTS"].keys()

        # Parse IDs into a dict: {pack: set(card_numbers)}
        pack_cards = {}
        for id_str in card_codes:
            card_id_pattern = r"^(A\d[a-b]?|P-A) (\d{3})$"
            match = re.match(card_id_pattern, id_str)
            if match:
                pack = match.group(1)
                card_num = int(match.group(2))
                pack_cards.setdefault(pack, set()).add(card_num)

        # Find missing cards for each pack
        missing_cards = {}
        for pack, info in STARTING_URLS.items():
            expected = set(range(1, info["num_cards"] + 1))
            actual = pack_cards.get(pack, set())
            missing = sorted(expected - actual)
            if missing:
                missing_cards[pack] = missing

        missing_cards = dict(sorted(missing_cards.items()))
        for pack, missing in missing_cards.items():
            if not "missing" in pack.split("_"):
                print(f"{pack} missing cards: {', '.join(f'{num:03d}' for num in missing)}")


def visualize_page_mappings():
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "page_mappings.json")
    with open(json_path) as f:
        page_mappings = json.load(f)

        rows = []

        # GOOD_EXTS: ID : ext
        for id_, ext in page_mappings.get("GOOD_EXTS", {}).items():
            rows.append({"ext": int(ext), "category": "GOOD_EXTS", "id": id_, "title": None})

        # WRONG_EXTS: ext : title
        for ext, title in page_mappings.get("WRONG_EXTS", {}).items():
            rows.append({"ext": int(ext), "category": "WRONG_EXTS", "id": None, "title": title})

        # BAD_EXTS: list of ints
        for ext in page_mappings.get("BAD_EXTS", []):
            rows.append({"ext": int(ext), "category": "BAD_EXTS", "id": None, "title": None})

        df = pd.DataFrame(rows)

        # scatterplot
        plt.figure(figsize=(10, 5))
        plt.scatter(df["ext"], df["category"], alpha=0.5, s=10)
        plt.xlabel("ext")
        plt.ylabel("category")
        plt.title("Distribution of GOOD / WRONG / BAD exts")
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update or find missing card page mappings.")
    parser.add_argument("--find", action="store_true", help="Find missing cards in page mappings.")
    parser.add_argument("--update", action="store_true", help="Update page mappings JSON file.")
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Create a plot showing distribution of cards found so far in page_mappings.json.",
    )

    args = parser.parse_args()

    if args.update:
        update_page_mappings()
    if args.find:
        find_missing_cards()
    if args.visualize:
        visualize_page_mappings()
    if not (args.update or args.find or args.visualize):
        parser.print_help()
