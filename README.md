# ionis-jupyter

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/IONIS-AI/ionis-jupyter/main)
[![PyPI](https://img.shields.io/pypi/v/ionis-jupyter)](https://pypi.org/project/ionis-jupyter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Jupyter notebooks and helper library for HF propagation research using IONIS datasets.

## What's Inside

**175+ million propagation signatures** spanning 18 years (2008-2026), ready for analysis:

| Dataset | Signatures | Source | SNR Type |
|---------|------------|--------|----------|
| WSPR | 93.6M | 10.8B WSPR spots | Measured (-30 to +20 dB) |
| RBN | 67.3M | 2.2B CW/RTTY spots | Real measured (8-29 dB) |
| Contest | 5.7M | 234M SSB/RTTY QSOs | Anchored (+10/0 dB) |
| PSKR | Growing | PSK Reporter MQTT | Measured (-34 to +38 dB) |
| DXpedition | 260K | 3.9M rare-grid paths | Real measured |

Plus solar indices (1932-2026), DSCOVR solar wind, and IRI-2020 ionospheric atlas.

## Quick Start

### Option 1: Binder (No Install)

Click the Binder badge above to launch notebooks in the cloud — nothing to install.

### Option 2: Local Install

```bash
# Install packages
pip install ionis-jupyter ionis-mcp

# Download datasets (choose your bundle)
ionis-download --bundle minimal      # ~430 MB: contest + grids + solar
ionis-download --bundle recommended  # ~1.1 GB: + pskr + dscovr
ionis-download --bundle full         # ~15 GB: all 9 datasets

# Launch Jupyter
jupyter lab
```

## Notebooks

| Notebook | Description | Audience |
|----------|-------------|----------|
| `01-getting-started` | Load data, basic queries | Everyone |
| `02-band-openings` | Hour×month heatmaps per band | Contesters, DXers |
| `03-solar-correlation` | SFI effect on propagation | Researchers |
| `04-path-analysis` | TX→RX specific path deep dive | Path planners |
| `05-greyline-terminator` | Day/night boundary propagation | Low-band DXers |
| `06-tid-detection` | SNR variance for TID research | HamSCI, ionospheric science |
| `07-cross-source-comparison` | WSPR vs RBN vs Contest vs PSKR | Data scientists |
| `08-distance-vs-snr` | Signal decay with distance | Antenna analysts |
| `09-seasonal-patterns` | Summer vs winter, solar cycle | Long-term researchers |
| `10-ionis-model-api` | Query live IONIS predictions | API users |

## Helper Library

The `ionis_jupyter` package provides utilities for common tasks:

```python
from ionis_jupyter import (
    # Data loading
    load_dataset, list_datasets,

    # Grid calculations
    grid_to_latlon, grid_distance, grid_bearing,

    # Solar geometry
    solar_elevation, is_dark, classify_path,

    # Plotting
    plot_band_heatmap, plot_solar_correlation,
    plot_path_profile, plot_distance_snr,
)

# Load WSPR signatures
wspr = load_dataset("wspr")
print(f"Loaded {len(wspr):,} signatures")

# Filter to 20m band
wspr_20m = wspr[wspr["band"] == 107]

# Plot hour×month heatmap
plot_band_heatmap(wspr_20m, band=107)
```

## Data Directory

By default, datasets are stored in `~/.ionis-mcp/data/`. Override with:

```bash
export IONIS_DATA_DIR=/path/to/your/data
```

Or download directly:

```bash
# Specific datasets
ionis-download --datasets wspr,rbn,solar

# To custom directory
ionis-download --bundle minimal --data-dir /my/data/path
```

## For Researchers

This repository is designed for:

- **PhD students** studying ionospheric propagation
- **HamSCI** researchers analyzing TIDs, eclipse effects, greyline
- **Data scientists** needing labeled propagation data for ML
- **Contesters** analyzing historical band conditions
- **Amateur radio operators** exploring propagation patterns

## Citation

If you use these datasets in research, please cite:

```
IONIS-AI Propagation Datasets.
Greg Beam, KI7MT. IONIS-AI Project.
https://ionis-ai.com

Data sources: WSPRNet, Reverse Beacon Network, PSK Reporter, CQ Contests.
```

## Links

- **Datasets**: [SourceForge](https://sourceforge.net/projects/ionis-ai/files/)
- **MCP Server**: [ionis-mcp on PyPI](https://pypi.org/project/ionis-mcp/)
- **Project**: [IONIS-AI on GitHub](https://github.com/IONIS-AI)

## License

MIT — see [LICENSE](LICENSE).

Datasets are CC BY 4.0 (see per-directory LICENSE.md files on SourceForge).
