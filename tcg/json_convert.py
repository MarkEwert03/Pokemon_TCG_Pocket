"""TCG Pocket JSON pipeline – single source of truth orchestrator.

This module is the primary entrypoint for the JSON-based card data pipeline.
It coordinates acquisition, normalisation, enrichment, validation, and export.

Usage (CLI)
-----------
.. code-block:: shell

    # Fetch latest raw JSON snapshot from the Game8 API
    python -m tcg.json_convert pull-base [--updated-at TIMESTAMP]

    # Build normalised base table from a snapshot
    python -m tcg.json_convert build-base [--input PATH] [--format csv|parquet]

    # Enrich base table (symbol conversion, derived fields, patches)
    python -m tcg.json_convert enrich [--input PATH] [--output DIR] [--format csv|parquet]

    # Validate a card table and print a quality report
    python -m tcg.json_convert validate [--input PATH]

    # Pass --config-from-env to load paths / settings from environment variables
    # (see tcg/config.py for the full list of TCG_* env vars).

Pipeline stages
---------------
1. **Acquire** – :func:`obtain_total_card_data` fetches raw JSON and saves a snapshot.
2. **Normalise** – :func:`build_base_table` flattens nested moves and enforces types.
3. **Export base** – :func:`clean_and_export_base` writes ``data/base/base_cards.csv``
   and a companion ``base_cards_schema.json`` manifest.
4. **Enrich** – ``enrich`` subcommand applies energy symbols, ex conversion, patches.
5. **Validate** – ``validate`` subcommand runs non-mutating data-quality checks.

The legacy HTML scraper pipeline (``tcg/driver.py``, ``tcg/io.py``,
``tcg/parser.py``) is kept intact as an auxiliary data source.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

from tcg.config import Config
from tcg.enrich.derived_fields import enrich_cards
from tcg.enrich.patches import apply_patches
from tcg.normalize.base_schema import (
    BASE_COLUMNS,
    SCHEMA_VERSION,
    flatten_to_base_table,
    normalize_base_types,
)
from tcg.sources.structural_api import fetch_raw, load_snapshot, save_snapshot
from tcg.validate.base_checks import validate_cards
from tcg.writers import export_base, export_enriched

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# High-level pipeline steps (importable by other modules)
# ---------------------------------------------------------------------------


def obtain_total_card_data(
    updated_at: int | None = None,
    endpoint: str | None = None,
    timeout: int = 30,
    raw_dir: Path | None = None,
) -> dict:
    """Fetch raw card data from the Game8 structural endpoint and save a snapshot.

    Parameters
    ----------
    updated_at:
        Unix timestamp for the ``updatedAt`` query parameter.
    endpoint:
        Override the default API endpoint URL.
    timeout:
        HTTP request timeout in seconds.
    raw_dir:
        Directory in which to save the raw snapshot.  Defaults to ``data/raw``.

    Returns
    -------
    dict
        Raw JSON payload with ``_meta`` populated (``source_url``,
        ``fetched_at``, ``record_count``).
    """
    kwargs: dict = {}
    if endpoint:
        kwargs["endpoint"] = endpoint

    raw = fetch_raw(updated_at=updated_at, timeout=timeout, **kwargs)

    if raw_dir is None:
        raw_dir = Path("data/raw")
    save_snapshot(raw, raw_dir)

    return raw


def build_base_table(raw: dict) -> pd.DataFrame:
    """Flatten raw JSON to a normalised base DataFrame.

    Calls :func:`~tcg.normalize.base_schema.flatten_to_base_table` then
    :func:`~tcg.normalize.base_schema.normalize_base_types`.

    Parameters
    ----------
    raw:
        Raw payload (from :func:`obtain_total_card_data` or a loaded snapshot).

    Returns
    -------
    pd.DataFrame
        Normalised base table with :data:`~tcg.normalize.base_schema.BASE_COLUMNS`.
    """
    df = flatten_to_base_table(raw)
    df = normalize_base_types(df)
    return df


def clean_and_export_base(
    df: pd.DataFrame,
    base_dir: Path,
    *,
    fmt: str = "csv",
    source_meta: dict | None = None,
) -> Path:
    """Export the normalised base table to *base_dir*.

    Writes the data file and a companion ``_schema.json`` manifest.

    Parameters
    ----------
    df:
        Normalised base table.
    base_dir:
        Output directory (created if absent).
    fmt:
        ``"csv"`` (default) or ``"parquet"``.
    source_meta:
        Metadata from the acquisition step embedded in the schema manifest.

    Returns
    -------
    Path
        Path to the written data file.
    """
    return export_base(
        df,
        base_dir=base_dir,
        fmt=fmt,
        schema_version=SCHEMA_VERSION,
        source_meta=source_meta,
    )


# ---------------------------------------------------------------------------
# CLI subcommand handlers
# ---------------------------------------------------------------------------


def _cmd_pull_base(args: argparse.Namespace, cfg: Config) -> int:
    """Handler for the ``pull-base`` subcommand."""
    try:
        raw = obtain_total_card_data(
            updated_at=args.updated_at,
            raw_dir=cfg.raw_dir,
            timeout=cfg.timeout,
        )
        count = raw.get("_meta", {}).get("record_count", "?")
        print(f"Fetched {count} cards. Snapshot saved to {cfg.raw_dir}/")
        return 0
    except Exception as exc:
        logger.error("pull-base failed: %s", exc)
        return 1


def _cmd_build_base(args: argparse.Namespace, cfg: Config) -> int:
    """Handler for the ``build-base`` subcommand."""
    try:
        if args.input:
            raw = load_snapshot(Path(args.input))
            logger.info("Loaded snapshot from %s", args.input)
        else:
            snapshots = sorted(cfg.raw_dir.glob("raw_*.json"))
            if not snapshots:
                print(
                    f"No snapshots found in {cfg.raw_dir}. "
                    "Run 'pull-base' first, or specify --input.",
                    file=sys.stderr,
                )
                return 1
            raw = load_snapshot(snapshots[-1])
            logger.info("Loaded latest snapshot from %s", snapshots[-1])

        fmt = args.format or cfg.output_format
        df = build_base_table(raw)
        out = clean_and_export_base(
            df,
            base_dir=cfg.base_dir,
            fmt=fmt,
            source_meta=raw.get("_meta"),
        )
        print(f"Base table ({len(df)} rows) written to {out}")
        return 0
    except Exception as exc:
        logger.error("build-base failed: %s", exc)
        return 1


def _cmd_enrich(args: argparse.Namespace, cfg: Config) -> int:
    """Handler for the ``enrich`` subcommand."""
    try:
        if args.input:
            input_path = Path(args.input)
        else:
            default = cfg.base_dir / "base_cards.csv"
            if not default.exists():
                print(
                    f"Base table not found at {default}. "
                    "Run 'build-base' first, or specify --input.",
                    file=sys.stderr,
                )
                return 1
            input_path = default

        df = pd.read_csv(input_path)
        logger.info("Loaded %d rows from %s", len(df), input_path)

        df = enrich_cards(df)
        df = apply_patches(df)

        out_dir = Path(args.output) if args.output else cfg.enriched_dir
        fmt = args.format or cfg.output_format
        out = export_enriched(df, out_dir, fmt=fmt)
        print(f"Enriched table ({len(df)} rows) written to {out}")
        return 0
    except Exception as exc:
        logger.error("enrich failed: %s", exc)
        return 1


def _cmd_validate(args: argparse.Namespace, cfg: Config) -> int:
    """Handler for the ``validate`` subcommand."""
    try:
        if args.input:
            input_path = Path(args.input)
        else:
            enriched = cfg.enriched_dir / "cards_enriched.csv"
            base = cfg.base_dir / "base_cards.csv"
            if enriched.exists():
                input_path = enriched
            elif base.exists():
                input_path = base
            else:
                print(
                    "No card table found. Run 'build-base' or 'enrich' first, "
                    "or specify --input.",
                    file=sys.stderr,
                )
                return 1

        df = pd.read_csv(input_path)
        logger.info("Validating %d rows from %s", len(df), input_path)

        issues = validate_cards(df)

        if not issues:
            print(f"✓ All checks passed ({len(df)} cards, 0 issues)")
            return 0

        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        print(
            f"Validation result: {len(errors)} error(s), {len(warnings)} warning(s)"
        )
        for issue in issues:
            tag = "ERROR" if issue.severity == "error" else "WARN "
            print(f"  [{tag}] {issue.check}: {issue.message}")
            if issue.row_ids:
                print(f"         Affected IDs: {issue.row_ids}")

        if cfg.reports_dir:
            cfg.reports_dir.mkdir(parents=True, exist_ok=True)
            report_path = cfg.reports_dir / "validation_report.json"
            report = [
                {
                    "severity": i.severity,
                    "check": i.check,
                    "message": i.message,
                    "row_ids": i.row_ids,
                }
                for i in issues
            ]
            with open(report_path, "w", encoding="utf-8") as fh:
                json.dump(report, fh, indent=2)
            print(f"Report saved to {report_path}")

        return 1 if errors else 0
    except Exception as exc:
        logger.error("validate failed: %s", exc)
        return 1


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tcg.json_convert",
        description="TCG Pocket JSON data pipeline",
    )
    parser.add_argument(
        "--config-from-env",
        action="store_true",
        help="Load configuration from TCG_* environment variables",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # pull-base
    p_pull = sub.add_parser(
        "pull-base", help="Fetch latest raw JSON snapshot from the Game8 API"
    )
    p_pull.add_argument(
        "--updated-at",
        dest="updated_at",
        type=int,
        default=None,
        metavar="TIMESTAMP",
        help="Unix timestamp for the updatedAt query param (default: current time)",
    )

    # build-base
    p_build = sub.add_parser(
        "build-base", help="Build normalised base table from a raw snapshot"
    )
    p_build.add_argument(
        "--input", metavar="PATH", help="Path to a raw JSON snapshot file"
    )
    p_build.add_argument(
        "--format",
        choices=["csv", "parquet"],
        default=None,
        metavar="FMT",
        help="Output format: csv (default) or parquet",
    )

    # enrich
    p_enrich = sub.add_parser(
        "enrich",
        help="Enrich base table with symbols, derived fields, and patches",
    )
    p_enrich.add_argument(
        "--input", metavar="PATH", help="Path to base CSV to enrich"
    )
    p_enrich.add_argument(
        "--output",
        metavar="DIR",
        help="Output directory (default: data/enriched)",
    )
    p_enrich.add_argument(
        "--format",
        choices=["csv", "parquet"],
        default=None,
        metavar="FMT",
        help="Output format: csv (default) or parquet",
    )

    # validate
    p_val = sub.add_parser(
        "validate", help="Validate a card table and print a quality report"
    )
    p_val.add_argument("--input", metavar="PATH", help="Path to CSV to validate")

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.  Returns exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    cfg = Config.from_env() if getattr(args, "config_from_env", False) else Config()

    handlers = {
        "pull-base": _cmd_pull_base,
        "build-base": _cmd_build_base,
        "enrich": _cmd_enrich,
        "validate": _cmd_validate,
    }

    if args.command is None:
        parser.print_help()
        return 0

    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help()
        return 1

    return handler(args, cfg)


if __name__ == "__main__":
    sys.exit(main())
