import pytest
from tcg.utils import (
    clean_str,
    parse_energy_cost,
    parse_retreat_cost,
    trim_after_second_parens,
    ENERGY_SYMBOLS,
    RETREAT_COSTS,
)


# ── clean_str ──────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "raw, empty_val, expected",
    [
        ("   Hello   World   ", None, "Hello World"),
        ("Line1\nLine2\t\tLine3", None, "Line1 Line2 Line3"),
        ("\t \n   \t", "N/A", "N/A"),  # collapses to empty → empty_val
        ("", None, None),  # truly empty string
        (None, "-", None),  # None stays None (DEFAULT_EMPTY)
        ("Already  clean", None, "Already clean"),
    ],
)
def test_clean_str(raw, empty_val, expected):
    assert clean_str(raw, empty_val) == expected
    # idempotency – running twice should give the same result
    if raw is not None:
        assert clean_str(clean_str(raw, empty_val), empty_val) == expected


# ── parse_energy_cost ──────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "energy_str, expected",
    [
        ("Darkness 2", ENERGY_SYMBOLS["Darkness"] * 2),
        ("Fire", ENERGY_SYMBOLS["Fire"]),
        ("Water 1", ENERGY_SYMBOLS["Water"]),  # explicit count == 1
        ("Colorless 3", ENERGY_SYMBOLS["Colorless"] * 3),
        ("Unknown 3", "?" * 3),  # unknown type, valid count
        ("Grass X", ENERGY_SYMBOLS["Grass"]),  # second token isn’t a digit
    ],
)
def test_parse_energy_cost(energy_str, expected):
    assert parse_energy_cost(energy_str) == expected


# ── parse_retreat_cost ─────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "url, expected",
    list(RETREAT_COSTS.items()) + [("https://invalid.com", -1)]
)
def test_parse_retreat_cost(url, expected):
    assert parse_retreat_cost(url) == expected


# ── trim_after_second_parens ───────────────────────────────────────────────────
@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Genetic Apex (A1) Mewtwo", "Genetic Apex (A1) Mewtwo"),
        ("Genetic Apex (A1) Any", "Genetic Apex (A1) Any"),
        (
            "Space-Time Smackdown (A2) Any (Space-Time Smackdown)",
            "Space-Time Smackdown (A2) Any",
        ),
        ("Name (Alpha) (Beta) (Gamma)", "Name (Alpha)"),
        ("No parentheses here", "No parentheses here"),
        ("(Only one)", "(Only one)"),
    ],
)
def test_trim_after_second_parens(raw, expected):
    assert trim_after_second_parens(raw) == expected
