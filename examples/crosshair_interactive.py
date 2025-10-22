"""
Example: Interactive Crosshair Demo
Shows the working crosshair visual with real-time data display
Run with --fullscreen flag for fullscreen mode
"""

import sys
from pathlib import Path
import os

# Suppress Qt DPI warning on Windows
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lightweight_charts import Chart, CandleStickStyleOptions, LineStyleOptions
from datetime import datetime, timedelta
import numpy as np
import logging

# Enable logging to see crosshair data
logging.basicConfig(level=logging.INFO)


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
    """Callback when crosshair moves - prints data to console."""
    if position.series_data:
        data = position.series_data
        if isinstance(data, dict) and "close" in data:
            print(f"\n📊 Crosshair Data:")
            print(f"   Time: {position.time.strftime('%Y-%m-%d') if position.time else 'N/A'}")
            print(f"   Open:  ${data.get('open', 0):.2f}")
            print(f"   High:  ${data.get('high', 0):.2f}")
            print(f"   Low:   ${data.get('low', 0):.2f}")
            print(f"   Close: ${data.get('close', 0):.2f}")
            print(f"   Price at cursor: ${position.price:.2f}")


def on_crosshair_leave():
    """Callback when mouse leaves chart."""
    print("\n👋 Mouse left chart area")


def main():
    # Check for flags
    fullscreen = "--fullscreen" in sys.argv
    maximized = "--maximized" in sys.argv or "-m" in sys.argv
    normal = "--normal" in sys.argv or "-n" in sys.argv
    
    # Default to maximized if no flag specified
    if not fullscreen and not maximized and not normal:
        maximized = True  # Default behavior
    
    print("=" * 70)
    print("Interactive Crosshair Demo - DARK MODE")
    if fullscreen:
        print("🖥️  FULLSCREEN MODE (No window borders)")
    elif maximized:
        print("🖥️  MAXIMIZED WINDOW (Window controls visible)")
    print("=" * 70)
    print("\n🎯 Features:")
    print("   ✅ Visual crosshair lines (vertical + horizontal)")
    print("   ✅ Follows mouse in real-time")
    print("   ✅ Snaps to nearest data point")
    print("   ✅ Event callbacks (see console output)")
    print("   ✅ Data extraction at cursor position")
    print("   ✅ Dark theme with neon colors")
    print("\n💡 Try this:")
    print("   • Move mouse over chart → See crosshair lines")
    print("   • Watch console → See OHLC data at cursor")
    print("   • Pan/zoom → Crosshair still works")
    if fullscreen:
        print("   • Press ESC to exit fullscreen")
    print("\n💻 Usage:")
    print("   python crosshair_interactive.py          # Maximized (default)")
    print("   python crosshair_interactive.py -m       # Maximized")
    print("   python crosshair_interactive.py --fullscreen # Fullscreen")
    print("   python crosshair_interactive.py --normal     # Normal size")
    print("=" * 70)
    
    # Create chart with DARK THEME
    chart = Chart(
        width=1400,
        height=700,
        title="Interactive Crosshair Demo - Move Mouse Over Chart!",
        background_color="#0a0a0a",  # ⭐ Dark background
        fullscreen=fullscreen,
        maximized=maximized
    )

    # Generate OHLC data
    ohlc_data = generate_ohlc_data(100)

    # Add candlestick series with bright colors for dark theme
    candle_series = chart.add_candlestick_series(
        "BTC/USD",
        CandleStickStyleOptions(
            up_color="#00FF41",      # Neon green
            down_color="#FF0040",    # Hot pink
            wick_color="#FFFFFF",    # White wicks
            border_up_color="#00FF41",
            border_down_color="#FF0040"
        )
    )
    candle_series.set_data(ohlc_data)

    # Add moving average
    ma_data = []
    for i in range(len(ohlc_data)):
        if i < 20:
            ma_data.append({"time": ohlc_data[i]["time"], "value": np.nan})
        else:
            window = ohlc_data[i-19:i+1]
            avg = np.mean([c["close"] for c in window])
            ma_data.append({"time": ohlc_data[i]["time"], "value": avg})
    
    ma_series = chart.add_line_series(
        "MA20",
        LineStyleOptions(color="#FFD700", width=2)  # Gold - looks great on dark
    )
    ma_series.set_data(ma_data)

    # Set time scale
    chart.update_time_scale_data(ohlc_data)
    
    # Set crosshair colors for dark theme
    chart.set_crosshair_colors(
        vert_color="#888888",
        horiz_color="#888888"
    )

    # Subscribe to crosshair events
    chart.subscribe_crosshair_move(on_crosshair_move)
    chart.subscribe_crosshair_leave(on_crosshair_leave)

    print("\n🚀 Chart ready! Move your mouse over the chart...")
    print("=" * 70)
    
    # Render chart
    chart.render()


if __name__ == "__main__":
    main()
