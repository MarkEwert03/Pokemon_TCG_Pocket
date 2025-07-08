from bs4 import BeautifulSoup
from tests.debug import debug_card_extract
from tcg_extract.io import fetch_html_table
from tcg_extract.parser import extract_card
from tcg_extract.parser import DEFAULT_EMPTY


TABLE_HTML = fetch_html_table()


def test_extract_card_raw_from_html():
    """Testing `A1 001` (Bulbasaur)"""
    html = """
        <tr>
            <td class="center"><input type="checkbox" id="checkbox1_1"></td>
            <td class="center"><b class="a-bold">A1 001</b></td>

            <td class="center">
            <div class="imageLink js-archive-open-image-modal"
                data-image-url="https://img.game8.co/3998332/91c4f79b2b3b4206205bf69db8dd3d1e.png/original"
                data-micromodal-trigger="js-archive-open-image-modal" data-archive-url><img
                src="https://img.game8.co/3998332/91c4f79b2b3b4206205bf69db8dd3d1e.png/show"
                class="a-img lazy lazy-non-square lazy-loaded"
                alt="Pokemon TCG Pocket - A1 001 Bulbasaur"
                data-src="https://img.game8.co/3998332/91c4f79b2b3b4206205bf69db8dd3d1e.png/show"
                width="172"
                style="height: 0; padding-bottom: calc(px*240/172); padding-bottom: calc(min(100%,172px)*240/172);"
                data-loaded="true"><span class="imageLink__icon"></span></div> <a class="a-link"
                href="https://game8.co/games/Pokemon-TCG-Pocket/archives/476002">Bulbasaur</a>

            </td>

            <td class="center"><img
                src="https://img.game8.co/3994728/d0cbe26800d9abdfccddbbfd5aeab3e5.png/show"
                class="a-img lazy lazy-non-square lazy-loaded" alt="Pokemon TCG Pocket - ◇ rarity"
                data-src="https://img.game8.co/3994728/d0cbe26800d9abdfccddbbfd5aeab3e5.png/show"
                width="18"
                style="height: 0; padding-bottom: calc(px*25/18); padding-bottom: calc(min(100%,18px)*25/18);"
                data-loaded="true">
            <hr class="a-table__line">◇
            </td>

            <td class="center"><img
                src="https://img.game8.co/3999180/083249170af7215407df57bf9840bc3e.png/show"
                class="a-img lazy lazy-loaded" alt="Pokemon TCG Pocket - Mewtwo Booster Pack"
                data-src="https://img.game8.co/3999180/083249170af7215407df57bf9840bc3e.png/show"
                width="50" height="50"
                data-loaded="true"> <br> <b class="a-bold">Genetic Apex (A1)</b> <br> Mewtwo</td>

            <td class="center"><img
                src="https://img.game8.co/3994729/63b3ad9a73304c7fb7ca479cee7ed4c3.png/show"
                class="a-img lazy lazy-loaded" alt="Pokemon TCG Pocket - Grass"
                data-src="https://img.game8.co/3994729/63b3ad9a73304c7fb7ca479cee7ed4c3.png/show"
                width="40" height="40"
                data-loaded="true"></td>

            <td class="center"> 70 </td>

            <td class="center"> Basic </td>

            <td class="center">35 Pts </td>
            <td class="left">
            <br> <b class="a-bold">Stage</b>: Basic <br>
            <div class="align"> <b class="a-bold">Retreat Cost</b>: <img
                src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                class="a-img lazy"
                alt="Pokemon TCG Pocket - Retreat Cost"
                data-src="https://img.game8.co/3994730/6e5546e2fbbc5a029ac79acf2b2b8042.png/show"
                width="20" height="20">
            </div>
            <hr class="a-table__line">

            <div class="align"> <b class="a-bold">Vine Whip</b>

                <a class="a-link" href="https://game8.co/games/Pokemon-TCG-Pocket/archives/476531"><img
                    src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                    class="a-img lazy"
                    alt="Grass"
                    data-src="https://img.game8.co/4018726/c2d96eaebb6cd06d6a53dfd48da5341c.png/show"
                    width="15"
                    height="15"></a>

                <a class="a-link" href="https://game8.co/games/Pokemon-TCG-Pocket/archives/476389"><img
                    src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                    class="a-img lazy"
                    alt="Colorless"
                    data-src="https://img.game8.co/4018721/a654c44596214b3bf38769c180602a16.png/show"
                    width="15" height="15"></a>

            </div>
            40 <br>

            </td>
            <td class="left">Open Genetic Apex (A1) Mewtwo packs</td>
        </tr>
        """
    row = BeautifulSoup(html, "lxml").find("tr")
    card = extract_card(row)

    assert card["number"] == "A1 001"
    assert card["name"] == "Bulbasaur"
    assert card["rarity"] == "◇"
    assert card["stage"] == "Basic"
    assert card["HP"] == "70"
    assert card["type"] == "Grass"
    assert card["weakness"] == "Fire"
    assert card["retreat_cost"] == "1"
    assert card["ultra_beast"] == "No"
    assert card["generation"] == "1"
    assert card["illustrator"] == "Narumi Sato"
    assert card["pack_name"] == "Genetic Apex (A1) Mewtwo"
    assert card["pack_points"] == "35"
    assert card["ability_name"] == DEFAULT_EMPTY
    assert card["ability_effect"] == DEFAULT_EMPTY
    assert card["move1_name"] == "Vine Whip"
    assert card["move1_cost"] == "🟢*️⃣"
    assert card["move1_damage"] == "40"
    assert card["move1_effect"] == DEFAULT_EMPTY
    assert card["move2_name"] == DEFAULT_EMPTY
    assert card["move2_cost"] == DEFAULT_EMPTY
    assert card["move2_damage"] == DEFAULT_EMPTY
    assert card["move2_effect"] == DEFAULT_EMPTY
    assert card["image"] == "https://img.game8.co/3998332/91c4f79b2b3b4206205bf69db8dd3d1e.png/show"
    assert card["url"] == "https://game8.co/games/Pokemon-TCG-Pocket/archives/476002"


