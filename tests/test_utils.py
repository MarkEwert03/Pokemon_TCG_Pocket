from tcg.utils import get_gimmick


def test_classifies_paradox_pokemon():
    assert get_gimmick("Great Tusk", "Fighting") == "Ancient"
    assert get_gimmick("Iron Bundle ex", "Water") == "Future"


def test_gimmick_excludes_trainers_and_unknowns():
    assert get_gimmick("Great Tusk", "Item") is None
    assert get_gimmick("Bulbasaur", "Grass") is None


def test_gimmick_keeps_ultra_beast_values():
    assert get_gimmick("Buzzwole ex", "Fighting") == "Ultra Beast"
