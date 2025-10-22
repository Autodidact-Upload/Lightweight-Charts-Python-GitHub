"""
Example 2: Candlestick Chart
OHLC candlestick chart showing price action
"""

import sys
from pathlib import Path
import os

# Suppress Qt DPI warning on Windows
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lightweight_charts import Chart, CandleStickStyleOptions
from datetime import datetime, timedelta
import numpy as np


def generate_ohlc_data(num_candles: int = 100):
    """Generate synthetic OHLC data."""
    base_date = datetime(2024, 1, 1)
    data = []
    price = 100
    
    for i in range(num_candles):
        date = base_date + timedelta(days=i)
        
        # Generate OHLC
        open_price = price
        close_price = price + np.random.randn() * 3
        high_price = max(open_price, close_price) + abs(np.random.randn() * 2)
        low_price = min(open_price, close_price) - abs(np.random.randn() * 2)
        
        data.append({
            "time": date,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": np.random.randint(1000000, 10000000)
        })
        
        price = close_price
    
    return data


def main():
    # Create chart
    chart = Chart(
        width=1200,
        height=600,
        title="Candlestick Chart - Bitcoin Price"
    )

    # Generate OHLC data
    ohlc_data = generate_ohlc_data(100)

    # Add candlestick series with custom styling
    candle_series = chart.add_candlestick_series(
        "BTC/USD",
        CandleStickStyleOptions(
            up_color="#26a69a",      # Green
            down_color="#ef5350",    # Red
            wick_color="#333333",
            wick_visible=True,
            border_visible=True
        )
    )
    candle_series.set_data(ohlc_data)

    # Set time scale data
    chart.update_time_scale_data(ohlc_data)

    # Render chart
    print("Rendering chart... Close the window to exit.")
    chart.render()


if __name__ == "__main__":
    main()
