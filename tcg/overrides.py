"""
Manual corrections for cards where game8's data is wrong or missing.

Format: {card number: {column: correct value}}
Applied last, so these always win over scraped values.
Add a short comment saying *why* each entry exists.
"""

from tcg.utils import COLORLESS

OVERRIDES: dict[str, dict[str, str]] = {
    # --- wrong values on game8 ---
    "A1 183": {"move1_damage": "40"},  # Dratini: Ram does 40, not 70
    "A2 047": {"move1_damage": "30"},  # Wash Rotom: Wave Splash does 30, not 39
    "A4 177": {"HP": "60"},
    "A1a 057": {"move1_cost": COLORLESS},  # Pidgey: Flap's cost is missing
    # --- weakness wrong (W) / page missing (M) ---
    "A1 169": {"weakness": "Fighting"},  # Nidoran M (W)
    "A1 170": {"weakness": "Fighting"},  # Nidorino (W)
    "A1 171": {"weakness": "Fighting"},  # Nidoking (W)
    "A1 241": {"weakness": "Fighting"},  # Nidoking (W)
    "A1a 048": {"weakness": "Grass"},  # Stonjourner (W)
    "P-A 028": {"weakness": "Water"},  # Volcarona (W)
    "P-A 037": {"weakness": "Darkness"},  # Cresselia ex (W)
    "P-A 038": {"weakness": "Darkness"},  # Misdreavus (W)
    # --- generation / illustrator missing on page ---
    "A1a 065": {"generation": "9"},  # Mythical Slab
    "A1a 066": {"generation": "9"},  # Budding Expeditioner
    "A1a 080": {"generation": "9"},  # Budding Expeditioner
    "P-A 053": {  # Floatzel (page missing)
        "generation": "4",
        "illustrator": "Shin Nagasawa",
        "weakness": "Lightning",
    },
    "P-A 056": {  # Ekans (page missing)
        "generation": "1",
        "illustrator": "Krgc",
        "weakness": "Fighting",
    },
    # TODO: illustrators still missing on game8 (fill in as found):
    #   A2b 002 005 006 007 008 014 018 020 021 023 025 040 041 047 049 068 070
    #       071 073 074 075 076 089 090 095 096 103
    #   A3  009 045 073 079 093 103 130 135 148 155 157 158 162 165 167 168 171
    #       172 174 178 179 190 197 203 228 229
    #   P-A 046 047 049 052 060 070
}


def apply_overrides(card: dict[str, str | None]) -> None:
    """Mutate `card` in place with any manual corrections for its number."""
    card.update(OVERRIDES.get(card["number"], {}))
