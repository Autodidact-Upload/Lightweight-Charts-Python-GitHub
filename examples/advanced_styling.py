"""
Example 6: Advanced Styling and Customization
Demonstrating custom colors and styles
"""

import sys
from pathlib import Path
import os

# Suppress Qt DPI warning on Windows
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lightweight_charts import (
    Chart,
    LineStyleOptions,
    CandleStickStyleOptions,
    HistogramStyleOptions
)
from datetime import datetime, timedelta
import numpy as np


def generate_market_data(num_candles: int = 100):
    """Generate realistic market data."""
    base_date = datetime(2024, 1, 1)
    ohlc_data = []
    price = 50000  # Bitcoin-like price
    
    for i in range(num_candles):
        date = base_date + timedelta(hours=i)
        
        open_price = price
        close_price = price + np.random.randn() * 500
        high_price = max(open_price, close_price) + abs(np.random.randn() * 300)
        low_price = min(open_price, close_price) - abs(np.random.randn() * 300)
        volume = np.random.randint(100000000, 1000000000)
        
        ohlc_data.append({
            "time": date,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": volume
        })
        
        price = close_price
    
    return ohlc_data


def main():
    # Create chart with dark theme
    chart = Chart(
        width=1400,
        height=800,
        title="Advanced Styling - Dark Theme",
        background_color="#1e1e1e"
    )

    # Generate data
    ohlc_data = generate_market_data(100)

    # Add candlestick series with custom colors
    candle_series = chart.add_candlestick_series(
        "BTC/USD",
        CandleStickStyleOptions(
            up_color="#00FF41",      # Neon green
            down_color="#FF0040",    # Hot pink
            wick_color="#FFFFFF",
            border_up_color="#00FF41",
            border_down_color="#FF0040",
            wick_visible=True,
            border_visible=True,
            body_width=0.8
        )
    )
    candle_series.set_data(ohlc_data)

    # Add EMA (exponential moving average) line
    ema_data = []
    alpha = 2 / (len(ohlc_data) + 1)
    ema = ohlc_data[0]["close"]
    
    for candle in ohlc_data:
        ema = candle["close"] * alpha + ema * (1 - alpha)
        ema_data.append({
            "time": candle["time"],
            "value": ema
        })

    ema_series = chart.add_line_series(
        "EMA12",
        LineStyleOptions(
            color="#FFD700",  # Gold
            width=3
        )
    )
    ema_series.set_data(ema_data)

    # Add volume histogram
    volume_data = [
        {"time": d["time"], "value": d["volume"] / 1e8}
        for d in ohlc_data
    ]
    
    volume_series = chart.add_histogram_series(
        "Volume",
        HistogramStyleOptions(
            color="#00BFFF",  # Deep sky blue
            bar_width=0.6
        )
    )
    volume_series.set_data(volume_data)

    # Set time scale
    chart.update_time_scale_data(ohlc_data)

    # Render chart
    print("Rendering chart... Close the window to exit.")
    chart.render()


if __name__ == "__main__":
    main()
