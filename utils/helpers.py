"""
Shared utilities for the CIC-IDS-2017 project.

Design rules:
  - No notebook-specific logic lives here. Only pure, reusable functions.
  - A single RANDOM_STATE constant is imported by every notebook.
  - Loading/cleaning is idempotent: you can call load_cic_ids_2017 multiple
    times and get the same result (important for caching).
"""

from __future__ import annotations

import glob
import os
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


# =============================================================================
# Global reproducibility seed. Import this everywhere.
# =============================================================================
RANDOM_STATE = 42


# =============================================================================
# Paths (relative to project root). Notebooks live in ./notebooks, so they
# resolve to parent for data/figures/results.
# =============================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
RESULTS_DIR = PROJECT_ROOT / "outputs" / "results"

for _p in (DATA_DIR, FIGURES_DIR, RESULTS_DIR):
    _p.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Loading the CIC-IDS-2017 CSV files
# =============================================================================
def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Column names in the CIC-IDS-2017 CSVs have leading spaces on every
    column (an artifact of CICFlowMeter's CSV export). We strip them so
    df["Flow Duration"] works instead of df[" Flow Duration"].

    The raw schema also contains a *genuinely* duplicated column:
    "Fwd Header Length" AND "Fwd Header Length.1" both appear as
    separate columns carrying the exact same values (verified against
    the raw data). This is a confirmed CICFlowMeter export bug. We drop
    the ".1" copy to keep the schema clean.
    """
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    if "Fwd Header Length.1" in df.columns:
        df = df.drop(columns=["Fwd Header Length.1"])

    return df


def _clean_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    The raw CSVs contain a UTF-8 replacement character (U+FFFD, bytes
    0xEF 0xBF 0xBD) in the Web Attack label names, where there should
    have been an en-dash. This corruption is baked into the raw files;
    no codec can recover the original character.

    We normalize all Label strings by:
      - Stripping surrounding whitespace.
      - Removing the replacement character (�) and any ASCII
        control/non-printable bytes that occasionally slip through.
      - Collapsing repeated whitespace to a single space.

    After this step, labels look like "Web Attack Brute Force" rather
    than "Web Attack � Brute Force" (or the even worse double-encoded
    "Web Attack ï¿½ Brute Force" you get from printing naively).
    """
    if "Label" not in df.columns:
        return df
    df = df.copy()
    labels = df["Label"].astype(str)
    labels = labels.str.replace("�", " ", regex=False)
    labels = labels.str.replace(r"[^\x20-\x7E]", " ", regex=True)
    labels = labels.str.replace(r"\s+", " ", regex=True).str.strip()
    df["Label"] = labels
    return df


def _optimize_memory(df: pd.DataFrame) -> pd.DataFrame:
    """
    The raw files default every numeric column to float64. For ~2.8M rows
    and ~80 columns that's ~1.7 GB. Downcasting ints to int32 and floats
    to float32 cuts this by roughly half with no loss of analytical value
    (we don't need 15 digits of precision for packet counts).
    """
    df = df.copy()
    for col in df.select_dtypes(include=["int64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="integer")
    for col in df.select_dtypes(include=["float64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="float")
    return df


def load_cic_ids_2017(
    data_dir: str | os.PathLike | None = None,
    files: Iterable[str] | None = None,
    nrows: int | None = None,
) -> pd.DataFrame:
    """
    Load and concatenate the CIC-IDS-2017 CSV files.

    Parameters
    ----------
    data_dir : path, optional
        Where the CSVs live. Defaults to DATA_DIR.
    files : iterable of str, optional
        Subset of filenames to load (e.g. for quick iteration).
    nrows : int, optional
        If given, read only the first N rows from EACH file. Handy for
        fast prototyping before committing to a full run.

    Returns
    -------
    pd.DataFrame
        A single concatenated, column-standardized, memory-optimized frame.
    """
    data_dir = Path(data_dir) if data_dir else DATA_DIR

    if files is None:
        csv_paths = sorted(glob.glob(str(data_dir / "*.csv")))
    else:
        csv_paths = [str(data_dir / f) for f in files]

    if not csv_paths:
        raise FileNotFoundError(
            f"No CSV files found in {data_dir}. "
            "Download the CIC-IDS-2017 dataset from Kaggle and place the "
            "CSVs into the data/ directory."
        )

    frames = []
    for path in csv_paths:
        # low_memory=False avoids dtype guessing per-chunk, which causes
        # mixed-type warnings on these files.
        df = pd.read_csv(path, low_memory=False, nrows=nrows,
                         encoding="latin1")
        df = _standardize_columns(df)
        df = _clean_labels(df)
        df["__source_file"] = Path(path).name  # keeps provenance for debugging
        frames.append(df)

    full = pd.concat(frames, ignore_index=True)
    full = _optimize_memory(full)
    return full


# =============================================================================
# Cached clean dataset — Parquet snapshot after Q1 preprocessing
# =============================================================================
CLEAN_PARQUET = DATA_DIR / "cic_ids_2017_clean.parquet"


def load_clean_cached() -> pd.DataFrame:
    """
    Return the cleaned dataset produced by Q1, loading from a Parquet
    snapshot on disk. Raises if Q1 hasn't been run yet.

    Q2 and Q3 both call this so they don't re-run the full Q1 pipeline.
    """
    if not CLEAN_PARQUET.exists():
        raise FileNotFoundError(
            f"{CLEAN_PARQUET} not found. Run notebooks/q1_eda.ipynb "
            "end-to-end first — it writes the cleaned snapshot."
        )
    return pd.read_parquet(CLEAN_PARQUET)


def save_clean_cached(df: pd.DataFrame) -> Path:
    """Persist the cleaned dataset so Q2/Q3 can load it instantly."""
    df.to_parquet(CLEAN_PARQUET, index=False)
    return CLEAN_PARQUET


# =============================================================================
# Cleaning helpers used in Q1 and reused in Q2/Q3
# =============================================================================
def handle_infinities(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace +/- inf with NaN. The CIC-IDS-2017 dataset has many Infs in
    rate columns (e.g. Flow Bytes/s) because those are computed as
    bytes / duration and duration can be 0 microseconds for single-packet
    flows. Leaving them as Inf breaks any scaler or model.
    """
    return df.replace([np.inf, -np.inf], np.nan)


def drop_duplicates_report(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Drop exact-duplicate rows and return (cleaned_df, removed_count)."""
    before = len(df)
    cleaned = df.drop_duplicates().reset_index(drop=True)
    return cleaned, before - len(cleaned)


def save_figure(fig, name: str, dpi: int = 120) -> Path:
    """Save a matplotlib figure under outputs/figures/ with consistent settings."""
    out = FIGURES_DIR / name
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    return out


def save_results(df: pd.DataFrame, name: str) -> Path:
    """Save a results DataFrame under outputs/results/."""
    out = RESULTS_DIR / name
    df.to_csv(out, index=False)
    return out
