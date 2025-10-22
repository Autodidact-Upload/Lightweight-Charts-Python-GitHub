# Multi-Pane Charts Guide

Complete guide to using multi-pane charts in Lightweight Charts Python.

## Overview

Multi-pane charts allow you to create professional trading dashboards with multiple independent chart areas, similar to TradingView. Each pane has its own:

- ✅ **Independent Y-axis** (price scale)
- ✅ **Own series** (candlesticks, lines, histograms, etc.)
- ✅ **Visual separation** with border lines
- ✅ **Synchronized X-axis** (time scale) across all panes
- ✅ **Synchronized crosshair** that spans all panes

## Architecture

The multi-pane system uses a **grid layout** where each pane is an independent Vispy view with its own camera and viewport:

```
┌─────────────────────────────────┐
│  Main Pane (75%)                │
│  - Candlesticks                 │
│  - Full pan/zoom (X & Y)        │
├─────────────────────────────────┤ ← Border line
│  Volume Pane (25%)              │
│  - Histogram                    │
│  - Y-axis locked (X pan only)   │
└─────────────────────────────────┘
```

**Key Design:**
- First pane = **main pane** with full interactivity
- Other panes = **Y-axis locked** (horizontal scroll only)
- All panes share the same **time scale**
- Each pane has its own **price scale**

## Basic Usage

### Creating a Multi-Pane Chart

```python
from lightweight_charts import Chart

# Create chart
chart = Chart(1400, 800, title="Trading Dashboard")

# Add panes with height ratios
main_pane = chart.add_pane("Price", height_ratio=0.75)     # 75% height
volume_pane = chart.add_pane("Volume", height_ratio=0.25)  # 25% height

# Add series to each pane
candles = main_pane.add_candlestick_series("BTC/USD")
candles.set_data(ohlc_data)

volume = volume_pane.add_histogram_series("Volume")
volume.set_data(volume_data)

# Update time scale and render
chart.update_time_scale_data(ohlc_data)
chart.render()
```

### Height Ratios

Height ratios are **relative** and automatically normalized:

```python
# These are equivalent:
pane1 = chart.add_pane("A", height_ratio=3)  # 75%
pane2 = chart.add_pane("B", height_ratio=1)  # 25%

# Same as:
pane1 = chart.add_pane("A", height_ratio=0.75)  # 75%
pane2 = chart.add_pane("B", height_ratio=0.25)  # 25%

# Also same as:
pane1 = chart.add_pane("A", height_ratio=300)  # 75%
pane2 = chart.add_pane("B", height_ratio=100)  # 25%
```

**Recommended ratios:**
- 2 panes: `0.85` / `0.15` (main/indicator)
- 3 panes: `0.60` / `0.20` / `0.20`
- 4 panes: `0.50` / `0.20` / `0.15` / `0.15`

## Complete Example

See full examples in the main guide...

---

**Version:** 1.0.0  
**Status:** Production Ready  
**Last Updated:** October 2025
