"""
Test: Dashed Crosshair Lines
Demo of the new dashed crosshair feature
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lightweight_charts import Chart, CandleStickStyleOptions, LineStyleOptions
from datetime import datetime, timedelta
import numpy as np

def main():
    print("=" * 70)
    print("DASHED CROSSHAIR DEMO")
    print("=" * 70)
    print("\n✨ Features:")
    print("   • Dashed vertical line (time axis)")
    print("   • Dashed horizontal line (price axis)")
    print("   • Customizable dash/gap lengths")
    print("   • Bright colors for visibility")
    print("\n💡 Try adjusting:")
    print("   • chart.set_crosshair_dash_style(dash_length=20, gap_length=10)")
    print("   • chart.set_crosshair_dash_style(dash_length=5, gap_length=3)")
    print("=" * 70)
    
    # Create chart with dark theme
    chart = Chart(
        width=1400,
        height=800,
        title="Dashed Crosshair Demo",
        background_color="#0a0a0a",
        maximized=True
    )
    
    # Generate OHLC data
    base_date = datetime(2024, 1, 1)
    data = []
    price = 100
    
    for i in range(100):
        open_p = price
        close_p = price + np.random.randn() * 2
        high_p = max(open_p, close_p) + abs(np.random.randn())
        low_p = min(open_p, close_p) - abs(np.random.randn())
        
        data.append({
            "time": base_date + timedelta(days=i),
            "open": open_p,
            "high": high_p,
            "low": low_p,
            "close": close_p
        })
        
        price = close_p
    
    # Add candlestick series
    candle_series = chart.add_candlestick_series(
        "BTC/USD",
        CandleStickStyleOptions(
            up_color="#00FF41",
            down_color="#FF0040",
            wick_color="#FFFFFF"
        )
    )
    candle_series.set_data(data)
    
    # Add moving average
    ma_data = []
    for i in range(len(data)):
        if i < 20:
            ma_data.append({"time": data[i]["time"], "value": np.nan})
        else:
            window = data[i-19:i+1]
            avg = np.mean([c["close"] for c in window])
            ma_data.append({"time": data[i]["time"], "value": avg})
    
    ma_series = chart.add_line_series(
        "MA20",
        LineStyleOptions(color="#FFD700", width=2)
    )
    ma_series.set_data(ma_data)
    
    chart.update_time_scale_data(data)
    
    # Set dashed crosshair with custom colors
    chart.set_crosshair_colors(
        vert_color="#00FFFF",  # Cyan
        horiz_color="#FF00FF"   # Magenta
    )
    
    # Customize dash pattern
    # Default: dash=10, gap=5
    # Try: dash=20, gap=10 for longer dashes
    # Try: dash=5, gap=3 for shorter dashes
    chart.set_crosshair_dash_style(dash_length=10, gap_length=5)  # type: ignore[attr-defined]
    
    print("\n🚀 Chart ready! Move your mouse to see dashed crosshair...")
    print("=" * 70)
    
    chart.render()


if __name__ == "__main__":
    main()
