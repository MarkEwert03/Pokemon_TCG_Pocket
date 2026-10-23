"""Paths, URLs and column definitions shared across the project."""

from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJ_ROOT / "data"

# Stage 1 input: the big raw JSON from game8
RAW_JSON_PATH = DATA_DIR / "raw" / "cards.json"
# Gzipped HTML of every individual card page (so parser tweaks never need a re-download)
PAGE_CACHE_DIR = DATA_DIR / "cache" / "pages"
# Final output
OUTPUT_CSV_PATH = DATA_DIR / "full.csv"
NO_PAGES_OUTPUT_CSV_PATH = DATA_DIR / "no_pages.csv"
# Cards whose page could not be fetched on the last run
FAILED_PAGES_PATH = DATA_DIR / "failed_pages.txt"
VALIDATION_LOG_PATH = DATA_DIR / "validation.log"
FINAL_VALIDATION_LOG_PATH = DATA_DIR / "validation_final.log"

JSON_URL = "https://game8.co/api/tool_structural_mappings/551.json"
USER_AGENT = "Mozilla/5.0 (compatible; Pokemon_TCG_Pocket-dataset-builder)"

# Ordered list of all columns each card has in the final CSV
COLUMNS = [
    "id",
    "base_id",
    "name",
    "rarity",
    "category",
    "stage",
    "evolves_from",
    "hp",
    "type",
    "weakness",
    "retreat_cost",
    "classification",
    "ko",
    "generation",
    "illustrator",
    "expansion",
    "pack_name",
    "pack_points",
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
    "image",
    "url",
]

# Columns that only exist on the individual card page (not in the raw JSON)
PAGE_FIELDS = (
    "generation",
    "illustrator",
    "weakness",
    "retreat_cost",
    "pack_points",
    "classification",
    "ability_effect",
)
