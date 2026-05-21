"""Tests for tcg.enrich.derived_fields and tcg.enrich.patches.

All tests use embedded fixture DataFrames – no network calls are made.
"""
import pandas as pd
import pytest

from tcg.enrich.derived_fields import (
    apply_energy_symbols,
    clear_trainer_move_fields,
    convert_ex_field,
    enrich_cards,
    fix_pokemon_type,
)
from tcg.enrich.patches import PATCHES, apply_patches
from tcg.utils import ENERGY_SYMBOLS


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _row(**overrides) -> dict:
    base: dict = {
        "id": "A1 001",
        "name": "Bulbasaur",
        "card_type": "Pokemon",
        "pokemon_type": "Grass",
        "hp": "70",
        "ex": "",
        "stage": "Basic",
        "rarity": "◇",
        "set": "Genetic Apex (A1)",
        "subset": "Mewtwo",
        "ability_name": None,
        "ability_effect": None,
        "move1_name": "Vine Whip",
        "move1_cost": "Grass:Colorless",
        "move1_damage": "40",
        "move1_description": None,
        "move2_name": None,
        "move2_cost": None,
        "move2_damage": None,
        "move2_description": None,
        "image": "https://img.game8.co/image.png/show",
        "page": "https://game8.co/archives/476002",
    }
    base.update(overrides)
    return base


def _df(**overrides) -> pd.DataFrame:
    return pd.DataFrame([_row(**overrides)])


# ---------------------------------------------------------------------------
# apply_energy_symbols
# ---------------------------------------------------------------------------


class TestApplyEnergySymbols:
    def test_single_grass_type(self):
        df = apply_energy_symbols(_df(move1_cost="Grass"))
        assert df.iloc[0]["move1_cost"] == ENERGY_SYMBOLS["Grass"]

    def test_colon_separator(self):
        df = apply_energy_symbols(_df(move1_cost="Grass:Colorless"))
        result = df.iloc[0]["move1_cost"]
        assert ENERGY_SYMBOLS["Grass"] in result
        assert ENERGY_SYMBOLS["Colorless"] in result

    def test_two_colorless_tokens(self):
        df = apply_energy_symbols(_df(move1_cost="Colorless 2"))
        assert df.iloc[0]["move1_cost"] == ENERGY_SYMBOLS["Colorless"] * 2

    def test_fire_type(self):
        df = apply_energy_symbols(_df(move1_cost="Fire"))
        assert df.iloc[0]["move1_cost"] == ENERGY_SYMBOLS["Fire"]

    def test_none_cost_becomes_empty_string(self):
        df = apply_energy_symbols(_df(move1_cost=None))
        assert df.iloc[0]["move1_cost"] == ""

    def test_empty_string_cost_stays_empty(self):
        df = apply_energy_symbols(_df(move1_cost=""))
        assert df.iloc[0]["move1_cost"] == ""

    def test_move2_cost_converted(self):
        df = apply_energy_symbols(_df(move2_cost="Water"))
        assert df.iloc[0]["move2_cost"] == ENERGY_SYMBOLS["Water"]

    def test_does_not_mutate_input(self):
        original = _df(move1_cost="Fire")
        original_val = original.iloc[0]["move1_cost"]
        apply_energy_symbols(original)
        assert original.iloc[0]["move1_cost"] == original_val


# ---------------------------------------------------------------------------
# convert_ex_field
# ---------------------------------------------------------------------------


class TestConvertExField:
    def test_empty_ex_pokemon_becomes_1(self):
        df = convert_ex_field(_df(ex="", card_type="Pokemon"))
        assert df.iloc[0]["ex"] == 1

    def test_ex_string_becomes_2(self):
        df = convert_ex_field(_df(ex="ex", card_type="Pokemon"))
        assert df.iloc[0]["ex"] == 2

    def test_mega_evolution_ex_becomes_3(self):
        df = convert_ex_field(_df(ex="Mega Evolution ex", card_type="Pokemon"))
        assert df.iloc[0]["ex"] == 3

    def test_trainer_card_becomes_0(self):
        df = convert_ex_field(_df(ex="", card_type="Trainer"))
        assert df.iloc[0]["ex"] == 0

    def test_item_card_becomes_0(self):
        df = convert_ex_field(_df(ex="", card_type="Item"))
        assert df.iloc[0]["ex"] == 0

    def test_does_not_mutate_input(self):
        original = _df(ex="ex", card_type="Pokemon")
        original_val = original.iloc[0]["ex"]
        convert_ex_field(original)
        assert original.iloc[0]["ex"] == original_val


# ---------------------------------------------------------------------------
# fix_pokemon_type
# ---------------------------------------------------------------------------


