#!/usr/bin/env python3
"""Generate sample SQLite datasets for Binder demos.

Creates small, realistic sample data that demonstrates notebook functionality
without requiring the full SourceForge downloads.

Run: python scripts/generate_sample_data.py
Output: data/sample/*.sqlite
"""

import sqlite3
import random
from pathlib import Path

# Sample grids (mix of US, EU, Asia, Oceania)
TX_GRIDS = ["DN13", "DN31", "CM87", "FN31", "EM73", "DM79", "CN87", "EN91"]
RX_GRIDS = ["JN48", "JO31", "IO91", "JN39", "PM95", "QM05", "PK04", "OF88"]

# Band IDs
BANDS = [102, 103, 105, 107, 108, 109, 110, 111]  # 160m through 10m
BAND_NAMES = {102: "160m", 103: "80m", 105: "40m", 107: "20m",
              108: "17m", 109: "15m", 110: "12m", 111: "10m"}

OUT_DIR = Path(__file__).parent.parent / "data" / "sample"


def generate_propagation_signatures(n_rows=5000):
    """Generate realistic propagation signatures."""
    rows = []
    for _ in range(n_rows):
        tx = random.choice(TX_GRIDS)
        rx = random.choice(RX_GRIDS)
        band = random.choice(BANDS)
        hour = random.randint(0, 23)
        month = random.randint(1, 12)

        # Realistic SNR based on band and hour
        base_snr = -5

        # High bands better during day
        if band >= 109:  # 15m, 10m
            if 10 <= hour <= 20:
                base_snr += random.uniform(3, 8)
            else:
                base_snr -= random.uniform(5, 15)
        # Low bands better at night
        elif band <= 103:  # 80m, 160m
            if hour < 6 or hour > 20:
                base_snr += random.uniform(2, 6)
            else:
                base_snr -= random.uniform(3, 8)
        else:  # Mid bands
            base_snr += random.uniform(-3, 5)

        # Add noise
        snr = base_snr + random.gauss(0, 3)
        snr = max(-30, min(20, snr))  # Clamp to realistic range

        # Solar indices
        sfi = random.uniform(70, 200)
        kp = random.uniform(0, 6)

        # Distance (km)
        distance = random.randint(1000, 15000)
        azimuth = random.randint(0, 359)

        rows.append({
            "tx_grid_4": tx,
            "rx_grid_4": rx,
            "band": band,
            "hour": hour,
            "month": month,
            "median_snr": round(snr, 1),
            "spot_count": random.randint(3, 500),
            "snr_std": round(random.uniform(1, 6), 2),
            "reliability": round(random.uniform(0.3, 1.0), 3),
            "avg_sfi": round(sfi, 1),
            "avg_kp": round(kp, 1),
            "avg_distance": distance,
            "avg_azimuth": azimuth,
        })

    return rows


def generate_solar_indices(n_days=1000):
    """Generate realistic solar indices."""
    rows = []
    # Start from 2020-01-01
    import datetime
    start = datetime.date(2020, 1, 1)

    for i in range(n_days):
        date = start + datetime.timedelta(days=i)

        # Simulate solar cycle (rough)
        cycle_phase = (i % 4000) / 4000  # ~11 year cycle compressed
        base_sfi = 70 + 130 * abs(0.5 - cycle_phase) * 2

        rows.append({
            "date": date.isoformat(),
            "sfi": round(base_sfi + random.gauss(0, 15), 1),
            "ssn": max(0, int(base_sfi - 50 + random.gauss(0, 20))),
            "kp_max": round(random.uniform(0, 7), 1),
            "kp_avg": round(random.uniform(0, 4), 1),
        })

    return rows


def generate_grid_lookup():
    """Generate grid lookup table."""
    rows = []
    # Generate a grid of grids
    for field1 in "ABCDEFGHIJKLMNOPQR":
        for field2 in "ABCDEFGHIJKLMNOPQR":
            for sq1 in range(10):
                for sq2 in range(10):
                    grid = f"{field1}{field2}{sq1}{sq2}"

                    # Calculate lat/lon
                    lon = (ord(field1) - ord('A')) * 20 - 180 + sq1 * 2 + 1
                    lat = (ord(field2) - ord('A')) * 10 - 90 + sq2 * 1 + 0.5

                    rows.append({
                        "grid_4": grid,
                        "lat": round(lat, 4),
                        "lon": round(lon, 4),
                    })

    # Just return a sample (full would be 32,400 rows)
    return random.sample(rows, 1000)


def create_sqlite(path, table_name, rows, schema):
    """Create SQLite file with data."""
    conn = sqlite3.connect(str(path))

    # Create table
    cols = ", ".join(f"{name} {dtype}" for name, dtype in schema)
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({cols})")

    # Insert data
    if rows:
        placeholders = ", ".join("?" * len(schema))
        col_names = [name for name, _ in schema]
        conn.executemany(
            f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({placeholders})",
            [[row[name] for name in col_names] for row in rows]
        )

    conn.commit()
    conn.close()
    print(f"Created {path} ({len(rows)} rows)")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Propagation signatures schema
    sig_schema = [
        ("tx_grid_4", "TEXT"),
        ("rx_grid_4", "TEXT"),
        ("band", "INTEGER"),
        ("hour", "INTEGER"),
        ("month", "INTEGER"),
        ("median_snr", "REAL"),
        ("spot_count", "INTEGER"),
        ("snr_std", "REAL"),
        ("reliability", "REAL"),
        ("avg_sfi", "REAL"),
        ("avg_kp", "REAL"),
        ("avg_distance", "INTEGER"),
        ("avg_azimuth", "INTEGER"),
    ]

    # Generate WSPR sample
    wspr_rows = generate_propagation_signatures(5000)
    create_sqlite(
        OUT_DIR / "wspr_signatures_sample.sqlite",
        "wspr_signatures",
        wspr_rows,
        sig_schema
    )

    # Generate contest sample
    contest_rows = generate_propagation_signatures(2000)
    create_sqlite(
        OUT_DIR / "contest_signatures_sample.sqlite",
        "contest_signatures",
        contest_rows,
        sig_schema
    )

    # Generate solar indices
    solar_schema = [
        ("date", "TEXT"),
        ("sfi", "REAL"),
        ("ssn", "INTEGER"),
        ("kp_max", "REAL"),
        ("kp_avg", "REAL"),
    ]
    solar_rows = generate_solar_indices(1000)
    create_sqlite(
        OUT_DIR / "solar_indices_sample.sqlite",
        "solar_indices",
        solar_rows,
        solar_schema
    )

    # Generate grid lookup
    grid_schema = [
        ("grid_4", "TEXT"),
        ("lat", "REAL"),
        ("lon", "REAL"),
    ]
    grid_rows = generate_grid_lookup()
    create_sqlite(
        OUT_DIR / "grid_lookup_sample.sqlite",
        "grid_lookup",
        grid_rows,
        grid_schema
    )

    print(f"\nSample data generated in {OUT_DIR}")


if __name__ == "__main__":
    main()
