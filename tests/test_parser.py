from bs4 import BeautifulSoup
from tcg_extract.parser import extract_card
from tests.debug import debug_card_extract


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
    
    card = debug_card_extract("A1 001")

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
    assert card["move1_effect"] == "N/A"
    assert card["move2_name"] == "N/A"
    assert card["move2_cost"] == "N/A"
    assert card["move2_damage"] == "N/A"
    assert card["move2_effect"] == "N/A"
    assert card["retreat_cost"] == "1"
    assert card["pack_name"] == "Genetic Apex (A1) Mewtwo"
    assert card["pack_points"] == "35"
    assert card["image"] == "https://img.game8.co/3998332/91c4f79b2b3b4206205bf69db8dd3d1e.png/show"


def test_extract_card_pokemon_two_attacks():
    """Testing `A1 004` (Venusaur ex)"""
    html = """
    <tr>
        <td class="center"><input type="checkbox" id="checkbox1_4"></td>
        <td class="center"><b class="a-bold">A1 004</b></td>

        <td class="center">
        <div class="imageLink js-archive-open-image-modal"
            data-image-url="https://img.game8.co/3995580/151d2c9455f83899618147d85881a75e.png/original"
            data-micromodal-trigger="js-archive-open-image-modal" data-archive-url><img
            src="https://img.game8.co/3995580/151d2c9455f83899618147d85881a75e.png/show"
            class="a-img lazy lazy-non-square lazy-loaded"
            alt="Pokemon TCG Pocket - A1 004 Venusaur ex"
            data-src="https://img.game8.co/3995580/151d2c9455f83899618147d85881a75e.png/show"
            width="172"
            style="height: 0; padding-bottom: calc(px*240/172); padding-bottom: calc(min(100%,172px)*240/172);"
            data-loaded="true"><span class="imageLink__icon"></span></div> <a class="a-link"
            href="https://game8.co/games/Pokemon-TCG-Pocket/archives/476005">Venusaur ex</a>

        </td>

        <td class="center"><img
            src="https://img.game8.co/3995617/622e1c0cca9ffdaa43cdd588b8e18d78.png/show"
            class="a-img lazy lazy-non-square lazy-loaded" alt="Pokemon TCG Pocket - ◇◇◇◇ rarity"
            data-src="https://img.game8.co/3995617/622e1c0cca9ffdaa43cdd588b8e18d78.png/show"
            width="74"
            style="height: 0; padding-bottom: calc(px*25/74); padding-bottom: calc(min(100%,74px)*25/74);"
            data-loaded="true">
        <hr class="a-table__line">◇◇◇◇
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

        <td class="center"> 190 </td>

        <td class="center"> Stage 2 </td>

        <td class="center">500 Pts </td>
        <td class="left">
        <br> <b class="a-bold">Stage</b>: Stage 2 <br>
        <div class="align"> <b class="a-bold">Retreat Cost</b>: <img
            src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
            class="a-img lazy lazy-non-square" alt="Pokemon TCG Pocket - Retreat Cost"
            data-src="https://img.game8.co/3998539/6bb558f97aac02e469e3ddc06e2ac167.png/show"
            width="60"
            style="height: 0; padding-bottom: calc(px*20/60); padding-bottom: calc(min(100%,60px)*20/60);">
        </div>
        <hr class="a-table__line">

        <div class="align"> <b class="a-bold">Razor Leaf</b>

            <a class="a-link" href="https://game8.co/games/Pokemon-TCG-Pocket/archives/476531"><img
                src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                class="a-img lazy"
                alt="Grass"
                data-src="https://img.game8.co/4018726/c2d96eaebb6cd06d6a53dfd48da5341c.png/show"
                width="15"
                height="15"></a>

            <a class="a-link" href="https://game8.co/games/Pokemon-TCG-Pocket/archives/476389"><img
                src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                class="a-img lazy lazy-non-square" alt="Colorless 2"
                data-src="https://img.game8.co/3998538/eea8469456d6b7ea7a2daf2995087d00.png/show"
                width="30"
                style="height: 0; padding-bottom: calc(px*15/30); padding-bottom: calc(min(100%,30px)*15/30);"></a>

        </div>
        60 <br>

        <div class="align"> <b class="a-bold">Giant Bloom</b>

            <a class="a-link" href="https://game8.co/games/Pokemon-TCG-Pocket/archives/476531"><img
                src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                class="a-img lazy lazy-non-square" alt="Grass 2"
                data-src="https://img.game8.co/3998531/579b7f81ac7b52e36dd4e8b52a9d2da8.png/show"
                width="30"
                style="height: 0; padding-bottom: calc(px*15/30); padding-bottom: calc(min(100%,30px)*15/30);"></a>

            <a class="a-link" href="https://game8.co/games/Pokemon-TCG-Pocket/archives/476389"><img
                src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                class="a-img lazy lazy-non-square" alt="Colorless 2"
                data-src="https://img.game8.co/3998538/eea8469456d6b7ea7a2daf2995087d00.png/show"
                width="30"
                style="height: 0; padding-bottom: calc(px*15/30); padding-bottom: calc(min(100%,30px)*15/30);"></a>

        </div>
        100 <br>
        Heal 30 damage from this Pokemon.

        </td>
        <td class="left">Open Genetic Apex (A1) Mewtwo packs</td>
    </tr>
    """
    row = BeautifulSoup(html, "lxml").find("tr")
    card = extract_card(row)

    assert card["number"] == "A1 004"
    assert card["name"] == "Venusaur ex"
    assert card["rarity"] == "◇◇◇◇"
    assert card["stage"] == "Stage 2"
    assert card["HP"] == "190"
    assert card["type"] == "Grass"
    assert card["move1_name"] == "Razor Leaf"
    assert card["move1_cost"] == "🟢*️⃣*️⃣"
    assert card["move1_damage"] == "60"
    assert card["move1_effect"] == "N/A"
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
    html = """
      <tr>
        <td class="center"><input type="checkbox" id="checkbox1_47"></td>
        <td class="center"><b class="a-bold">A1 047</b></td>

        <td class="center">
          <div class="imageLink js-archive-open-image-modal"
            data-image-url="https://img.game8.co/3998342/21cb0fbf6aa4a791867a2c21ff9add20.png/original"
            data-micromodal-trigger="js-archive-open-image-modal" data-archive-url><img
              src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
              class="a-img lazy lazy-non-square" alt="Pokemon TCG Pocket - A1 047 Moltres ex"
              data-src="https://img.game8.co/3998342/21cb0fbf6aa4a791867a2c21ff9add20.png/show"
              width="172"
              style="height: 0; padding-bottom: calc(px*240/172); padding-bottom: calc(min(100%,172px)*240/172);"><span
              class="imageLink__icon"></span></div> <a class="a-link"
            href="https://game8.co/games/Pokemon-TCG-Pocket/archives/476048">Moltres ex</a>

        </td>

        <td class="center"><img
            src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
            class="a-img lazy lazy-non-square" alt="Pokemon TCG Pocket - ◇◇◇◇ rarity"
            data-src="https://img.game8.co/3995617/622e1c0cca9ffdaa43cdd588b8e18d78.png/show"
            width="74"
            style="height: 0; padding-bottom: calc(px*25/74); padding-bottom: calc(min(100%,74px)*25/74);">
          <hr class="a-table__line">◇◇◇◇
        </td>

        <td class="center"><img
            src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
            class="a-img lazy" alt="Pokemon TCG Pocket - Charizard Booster Pack"
            data-src="https://img.game8.co/3999185/6405ea32582539f6e270b2b15529d130.png/show"
            width="50" height="50">
          <br> <b class="a-bold">Genetic Apex (A1)</b> <br> Charizard
        </td>

        <td class="center"><img
            src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
            class="a-img lazy" alt="Pokemon TCG Pocket - Fire"
            data-src="https://img.game8.co/3994715/1a36293e91b194645e3977ace96e446e.png/show"
            width="40" height="40">
        </td>

        <td class="center"> 140 </td>

        <td class="center"> Basic </td>

        <td class="center">500 Pts </td>
        <td class="left">
          <br> <b class="a-bold">Stage</b>: Basic <br>
          <div class="align"> <b class="a-bold">Retreat Cost</b>: <img
              src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
              class="a-img lazy lazy-non-square" alt="Pokemon TCG Pocket - Retreat Cost"
              data-src="https://img.game8.co/3998538/eea8469456d6b7ea7a2daf2995087d00.png/show"
              width="40"
              style="height: 0; padding-bottom: calc(px*20/40); padding-bottom: calc(min(100%,40px)*20/40);">
          </div>
          <hr class="a-table__line">

          <div class="align"> <b class="a-bold">Inferno Dance</b>

            <a class="a-link" href="https://game8.co/games/Pokemon-TCG-Pocket/archives/476411"><img
                src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                class="a-img lazy"
                alt="Fire"
                data-src="https://img.game8.co/4018725/13914d1a973822da2863205cffe8d814.png/show"
                width="15"
                height="15"></a>

          </div>
          <br>
          Flip 3 coins. Take an amount of Fire Energy from your Energy Zone equal to the number of
          heads and attach it
          to your Benched Fire Pokemon in any way you like.

          <div class="align"> <b class="a-bold">Heat Blast</b>

            <a class="a-link" href="https://game8.co/games/Pokemon-TCG-Pocket/archives/476411"><img
                src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                class="a-img lazy"
                alt="Fire"
                data-src="https://img.game8.co/4018725/13914d1a973822da2863205cffe8d814.png/show"
                width="15"
                height="15"></a>

            <a class="a-link" href="https://game8.co/games/Pokemon-TCG-Pocket/archives/476389"><img
                src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                class="a-img lazy lazy-non-square" alt="Colorless 2"
                data-src="https://img.game8.co/3998538/eea8469456d6b7ea7a2daf2995087d00.png/show"
                width="30"
                style="height: 0; padding-bottom: calc(px*15/30); padding-bottom: calc(min(100%,30px)*15/30);"></a>

          </div>
          70 <br>

        </td>
        <td class="left">Open Genetic Apex (A1) Charizard packs</td>
      </tr>
    """
    row = BeautifulSoup(html, "lxml").find("tr")
    card = extract_card(row)

    assert card["number"] == "A1 047"
    assert card["name"] == "Moltres ex"
    assert card["rarity"] == "◇◇◇◇"
    assert card["stage"] == "Basic"
    assert card["HP"] == "140"
    assert card["type"] == "Fire"
    assert card["move1_name"] == "Inferno Dance"
    assert card["move1_cost"] == "🔴"
    assert card["move1_damage"] == "N/A"
    assert (
        card["move1_effect"]
        == "Flip 3 coins. Take an amount of Fire Energy from your Energy Zone equal to the number of heads and attach it to your Benched Fire Pokemon in any way you like."
    )
    assert card["move2_name"] == "Heat Blast"
    assert card["move2_cost"] == "🔴*️⃣*️⃣"
    assert card["move2_damage"] == "70"
    assert card["move2_effect"] == "N/A"
    assert card["retreat_cost"] == "2"
    assert card["pack_name"] == "Genetic Apex (A1) Charizard"
    assert card["pack_points"] == "500"
    assert card["image"] == "https://img.game8.co/3998342/21cb0fbf6aa4a791867a2c21ff9add20.png/show"

