"""Tests for tcg.normalize.base_schema.

All tests use embedded fixture data – no network calls are made.
"""
import pandas as pd
import pytest

from tcg.normalize.base_schema import (
    BASE_COLUMNS,
    flatten_to_base_table,
    normalize_base_types,
)

# ---------------------------------------------------------------------------
# Shared fixture payload
# ---------------------------------------------------------------------------

SAMPLE_RAW: dict = {
    "cardArraySchema": {
        "cards": [
            {
                "id": "A1 001",
                "name": "Bulbasaur",
                "card_type": "Pokemon",
                "pokemon_type": "Grass",
                "hp": "70",
                "ex": "",
                "evolution_stage": "Basic",
                "rarity": "◇",
                "set": "Genetic Apex (A1)",
                "subset": "Mewtwo",
                "ability": "",
                "image_url": "https://img.game8.co/image.png/show",
                "archive_url": "https://game8.co/games/Pokemon-TCG-Pocket/archives/476002",
                "trainer_type": "Basic",
                "owned": False,
                "moves": [
                    {
                        "name": "Vine Whip",
                        "damage": "40",
                        "energy_cost": "Grass:Colorless",
                        "description": "",
                    },
                    {"name": "", "damage": "", "energy_cost": "", "description": ""},
                    # Noisy 3rd slot with pack-drop data – must be discarded
                    {
                        "name": "",
                        "damage": "1.562% | 0.277% | 0% | 0%",
                        "energy_cost": "A1-M:A4b",
                        "description": "",
                    },
                ],
            },
            {
                "id": "A1 004",
                "name": "Venusaur ex",
                "card_type": "Pokemon",
                "pokemon_type": "Grass",
                "hp": "190",
                "ex": "ex",
                "evolution_stage": "Stage 2",
                "rarity": "◇◇◇◇",
                "set": "Genetic Apex (A1)",
                "subset": "Mewtwo",
                "ability": "",
                "image_url": "https://img.game8.co/image2.png/show",
                "archive_url": "https://game8.co/games/Pokemon-TCG-Pocket/archives/476005",
                "trainer_type": "Stage 2",
                "owned": False,
                "moves": [
                    {
                        "name": "Razor Leaf",
                        "damage": "60",
                        "energy_cost": "Grass:Colorless 2",
                        "description": "",
                    },
                    {
                        "name": "Giant Bloom",
                        "damage": "100",
                        "energy_cost": "Grass 2:Colorless 2",
                        "description": "Heal 30 damage from this Pokemon.",
                    },
                    {"name": "", "damage": "0%", "energy_cost": "A1-M:A4b", "description": ""},
                ],
            },
            {
                "id": "A1 007",
                "name": "Butterfree",
                "card_type": "Pokemon",
                "pokemon_type": "Grass",
                "hp": "120",
                "ex": "",
                "evolution_stage": "Stage 2",
                "rarity": "◇◇◇",
                "set": "Genetic Apex (A1)",
                "subset": "Pikachu",
                "ability": "Powder Heal",
                "image_url": "https://img.game8.co/image3.png/show",
                "archive_url": "https://game8.co/games/Pokemon-TCG-Pocket/archives/476008",
                "trainer_type": "Stage 2",
                "owned": False,
                "moves": [
                    {
                        "name": "Gust",
                        "damage": "60",
                        "energy_cost": "Grass:Colorless 2",
                        "description": "",
                    },
                    {"name": "", "damage": "", "energy_cost": "", "description": ""},
                    {"name": "", "damage": "", "energy_cost": "A1-P", "description": ""},
                ],
            },
            {
                "id": "A1 219",
                "name": "Erika",
                "card_type": "Trainer",
                "pokemon_type": "Supporter",
                "hp": "",
                "ex": "",
                "evolution_stage": "",
                "rarity": "◇◇",
                "set": "Genetic Apex (A1)",
                "subset": "Charizard",
                "ability": "",
                "image_url": "https://img.game8.co/image4.png/show",
                "archive_url": "https://game8.co/games/Pokemon-TCG-Pocket/archives/476272",
                "trainer_type": "",
                "owned": False,
                "moves": [],
            },
        ]
    }
}


# ---------------------------------------------------------------------------
# flatten_to_base_table
# ---------------------------------------------------------------------------


