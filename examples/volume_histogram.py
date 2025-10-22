"""
Example 5: Volume Histogram
Histogram chart for volume analysis
"""

import sys
from pathlib import Path
import os

# Suppress Qt DPI warning on Windows
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lightweight_charts import Chart, HistogramStyleOptions
from datetime import datetime, timedelta
import numpy as np


def generate_volume_data(num_candles: int = 100):
    """Generate OHLC data with volume."""
    base_date = datetime(2024, 1, 1)
    data = []
    price = 100
    
    for i in range(num_candles):
        date = base_date + timedelta(days=i)
        
        open_price = price
        close_price = price + np.random.randn() * 3
        volume = np.random.randint(1000000, 10000000)
        
        data.append({
            "time": date,
            "open": open_price,
            "high": max(open_price, close_price) + abs(np.random.randn() * 2),
            "low": min(open_price, close_price) - abs(np.random.randn() * 2),
            "close": close_price,
            "volume": volume / 1e6  # Convert to millions
        })
        
        price = close_price
    
    return data


def main():
    # Create chart
    chart = Chart(
        width=1200,
        height=600,
        title="Volume Histogram - Trading Activity"
    )

    # Generate data
    data = generate_volume_data(100)

    # Add histogram series for volume
    volume_series = chart.add_histogram_series(
        "Volume",
        HistogramStyleOptions(
            color="#2196F3",
            bar_width=0.7
        )
    )
    
    volume_data = [{"time": d["time"], "value": d["volume"]} for d in data]
    volume_series.set_data(volume_data)

    # Set time scale
    chart.update_time_scale_data(volume_data)

    # Render chart
    print("Rendering chart... Close the window to exit.")
    chart.render()


if __name__ == "__main__":
    main()
