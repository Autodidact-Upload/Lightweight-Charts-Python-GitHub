"""
Debug script to understand crosshair behavior
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
    format='%(name)s - %(levelname)s - %(message)s'
)

def generate_data():
    """Generate only 20 candles so there's lots of empty space."""
    base_date = datetime(2024, 1, 1)
    data = []
    price = 100
    
    for i in range(20):  # Only 20 candles
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
    print("Crosshair Debug Test")
    print("=" * 70)
    print("\nOnly 20 candles - lots of empty space!")
    print("Move mouse to the RIGHT of the candles")
    print("Watch the DEBUG output in console")
    print("=" * 70)
    
    chart = Chart(
        title="Crosshair Debug - Only 20 Candles",
        background_color="#1e1e1e",
        width=1400,
        height=700
    )

    ohlc_data = generate_data()
    print(f"\nData: {len(ohlc_data)} candles (0-19)")

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
    chart.set_crosshair_colors("#FFFF00", "#FFFF00")  # Bright yellow

    def on_move(position):
        print(f"\n{'='*60}")
        print(f"Mouse moved:")
        print(f"  X: {position.x:.2f}")
        print(f"  Y: {position.y:.2f}")
        print(f"  Price: ${position.price:.2f}" if position.price else "  Price: None")
        print(f"  Has data: {position.series_data is not None}")
        if position.series_data:
            print(f"  Data index: {position.data_index}")
        print(f"{'='*60}")

    chart.subscribe_crosshair_move(on_move)

    print("\n🚀 Move mouse around and watch console output")
    chart.render()

if __name__ == "__main__":
    main()
