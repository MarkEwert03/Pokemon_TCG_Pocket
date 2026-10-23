from tcg.config import COLUMNS
from tcg.from_json import convert_card

PULL_RATE_JUNK = {
    "name": "",
    "damage": "1.562% | 0.277% | 0% | 0%",
    "energy_cost": "A1-M:A4b",
    "description": "",
}
EMPTY_MOVE = {"name": "", "damage": "", "energy_cost": "", "description": ""}

BULBASAUR = {  # copied from the real JSON
    "id": "A1 001",
    "name": "Bulbasaur",
    "card_type": "Pokemon",
    "pokemon_type": "Grass",
    "rarity": "◇",
    "evolution_stage": "Basic",
    "ex": "",
    "hp": "70",
    "ability": "",
    "image_url": "https://img.game8.co/3998332/91c4f79b2b3b4206205bf69db8dd3d1e.png/show",
    "set": "Genetic Apex (A1)",
    "subset": "Mewtwo",
    "trainer_type": "Basic",
    "owned": False,
    "archive_url": "https://game8.co/games/Pokemon-TCG-Pocket/archives/476002",
    "moves": [
        {"name": "Vine Whip", "damage": "40", "energy_cost": "Grass:Colorless", "description": ""},
        EMPTY_MOVE,
        PULL_RATE_JUNK,
    ],
}


def test_has_exactly_the_readme_columns():
    assert list(convert_card(BULBASAUR)) == COLUMNS


def test_basic_pokemon():
    card = convert_card(BULBASAUR)
    assert card["id"] == "A1 001"
    assert card["name"] == "Bulbasaur"
    assert card["category"] == "Pokemon"
    assert card["stage"] == "Basic"
    assert card["hp"] == "70"
    assert card["type"] == "Grass"
    assert card["knockout_points"] == "1"
    assert card["expansion"] == "Genetic Apex (A1)"
    assert card["pack_name"] == "Mewtwo"
    assert card["move1_name"] == "Vine Whip"
    assert card["move1_cost"] == "🟢🔘"
    assert card["move1_damage"] == "40"
    assert card["move1_effect"] is None
    # empty slot + pull-rate junk must not leak into move2
    assert card["move2_name"] is None and card["move2_damage"] is None
    # page-only fields are left for the scraper
    assert card["weakness"] is None and card["generation"] is None


def test_ability_pokemon_packs_moves_consecutively():
    raw = {
        **BULBASAUR,
        "id": "A1 999",
        "ability": "Powder Heal",
        "moves": [
            {"name": "Crimson Storm", "damage": "200", "energy_cost": "Fire:Colorless 2", "description": "Discard 2 Fire Energy."},
            PULL_RATE_JUNK,
        ],
    }
    card = convert_card(raw)
    assert card["ability_name"] == "Powder Heal"
    assert card["move1_name"] == "Crimson Storm"
    assert card["move1_cost"] == "🔴🔘🔘"
    assert card["move1_effect"] == "Discard 2 Fire Energy."
    assert card["move2_name"] is None


def test_trainer_card():
    raw = {
        "id": "A1 223",
        "name": "Professor's Research",
        "card_type": "Trainer",
        "pokemon_type": "Supporter",
        "rarity": "◇",
        "evolution_stage": "",
        "hp": "",
        "ability": "",
        "set": "Genetic Apex (A1)",
        "subset": "Any",
        "archive_url": "https://game8.co/games/Pokemon-TCG-Pocket/archives/1",
        "image_url": "x",
        "moves": [
            {"name": "", "damage": "", "energy_cost": "", "description": "Draw 2 cards."},
            PULL_RATE_JUNK,
        ],
    }
    card = convert_card(raw)
    assert card["type"] == "Supporter"
    assert card["category"] == "Trainer"
    assert card["stage"] is None and card["hp"] is None
    assert card["knockout_points"] is None
    assert card["move1_cost"] is None
    assert card["ability_effect"] == "Draw 2 cards."


def test_tool_is_renamed():
    raw = {**BULBASAUR, "card_type": "Trainer", "pokemon_type": "Tool", "moves": []}
    assert convert_card(raw)["type"] == "Pokemon Tool"


def test_single_pack_expansion_uses_any_pack_name():
    raw = {**BULBASAUR, "set": "Eevee Grove", "subset": "Eevee"}
    card = convert_card(raw, {"Eevee Grove"})
    assert card["expansion"] == "Eevee Grove"
    assert card["pack_name"] == "Any"


def test_any_subset_is_normalized():
    raw = {**BULBASAUR, "subset": "Any (Genetic Apex)"}
    assert convert_card(raw)["pack_name"] == "Any"


def test_ex_and_mega_ex_knockout_points():
    ex_card = convert_card({**BULBASAUR, "name": "Charizard ex", "ex": "ex"})
    mega_ex_card = convert_card(
        {**BULBASAUR, "name": "Mega Charizard Y ex", "ex": "Mega Evolution ex"}
    )
    assert ex_card["knockout_points"] == "2"
    assert mega_ex_card["knockout_points"] == "3"
