"""
The fixture below is a *mock* modelled on the real Bulbasaur page
(https://game8.co/games/Pokemon-TCG-Pocket/archives/476002): label rows followed
by value rows, with some cells spanning columns.

If you save a real page to tests/fixtures/ you can add a test that parses it,
which is the best way to confirm the parser against the live site.
"""

from tcg.card_page import parse_card_page
from tcg.utils import energy_cost_to_symbols, find_type_name

CARD_INFO = """
<table class="a-table table--fixed a-table">
 <tr><td colspan="3">A1 001 Bulbasaur</td><td>Rating</td></tr>
 <tr><td colspan="3">Pack</td></tr>
 <tr><td colspan="3"><a href="#">Genetic Apex (Mewtwo)</a></td></tr>
 <tr><td colspan="3">Generation</td></tr>
 <tr><td colspan="3"><a href="#">Gen 1</a></td></tr>
 <tr><td colspan="3">Illustrator</td></tr>
 <tr><td colspan="3"><a href="#">Narumi Sato</a></td></tr>
 <tr><td>Stage</td><td>Type</td><td>Weakness</td></tr>
 <tr><td><a>Basic</a></td><td><a><img alt="Grass"></a></td><td><a><img alt="Fire"></a></td></tr>
 <tr><td>HP</td><td>Retreat Cost</td><td>Rarity</td></tr>
 <tr><td>70</td><td><a><img alt="Colorless"></a><a><img alt="Colorless"></a></td><td><a>◇</a></td></tr>
</table>
"""


def page(moves_html: str, extra: str = "") -> str:
    return f"""<html><body>
    {CARD_INFO}
    <h3>Bulbasaur Moves and Abilities</h3>
    <table>{moves_html}</table>
    <h3>Can be Crafted with 35 Pack Points</h3>
    <p>You can craft Bulbasaur by spending <b>35 Pack Points</b>!</p>
    <p>Can be Crafted with 35 Pack Points</p>
    <a href="#">List of Ultra Beasts</a>
    {extra}
    </body></html>"""


ATTACK_ONLY = "<tr><td>Grass Colorless Vine Whip</td></tr><tr><td>Damage: 40</td></tr>"


def test_basic_pokemon_page():
    out = parse_card_page(page(ATTACK_ONLY), is_trainer=False)
    assert out["generation"] == "1"
    assert out["illustrator"] == "Narumi Sato"
    assert out["weakness"] == "Fire"
    assert out["retreat_cost"] == "2"
    assert out["pack_points"] == "35"
    # the sidebar "List of Ultra Beasts" link must not trigger a false positive
    assert out["ultra_beast"] == "No"
    assert out["ability_effect"] is None


def test_ultra_beast_detected_inside_card_tables():
    moves = ATTACK_ONLY + "<tr><td>Ultra Beast</td></tr>"
    assert parse_card_page(page(moves), is_trainer=False)["ultra_beast"] == "Yes"


def test_ability_effect_found_by_name_in_next_row():
    moves = (
        "<tr><td>[Ability] Powder Heal</td></tr>"
        "<tr><td>Once during your turn, you may heal 20 damage from each of your Pokémon.</td></tr>"
        "<tr><td>Vine Whip</td></tr>"
    )
    out = parse_card_page(page(moves), is_trainer=False, ability_name="Powder Heal")
    assert out["ability_effect"].startswith("Once during your turn")


def test_ability_effect_found_by_name_in_same_row():
    moves = "<tr><td>[Ability] Rough Skin: Do 20 damage to the attacker.</td></tr>"
    out = parse_card_page(page(moves), is_trainer=False, ability_name="Rough Skin")
    assert out["ability_effect"] == "Do 20 damage to the attacker."


def test_trainer_skips_weakness_and_retreat_and_takes_text():
    moves = "<tr><td>Draw 2 cards.</td></tr>"
    out = parse_card_page(page(moves), is_trainer=True)
    assert out["weakness"] is None and out["retreat_cost"] is None
    assert out["ability_effect"] == "Draw 2 cards."
    assert out["generation"] == "1"


def test_zero_retreat_cost_and_missing_pieces():
    html = page(ATTACK_ONLY).replace(
        '<a><img alt="Colorless"></a><a><img alt="Colorless"></a>', "-"
    )
    assert parse_card_page(html, is_trainer=False)["retreat_cost"] == "0"


def test_garbage_html_returns_all_none_without_crashing():
    out = parse_card_page("<html><body>nothing here</body></html>", is_trainer=False)
    assert out["generation"] is None and out["illustrator"] is None
    assert out["pack_points"] is None


def test_energy_helpers():
    assert energy_cost_to_symbols("Fire:Colorless 2") == "🔴🔘🔘"
    assert energy_cost_to_symbols("Lighting") == "🟡"  # game8 typo
    assert energy_cost_to_symbols("Mystery") == "?"
    assert find_type_name("Pokemon TCG Pocket - Fire Type Icon") == "Fire"
    assert find_type_name("-") is None
