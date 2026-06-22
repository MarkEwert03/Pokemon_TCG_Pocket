"""Normalisation layer: flatten nested JSON into a stable, typed base DataFrame.

Responsibilities
----------------
- Define the canonical ``BASE_COLUMNS`` list and ``SCHEMA_VERSION``.
- Convert the structural JSON's nested ``moves`` list into wide columns.
- Discard the noisy 3rd-move slot (contains pack-drop percentages, not moves).
- Enforce stable column types (nullable int for ``hp``, stripped strings, etc.).

This module does **not** interpret values (no symbol conversions, no patches).
All transformation is handled by the ``tcg.enrich`` layer.
"""
from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "1.0"

# Ordered list of columns that define the base schema.
# Downstream code must not depend on positional indices – use column names.
BASE_COLUMNS: list[str] = [
    "id",
    "name",
    "card_type",
    "pokemon_type",
    "hp",
    "ex",
    "stage",
    "rarity",
    "set",
    "subset",
    "ability_name",
    "ability_effect",
    "move1_name",
    "move1_cost",
    "move1_damage",
    "move1_description",
    "move2_name",
    "move2_cost",
    "move2_damage",
    "move2_description",
    "image",
    "page",
]


def _valid_moves(moves: list[dict]) -> list[dict]:
    """Return only moves that have a non-empty ``name`` field.

    The structural JSON always includes a noisy 3rd slot whose ``name`` is
    empty and whose ``damage`` / ``energy_cost`` contain pack-drop percentages
    or set codes.  Filtering by non-empty name cleanly removes those slots.
    """
    return [m for m in moves if isinstance(m, dict) and str(m.get("name", "")).strip()]


def flatten_to_base_table(raw: dict) -> pd.DataFrame:
    """Convert raw structural JSON into a one-row-per-card DataFrame.

    Rules applied:
    * Only the first two *valid* (non-empty name) moves are kept.
    * The noisy 3rd-slot move is silently discarded.
    * Every BASE_COLUMNS column is always present; missing values become ``""``.
    * The ``ability_effect`` column is always ``""`` – this field is not
      available in the structural JSON and must be filled by an enrichment step
      (e.g. from the HTML scraper pipeline).

    Parameters
    ----------
    raw:
        Raw payload as returned by :func:`tcg.sources.structural_api.fetch_raw`
        or loaded via :func:`tcg.sources.structural_api.load_snapshot`.

    Returns
    -------
    pd.DataFrame
        DataFrame with exactly :data:`BASE_COLUMNS` columns and one row per card.
    """
    cards: list[dict[str, Any]] = raw.get("cardArraySchema", {}).get("cards", [])

    if not cards:
        logger.warning("No cards found in raw JSON; returning empty base table")
        return pd.DataFrame(columns=BASE_COLUMNS)

    rows: list[dict[str, Any]] = []

    for card in cards:
        valid = _valid_moves(card.get("moves", []))
        m1 = valid[0] if len(valid) > 0 else {}
        m2 = valid[1] if len(valid) > 1 else {}

        row: dict[str, Any] = {
            "id":               card.get("id", ""),
            "name":             card.get("name", ""),
            "card_type":        card.get("card_type", ""),
            "pokemon_type":     card.get("pokemon_type", ""),
            "hp":               card.get("hp", ""),
            "ex":               card.get("ex", ""),
            "stage":            card.get("evolution_stage", ""),
            "rarity":           card.get("rarity", ""),
            "set":              card.get("set", ""),
            "subset":           card.get("subset", ""),
            "ability_name":     card.get("ability", ""),
            "ability_effect":   "",
            "move1_name":        m1.get("name", ""),
            "move1_cost":        m1.get("energy_cost", ""),
            "move1_damage":      m1.get("damage", ""),
            "move1_description": m1.get("description", ""),
            "move2_name":        m2.get("name", ""),
            "move2_cost":        m2.get("energy_cost", ""),
            "move2_damage":      m2.get("damage", ""),
            "move2_description": m2.get("description", ""),
            "image":            card.get("image_url", ""),
            "page":             card.get("archive_url", ""),
        }
        rows.append(row)

    df = pd.DataFrame(rows, columns=BASE_COLUMNS)
    logger.info("Flattened %d cards into base table", len(df))
    return df


def normalize_base_types(df: pd.DataFrame) -> pd.DataFrame:
    """Enforce stable column types on the base DataFrame.

    Transformations applied (on a copy – original is never mutated):

    * ``id`` and ``name`` – stripped strings.
    * ``hp`` – nullable integer (``Int64``); non-numeric values become ``pd.NA``.
    * All remaining ``object`` columns – empty strings become ``None``.

    Parameters
    ----------
    df:
        Raw output of :func:`flatten_to_base_table`.

    Returns
    -------
    pd.DataFrame
        Copy of *df* with enforced types.
    """
    df = df.copy()

    df["id"] = df["id"].astype(str).str.strip()
    df["name"] = df["name"].astype(str).str.strip()
    df["hp"] = pd.to_numeric(df["hp"], errors="coerce").astype("Int64")

    # Normalise empty strings → None in all remaining string columns
    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].replace("", None)

    return df
