"""Explicit manual overrides for known data-quality issues in the JSON source.

When the upstream structural JSON contains incorrect values for specific cards,
those corrections live here – not scattered throughout the pipeline.

Guidelines
----------
* Every entry must have an inline comment with the card name and the reason
  for the override.
* Prefer fixing upstream (raise an issue / PR to Game8) over patching here.
* Keep this file sorted by card id for easy auditing.

Schema
------
``PATCHES`` maps ``card_id`` → ``{field_name: corrected_value}``.
The corrected value is stored as a *string* matching the base-table representation
(before ``normalize_base_types`` converts ``hp`` to ``Int64``).
"""
from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Known patches
# ---------------------------------------------------------------------------

# Format: { card_id: { field: correct_raw_value } }
PATCHES: dict[str, dict[str, str]] = {
    # A4 177: HP is incorrectly listed in the source JSON.
    "A4 177": {"hp": "60"},
}


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------


def apply_patches(
    df: pd.DataFrame,
    patches: dict[str, dict[str, str]] | None = None,
) -> pd.DataFrame:
    """Apply manual field overrides to *df*.

    Parameters
    ----------
    df:
        Table to patch.  A copy is made – the original is never mutated.
    patches:
        Override the default :data:`PATCHES` registry.  Useful in tests.

    Returns
    -------
    pd.DataFrame
        Copy of *df* with all applicable patches applied.
    """
    if patches is None:
        patches = PATCHES

    df = df.copy()
    patched_cards = 0

    for card_id, field_fixes in patches.items():
        mask = df["id"] == card_id
        if not mask.any():
            logger.debug("Patch target %r not found in dataset; skipping", card_id)
            continue

        for fld, value in field_fixes.items():
            if fld not in df.columns:
                logger.warning(
                    "Patch field %r not in DataFrame columns; skipping", fld
                )
                continue
            df.loc[mask, fld] = value

        patched_cards += 1

    total_fields = sum(len(v) for v in patches.values())
    logger.info(
        "Patches: applied %d card(s) / %d field override(s) defined",
        patched_cards,
        total_fields,
    )
    return df
