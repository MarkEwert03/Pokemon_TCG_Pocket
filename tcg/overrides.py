"""
Manual corrections for cards where game8's data is wrong or missing.

Format: {card id: {column: correct value}}. Keep all corrections for one card
inside the same inner dictionary; duplicate card IDs overwrite earlier entries.
Applied last, so these always win over scraped values.
Add a short comment saying *why* each entry exists.
"""

import warnings

# These corrections describe gameplay shared by every card with the same
# base_id. Keys are canonical base IDs, not individual card IDs.
FUNCTIONAL_FIELDS = frozenset(
    {
        "stage",
        "evolves_from",
        "hp",
        "type",
        "weakness",
        "retreat_cost",
        "ko",
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
    }
)

BASE_OVERRIDES: dict[str, dict[str, str]] = {
    # Infernape ex has no retreat cost; Game8's "-" placeholder was parsed as 1.
    "A2 029": {"retreat_cost": "0"},
    # --- wrong or missing values on game8 ---
    "A1 183": {"move1_damage": "40"},  # Dratini: Ram does 40, not 70
    "A2b 041": {
        "move1_name": "Magnum Punch",
        "move1_cost": "🟠🟠🟠",
        "move1_damage": "90",
    },  # Hitmonchan: Missing all move info
    "A4 177": {"hp": "60"},  # Spinarak: HP is included as "/"
    "B1a 006": {"retreat_cost": "1"},  # Ariados: RC should be 1 not 2
    "B3 031": {
        "move1_cost": "🔴",
        "move1_damage": "20",
    },  # Larvesta: Move cost and damage not included
    "B4 233": {"move1_damage": "40"},  # Dragonair: Draconic Whip
    "B4b 174": {"move1_damage": "40"},  # Axew: Sharp Fang
    "A2b 006": {"move1_damage": "40"},  # Floragato: Slash
    # --- weakness wrong (W) / page missing (M) ---
    "A1 169": {"weakness": "Fighting"},  # Nidoran M (W)
    "A1 170": {"weakness": "Fighting"},  # Nidorino (W)
    "A1 171": {"weakness": "Fighting"},  # Nidoking (W)
    "A1 241": {"weakness": "Fighting"},  # Nidoking (W)
    "A1a 048": {"weakness": "Grass"},  # Stonjourner (W)
    "P-A 028": {"weakness": "Water"},  # Volcarona (W)
    "P-A 037": {"weakness": "Darkness"},  # Cresselia ex (W)
    "P-A 038": {"weakness": "Darkness"},  # Misdreavus (W)
    "B2 181": {"weakness": "Water"},  # Blacephalon ex: Incorrectly has weakness as Fire
    "B2 195": {
        "stage": "Basic",
        "weakness": "Water",
    },  # Blacephalon ex: Missing stage and weakness
    # --- type wrong or missing on game8
    "B1 027": {"type": "Grass"},  # Rillaboom: listed as Fire (B1 229 is Grass)
    "B1a 070": {"type": "Grass"},  # Ariados: listed as Darkness (B1a 006 is Grass)
    "B2a 115": {"type": "Supporter"},  # Arven: Missing type
    "B2b 117": {"type": "Pokemon Tool"},  # Metal Core Barrier: Missing type
    # --- stage missing on game8 (B2 194-233 are alternate arts; copied from the original print) ---
    "B2 194": {"stage": "Basic"},  # Teal Mask Ogerpon ex
    "B2 196": {"stage": "Stage 1"},  # Alolan Ninetales ex
    "B2 197": {"stage": "Stage 2"},  # Mega Swampert ex
    "B2 198": {"stage": "Stage 1"},  # Toxtricity ex
    "B2 199": {
        "stage": "Basic",
        "ability_name": "Disguise",
        "ability_effect": "When this Pokemon is first damaged by an attack after coming into play, prevent that damage",
    },  # Mimikyu ex: Blank ability text
    "B2 200": {"stage": "Stage 2"},  # Gigalith ex
    "B2 201": {"stage": "Basic"},  # Mega Mawile ex
    "B2 202": {"stage": "Basic"},  # Mega Kangaskhan ex
    "B2 203": {"stage": "Stage 2"},  # Mega Gardevoir ex
    "B2 204": {"stage": "Basic"},  # Meowth
    "B2 205": {"stage": "Basic"},  # Tangela
    "B2 206": {
        "stage": "Basic",
        "weakness": None,
    },  # Magby: Incorrectly had weakness to Fire
    "B2 207": {"stage": "Basic"},  # Magmar
    "B2 208": {"stage": "Basic"},  # Horsea
    "B2 209": {"stage": "Stage 1"},  # Seadra
    "B2 210": {
        "stage": "Stage 1",
        "weakness": "Lightning",
    },  # Omanyte: Incorrectly had weakness as Grass
    "B2 211": {
        "stage": "Stage 2",
        "weakness": "Lightning",
    },  # Omastar (Omastar is Water; base A1 082 is Lightning)
    "B2 212": {
        "stage": "Basic",
        "weakness": None,
    },  # Mantyke: Incorrectly had weakness as Water
    "B2 213": {
        "stage": "Basic",
        "weakness": None,
    },  # Pichu: Incorrectly had weakness as Lightning
    "B2 214": {"stage": "Basic"},  # Clefairy
    "B2 215": {"stage": "Stage 1"},  # Clefable
    "B2 216": {"stage": "Basic"},  # Latias
    "B2 217": {
        "stage": "Basic",
        "ability_name": "Fantastical Floating",
        "ability_effect": "If you have Latias in play, this Pokemon has no Retreat Cost.",
    },  # Latios: Blank ability
    "B2 218": {"stage": "Basic", "move1_damage": "80"},  # Hitmonlee (blank; base print is 80)
    "B2 219": {"stage": "Basic"},  # Hitmonchan
    "B2 220": {"stage": "Stage 1"},  # Kabuto
    "B2 221": {"stage": "Stage 2"},  # Kabutops
    "B2 222": {"stage": "Basic"},  # Phanpy
    "B2 223": {
        "stage": "Basic",
        "weakness": None,
    },  # Tyrogue: Incorrectly had weakness as Fighting
    "B2 224": {"stage": "Basic"},  # Tauros
    "B2 225": {
        "stage": "Stage 1",
        "ability_name": "Combust",
        "ability_effect": "Once during your turn, you may attach a Fire Energy from your discard pile to this Pokemon. If you do, do 20 damage to this Pokemon.",
    },  # Flareon ex: Blank ability
    "B2 226": {"stage": "Basic"},  # Ho-Oh ex
    "B2 227": {"stage": "Stage 2"},  # Kingdra ex
    "B2 228": {
        "stage": "Stage 1",
        "ability_name": "Psychic Healing",
        "ability_effect": "Once during your turn, if this Pokemon is in the Active Spot, you may heal 30 damage from 1 of your Pokemon.",
    },  # Espeon ex: Blank ability
    "B2 229": {
        "stage": "Stage 1",
        "ability_name": "Happy Ribbon",
        "ability_effect": "Once during your turn, when you play this Pokemon from your hand to evolve 1 of your Pokemon, you may draw 2 cards.",
    },  # Sylveon ex: Blank ability
    "B2 230": {"stage": "Stage 1"},  # Donphan ex
    "B2 231": {
        "stage": "Stage 1",
        "ability_name": "Dark Chase",
        "ability_effect": "Once during your turn, if this Pokemon is in the Active Spot, you may switch in 1 of your opponent's benched Pokemon that has damage on it to the Active Spot.",
    },  # Umbreon ex: Blank ability
    "B2 232": {"stage": "Basic"},  # Lugia ex
    "B2 233": {"stage": "Basic"},  # Meloetta
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
    # --- stage wrong on game8 (checked against the evolution chain: stage = 1 + stage of the card it evolves from) ---
    "A3a 087": {"stage": "Stage 1"},  # Alolan Dugtrio ex: evolves from Alolan Diglett (Basic)
    "A3b 015": {"stage": "Stage 1"},  # Salazzle: evolves from Salandit (Basic)
    "A3b 057": {"stage": "Stage 1"},  # Snorlax ex: evolves from Munchlax (Basic)
    "A3b 084": {"stage": "Stage 1"},  # Snorlax ex: evolves from Munchlax (Basic)
    "A4b 288": {"stage": "Stage 1"},  # Snorlax ex: evolves from Munchlax (Basic)
    "B1 327": {"stage": "Stage 1"},  # Bibarel ex: evolves from Bidoof (Basic)
    "B2a 082": {"stage": "Stage 1"},  # Maushold: evolves from Tandemaus (Basic)
    "B3 008": {"stage": "Stage 2"},  # Mega Sceptile ex: evolves from Grovyle (Stage 1)
    "B3 160": {"stage": "Stage 1"},  # Flapple: evolves from Applin (Basic)
    "B3 204": {"stage": "Stage 1"},  # Mega Lucario ex: evolves from Riolu (Basic)
    "B4b 012": {"stage": "Stage 2"},  # Mega Sceptile ex: evolves from Grovyle (Stage 1)
    "B4b 275": {"stage": "Basic"},  # Alolan Vulpix: no evolves_from
    "B4b 348": {"stage": "Stage 2"},  # Haxorus: evolves from Fraxure (Stage 1)
    "B4b 417": {"stage": "Stage 1"},  # Mega Altaria ex: evolves from Swablu (Basic)
    "B4b 418": {"stage": "Stage 1"},  # Mega Lucario ex: evolves from Riolu (Basic)
    "P-A 091": {"stage": "Stage 1"},  # Greedent: evolves from Skwovet (Basic)
    "P-A 097": {"stage": "Basic"},  # Kangaskhan: no evolves_from
    # --- attack cost wrong on game8 (variant disagrees with the card's other prints) ---
    "A2b 020": {"move1_cost": "🔵🔵🔘🔘"},  # Dondozo: Ocean Cyclone
    "A2b 056": {"move1_cost": "⚪⚪🔘"},  # Revavroom: Spinning Drift
    "A4 065": {"move1_cost": "🟡🔘🔘"},  # Lanturn ex: Flashing Signal
    "A3a 019": {"move1_cost": "🟡"},  # Tapu Koko ex: Plasma Hurricane
    "A3 104": {"move1_cost": "🟤🔘"},  # Passimian ex: Seismic Toss
    "A3a 006": {"move1_cost": "🔘🔘"},  # Buzzwole ex: Punch
    "A3 087": {"move1_cost": "🟣🔘🔘"},  # Lunala ex: Lunar Blast
    "B2a 002": {"move1_cost": "🟢"},  # Floragato: Leaf Step
    "B3 079": {"move1_cost": "🟤"},  # Riolu: Fighting Fist
    "B3 122": {"move1_cost": "🔘"},  # Meltan: Stampede
    "B2 130": {"move1_cost": "🔘🔘"},  # Smeargle: Tail Whap
    # --- attack damage wrong or blank on game8 (variant disagrees with the card's other prints) ---
    "A1 018": {"move1_damage": "20"},  # Bellsprout
    "A1 079": {
        "move1_damage": "20+",
        "move1_effect": "If this Pokemon has at least 3 extra Water Energy attached, this attack does 70 more damage.",
    },  # Lapras
    "A1 154": {"move1_damage": None},  # Hitmonlee (does 30 dmg to bench)
    "A2 019": {"move1_damage": "40+"},  # Carnivine
    "A2b 040": {"move1_damage": "30"},  # Hitmonlee
    "A2b 048": {"move1_damage": "60+"},  # Paldean Clodsire ex
    "A4 045": {"move1_damage": "20+"},  # Gyarados
    "B1 005": {"move1_damage": None},  # Beautifly (does 50 dmg to one pokemon)
}

