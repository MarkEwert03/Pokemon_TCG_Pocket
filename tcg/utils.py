"""Small, dependency-free helpers: string cleaning and energy-type handling."""

import re

# The ten Pokémon TCG Pocket types (anything else on a card is a Trainer subtype)
TYPE_NAMES = [
    "Colorless",
    "Grass",
    "Fire",
    "Water",
    "Lightning",
    "Psychic",
    "Fighting",
    "Darkness",
    "Metal",
    "Dragon",
]

# game8 typos seen in the wild -> real type name
TYPE_ALIASES = {
    "lighting": "Lightning",
    "fightring": "Fighting",
    "fighitng": "Fighting",
}

# Type name -> emoji used in the move*_cost columns
ENERGY_SYMBOLS = {
    "Colorless": "🔘",
    "Grass": "🟢",
    "Fire": "🔴",
    "Water": "🔵",
    "Lightning": "🟡",
    "Psychic": "🟣",
    "Fighting": "🟤",
    "Darkness": "⚫",
    "Metal": "⚪",
    "Dragon": "🟠",
    "Blank": "💭",
}
COLORLESS = ENERGY_SYMBOLS["Colorless"]
EFFECT_FIELDS = ("ability_effect", "move1_effect", "move2_effect")


def clean_str(value: str | None) -> str | None:
    """
    Collapse all whitespace to single spaces and strip the ends.
    Returns `None` for `None` or whitespace-only input.

    >>> clean_str("   Hello   World   ")
    'Hello World'
    >>> clean_str("\\t \\n ") is None
    True
    """
    if value is None:
        return None
    out = " ".join(str(value).split())
    return out or None


def normalize_effect_text(value: str | None) -> str | None:
    """Normalize effect text for consistent comparisons and output."""
    value = clean_str(value)
    if value is None:
        return None
    value = value.replace("’", "'").replace("‘", "'").replace("Pokémon", "Pokemon")
    value = clean_str(value)
    if value and value[-1] not in ".!?":
        value += "."
    return value


def normalize_effect_fields(card: dict[str, str | None]) -> None:
    """Normalize all effect-text fields on a card in place."""
    for field in EFFECT_FIELDS:
        card[field] = normalize_effect_text(card.get(field))


def find_type_name(text: str | None) -> str | None:
    """
    Find a Pokémon type name inside arbitrary text (a link label, an image alt, ...).

    >>> find_type_name("Pokemon TCG Pocket - Fire Type Icon")
    'Fire'
    >>> find_type_name("Lighting")
    'Lightning'
    >>> find_type_name("-") is None
    True
    """
    if not text:
        return None
    low = text.lower()
    for alias, real in TYPE_ALIASES.items():
        if alias in low:
            return real
    for name in TYPE_NAMES:
        if re.search(rf"\b{name.lower()}\b", low):
            return name
    return None


def is_trainer_type(card_type: str | None) -> bool:
    """A card is a Trainer (Item / Supporter / Pokemon Tool / ...) if its type isn't a Pokémon type."""
    return card_type not in TYPE_NAMES


def parse_energy_cost(energy_str: str) -> str:
    """
    Turn one energy descriptor like "Fire 2" into repeated emoji.
    Unknown types become "?" so problems are visible in the CSV.

    >>> parse_energy_cost("Darkness 2")
    '⚫⚫'
    >>> parse_energy_cost("Fire")
    '🔴'
    >>> parse_energy_cost("Unknown 3")
    '???'
    """
    m = re.fullmatch(r"(.+?)\s+(\d+)", energy_str.strip())
    name, count = (m.group(1), int(m.group(2))) if m else (energy_str.strip(), 1)
    symbol = ENERGY_SYMBOLS.get(name)
    if symbol is None:
        symbol = ENERGY_SYMBOLS.get(TYPE_ALIASES.get(name.lower(), ""), "?")
    return symbol * count


def energy_cost_to_symbols(text: str | None) -> str | None:
    """
    Convert the JSON's energy cost ("Grass:Colorless 2") to emoji ("🟢🔘🔘").
    Entries may be separated by ':' or ';'. Empty input gives `None`.

    >>> energy_cost_to_symbols("Grass:Colorless 2")
    '🟢🔘🔘'
    >>> energy_cost_to_symbols("") is None
    True
    """
    if not text:
        return None
    parts = [p.strip() for p in re.split(r"[:;]", text) if p.strip()]
    return "".join(parse_energy_cost(p) for p in parts) or None


ULTRA_BEASTS = {
    "Nihilego", "Buzzwole", "Pheromosa", "Xurkitree", "Celesteela", "Kartana",
    "Guzzlord", "Poipole", "Naganadel", "Stakataka", "Blacephalon",
}

ANCIENT_PARADOX = {
    "Great Tusk", "Scream Tail", "Brute Bonnet", "Flutter Mane",
    "Slither Wing", "Sandy Shocks", "Roaring Moon", "Koraidon",
    "Walking Wake", "Raging Bolt", "Gouging Fire",
}

FUTURE_PARADOX = {
    "Iron Treads", "Iron Bundle", "Iron Hands", "Iron Jugulis",
    "Iron Moth", "Iron Thorns", "Iron Valiant", "Miraidon",
    "Iron Boulder", "Iron Crown", "Iron Leaves",
}


def is_ultra_beast(name: str | None, card_type: str | None) -> bool:
    """True for Pokémon cards (incl. ex versions) of an Ultra Beast; never for Trainers."""
    if not name or is_trainer_type(card_type):
        return False
    return re.sub(r"\s+ex$", "", name) in ULTRA_BEASTS


def get_gimmick(name: str | None, card_type: str | None) -> str | None:
    """Return the broad gimmick for a Pokémon, or None when unclassified."""
    if not name or is_trainer_type(card_type):
        return None
    normalized_name = re.sub(r"\s+ex$", "", name)
    if normalized_name in ANCIENT_PARADOX:
        return "Ancient"
    if normalized_name in FUTURE_PARADOX:
        return "Future"
    if normalized_name in ULTRA_BEASTS:
        return "Ultra Beast"
    return None


def get_knockout_points(
    name: str | None, card_type: str | None, ex: str | None = None
) -> str | None:
    """Return string-valued prize points for a Pokémon, or None for non-Pokémon cards."""
    if not name or is_trainer_type(card_type):
        return None
    normalized_name = name.strip()
    if normalized_name.lower().startswith("mega ") or (ex and "mega" in ex.lower()):
        return "3"
    if (ex and ex.strip()) or re.search(r"\s+ex$", normalized_name, re.IGNORECASE):
        return "2"
    return "1"
