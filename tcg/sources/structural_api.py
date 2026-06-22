"""Acquisition layer: fetch raw card JSON from the Game8 structural-mappings endpoint.

Responsibilities
----------------
- HTTP GET with configurable timeout and ``updatedAt`` query parameter.
- Attach ``_meta`` with source URL, fetch timestamp, and record count.
- Save/load timestamped snapshots to/from ``data/raw/``.

Nothing in this module transforms or interprets the payload – it is stored
verbatim so that every downstream step is reproducible from the same file.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import requests

ENDPOINT = "https://game8.co/api/tool_structural_mappings/551.json"
DEFAULT_TIMEOUT = 30

logger = logging.getLogger(__name__)


def fetch_raw(
    updated_at: int | None = None,
    endpoint: str = ENDPOINT,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    """Fetch the raw structural JSON from the Game8 endpoint.

    Parameters
    ----------
    updated_at:
        Unix timestamp sent as the ``updatedAt`` query parameter.
        Defaults to the current wall-clock time.
    endpoint:
        Base URL of the structural-mappings API.
    timeout:
        HTTP request timeout in seconds.

    Returns
    -------
    dict
        Raw JSON payload with a ``_meta`` key added containing:

        * ``source_url``   – the full URL that was requested
        * ``fetched_at``   – Unix timestamp used for the request
        * ``record_count`` – number of card records in the payload

    Raises
    ------
    requests.HTTPError
        If the server responds with a non-2xx status code.
    """
    if updated_at is None:
        updated_at = int(time.time())

    url = f"{endpoint}?updatedAt={updated_at}"
    logger.info("Fetching structural data from %s", url)

    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()

    raw: dict = resp.json()
    cards = raw.get("cardArraySchema", {}).get("cards", [])
    record_count = len(cards)
    logger.info("Fetched %d card records", record_count)

    raw.setdefault("_meta", {})
    raw["_meta"]["source_url"] = url
    raw["_meta"]["fetched_at"] = updated_at
    raw["_meta"]["record_count"] = record_count

    return raw


def save_snapshot(raw: dict, raw_dir: Path) -> Path:
    """Persist a raw payload to a timestamped JSON file inside *raw_dir*.

    The file is named ``raw_{fetched_at}.json`` where ``fetched_at`` comes
    from ``raw["_meta"]["fetched_at"]``; if that key is absent the current
    time is used.

    Parameters
    ----------
    raw:
        Raw JSON dict as returned by :func:`fetch_raw`.
    raw_dir:
        Target directory (created if it does not exist).

    Returns
    -------
    Path
        Absolute path to the saved file.
    """
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    ts = raw.get("_meta", {}).get("fetched_at", int(time.time()))
    path = raw_dir / f"raw_{ts}.json"

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(raw, fh, ensure_ascii=False, indent=2)

    logger.info("Saved raw snapshot → %s", path)
    return path


def load_snapshot(path: Path) -> dict:
    """Load a previously saved raw snapshot from *path*.

    Parameters
    ----------
    path:
        Path to a ``raw_*.json`` file created by :func:`save_snapshot`.

    Returns
    -------
    dict
        The raw JSON payload.
    """
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)
