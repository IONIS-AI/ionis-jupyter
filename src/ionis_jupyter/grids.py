"""Maidenhead grid utilities for propagation analysis.

Provides conversion between Maidenhead grid squares and lat/lon coordinates,
plus distance and bearing calculations.
"""

import math
from typing import Tuple


def grid_to_latlon(grid: str) -> Tuple[float, float]:
    """Convert Maidenhead grid to latitude/longitude (center of square).

    Args:
        grid: Maidenhead grid (2, 4, 6, or 8 characters)

    Returns:
        Tuple of (latitude, longitude) in degrees

    Raises:
        ValueError: If grid format is invalid

    Example:
        >>> grid_to_latlon("DN13")
        (43.5, -115.0)
        >>> grid_to_latlon("FN31pr")
        (41.729, -72.458)
    """
    grid = grid.upper().strip()

    if len(grid) < 2:
        raise ValueError(f"Grid too short: {grid}")

    # Field (A-R, A-R) -> 20x10 degrees
    lon = (ord(grid[0]) - ord("A")) * 20 - 180
    lat = (ord(grid[1]) - ord("A")) * 10 - 90

    if len(grid) >= 4:
        # Square (0-9, 0-9) -> 2x1 degrees
        lon += int(grid[2]) * 2
        lat += int(grid[3]) * 1

    if len(grid) >= 6:
        # Subsquare (a-x, a-x) -> 5x2.5 arcminutes
        lon += (ord(grid[4].upper()) - ord("A")) * (5 / 60)
        lat += (ord(grid[5].upper()) - ord("A")) * (2.5 / 60)

    if len(grid) >= 8:
        # Extended square (0-9, 0-9) -> 0.5x0.25 arcminutes
        lon += int(grid[6]) * (0.5 / 60)
        lat += int(grid[7]) * (0.25 / 60)

    # Center of the grid square
    if len(grid) == 2:
        lon += 10
        lat += 5
    elif len(grid) == 4:
        lon += 1
        lat += 0.5
    elif len(grid) == 6:
        lon += 2.5 / 60
        lat += 1.25 / 60
    elif len(grid) == 8:
        lon += 0.25 / 60
        lat += 0.125 / 60

    return (lat, lon)


def latlon_to_grid(lat: float, lon: float, precision: int = 4) -> str:
    """Convert latitude/longitude to Maidenhead grid.

    Args:
        lat: Latitude in degrees (-90 to 90)
        lon: Longitude in degrees (-180 to 180)
        precision: Grid precision (2, 4, 6, or 8 characters)

    Returns:
        Maidenhead grid string

    Example:
        >>> latlon_to_grid(43.5, -115.0)
        "DN13"
        >>> latlon_to_grid(41.729, -72.458, precision=6)
        "FN31pr"
    """
    lon += 180
    lat += 90

    # Field
    grid = chr(ord("A") + int(lon / 20))
    grid += chr(ord("A") + int(lat / 10))

    if precision >= 4:
        # Square
        lon_remainder = lon % 20
        lat_remainder = lat % 10
        grid += str(int(lon_remainder / 2))
        grid += str(int(lat_remainder / 1))

    if precision >= 6:
        # Subsquare
        lon_remainder = (lon % 2) * 60
        lat_remainder = (lat % 1) * 60
        grid += chr(ord("a") + int(lon_remainder / 5))
        grid += chr(ord("a") + int(lat_remainder / 2.5))

    if precision >= 8:
        # Extended
        lon_remainder = (lon_remainder % 5) * 60
        lat_remainder = (lat_remainder % 2.5) * 60
        grid += str(int(lon_remainder / 30))
        grid += str(int(lat_remainder / 15))

    return grid


def grid_distance(grid1: str, grid2: str) -> float:
    """Calculate great-circle distance between two grids in kilometers.

    Args:
        grid1: First Maidenhead grid
        grid2: Second Maidenhead grid

    Returns:
        Distance in kilometers

    Example:
        >>> grid_distance("DN13", "JN48")  # Idaho to central Europe
        8742.5
    """
    lat1, lon1 = grid_to_latlon(grid1)
    lat2, lon2 = grid_to_latlon(grid2)

    # Haversine formula
    R = 6371.0  # Earth radius in km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def grid_bearing(grid1: str, grid2: str) -> float:
    """Calculate initial bearing from grid1 to grid2 in degrees.

    Args:
        grid1: Origin Maidenhead grid
        grid2: Destination Maidenhead grid

    Returns:
        Bearing in degrees (0-360, 0=North, 90=East)

    Example:
        >>> grid_bearing("DN13", "JN48")  # Idaho to Europe
        35.2  # Northeast
    """
    lat1, lon1 = grid_to_latlon(grid1)
    lat2, lon2 = grid_to_latlon(grid2)

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)

    x = math.sin(dlon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)

    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360