def test_extract_card_pokemon_dynamic_dmg():
    """Testing `A1 026` (Pinsir)"""
    card = debug_card_extract("A1 026")

    assert card["number"] == "A1 026"
    assert card["name"] == "Pinsir"
    assert card["rarity"] == "◇◇"
    assert card["stage"] == "Basic"
    assert card["HP"] == "90"
    assert card["type"] == "Grass"
    assert card["move1_name"] == "Double Horn"
    assert card["move1_cost"] == "🟢🟢"
    assert card["move1_damage"] == "50x"
    assert (
        card["move1_effect"]
        == "Flip 2 coins. This attack does 50 damage for each heads."
    )
    assert card["move2_name"] == "N/A"
    assert card["move2_cost"] == "N/A"
    assert card["move2_damage"] == "N/A"
    assert card["move2_effect"] == "N/A"
    assert card["retreat_cost"] == "2"
    assert card["pack_name"] == "Genetic Apex (A1) Any"
    assert card["pack_points"] == "70"
    assert card["image"] == "https://img.game8.co/3998396/85716016d8d17502c3856d4d2c2276aa.png/show"


def test_extract_card_pokemon_ability():
    """Testing `A1 007` (Butterfree)"""
    card = debug_card_extract("A1 007")

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
    assert card["move1_name"] == "N/A"
    assert card["move1_cost"] == "N/A"
    assert card["move1_damage"] == "N/A"
    assert card["move1_effect"] == "N/A"
    assert card["move2_name"] == "Gust"
    assert card["move2_cost"] == "🟢*️⃣*️⃣"
    assert card["move2_damage"] == "60"
    assert card["move2_effect"] == "N/A"
    assert card["retreat_cost"] == "1"
    assert card["pack_name"] == "Genetic Apex (A1) Pikachu"
    assert card["pack_points"] == "150"
    assert card["image"] == "https://img.game8.co/4004057/6ba461fb08292cbabe715b6ead54dfb9.png/show"


