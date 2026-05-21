"""Output layer: write card DataFrames to CSV or Parquet, plus JSON schema manifests.

Public API
----------
* :func:`write_csv`             – write DataFrame → CSV
* :func:`write_parquet`         – write DataFrame → Parquet (requires ``pyarrow``)
* :func:`write_schema_manifest` – write a JSON file describing the DataFrame schema
* :func:`export_base`           – write base table + manifest to ``data/base/``
* :func:`export_enriched`       – write enriched table to ``data/enriched/``

All functions create parent directories as needed and log the output path.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Low-level writers
# ---------------------------------------------------------------------------


def write_csv(df: pd.DataFrame, path: Path) -> None:
    """Write *df* to a UTF-8 CSV file at *path*.

    Parent directories are created if absent.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    logger.info("Wrote %d rows → %s", len(df), path)


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    """Write *df* to a Parquet file at *path*.

    Parent directories are created if absent.

    Raises
    ------
    ImportError
        If ``pyarrow`` is not installed.
    """
    try:
        import pyarrow  # noqa: F401 – availability check only
    except ImportError as exc:
        raise ImportError(
            "pyarrow is required for Parquet output. "
            "Install it with: pip install pyarrow"
        ) from exc

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    logger.info("Wrote %d rows → %s", len(df), path)


def write_schema_manifest(
    df: pd.DataFrame,
    path: Path,
    *,
    schema_version: str,
    source_meta: dict | None = None,
) -> None:
    """Write a JSON schema manifest alongside the data file.

    The manifest records:

    * ``schema_version`` – version string from the pipeline config
    * ``row_count``       – number of rows in *df*
    * ``columns``         – mapping of ``{column_name: dtype_string}``
    * ``source``          – forwarded ``source_meta`` dict (or ``{}``)

    Parameters
    ----------
    df:
        The DataFrame whose schema to record.
    path:
        Output path for the ``.json`` manifest file.
    schema_version:
        Version string to embed in the manifest.
    source_meta:
        Arbitrary metadata from the acquisition step (e.g. ``source_url``,
        ``fetched_at``).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": schema_version,
        "row_count": len(df),
        "columns": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "source": source_meta or {},
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)

    logger.info("Wrote schema manifest → %s", path)


# ---------------------------------------------------------------------------
# High-level export helpers
# ---------------------------------------------------------------------------


def export_base(
    df: pd.DataFrame,
    base_dir: Path,
    *,
    fmt: str = "csv",
    schema_version: str = "1.0",
    source_meta: dict | None = None,
) -> Path:
    """Write the base table plus a schema manifest to *base_dir*.

    Output files:

    * ``base_cards.csv``        (or ``.parquet`` when ``fmt="parquet"``)
    * ``base_cards_schema.json``

    Parameters
    ----------
    df:
        Normalised base card table.
    base_dir:
        Output directory (created if absent).
    fmt:
        ``"csv"`` (default) or ``"parquet"``.
    schema_version:
        Version string embedded in the manifest.
    source_meta:
        Acquisition metadata forwarded to the manifest.

    Returns
    -------
    Path
        Path of the written data file.
    """
    base_dir = Path(base_dir)
    stem = "base_cards"

    if fmt == "parquet":
        data_path = base_dir / f"{stem}.parquet"
        write_parquet(df, data_path)
    else:
        data_path = base_dir / f"{stem}.csv"
        write_csv(df, data_path)

    manifest_path = base_dir / f"{stem}_schema.json"
    write_schema_manifest(
        df,
        manifest_path,
        schema_version=schema_version,
        source_meta=source_meta,
    )
    return data_path


def export_enriched(
    df: pd.DataFrame,
    enriched_dir: Path,
    *,
    fmt: str = "csv",
) -> Path:
    """Write the enriched table to *enriched_dir*.

    Output file: ``cards_enriched.csv`` (or ``.parquet``).

    Parameters
    ----------
    df:
        Enriched card table.
    enriched_dir:
        Output directory (created if absent).
    fmt:
        ``"csv"`` or ``"parquet"``.

    Returns
    -------
    Path
        Path of the written data file.
    """
    enriched_dir = Path(enriched_dir)
    stem = "cards_enriched"

    if fmt == "parquet":
        path = enriched_dir / f"{stem}.parquet"
        write_parquet(df, path)
    else:
        path = enriched_dir / f"{stem}.csv"
        write_csv(df, path)

    return path
