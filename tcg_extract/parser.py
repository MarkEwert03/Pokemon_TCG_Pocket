import bs4
from tcg_extract.utils import clean_str, parse_energy_cost, parse_retreat_cost


def extract_move_info(
    div: bs4.element.Tag, next_align: bs4.element.Tag | None
) -> tuple[str, str, str, str]:
    """
    Extracts move informationfrom a `<div class="align">` element.

    Stops parsing once it reaches `next_align`, or end of siblings.

    Args:
        div (bs4.element.Tag):
            The `div` element containing the move inforation about the card.
        next_align (bs4.element.Tag):
            The next `<div class="align">` element.

    Returns:
        out (Tuple[str, str, str, str]):
            A tuple containing the following move information:
                - move_name
                - move_cost
                - move_damage
                - move_effect

    """
    # --- Name ---
    name = div.find("b").text.strip() if div.find("b") else "N/A"

    # --- Cost ---
    alt_texts = [img.get("alt", "") for img in div.find_all("img")]

    cost = "".join(parse_energy_cost(alt) for alt in alt_texts) or "N/A"

    # --- Damage + Effect ---
    damage = "N/A"
    effect = "N/A"
    found_damage = False

    for sib in div.next_siblings:
        # stop if we hit the next move div
        if sib == next_align:
            break
        # if it's a Tag, skip non-useful ones like <br>
        if isinstance(sib, bs4.element.Tag):
            continue
        # if it's a string
        text = sib.strip()
        if not text:
            continue
        if not found_damage and text.isdigit():
            damage = text
            found_damage = True
        elif found_damage:
            # first non-digit string after damage
            effect = text
            break

    return name, cost, damage, effect


def extract_cell9(cell9: bs4.element.Tag) -> list[str]:
    """
    Extracts key Pokémon TCG card details from a `<td class="left">` element into a flat dictionary.

    Args:
        cell9 (bs4.element.Tag):
            A `<td>` tag containing:
            - A <b>Stage</b> label and value
            - A <b>Retreat Cost</b> label with cost icons
            - Up to two <div class="align"> blocks for attacks, each with:
                • <b>Attack Name</b>
                • Energy cost icons
                • Damage value
                • Optional effect text

    Returns:
        cell9_data (Dict[str, str]):
            A dict with these keys (all default to "N/A" if not found):
            - stage        : Stage description (e.g. "Stage 2")
            - retreat_cost : Comma-separated alt texts of retreat-cost icons
            - move1_name   : First attack's name
            - move1_damage : First attack's damage amount
            - move1_effect : First attack's optional effect text
            - move2_name   : Second attack's name
            - move2_damage : Second attack's damage amount
            - move2_effect : Second attack's optional effect text
    """
    # Create dict with desired keys and default values
    cell9_data = {
        "stage": "N/A",
        "retreat_cost": "N/A",
        "ability_name": "N/A",
        "ability_effect": "N/A",
        "move1_name": "N/A",
        "move1_cost": "N/A",
        "move1_damage": "N/A",
        "move1_effect": "N/A",
        "move2_name": "N/A",
        "move2_cost": "N/A",
        "move2_damage": "N/A",
        "move2_effect": "N/A",
    }

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
        next_div = move_divs[i+1] if i+1 < len(move_divs) else None
        name, cost, dmg, effect = extract_move_info(div, next_div)

        cell9_data[f"move{j}_name"] = name
        cell9_data[f"move{j}_cost"] = cost
        cell9_data[f"move{j}_damage"] = dmg
        cell9_data[f"move{j}_effect"] = effect

    return cell9_data


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
    type = cells[5].find("img")["alt"].split("-")[-1]  # last word is the type
    HP = cells[6].text
    stage = cells[7].text
    pack_points = cells[8].text.replace(",", "")[:-4]  # remove comma and "Pts"
    # cell 9 contains retreat cost, effect, and moves data
    cell9 = extract_cell9(cells[9])

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
    }

    # Merge data from cell 9
    card = card | cell9

    # Normalize spacing in all fields and replace empty string with empty
    card = {k: clean_str(v) for k, v in card.items()}

    return card
