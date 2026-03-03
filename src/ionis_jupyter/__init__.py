"""IONIS Jupyter — Helper library for HF propagation research.

This package provides utilities for loading and analyzing IONIS datasets
in Jupyter notebooks. Designed for researchers, data scientists, and
amateur radio operators studying ionospheric propagation.

Example:
    >>> from ionis_jupyter import load_dataset, grid_distance
    >>> wspr = load_dataset("wspr")
    >>> print(f"Loaded {len(wspr):,} WSPR signatures")
"""

__version__ = "0.1.0"

from .loader import load_dataset, list_datasets, get_data_dir
from .grids import (
    grid_to_latlon,
    latlon_to_grid,
    grid_distance,
    grid_bearing,
)
from .solar import solar_elevation, is_dark, classify_path
from .plots import (
    plot_band_heatmap,
    plot_solar_correlation,
    plot_path_profile,
    plot_distance_snr,
)

__all__ = [
    # Version
    "__version__",
    # Loader
    "load_dataset",
    "list_datasets",
    "get_data_dir",
    # Grids
    "grid_to_latlon",
    "latlon_to_grid",
    "grid_distance",
    "grid_bearing",
    # Solar
    "solar_elevation",
    "is_dark",
    "classify_path",
    # Plots
    "plot_band_heatmap",
    "plot_solar_correlation",
    "plot_path_profile",
    "plot_distance_snr",
]