def test_extract_card_pokemon_one_attack():
    """Testing `A1 001` (Bulbasaur)"""

    expected_keys = {
        "number",
        "name",
        "rarity",
        "stage",
        "HP",
        "type",
        "weakness",
        "retreat_cost",
        "ultra_beast",
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
    }

    card = debug_card_extract("A1 001", html=TABLE_HTML)

    assert set(card.keys()) == expected_keys
    assert card["number"] == "A1 001"
    assert card["name"] == "Bulbasaur"
    assert card["rarity"] == "◇"
    assert card["stage"] == "Basic"
    assert card["HP"] == "70"
    assert card["type"] == "Grass"
    assert card["weakness"] == "Fire"
    assert card["retreat_cost"] == "1"
    assert card["ultra_beast"] == "No"
    assert card["generation"] == "1"
    assert card["illustrator"] == "Narumi Sato"
    assert card["pack_name"] == "Genetic Apex (A1) Mewtwo"
    assert card["pack_points"] == "35"
    assert card["ability_name"] == DEFAULT_EMPTY
    assert card["ability_effect"] == DEFAULT_EMPTY
    assert card["move1_name"] == "Vine Whip"
    assert card["move1_cost"] == "🟢*️⃣"
    assert card["move1_damage"] == "40"
    assert card["move1_effect"] == DEFAULT_EMPTY
    assert card["move2_name"] == DEFAULT_EMPTY
    assert card["move2_cost"] == DEFAULT_EMPTY
    assert card["move2_damage"] == DEFAULT_EMPTY
    assert card["move2_effect"] == DEFAULT_EMPTY
    assert card["image"] == "https://img.game8.co/3998332/91c4f79b2b3b4206205bf69db8dd3d1e.png/show"
    assert card["url"] == "https://game8.co/games/Pokemon-TCG-Pocket/archives/476002"


