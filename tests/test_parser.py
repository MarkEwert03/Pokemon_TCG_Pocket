from bs4 import BeautifulSoup
from tcg_extract.parser import extract_card
from tcg_extract.io import fetch_html_table
from tests.debug import debug_card_extract

TABLE_HTML = fetch_html_table()
DEFAULT_EMPTY = None

def test_extract_card_pokemon_one_attack():
    """Testing `A1 001` (Bulbasaur)"""

    expected_keys = {
        "number",
        "name",
        "rarity",
        "stage",
        "HP",
        "type",
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
        "retreat_cost",
        "pack_name",
        "pack_points",
        "image",
    }

    card = debug_card_extract("A1 001", html=TABLE_HTML)

    assert set(card.keys()) == expected_keys
    assert card["number"] == "A1 001"
    assert card["name"] == "Bulbasaur"
    assert card["rarity"] == "◇"
    assert card["stage"] == "Basic"
    assert card["HP"] == "70"
    assert card["type"] == "Grass"
    assert card["move1_name"] == "Vine Whip"
    assert card["move1_cost"] == "🟢*️⃣"
    assert card["move1_damage"] == "40"
    assert card["move1_effect"] == DEFAULT_EMPTY
    assert card["move2_name"] == DEFAULT_EMPTY
    assert card["move2_cost"] == DEFAULT_EMPTY
    assert card["move2_damage"] == DEFAULT_EMPTY
    assert card["move2_effect"] == DEFAULT_EMPTY
    assert card["retreat_cost"] == "1"
    assert card["pack_name"] == "Genetic Apex (A1) Mewtwo"
    assert card["pack_points"] == "35"
    assert card["image"] == "https://img.game8.co/3998332/91c4f79b2b3b4206205bf69db8dd3d1e.png/show"


def test_extract_card_pokemon_two_attacks():
    """Testing `A1 004` (Venusaur ex)"""
    card = debug_card_extract("A1 004", html=TABLE_HTML)

    assert card["number"] == "A1 004"
    assert card["name"] == "Venusaur ex"
    assert card["rarity"] == "◇◇◇◇"
    assert card["stage"] == "Stage 2"
    assert card["HP"] == "190"
    assert card["type"] == "Grass"
    assert card["move1_name"] == "Razor Leaf"
    assert card["move1_cost"] == "🟢*️⃣*️⃣"
    assert card["move1_damage"] == "60"
    assert card["move1_effect"] == DEFAULT_EMPTY
    assert card["move2_name"] == "Giant Bloom"
    assert card["move2_cost"] == "🟢🟢*️⃣*️⃣"
    assert card["move2_damage"] == "100"
    assert card["move2_effect"] == "Heal 30 damage from this Pokemon."
    assert card["retreat_cost"] == "3"
    assert card["pack_name"] == "Genetic Apex (A1) Mewtwo"
    assert card["pack_points"] == "500"
    assert card["image"] == "https://img.game8.co/3995580/151d2c9455f83899618147d85881a75e.png/show"


def test_extract_card_pokemon_move_desc_no_dmg():
    """Testing `A1 047` (Moltres ex)"""
    card = debug_card_extract("A1 047", html=TABLE_HTML)

    assert card["number"] == "A1 047"
    assert card["name"] == "Moltres ex"
    assert card["rarity"] == "◇◇◇◇"
    assert card["stage"] == "Basic"
    assert card["HP"] == "140"
    assert card["type"] == "Fire"
    assert card["move1_name"] == "Inferno Dance"
    assert card["move1_cost"] == "🔴"
    assert card["move1_damage"] == DEFAULT_EMPTY
    assert (
        card["move1_effect"]
        == "Flip 3 coins. Take an amount of Fire Energy from your Energy Zone equal to the number of heads and attach it to your Benched Fire Pokemon in any way you like."
    )
    assert card["move2_name"] == "Heat Blast"
    assert card["move2_cost"] == "🔴*️⃣*️⃣"
    assert card["move2_damage"] == "70"
    assert card["move2_effect"] == DEFAULT_EMPTY
    assert card["retreat_cost"] == "2"
    assert card["pack_name"] == "Genetic Apex (A1) Charizard"
    assert card["pack_points"] == "500"
    assert card["image"] == "https://img.game8.co/3998342/21cb0fbf6aa4a791867a2c21ff9add20.png/show"


def test_extract_card_pokemon_dynamic_dmg():
    """Testing `A1 026` (Pinsir)"""
    card = debug_card_extract("A1 026", html=TABLE_HTML)

    assert card["number"] == "A1 026"
    assert card["name"] == "Pinsir"
    assert card["rarity"] == "◇◇"
    assert card["stage"] == "Basic"
    assert card["HP"] == "90"
    assert card["type"] == "Grass"
    assert card["move1_name"] == "Double Horn"
    assert card["move1_cost"] == "🟢🟢"
    assert card["move1_damage"] == "50x"
    assert card["move1_effect"] == "Flip 2 coins. This attack does 50 damage for each heads."
    assert card["move2_name"] == DEFAULT_EMPTY
    assert card["move2_cost"] == DEFAULT_EMPTY
    assert card["move2_damage"] == DEFAULT_EMPTY
    assert card["move2_effect"] == DEFAULT_EMPTY
    assert card["retreat_cost"] == "2"
    assert card["pack_name"] == "Genetic Apex (A1) Any"
    assert card["pack_points"] == "70"
    assert card["image"] == "https://img.game8.co/4171739/029c4cb3ce8eb5f85a1359121766e8ce.png/show"


