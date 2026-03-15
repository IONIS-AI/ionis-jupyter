# Vandenberg Launch TID Correlation Dataset

WSPR 20m spot counts correlated with SpaceX Falcon 9 launches from Vandenberg SFB (SLC-4E), 2022-2025.

## Purpose

Supplementary data for Travelling Ionospheric Disturbance (TID) research. Rocket exhaust
creates gravity waves that modulate F-layer electron density, potentially enhancing or
disrupting HF propagation. This dataset provides WSPR 20m spot counts during launch windows
compared to control days, with solar conditions included to rule out confounds.

Motivated by Isobel Smith's HamSCI mailing list research on SpaceX-induced TIDs observed
in WSPR 20m data (November 2025).

## Files

| File | Rows | Description |
|------|------|-------------|
| `vandenberg_tid_detail.csv` | 84 | Daily spot counts for 12 launches, 7 days each (launch day + 3 control days before/after) |
| `vandenberg_tid_summary.csv` | 12 | Per-launch summary with z-scores and percentage change |

## Columns — Detail

| Column | Description |
|--------|-------------|
| `mission` | SpaceX mission name |
| `launch_date` | Date of launch (YYYY-MM-DD) |
| `window_start_utc` | Hour (UTC) of analysis window start (launch time rounded down) |
| `spot_date` | Date of this row's spot count |
| `day_type` | `launch` or `control` |
| `wspr_20m_spots` | Total WSPR spots on 20m band during 3-hour window |
| `mean_snr` | Mean SNR (dB) across all spots in window |
| `snr_std` | Standard deviation of SNR (dB) — elevated values may indicate TID activity |
| `unique_tx` | Number of unique transmitting stations |
| `unique_rx` | Number of unique receiving stations |
| `sfi` | Solar Flux Index (SFU) — daily value from GFZ Potsdam |
| `ssn` | Sunspot Number — daily value from GFZ Potsdam |
| `kp` | Kp index — daily average from GFZ Potsdam |

## Columns — Summary

| Column | Description |
|--------|-------------|
| `mission` | SpaceX mission name |
| `launch_date` | Date of launch |
| `launch_hour` | UTC hour of launch |
| `launch_spots` | WSPR 20m spots in 3-hour window on launch day |
| `control_avg` | Mean spot count across 6 control days |
| `control_std` | Standard deviation of control day spot counts |
| `pct_change` | Percentage change: launch day vs control average |
| `z_score` | (launch_spots - control_avg) / control_std |

## Launches Included

| Mission | Date | UTC | Z-Score | Notes |
|---------|------|-----|---------|-------|
| Sentinel-6B | 2025-11-17 | 05z | +6.20 | Strongest anomaly |
| NROL-87 | 2022-02-02 | 20z | +2.87 | Significant |
| NROL-57 | 2025-03-21 | 06z | +1.37 | Moderate |
| Starlink 5-2 | 2023-01-19 | 15z | +1.37 | Moderate |
| SARah-1 | 2022-06-18 | 14z | +0.72 | Weak |
| NROL-113 | 2024-09-06 | 03z | +0.67 | Weak |
| Transporter-10 | 2024-03-04 | 22z | +0.15 | None |
| SPHEREx | 2025-03-11 | 03z | -0.50 | None |
| Transporter-13 | 2025-03-15 | 06z | -0.59 | None |
| Transporter-8 | 2023-06-12 | 21z | -0.99 | None |
| Transporter-9 | 2023-11-11 | 18z | -2.64 | Negative |
| NROL-167 | 2024-10-24 | 17z | -2.74 | Negative |

## Key Finding

5 of 12 launches show elevated WSPR spot counts (z > 0), but only 2 are statistically
significant (z > 2). Sentinel-6B (z = 6.2) is a massive outlier — 56% more spots than
control days despite declining solar conditions (SFI dropped 132 to 122, SSN dropped 100
to 57 on launch day).

The mixed results suggest TID effects are conditional on:
- Time of day (ionospheric geometry relative to launch trajectory)
- Season (F-layer height and density)
- Solar cycle position (background ionization level)
- Launch trajectory and orbit inclination

## Methodology

- **Band**: WSPR 20m (band ID 107, 14.0956 MHz)
- **Window**: 3 hours starting at launch time (rounded to nearest hour)
- **Control days**: 3 days before and 3 days after launch, same hour window
- **Solar data**: GFZ Potsdam daily SFI/SSN, Kp daily average
- **Source**: 10.8 billion WSPR spots in ClickHouse (`wspr.bronze`), 2008-2026

## Limitations

- Launch times are approximate (rounded to nearest hour for WSPR alignment)
- Some launches may be from Cape Canaveral, not Vandenberg — verify against official records
- No spatial filtering — spots are global, not restricted to paths near launch site
- 3-day control window may not capture weekly patterns
- Solar conditions are daily averages — Kp has 3-hour resolution in the raw data

## Suggested Extensions

1. **Spatial filtering**: Restrict to paths crossing the western US / eastern Pacific
2. **SNR distribution analysis**: Compare launch vs control day SNR histograms
3. **Multi-band**: Repeat analysis for 40m, 30m, 15m
4. **More launches**: Extend to 50+ Vandenberg launches (2023-2025 cadence supports this)
5. **Temporal resolution**: Use 2-minute WSPR cycle data for periodicity analysis

## Citation

```
KI7MT Sovereign AI Lab (2026). Vandenberg Launch TID Correlation Dataset.
WSPR data from wsprnet.org. Solar indices from GFZ Potsdam.
Available at: https://sourceforge.net/projects/ionis-ai/
```

## License

MIT License. See repository root for details.

## Related

- Notebook: `notebooks/06-tid-detection.ipynb` (Section 9: Case Study)
- IONIS datasets: https://sourceforge.net/projects/ionis-ai/
- Tools: https://qso-graph.io
