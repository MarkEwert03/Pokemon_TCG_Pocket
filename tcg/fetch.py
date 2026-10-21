"""
All network access lives here:
- download the big raw JSON
- download individual card pages, caching each one gzipped on disk
"""

import gzip
import json
import time
from pathlib import Path

import requests

from tcg.config import JSON_URL, PAGE_CACHE_DIR, USER_AGENT

HEADERS = {"User-Agent": USER_AGENT}


def download_raw_json(dest: Path, updated_at: int | None = None) -> dict:
    """
    Download the card database JSON and save it to `dest`.

    The endpoint takes an `updatedAt` unix timestamp (defaults to now).
    """
    updated_at = updated_at or int(time.time())
    resp = requests.get(JSON_URL, params={"updatedAt": updated_at}, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def ensure_raw_json(path: Path, refresh: bool = False) -> Path:
    """Make sure the raw JSON exists locally, downloading it if needed."""
    if refresh or not path.exists():
        print(f"Downloading card database -> {path}")
        download_raw_json(path, updated_at=1790751231)
    return path


def _cache_path(url: str) -> Path:
    # ".../archives/476002" -> "476002.html.gz"
    return PAGE_CACHE_DIR / f"{url.rstrip('/').split('/')[-1]}.html.gz"


def get_card_html(
    url: str, refresh: bool = False, delay: float = 0.25, retries: int = 3
) -> str | None:
    """
    Return the HTML of a card page, using the on-disk cache when possible.

    Returns `None` if the page does not exist (404).
    Raises `requests.RequestException` if the page still fails after `retries`.
    """
    path = _cache_path(url)
    if path.exists() and not refresh:
        return gzip.decompress(path.read_bytes()).decode("utf-8")

    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()

            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(gzip.compress(resp.content))
            time.sleep(delay)  # be polite to the server
            return resp.content.decode("utf-8", errors="replace")
        except requests.RequestException as e:
            last_error = e
            time.sleep(2**attempt)

    raise last_error  # type: ignore[misc]
