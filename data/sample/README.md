# Sample Data for Binder Demos

This directory contains small sample datasets for demonstration purposes.

**These are synthetic/generated data** — realistic enough to demonstrate the
notebooks but not actual propagation observations.

## Files

| File | Rows | Description |
|------|------|-------------|
| `wspr_signatures_sample.sqlite` | 5,000 | Synthetic WSPR signatures |
| `contest_signatures_sample.sqlite` | 2,000 | Synthetic contest signatures |
| `solar_indices_sample.sqlite` | 1,000 | Synthetic solar indices |
| `grid_lookup_sample.sqlite` | 1,000 | Real Maidenhead grid coordinates |

## Usage

The `ionis_jupyter` loader automatically falls back to these samples when
the full datasets aren't available (e.g., in Binder environments).

```python
from ionis_jupyter import load_dataset, is_using_sample_data

df = load_dataset("wspr")  # Uses sample if full data not found
print(f"Using sample: {is_using_sample_data()}")
```

## For Real Analysis

Download the full datasets from SourceForge:

```bash
pip install ionis-mcp
ionis-download --bundle minimal  # ~430 MB
```

Full datasets: https://sourceforge.net/projects/ionis-ai/files/