class TestFlattenToBaseTable:
    def test_returns_dataframe(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        assert isinstance(df, pd.DataFrame)

    def test_columns_match_base_columns(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        assert list(df.columns) == BASE_COLUMNS

    def test_row_count(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        assert len(df) == 4

    def test_bulbasaur_fields(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        row = df[df["id"] == "A1 001"].iloc[0]
        assert row["name"] == "Bulbasaur"
        assert row["card_type"] == "Pokemon"
        assert row["hp"] == "70"
        assert row["move1_name"] == "Vine Whip"
        assert row["move1_cost"] == "Grass:Colorless"
        assert row["move1_damage"] == "40"
        assert row["move2_name"] == ""

    def test_two_moves_extracted(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        row = df[df["id"] == "A1 004"].iloc[0]
        assert row["move1_name"] == "Razor Leaf"
        assert row["move2_name"] == "Giant Bloom"
        assert row["move2_description"] == "Heal 30 damage from this Pokemon."

    def test_noisy_third_move_discarded(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        # Percentage strings from the 3rd slot must never appear in move columns
        move_name_values = df["move1_name"].tolist() + df["move2_name"].tolist()
        assert all("%" not in str(v) for v in move_name_values)

    def test_trainer_card_empty_moves(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        row = df[df["id"] == "A1 219"].iloc[0]
        assert row["card_type"] == "Trainer"
        assert row["move1_name"] == ""
        assert row["move2_name"] == ""

    def test_empty_raw_returns_empty_df(self):
        df = flatten_to_base_table({})
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == BASE_COLUMNS

    def test_ability_name_mapped(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        row = df[df["id"] == "A1 007"].iloc[0]
        assert row["ability_name"] == "Powder Heal"
        # Ability cards still populate move1 with the first valid move
        assert row["move1_name"] == "Gust"

    def test_ability_effect_is_empty_placeholder(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        # ability_effect is not available in the structural JSON
        assert (df["ability_effect"] == "").all()

    def test_set_and_subset_mapped(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        row = df[df["id"] == "A1 001"].iloc[0]
        assert row["set"] == "Genetic Apex (A1)"
        assert row["subset"] == "Mewtwo"

    def test_image_and_page_mapped(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        row = df[df["id"] == "A1 001"].iloc[0]
        assert row["image"].startswith("https://")
        assert row["page"].startswith("https://")


# ---------------------------------------------------------------------------
# normalize_base_types
# ---------------------------------------------------------------------------


class TestNormalizeBaseTypes:
    def test_hp_is_nullable_int64(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        df = normalize_base_types(df)
        assert df["hp"].dtype.name == "Int64"

    def test_hp_numeric_value(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        df = normalize_base_types(df)
        assert df.loc[df["id"] == "A1 001", "hp"].iloc[0] == 70

    def test_hp_na_for_trainer(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        df = normalize_base_types(df)
        trainer_hp = df.loc[df["id"] == "A1 219", "hp"].iloc[0]
        assert pd.isna(trainer_hp)

    def test_empty_strings_become_none(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        df = normalize_base_types(df)
        bulbasaur = df[df["id"] == "A1 001"].iloc[0]
        # move2_name was "" → should be None/NA
        assert bulbasaur["move2_name"] is None or pd.isna(bulbasaur["move2_name"])

    def test_id_is_stripped(self):
        raw = {
            "cardArraySchema": {
                "cards": [
                    {
                        "id": "  A1 001  ",
                        "name": "Bulbasaur",
                        "card_type": "Pokemon",
                        "pokemon_type": "Grass",
                        "hp": "70",
                        "ex": "",
                        "evolution_stage": "Basic",
                        "rarity": "◇",
                        "set": "A",
                        "subset": "B",
                        "ability": "",
                        "image_url": "https://example.com",
                        "archive_url": "https://example.com",
                        "moves": [],
                    }
                ]
            }
        }
        df = normalize_base_types(flatten_to_base_table(raw))
        assert df.iloc[0]["id"] == "A1 001"

    def test_does_not_mutate_input(self):
        df = flatten_to_base_table(SAMPLE_RAW)
        original_hp_dtype = df["hp"].dtype
        _ = normalize_base_types(df)
        assert df["hp"].dtype == original_hp_dtype
