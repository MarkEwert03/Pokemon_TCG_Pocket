from tcg_extract.parser import clean_str, extract_card
from bs4 import BeautifulSoup


def test_clean_str():
    assert clean_str("  Hello   World  ") == "Hello World"
    assert clean_str("Line1\nLine2\t\tLine3") == "Line1 Line2 Line3"
    assert clean_str("\t \n     \t", empty_val="N/A") == "N/A"
    assert clean_str("", empty_val="") == ""


def test_extract_card_sample():
    html = """
    <tr>
        <td></td>
        <td>A1 001</td>
        <td><a>Bulbasaur</a><img data-src="image.png"/></td>
        <td>◇</td>
        <td>Genetic Apex</td>
        <td><img alt="Pokemon TCG Pocket - Grass"/></td>
        <td>70</td>
        <td>Basic</td>
        <td>35 Pts</td>
        <td></td>
        <td>Open packs</td>
    </tr>
    """
    row = BeautifulSoup(html, "lxml").find("tr")
    card = extract_card(row)

    assert card["number"] == "A1 001"
    assert card["name"] == "Bulbasaur"
    assert card["image"] == "image.png"
    assert card["rarity"] == "◇"
    assert card["type"] == "Grass"
    assert card["HP"] == "70"
    assert card["pack_points"] == "35"
