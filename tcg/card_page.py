"""
Stage 3: extract the fields the raw JSON does not have from a card page's HTML.

Fields produced (see `config.PAGE_FIELDS`):
    gen, illustrator, weakness, rc,
    pack_points, gimmick, ability_effect

This module is pure: HTML string in, dict out. No network, no disk. That makes
it easy to tweak and re-run against the cached pages.

The card-info table on a game8 card page is laid out as "label row, value row"
pairs, e.g.

    | Stage | Type | Weakness |
    | Basic | Grass | Fire    |

so we find a label cell and read the cell at the same position in the next row.
"""

import re

from bs4 import BeautifulSoup, Tag

from tcg.config import PAGE_FIELDS
from tcg.utils import clean_str, find_type_name


# ---------------------------------------------------------------- helpers
def _text(node: Tag | None) -> str | None:
    return clean_str(node.get_text(" ")) if node is not None else None


def _has_content(cell: Tag) -> bool:
    """A cell counts as non-empty if it has text *or* an icon (type icons have no text)."""
    return bool(_text(cell)) or cell.find("img") is not None


def _find_table(soup: BeautifulSoup, required_labels: tuple[str, ...]) -> Tag | None:
    """Smallest <table> whose text contains all `required_labels`."""
    best, best_len = None, None
    for table in soup.find_all("table"):
        text = table.get_text(" ")
        if all(label in text for label in required_labels):
            if best is None or len(text) < best_len:
                best, best_len = table, len(text)
    return best


def _value_below(table: Tag, label: str) -> Tag | None:
    """
    Find the cell whose text is exactly `label` and return the cell beneath it
    (same column index in the next row, else the first non-empty cell there).
    """
    for tr in table.find_all("tr"):
        cells = tr.find_all(["td", "th"], recursive=False)
        for i, cell in enumerate(cells):
            if _text(cell) != label:
                continue
            next_row = tr.find_next_sibling("tr")
            if next_row is None:
                return None
            below = next_row.find_all(["td", "th"], recursive=False)
            if i < len(below) and _has_content(below[i]):
                return below[i]
            return next((c for c in below if _has_content(c)), None)
    return None


def _extract_labeled_text(table: Tag | None, label: str) -> str | None:
    """Return the text in the value row immediately below a labeled row."""
    if table is None:
        return None
    return _text(_value_below(table, label))


def _find_moves_table(soup: BeautifulSoup) -> Tag | None:
    """The table under the '<Name> Moves and Abilities' heading."""
    heading = soup.find(
        lambda t: t.name in ("h2", "h3", "h4") and "Moves and Abilities" in t.get_text()
    )
    return heading.find_next("table") if heading else None


# ------------------------------------------------------------- extractors
def _extract_type(cell: Tag | None) -> str | None:
    """Type name from a cell holding a type icon/link (weakness)."""
    if cell is None:
        return None
    candidates = [img.get("alt", "") for img in cell.find_all("img")]
    candidates.append(cell.get_text(" "))
    for c in candidates:
        found = find_type_name(c)
        if found:
            return found
    return None


def _extract_rc(cell: Tag | None) -> str | None:
    """
    Count the energy icons in the retreat-cost cell.
    An icon labelled e.g. "Colorless 2" counts as 2. No icons => cost 0.
    """
    if cell is None:
        return None
    icons = cell.find_all("img")
    if icons:
        labels = [icon.get("alt", "").strip() for icon in icons]
        if all(label in {"", "-", "N/A"} for label in labels):
            return "0"
    else:
        labels = [link.get_text(" ", strip=True) for link in cell.find_all("a")]
        if not labels:
            labels = [cell.get_text(" ", strip=True)]
        if all(label in {"", "-", "N/A"} for label in labels):
            return "0"

    total = 0
    for icon in icons or cell.find_all("a"):
        label = icon.get("alt") or icon.get_text(" ") or ""
        if label.strip() in {"", "-", "N/A"}:
            continue
        m = re.search(r"(\d+)\s*$", label.strip())
        total += int(m.group(1)) if m else 1
    return str(total)


def _extract_pack_points(page_text: str) -> str | None:
    m = re.search(r"Crafted with ([\d,]+) Pack Points", page_text)
    return m.group(1).replace(",", "") if m else None


def _row_texts(table: Tag | None) -> list[str]:
    if table is None:
        return []
    rows = (clean_str(tr.get_text(" ")) for tr in table.find_all("tr"))
    return [r for r in rows if r]


def _extract_ability_effect(moves_table: Tag | None, ability_name: str) -> str | None:
    """
    Anchor on the ability's name (known from the JSON): the effect is either the
    rest of that row, or the whole next row.
    """
    rows = _row_texts(moves_table)
    needle = ability_name.lower()
    for i, row in enumerate(rows):
        pos = row.lower().find(needle)
        if pos == -1:
            continue
        remainder = row[pos + len(ability_name):].strip(" :-")
        if remainder:
            return remainder
        return rows[i + 1] if i + 1 < len(rows) else None
    return None


def _extract_trainer_text(moves_table: Tag | None) -> str | None:
    return clean_str(" ".join(_row_texts(moves_table)))


# ------------------------------------------------------------------ main
def parse_card_page(
    html: str, *, is_trainer: bool, ability_name: str | None = None
) -> dict[str, str | None]:
    """
    Parse one card page. Anything that can't be found is left as `None`.

    Parameters
    ----------
    html : str
        Raw HTML of the card's game8 page.
    is_trainer : bool
        Trainer cards have no weakness / retreat cost, and their text is
        returned in `ability_effect`.
    ability_name : str, optional
        The ability's name (from the JSON), used to locate its effect text.
    """
    soup = BeautifulSoup(html, "lxml")
    result: dict[str, str | None] = dict.fromkeys(PAGE_FIELDS)

    info = _find_table(soup, ("Generation", "Illustrator"))
    moves = _find_moves_table(soup)

    if info is not None:
        gen = _text(_value_below(info, "Generation"))
        m = re.search(r"\d+", gen or "")
        result["gen"] = m.group() if m else None
        result["illustrator"] = _text(_value_below(info, "Illustrator"))
        if not is_trainer:
            result["weakness"] = _extract_type(_value_below(info, "Weakness"))
            result["rc"] = _extract_rc(
                _value_below(info, "Retreat Cost")
            )

    page_text = clean_str(soup.get_text(" ")) or ""
    result["pack_points"] = _extract_pack_points(page_text)

    # Only look inside the card's own tables, so the "List of Ultra Beasts"
    # sidebar link on every page doesn't cause false positives.
    scan = f"{_text(info) or ''} {_text(moves) or ''}".lower()
    result["gimmick"] = "Ultra Beast" if "ultra beast" in scan else None

    if is_trainer:
        # Trainer pages store their text in the card-info table under
        # "Effect", rather than in a Moves and Abilities table.
        result["ability_effect"] = (
            _extract_labeled_text(info, "Effect") or _extract_trainer_text(moves)
        )
    elif ability_name:
        result["ability_effect"] = _extract_ability_effect(moves, ability_name)

    return result
