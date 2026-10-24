import csv
import json

from tcg import fetch, pipeline
from tcg.config import COLUMNS
from tcg.validation import (
    audit_overrides,
    find_battle_attribute_mismatches,
    missing_required_fields,
    validate_csv_file,
    write_validation_log,
)
from tcg.overrides import OVERRIDES, apply_overrides
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
        rows = {r["id"]: r for r in reader}

    bulb = rows["A1 001"]
    assert (bulb["weakness"], bulb["retreat_cost"], bulb["generation"]) == ("Fire", "2", "1")
    assert bulb["illustrator"] == "Narumi Sato" and bulb["pack_points"] == "35"
    assert bulb["move2_name"] == ""  # None is written as an empty cell

    assert rows["A1 183"]["move1_damage"] == "40"  # override beat the JSON's 70


def test_assign_base_ids_uses_first_matching_signature():
    cards = [
        {"id": "A1 055", "name": "Blastoise", "hp": "150", "move1_name": "Hydro Pump"},
        {"id": "P-A 029", "name": "Blastoise", "hp": "150", "move1_name": "Hydro Pump"},
        {"id": "B1a 019", "name": "Blastoise", "hp": "150", "move1_name": "Double Splash"},
        {"id": "B1a 020", "name": "Mega Blastoise ex", "hp": "230", "move1_name": "Triple Bombardment"},
        {"id": "B1a 084", "name": "Mega Blastoise ex", "hp": "230", "move1_name": "Triple Bombardment"},
    ]

    pipeline.assign_base_ids(cards)

    assert cards[0]["base_id"] == "A1 055"
    assert cards[1]["base_id"] == "A1 055"
    assert cards[2]["base_id"] == "B1a 019"
    assert cards[4]["base_id"] == "B1a 020"


def test_sort_cards_uses_set_order_and_card_number():
    cards = [
        {"id": "P-A 002"},
        {"id": "A2b 010"},
        {"id": "A1 002"},
        {"id": "A1 001"},
    ]

    pipeline.sort_cards(cards)

    assert [card["id"] for card in cards] == [
        "A1 001", "A1 002", "A2b 010", "P-A 002"
    ]


def test_assign_indexes_is_one_based():
    cards = [{"id": "A1 001"}, {"id": "A1 002"}]

    pipeline.assign_indexes(cards)

    assert [card["index"] for card in cards] == ["1", "2"]


def test_failed_page_does_not_stop_the_run(tmp_path, monkeypatch):
    json_path = _write_json(tmp_path, [BULBASAUR])
    monkeypatch.setattr(pipeline, "FAILED_PAGES_PATH", tmp_path / "failed.txt")

    def boom(url, **kw):
        raise RuntimeError("network down")

    monkeypatch.setattr(fetch, "get_card_html", boom)
    cards = pipeline.build_cards(json_path=json_path, workers=1, delay=0)

    assert cards[0]["name"] == "Bulbasaur" and cards[0]["generation"] is None
    assert "A1 001" in (tmp_path / "failed.txt").read_text()


def test_required_fields_depend_on_card_category():
    pokemon = {"category": "Pokemon", "id": "A1 001", "move1_name": ""}
    trainer = {"category": "Trainer", "id": "A1 223", "ability_effect": ""}

    assert missing_required_fields(pokemon) == [
        "base_id", "name", "rarity", "type", "generation", "illustrator",
        "expansion", "pack_name", "image", "url", "stage", "hp",
        "retreat_cost", "ko", "move1_name", "move1_cost",
    ]
    assert missing_required_fields(trainer) == [
        "base_id", "name", "rarity", "type", "generation", "illustrator",
        "expansion", "pack_name", "image", "url", "ability_effect",
    ]


def test_pipeline_writes_pre_override_validation_log(tmp_path):
    card = {
        "id": "A1 001",
        "name": "Bulbasaur",
        "category": "Pokemon",
        "move1_name": "",
    }
    log_path = tmp_path / "validation.log"
    findings = write_validation_log([card], log_path)

    assert ("A1 001", "Bulbasaur", "move1_name") in findings
    assert "A1 001\tBulbasaur\tmove1_name" in log_path.read_text()