class TestFixPokemonType:
    def test_tool_renamed_to_pokemon_tool(self):
        df = fix_pokemon_type(_df(pokemon_type="Tool"))
        assert df.iloc[0]["pokemon_type"] == "Pokemon Tool"

    def test_grass_unchanged(self):
        df = fix_pokemon_type(_df(pokemon_type="Grass"))
        assert df.iloc[0]["pokemon_type"] == "Grass"

    def test_fire_unchanged(self):
        df = fix_pokemon_type(_df(pokemon_type="Fire"))
        assert df.iloc[0]["pokemon_type"] == "Fire"

    def test_does_not_mutate_input(self):
        original = _df(pokemon_type="Tool")
        original_val = original.iloc[0]["pokemon_type"]
        fix_pokemon_type(original)
        assert original.iloc[0]["pokemon_type"] == original_val


# ---------------------------------------------------------------------------
# clear_trainer_move_fields
# ---------------------------------------------------------------------------


class TestClearTrainerMoveFields:
    def test_supporter_move1_cost_cleared(self):
        df = clear_trainer_move_fields(_df(card_type="Supporter", move1_cost="🟢"))
        assert df.iloc[0]["move1_cost"] == ""

    def test_item_move2_cost_cleared(self):
        df = clear_trainer_move_fields(
            _df(card_type="Item", move2_cost="🔴")
        )
        assert df.iloc[0]["move2_cost"] == ""

    def test_pokemon_tool_stage_cleared(self):
        df = clear_trainer_move_fields(_df(card_type="Pokemon Tool", stage="Basic"))
        assert df.iloc[0]["stage"] == ""

    def test_pokemon_card_move_cost_preserved(self):
        df = clear_trainer_move_fields(_df(card_type="Pokemon", move1_cost="🟢"))
        assert df.iloc[0]["move1_cost"] == "🟢"

    def test_pokemon_card_stage_preserved(self):
        df = clear_trainer_move_fields(_df(card_type="Pokemon", stage="Stage 1"))
        assert df.iloc[0]["stage"] == "Stage 1"

    def test_does_not_mutate_input(self):
        original = _df(card_type="Item", move1_cost="🟢")
        original_val = original.iloc[0]["move1_cost"]
        clear_trainer_move_fields(original)
        assert original.iloc[0]["move1_cost"] == original_val


# ---------------------------------------------------------------------------
# apply_patches
# ---------------------------------------------------------------------------


class TestApplyPatches:
    def test_patch_applied_when_id_matches(self):
        patches = {"A1 001": {"hp": "999"}}
        df = apply_patches(_df(id="A1 001", hp="50"), patches=patches)
        assert str(df.iloc[0]["hp"]) == "999"

    def test_missing_patch_target_silently_skipped(self):
        patches = {"MISSING 999": {"hp": "99"}}
        df = apply_patches(_df(id="A1 001"), patches=patches)
        assert df.iloc[0]["id"] == "A1 001"

    def test_bad_field_name_silently_skipped(self):
        patches = {"A1 001": {"nonexistent_field": "value"}}
        df = apply_patches(_df(id="A1 001"), patches=patches)
        assert "nonexistent_field" not in df.columns

    def test_does_not_mutate_input(self):
        patches = {"A1 001": {"name": "Modified"}}
        original = _df(id="A1 001", name="Bulbasaur")
        original_name = original.iloc[0]["name"]
        apply_patches(original, patches=patches)
        assert original.iloc[0]["name"] == original_name

    def test_empty_patches_no_change(self):
        original = _df(id="A1 001", name="Bulbasaur")
        df = apply_patches(original, patches={})
        assert df.iloc[0]["name"] == "Bulbasaur"

    def test_default_patches_a4_177_hp(self):
        """The known A4 177 hp patch must be in PATCHES and correct the value."""
        assert "A4 177" in PATCHES
        assert "hp" in PATCHES["A4 177"]
        df = apply_patches(_df(id="A4 177", hp="100"))
        assert str(df.iloc[0]["hp"]) == PATCHES["A4 177"]["hp"]


# ---------------------------------------------------------------------------
# enrich_cards (integration / wrapper)
# ---------------------------------------------------------------------------


class TestEnrichCards:
    def test_pokemon_ex_converted(self):
        df = enrich_cards(_df(id="A1 004", card_type="Pokemon", ex="ex"))
        assert df.iloc[0]["ex"] == 2

    def test_pokemon_without_ex_is_1(self):
        df = enrich_cards(_df(card_type="Pokemon", ex=""))
        assert df.iloc[0]["ex"] == 1

    def test_trainer_ex_is_0(self):
        df = enrich_cards(_df(card_type="Supporter", ex=""))
        assert df.iloc[0]["ex"] == 0

    def test_move_cost_symbols_applied(self):
        df = enrich_cards(_df(move1_cost="Grass:Colorless"))
        result = df.iloc[0]["move1_cost"]
        assert ENERGY_SYMBOLS["Grass"] in result

    def test_tool_type_normalised(self):
        df = enrich_cards(_df(pokemon_type="Tool"))
        assert df.iloc[0]["pokemon_type"] == "Pokemon Tool"

    def test_trainer_move_cost_cleared(self):
        df = enrich_cards(_df(card_type="Item", move1_cost="Fire", stage="Basic"))
        assert df.iloc[0]["move1_cost"] == ""
        assert df.iloc[0]["stage"] == ""
