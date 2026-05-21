"""Tests for tcg.validate.base_checks.

All tests use embedded fixture DataFrames – no network calls are made.
"""
import pandas as pd
import pytest

from tcg.validate.base_checks import ValidationIssue, validate_cards


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _make_df(**overrides) -> pd.DataFrame:
    """Return a minimal one-row DataFrame that passes all checks by default.

    Any keyword argument overrides a field in that row.
    """
    base: dict = {
        "id": "A1 001",
        "name": "Bulbasaur",
        "card_type": "Pokemon",
        "pokemon_type": "Grass",
        "hp": 70,
        "ex": 1,
        "stage": "Basic",
        "rarity": "◇",
        "set": "Genetic Apex (A1)",
        "subset": "Mewtwo",
        "ability_name": None,
        "ability_effect": None,
        "move1_name": "Vine Whip",
        "move1_cost": "🟢",
        "move1_damage": "40",
        "move1_description": None,
        "move2_name": None,
        "move2_cost": None,
        "move2_damage": None,
        "move2_description": None,
        "image": "https://img.game8.co/image.png/show",
        "page": "https://game8.co/games/Pokemon-TCG-Pocket/archives/476002",
    }
    base.update(overrides)
    return pd.DataFrame([base])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestValidateCards:
    # ── clean data ──────────────────────────────────────────────────────────

    def test_clean_data_no_issues(self):
        df = _make_df()
        assert validate_cards(df) == []

    # ── required columns ────────────────────────────────────────────────────

    def test_missing_required_column_id(self):
        df = _make_df().drop(columns=["id"])
        issues = validate_cards(df)
        assert any(i.check == "required_columns" and i.severity == "error" for i in issues)

    def test_missing_required_column_image(self):
        df = _make_df().drop(columns=["image"])
        issues = validate_cards(df)
        assert any(i.check == "required_columns" for i in issues)

    def test_missing_required_column_aborts_further_checks(self):
        # With a missing column only the required_columns error should appear
        df = _make_df().drop(columns=["id"])
        issues = validate_cards(df)
        assert len(issues) == 1
        assert issues[0].check == "required_columns"

    # ── id uniqueness / non-null ─────────────────────────────────────────────

    def test_null_id(self):
        df = _make_df(id=None)
        issues = validate_cards(df)
        assert any(i.check == "id_non_null" and i.severity == "error" for i in issues)

    def test_empty_string_id(self):
        df = _make_df(id="")
        issues = validate_cards(df)
        assert any(i.check == "id_non_null" for i in issues)

    def test_duplicate_ids(self):
        df = pd.concat([_make_df(id="A1 001"), _make_df(id="A1 001")], ignore_index=True)
        issues = validate_cards(df)
        assert any(i.check == "id_unique" and i.severity == "error" for i in issues)

    def test_unique_ids_no_issue(self):
        df = pd.concat([_make_df(id="A1 001"), _make_df(id="A1 002")], ignore_index=True)
        issues = validate_cards(df)
        assert not any(i.check == "id_unique" for i in issues)

    # ── card_type domain ─────────────────────────────────────────────────────

    def test_unexpected_card_type_warning(self):
        df = _make_df(card_type="Weird")
        issues = validate_cards(df)
        assert any(i.check == "card_type_domain" and i.severity == "warning" for i in issues)

    def test_valid_card_types_no_issue(self):
        for ct in ("Pokemon", "Item", "Supporter", "Pokemon Tool"):
            df = _make_df(card_type=ct)
            issues = validate_cards(df)
            assert not any(i.check == "card_type_domain" for i in issues), ct

    # ── hp numeric ──────────────────────────────────────────────────────────

    def test_missing_hp_for_pokemon_warning(self):
        df = _make_df(hp=None)
        df["hp"] = pd.array([pd.NA], dtype="Int64")
        issues = validate_cards(df)
        assert any(i.check == "hp_numeric" and i.severity == "warning" for i in issues)

    def test_missing_hp_for_trainer_no_issue(self):
        df = _make_df(card_type="Item", hp=None)
        df["hp"] = pd.array([pd.NA], dtype="Int64")
        issues = validate_cards(df)
        assert not any(i.check == "hp_numeric" for i in issues)

    # ── move consistency ─────────────────────────────────────────────────────

    def test_move1_consistency_empty_name_with_cost(self):
        df = _make_df(move1_name=None, move1_cost="🟢")
        issues = validate_cards(df)
        assert any("move1_consistency" in i.check for i in issues)

    def test_move1_consistency_all_none_no_issue(self):
        # All move1 sub-fields are None → no inconsistency
        df = _make_df(
            move1_name=None,
            move1_cost=None,
            move1_damage=None,
            move1_description=None,
        )
        issues = validate_cards(df)
        assert not any("move1_consistency" in i.check for i in issues)

    def test_move2_consistency_empty_name_with_damage(self):
        df = _make_df(move2_name=None, move2_damage="50")
        issues = validate_cards(df)
        assert any("move2_consistency" in i.check for i in issues)

    # ── URL shape ────────────────────────────────────────────────────────────

    def test_malformed_image_url_warning(self):
        df = _make_df(image="not_a_url")
        issues = validate_cards(df)
        assert any(i.check == "image_url_shape" and i.severity == "warning" for i in issues)

    def test_malformed_page_url_warning(self):
        df = _make_df(page="not_a_url")
        issues = validate_cards(df)
        assert any(i.check == "page_url_shape" and i.severity == "warning" for i in issues)

    def test_null_url_no_issue(self):
        # None/NA URLs are skipped (only non-null values are checked)
        df = _make_df(image=None)
        issues = validate_cards(df)
        assert not any(i.check == "image_url_shape" for i in issues)

    def test_valid_https_url_no_issue(self):
        df = _make_df(image="https://example.com/img.png")
        issues = validate_cards(df)
        assert not any(i.check == "image_url_shape" for i in issues)

    # ── multi-card DataFrame ─────────────────────────────────────────────────

    def test_one_bad_row_in_multiple_cards(self):
        good = _make_df(id="A1 001")
        bad = _make_df(id="A1 002", card_type="BadType")
        df = pd.concat([good, bad], ignore_index=True)
        issues = validate_cards(df)
        card_type_issue = next(i for i in issues if i.check == "card_type_domain")
        assert "A1 002" in card_type_issue.row_ids

    # ── ValidationIssue dataclass ────────────────────────────────────────────

    def test_issue_row_ids_default_empty(self):
        issue = ValidationIssue(severity="error", check="test", message="msg")
        assert issue.row_ids == []
