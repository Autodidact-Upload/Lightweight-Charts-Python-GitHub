# API Reference - Lightweight Charts for Python

## Table of Contents
1. [Chart](#chart)
2. [Series Classes](#series-classes)
3. [Data Types](#data-types)
4. [Scales](#scales)
5. [Utilities](#utilities)

---

## Chart

### `Chart`

Main chart class for rendering financial data.

#### Constructor

```python
Chart(
    width: int = 800,
    height: int = 600,
    title: str = "Financial Chart",
    background_color: str = "#ffffff"
)
```

**Parameters:**
- `width`: Chart width in pixels
- `height`: Chart height in pixels
- `title`: Window title
- `background_color`: Background color in hex format

#### Methods

##### `add_line_series(name, style)`

Add a line series to the chart.

```python
def add_line_series(
    name: str = "",
    style: Optional[LineStyleOptions] = None
) -> LineSeries
```

**Returns:** LineSeries instance

**Example:**
```python
chart = Chart()
line = chart.add_line_series("Price")
line.set_data(data)
```

---

##### `add_candlestick_series(name, style)`

Add a candlestick series.

```python
def add_candlestick_series(
    name: str = "",
    style: Optional[CandleStickStyleOptions] = None
) -> CandlestickSeries
```

**Returns:** CandlestickSeries instance

**Example:**
```python
chart = Chart()
candles = chart.add_candlestick_series("OHLC")
candles.set_data(ohlc_data)
```

---

##### `add_area_series(name, style)`

Add an area series.

```python
def add_area_series(
    name: str = "",
    style: Optional[AreaStyleOptions] = None
) -> AreaSeries
```

**Returns:** AreaSeries instance

---

##### `add_histogram_series(name, style)`

Add a histogram series.

```python
def add_histogram_series(
    name: str = "",
    style: Optional[HistogramStyleOptions] = None
) -> HistogramSeries
```

**Returns:** HistogramSeries instance

---

##### `render()`

Render and display the chart.

```python
def render() -> None
```

**Example:**
```python
chart.render()  # Displays the chart window
```

---

##### `pan(delta)`

Pan the chart left/right.

```python
def pan(delta: float) -> None
```

**Parameters:**
- `delta`: Number of bars to pan

---

##### `zoom(factor, center)`

Zoom the chart in/out.

```python
def zoom(factor: float, center: Optional[float] = None) -> None
```

**Parameters:**
- `factor`: Zoom factor (>1 = zoom in, <1 = zoom out)
- `center`: Zoom center point (0-1, default 0.5 = middle)

---

## Series Classes

### `LineSeries`

Line chart series.

#### Methods

##### `set_data(data)`

Set series data.

```python
def set_data(data: List[Dict[str, Any]]) -> None
```

**Data format:**
```python
[
    {"time": datetime(2024, 1, 1), "value": 100.5},
    {"time": datetime(2024, 1, 2), "value": 102.3},
]
```

---

### `CandlestickSeries`

Candlestick chart series for OHLC data.

#### Methods

##### `set_data(data)`

Set OHLC data.

**Data format:**
```python
[
    {
        "time": datetime(2024, 1, 1),
        "open": 100.0,
        "high": 102.5,
        "low": 99.5,
        "close": 101.0,
        "volume": 1000000  # Optional
    }
]
```

---

### `AreaSeries`

Area chart with fill.

---

### `HistogramSeries`

Histogram/bar chart series.

---

## Data Types

### `LineStyleOptions`

Configuration for line series.

```python
@dataclass
class LineStyleOptions:
    color: str = "#2196F3"
    width: int = 2
    style: str = "solid"  # solid, dotted, dashed
```

---

### `CandleStickStyleOptions`

Configuration for candlestick series.

```python
@dataclass
class CandleStickStyleOptions:
    up_color: str = "#26a69a"          # Green
    down_color: str = "#ef5350"        # Red
    wick_color: str = "#333333"
    border_up_color: str = "#26a69a"
    border_down_color: str = "#ef5350"
    wick_visible: bool = True
    border_visible: bool = True
    body_width: float = 0.6
```

---

### `AreaStyleOptions`

Configuration for area series.

```python
@dataclass
class AreaStyleOptions:
    line_color: str = "#2196F3"
    fill_color: str = "#2196F3"
    line_width: int = 2
    fill_alpha: float = 0.3
```

---

## Usage Examples

### Basic Line Chart

```python
from lightweight_charts import Chart, LineStyleOptions
from datetime import datetime, timedelta

chart = Chart(width=1200, height=600)

data = [
    {"time": datetime(2024, 1, 1), "value": 100},
    {"time": datetime(2024, 1, 2), "value": 102},
]

line = chart.add_line_series("Stock", LineStyleOptions(color="#2196F3"))
line.set_data(data)
chart.update_time_scale_data(data)
chart.render()
```

### Candlestick Chart

```python
from lightweight_charts import Chart, CandleStickStyleOptions

chart = Chart()

ohlc_data = [
    {
        "time": datetime(2024, 1, 1),
        "open": 100,
        "high": 102,
        "low": 99,
        "close": 101
    }
]

candles = chart.add_candlestick_series("BTC/USD")
candles.set_data(ohlc_data)
chart.render()
```

---
