"""
Simple Multi-Pane Example
Shows basic multi-pane setup with price and volume
"""

from lightweight_charts import Chart, CandleStickStyleOptions, HistogramStyleOptions
from datetime import datetime, timedelta
import numpy as np

# Generate sample data
def generate_data(days=100):
    np.random.seed(42)
    data = []
    price = 100.0
    base_date = datetime(2024, 1, 1)
    
    for i in range(days):
        price += np.random.randn() * 2
        daily_range = abs(np.random.randn()) * 3
        
        open_p = price + np.random.randn() * 0.5
        close_p = price + np.random.randn() * 0.5
        high_p = max(open_p, close_p) + daily_range * 0.7
        low_p = min(open_p, close_p) - daily_range * 0.3
        volume = 1000000 * (0.5 + np.random.rand())
        
        data.append({
            "time": base_date + timedelta(days=i),
            "open": open_p,
            "high": high_p,
            "low": low_p,
            "close": close_p,
            "volume": volume
        })
    
    return data

# Generate data
ohlc_data = generate_data(100)
volume_data = [{"time": d["time"], "value": d["volume"]} for d in ohlc_data]

# Create chart
chart = Chart(1200, 700, title="Price & Volume - Multi-Pane", background_color="#1E222D")

# Add two panes
price_pane = chart.add_pane("Price", height_ratio=0.85)  # 85% height
volume_pane = chart.add_pane("Volume", height_ratio=0.15)  # 15% height

# Add candlesticks to price pane
candles = price_pane.add_candlestick_series(
    "BTC/USD",
    CandleStickStyleOptions(up_color="#26A69A", down_color="#EF5350")
)
candles.set_data(ohlc_data)

# Add volume histogram to volume pane
volume = volume_pane.add_histogram_series(
    "Volume",
    HistogramStyleOptions(color="#4CAF50", bar_width=0.8)
)
volume.set_data(volume_data)

# Configure
chart.update_time_scale_data(ohlc_data)
chart.set_crosshair_colors(vert_color="#00FFFF", horiz_color="#FF00FF")

print("✅ Two-pane chart ready!")
print("📊 Price pane: 75% | Volume pane: 25%")
print("🎯 Crosshair synchronized across both panes")

# Render
chart.render()
