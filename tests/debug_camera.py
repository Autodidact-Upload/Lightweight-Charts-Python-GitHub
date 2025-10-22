"""
Advanced debug script to understand what's happening with scrolling
"""

import sys
from pathlib import Path
import os

os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lightweight_charts import Chart, CandleStickStyleOptions
from datetime import datetime, timedelta
import numpy as np
import logging

# Enable DEBUG logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s'
)

def generate_data():
    base_date = datetime(2024, 1, 1)
    data = []
    price = 100
    
    for i in range(50):
        date = base_date + timedelta(days=i)
        open_price = price
        close_price = price + np.random.randn() * 2
        high_price = max(open_price, close_price) + abs(np.random.randn())
        low_price = min(open_price, close_price) - abs(np.random.randn())
        
        data.append({
            "time": date,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price
        })
        price = close_price
    
    return data

def main():
    print("=" * 70)
    print("Crosshair Camera Debug")
    print("=" * 70)
    print("\n🎯 Test this:")
    print("   1. Move mouse over the chart (don't move it after)")
    print("   2. Scroll UP with mouse wheel")
    print("   3. Watch console - does 'Camera changed' appear?")
    print("   4. Does the horizontal crosshair line move up?")
    print("=" * 70)
    
    chart = Chart(
        title="Camera Debug - Scroll Up/Down",
        background_color="#1e1e1e",
        width=1400,
        height=700
    )

    ohlc_data = generate_data()
    candles = chart.add_candlestick_series(
        "Price",
        CandleStickStyleOptions(
            up_color="#26a69a",
            down_color="#ef5350",
            wick_color="#FFFFFF"
        )
    )
    candles.set_data(ohlc_data)
    chart.update_time_scale_data(ohlc_data)
    
    # Make crosshair VERY visible
    chart.set_crosshair_colors("#00FF00", "#00FF00")  # Bright green
    
    print("\n✅ Chart ready - Move mouse, then scroll!")
    print("   Watch for 'Camera changed' messages\n")
    
    chart.render()

if __name__ == "__main__":
    main()
