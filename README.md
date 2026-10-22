# Pokemon_TCG_Pocket

Builds a clean CSV of every Pokémon TCG Pocket card (one row per card) from [Game8's card database](https://game8.co/games/Pokemon-TCG-Pocket/archives/482685).

Visualizations for the dataset can be found in [analysis.ipynb](https://github.com/MarkEwert03/Pokemon_TCG_Pocket/blob/main/analysis.ipynb).

---

## How it works

```
 game8 JSON API ──► data/raw/cards.json ──► tcg/from_json.py ──┐
                                                                ├─► merge ─► overrides ─► data/full.csv
 each card's archive_url ─► data/cache/pages ─► tcg/card_page.py ┘
```

1. **Download** the big raw JSON (once; kept in `data/raw/cards.json`).
2. **Convert** it to one flat dict per card. The JSON already has name, rarity, stage, HP, type, pack, ability name, moves (name / cost / damage / effect), image and URL.
3. **Scrape** each card's own page (the JSON gives its `archive_url`) for what the JSON lacks: `generation`, `illustrator`, `weakness`, `retreat_cost`, `pack_points`, `ultra_beast`, `ability_effect`. Every page is cached gzipped on disk, so re-runs are fast and you can tweak the parser without re-downloading.
4. **Apply manual overrides** (`tcg/overrides.py`) for cards where Game8 is wrong or missing data.
5. **Write** `data/full.csv`.

---

## 🛠️ Installation

```bash
git clone https://github.com/MarkEwert03/Pokemon_TCG_Pocket
cd Pokemon_TCG_Pocket
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 🧪 How to Run

From the project root:

```bash
python run.py                       # full pipeline -> data/full.csv
```

Useful options:

| Command | What it does |
|---|---|
| `python run.py --no-pages` | JSON only (fast, offline-ish). Page-only columns stay blank. |
| `python run.py --refresh-json` | Re-download the raw JSON (do this when new sets are released). |
| `python run.py --refresh-pages` | Ignore the page cache and re-download every card page. |
| `python run.py --limit 20` | Only process the first 20 cards (good for testing). |
| `python run.py --json path/to/file.json` | Use a JSON file you already have. |
| `python run.py --debug "A1 001"` | Print one finished card as JSON. |

At the end of every run a report shows how many values were filled per column. A column that's suddenly near 0 means a parser broke. Cards whose page failed to download are listed in `data/failed_pages.txt`; just re-run to retry them (successful pages are cached).

## 💻 Developers

```bash
pip install -r requirements-dev.txt
python -m pytest                                  # unit tests (no network needed)
python scripts/compare_csv.py old.csv data/full.csv --show weakness retreat_cost
```

### Project layout

```
run.py                 command-line entry point
tcg/
  config.py            paths, URLs, COLUMNS
  fetch.py             all network access (JSON download, cached page download)
  from_json.py         raw JSON -> flat card dict
  card_page.py         card page HTML -> generation, illustrator, weakness, ...
  overrides.py         manual per-card fixes
  pipeline.py          glues the stages together, writes the CSV
  utils.py             string + energy-symbol helpers
tests/                 pytest suite
scripts/compare_csv.py diff two CSVs column by column
archive/               the previous approaches, kept for reference (not used)
data/
  raw/cards.json       raw JSON from game8
  cache/pages/         cached card pages (git-ignored)
  full.csv             final output
```

### Fixing a wrong or missing value

Add an entry to `OVERRIDES` in `tcg/overrides.py` with a comment saying why.

---

## 🧾 Output Format

The finished data is at [`data/full.csv`](https://github.com/MarkEwert03/Pokemon_TCG_Pocket/blob/main/data/full.csv). Empty cells mean "not applicable / not available".

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
  - Evolutionary stage of Pokémon (blank for Trainers)
  - Examples: "Basic", "Stage 1", "Stage 2"
- `hp`
  - Hit points (health) of the Pokémon card.
  - Examples: "70", "100", "180"
- `type`
  - Pokémon TCG type or trainer card classification.
  - Examples: "Grass", "Colorless", "Supporter", "Item", "Pokemon Tool"
- `weakness`
  - The TCG type this Pokémon is weak against.
  - Examples: "Fire", "Lightning", "Darkness"
- `retreat_cost`
  - Number of energy symbols needed to retreat the Pokémon.
  - Examples: "0", "1", "4"
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
  - The name of the card's first attack.
  - Examples: "Vine Whip", "Bite", "Double-Edge"
- `move1_cost`
  - The energy required for the first attack (emoji format; 🔘 = Colorless).
  - Examples: "🟢🔘", "🔵🟡", "🟤"
- `move1_damage`
  - The damage dealt by the first attack.
  - Examples: "40", "10+", "50x"
- `move1_effect`
  - Additional effect text for the first attack (if any).
  - Examples: "Heal 30 damage from this Pokémon.", "Flip 2 coins. This attack does 30 more damage for each heads."
- `move2_name`
  - Name of the second attack (if present).
  - Example: "Crimson Storm"
- `move2_cost`
  - The energy required for the second attack.
  - Example: "🔴🔴🔘🔘"
- `move2_damage`
  - The damage dealt by the second attack.
  - Example: "200"
- `move2_effect`
  - Additional effect text for the second attack.
  - Example: "Discard 2 Fire Energy from this Pokémon."
- `image`
  - URL to the full-size image of the card.
  - Example: "https://img.game8.co/3998332/91c4f79b2b3b4206205bf69db8dd3d1e.png/show"
- `url`
  - Link to the card's dedicated page on Game8.
  - Example: "https://game8.co/games/Pokemon-TCG-Pocket/archives/476002"

</details>

### Example (`python run.py --debug "A1 001"`)

```json
{
  "id": "A1 001",
  "name": "Bulbasaur",
  "rarity": "◇",
  "stage": "Basic",
  "hp": "70",
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
  "move1_cost": "🟢🔘",
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
