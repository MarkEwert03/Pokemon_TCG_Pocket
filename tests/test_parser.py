from tcg_extract.parser import extract_card
from bs4 import BeautifulSoup


def test_extract_card_sample():
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

    expected_keys = {
        "number",
        "name",
        "image",
        "rarity",
        "stage",
        "HP",
        "type",
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
    }
    assert set(card.keys()) == expected_keys
    assert card["number"] == "A1 001"
    assert card["name"] == "Bulbasaur"
    assert card["image"] == "https://img.game8.co/3998332/91c4f79b2b3b4206205bf69db8dd3d1e.png/show"
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
