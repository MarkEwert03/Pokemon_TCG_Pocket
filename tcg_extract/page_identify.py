from bs4 import BeautifulSoup
import json
import os
import re
import requests
import random

GAMECO_PREFIX = "https://game8.co/games/Pokemon-TCG-Pocket/archives/"

STARTING_URLS = {
    "A1": {"url_ext": 476002, "num_cards_in_pack": 286},  # Bulbasaur
    "A1a": {"url_ext": 491414, "num_cards_in_pack": 86},  # Exeggcute
    "A2": {"url_ext": 496840, "num_cards_in_pack": 207},  # Oddish
    "A2a": {"url_ext": 502148, "num_cards_in_pack": 96},  # Heracross
    "A2b": {"url_ext": 507212, "num_cards_in_pack": 111},  # Weedle
    "A3": {"url_ext": 518856, "num_cards_in_pack": 239},  # Exeggcute
    "A3a": {"url_ext": 524061, "num_cards_in_pack": 103},  # Petilil
    "A3b": {"url_ext": 531867, "num_cards_in_pack": 107},  # Tropius
    "A4": {"url_ext": 539913, "num_cards_in_pack": 241},  # Oddish
    "A4a": {"url_ext": 546447, "num_cards_in_pack": 105},  # Hoppip
    "P-A": {"url_ext": 476288, "num_cards_in_pack": 108},  # Potion
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
            print(f"Error fetching URL: {e}")
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

    title_pattern = r"^.* Card - .* \| .*$"
    card_id_pattern = r"A\d[a,b]? \d\d\d"
    if re.match(title_pattern, title):
        html_first_line = response.text.partition("\n")[0]
        id_match = re.search(card_id_pattern, html_first_line)
        if id_match:
            card_id = id_match.group()
            url_ext = int(url.split("/")[-1])
            return {card_id: url_ext}
        else:
            print(f"Could not find card id: {url}")
            return {}
    else:
        print(f"Not a card page: {url}")
        return {}


def handle_ext(ext: int, page_mappings : dict):
    """
    Determines how to hendle the 6 digit url extention.
    
    - If `ext` already exists in `page_mappings`, the lookup is skipped.
    - If `ext` is in `"BAD_EXTS`, the lookup is also skipped
    - Otherwise we attempt to go to the `game8.co/.../ext` page
      - If something goes wrong, `ext` is added to `BAD_EXTS`
      - Otherwise we add `{"<CARD_ID>": ext}` to page mappings
    
    Parameters
    ----------
    ext : int
        The 6 digit extention at the end of a `https://game8.co/games/Pokemon-TCG-Pocket/archives/` url
    page_mappings : dict
        The dictionary housing the `"<CARD ID>": "<URL_EXT>"` pairs and the `"BAD_EXTS"` list
    """
    if ext in page_mappings.values():
        print(f"{ext} already in page_exts.json.")
        return

    if ext in page_mappings["BAD_EXTS"]:
        print(f"{ext} is a bad ext.")
    else:
        full_url = GAMECO_PREFIX + str(ext)
        current_page_mapping = extract_single_card_page(full_url)
        # If page_data is empty, then we had an error with the page,
        #   so add ext to the list of bad exts
        if not current_page_mapping:
            page_mappings["BAD_EXTS"] += [ext]
            return
        # Append new page data to page_exts
        page_mappings |= current_page_mapping
        print(f"{current_page_mapping} added!")


def update_page_info():
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
        if not "BAD_EXTS" in page_mappings:
            page_mappings["BAD_EXTS"] = []

        # TODO Incorperate STARTING_URLS into range
        for ext in range(476000, 476005):
            handle_ext(ext, page_mappings)

    # Helper sort function for the dict
    def sort_key(item):
        key = item[0]
        if key == "BAD_EXTS":
            # Assign highest possible value to put 'BAD_EXTS' at the end
            return (chr(255), float("inf"))
        code, number = key.split()
        return (code, int(number))

    # Write the updated data back to the file
    page_mappings["BAD_EXTS"] = sorted(page_mappings["BAD_EXTS"])
    sorted_page_exts = dict(sorted(page_mappings.items(), key=sort_key))
    with open(json_path, "w") as f:
        json.dump(sorted_page_exts, f, indent=4)


if __name__ == "__main__":
    update_page_info()
