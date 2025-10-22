"""
Example 8: Crosshair and Markers
Demonstrates crosshair functionality, price markers, and tooltips
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
    CandleStickStyleOptions,
    LineStyleOptions,
    PriceMarker,
    TimeMarker
)
from datetime import datetime, timedelta
import numpy as np


def generate_ohlc_data(num_candles: int = 100):
    """Generate synthetic OHLC data."""
    base_date = datetime(2024, 1, 1)
    data = []
    price = 100
    
    for i in range(num_candles):
        date = base_date + timedelta(days=i)
        
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


def on_crosshair_move(position):
    """Callback when crosshair moves."""
    if position and position.series_data:
        data = position.series_data
        print(f"\n📍 Crosshair Position:")
        print(f"   Time: {position.time}")
        print(f"   Price: ${position.price:.2f}")
        if "open" in data:
            print(f"   Open: ${data['open']:.2f}")
            print(f"   High: ${data['high']:.2f}")
            print(f"   Low: ${data['low']:.2f}")
            print(f"   Close: ${data['close']:.2f}")


def on_crosshair_leave():
    """Callback when crosshair leaves chart."""
    print("\n↩️  Crosshair left the chart")


def main():
    print("=" * 70)
    print("Crosshair & Markers Example")
    print("=" * 70)
    print("Features demonstrated:")
    print("  • Crosshair with price/time display")
    print("  • Price markers on the price axis")
    print("  • Time markers on the time axis")
    print("  • Tooltip data on hover")
    print("  • Event callbacks")
    print("=" * 70)
    
    # Create chart
    chart = Chart(
        width=1400,
        height=800,
        title="Crosshair & Markers - Interactive Example"
    )

    # Generate OHLC data
    ohlc_data = generate_ohlc_data(100)

    # Add candlestick series
    candle_series = chart.add_candlestick_series(
        "BTC/USD",
        CandleStickStyleOptions(
            up_color="#26a69a",
            down_color="#ef5350"
        )
    )
    candle_series.set_data(ohlc_data)

    # Add moving average
    ma_data = []
    for i, candle in enumerate(ohlc_data):
        start_idx = max(0, i - 19)
        ma = np.mean([c["close"] for c in ohlc_data[start_idx:i+1]])
        ma_data.append({
            "time": candle["time"],
            "value": ma
        })

    ma_series = chart.add_line_series(
        "MA20",
        LineStyleOptions(color="#FF9800", width=2)
    )
    ma_series.set_data(ma_data)

    # Add price markers
    current_price = ohlc_data[-1]["close"]
    chart.add_price_marker(PriceMarker(
        price=current_price,
        color="#2196F3",
        label=f"Current: ${current_price:.2f}"
    ))
    
    # Add price marker at specific level
    chart.add_price_marker(PriceMarker(
        price=110,
        color="#FF5722",
        label="Resistance: $110"
    ))
    
    chart.add_price_marker(PriceMarker(
        price=90,
        color="#4CAF50",
        label="Support: $90"
    ))

    # Add time markers
    chart.add_time_marker(TimeMarker(
        time=ohlc_data[25]["time"],
        color="#9C27B0",
        label="Event A"
    ))
    
    chart.add_time_marker(TimeMarker(
        time=ohlc_data[75]["time"],
        color="#FF9800",
        label="Event B"
    ))

    # Subscribe to crosshair events
    chart.subscribe_crosshair_move(on_crosshair_move)
    chart.subscribe_crosshair_leave(on_crosshair_leave)

    # Set time scale
    chart.update_time_scale_data(ohlc_data)

    print("\n✓ Chart created with crosshair system")
    print("✓ Price markers added (Current, Resistance, Support)")
    print("✓ Time markers added (Event A, Event B)")
    print("✓ Crosshair callbacks registered")
    print("\n📊 Hover over the chart to see crosshair in action!")
    print("   Mouse events will be printed to console")
    print("\n💡 Note: Vispy's mouse event handling is basic.")
    print("   For production use, consider implementing custom")
    print("   mouse tracking for better crosshair interaction.")
    print("=" * 70)
    
    # Render chart
    chart.render()


if __name__ == "__main__":
    main()