def test_extract_card_pokemon_two_attacks():
    """Testing `A1 004` (Venusaur ex)"""
    card = debug_card_extract("A1 004", html=TABLE_HTML)

    assert card["number"] == "A1 004"
    assert card["name"] == "Venusaur ex"
    assert card["rarity"] == "◇◇◇◇"
    assert card["stage"] == "Stage 2"
    assert card["HP"] == "190"
    assert card["type"] == "Grass"
    assert card["weakness"] == "Fire"
    assert card["retreat_cost"] == "3"
    assert card["ultra_beast"] == "No"
    assert card["generation"] == "1"
    assert card["illustrator"] == "PLANETA CG Works"
    assert card["pack_name"] == "Genetic Apex (A1) Mewtwo"
    assert card["pack_points"] == "500"
    assert card["ability_name"] == DEFAULT_EMPTY
    assert card["ability_effect"] == DEFAULT_EMPTY
    assert card["move1_name"] == "Razor Leaf"
    assert card["move1_cost"] == "🟢*️⃣*️⃣"
    assert card["move1_damage"] == "60"
    assert card["move1_effect"] == DEFAULT_EMPTY
    assert card["move2_name"] == "Giant Bloom"
    assert card["move2_cost"] == "🟢🟢*️⃣*️⃣"
    assert card["move2_damage"] == "100"
    assert card["move2_effect"] == "Heal 30 damage from this Pokemon."
    assert card["image"] == "https://img.game8.co/3995580/151d2c9455f83899618147d85881a75e.png/show"
    assert card["url"] == "https://game8.co/games/Pokemon-TCG-Pocket/archives/476005"


def test_extract_card_pokemon_move_desc_no_dmg():
    """Testing `A1 047` (Moltres ex)"""
    card = debug_card_extract("A1 047", html=TABLE_HTML)

    assert card["number"] == "A1 047"
    assert card["name"] == "Moltres ex"
    assert card["rarity"] == "◇◇◇◇"
    assert card["stage"] == "Basic"
    assert card["HP"] == "140"
    assert card["type"] == "Fire"
    assert card["weakness"] == "Lightning"
    assert card["retreat_cost"] == "2"
    assert card["ultra_beast"] == "No"
    assert card["generation"] == "1"
    assert card["illustrator"] == "PLANETA Tsuji"
    assert card["pack_name"] == "Genetic Apex (A1) Charizard"
    assert card["pack_points"] == "500"
    assert card["ability_name"] == DEFAULT_EMPTY
    assert card["ability_effect"] == DEFAULT_EMPTY
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
    assert card["image"] == "https://img.game8.co/3998342/21cb0fbf6aa4a791867a2c21ff9add20.png/show"
    assert card["url"] == "https://game8.co/games/Pokemon-TCG-Pocket/archives/476048"


def test_extract_card_pokemon_dynamic_dmg():
    """Testing `A1 026` (Pinsir)"""
    card = debug_card_extract("A1 026", html=TABLE_HTML)

    assert card["number"] == "A1 026"
    assert card["name"] == "Pinsir"
    assert card["rarity"] == "◇◇"
    assert card["stage"] == "Basic"
    assert card["HP"] == "90"
    assert card["type"] == "Grass"
    assert card["weakness"] == "Fire"
    assert card["retreat_cost"] == "2"
    assert card["ultra_beast"] == "No"
    assert card["generation"] == "1"
    assert card["illustrator"] == "Eri Yamaki"
    assert card["pack_name"] == "Genetic Apex (A1) Any"
    assert card["pack_points"] == "70"
    assert card["ability_name"] == DEFAULT_EMPTY
    assert card["ability_effect"] == DEFAULT_EMPTY
    assert card["move1_name"] == "Double Horn"
    assert card["move1_cost"] == "🟢🟢"
    assert card["move1_damage"] == "50x"
    assert card["move1_effect"] == "Flip 2 coins. This attack does 50 damage for each heads."
    assert card["move2_name"] == DEFAULT_EMPTY
    assert card["move2_cost"] == DEFAULT_EMPTY
    assert card["move2_damage"] == DEFAULT_EMPTY
    assert card["move2_effect"] == DEFAULT_EMPTY
    assert card["image"] == "https://img.game8.co/4171739/029c4cb3ce8eb5f85a1359121766e8ce.png/show"
    assert card["url"] == "https://game8.co/games/Pokemon-TCG-Pocket/archives/476027"


