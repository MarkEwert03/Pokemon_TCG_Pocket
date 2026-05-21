"""Central configuration for the TCG Pocket JSON data pipeline.

Values can be provided programmatically via the :class:`Config` dataclass or
loaded from environment variables with :meth:`Config.from_env`.

Environment variables (all optional, fall back to the defaults shown):
    TCG_RAW_DIR       – path for raw JSON snapshots      (default: data/raw)
    TCG_BASE_DIR      – path for normalised base tables  (default: data/base)
    TCG_ENRICHED_DIR  – path for enriched tables         (default: data/enriched)
    TCG_REPORTS_DIR   – path for validation reports      (default: data/reports)
    TCG_ENDPOINT      – structural-mappings API URL
    TCG_TIMEOUT       – HTTP timeout in seconds          (default: 30)
    TCG_OUTPUT_FORMAT – csv or parquet                   (default: csv)
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA_VERSION = "1.0"

_DEFAULT_ENDPOINT = "https://game8.co/api/tool_structural_mappings/551.json"


@dataclass
class Config:
    """Runtime configuration for the JSON pipeline."""

    raw_dir: Path = field(default_factory=lambda: Path("data/raw"))
    base_dir: Path = field(default_factory=lambda: Path("data/base"))
    enriched_dir: Path = field(default_factory=lambda: Path("data/enriched"))
    reports_dir: Path = field(default_factory=lambda: Path("data/reports"))
    endpoint: str = _DEFAULT_ENDPOINT
    timeout: int = 30
    output_format: str = "csv"
    schema_version: str = SCHEMA_VERSION

    @classmethod
    def from_env(cls) -> "Config":
        """Build a :class:`Config` from environment variables, falling back to defaults."""
        return cls(
            raw_dir=Path(os.getenv("TCG_RAW_DIR", "data/raw")),
            base_dir=Path(os.getenv("TCG_BASE_DIR", "data/base")),
            enriched_dir=Path(os.getenv("TCG_ENRICHED_DIR", "data/enriched")),
            reports_dir=Path(os.getenv("TCG_REPORTS_DIR", "data/reports")),
            endpoint=os.getenv("TCG_ENDPOINT", _DEFAULT_ENDPOINT),
            timeout=int(os.getenv("TCG_TIMEOUT", "30")),
            output_format=os.getenv("TCG_OUTPUT_FORMAT", "csv"),
        )
