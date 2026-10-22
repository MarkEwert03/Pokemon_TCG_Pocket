from tcg.utils import get_classification


def test_classifies_paradox_pokemon():
    assert get_classification("Great Tusk", "Fighting") == "Ancient"
    assert get_classification("Iron Bundle ex", "Water") == "Future"


def test_classification_excludes_trainers_and_unknowns():
    assert get_classification("Great Tusk", "Item") is None
    assert get_classification("Bulbasaur", "Grass") is None


def test_classification_keeps_ultra_beast_values():
    assert get_classification("Buzzwole ex", "Fighting") == "Ultra Beast"