def test_extract_card_pokemon_ability():
    """Testing `A1 007` (Butterfree)"""
    card = debug_card_extract("A1 007", html=TABLE_HTML)

    assert card["number"] == "A1 007"
    assert card["name"] == "Butterfree"
    assert card["rarity"] == "◇◇◇"
    assert card["stage"] == "Stage 2"
    assert card["HP"] == "120"
    assert card["type"] == "Grass"
    assert card["weakness"] == "Fire"
    assert card["retreat_cost"] == "1"
    assert card["ultra_beast"] == "No"
    assert card["generation"] == "1"
    assert card["illustrator"] == "Shin Nagasawa"
    assert card["pack_name"] == "Genetic Apex (A1) Pikachu"
    assert card["pack_points"] == "150"
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
    assert card["image"] == "https://img.game8.co/4004057/6ba461fb08292cbabe715b6ead54dfb9.png/show"
    assert card["url"] == "https://game8.co/games/Pokemon-TCG-Pocket/archives/476008"


def test_extract_card_pokemon_dragon_weakness():
    """Testing `A1 183` (Dratini)"""
    card = debug_card_extract("A1 183", html=TABLE_HTML)

    assert card["number"] == "A1 183"
    assert card["name"] == "Dratini"
    assert card["rarity"] == "◇"
    assert card["stage"] == "Basic"
    assert card["HP"] == "70"
    assert card["type"] == "Dragon"
    assert card["weakness"] == DEFAULT_EMPTY
    assert card["retreat_cost"] == "1"
    assert card["ultra_beast"] == "No"
    assert card["generation"] == "1"
    assert card["illustrator"] == "Ayaka Yoshida"
    assert card["pack_name"] == "Genetic Apex (A1) Mewtwo"
    assert card["pack_points"] == "35"
    assert card["ability_name"] == DEFAULT_EMPTY
    assert card["ability_effect"] == DEFAULT_EMPTY
    assert card["move1_name"] == "Ram"
    assert card["move1_cost"] == "🔵🟡"
    assert card["move1_damage"] == "40"
    assert card["move1_effect"] == DEFAULT_EMPTY
    assert card["move2_name"] == DEFAULT_EMPTY
    assert card["move2_cost"] == DEFAULT_EMPTY
    assert card["move2_damage"] == DEFAULT_EMPTY
    assert card["move2_effect"] == DEFAULT_EMPTY
    assert card["image"] == "https://img.game8.co/3998335/06a6057b224d2d3f3a15dbd309fb417f.png/show"
    assert card["url"] == "https://game8.co/games/Pokemon-TCG-Pocket/archives/476184"