def test_validation_log_can_describe_final_stage(tmp_path):
    log_path = tmp_path / "validation_final.log"
    findings = write_validation_log(
        [{"id": "A1 001", "name": "Bulbasaur", "category": "Pokemon"}],
        log_path,
        stage="Final",
    )

    assert findings
    assert log_path.read_text().startswith("Final required-field validation")


def test_base_id_battle_attributes_must_match():
    cards = [
        {
            "id": "A1 001",
            "base_id": "A1 001",
            "stage": "Basic",
            "type": "Grass",
            "move1_name": "Tackle",
        },
        {
            "id": "P-A 001",
            "base_id": "A1 001",
            "stage": "Stage 1",
            "type": "Grass",
            "move1_name": "Tackle",
        },
    ]

    assert find_battle_attribute_mismatches(cards) == [
        ("A1 001", "P-A 001", "stage", "Basic", "Stage 1"),
    ]


def test_validation_log_includes_base_id_battle_mismatches(tmp_path):
    log_path = tmp_path / "validation.log"
    cards = [
        {"id": "A1 001", "base_id": "A1 001", "type": "Grass"},
        {"id": "P-A 001", "base_id": "A1 001", "type": "Fire"},
    ]

    findings = write_validation_log(cards, log_path)

    assert ("A1 001", "P-A 001", "type", "Grass", "Fire") in findings
    assert "base_id\tcard_id\tattribute\tcanonical_value\tcard_value" in log_path.read_text()
    assert "A1 001\tP-A 001\ttype\tGrass\tFire" in log_path.read_text()


def test_validate_csv_file_reads_final_output(tmp_path):
    csv_path = tmp_path / "full.csv"
    csv_path.write_text(
        "id,name,category\nA1 001,Bulbasaur,Pokemon\n", encoding="utf-8"
    )
    log_path = tmp_path / "validation_final.log"

    findings = validate_csv_file(csv_path, log_path)

    assert ("A1 001", "Bulbasaur", "base_id") in findings
    assert log_path.read_text().startswith("Final required-field validation")


def test_override_audit_classifies_source_values(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "tcg.validation.OVERRIDES",
        {
            "A1 001": {
                "stage": "Basic",
                "illustrator": "Narumi Sato",
                "hp": "70",
            }
        },
    )
    cards = [
        {
            "id": "A1 001",
            "name": "Bulbasaur",
            "stage": "Basic",
            "illustrator": "Other Artist",
            "hp": None,
        }
    ]
    counts = audit_overrides(cards, tmp_path / "override_audit.log")

    assert counts == {
        "REDUNDANT": 1,
        "FILLING_MISSING": 1,
        "ACTIVE_CORRECTION": 1,
        "CARD_NOT_FOUND": 0,
    }
    report = (tmp_path / "override_audit.log").read_text()
    assert "REDUNDANT\tA1 001\tBulbasaur\tstage\tBasic" in report
    assert "FILLING_MISSING\tA1 001\tBulbasaur\thp\t<missing>" in report
    assert "ACTIVE_CORRECTION\tA1 001\tBulbasaur\tillustrator\tOther Artist" in report


def test_build_cards_can_skip_manual_overrides(tmp_path, monkeypatch):
    json_path = _write_json(tmp_path, [BULBASAUR])
    monkeypatch.setattr(fetch, "get_card_html", lambda url, **kw: page(ATTACK_ONLY))
    monkeypatch.setattr(
        pipeline,
        "apply_overrides",
        lambda card: card.update({"hp": "999"}),
    )

    source_cards = pipeline.build_cards(
        json_path=json_path,
        workers=1,
        delay=0,
        apply_manual_overrides=False,
    )

    assert source_cards[0]["hp"] == "70"


def test_multi_field_override_stays_grouped():
    assert OVERRIDES["B3 031"] == {
        "move1_cost": "🔴",
        "move1_damage": "20",
    }

    card = {"id": "B3 031", "move1_cost": "?", "move1_damage": None}
    apply_overrides(card)

    assert card["move1_cost"] == "🔴"
    assert card["move1_damage"] == "20"
