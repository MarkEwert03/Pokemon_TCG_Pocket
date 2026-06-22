"""Enrichment layer: derive and transform fields from the base table.

Transformations provided
------------------------
* :func:`apply_energy_symbols`    – convert ``moveN_cost`` text → emoji symbols
* :func:`convert_ex_field`        – map raw ``ex`` string → numeric ordinal
* :func:`fix_pokemon_type`        – normalise ``"Tool"`` → ``"Pokemon Tool"``
* :func:`clear_trainer_move_fields` – blank move costs / stage for Trainer cards
* :func:`enrich_cards`            – convenience wrapper that calls all of the above

All functions return a **copy** of the input DataFrame; the original is never
mutated.
"""
from __future__ import annotations

import logging
import re

import pandas as pd

from tcg.utils import parse_energy_cost

logger = logging.getLogger(__name__)

# Separator between energy-cost tokens in the structural JSON.
# Examples: "Grass:Colorless 2", "Water 2;Colorless"
_ENERGY_SEP = re.compile(r"[:;]")

# Card types that represent Trainer cards (no moves, no stage).
_TRAINER_TYPES: frozenset[str] = frozenset({"Item", "Supporter", "Pokemon Tool"})


# ── Energy symbols ────────────────────────────────────────────────────────────


def _energy_text_to_symbols(text: str | None) -> str:
    """Convert a raw energy-cost string to a run of emoji symbols.

    The structural JSON encodes energy costs as ``"Type Count:Type Count"``,
    e.g. ``"Grass:Colorless 2"`` or ``"Fire 2:Colorless 2"``.  Each colon-
    or semicolon-separated token is passed through
    :func:`tcg.utils.parse_energy_cost`.

    Returns an empty string for falsy input.
    """
    if not text or not str(text).strip():
        return ""
    tokens = [t.strip() for t in _ENERGY_SEP.split(str(text))]
    return "".join(parse_energy_cost(t) for t in tokens if t)


def apply_energy_symbols(df: pd.DataFrame) -> pd.DataFrame:
    """Replace raw energy-cost text in ``move1_cost`` and ``move2_cost`` with
    emoji symbol strings.

    Parameters
    ----------
    df:
        Base table as produced by
        :func:`tcg.normalize.base_schema.flatten_to_base_table`.

    Returns
    -------
    pd.DataFrame
        Copy of *df* with move cost columns converted to symbol strings.
    """
    df = df.copy()
    for col in ("move1_cost", "move2_cost"):
        if col in df.columns:
            df[col] = df[col].apply(_energy_text_to_symbols)
    logger.info("Applied energy symbols to move cost columns")
    return df


# ── ex ordinal ────────────────────────────────────────────────────────────────


def convert_ex_field(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the raw ``ex`` string field to a numeric ordinal.

    Mapping:

    =====================  =====
    Raw value              Result
    =====================  =====
    ``"ex"``               2
    ``"Mega Evolution ex"``  3
    ``""`` on a Pokémon    1
    ``""`` on a Trainer    0
    =====================  =====

    Parameters
    ----------
    df:
        Must contain ``ex`` and ``card_type`` columns.

    Returns
    -------
    pd.DataFrame
        Copy of *df* with ``ex`` as integer values.
    """
    df = df.copy()

    def _convert(row: pd.Series) -> int:
        val = str(row.get("ex") or "").strip()
        if val == "ex":
            return 2
        if val == "Mega Evolution ex":
            return 3
        return 1 if row.get("card_type") == "Pokemon" else 0

    df["ex"] = df.apply(_convert, axis=1)
    logger.info("Converted ex field to numeric ordinal")
    return df


# ── pokemon_type normalisation ────────────────────────────────────────────────


def fix_pokemon_type(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise the ``pokemon_type`` value ``"Tool"`` to ``"Pokemon Tool"``.

    The structural JSON uses ``"Tool"`` for Pokémon Tool cards; the scraper
    pipeline and ``full.csv`` use the more descriptive ``"Pokemon Tool"``.

    Parameters
    ----------
    df:
        Must contain ``pokemon_type`` column.

    Returns
    -------
    pd.DataFrame
        Copy of *df* with the corrected ``pokemon_type``.
    """
    df = df.copy()
    df.loc[df["pokemon_type"] == "Tool", "pokemon_type"] = "Pokemon Tool"
    return df


# ── Trainer card cleanup ──────────────────────────────────────────────────────


def clear_trainer_move_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Blank out move-cost and stage columns for Trainer cards.

    Trainer cards (``"Item"``, ``"Supporter"``, ``"Pokemon Tool"``) have no
    moves; any values in those columns come from source noise.

    Parameters
    ----------
    df:
        Must contain ``card_type``, move cost, and ``stage`` columns.

    Returns
    -------
    pd.DataFrame
        Copy of *df* with Trainer-card move and stage fields set to ``""``.
    """
    df = df.copy()
    is_trainer = df["card_type"].isin(_TRAINER_TYPES)
    for col in ("move1_cost", "move2_cost", "stage"):
        if col in df.columns:
            df.loc[is_trainer, col] = ""
    return df


# ── Convenience wrapper ───────────────────────────────────────────────────────


def enrich_cards(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all enrichment transformations in the correct order.

    Steps executed:

    1. :func:`apply_energy_symbols`
    2. :func:`convert_ex_field`
    3. :func:`fix_pokemon_type`
    4. :func:`clear_trainer_move_fields`

    Parameters
    ----------
    df:
        Base table (output of :func:`tcg.normalize.base_schema.flatten_to_base_table`).

    Returns
    -------
    pd.DataFrame
        Enriched table.
    """
    df = apply_energy_symbols(df)
    df = convert_ex_field(df)
    df = fix_pokemon_type(df)
    df = clear_trainer_move_fields(df)
    return df
