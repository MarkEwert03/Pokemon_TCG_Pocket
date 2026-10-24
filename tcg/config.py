"""Paths, URLs and column definitions shared across the project."""

from datetime import datetime
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJ_ROOT / "data"
LOGS_DIR = PROJ_ROOT / "logs"

# Stage 1 input: the big raw JSON from game8
RAW_JSON_PATH = DATA_DIR / "raw" / "cards.json"
# Gzipped HTML of every individual card page (so parser tweaks never need a re-download)
PAGE_CACHE_DIR = DATA_DIR / "cache" / "pages"
# Final output
OUTPUT_CSV_PATH = DATA_DIR / "full.csv"
NO_PAGES_OUTPUT_CSV_PATH = DATA_DIR / "no_pages.csv"
# Cards whose page could not be fetched on the last run
FAILED_PAGES_PATH = DATA_DIR / "failed_pages.txt"
LOG_TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
VALIDATION_LOG_PATH = LOGS_DIR / f"validation_{LOG_TIMESTAMP}.log"
FINAL_VALIDATION_LOG_PATH = LOGS_DIR / f"validation_final_{LOG_TIMESTAMP}.log"
OVERRIDE_AUDIT_LOG_PATH = LOGS_DIR / f"override_audit_{LOG_TIMESTAMP}.log"

JSON_URL = "https://game8.co/api/tool_structural_mappings/551.json"
USER_AGENT = "Mozilla/5.0 (compatible; Pokemon_TCG_Pocket-dataset-builder)"

# Ordered list of all columns each card has in the final CSV
COLUMNS = [
    "index",
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

# Cards are ordered by release family, then by the numeric card number.
SET_ORDER = (
    "A1", "A1a", "A2", "A2a", "A2b", "A3", "A3a", "A3b",
    "A4", "A4a", "A4b", "B1", "B1a", "B2", "B2a", "B2b",
    "B3", "B3a", "B3b", "B4", "B4a", "B4b", "P-A", "P-B",
)

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
