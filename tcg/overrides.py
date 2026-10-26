"""
Manual corrections for cards where game8's data is wrong or missing.

Format: {card id: {column: correct value}}. Keep all corrections for one card
inside the same inner dictionary; duplicate card IDs overwrite earlier entries.
Applied last, so these always win over scraped values.
Add a short comment saying *why* each entry exists.
"""

import warnings

# These corrections describe gameplay shared by every card with the same
# canon_id. Keys are canonical IDs, not individual card IDs.
FUNCTIONAL_FIELDS = frozenset(
    {
        "stage",
        "evolves_from",
        "hp",
        "type",
        "weakness",
        "rc",
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

# Explicit canonical-link corrections are applied after heuristic assignment.
# Keys and values are card IDs; the value is the desired canonical card.
CANON_ID_OVERRIDES: dict[str, str] = {
    "A2a 078": "A2a 034",  # Unown: same CHECK ability as A2a 034
    "A4 084": "A4 084",  # Unown: GUARD is functionally distinct
    "A4 085": "A4 085",  # Unown: POWER is functionally distinct
    "B4 023": "B4 023",  # Moltres also with Sky Attack
    "B4 072": "B4 072",  # Kirlia also with Double Spin
    "B4b 105": "B4b 105",  # Kirlia also with Double Spin
    "B4b 305": "B4b 305",  # Kirlia also with Double Spin
}

CANON_OVERRIDES: dict[str, dict[str, str]] = {
    # misc ------------------------------------------------------------
    "A2b 041": {
        "move1_name": "Magnum Punch",
        "move1_cost": "🟠🟠🟠",
        "move1_damage": "90",
    },  # Hitmonchan: Magnum Punch
    "B3 031": {
        "move1_cost": "🔴",
        "move1_damage": "20",
    },  # Larvesta: Move cost and damage not included
    # stage  ------------------------------------------------------------
    "B2 017": {"stage": "Basic"},  # Teal Mask Ogerpon ex (was keyed by variant B2 194)
    "B2 029": {"stage": "Stage 1"},  # Alolan Ninetales ex (was keyed by variant B2 196)
    "B2 036": {"stage": "Stage 2"},  # Mega Swampert ex (was keyed by variant B2 197)
    "B2 055": {"stage": "Stage 1"},  # Toxtricity ex (was keyed by variant B2 198)
    "B2 073": {
        "stage": "Basic",
        "ability_name": "Disguise",
        "ability_effect": "When this Pokemon is first damaged by an attack after coming into play, prevent that damage",
    },  # Mimikyu ex: Blank ability text (was keyed by variant B2 199)
    "B2 087": {"stage": "Stage 2"},  # Gigalith ex (was keyed by variant B2 200)
    "B2 113": {"stage": "Basic"},  # Mega Mawile ex (was keyed by variant B2 201)
    "B2 127": {"stage": "Basic"},  # Mega Kangaskhan ex (was keyed by variant B2 202)
    "B2 066": {"stage": "Stage 2"},  # Mega Gardevoir ex (was keyed by variant B2 203)
    "B2 124": {"stage": "Basic"},  # Meowth (was keyed by variant B2 204)
    "A4 004": {"stage": "Basic"},  # Tangela (was keyed by variant B2 205)
    "A4 032": {
        "stage": "Basic",
        "weakness": None,
    },  # Magby: Incorrectly had weakness to Fire (was keyed by variant B2 206)
    "A2 023": {"stage": "Basic"},  # Magmar (was keyed by variant B2 207)
    "A4 041": {"stage": "Basic"},  # Horsea (was keyed by variant B2 208)
    "A4 042": {"stage": "Stage 1"},  # Seadra (was keyed by variant B2 209)
    "A1 081": {
        "stage": "Stage 1",
        "weakness": "Lightning",
    },  # Omanyte: Incorrectly had weakness as Grass (was keyed by variant B2 210)
    "A1 082": {
        "stage": "Stage 2",
        "weakness": "Lightning",
    },  # Omastar (Omastar is Water; base A1 082 is Lightning) (was keyed by variant B2 211)
    "A4a 023": {
        "stage": "Basic",
        "weakness": None,
    },  # Mantyke: Incorrectly had weakness as Water (was keyed by variant B2 212)
    "A4 066": {
        "stage": "Basic",
        "weakness": None,
    },  # Pichu: Incorrectly had weakness as Lightning (was keyed by variant B2 213)
    "A1 113": {"stage": "Basic"},  # Clefairy (was keyed by variant B2 214)
    "A1 114": {"stage": "Stage 1"},  # Clefable (was keyed by variant B2 215)
    "A4a 036": {"stage": "Basic"},  # Latias (was keyed by variant B2 216)
    "A4a 037": {
        "stage": "Basic",
        "ability_name": "Fantastical Floating",
        "ability_effect": "If you have Latias in play, this Pokemon has no Retreat Cost.",
    },  # Latios: Blank ability (was keyed by variant B2 217)
    "A1 154": {
        "stage": "Basic",
        "move1_damage": None,
    },  # Hitmonlee (blank; base print is 80) (was keyed by variant B2 218)
    "A1 155": {"stage": "Basic"},  # Hitmonchan (was keyed by variant B2 219)
    "A1 158": {"stage": "Stage 1"},  # Kabuto (was keyed by variant B2 220)
    "A1 159": {"stage": "Stage 2"},  # Kabutops (was keyed by variant B2 221)
    "A4 099": {"stage": "Basic"},  # Phanpy (was keyed by variant B2 222)
    "A4 101": {
        "stage": "Basic",
        "weakness": None,
    },  # Tyrogue: Incorrectly had weakness as Fighting (was keyed by variant B2 223)
    "A1a 060": {"stage": "Basic"},  # Tauros (was keyed by variant B2 224)
    "A3b 009": {
        "stage": "Stage 1",
        "ability_name": "Combust",
        "ability_effect": "Once during your turn, you may attach a Fire Energy from your discard pile to this Pokemon. If you do, do 20 damage to this Pokemon.",
    },  # Flareon ex: Blank ability (was keyed by variant B2 225)
    "A4 034": {"stage": "Basic"},  # Ho-Oh ex (was keyed by variant B2 226)
    "A4 043": {"stage": "Stage 2"},  # Kingdra ex (was keyed by variant B2 227)
    "A4 083": {
        "stage": "Stage 1",
        "ability_name": "Psychic Healing",
        "ability_effect": "Once during your turn, if this Pokemon is in the Active Spot, you may heal 30 damage from 1 of your Pokemon.",
    },  # Espeon ex: Blank ability (was keyed by variant B2 228)
    "A3b 034": {
        "stage": "Stage 1",
        "ability_name": "Happy Ribbon",
        "ability_effect": "Once during your turn, when you play this Pokemon from your hand to evolve 1 of your Pokemon, you may draw 2 cards.",
    },  # Sylveon ex: Blank ability (was keyed by variant B2 229)
    "A4 100": {"stage": "Stage 1"},  # Donphan ex (was keyed by variant B2 230)
    "A4 112": {
        "stage": "Stage 1",
        "ability_name": "Dark Chase",
        "ability_effect": "Once during your turn, if this Pokemon is in the Active Spot, you may switch in 1 of your opponent's benched Pokemon that has damage on it to the Active Spot.",
    },  # Umbreon ex: Blank ability (was keyed by variant B2 231)
    "B2 070": {"stage": "Basic"},  # Meloetta (was keyed by variant B2 233)
    # hp ------------------------------------------------------------
    "A4 177": {"hp": "60"},  # Spinarak: HP is included as "/"
    # type ------------------------------------------------------------
    "B1 027": {"type": "Grass"},  # Rillaboom: listed as Fire (B1 229 is Grass)
    "B1a 006": {
        "type": "Grass",
        "rc": "1",
    },  # Ariados: listed as Darkness (B1a 006 is Grass) (was keyed by variant B1a 070)
    "B2a 091": {"type": "Supporter"},  # Arven: Missing type (was keyed by variant B2a 115)
    "B2 148": {
        "type": "Pokemon Tool"
    },  # Metal Core Barrier: Missing type (was keyed by variant B2b 117)
    # weakness ------------------------------------------------------------
    "A1 169": {"weakness": "Fighting"},  # Nidoran M (W)
    "A1 170": {"weakness": "Fighting"},  # Nidorino (W)
    "A1 171": {"weakness": "Fighting"},  # Nidoking (W) (also fixes variant A1 241)
    "A1a 048": {"weakness": "Grass"},  # Stonjourner (W)
    "A1a 014": {"weakness": "Water"},  # Volcarona (W) (was keyed by variant P-A 028)
    "P-A 037": {"weakness": "Darkness"},  # Cresselia ex (W)
    "P-A 038": {"weakness": "Darkness"},  # Misdreavus (W)
    "B2 023": {
        "weakness": "Water",
        "stage": "Basic",
    },  # Blacephalon ex: Incorrectly has weakness as Fire (was keyed by variant B2 181; also fixes variant B2 195)
    # rc ------------------------------------------------------------
    "A2 029": {"rc": "0"},  # Infernape ex
    "A2 061": {"rc": "1"},  # Pachirisu ex: other 4 prints say 1 (variant A2 183)
    "A3 098": {"rc": "1"},  # Rockruff: other 2 prints say 1 (variant B1 310)
    "B1 069": {"rc": "2"},  # Jellicent: other 2 prints say 2 (variant B3 210)
    "B1 085": {"rc": "1"},  # Mega Ampharos ex: other 4 prints say 1 (variant B3b 103)
    "B1 088": {"rc": "1"},  # Luxray: other 2 prints say 1 (variant P-B 004)
    "B1a 062": {"rc": "1"},  # Buneary: other 5 prints say 1 (variant B1a 075)
    "B1a 034": {
        "rc": "3"
    },  # Reuniclus: alt art read as 0 (missing icon); base print is 3 (variant B1a 072)
    "B1a 037": {
        "rc": "2"
    },  # Xerneas: alt art read as 0 (missing icon); base print is 2 (variant B1a 073)
    "B1a 049": {
        "rc": "1"
    },  # Trubbish: alt art read as 0 (missing icon); base print is 1 (variant B1a 074)
    "B3 004": {
        "rc": "1",
        "ability_effect": "Each of your evolved Pokemon can use any attack from its previous Evolutions. (You still need the necessary Energy to use each attack.)",
    },  # Celebi: (variant B4b 009)
    "B3 013": {"rc": "0"},  # Budew: other 3 prints say 0 (variant B4b 246)
    "B4 068": {"rc": "0"},  # Mime Jr.: other 2 prints say 0 (variant B4b 308)
    "B4 074": {"rc": "0"},  # Wynaut: other 3 prints say 0 (variant B4b 306)
    # stage ------------------------------------------------------------
    "A3a 047": {
        "stage": "Stage 1",
    },  # Alolan Dugtrio ex: evolves from Alolan Diglett (Basic) (was keyed by variant A3a 087)
    "A3b 015": {"stage": "Stage 1"},  # Salazzle: evolves from Salandit (Basic)
    "A3b 057": {
        "stage": "Stage 1",
    },  # Snorlax ex: evolves from Munchlax (Basic) (also fixes variant A3b 084; also fixes variant A4b 288)
    "A2b 065": {
        "stage": "Stage 1"
    },  # Bibarel ex: evolves from Bidoof (Basic) (was keyed by variant B1 327)
    "B2a 082": {
        "stage": "Stage 1",
        "move1_effect": "Flip 3 coins. For each heads, discard a random Energy from your opponent's Active Pokemon.",
    },  # Maushold: evolves from Tandemaus (Basic) | Maushold: typo fixed (was keyed by variant B2a 099)
    "B3 008": {
        "stage": "Stage 2",
    },  # Mega Sceptile ex: evolves from Grovyle (Stage 1) (also fixes variant B4b 012)
    "B3 160": {"stage": "Stage 1"},  # Flapple: evolves from Applin (Basic)
    "B3 081": {
        "stage": "Stage 1",
    },  # Mega Lucario ex: evolves from Riolu (Basic) (was keyed by variant B3 204; also fixes variant B4b 418)
    "B2 028": {"stage": "Basic"},  # Alolan Vulpix: no evolves_from (was keyed by variant B4b 275)
    "B2b 110": {
        "stage": "Stage 2",
        "move1_effect": "This attack does 20 more damage for each Benched Pokemon (both yours and your opponent's).",
    },  # Haxorus: evolves from Fraxure (Stage 1) (was keyed by variant B4b 348)
    "B1 102": {
        "stage": "Stage 1",
    },  # Mega Altaria ex: evolves from Swablu (Basic) (was keyed by variant B4b 417)
    "A3b 065": {
        "stage": "Stage 1"
    },  # Greedent: evolves from Skwovet (Basic) (was keyed by variant P-A 091)
    "A4 133": {"stage": "Basic"},  # Kangaskhan: no evolves_from (was keyed by variant P-A 097)
    # move1_cost ------------------------------------------------------------
    "A2b 020": {"move1_cost": "🔵🔵🔘🔘"},  # Dondozo: Ocean Cyclone
    "A2b 056": {"move1_cost": "⚪⚪🔘"},  # Revavroom: Spinning Drift
    "A4 065": {"move1_cost": "🟡🔘🔘"},  # Lanturn ex: Flashing Signal
    "A3a 019": {"move1_cost": "🟡"},  # Tapu Koko ex: Plasma Hurricane
    "A3 104": {"move1_cost": "🟤🔘"},  # Passimian ex: Seismic Toss
    "A3a 006": {"move1_cost": "🔘🔘"},  # Buzzwole ex: Punch
    "A3 087": {"move1_cost": "🟣🔘🔘"},  # Lunala ex: Lunar Blast
    "A4 149": {"stage": "Basic", "move1_cost": "🔴🔵🟡"},  # Lugia ex: Elemental Blast
    "B2a 002": {"move1_cost": "🟢"},  # Floragato: Leaf Step
    "B3 079": {"move1_cost": "🟤"},  # Riolu: Fighting Fist
    "B3 122": {"move1_cost": "🔘"},  # Meltan: Stampede
    "B2 130": {"move1_cost": "🔘🔘"},  # Smeargle: Tail Whap
    "B4 054": {"move1_cost": "🟡"},  # Pachirisu: Crackling Snap
    # move1_damage ------------------------------------------------------------
    "A1 018": {"move1_damage": "20"},  # Bellsprout: Vine Whip
    "A1 183": {"move1_damage": "40"},  # Dratini: Ram
    "A1 079": {
        "move1_damage": "20+",
        "move1_effect": "If this Pokemon has at least 3 extra Water Energy attached, this attack does 70 more damage.",
    },  # Lapras: Hydro Pump
    "A2 019": {"move1_damage": "40+"},  # Carnivine: Flog
    "A2b 006": {"move1_damage": "40"},  # Floragato: Slash
    "A2b 040": {"move1_damage": "30"},  # Hitmonlee: Kick
    "A2b 048": {"move1_damage": "60+"},  # Paldean Clodsire ex: Venoshock
    "A3 100": {"move1_damage": "80"},  # Lycanroc: Crunch
    "A4 045": {"move1_damage": "20+"},  # Gyarados: Wild Swing
    "B1 005": {"move1_damage": None},  # Beautifly: Skill Dive
    "B2b 054": {"move1_damage": "40"},  # Axew: Sharp Fang (was keyed by variant B4b 174)
    "B4 117": {"move1_damage": "40"},  # Dragonair: Draconic Whip (was keyed by variant B4 233)
    # move2_effect ------------------------------------------------------------
    "B2a 037": {
        "move2_effect": "Discard all Water Energy from this Pokemon. This attack does 130 damage to 1 of your opponent's Pokemon.",
    },  # Chien-Pao ex (also fixes variant B2a 102; also fixes variant B2a 112; also fixes variant P-B 041; also fixes variant B4b 081)
    # ability ------------------------------------------------------------
    "A2 033": {
        "ability_name": "Thick Fat",
        "ability_effect": "This Pokémon takes -30 damage from attacks from Fire or Water Pokémon.",
    },  # Mamoswine: blank; base A2 033 has it (was keyed by variant A2 160)
    "B1 121": {
        "ability_name": "Watch Over",
        "ability_effect": "Once during your turn, you may heal 20 damage from your Active Pokemon.",
    },  # Indeedee ex: blank; base B1 121 has it (was keyed by variant B3b 104)
    "B1 160": {
        "ability_name": "Poison Point",
        "ability_effect": "If this Pokemon is in the Active Spot and is damaged by an attack from your opponent's Pokemon, the Attacking Pokemon is now Poisoned.",
    },  # Dragalge ex: blank; base B1 160 has it; blank; other prints have it (was keyed by variant B4b 148)
    "B2a 020": {
        "ability_name": "Armor",
        "ability_effect": "This Pokemon takes -30 damage from attacks.",
    },  # Armarouge ex: blank; base B2a 020 has it (was keyed by variant B2a 101, B2a 111)
    "B2b 008": {
        "ability_name": "Ignition",
        "ability_effect": "Once during your turn, when you play this Pokemon from your hand to evolve 1 of your Pokemon, you may take a Fire Energy from your Energy Zone and attach it to your Active Fire Pokemon.",
    },  # Charmeleon: blank; base B2b 008 has it (was keyed by variant B2b 092)
    "B2b 050": {
        "ability_name": "Metal Transport",
        "ability_effect": "Once during your turn, you may switch your Active Metal Pokemon with 1 of your Benched Pokemon.",
    },  # Revavroom: blank; base B2b 050 has it (was keyed by variant B2b 074)
    "B3 037": {
        "ability_name": "Frozen Flow",
        "ability_effect": "Once during your turn, if this Pokemon is in the Active Spot, you may switch out your opponent's Active Pokemon to the Bench. (Your opponent chooses the new Active Pokemon.)",
    },  # Vaporeon ex: blank; base B3 037 has it; blank; other prints have it (was keyed by variant B3b 102)
    "B3b 055": {
        "ability_name": "Massive Body",
        "ability_effect": "As long as this Pokemon is in the Active Spot, your opponent can't play any Stadium cards from their hand.",
    },  # Snorlax: blank; base B3b 055 has it (was keyed by variant B3b 100)
    "A3 149": {
        "ability_effect": "Put 1 of your Colorless Pokemon that has damage on it into your hand.",
    },  # Ilima: 'Normal' should be 'Colorless' (as on A3 191)
    "A3 155": {
        "ability_effect": "Heal 60 damage from 1 of your Stage 2 Pokemon.",
    },  # Lillie: 'Two Pokemon' is a typo for 'Stage 2' (was keyed by variant A3 197, A3 209)
    "B1 018": {
        "ability_effect": "Each of your Grass Pokemon gets +20 HP.",
    },  # Lilligant: typo fixed (was keyed by variant B1 329)
    "B1 177": {
        "ability_effect": "As long as this Pokemon is in the Active Spot, attacks used by your opponent's Active Pokemon cost 1 Colorless Energy more.",
    },  # Goomy: typo fixed (was keyed by variant B1 247)
    "B1 217": {
        "ability_effect": "Attach a Fire Energy from your discard pile to your Active Fire Pokemon.",
    },  # Flame Patch: typo fixed ('Enery'); trailing period kept (was keyed by variant B4b 203)
    "B2 151": {
        "ability_effect": "You can use this card only if your Pokemon in play have 3 or more different types of Energy attached. Move all Energy from each of your Benched Pokemon to your Active Pokemon.",
    },  # Juggler: page shows another Trainer's text; base B2 151 has the right one (was keyed by variant B2 192)
    # effect text blank or misspelled on a variant (copied from the card's other prints) ---
    "A2 022": {
        "move1_effect": "Once during your turn, you may heal 10 damage from each of your Pokémon.",
    },  # Shaymin: blank; other prints have it (was keyed by variant A2 159)
    "A3 100": {
        "move1_effect": "Flip a coin. If heads, discard a random Energy from your opponent's Active Pokemon.",
    },  # Lycanroc: blank; other prints have it
    "A3 122": {
        "move1_effect": "This Pokemon also does 10 damage to itself.",
    },  # Solgaleo ex: blank; other prints have it (was keyed by variant B1a 101)
    "A4 001": {
        "move1_effect": "Your opponent's Active Pokemon is now Poisoned.",
    },  # Oddish: blank; other prints have it (was keyed by variant B1a 088)
    "A4 002": {
        "move1_effect": "Your opponent's Active Pokemon is now Poisoned.",
    },  # Gloom: blank; other prints have it
    "B2b 043": {
        "move1_effect": "Flip a coin. If tails, this attack does nothing."
    },  # Zorua: typo fixed
    "B3 039": {
        "move1_effect": "If this Pokemon has any Fighting Energy attached, this attack does 60 more damage.",
    },  # Quagsire: typo fixed (was keyed by variant B3 162)
    "B3 062": {
        "move1_effect": "If this Pokemon has no damage on it, this attack does 30 more damage.",
    },  # Morpeko: typo fixed
    "B3 106": {
        "move1_effect": "This attack does 30 damage for each of your Benched Darkness-type Pokemon.",
    },  # Zoroark ex: typo fixed (was keyed by variant B4 230, B4b 146)
    "A3 033": {
        "move2_effect": "If this Pokémon has damage on it, this attack does 60 more damage.",
    },  # Incineroar ex: blank; other prints have it (was keyed by variant B1 318)
}


OVERRIDES: dict[str, dict[str, str | None]] = {
    # misc ------------------------------------------------------------
    "B4b 009": {
        "image": "https://img.game8.co/4479795/7ff12fab25f704898086ae6aba1a07b7.png/show",
        "url": "https://game8.co/games/Pokemon-TCG-Pocket/archives/596976",
    },  # Celebi: Incorrectly linked to Mega Pinsir ex page
    # gen ------------------------------------------------------------
    "A1a 065": {"gen": "9"},  # Mythical Slab
    "A1a 066": {"gen": "9"},  # Budding Expeditioner
    "A1a 080": {"gen": "9"},  # Budding Expeditioner
    "B4a 087": {"gen": "1"},  # Team Rocket's Boss
    "B4b 373": {"gen": "9"},  # Ancient Booster Energy Capsule
    "B4b 374": {"gen": "9"},  # Future Booster Energy Capsule
    "B4b 397": {"gen": "9"},  # Mesagoza
    "B4 113": {"gen": "9"},  # Archaludon (debuted in Gen 9; entered by hand)
    # rarity ------------------------------------------------------------
    "P-B 087": {"rarity": "Promo"},  # Mega Sceptile ex
    "P-B 088": {"rarity": "Promo"},  # Team Rocket's Scyther
    "P-B 089": {"rarity": "Promo"},  # Team Rocket's Lapras
    "P-B 090": {"rarity": "Promo"},  # Wingull
    "P-B 091": {"rarity": "Promo"},  # Team Rocket's Wobbuffet
    "P-B 092": {"rarity": "Promo"},  # Marowak
    "P-B 093": {"rarity": "Promo"},  # Fennekin
    "P-B 094": {"rarity": "Promo"},  # Meowstic
    # illustrator ------------------------------------------------------------
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
    # TODO: gen still missing on game8 (almost all Trainers, from the newer sets):
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
    #   rc: A1 040 / A3a 090 Arcanine (1 vs 2) | A1 058 / A4a 094 Golduck (1 vs 2)
    #       A2 079 / A2 168 Cresselia (1 vs 2) | A3 078 / A3 167 Cutiefly (0 vs 1)
    #       B1 068 / B3 209 Frillish (1 vs 2) | B3b 034 Fidough (0, 0, 1, 1) | B4 141 Swanna ex (1, 1, 2, 2)
    #   weakness: A4 057 / A4 170 Delibird (Metal vs Lightning)
    #   move1_cost: B4 054 / P-B 085 Pachirisu (🟡 vs 🟡🟡) | B2a 002 vs P-B 069 Floragato (🟢🟢 vs 🟢)
    #   effect numbers: A1 079, B1 108, B1 157, B1 175
    # TODO: B3b 049 Hisuian Sliggoo is Stage 1 but evolves_from is blank (Hisuian Goomy isn't in the data).
    # TODO: ~41 effect texts differ between prints only in wording or punctuation (' vs ', Pokémon vs Pokemon,
    #   trailing period). Not errors; a normalization step in the pipeline is better than overrides.
}


def apply_canon_id_overrides(cards: list[dict[str, str | None]]) -> None:
    """Apply explicit canonical-link corrections after heuristic assignment."""
    for card in cards:
        canon_id = CANON_ID_OVERRIDES.get(card.get("id"))
        if canon_id is not None:
            card["canon_id"] = canon_id


def apply_overrides(card: dict[str, str | None]) -> None:
    """Apply canonical-level functional corrections, then card-specific fixes."""
    base_overrides = CANON_OVERRIDES.get(card.get("canon_id"), {})
    invalid_fields = set(base_overrides) - FUNCTIONAL_FIELDS
    if invalid_fields:
        warnings.warn(
            f"Canonical override for {card.get('canon_id')!r} contains non-functional "
            f"fields: {sorted(invalid_fields)}; ignoring those fields.",
            UserWarning,
            stacklevel=2,
        )
        base_overrides = {
            field: value for field, value in base_overrides.items() if field in FUNCTIONAL_FIELDS
        }
    card.update(base_overrides)
    card.update(OVERRIDES.get(card["id"], {}))


def check_override_keys(cards: list[dict[str, str | None]]) -> list[str]:
    """
    Return a list of problems with the override keys (empty list = all good).
    Run it on the finished cards, e.g. in a test:  assert not check_override_keys(cards)

    - CANON_ID_OVERRIDES keys and values must be card ids.
    - CANON_OVERRIDES keys must be some card's canon_id. A key that is only a variant's id
      matches nothing, so the correction is silently never applied.
    - OVERRIDES keys must be card ids that exist.
    """
    canon_ids = {c["canon_id"] for c in cards}
    ids = {c["id"] for c in cards}
    problems = []
    for key, target in CANON_ID_OVERRIDES.items():
        if key not in ids:
            problems.append(f"CANON_ID_OVERRIDES key {key!r} is not a card id")
        if target not in ids:
            problems.append(f"CANON_ID_OVERRIDES target {target!r} is not a card id")
    for key in CANON_OVERRIDES:
        if key not in canon_ids:
            problems.append(f"CANON_OVERRIDES key {key!r} is not a canon_id of any card")
    for key in OVERRIDES:
        if key not in ids:
            problems.append(f"OVERRIDES key {key!r} is not a card id")
    return problems
