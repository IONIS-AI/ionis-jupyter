"""Dataset loader for IONIS SQLite files.

Loads datasets from the ionis-mcp data directory. Compatible with data
downloaded via `ionis-download` CLI.

Falls back to bundled sample data for Binder/demo environments.
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

# Dataset paths relative to data root (matches ionis-mcp structure)
DATASET_PATHS = {
    "wspr": "propagation/wspr-signatures/wspr_signatures_v2.sqlite",
    "rbn": "propagation/rbn-signatures/rbn_signatures.sqlite",
    "contest": "propagation/contest-signatures/contest_signatures.sqlite",
    "dxpedition": "propagation/dxpedition-signatures/dxpedition_signatures.sqlite",
    "pskr": "propagation/pskr-signatures/pskr_signatures.sqlite",
    "solar": "solar/solar-indices/solar_indices.sqlite",
    "dscovr": "solar/dscovr/dscovr_l1.sqlite",
    "grids": "tools/grid-lookup/grid_lookup.sqlite",
    "balloons": "tools/balloon-callsigns/balloon_callsigns_v2.sqlite",
}

# Sample data paths (bundled with package for Binder demos)
SAMPLE_PATHS = {
    "wspr": "wspr_signatures_sample.sqlite",
    "contest": "contest_signatures_sample.sqlite",
    "solar": "solar_indices_sample.sqlite",
    "grids": "grid_lookup_sample.sqlite",
}

# Table names within each SQLite file
DATASET_TABLES = {
    "wspr": "wspr_signatures",
    "rbn": "rbn_signatures",
    "contest": "contest_signatures",
    "dxpedition": "dxpedition_signatures",
    "pskr": "pskr_signatures",
    "solar": "solar_indices",
    "dscovr": "dscovr_l1",
    "grids": "grid_lookup",
    "balloons": "balloon_callsigns",
}

# Flag to track if we're using sample data
_using_sample_data = False

# Band ID to name mapping
BAND_NAMES = {
    102: "160m", 103: "80m", 104: "60m", 105: "40m", 106: "30m",
    107: "20m", 108: "17m", 109: "15m", 110: "12m", 111: "10m",
}


def get_data_dir() -> Path:
    """Get the IONIS data directory.

    Resolution order:
    1. IONIS_DATA_DIR environment variable
    2. Platform default (~/.ionis-mcp/data/ on Unix)

    Returns:
        Path to data directory

    Raises:
        FileNotFoundError: If no data directory found
    """
    # Check environment variable first
    if env_dir := os.environ.get("IONIS_DATA_DIR"):
        path = Path(env_dir)
        if path.exists():
            return path

    # Platform default
    if os.name == "nt":  # Windows
        base = Path(os.environ.get("LOCALAPPDATA", "~"))
    else:  # Unix/macOS
        base = Path.home()

    default_path = base / ".ionis-mcp" / "data"

    # Look for versioned subdirectory (v1.0, 2026-04, etc.)
    if default_path.exists():
        # Prefer frozen versions over monthlies
        for subdir in sorted(default_path.iterdir(), reverse=True):
            if subdir.is_dir() and (subdir.name.startswith("v") or subdir.name[:4].isdigit()):
                return subdir
        return default_path

    raise FileNotFoundError(
        "IONIS data directory not found. Run: ionis-download --bundle minimal"
    )


def list_datasets(data_dir: Optional[Path] = None) -> dict:
    """List available datasets and their status.

    Args:
        data_dir: Override data directory (default: auto-detect)

    Returns:
        Dict of dataset name -> {"path": Path, "exists": bool, "rows": int|None, "sample": bool}
    """
    if data_dir is None:
        try:
            data_dir = get_data_dir()
        except FileNotFoundError:
            data_dir = None

    sample_dir = _get_sample_dir()
    result = {}

    for name, rel_path in DATASET_PATHS.items():
        path = None
        exists = False
        rows = None
        is_sample = False

        # Check full dataset
        if data_dir is not None:
            full_path = data_dir / rel_path
            if full_path.exists():
                path = full_path
                exists = True

        # Check sample data if full not found
        if not exists and name in SAMPLE_PATHS:
            sample_path = sample_dir / SAMPLE_PATHS[name]
            if sample_path.exists():
                path = sample_path
                exists = True
                is_sample = True

        # Get row count
        if exists and path:
            try:
                conn = sqlite3.connect(str(path))
                table = DATASET_TABLES[name]
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                rows = cursor.fetchone()[0]
                conn.close()
            except Exception:
                pass

        result[name] = {"path": path, "exists": exists, "rows": rows, "sample": is_sample}

    return result


def _get_sample_dir() -> Path:
    """Get the bundled sample data directory."""
    # Sample data is bundled inside the installed package
    return Path(__file__).parent / "sample_data"


def _find_dataset(name: str, data_dir: Optional[Path] = None) -> Tuple[Path, bool]:
    """Find dataset path, falling back to sample data.

    Returns:
        Tuple of (path, is_sample)
    """
    # Try full dataset first
    if data_dir is not None:
        full_path = data_dir / DATASET_PATHS[name]
        if full_path.exists():
            return full_path, False
    else:
        try:
            full_dir = get_data_dir()
            full_path = full_dir / DATASET_PATHS[name]
            if full_path.exists():
                return full_path, False
        except FileNotFoundError:
            pass

    # Fall back to sample data
    if name in SAMPLE_PATHS:
        sample_path = _get_sample_dir() / SAMPLE_PATHS[name]
        if sample_path.exists():
            return sample_path, True

    # Nothing found
    raise FileNotFoundError(
        f"Dataset '{name}' not found. "
        f"Run: ionis-download --datasets {name}\n"
        f"Or use sample data (available for: {', '.join(SAMPLE_PATHS.keys())})"
    )


def load_dataset(
    name: str,
    data_dir: Optional[Path] = None,
    query: Optional[str] = None,
    limit: Optional[int] = None,
) -> pd.DataFrame:
    """Load an IONIS dataset into a pandas DataFrame.

    Args:
        name: Dataset name (wspr, rbn, contest, dxpedition, pskr, solar, dscovr, grids, balloons)
        data_dir: Override data directory (default: auto-detect)
        query: Custom SQL query (default: SELECT * FROM table)
        limit: Limit rows returned (default: all)

    Returns:
        pandas DataFrame with dataset contents

    Note:
        Falls back to bundled sample data if full dataset not found.
        Sample data is limited but sufficient for demos.

    Raises:
        ValueError: If dataset name is invalid
        FileNotFoundError: If dataset file not found

    Example:
        >>> wspr = load_dataset("wspr", limit=10000)
        >>> print(wspr.head())
    """
    global _using_sample_data

    if name not in DATASET_PATHS:
        valid = ", ".join(sorted(DATASET_PATHS.keys()))
        raise ValueError(f"Unknown dataset '{name}'. Valid: {valid}")

    path, is_sample = _find_dataset(name, data_dir)

    if is_sample:
        _using_sample_data = True
        print(f"[Using sample data for '{name}' - {path.name}]")

    conn = sqlite3.connect(str(path))

    if query is None:
        table = DATASET_TABLES[name]
        query = f"SELECT * FROM {table}"
        if limit:
            query += f" LIMIT {limit}"

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def is_using_sample_data() -> bool:
    """Check if any loaded dataset was from sample data."""
    return _using_sample_data


def band_name(band_id: int) -> str:
    """Convert band ID to name (e.g., 107 -> '20m')."""
    return BAND_NAMES.get(band_id, str(band_id))
