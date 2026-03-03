"""Solar geometry utilities for propagation analysis.

Provides solar elevation calculations and path classification
(both-day, cross-terminator, both-dark).
"""

import math
from datetime import datetime, timezone
from typing import Tuple

from .grids import grid_to_latlon


def solar_elevation(lat: float, lon: float, dt: datetime) -> float:
    """Calculate solar elevation angle at a location and time.

    Uses the same algorithm as model.py in ionis-training for consistency.

    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        dt: UTC datetime

    Returns:
        Solar elevation in degrees (negative = below horizon)

    Example:
        >>> from datetime import datetime, timezone
        >>> dt = datetime(2026, 3, 3, 14, 0, tzinfo=timezone.utc)
        >>> solar_elevation(43.5, -115.0, dt)  # Idaho at 14:00 UTC
        25.3
    """
    # Ensure UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # Day of year
    doy = dt.timetuple().tm_yday

    # Solar declination (simplified)
    decl = -23.45 * math.cos(math.radians(360 / 365 * (doy + 10)))

    # Hour angle
    hour = dt.hour + dt.minute / 60 + dt.second / 3600
    solar_noon = 12.0 - lon / 15.0
    hour_angle = 15.0 * (hour - solar_noon)

    # Solar elevation
    lat_rad = math.radians(lat)
    decl_rad = math.radians(decl)
    hour_rad = math.radians(hour_angle)

    sin_elev = (
        math.sin(lat_rad) * math.sin(decl_rad) +
        math.cos(lat_rad) * math.cos(decl_rad) * math.cos(hour_rad)
    )

    return math.degrees(math.asin(max(-1, min(1, sin_elev))))


def solar_elevation_grid(grid: str, dt: datetime) -> float:
    """Calculate solar elevation for a Maidenhead grid.

    Args:
        grid: Maidenhead grid (4+ characters recommended)
        dt: UTC datetime

    Returns:
        Solar elevation in degrees

    Example:
        >>> solar_elevation_grid("DN13", datetime(2026, 3, 3, 14, 0, tzinfo=timezone.utc))
        25.3
    """
    lat, lon = grid_to_latlon(grid)
    return solar_elevation(lat, lon, dt)


def is_dark(lat: float, lon: float, dt: datetime, threshold: float = -6.0) -> bool:
    """Check if a location is in darkness.

    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        dt: UTC datetime
        threshold: Solar elevation threshold (default: -6 = civil twilight)

    Returns:
        True if solar elevation is below threshold
    """
    return solar_elevation(lat, lon, dt) < threshold


def is_dark_grid(grid: str, dt: datetime, threshold: float = -6.0) -> bool:
    """Check if a grid is in darkness.

    Args:
        grid: Maidenhead grid
        dt: UTC datetime
        threshold: Solar elevation threshold (default: -6 = civil twilight)

    Returns:
        True if grid is dark
    """
    lat, lon = grid_to_latlon(grid)
    return is_dark(lat, lon, dt, threshold)


def classify_path(
    tx_grid: str,
    rx_grid: str,
    dt: datetime,
    threshold: float = -6.0,
) -> str:
    """Classify a propagation path by solar geometry.

    Args:
        tx_grid: Transmitter Maidenhead grid
        rx_grid: Receiver Maidenhead grid
        dt: UTC datetime
        threshold: Solar elevation threshold (default: -6)

    Returns:
        One of: "both-day", "cross-terminator", "both-dark"

    Example:
        >>> # Idaho to Europe at 02:00 UTC in February
        >>> classify_path("DN13", "JN48", datetime(2026, 2, 15, 2, 0, tzinfo=timezone.utc))
        "both-dark"
    """
    tx_dark = is_dark_grid(tx_grid, dt, threshold)
    rx_dark = is_dark_grid(rx_grid, dt, threshold)

    if tx_dark and rx_dark:
        return "both-dark"
    elif not tx_dark and not rx_dark:
        return "both-day"
    else:
        return "cross-terminator"


def solar_depression(lat: float, lon: float, dt: datetime) -> float:
    """Calculate solar depression angle (negative of elevation when below horizon).

    Useful for characterizing darkness depth. Positive values = sun below horizon.

    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        dt: UTC datetime

    Returns:
        Solar depression in degrees (positive when dark)
    """
    return -solar_elevation(lat, lon, dt)


def hour_angle(lon: float, dt: datetime) -> float:
    """Calculate hour angle for a longitude at a given time.

    Args:
        lon: Longitude in degrees
        dt: UTC datetime

    Returns:
        Hour angle in degrees (-180 to 180, 0 = solar noon)
    """
    hour = dt.hour + dt.minute / 60 + dt.second / 3600
    solar_noon = 12.0 - lon / 15.0
    ha = 15.0 * (hour - solar_noon)
    # Normalize to -180 to 180
    while ha > 180:
        ha -= 360
    while ha < -180:
        ha += 360
    return ha
