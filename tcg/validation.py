"""Validation rules for required card fields."""

import csv
from pathlib import Path

UNIVERSAL_FIELDS = (
    "id",
    "base_id",
    "name",
    "rarity",
    "category",
    "type",
    "generation",
    "illustrator",
    "expansion",
    "pack_name",
    "image",
    "url",
)
POKEMON_FIELDS = ("stage", "hp", "retreat_cost", "ko", "move1_name", "move1_cost")
TRAINER_FIELDS = ("ability_effect",)


def missing_required_fields(card: dict) -> list[str]:
    """Return required fields that are missing before manual overrides."""
    fields = list(UNIVERSAL_FIELDS)
    if card.get("category") == "Pokemon":
        fields.extend(POKEMON_FIELDS)
    elif card.get("category") == "Trainer":
        fields.extend(TRAINER_FIELDS)
    return [field for field in fields if not card.get(field)]


def find_missing_fields(cards: list[dict]) -> list[tuple[str, str, str]]:
    """Return card ID, name, and required fields missing from a card collection."""
    findings = [
        (card.get("id") or "<missing id>", card.get("name") or "<missing name>", field)
        for card in cards
        for field in missing_required_fields(card)
    ]
    return findings


def write_validation_log(
    cards: list[dict], path: Path, *, stage: str = "Pre-override"
) -> list[tuple[str, str, str]]:
    """Write missing-field diagnostics and return the findings."""
    findings = find_missing_fields(cards)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"{stage} required-field validation",
        "card_id\tname\tmissing_field",
    ]
    lines.extend(f"{card_id}\t{name}\t{field}" for card_id, name, field in findings)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return findings


def validate_csv_file(csv_path: Path, log_path: Path) -> list[tuple[str, str, str]]:
    """Read a completed CSV and write a final required-field validation report."""
    with csv_path.open(encoding="utf-8", newline="") as file:
        cards = list(csv.DictReader(file))
    return write_validation_log(cards, log_path, stage="Final")
