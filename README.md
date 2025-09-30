# Pokemon_TCG_Pocket

A small Python utility to parse HTML tables containing [Pokémon TCG (Trading Card Game) Pocket card data](https://game8.co/games/Pokemon-TCG-Pocket/archives/482685) and export them into a structured CSV format.

---

## 🚀 Features

- Parses `<table>` elements with Pokémon TCG Pocket card data sourced from Game8
- Extracts card attributes such as number, name, type, HP, image URL, rarity, and more
- Outputs the data to a well-formatted CSV file
- Supports multiple rows (multiple cards) per HTML file
- Uses `pathlib` for robust, cross-platform file handling
- Designed for easy modular extension

---

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/MarkEwert03/Pokemon_TCG_Pocket
   cd Pokemon_TCG_Pocket
   ```

2. (Optional but recommended) Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate # On Windows use: .venv\Scripts\activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
---

## 📥 Input Format
**No input needed!** The tables are directly fetched from the [game8 archive](https://game8.co/games/Pokemon-TCG-Pocket/archives/482685) via the `requests` library.
In this way, changes made to the source table will automatically be updated in the resulting csv whenever the script is re-run.

---

## 🧾 Output Format
The file containing all the parsed and processed data is located at [`data/full.csv`](https://github.com/MarkEwert03/Pokemon_TCG_Pocket/blob/main/data/full.csv)

<details>
<summary>Click to expand column descriptions</summary>

Columns include:
- `id`
  - The card’s unique identifier combining set and index.
  - Examples: "A1 001", "A2b 107", "P-A 034"
- `name`
  - The full name of the Pokémon or trainer.
  - Examples: "Bulbasaur", "Gengar ex", "Brock", "Rocky Helmet"
- `rarity`
  - Visual rarity denoted by a series of symbols
  - Examples: "◇", "☆☆☆", "♛", "✸✸"
- `stage`
  - Evolutionary stage of Pokémon
  - Examples: "Basic", "Stage 1", "Stage 2"
- `HP`
  - Hit points (health) of the Pokémon card.
  - Examples: "70", "100", "180"
- `type`
  - Pokémon TCG type or trainer card classification.
  - Examples: "Grass", "Colorless", "Supporter", "Item"
- `weakness`
  - The TCG type this Pokémon is weak against.
  - Examples: "Fire", "Lightning", "Darkness"
- `retreat_cost`
  - Number of energy symbols needed to retreat the Pokémon.
  - Examples: "1", "4"
- `ultra_beast`
  - Whether the card is classified as an Ultra Beast.
  - Examples: "No", "Yes"
- `generation`
  - The mainline game generation the Pokémon originates from.
  - Examples: "1", "5", "9"
- `illustrator`
  - The name of the card's illustrator.
  - Examples: "Narumi Sato", "HYOGONOSUKE", "0313"
- `pack_name`
  - The name of the pack in which the card appears.
  - Examples: "Genetic Apex (A1) Mewtwo", "Space-Time Smackdown (A2) Any", "Promo Promo-A"
- `pack_points`
  - The number of pack points required to exchange for this card.
  - Examples: "35", "500", "2500"
- `ability_name`
  - The name of the Pokémon's ability (if the card has one).
  - Examples: "Powder Heal", "CHECK", "Rough Skin"
- `ability_effect`
  - Description of the ability's effect. Also used to store Trainer card text.
  - Examples: "Once during your turn, you may heal 20 damage from each of your Pokémon.", "Draw 2 cards."
- `move1_name`
  - The name of the first move.
  - Examples: "Vine Whip", "Bite", "Double-Edge"
- `move1_cost`
  - The energy required to perform the first move (emoji format).
  - Examples: "🟢*️⃣", "🔵🟡", "🟤"
- `move1_damage`
  - The damage dealt by the first move.
  - Examples: "40", "10+", "50x"
- `move1_effect`
  - The description of additional effects text for the first move (if any).
  - Examples: "Heal 30 damage from this Pokémon.", "Flip 2 coins. This attack does 30 more damage for each heads."
- `move2_name`
  - Name of the second move (if present). If an ability was present, the move info appears here.
  - Example: "Crimson Storm"
- `move2_cost`
  - The energy required to perform the second move.
  - Example: "🔴🔴*️⃣ *️⃣"
- `move2_damage`
  - The damage dealt by the second move.
  - Example: "200"
- `move2_effect`
  - The description of additional effects for the second move.
  - Example: "Discard 2 Fire Energy from this Pokémon."
- `image`
  - URL to the full-size image of the card.
  - Example: "https://img.game8.co/3998332/91c4f79b2b3b4206205bf69db8dd3d1e.png/show"
- `url`
  - Link to the card's dedicated page on Game8.
  - Example: "https://game8.co/games/Pokemon-TCG-Pocket/archives/476002"

</details>

---

## 🧪 How to Run
From the project root directory, type:
   ```bash
   python run.py
   ```

## 💻 Developers
While working on this project, it is often convenient to check the result of the extracted card (stored as a dict). There is a helper method in `tests/debug.py` that accomplishes this.

From the project root directory, type `python -m tests.debug "<id>"` where `<id>` is the unique ID number for each card (e.g. A1 001)

Example:
   ```bash
    python -m tests.debug "A1 001"
   ```
   ```json
   {
     "number": "A1 001",
     "name": "Bulbasaur",
     "rarity": "◇",
     "stage": "Basic",
     "HP": "70",
     "type": "Grass",
     "weakness": "Fire",
     "retreat_cost": "1",
     "ultra_beast": "No",
     "generation": "1",
     "illustrator": "Narumi Sato",
     "pack_name": "Genetic Apex (A1) Mewtwo",
     "pack_points": "35",
     "ability_name": null,
     "ability_effect": null,
     "move1_name": "Vine Whip",
     "move1_cost": "🟢*️⃣",
     "move1_damage": "40",
     "move1_effect": null,
     "move2_name": null,
     "move2_cost": null,
     "move2_damage": null,
     "move2_effect": null,
     "image": "https://img.game8.co/3998332/91c4f79b2b3b4206205bf69db8dd3d1e.png/show",
     "url": "https://game8.co/games/Pokemon-TCG-Pocket/archives/476002"
   }
   ```

