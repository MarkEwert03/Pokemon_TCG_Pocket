import bs4
from bs4 import BeautifulSoup
import re
import requests
from tcg_extract.utils import (
    clean_str,
    parse_energy_cost,
    parse_retreat_cost,
    trim_after_second_parens,
    DEFAULT_EMPTY,
)


def extract_move_info(
    div: bs4.element.Tag, next_div: bs4.element.Tag | None
) -> tuple[str, str, str, str]:
    """
    Extract a single attack's name, cost, damage and effect.

    Parameters
    ----------
    div : bs4.element.Tag
        A `<div class="align">` that wraps:
        - A `<b>` containing the `attack name`.
        - One or more `<img alt="Type N">` energy-cost icons.
    next_div : bs4.element.Tag or None
        The `next` `<div class="align">` tag (or `None`), used as a boundary
        to stop gathering sibling text.

    Returns
    -------
    tuple[str, str, str, str]
        A 4-tuple:
        - `name` (`str`): The attack's name.
        - `cost_symbols` (`str`): Symbols (e.g. `"⚫⚫"`) from `parse_energy_cost`.
        - `damage` (`str`): Numeric damage.
        - `effect` (`str`): The textual effect
    """

    # Get Name
    name_tag = div.find("b")
    name = name_tag.text.strip() if name_tag else DEFAULT_EMPTY

    cost_alts = [img["alt"] for img in div.find_all("img", alt=True)]
    cost = "".join(parse_energy_cost(alt) for alt in cost_alts) or DEFAULT_EMPTY

    # Gather all text siblings up to next_div
    texts: list[str] = []
    for sib in div.next_siblings:
        if sib is next_div:
            break
        if isinstance(sib, bs4.element.Tag):
            continue
        t = sib.strip()
        if t:
            texts.append(t)

    # Decide damage/effect
    # Only allow digits, "x", and "+" to account for "50x" or "30+"
    is_pokemon_numeric = bool(re.fullmatch(r"[0-9x+]+", texts[0]))
    if texts and is_pokemon_numeric:
        damage = texts[0]
        effect = texts[1] if len(texts) > 1 else DEFAULT_EMPTY
    elif texts:
        damage = DEFAULT_EMPTY
        effect = texts[0]
    else:
        damage = DEFAULT_EMPTY
        effect = DEFAULT_EMPTY

    return name, cost, damage, effect


def extract_cell9(cell9: bs4.element.Tag, is_trainer: bool) -> dict[str, str | None]:
    """
    Parse the details cell (`<td class="left">`) into flat fields.

    Parameters
    ----------
    cell9 : bs4.element.Tag
        The `<td class="left">` containing:
        - A `Stage` label/value
        - A `Retreat Cost` icon
        - Optional `[Ability]` block
        - Up to two `<div class="align">` attack blocks
    is_trainer : bool
        If `True`, this is a Trainer/Item/Tool card (no Stage/moves) so
        its full description goes into `ability_effect`.

    Returns
    -------
    dict[str, str | None]
        Flat mapping with default DEFAULT_EMPTY:

        - `stage`: e.g. `"Stage 2"`
        - `retreat_cost`: numeric cost from `parse_retreat_cost`
        - `ability_name`, `ability_effect`
        - `move1_name`, `move1_cost`, `move1_damage`, `move1_effect`
        - `move2_name`, `move2_cost`, `move2_damage`, `move2_effect`
    """
    # Create dict with desired keys and default values
    cell9_data = {
        "stage": DEFAULT_EMPTY,
        "retreat_cost": DEFAULT_EMPTY,
        "ability_name": DEFAULT_EMPTY,
        "ability_effect": DEFAULT_EMPTY,
        "move1_name": DEFAULT_EMPTY,
        "move1_cost": DEFAULT_EMPTY,
        "move1_damage": DEFAULT_EMPTY,
        "move1_effect": DEFAULT_EMPTY,
        "move2_name": DEFAULT_EMPTY,
        "move2_cost": DEFAULT_EMPTY,
        "move2_damage": DEFAULT_EMPTY,
        "move2_effect": DEFAULT_EMPTY,
    }

    # Handle case for trainer type first
    if is_trainer:
        # Trainer cards only have 1 description
        # Put description in ability_effect
        cell_text = clean_str(cell9.text)
        trainer_desc = cell_text if cell_text[0] != "-" else cell_text[6:]
        cell9_data["ability_effect"] = trainer_desc
        return cell9_data

    # --- Stage ---
    stage_tag = cell9.find("b", string="Stage")
    if stage_tag and stage_tag.next_sibling:
        cell9_data["stage"] = clean_str(stage_tag.next_sibling.strip(":"))

    # --- Retreat Cost ---
    retreat_tag = cell9.find("b", string="Retreat Cost")
    if retreat_tag:
        # its parent <div> holds the <img> icons
        retreat_div = retreat_tag.find_parent("div")
        retreat_img = retreat_div.find("img").get("data-src")
        cell9_data["retreat_cost"] = str(parse_retreat_cost(retreat_img))

    # --- Ability (optional for the card) ---
    ability_span = cell9.find("span", string="[Ability]")
    if ability_span:
        name = None
        effect = None
        sib = ability_span.next_sibling
        while sib and (name is None or effect is None):
            if isinstance(sib, str):
                text = sib.strip()
                if text:
                    if name is None:
                        name = text
                    elif effect is None:
                        effect = text
            sib = sib.next_sibling

        cell9_data["ability_name"] = name or "N/A"
        cell9_data["ability_effect"] = effect or "N/A"

    # --- Moves (up to 2) ---
    move_divs = cell9.find_all("div", class_="align")[1:]  # skip first (retreat)
    move_start_index = 2 if ability_span else 1  # shift moves if ability is present

    for i, div in enumerate(move_divs):
        j = move_start_index + i  # will be 1 or 2 depending on ability
        next_div = move_divs[i + 1] if i + 1 < len(move_divs) else None
        name, cost, dmg, effect = extract_move_info(div, next_div)

        cell9_data[f"move{j}_name"] = name
        cell9_data[f"move{j}_cost"] = cost
        cell9_data[f"move{j}_damage"] = dmg
        cell9_data[f"move{j}_effect"] = effect

    return cell9_data


