import bs4
from bs4 import BeautifulSoup
import re
import requests
from tcg.utils import (
    clean_str,
    parse_energy_cost,
    parse_retreat_cost,
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

        - `stage`
        - `retreat_cost` (numeric cost gotten from `parse_retreat_cost`)
        - `ultra_beast` (string truth value gotten from move info divs)
        - `ability_name`, `ability_effect`
        - `move1_name`, `move1_cost`, `move1_damage`, `move1_effect`
        - `move2_name`, `move2_cost`, `move2_damage`, `move2_effect`
    """
    # Create dict with desired keys and default values
    cell9_data = {
        "stage": DEFAULT_EMPTY,
        "retreat_cost": DEFAULT_EMPTY,
        "ultra_beast": "No",
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
        # Immediately check for Ultra beats to stop future div out of range
        if clean_str(div.text) == "Ultra Beast":
            cell9_data["ultra_beast"] = "Yes"
            continue

        j = move_start_index + i  # will be 1 or 2 depending on ability
        next_div = move_divs[i + 1] if i + 1 < len(move_divs) else None
        name, cost, dmg, effect = extract_move_info(div, next_div)

        cell9_data[f"move{j}_name"] = name
        cell9_data[f"move{j}_cost"] = cost
        cell9_data[f"move{j}_damage"] = dmg
        cell9_data[f"move{j}_effect"] = effect

    return cell9_data


def extract_general_info(table_general: bs4.Tag) -> dict[str, str | None]:
    """
    Extracts general information about a Pokémon TCG card from a given HTML table.

    Parameters
    ----------
        table_general: bs4.Tag
            A BeautifulSoup object representing the general info table of a card.

    Returns
    -------
        result : dict
            A dictionary containing the following extracted card information:
                - id
                - name
                - image (url to the card image)
                - pack name
                - generation
                - illustrator
                - stage, type
                - weakness
                - HP
                - retreat cost
                - rarity.
    """
    result = {}

    # 1. ID, Name, and Image link
    card_img = table_general.select_one("div.imageLink img")
    # id_name looks like ["A1", "001", "Bulbasaur"]
    id_name = card_img.get("alt").split(" ")
    result["id"] = " ".join(id_name[:2])
    result["name"] = " ".join(id_name[2:])
    result["image"] = card_img.get("data-src") or card_img.get("src")

    rows = table_general.find_all("tr")

    # Helper to get the text of the row following a header row containing given label
    def _get_value_after_header(label: str):
        for i, r in enumerate(rows):
            if r.find("th") and label in r.get_text(strip=True):
                if i + 1 < len(rows):
                    return rows[i + 1]
        raise Exception("No row found ")

    # 2. Pack name
    pack_row = _get_value_after_header("Pack")
    # Join text, handle <br>, condense spaces
    pack_text = pack_row.get_text(separator=" ", strip=True)
    pack_text = re.sub(r"\s+", " ", pack_text).split("・")
    result["pack_name"] = " & ".join(pack_text[1:])

    # 3. Generation
    gen_row = _get_value_after_header("Generation")
    gen_text = gen_row.get_text(" ", strip=True)
    # Remove 'Gen ' prefix, keep numeric part
    m = re.search(r"\d+", gen_text)
    if m:
        result["generation"] = m.group()

    # 4. Illustrator
    ill_row = _get_value_after_header("Illustrator")
    ill_text = ill_row.get_text(" ", strip=True)
    result["illustrator"] = ill_text

    # Helper to take a TD with possible <img alt> and return alt or text
    def _icon_link_to_text(td: bs4.element.Tag) -> str | None:
        img = td.find("img")
        if img and img.get("alt"):
            return img.get("alt").strip()
        text = td.get_text(strip=True)
        return text or None

    # 5. Stage | Type | Weakness
    stage_th = table_general.find("th", string=lambda s: s and "Stage" in s)
    row_below = stage_th.find_parent("tr").find_next_sibling("tr")
    tds = row_below.find_all("td")
    # Extract from 3 cells in the row
    result["stage"] = tds[0].get_text(strip=True)
    result["type"] = parse_energy_cost(_icon_link_to_text(tds[1]))
    result["weakness"] = parse_energy_cost(_icon_link_to_text(tds[2]))

    # 6. HP / Retreat Cost / Rarity
    hp_th = table_general.find("th", string=lambda s: s and "HP" in s)
    row_below = hp_th.find_parent("tr").find_next_sibling("tr")
    tds = row_below.find_all("td")
    # Extract from 3 cells in the row
    result["HP"] = tds[0].getText(strip=True)
    retreat_cost_url = tds[1].select_one("a.a-link img").get("data-src")
    result["retreat_cost"] = str(parse_retreat_cost(retreat_cost_url))
    result["rarity"] = _icon_link_to_text(tds[2])

    return result


def extract_moves_and_abilities(table_moves_abilities: bs4.Tag) -> dict[str, str | None]:
    """
    Extracts moves and abilities information about a Pokémon TCG card from a given HTML table.

    Parameters
    ----------
        table_general: bs4.Tag
            A BeautifulSoup object representing the ability and move info table of a card.

    Returns
    -------
        result : dict
            A dictionary containing the following extracted card information:
                - ability_name
                - ability_effect
                - move1_name
                - move1_cost
                - move1_damage
                - move1_effect
                - move2_name
                - move2_cost
                - move2_damage
                - move2_effect
    """
    # First row: move name and cost (icons)
    th = table_moves_abilities.find("th")
    # Move name: after all icons, as text
    move_name = th.get_text(separator=" ", strip=True)
    # Move cost: get all icon alt texts
    cost_alts = [parse_energy_cost(img.get("alt")) for img in th.find_all("img")]
    move_cost = " ".join(cost_alts)
    # Remove cost words from move_name
    for alt in cost_alts:
        move_name = move_name.replace(alt, "")
    move_name = move_name.strip()

    # Second row: damage and effect (if any)
    td = table_moves_abilities.find("td")
    damage = None
    effect = None
    if td:
        # Try to find "Damage: NNN"
        import re

        m = re.search(r"Damage\s*:\s*([0-9X]+)", td.get_text())
        damage = m.group(1) if m else None
        # Effect: text after damage, if any
        txt = td.get_text().split("Damage", 1)
        if len(txt) > 1:
            after_damage = txt[1]
            # Remove ": <digits>" part
            after_damage = re.sub(r":\s*[0-9X]+", "", after_damage, 1)
            effect = after_damage.strip() or None

    return {
        f"move{1}_name": move_name,
        f"move{1}_cost": move_cost,
        f"move{1}_damage": damage,
        f"move{1}_effect": effect,
    }


def fix_edge_cases(card: dict[str, str | None]):
    """
    Applies manual overrides to correct known card-specific data issues.

    This function mutates the `card` dictionary in-place to fix edge cases
    where data is missing or incorrect on the original source page. These include:
    - Missing move costs
    - Incorrect damage values
    - Missing illustrator, generation, or weakness fields

    Parameters
    ----------
    card : dict[str, str | None]
        A single card dictionary as returned by `extract_card()`

    Notes
    -----
    - Fixes are hardcoded using pattern matching on `card["id"]`.
    - Uses lookup dictionaries for illustrator, generation, and weakness patches.
    - This function modifies `card` in-place and does not return anything.
    """
    FIXED_ILLUSTRATORS = {
        "P-A 053": "Shin Nagasawa",  # Floatzel
        "P-A 056": "Krgc",  # Ekans
        # "A2b 002": "",  # Kakuna
        # "A2b 005": "",  # Sprigatito
        # "A2b 006": "",  # Floragato
        # "A2b 007": "",  # Meowscarada
        # "A2b 008": "",  # Charmander
        # "A2b 014": "",  # Tentacool
        # "A2b 018": "",  # Wiglett
        # "A2b 020": "",  # Dondozo
        # "A2b 021": "",  # Tatsugiri
        # "A2b 023": "",  # Voltorb
        # "A2b 025": "",  # Pachirisu
        # "A2b 040": "",  # Hitmonlee
        # "A2b 041": "",  # Hitmonchan
        # "A2b 047": "",  # Paldean Wooper
        # "A2b 049": "",  # Spiritomb
        # "A2b 068": "",  # Cyclizar
        # "A2b 070": "",  # Pokemon Center Lady
        # "A2b 071": "",  # Red
        # "A2b 073": "",  # Meowscarada
        # "A2b 074": "",  # Buizel
        # "A2b 075": "",  # Tatsugiri
        # "A2b 076": "",  # Grafaiai
        # "A2b 089": "",  # Pokemon Center Lady
        # "A2b 090": "",  # Red
        # "A2b 095": "",  # Bibarel ex
        # "A2b 096": "",  # Giratina ex
        # "A2b 103": "",  # Pachirisu
        # "A3 009": "",  # Rowlet
        # "A3 045": "",  # Popplio
        # "A3 073": "",  # Lunatone
        # "A3 079": "",  # Ribombee
        # "A3 093": "",  # Drilbur
        # "A3 103": "",  # Mudsdale
        # "A3 130": "",  # Delcatty
        # "A3 135": "",  # Toucannon
        # "A3 148": "",  # Acerola
        # "A3 155": "",  # Lillie
        # "A3 157": "",  # Morelull
        # "A3 158": "",  # Tsareena
        # "A3 162": "",  # Alolan Vulpix
        # "A3 165": "",  # Oricorio
        # "A3 167": "",  # Cutiefly
        # "A3 168": "",  # Comfey
        # "A3 171": "",  # Cosmog
        # "A3 172": "",  # Rockruff
        # "A3 174": "",  # Minior
        # "A3 178": "",  # Bewear
        # "A3 179": "",  # Komala
        # "A3 190": "",  # Acerola
        # "A3 197": "",  # Lillie
        # "A3 203": "",  # Alolan Raichu ex
        # "A3 228": "",  # Jigglypuff
        # "A3 229": "",  # Wigglytuff
        # "P-A 046": "",  # Gible
        # "P-A 047": "",  # Staraptor
        # "P-A 049": "",  # Snorlax
        # "P-A 052": "",  # Sprigatito
        # "P-A 060": "",  # Exeggcute
        # "P-A 070": "",  # Alolan Ninetales
    }

    FIXED_GENERATIONS = {
        "A1a 065": "9",  # Mythical Slab
        "A1a 066": "9",  # Budding Expeditioner
        "A1a 080": "9",  # Budding Expeditioner
        "P-A 053": "4",  # Floatzel
        "P-A 056": "1",  # Ekans
    }

    # M = Missing Page, I = Incorrect
    FIXED_WEAKNESSES = {
        "A1 169": "Fighting",  # Nidoran M (I)
        "A1 170": "Fighting",  # Nidorino (I)
        "A1 171": "Fighting",  # Nidoking (I)
        "A1 241": "Fighting",  # Nidoking (I)
        "A1a 048": "Grass",  # Stonjourner (I)
        "P-A 028": "Water",  # Volcarona (I)
        "P-A 037": "Darkness",  # Cresselia ex (I)
        "P-A 038": "Darkness",  # Misdreavus (I)
        "P-A 053": "Lightning",  # Floatzel (M)
        "P-A 056": "Fighting",  # Ekans (M)
    }

    # Specific fixes for fields in main table
    match card["id"]:
        case "A1 183":  # Dratini
            # Dratini's Ram should do 40 dmg not 70
            card["move1_damage"] = "40"

        case "A1a 057":  # Pidgey
            # Missing energy cost for Flap
            card["move1_cost"] = "*️⃣"

        case "A2 047":  # Wash Rotom
            # Wash Rotom's Wave Splash should do 30 dmg not 39
            card["move1_damage"] = "30"

    # General lookups for missing values on extra details page
    for field, lookup in [
        ("illustrator", FIXED_ILLUSTRATORS),
        ("generation", FIXED_GENERATIONS),
        ("weakness", FIXED_WEAKNESSES),
    ]:
        val = lookup.get(card["id"])
        if val:
            card[field] = val

    # Mutates card in-place, so no need to return


def extract_card(card_page_url: str) -> dict[str, str | None]:
    """
    Extract the page info for a card.

    Parameters
    ----------
    card_page_url : str
        The url to the detailed card page.

    Returns
    -------
    out : dict[str, str]
        A dictionary containing all relevent information for the card. Has the following attributes:
        - `id`, `name`, `pack_name`
        - `rarity`, `type`, `HP`, `stage`
        - `pack_points`, `retreat_cost`, `ultra_beast`
        - `ability_name`, `ability_effect`
        - `move1_name`, `move1_cost`, `move1_damage`, `move1_effect`
        - `move2_name`, `move2_cost`, `move2_damage`, `move2_effect`
        - `generation`, `illustrator`, `weakness`
        - `url`, `image`

    Notes
    -----
    - Cleans whitespace via `clean_str()` at the end.
    """
    # Download the page from the given link
    card_page_response = requests.get(card_page_url)
    card_page_response.raise_for_status()

    # Dictionary to store data
    card = {}

    # Parse total HTML with BeautifulSoup
    soup = BeautifulSoup(card_page_response.text, "lxml")
    card_url = card_page_response.url
    card["url"] = card_url

    # Extract general innformation from table 1
    table_general = soup.select("table.a-table")[1]
    card = card | extract_general_info(table_general)

    # Extract general innformation from table 3
    table_moves_abilities = soup.select("table.a-table")[3]
    # print(table_moves_abilities)
    # quit()
    card = card | extract_moves_and_abilities(table_moves_abilities)

    # Normalize spacing in all fields and replace empty string with empty
    card = {k: clean_str(v) for k, v in card.items()}

    # Fix final misc things that are card specific
    # fix_edge_cases(card)

    return card
