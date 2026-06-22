"""Validation layer: non-mutating data-quality checks on the base (or enriched) DataFrame.

All checks return :class:`ValidationIssue` objects; they never modify the
DataFrame.  The exit code of the ``validate`` CLI subcommand is non-zero when
at least one *error*-severity issue is found.

Checks performed by :func:`validate_cards`
-------------------------------------------
1. Required columns present.
2. ``id`` non-null and unique.
3. ``card_type`` is within the expected domain.
4. ``hp`` is present for all Pokémon cards.
5. Move consistency – if ``moveN_name`` is empty the cost/damage/description
   must also be empty.
6. ``image`` and ``page`` URLs have the expected ``http(s)://`` prefix.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS: list[str] = [
    "id", "name", "card_type", "rarity", "set", "image", "page",
]

VALID_CARD_TYPES: frozenset[str] = frozenset(
    {"Pokemon", "Trainer", "Item", "Supporter", "Pokemon Tool"}
)

_URL_RE = re.compile(r"^https?://")


@dataclass
class ValidationIssue:
    """A single data-quality finding produced by :func:`validate_cards`."""

    severity: str           # ``"error"`` or ``"warning"``
    check: str              # short machine-readable check name
    message: str            # human-readable description
    row_ids: list[str] = field(default_factory=list)


def validate_cards(df: pd.DataFrame) -> list[ValidationIssue]:
    """Run a battery of data-quality checks on *df*.

    The function is **non-mutating** – *df* is never modified.

    Parameters
    ----------
    df:
        A base or enriched card table.

    Returns
    -------
    list[ValidationIssue]
        All issues found.  An empty list means every check passed.
    """
    issues: list[ValidationIssue] = []

    # ── 1. Required columns ────────────────────────────────────────────────
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        issues.append(
            ValidationIssue(
                severity="error",
                check="required_columns",
                message=f"Missing required columns: {missing_cols}",
            )
        )
        logger.warning("Aborting further checks – required columns absent")
        return issues

    # ── 2. id non-null and unique ──────────────────────────────────────────
    null_mask = df["id"].isna() | (df["id"].astype(str).str.strip() == "")
    if null_mask.any():
        issues.append(
            ValidationIssue(
                severity="error",
                check="id_non_null",
                message=f"{null_mask.sum()} row(s) have a null/empty id",
            )
        )

    dup_mask = df["id"].duplicated(keep=False)
    if dup_mask.any():
        dup_vals: list[str] = df.loc[dup_mask, "id"].unique().tolist()
        issues.append(
            ValidationIssue(
                severity="error",
                check="id_unique",
                message=f"{len(dup_vals)} duplicate id value(s): {dup_vals[:10]}",
                row_ids=dup_vals[:10],
            )
        )

    # ── 3. card_type domain ────────────────────────────────────────────────
    bad_type_mask = df["card_type"].notna() & ~df["card_type"].isin(VALID_CARD_TYPES)
    if bad_type_mask.any():
        bad_vals = df.loc[bad_type_mask, "card_type"].unique().tolist()
        issues.append(
            ValidationIssue(
                severity="warning",
                check="card_type_domain",
                message=f"Unexpected card_type value(s): {bad_vals}",
                row_ids=df.loc[bad_type_mask, "id"].tolist()[:10],
            )
        )

    # ── 4. hp present for Pokémon cards ────────────────────────────────────
    if "hp" in df.columns:
        pokemon_mask = df["card_type"] == "Pokemon"
        missing_hp = pokemon_mask & df["hp"].isna()
        if missing_hp.any():
            issues.append(
                ValidationIssue(
                    severity="warning",
                    check="hp_numeric",
                    message=f"{missing_hp.sum()} Pokémon card(s) with missing hp",
                    row_ids=df.loc[missing_hp, "id"].tolist()[:10],
                )
            )

    # ── 5. Move consistency ────────────────────────────────────────────────
    for n in (1, 2):
        name_col = f"move{n}_name"
        for sub in ("cost", "damage", "description"):
            sub_col = f"move{n}_{sub}"
            if name_col not in df.columns or sub_col not in df.columns:
                continue
            inconsistent = df[df[name_col].isna() & df[sub_col].notna()]
            if not inconsistent.empty:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        check=f"move{n}_consistency",
                        message=(
                            f"{len(inconsistent)} row(s) have empty {name_col} "
                            f"but non-empty {sub_col}"
                        ),
                        row_ids=inconsistent["id"].tolist()[:10],
                    )
                )

    # ── 6. URL shape ───────────────────────────────────────────────────────
    for url_col in ("image", "page"):
        if url_col not in df.columns:
            continue
        bad_url_mask = df[url_col].notna() & ~df[url_col].astype(str).str.match(
            _URL_RE
        )
        if bad_url_mask.any():
            issues.append(
                ValidationIssue(
                    severity="warning",
                    check=f"{url_col}_url_shape",
                    message=f"{bad_url_mask.sum()} row(s) have a malformed {url_col} URL",
                    row_ids=df.loc[bad_url_mask, "id"].tolist()[:10],
                )
            )

    if not issues:
        logger.info("All validation checks passed (%d cards)", len(df))
    else:
        errors = sum(1 for i in issues if i.severity == "error")
        warnings = sum(1 for i in issues if i.severity == "warning")
        logger.warning("Validation: %d error(s), %d warning(s)", errors, warnings)

    return issues
