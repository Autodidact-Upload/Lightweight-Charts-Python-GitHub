# Tutorial - Lightweight Charts for Python

## Getting Started

### Installation

1. **Clone or download the repository:**
   ```bash
   cd Lightweight-Charts-Python
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Your First Chart

Create a file named `my_first_chart.py`:

```python
from datetime import datetime, timedelta
import numpy as np
from lightweight_charts import Chart, LineStyleOptions

# Generate sample data
data = []
price = 100
base_date = datetime(2024, 1, 1)

for i in range(50):
    price += np.random.randn()
    data.append({
        "time": base_date + timedelta(days=i),
        "value": price
    })

# Create and display chart
chart = Chart(width=1200, height=600, title="My First Chart")
line = chart.add_line_series("Price", LineStyleOptions(color="#2196F3"))
line.set_data(data)
chart.update_time_scale_data(data)
chart.render()
```

Run it:
```bash
python my_first_chart.py
```

---

## Working with Series

### Line Series

Perfect for displaying trends and moving averages:

```python
from lightweight_charts import Chart, LineStyleOptions
from datetime import datetime

chart = Chart()

# Create line series
line = chart.add_line_series(
    "My Line",
    LineStyleOptions(
        color="#FF5722",
        width=3
    )
)

data = [
    {"time": datetime(2024, 1, 1), "value": 100},
    {"time": datetime(2024, 1, 2), "value": 102},
    {"time": datetime(2024, 1, 3), "value": 101},
]

line.set_data(data)
chart.render()
```

---

### Candlestick Series

For OHLC (Open, High, Low, Close) data:

```python
from lightweight_charts import Chart, CandleStickStyleOptions
from datetime import datetime

chart = Chart()

candles = chart.add_candlestick_series(
    "BTC/USD",
    CandleStickStyleOptions(
        up_color="#26a69a",    # Green
        down_color="#ef5350",  # Red
        wick_visible=True,
        border_visible=True
    )
)

ohlc_data = [
    {
        "time": datetime(2024, 1, 1),
        "open": 50000,
        "high": 51000,
        "low": 49500,
        "close": 50500
    },
    {
        "time": datetime(2024, 1, 2),
        "open": 50500,
        "high": 52000,
        "low": 50000,
        "close": 51500
    }
]

candles.set_data(ohlc_data)
chart.render()
```

---

## Multiple Series

Combine different series types on one chart:

```python
from lightweight_charts import (
    Chart,
    CandleStickStyleOptions,
    LineStyleOptions,
    HistogramStyleOptions
)

chart = Chart(width=1400, height=800, title="Multi-Series Chart")

# Add candlesticks
candles = chart.add_candlestick_series("OHLC")
candles.set_data(ohlc_data)

# Add moving average
ma_line = chart.add_line_series(
    "MA20",
    LineStyleOptions(color="#FF9800", width=2)
)
ma_line.set_data(ma_data)

# Add volume
volume = chart.add_histogram_series(
    "Volume",
    HistogramStyleOptions(color="#2196F3")
)
volume.set_data(volume_data)

# Update time scale
chart.update_time_scale_data(ohlc_data)

chart.render()
```

---

## Real-Time Data

For streaming data updates:

```python
# Initial data
initial_data = [...]
line.set_data(initial_data)

# Update loop
while True:
    new_data_point = get_latest_data()  # Your data source
    initial_data.append(new_data_point)
    
    line.set_data(initial_data)
    chart.update_time_scale_data(initial_data)
    chart._update_visuals()
    
    time.sleep(1)  # Update interval
```

---

## Next Steps

- Explore the `/examples` directory for more examples
- Check `/docs/API.md` for detailed API reference
- Read TradingView's documentation for chart concepts
- Contribute improvements back to the project

Happy charting!
