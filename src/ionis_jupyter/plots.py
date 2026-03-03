"""Plotting utilities for propagation analysis.

Provides reusable matplotlib/seaborn plots for common visualizations.
"""

from typing import Optional, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .loader import BAND_NAMES


def plot_band_heatmap(
    df: pd.DataFrame,
    band: int,
    value_col: str = "median_snr",
    title: Optional[str] = None,
    figsize: tuple = (12, 6),
    cmap: str = "RdYlGn",
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Plot hour×month heatmap for a single band.

    Args:
        df: DataFrame with hour, month, and value columns
        band: Band ID to filter (e.g., 107 for 20m)
        value_col: Column to aggregate (default: median_snr)
        title: Plot title (default: auto-generated)
        figsize: Figure size (width, height)
        cmap: Colormap name
        ax: Existing axes to plot on

    Returns:
        matplotlib Axes object

    Example:
        >>> wspr = load_dataset("wspr")
        >>> wspr_20m = wspr[wspr["band"] == 107]
        >>> plot_band_heatmap(wspr_20m, 107)
    """
    band_df = df[df["band"] == band] if "band" in df.columns else df

    # Pivot to hour×month
    pivot = band_df.groupby(["hour", "month"])[value_col].mean().unstack(fill_value=np.nan)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    sns.heatmap(
        pivot,
        ax=ax,
        cmap=cmap,
        center=0,
        annot=False,
        fmt=".1f",
        cbar_kws={"label": f"{value_col} (dB)"},
    )

    band_name = BAND_NAMES.get(band, str(band))
    ax.set_title(title or f"{band_name} Band Openings by Hour and Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Hour (UTC)")

    return ax


def plot_solar_correlation(
    df: pd.DataFrame,
    sfi_col: str = "avg_sfi",
    snr_col: str = "median_snr",
    band: Optional[int] = None,
    title: Optional[str] = None,
    figsize: tuple = (10, 6),
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Plot SNR vs SFI correlation with regression line.

    Args:
        df: DataFrame with SFI and SNR columns
        sfi_col: SFI column name
        snr_col: SNR column name
        band: Optional band to filter
        title: Plot title
        figsize: Figure size
        ax: Existing axes

    Returns:
        matplotlib Axes object
    """
    plot_df = df.copy()
    if band is not None and "band" in plot_df.columns:
        plot_df = plot_df[plot_df["band"] == band]

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    # Bin SFI into brackets
    plot_df["sfi_bracket"] = (plot_df[sfi_col] // 20) * 20

    # Aggregate by bracket
    agg = plot_df.groupby("sfi_bracket")[snr_col].agg(["mean", "std", "count"]).reset_index()
    agg = agg[agg["count"] >= 10]  # Minimum samples

    ax.errorbar(
        agg["sfi_bracket"],
        agg["mean"],
        yerr=agg["std"] / np.sqrt(agg["count"]),
        fmt="o-",
        capsize=3,
        label="Mean SNR",
    )

    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("Solar Flux Index (SFU)")
    ax.set_ylabel(f"{snr_col} (dB)")

    band_name = BAND_NAMES.get(band, "") if band else "All Bands"
    ax.set_title(title or f"Solar Correlation — {band_name}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    return ax


def plot_path_profile(
    df: pd.DataFrame,
    tx_grid: str,
    rx_grid: str,
    band: Optional[int] = None,
    title: Optional[str] = None,
    figsize: tuple = (12, 5),
) -> plt.Figure:
    """Plot hour-by-hour propagation profile for a specific path.

    Args:
        df: DataFrame with tx_grid_4, rx_grid_4, hour, median_snr columns
        tx_grid: Transmitter grid (4-char)
        rx_grid: Receiver grid (4-char)
        band: Optional band filter
        title: Plot title
        figsize: Figure size

    Returns:
        matplotlib Figure object
    """
    # Filter to path
    mask = (df["tx_grid_4"] == tx_grid[:4]) & (df["rx_grid_4"] == rx_grid[:4])
    if band is not None:
        mask &= df["band"] == band

    path_df = df[mask]

    if path_df.empty:
        raise ValueError(f"No data found for path {tx_grid} → {rx_grid}")

    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # Left: Hour profile
    hour_agg = path_df.groupby("hour")["median_snr"].mean()
    axes[0].bar(hour_agg.index, hour_agg.values, color="steelblue", alpha=0.7)
    axes[0].axhline(0, color="gray", linestyle="--", alpha=0.5)
    axes[0].set_xlabel("Hour (UTC)")
    axes[0].set_ylabel("Median SNR (dB)")
    axes[0].set_title("Hour Profile")
    axes[0].set_xticks(range(0, 24, 2))

    # Right: Month profile
    month_agg = path_df.groupby("month")["median_snr"].mean()
    axes[1].bar(month_agg.index, month_agg.values, color="forestgreen", alpha=0.7)
    axes[1].axhline(0, color="gray", linestyle="--", alpha=0.5)
    axes[1].set_xlabel("Month")
    axes[1].set_ylabel("Median SNR (dB)")
    axes[1].set_title("Seasonal Profile")
    axes[1].set_xticks(range(1, 13))

    band_name = BAND_NAMES.get(band, "") if band else ""
    fig.suptitle(title or f"Path: {tx_grid} → {rx_grid} {band_name}".strip())
    fig.tight_layout()

    return fig


def plot_distance_snr(
    df: pd.DataFrame,
    band: Optional[int] = None,
    distance_col: str = "avg_distance",
    snr_col: str = "median_snr",
    bins: int = 20,
    title: Optional[str] = None,
    figsize: tuple = (10, 6),
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Plot SNR vs distance relationship.

    Args:
        df: DataFrame with distance and SNR columns
        band: Optional band filter
        distance_col: Distance column name
        snr_col: SNR column name
        bins: Number of distance bins
        title: Plot title
        figsize: Figure size
        ax: Existing axes

    Returns:
        matplotlib Axes object
    """
    plot_df = df.copy()
    if band is not None and "band" in plot_df.columns:
        plot_df = plot_df[plot_df["band"] == band]

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    # Bin distances
    plot_df["distance_bin"] = pd.cut(plot_df[distance_col], bins=bins)
    agg = plot_df.groupby("distance_bin")[snr_col].agg(["mean", "std", "count"]).reset_index()

    # Get bin centers
    agg["distance_center"] = agg["distance_bin"].apply(lambda x: x.mid if pd.notna(x) else np.nan)
    agg = agg.dropna()

    ax.errorbar(
        agg["distance_center"],
        agg["mean"],
        yerr=agg["std"] / np.sqrt(agg["count"]),
        fmt="o-",
        capsize=3,
    )

    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel(f"{snr_col} (dB)")

    band_name = BAND_NAMES.get(band, "") if band else "All Bands"
    ax.set_title(title or f"SNR vs Distance — {band_name}")
    ax.grid(True, alpha=0.3)

    return ax


def plot_band_comparison(
    df: pd.DataFrame,
    bands: Optional[List[int]] = None,
    hour: Optional[int] = None,
    month: Optional[int] = None,
    figsize: tuple = (12, 6),
) -> plt.Figure:
    """Compare SNR distributions across bands.

    Args:
        df: DataFrame with band and median_snr columns
        bands: List of band IDs to compare (default: all)
        hour: Optional hour filter
        month: Optional month filter
        figsize: Figure size

    Returns:
        matplotlib Figure object
    """
    plot_df = df.copy()

    if hour is not None:
        plot_df = plot_df[plot_df["hour"] == hour]
    if month is not None:
        plot_df = plot_df[plot_df["month"] == month]

    if bands is None:
        bands = sorted(plot_df["band"].unique())

    fig, ax = plt.subplots(figsize=figsize)

    band_data = []
    band_labels = []
    for band in bands:
        band_df = plot_df[plot_df["band"] == band]["median_snr"].dropna()
        if len(band_df) > 0:
            band_data.append(band_df.values)
            band_labels.append(BAND_NAMES.get(band, str(band)))

    ax.boxplot(band_data, labels=band_labels)
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("Band")
    ax.set_ylabel("Median SNR (dB)")

    title_parts = ["Band Comparison"]
    if hour is not None:
        title_parts.append(f"Hour {hour:02d} UTC")
    if month is not None:
        title_parts.append(f"Month {month}")
    ax.set_title(" — ".join(title_parts))

    ax.grid(True, alpha=0.3, axis="y")

    return fig
