from bs4 import BeautifulSoup
import json
import os
import re
import requests

GAMECO_PREFIX = "https://game8.co/games/Pokemon-TCG-Pocket/archives/"

STARTING_URLS = {
    "A1": {"url_id": 476002, "num_cards_in_pack": 286},  # Bulbasaur
    "A1a": {"url_id": 491414, "num_cards_in_pack": 86},  # Exeggcute
    "A2": {"url_id": 496840, "num_cards_in_pack": 207},  # Oddish
    "A2a": {"url_id": 502148, "num_cards_in_pack": 96},  # Heracross
    "A2b": {"url_id": 507212, "num_cards_in_pack": 111},  # Weedle
    "A3": {"url_id": 518856, "num_cards_in_pack": 239},  # Exeggcute
    "A3a": {"url_id": 524061, "num_cards_in_pack": 103},  # Petilil
    "A3b": {"url_id": 531867, "num_cards_in_pack": 107},  # Tropius
    "A4": {"url_id": 539913, "num_cards_in_pack": 241},  # Oddish
    "A4a": {"url_id": 546447, "num_cards_in_pack": 105},  # Hoppip
    "P-A": {"url_id": 476288, "num_cards_in_pack": 108},  # Potion
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
            print("No title found in HTML.")
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
            url_id = int(url.split("/")[-1])
            return {card_id: url_id}
        else:
            print("Did not find card id!")
            return {}
    else:
        print(f"<{title}> is not a card page")
        return {}


def update_page_info():
    """
    Updates `/data/page_urls.json` with new page data.
    """
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "page_urls.json")

    # Read existing JSON data
    with open(json_path, "r") as f:
        page_urls = json.load(f)

        for ext in range(STARTING_URLS["A1"]["url_id"], STARTING_URLS["A1"]["url_id"]+10):
            if ext in page_urls.values():
                print(f"{ext} already in page_urls.json")
            else:
                full_url = GAMECO_PREFIX + str(ext)
                page_data = extract_single_card_page(full_url)
                page_urls = page_urls | page_data
                print(f"{page_data} added!")

    # Step 3: Write the updated data back to the file
    with open(json_path, "w") as f:
        json.dump(page_urls, f, indent=4)


if __name__ == "__main__":
    update_page_info()
