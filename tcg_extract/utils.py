ENERGY_SYMBOLS = {
    "Colorless": "*️⃣",
    "Grass": "🟢",
    "Fire": "🔴",
    "Water": "🔵",
    "Lightning": "🟡",
    "Psychic": "🟣",
    "Fighting": "🟤",
    "Darkness": "⚫",
    "Metal": "⚪",
    "Dragon": "🟠",
}

RETREAT_COSTS = {
    "https://img.game8.co/3998614/b92af68265b2e7623de5efdf8197a9bf.png/show": 0,
    "https://img.game8.co/3994730/6e5546e2fbbc5a029ac79acf2b2b8042.png/show": 1,
    "https://img.game8.co/3998538/eea8469456d6b7ea7a2daf2995087d00.png/show": 2,
    "https://img.game8.co/3998539/6bb558f97aac02e469e3ddc06e2ac167.png/show": 3,
    "https://img.game8.co/3998556/3831ed9a23dbc9db0da4254334165863.png/show": 4,
}


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


def parse_energy_cost(energy_str: str) -> str:
    """
    Convert an energy descriptor like "Fire 2" into repeated symbols.

    Args:
        energy_str (str): a string of the form "<Type> <count>", e.g. "Darkness 2",
                          or just "<Type>" (implying count=1).

    Returns:
        A string consisting of `count` copies of the corresponding symbol
        from ENERGY_SYMBOLS, or "?" if the type isn't in the dict.

    Examples:
        >>> parse_energy_cost("Darkness 2")
        '⚫⚫'
        >>> parse_energy_cost("Fire")
        '🔴'
        >>> parse_energy_cost("Unknown 3")
        '???'
    """
    parts = energy_str.rsplit(" ", 1)
    if len(parts) == 2 and parts[1].isdigit():
        type_name, count = parts[0], int(parts[1])
    else:
        type_name, count = energy_str, 1

    symbol = ENERGY_SYMBOLS.get(type_name, "?")
    return symbol * count

def parse_retreat_cost(retreat_cost_img: str) -> int:
    """
    Maps a retreat cost image URL to its corresponding numeric retreat cost.

    Parameters:
        retreat_cost_img (str):
            The full URL of the retreat cost icon image (e.g., from an <img> tag's "data-src" attribute).

    Returns:
        out (int):
            The numeric retreat cost (0-4) if the URL is recognized,
            or -1 if the image is not found in the known RETREAT_COSTS mapping.

    Examples:
    >>> parse_retreat_cost("https://img.game8.co/3998539/6bb558f97aac02e469e3ddc06e2ac167.png/show")
    3
    >>> parse_retreat_cost("https://img.unknown.com/retreat5.png")
    -1
    """
    return RETREAT_COSTS.get(retreat_cost_img, -1)