def extract_extra_card_details(card_full_url: str, is_trainer: bool) -> dict[str, str | None]:
    """
    Parse additional details from the cards full page.

    Parameters
    ----------
    card_full_url : str
        The url linking to the cards full page
    is_trainer : bool
        If `True`, this is a Trainer/Item/Tool card (no Stage/moves) so
        its full description goes into `ability_effect`.

    Returns
    -------
    card_extra_details : dict[str, str | None]
        Flat mapping of the fields with default DEFAULT_EMPTY:
            - `generation`
            - `illustrator`
            - `weakness`
    """
    # Download page
    response = requests.get(card_full_url)
    response.raise_for_status()

    # Parse total HTML with BeautifulSoup
    soup = BeautifulSoup(response.text, "lxml")
    table = soup.select_one("table.a-table.table--fixed.a-table")
    rows = table.find_all("tr")

    # Get metadata with soup operations
    # rating = rows[1].find("td").find("a").find("img").get("data-src")
    generation = rows[5].find("td").text
    illustrator = rows[7].find("td").text
    weakness = (
        DEFAULT_EMPTY if is_trainer else rows[9].find_all("td")[2].find("a").find("img").get("alt")
    )

    # Create dictionary with card info
    card_extra_details = {
        "generation": generation,
        "illustrator": illustrator,
        "weakness": weakness,
    }

    return card_extra_details


def extract_card(card_html: bs4.element.Tag) -> dict[str, str]:
    """
    Convert a `<tr>` row into a full card-info dict.

    Parameters
    ----------
    card_html : bs4.element.Tag
        A `<tr>` containing exactly ten `<td>` cells in the known layout:

            0) checkbox
            1) number
            2) name/image
            3) rarity
            4) pack,
            5) type
            6) HP
            7) stage
            8) points
            9) moves/details.

    Returns
    -------
    dict[str, str]
        Merges:
        - Basic columns: `number`, `name`, `image`, `rarity`,
          `pack_name`, `type`, `HP`, `stage`, `pack_points`, `url`
        - Cell 9 columns: `stage`, `retreat_cost`, `ability_name`, `ability_effect`,
          `move1_name`, `move1_cost`, `move1_damage`, `move1_effect`,
          `move2_name`, `move2_cost`, `move2_damage`, `move2_effect`
        - Extra details columns: `Generation`, `Illustrator`, `Weakness`

    Notes
    -----
    - Determines `is_trainer` by `type` in `{"Item", "Supporter", "Pokemon Tool"}`.
    - Cleans whitespace via `clean_str()` at the end.
    """
    cells = card_html.find_all("td")
    # cell_0 is checkmark (ignored)

    # Extract card data from each cell
    number = cells[1].text
    name = cells[2].find("a").text
    image = cells[2].find("img").get("data-src")
    rarity = cells[3].text
    pack = trim_after_second_parens(cells[4].text)
    type = cells[5].find("img")["alt"].split("-")[-1]  # last word is the type
    HP = cells[6].text
    stage = cells[7].text
    pack_points = cells[8].text.replace(",", "").replace("Pts", "")

    # Flag to determine if card is pokemon or not
    is_trainer = clean_str(type) in ["Item", "Supporter", "Pokemon Tool"]

    # Cell 9 contains retreat cost, effect, and moves data
    cell9 = extract_cell9(cells[9], is_trainer=is_trainer)

    # Extract more information from the individual card pages
    card_full_url = cells[2].find("a").get("href")
    extra_card_details = extract_extra_card_details(card_full_url, is_trainer=is_trainer)

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
        "url": card_full_url,
    }

    # Merge data from cell 9 and full page
    card = card | cell9
    card = card | extra_card_details

    # Normalize spacing in all fields and replace empty string with empty
    card = {k: clean_str(v) for k, v in card.items()}

    # Weird edge case; missing energy cost for A1a 057 (Pidgey)
    if card["number"] == "A1a 057":
        card["move1_cost"] = "*️⃣"

    return card