OVERRIDES: dict[str, dict[str, str | None]] = {
    # --- wrong or missing values on game8 ---
    "B4b 009": {
        "ability_effect": "Each of your evolved Pokemon can use any attack from its previous Evolutions. (You still need the necessary Energy to use each attack.)",
        "image": "https://img.game8.co/4479795/7ff12fab25f704898086ae6aba1a07b7.png/show",
        "url": "https://game8.co/games/Pokemon-TCG-Pocket/archives/596976",
        "retreat_cost": "1",
    },  # Celebi: Incorrectly linked to Mega Pinsir ex page
    # --- generation / illustrator missing on page ---
    "A1a 065": {"generation": "9"},  # Mythical Slab
    "A1a 066": {"generation": "9"},  # Budding Expeditioner
    "A1a 080": {"generation": "9"},  # Budding Expeditioner
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
    #   P-B 012 033 041 054 070 071 091 095 101 103
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
    # NOTE: blank weakness is NOT missing data for baby Pokémon (Azurill, Bonsly, Budew, Chingling, Cleffa, Elekid, Happiny, Igglybuff, Magby, Mantyke, Mime Jr., Munchlax, Pichu, Smoochum, Tyrogue, Wynaut) or Dragon types; they have none.
    # TODO: spot-check type against the card art. Nothing in the data confirms these (attacks cost
    #   only Colorless, single print) and they differ from the species' usual type; likely genuine:
    #   A1 085 086 | A2 121 | A2a 035 | A3a 027 | A4 062 063 073 | P-B 022 | B2a 010 | B3a 057
    #   B3b 026 | B4 077
    # TODO: prints of the same card disagree and the data can't say which is right (check the art):
    #   retreat_cost: A1 040 / A3a 090 Arcanine (1 vs 2) | A1 058 / A4a 094 Golduck (1 vs 2)
    #       A2 079 / A2 168 Cresselia (1 vs 2) | A3 078 / A3 167 Cutiefly (0 vs 1)
    #       B1 068 / B3 209 Frillish (1 vs 2) | B3b 034 Fidough (0, 0, 1, 1) | B4 141 Swanna ex (1, 1, 2, 2)
    #   weakness: A4 057 / A4 170 Delibird (Metal vs Lightning)
    #   move1_damage: A3 100 / P-A 068 Lycanroc (80 vs 100)
    #   move1_cost: B4 054 / P-B 085 Pachirisu (🟡 vs 🟡🟡) | B2a 002 vs P-B 069 Floragato (🟢🟢 vs 🟢)
    #   effect numbers: A1 079, B1 108, B1 157, B1 175
    # TODO: these share a base_id but look like DIFFERENT cards (cost, damage and effect all agree with
    #   each other); probably a base_id linkage problem, not wrong data. Left alone:
    #   A1 046 / B4 023 Moltres | B3 064 / B4 072 B4b 105 B4b 305 Kirlia | A2a 034 / A4 084 A4 085 Unown
    # TODO: B3b 049 Hisuian Sliggoo is Stage 1 but evolves_from is blank (Hisuian Goomy isn't in the data).
    # TODO: ~41 effect texts differ between prints only in wording or punctuation (' vs ', Pokémon vs Pokemon,
    #   trailing period). Not errors; a normalization step in the pipeline is better than overrides.
}


def apply_overrides(card: dict[str, str | None]) -> None:
    """Apply base-level functional corrections, then card-specific fixes."""
    base_overrides = BASE_OVERRIDES.get(card.get("base_id"), {})
    invalid_fields = set(base_overrides) - FUNCTIONAL_FIELDS
    if invalid_fields:
        warnings.warn(
            f"Base override for {card.get('base_id')!r} contains non-functional "
            f"fields: {sorted(invalid_fields)}; ignoring those fields.",
            UserWarning,
            stacklevel=2,
        )
        base_overrides = {
            field: value for field, value in base_overrides.items() if field in FUNCTIONAL_FIELDS
        }
    card.update(base_overrides)
    card.update(OVERRIDES.get(card["id"], {}))