def test_extract_card_fossil():
    """Testing `A1 216` (Helix Fossil)"""
    card = debug_card_extract("A1 216")

    assert card["number"] == "A1 216"
    assert card["name"] == "Helix Fossil"
    assert card["rarity"] == "◇"
    assert card["stage"] == "N/A"
    assert card["HP"] == "N/A"
    assert card["type"] == "Item"
    assert card["ability_name"] == "N/A"
    assert (
        card["ability_effect"]
        == "Play this card as if it were a 40-HP Basic Colorless Pokemon. At any time during your turn, you may discard this card from play. This card can't retreat."
    )
    assert card["move1_name"] == "N/A"
    assert card["move1_cost"] == "N/A"
    assert card["move1_damage"] == "N/A"
    assert card["move1_effect"] == "N/A"
    assert card["move2_name"] == "N/A"
    assert card["move2_cost"] == "N/A"
    assert card["move2_damage"] == "N/A"
    assert card["move2_effect"] == "N/A"
    assert card["retreat_cost"] == "N/A"
    assert card["pack_name"] == "Genetic Apex (A1) Pikachu"
    assert card["pack_points"] == "35"
    assert card["image"] == "https://img.game8.co/4004042/6f1a71c0a509b36ccf7dd29bf8bfa967.png/show"


