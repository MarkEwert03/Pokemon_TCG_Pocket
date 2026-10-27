from tcg.utils import get_gimmick, normalize_effect_fields, normalize_effect_text


def test_classifies_paradox_pokemon():
    assert get_gimmick("Great Tusk", "Fighting") == "Ancient"
    assert get_gimmick("Iron Bundle ex", "Water") == "Future"


def test_gimmick_excludes_trainers_and_unknowns():
    assert get_gimmick("Great Tusk", "Item") is None
    assert get_gimmick("Bulbasaur", "Grass") is None


def test_gimmick_keeps_ultra_beast_values():
    assert get_gimmick("Buzzwole ex", "Fighting") == "Ultra Beast"


def test_normalize_effect_text():
    assert normalize_effect_text(
        "  Once during your turn, heal 20 damage from Pokémon’s Active Pokémon  "
    ) == "Once during your turn, heal 20 damage from Pokemon's Active Pokemon."
    assert normalize_effect_text("Flip a coin!") == "Flip a coin!"
    assert normalize_effect_text("Draw 2 cards.") == "Draw 2 cards."
    assert normalize_effect_text(None) is None


def test_normalize_effect_fields():
    card = {
        "ability_effect": "Use Pokémon’s Ability",
        "move1_effect": "  Do damage  ",
        "move2_effect": None,
    }

    normalize_effect_fields(card)

    assert card == {
        "ability_effect": "Use Pokemon's Ability.",
        "move1_effect": "Do damage.",
        "move2_effect": None,
    }
