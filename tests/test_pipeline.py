import csv
import json

from tcg import fetch, pipeline
from tcg.config import COLUMNS
from tests.test_card_page import ATTACK_ONLY, page
from tests.test_from_json import BULBASAUR, EMPTY_MOVE


def _write_json(tmp_path, cards):
    path = tmp_path / "cards.json"
    path.write_text(json.dumps({"cardArraySchema": {"cards": cards}}), encoding="utf-8")
    return path


def test_end_to_end(tmp_path, monkeypatch):
    # A card that has a manual override (Dratini's damage) plus a normal one
    dratini = {**BULBASAUR, "id": "A1 183", "name": "Dratini", "moves": [
        {"name": "Ram", "damage": "70", "energy_cost": "Colorless", "description": ""}, EMPTY_MOVE]}
    json_path = _write_json(tmp_path, [BULBASAUR, dratini])

    monkeypatch.setattr(fetch, "get_card_html", lambda url, **kw: page(ATTACK_ONLY))

    out = tmp_path / "full.csv"
    pipeline.run(output_file=out, json_path=json_path, workers=1, delay=0)

    with open(out, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == COLUMNS
        rows = {r["number"]: r for r in reader}

    bulb = rows["A1 001"]
    assert (bulb["weakness"], bulb["retreat_cost"], bulb["generation"]) == ("Fire", "2", "1")
    assert bulb["illustrator"] == "Narumi Sato" and bulb["pack_points"] == "35"
    assert bulb["move2_name"] == ""  # None is written as an empty cell

    assert rows["A1 183"]["move1_damage"] == "40"  # override beat the JSON's 70


def test_failed_page_does_not_stop_the_run(tmp_path, monkeypatch):
    json_path = _write_json(tmp_path, [BULBASAUR])
    monkeypatch.setattr(pipeline, "FAILED_PAGES_PATH", tmp_path / "failed.txt")

    def boom(url, **kw):
        raise RuntimeError("network down")

    monkeypatch.setattr(fetch, "get_card_html", boom)
    cards = pipeline.build_cards(json_path=json_path, workers=1, delay=0)

    assert cards[0]["name"] == "Bulbasaur" and cards[0]["generation"] is None
    assert "A1 001" in (tmp_path / "failed.txt").read_text()
