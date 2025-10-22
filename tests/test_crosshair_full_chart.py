"""
Test: Crosshair Full Chart Coverage
Verify that crosshair is visible everywhere on the chart, not just over candles
"""

import sys
from pathlib import Path
import os

os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lightweight_charts import Chart, CandleStickStyleOptions
from datetime import datetime, timedelta
import numpy as np

def generate_sparse_data():
    """Generate data with gaps to test empty space crosshair."""
    base_date = datetime(2024, 1, 1)
    data = []
    price = 100
    
    # First cluster: days 0-20
    for i in range(20):
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
    
    # GAP: days 21-50 (no data)
    
    # Second cluster: days 51-70
    for i in range(51, 71):
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
    print("Testing: Crosshair Full Chart Coverage")
    print("=" * 70)
    print("\n🎯 What to test:")
    print("   1. Move mouse BEFORE first candle (left side)")
    print("   2. Move mouse OVER candles")
    print("   3. Move mouse in the GAP (between clusters)")
    print("   4. Move mouse AFTER last candle (right side)")
    print("\n✅ Expected behavior:")
    print("   • Crosshair visible EVERYWHERE")
    print("   • Shows data when over candles")
    print("   • Shows price when over empty space")
    print("   • Never disappears!")
    print("\n💡 This is TradingView-like behavior!")
    print("=" * 70)
    
    # Create chart
    chart = Chart(
        title="Crosshair Test - Move Mouse Everywhere!",
        background_color="#1e1e1e",
        width=1400,
        height=700
    )

    # Generate sparse data with gaps
    ohlc_data = generate_sparse_data()
    print(f"\n📊 Generated {len(ohlc_data)} candles with a gap in the middle")

    # Add candlesticks
    candles = chart.add_candlestick_series(
        "Sparse Data",
        CandleStickStyleOptions(
            up_color="#26a69a",
            down_color="#ef5350",
            wick_color="#FFFFFF"
        )
    )
    candles.set_data(ohlc_data)

    # Set time scale
    chart.update_time_scale_data(ohlc_data)
    
    # Set crosshair colors
    chart.set_crosshair_colors("#888888", "#888888")

    # Add callback to show when crosshair is working
    def on_move(position):
        if position.series_data:
            print(f"✅ Over data: price=${position.price:.2f}, has OHLC data")
        else:
            print(f"✅ Over empty space: price=${position.price:.2f} (no data)")

    chart.subscribe_crosshair_move(on_move)

    print("\n🚀 Chart ready!")
    print("   • Move mouse EVERYWHERE on the chart")
    print("   • Crosshair should ALWAYS be visible")
    print("   • Check console for data vs empty space detection")
    print("=" * 70)
    
    # Render
    chart.render()


if __name__ == "__main__":
    main()
