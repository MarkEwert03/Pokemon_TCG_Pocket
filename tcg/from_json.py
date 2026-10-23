"""
Stage 2: turn the big raw game8 JSON into one flat dict per card.

Everything the JSON can provide is filled in here. Fields that only exist on
the individual card pages (see `config.PAGE_FIELDS`) are left as `None` and
filled in by `pipeline.py` after scraping.
"""

import json
import re
from pathlib import Path

from tcg.config import COLUMNS
from tcg.utils import (
    clean_str,
    energy_cost_to_symbols,
    get_knockout_points,
    is_trainer_type,
)


# Pack codes like "A1-M", "A4b", "P-A" appear in the junk entry's energy_cost
_PACK_CODE = re.compile(r"^(?:[AB]\d+[a-z]?|P-[AB])(?:-[A-Z])?$")


def load_raw_cards(path: Path) -> list[dict]:
    """Return the list of raw card dicts from `cardArraySchema.cards`."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    cards = data.get("cardArraySchema", {}).get("cards", [])
    if not cards:
        raise ValueError(f"No cards found in {path}")
    return cards


def _convert_move(raw_move: dict) -> dict | None:
    """
    Convert one entry of a card's `moves` list.

    Returns `None` for empty slots and for the junk entry game8 appends to every
    card (its "damage" is a pull-rate string like "1.5% | 0.2% | 0% | 0%").
    """
    damage = clean_str(raw_move.get("damage"))
    if damage and "%" in damage:
        return None
    tokens = re.split(r"[:;]", raw_move.get("energy_cost") or "")
    if any(_PACK_CODE.match(t.strip()) for t in tokens):
        return None  # pull-rate junk whose "energy" is really a list of packs

    move = {
        "name": clean_str(raw_move.get("name")),
        "cost": energy_cost_to_symbols(raw_move.get("energy_cost")),
        "damage": damage,
        "effect": clean_str(raw_move.get("description")),
    }
    return move if any(move.values()) else None


def convert_card(
    raw: dict, single_pack_expansions: set[str] | None = None
) -> dict[str, str | None]:
    """
    Convert one raw JSON card into a dict with exactly the keys in `COLUMNS`.

    Note: moves are packed consecutively, so `move1_*` is always the card's
    first attack, whether or not the card also has an ability.
    """
    card: dict[str, str | None] = dict.fromkeys(COLUMNS)

    is_pokemon = raw.get("card_type") == "Pokemon"

    card_type = clean_str(raw.get("pokemon_type"))
    if card_type == "Tool":
        card_type = "Pokemon Tool"

    set_name = clean_str(raw.get("set"))
    subset = clean_str(raw.get("subset"))
    single_pack_expansions = single_pack_expansions or set()
    if set_name in single_pack_expansions or (subset and subset.startswith("Any (")):
        pack_name = "Any"
    else:
        pack_name = subset

    card.update(
        id=clean_str(raw.get("id")),
        name=clean_str(raw.get("name")),
        rarity=clean_str(raw.get("rarity")),
        stage=clean_str(raw.get("evolution_stage")) if is_pokemon else None,
        hp=clean_str(raw.get("hp")) if is_pokemon else None,
        type=card_type,
        knockout_points=get_knockout_points(
            clean_str(raw.get("name")), card_type, clean_str(raw.get("ex"))
        ),
        expansion=set_name,
        pack_name=pack_name,
        ability_name=clean_str(raw.get("ability")),
        image=clean_str(raw.get("image_url")),
        url=clean_str(raw.get("archive_url")),
    )

    moves = [m for m in map(_convert_move, raw.get("moves") or []) if m]

    if is_trainer_type(card_type):
        # Trainers have no attacks. If the JSON carries their text, keep it in
        # ability_effect (README convention); otherwise the page scrape fills it.
        card["ability_effect"] = next((m["effect"] for m in moves if m["effect"]), None)
    else:
        for i, move in enumerate(moves[:2], start=1):
            card[f"move{i}_name"] = move["name"]
            card[f"move{i}_cost"] = move["cost"]
            card[f"move{i}_damage"] = move["damage"]
            card[f"move{i}_effect"] = move["effect"]

    return card


def convert_all(raw_cards: list[dict]) -> list[dict[str, str | None]]:
    subsets_by_expansion: dict[str, set[str]] = {}
    for raw in raw_cards:
        expansion = clean_str(raw.get("set"))
        subset = clean_str(raw.get("subset"))
        if expansion and subset:
            subsets_by_expansion.setdefault(expansion, set()).add(subset)
    single_pack_expansions = {
        expansion for expansion, subsets in subsets_by_expansion.items() if len(subsets) == 1
    }
    return [convert_card(c, single_pack_expansions) for c in raw_cards]