def test_extract_card_pokemon_ultra_beast():
    """Testing `A3a 006` (Buzzwole ex)"""
    card = debug_card_extract("A3a 006", html=TABLE_HTML)

    assert card["number"] == "A3a 006"
    assert card["name"] == "Buzzwole ex"
    assert card["rarity"] == "◇◇◇◇"
    assert card["stage"] == "Basic"
    assert card["HP"] == "140"
    assert card["type"] == "Grass"
    assert card["weakness"] == "Fire"
    assert card["retreat_cost"] == "2"
    assert card["ultra_beast"] == "Yes"
    assert card["generation"] == "7"
    assert card["illustrator"] == "PLANETA Mochizuki"
    assert card["pack_name"] == "Extradimensional Crisis (A3a) Buzzwole"
    assert card["pack_points"] == "500"
    assert card["ability_name"] == DEFAULT_EMPTY
    assert card["ability_effect"] == DEFAULT_EMPTY
    assert card["move1_name"] == "Punch"
    assert card["move1_cost"] == "*️⃣*️⃣"
    assert card["move1_damage"] == "30"
    assert card["move1_effect"] == DEFAULT_EMPTY
    assert card["move2_name"] == "Big Beat"
    assert card["move2_cost"] == "🟢🟢*️⃣"
    assert card["move2_damage"] == "120"
    assert card["move2_effect"] == "During your next turn, this Pokemon can't use Big Beat."
    assert card["image"] == "https://img.game8.co/4185088/48191f53a1f16dd41c7995e2f2277e83.png/show"
    assert card["url"] == "https://game8.co/games/Pokemon-TCG-Pocket/archives/523189"


def test_extract_card_fossil():
    """Testing `A1 216` (Helix Fossil)"""
    card = debug_card_extract("A1 216", html=TABLE_HTML)

    assert card["number"] == "A1 216"
    assert card["name"] == "Helix Fossil"
    assert card["rarity"] == "◇"
    assert card["stage"] == DEFAULT_EMPTY
    assert card["HP"] == DEFAULT_EMPTY
    assert card["type"] == "Item"
    assert card["weakness"] == DEFAULT_EMPTY
    assert card["retreat_cost"] == DEFAULT_EMPTY
    assert card["ultra_beast"] == "No"
    assert card["generation"] == "1"
    assert card["illustrator"] == "Toyste Beach"
    assert card["pack_name"] == "Genetic Apex (A1) Pikachu"
    assert card["pack_points"] == "35"
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
    assert card["image"] == "https://img.game8.co/4004042/6f1a71c0a509b36ccf7dd29bf8bfa967.png/show"
    assert card["url"] == "https://game8.co/games/Pokemon-TCG-Pocket/archives/476269"


def test_extract_card_supporter():
    """Testing `A1 219` (Erika)"""
    card = debug_card_extract("A1 219", html=TABLE_HTML)

    assert card["number"] == "A1 219"
    assert card["name"] == "Erika"
    assert card["rarity"] == "◇◇"
    assert card["stage"] == DEFAULT_EMPTY
    assert card["HP"] == DEFAULT_EMPTY
    assert card["type"] == "Supporter"
    assert card["weakness"] == DEFAULT_EMPTY
    assert card["retreat_cost"] == DEFAULT_EMPTY
    assert card["ultra_beast"] == "No"
    assert card["generation"] == "1"
    assert card["illustrator"] == "kirisAki"
    assert card["pack_name"] == "Genetic Apex (A1) Charizard"
    assert card["pack_points"] == "70"
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
    assert card["image"] == "https://img.game8.co/3995535/5bc1164c2b9a79f4c40f21a8975adbb3.png/show"
    assert card["url"] == "https://game8.co/games/Pokemon-TCG-Pocket/archives/476272"


def test_extract_card_full_art_supporter():
    """Testing `A1 269` (Full Art Koga)"""
    card = debug_card_extract("A1 269", html=TABLE_HTML)

    assert card["number"] == "A1 269"
    assert card["name"] == "Koga"
    assert card["rarity"] == "☆☆"
    assert card["stage"] == DEFAULT_EMPTY
    assert card["HP"] == DEFAULT_EMPTY
    assert card["type"] == "Supporter"
    assert card["weakness"] == DEFAULT_EMPTY
    assert card["retreat_cost"] == DEFAULT_EMPTY
    assert card["ultra_beast"] == "No"
    assert card["generation"] == "1"
    assert card["illustrator"] == "Souichirou Gunjima"
    assert card["pack_name"] == "Genetic Apex (A1) Mewtwo"
    assert card["pack_points"] == "1250"
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
    assert card["image"] == "https://img.game8.co/4004062/0c2bbaf7e3e34c46d1593b6780108de9.png/show"
    assert card["url"] == "https://game8.co/games/Pokemon-TCG-Pocket/archives/476283"


