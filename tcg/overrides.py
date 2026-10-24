"""
Manual corrections for cards where game8's data is wrong or missing.

Format: {card id: {column: correct value}}. Keep all corrections for one card
inside the same inner dictionary; duplicate card IDs overwrite earlier entries.
Applied last, so these always win over scraped values.
Add a short comment saying *why* each entry exists.
"""

from tcg.utils import COLORLESS

OVERRIDES: dict[str, dict[str, str]] = {
    # --- wrong or missing values on game8 ---
    "A1 183": {"move1_damage": "40"},  # Dratini: Ram does 40, not 70
    "A4 177": {"hp": "60"},  # Spinarak: HP is included as "/"
    "B3 031": {  # Larvesta: Move cost and damage not included
        "move1_cost": "🔴",
        "move1_damage": "20",
    },
    "B2a 115": {"type": "Supporter"},  # Arven: Missing type
    "B2b 117": {"type": "Pokemon Tool"},  # Metal Core Barrier: Missing type
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
    # --- type wrong on game8 (attacks use Grass energy; the card's other print is Grass) ---
    "B1 027": {"type": "Grass"},  # Rillaboom: listed as Fire (B1 229 is Grass)
    "B1a 070": {"type": "Grass"},  # Ariados: listed as Darkness (B1a 006 is Grass)
    # --- stage missing on game8 (B2 194-233 are alternate arts; copied from the original print) ---
    "B2 194": {"stage": "Basic"},  # Teal Mask Ogerpon ex
    "B2 195": {"stage": "Basic"},  # Blacephalon ex
    "B2 196": {"stage": "Stage 1"},  # Alolan Ninetales ex
    "B2 197": {"stage": "Stage 2"},  # Mega Swampert ex
    "B2 198": {"stage": "Stage 1"},  # Toxtricity ex
    "B2 199": {"stage": "Basic"},  # Mimikyu ex
    "B2 200": {"stage": "Stage 2"},  # Gigalith ex
    "B2 201": {"stage": "Basic"},  # Mega Mawile ex
    "B2 202": {"stage": "Basic"},  # Mega Kangaskhan ex
    "B2 203": {"stage": "Stage 2"},  # Mega Gardevoir ex
    "B2 204": {"stage": "Basic"},  # Meowth
    "B2 205": {"stage": "Basic"},  # Tangela
    "B2 206": {"stage": "Basic"},  # Magby
    "B2 207": {"stage": "Basic"},  # Magmar
    "B2 208": {"stage": "Basic"},  # Horsea
    "B2 209": {"stage": "Stage 1"},  # Seadra
    "B2 210": {"stage": "Stage 1"},  # Omanyte
    "B2 211": {"stage": "Stage 2"},  # Omastar
    "B2 212": {"stage": "Basic"},  # Mantyke
    "B2 213": {"stage": "Basic"},  # Pichu
    "B2 214": {"stage": "Basic"},  # Clefairy
    "B2 215": {"stage": "Stage 1"},  # Clefable
    "B2 216": {"stage": "Basic"},  # Latias
    "B2 217": {"stage": "Basic"},  # Latios
    "B2 218": {"stage": "Basic"},  # Hitmonlee
    "B2 219": {"stage": "Basic"},  # Hitmonchan
    "B2 220": {"stage": "Stage 1"},  # Kabuto
    "B2 221": {"stage": "Stage 2"},  # Kabutops
    "B2 222": {"stage": "Basic"},  # Phanpy
    "B2 223": {"stage": "Basic"},  # Tyrogue
    "B2 224": {"stage": "Basic"},  # Tauros
    "B2 225": {"stage": "Stage 1"},  # Flareon ex
    "B2 226": {"stage": "Basic"},  # Ho-Oh ex
    "B2 227": {"stage": "Stage 2"},  # Kingdra ex
    "B2 228": {"stage": "Stage 1"},  # Espeon ex
    "B2 229": {"stage": "Stage 1"},  # Sylveon ex
    "B2 230": {"stage": "Stage 1"},  # Donphan ex
    "B2 231": {"stage": "Stage 1"},  # Umbreon ex
    "B2 232": {"stage": "Basic"},  # Lugia ex
    "B2 233": {"stage": "Basic"},  # Meloetta
    # --- rarity missing on game8 (Promo-B cards) ---
    "P-B 087": {"rarity": "Promo"},  # Mega Sceptile ex
    "P-B 088": {"rarity": "Promo"},  # Team Rocket's Scyther
    "P-B 089": {"rarity": "Promo"},  # Team Rocket's Lapras
    "P-B 090": {"rarity": "Promo"},  # Wingull
    "P-B 091": {"rarity": "Promo"},  # Team Rocket's Wobbuffet
    "P-B 092": {"rarity": "Promo"},  # Marowak
    "P-B 093": {"rarity": "Promo"},  # Fennekin
    "P-B 094": {"rarity": "Promo"},  # Meowstic
    # --- generation missing on game8 (copied from the same card's other print) ---
    "B4a 087": {"generation": "1"},  # Team Rocket's Boss
    "B4b 373": {"generation": "9"},  # Ancient Booster Energy Capsule
    "B4b 374": {"generation": "9"},  # Future Booster Energy Capsule
    "B4b 397": {"generation": "9"},  # Mesagoza
    "B4 113": {"generation": "9"},  # Archaludon (debuted in Gen 9; entered by hand)
    # --- illustrator missing on game8 (same card, same rarity, other print) ---
    "B2 145": {"illustrator": "inose yukie"},  # Lucky Ice Pop
    "B2a 092": {"illustrator": "Susumu Maeya"},  # Penny
    "B4b 198": {"illustrator": "inose yukie"},  # Lucky Ice Pop
    # --- game8 typo: effect text ends in "/" instead of "." ---
    "B2a 037": {
        "move2_effect": "Discard all Water Energy from this Pokemon. This attack does 130 damage to 1 of your opponent's Pokemon."
    },  # Chien-Pao ex
    "B2a 102": {
        "move2_effect": "Discard all Water Energy from this Pokemon. This attack does 130 damage to 1 of your opponent's Pokemon."
    },  # Chien-Pao ex
    "B2a 112": {
        "move2_effect": "Discard all Water Energy from this Pokemon. This attack does 130 damage to 1 of your opponent's Pokemon."
    },  # Chien-Pao ex
    "P-B 041": {
        "move2_effect": "Discard all Water Energy from this Pokemon. This attack does 130 damage to 1 of your opponent's Pokemon."
    },  # Chien-Pao ex
    "B4b 081": {
        "move2_effect": "Discard all Water Energy from this Pokemon. This attack does 130 damage to 1 of your opponent's Pokemon."
    },  # Chien-Pao ex
    # TODO: illustrators still missing on game8 (fill in as found):
    #   A2b 075
    #   A3 062
    #   A3a 084 085
    #   A3b 011
    #   A4 003 016 058 067 110 115 136 144 157 162 163 165 166 167 168 172 173 183
    #       185 197 210 211
    #   A4a 002 031 067 072 087 088
    #   A4b 332 333 356 357 374
    #   B1 009 015 017 030 057 059 083 104 126 163 179 229 232 240 249 267 275 278
    #       283 292 293 294 298 300 301 302 303 305 306 310 312 313
    #   B1a 018 032 043 057 075 091 092 093 096 097
    #   P-B 012 033 041 054 070 071 091 095 101 103
    #   B2 003 018 057 063 064 065 069 090 095 101 136 138 150 153 158 159 164 165
    #       191 195 205 208 209 210 211 212 213 214 215 216 217
    #   B2a 007 019 021 028 032 037 052 066 068 070 102 109 111 116 117 118 119 120
    #       121
    #   B2b 011 017 028 037 046 055 070 074 088 089 090 091 092 093 094 098 099 104
    #       105 106 107
    #   B3 013 024 035 047 072 085 086 101 122 137 149 153 158 159 160 161 169 171
    #       178 180 190 197 200 204 206 207 208 212 213 214 233 234
    #   B3a 001 013 029 030 031 034 036 058 060 061 067 074 081 084 093 096 098 099
    #       102 103 109
    #   B3b 010 020 033 052 061 066 073 074 083 086 088 098
    #   B4 043 054 071 078 100 107 117 121 126 128 152 156 168 169 173 177 179 192
    #       199 201 202 203 205 206 207 208 213 214 222 232 233
    #   B4a 019 021 024 029 039 040 048 051 058 072 075 078 081 097 098 103 104
    #   B4b 013 016 018 024 033 049 053 077 081 089 104 118 136 139 159 170 175 189
    #       217 221 227 232 246 248 249 254 260 271 274 296 304 313 326 337 344 347
    #       359 383 387 393 398 404 406 429
    # TODO: generation still missing on game8 (almost all Trainers, from the newer sets):
    #   A4 151 152 153 154 155
    #   A4a 067 068 070 084
    #   A4b 310 311
    #   B1 213 215 217 219 220 331
    #   B1a 067 103
    #   B2 145 147 148 153 154 155 234
    #   B2a 086 087 131
    #   B2b 065 066 069 117
    #   B3 147 153 154 155
    #   B3b 064 065 067 069 084 106
    #   B4 145 148 149 154 155
    #   B4a 067 068 069 070 085 086 094 110
    #   B4b 198 199 200 201 202 203 204 206 209 210 211 216 227 228 229 230 232 233
    #       234 235 236 364 365 366 367 368 369 370 372 375 376 377 382 393 394 395
    #       396 398 399 400 401 402
    # TODO: weakness still missing on game8 (Dragon cards have none, so they are skipped):
    #   A4 032 066 070 075 077 101 166 171
    #   P-A 093
    #   A4a 023 059 063 077 105
    #   B1 109
    #   B3 013 078 159 168
    #   B3b 054 105
    #   B4 068 074 168
    #   B4a 063 077
    #   B4b 013 108 109 110 188 246 306 307 308 358
    # TODO: spot-check type against the card art. Nothing in the data confirms these (attacks cost
    #   only Colorless, single print) and they differ from the species' usual type; likely genuine:
    #   A1 085 086 | A2 121 | A2a 035 | A3a 027 | A4 062 063 073 | P-B 022 | B2a 010 | B3a 057
    #   B3b 026 | B4 077
    # TODO: Ariados B1a 006 vs B1a 070 disagree on retreat_cost (2 vs 1); one of them is wrong.
    # TODO: incomplete attack/ability data on game8:
    #   A2b 041 Hitmonchan: move1_name missing (damage 90 is present)
    #   B4b 009 Celebi: ability "Time Recall" has no effect text
    #   B4 233 Dragonair "Draconic Whip" and B4b 174 Axew "Sharp Fang": no damage or effect
}


def apply_overrides(card: dict[str, str | None]) -> None:
    """Mutate `card` in place with any manual corrections for its id."""
    card.update(OVERRIDES.get(card["id"], {}))
