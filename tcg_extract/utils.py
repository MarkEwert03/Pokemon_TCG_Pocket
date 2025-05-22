import re

DEFAULT_EMPTY = None

COLUMNS = [
    "number",
    "name",
    "rarity",
    "stage",
    "HP",
    "type",
    "weakness",
    "retreat_cost",
    "generation",
    "illustrator",
    "pack_name",
    "pack_points",
    "ability_name",
    "ability_effect",
    "move1_name",
    "move1_cost",
    "move1_damage",
    "move1_effect",
    "move2_name",
    "move2_cost",
    "move2_damage",
    "move2_effect",
    "image",
    "url",
]

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
    "https://img.game8.co/4018721/a654c44596214b3bf38769c180602a16.png/show": 1,
    "https://img.game8.co/3346529/3dd07276f0d15aef9ef1b5f294a8c94a.png/show": 1,  # only for P-A 051
    "https://img.game8.co/3998538/eea8469456d6b7ea7a2daf2995087d00.png/show": 2,
    "https://img.game8.co/3998539/6bb558f97aac02e469e3ddc06e2ac167.png/show": 3,
    "https://img.game8.co/3998556/3831ed9a23dbc9db0da4254334165863.png/show": 4,
}

DEFAULT_EMPTY = None


def clean_str(string: str, empty_val: str = DEFAULT_EMPTY) -> str | None:
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
    if string is None:
        return DEFAULT_EMPTY

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
    match len(parts):
        case 0:
            return ""
        case 1:
            type_name = energy_str
            count = 1
        case 2:
            type_name = parts[0]
            count = int(parts[1]) if parts[1].isdigit() else 1
        case _:
            raise ValueError(
                f"energy_str was <{energy_str}> and should be of the form <ENERGY COUNT>"
            )

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


def trim_after_second_parens(s: str) -> str:
    """
    Trims a string to just before the second opening parenthesis, if one exists.

    This function is useful for removing trailing descriptive or redundant info
    that appears after the second set of parentheses in a string, while preserving
    the core phrase up to and including the first set of parentheses.

    Args:
        s (str): Input string that may contain multiple sets of parentheses.

    Returns:
        str: The trimmed string, or the original string if there are fewer than two
             opening parentheses.

    Examples:
        >>> trim_after_second_parens("Genetic Apex (A1) Mewtwo")
        'Genetic Apex (A1) Mewtwo'
        >>> trim_after_second_parens("Genetic Apex (A1) Any")
        'Genetic Apex (A1) Any'
        >>> trim_after_second_parens("Space-Time Smackdown (A2) Any (Space-Time Smackdown)")
        'Space-Time Smackdown (A2)'
        >>> trim_after_second_parens("Name (Alpha) (Beta) (Gamma)")
        'Name (Alpha)'
        >>> trim_after_second_parens("No parentheses here")
        'No parentheses here'
        >>> trim_after_second_parens("(Only one)")
        '(Only one)'
    """
    # Find all positions of opening parentheses
    matches = list(re.finditer(r"\(", s))
    if len(matches) <= 1:
        return s  # Keep original if only one or none

    # Cut string just before the second opening parenthesis
    return s[: matches[1].start()].strip()
