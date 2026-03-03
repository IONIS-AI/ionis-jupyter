"""Dataset loader for IONIS SQLite files.

Loads datasets from the ionis-mcp data directory. Compatible with data
downloaded via `ionis-download` CLI.
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional

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
        Dict of dataset name -> {"path": Path, "exists": bool, "rows": int|None}
    """
    if data_dir is None:
        try:
            data_dir = get_data_dir()
        except FileNotFoundError:
            data_dir = Path(".")

    result = {}
    for name, rel_path in DATASET_PATHS.items():
        path = data_dir / rel_path
        exists = path.exists()
        rows = None

        if exists:
            try:
                conn = sqlite3.connect(str(path))
                table = DATASET_TABLES[name]
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                rows = cursor.fetchone()[0]
                conn.close()
            except Exception:
                pass

        result[name] = {"path": path, "exists": exists, "rows": rows}

    return result


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

    Raises:
        ValueError: If dataset name is invalid
        FileNotFoundError: If dataset file not found

    Example:
        >>> wspr = load_dataset("wspr", limit=10000)
        >>> print(wspr.head())
    """
    if name not in DATASET_PATHS:
        valid = ", ".join(sorted(DATASET_PATHS.keys()))
        raise ValueError(f"Unknown dataset '{name}'. Valid: {valid}")

    if data_dir is None:
        data_dir = get_data_dir()

    path = data_dir / DATASET_PATHS[name]

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset '{name}' not found at {path}. "
            f"Run: ionis-download --datasets {name}"
        )

    conn = sqlite3.connect(str(path))

    if query is None:
        table = DATASET_TABLES[name]
        query = f"SELECT * FROM {table}"
        if limit:
            query += f" LIMIT {limit}"

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def band_name(band_id: int) -> str:
    """Convert band ID to name (e.g., 107 -> '20m')."""
    return BAND_NAMES.get(band_id, str(band_id))
