import bs4


def clean_str(string: str, empty_val: str = "N/A") -> str:
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


def extract_cell9(cell9: bs4.element.Tag) -> list[str]:
    """Extracts data from cell 9"""
    # Create dict with desired keys and default values
    result = {
        "stage": "N/A",
        "retreat_cost": "N/A",
        "move1_name": "N/A",
        "move1_damage": "N/A",
        "move1_effect": "N/A",
        "move2_name": "N/A",
        "move2_damage": "N/A",
        "move2_effect": "N/A"
    }


    # --- Stage ---
    stage_tag = cell9.find("b", string="Stage")
    if stage_tag and stage_tag.next_sibling:
        result["stage"] = clean_str(stage_tag.next_sibling.strip(":"))

    # --- Retreat Cost ---
    retreat_tag = cell9.find("b", string="Retreat Cost")
    if retreat_tag:
        # its parent <div> holds the <img> icons
        retreat_div = retreat_tag.find_parent("div")
        retreat_img = retreat_div.find("img").get("data-src")
        result["retreat_cost"] = retreat_img

    # --- Moves (up to 2) ---
    move_divs = cell9.find_all("div", class_="align")[1:]  # skip first (retreat)
    for i, div in enumerate(move_divs, start=1): # 1-based index for the dict
        # move_i name
        name_tag = div.find("b")
        if name_tag:
            result[f"move{i}_name"] = clean_str(name_tag.text)

        # go through siblings for damage then effect
        damage = None
        effect = None
        for sib in div.next_siblings:
            # text nodes or NavigableString
            text = sib.strip() if isinstance(sib, str) else None
            if not text:
                continue
            if damage is None and text.isdigit():
                damage = text
                continue
            # anything non-digit after damage is the effect
            if damage is not None:
                effect = text
                break

        if damage is not None:
            result[f"move{i}_damage"] = damage
        if effect:
            result[f"move{i}_effect"] = effect

    print(result)
    return result


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

    # Normalize spacing in all fields and replace empty string with empty
    card = {k: clean_str(v) for k, v in card.items()}

    return card
