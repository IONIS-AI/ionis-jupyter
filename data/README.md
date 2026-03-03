# Data Directory

This directory is a placeholder. Datasets are downloaded separately.

## Download Datasets

```bash
# Install the download CLI
pip install ionis-mcp

# Download datasets (choose your bundle)
ionis-download --bundle minimal      # ~430 MB: contest + grids + solar
ionis-download --bundle recommended  # ~1.1 GB: + pskr + dscovr
ionis-download --bundle full         # ~15 GB: all 9 datasets
```

Datasets are stored in `~/.ionis-mcp/data/` by default.

## Direct Download

Alternatively, download from SourceForge:

https://sourceforge.net/projects/ionis-ai/files/

## Available Datasets

| Dataset | Size | Description |
|---------|------|-------------|
| wspr | ~2.3 GB | 93.6M WSPR signatures (2008-2026) |
| rbn | ~1.8 GB | 67.3M RBN signatures (2009-2026) |
| contest | ~150 MB | 5.7M contest signatures (2005-2025) |
| pskr | Growing | PSK Reporter signatures (2026+) |
| dxpedition | ~10 MB | 260K DXpedition signatures |
| solar | ~5 MB | Daily SFI/SSN/Kp (1932-2026) |
| dscovr | ~15 MB | DSCOVR L1 solar wind |
| grids | ~2 MB | 31.7K Maidenhead grid lookup |
| balloons | ~50 KB | 1,047 pico-balloon callsigns |