def test_extract_card_tool():
    """Testing `A3 146` (Poison Barb)"""
    card = debug_card_extract("A3 146", html=TABLE_HTML)

    assert card["number"] == "A3 146"
    assert card["name"] == "Poison Barb"
    assert card["rarity"] == "◇◇"
    assert card["stage"] == DEFAULT_EMPTY
    assert card["HP"] == DEFAULT_EMPTY
    assert card["type"] == "Pokemon Tool"
    assert card["weakness"] == DEFAULT_EMPTY
    assert card["retreat_cost"] == DEFAULT_EMPTY
    assert card["ultra_beast"] == "No"
    assert card["generation"] == "2"
    assert card["illustrator"] == "Toyste Beach"
    assert card["pack_name"] == "Celestial Guardians (A3) Lunala"
    assert card["pack_points"] == "70"
    assert card["ability_name"] == DEFAULT_EMPTY
    assert (
        card["ability_effect"]
        == "If the Pokemon this card is attached to is your Active Pokemon and is damaged by an attack from your opponent’s Pokemon, the Attacking Pokemon is now Poisoned."
    )
    assert card["move1_name"] == DEFAULT_EMPTY
    assert card["move1_cost"] == DEFAULT_EMPTY
    assert card["move1_damage"] == DEFAULT_EMPTY
    assert card["move1_effect"] == DEFAULT_EMPTY
    assert card["move2_name"] == DEFAULT_EMPTY
    assert card["move2_cost"] == DEFAULT_EMPTY
    assert card["move2_damage"] == DEFAULT_EMPTY
    assert card["move2_effect"] == DEFAULT_EMPTY
    assert card["image"] == "https://img.game8.co/4162476/1cdd88829801e39c73f40dc50816b558.png/show"
    assert card["url"] == "https://game8.co/games/Pokemon-TCG-Pocket/archives/518821"


def test_extract_card_promo_item():
    """Testing `P-A 005` (Poke Ball)"""
    card = debug_card_extract("P-A 005", html=TABLE_HTML)

    assert card["number"] == "P-A 005"
    assert card["name"] == "Poke Ball"
    assert card["rarity"] == "Promo"
    assert card["stage"] == DEFAULT_EMPTY
    assert card["HP"] == DEFAULT_EMPTY
    assert card["type"] == "Item"
    assert card["weakness"] == DEFAULT_EMPTY
    assert card["retreat_cost"] == DEFAULT_EMPTY
    assert card["ultra_beast"] == "No"
    assert card["generation"] == "1"
    assert card["illustrator"] == "Ryo Ueda"
    assert card["pack_name"] == "Promo Promo-A"
    assert card["pack_points"] == DEFAULT_EMPTY
    assert card["ability_name"] == DEFAULT_EMPTY
    assert card["ability_effect"] == "Put 1 random Basic Pokemon from your deck into your hand."
    assert card["move1_name"] == DEFAULT_EMPTY
    assert card["move1_cost"] == DEFAULT_EMPTY
    assert card["move1_damage"] == DEFAULT_EMPTY
    assert card["move1_effect"] == DEFAULT_EMPTY
    assert card["move2_name"] == DEFAULT_EMPTY
    assert card["move2_cost"] == DEFAULT_EMPTY
    assert card["move2_damage"] == DEFAULT_EMPTY
    assert card["move2_effect"] == DEFAULT_EMPTY
    assert card["image"] == "https://img.game8.co/3998351/d2ca1646332bd0640346f06449f4d942.png/show"
    assert card["url"] == "https://game8.co/games/Pokemon-TCG-Pocket/archives/476292"
