"""
Minimal test to understand the crosshair behavior
"""

import sys
from pathlib import Path
import os

os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lightweight_charts import Chart, CandleStickStyleOptions
from datetime import datetime, timedelta
import numpy as np

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
    print("Minimal Crosshair Test")
    print("=" * 70)
    print("\nInstructions:")
    print("1. Move mouse to CENTER of chart")
    print("2. KEEP MOUSE STILL (don't move it!)")
    print("3. Scroll UP slowly with mouse wheel")
    print("4. What happens to the crosshair?")
    print("   - Does horizontal line move UP with the chart?")
    print("   - Or does it stay in place?")
    print("=" * 70)
    
    chart = Chart(
        title="Crosshair Test - Don't Move Mouse, Just Scroll",
        background_color="#000000",  # Black background
        width=1200,
        height=800
    )

    ohlc_data = generate_data()
    candles = chart.add_candlestick_series(
        "Price",
        CandleStickStyleOptions(
            up_color="#00FF00",
            down_color="#FF0000",
            wick_color="#FFFFFF"
        )
    )
    candles.set_data(ohlc_data)
    chart.update_time_scale_data(ohlc_data)
    
    # Very bright crosshair
    chart.set_crosshair_colors("#FFFF00", "#FFFF00")  # Yellow
    
    print("\n✅ Chart ready!")
    print("   Move mouse to center, then scroll up")
    print("   Watch what the HORIZONTAL line does\n")
    
    chart.render()

if __name__ == "__main__":
    main()