def test_extract_card_supporter():
    """Testing `A1 219` (Erika)"""
    card = debug_card_extract("A1 219")

    assert card["number"] == "A1 219"
    assert card["name"] == "Erika"
    assert card["rarity"] == "◇◇"
    assert card["stage"] == "N/A"
    assert card["HP"] == "N/A"
    assert card["type"] == "Supporter"
    assert card["ability_name"] == "N/A"
    assert card["ability_effect"] == "Heal 50 damage from 1 of your Grass Pokemon."
    assert card["move1_name"] == "N/A"
    assert card["move1_cost"] == "N/A"
    assert card["move1_damage"] == "N/A"
    assert card["move1_effect"] == "N/A"
    assert card["move2_name"] == "N/A"
    assert card["move2_cost"] == "N/A"
    assert card["move2_damage"] == "N/A"
    assert card["move2_effect"] == "N/A"
    assert card["retreat_cost"] == "N/A"
    assert card["pack_name"] == "Genetic Apex (A1) Charizard"
    assert card["pack_points"] == "70"
    assert card["image"] == "https://img.game8.co/3995535/5bc1164c2b9a79f4c40f21a8975adbb3.png/show"


def test_extract_card_full_art_supporter():
    """Testing `A1 269` (Full Art Koga)"""
    card = debug_card_extract("A1 269")

    assert card["number"] == "A1 269"
    assert card["name"] == "Koga"
    assert card["rarity"] == "☆☆"
    assert card["stage"] == "N/A"
    assert card["HP"] == "N/A"
    assert card["type"] == "Supporter"
    assert card["ability_name"] == "N/A"
    assert card["ability_effect"] == "Put your Muk or Weezing in the Active Spot into your hand."
    assert card["move1_name"] == "N/A"
    assert card["move1_cost"] == "N/A"
    assert card["move1_damage"] == "N/A"
    assert card["move1_effect"] == "N/A"
    assert card["move2_name"] == "N/A"
    assert card["move2_cost"] == "N/A"
    assert card["move2_damage"] == "N/A"
    assert card["move2_effect"] == "N/A"
    assert card["retreat_cost"] == "N/A"
    assert card["pack_name"] == "Genetic Apex (A1) Mewtwo"
    assert card["pack_points"] == "1250"
    assert card["image"] == "https://img.game8.co/4004062/0c2bbaf7e3e34c46d1593b6780108de9.png/show"