def test_extract_card_pokemon_ability():
    """Testing `A1 007` (Butterfree)"""
    card = debug_card_extract("A1 007", html=TABLE_HTML)

    assert card["number"] == "A1 007"
    assert card["name"] == "Butterfree"
    assert card["rarity"] == "◇◇◇"
    assert card["stage"] == "Stage 2"
    assert card["HP"] == "120"
    assert card["type"] == "Grass"
    assert card["ability_name"] == "Powder Heal"
    assert (
        card["ability_effect"]
        == "Once during your turn, you may heal 20 damage from each of your Pokemon."
    )
    assert card["move1_name"] == DEFAULT_EMPTY
    assert card["move1_cost"] == DEFAULT_EMPTY
    assert card["move1_damage"] == DEFAULT_EMPTY
    assert card["move1_effect"] == DEFAULT_EMPTY
    assert card["move2_name"] == "Gust"
    assert card["move2_cost"] == "🟢*️⃣*️⃣"
    assert card["move2_damage"] == "60"
    assert card["move2_effect"] == DEFAULT_EMPTY
    assert card["retreat_cost"] == "1"
    assert card["pack_name"] == "Genetic Apex (A1) Pikachu"
    assert card["pack_points"] == "150"
    assert card["image"] == "https://img.game8.co/4004057/6ba461fb08292cbabe715b6ead54dfb9.png/show"


def test_extract_card_fossil():
    """Testing `A1 216` (Helix Fossil)"""
    card = debug_card_extract("A1 216", html=TABLE_HTML)

    assert card["number"] == "A1 216"
    assert card["name"] == "Helix Fossil"
    assert card["rarity"] == "◇"
    assert card["stage"] == DEFAULT_EMPTY
    assert card["HP"] == DEFAULT_EMPTY
    assert card["type"] == "Item"
    assert card["ability_name"] == DEFAULT_EMPTY
    assert (
        card["ability_effect"]
        == "Play this card as if it were a 40-HP Basic Colorless Pokemon. At any time during your turn, you may discard this card from play. This card can't retreat."
    )
    assert card["move1_name"] == DEFAULT_EMPTY
    assert card["move1_cost"] == DEFAULT_EMPTY
    assert card["move1_damage"] == DEFAULT_EMPTY
    assert card["move1_effect"] == DEFAULT_EMPTY
    assert card["move2_name"] == DEFAULT_EMPTY
    assert card["move2_cost"] == DEFAULT_EMPTY
    assert card["move2_damage"] == DEFAULT_EMPTY
    assert card["move2_effect"] == DEFAULT_EMPTY
    assert card["retreat_cost"] == DEFAULT_EMPTY
    assert card["pack_name"] == "Genetic Apex (A1) Pikachu"
    assert card["pack_points"] == "35"
    assert card["image"] == "https://img.game8.co/4004042/6f1a71c0a509b36ccf7dd29bf8bfa967.png/show"


def test_extract_card_supporter():
    """Testing `A1 219` (Erika)"""
    card = debug_card_extract("A1 219", html=TABLE_HTML)

    assert card["number"] == "A1 219"
    assert card["name"] == "Erika"
    assert card["rarity"] == "◇◇"
    assert card["stage"] == DEFAULT_EMPTY
    assert card["HP"] == DEFAULT_EMPTY
    assert card["type"] == "Supporter"
    assert card["ability_name"] == DEFAULT_EMPTY
    assert card["ability_effect"] == "Heal 50 damage from 1 of your Grass Pokemon."
    assert card["move1_name"] == DEFAULT_EMPTY
    assert card["move1_cost"] == DEFAULT_EMPTY
    assert card["move1_damage"] == DEFAULT_EMPTY
    assert card["move1_effect"] == DEFAULT_EMPTY
    assert card["move2_name"] == DEFAULT_EMPTY
    assert card["move2_cost"] == DEFAULT_EMPTY
    assert card["move2_damage"] == DEFAULT_EMPTY
    assert card["move2_effect"] == DEFAULT_EMPTY
    assert card["retreat_cost"] == DEFAULT_EMPTY
    assert card["pack_name"] == "Genetic Apex (A1) Charizard"
    assert card["pack_points"] == "70"
    assert card["image"] == "https://img.game8.co/3995535/5bc1164c2b9a79f4c40f21a8975adbb3.png/show"


def test_extract_card_full_art_supporter():
    """Testing `A1 269` (Full Art Koga)"""
    card = debug_card_extract("A1 269", html=TABLE_HTML)

    assert card["number"] == "A1 269"
    assert card["name"] == "Koga"
    assert card["rarity"] == "☆☆"
    assert card["stage"] == DEFAULT_EMPTY
    assert card["HP"] == DEFAULT_EMPTY
    assert card["type"] == "Supporter"
    assert card["ability_name"] == DEFAULT_EMPTY
    assert card["ability_effect"] == "Put your Muk or Weezing in the Active Spot into your hand."
    assert card["move1_name"] == DEFAULT_EMPTY
    assert card["move1_cost"] == DEFAULT_EMPTY
    assert card["move1_damage"] == DEFAULT_EMPTY
    assert card["move1_effect"] == DEFAULT_EMPTY
    assert card["move2_name"] == DEFAULT_EMPTY
    assert card["move2_cost"] == DEFAULT_EMPTY
    assert card["move2_damage"] == DEFAULT_EMPTY
    assert card["move2_effect"] == DEFAULT_EMPTY
    assert card["retreat_cost"] == DEFAULT_EMPTY
    assert card["pack_name"] == "Genetic Apex (A1) Mewtwo"
    assert card["pack_points"] == "1250"
    assert card["image"] == "https://img.game8.co/4004062/0c2bbaf7e3e34c46d1593b6780108de9.png/show"
