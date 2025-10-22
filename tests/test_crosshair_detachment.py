"""
Test: Crosshair detachment issue when scrolling beyond candles
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lightweight_charts import Chart, CandleStickStyleOptions
from datetime import datetime, timedelta
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("=" * 70)
    print("Testing Crosshair Detachment Issue")
    print("=" * 70)
    print("\n📋 Test Instructions:")
    print("1. Move mouse over chart - both lines should follow")
    print("2. Scroll UP (above candles) - watch the crosshair")
    print("3. Scroll DOWN (below candles) - watch the crosshair")
    print("\n🐛 Expected Issue:")
    print("   - Vertical line 'sticks' to candle area")
    print("   - Horizontal line continues to follow mouse")
    print("   - Lines become 'detached'")
    print("=" * 70)
    
    chart = Chart(
        width=1200,
        height=800,
        title="Crosshair Detachment Test",
        background_color="#0a0a0a"
    )
    
    # Generate OHLC data
    base_date = datetime(2024, 1, 1)
    data = []
    price = 100
    
    for i in range(50):
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
    
    candle_series = chart.add_candlestick_series(
        "Test",
        CandleStickStyleOptions(
            up_color="#00FF41",
            down_color="#FF0040",
            wick_color="#FFFFFF"
        )
    )
    candle_series.set_data(data)
    
    chart.update_time_scale_data(data)
    
    # Bright crosshair for visibility
    chart.set_crosshair_colors(
        vert_color="#FFFF00",  # Yellow
        horiz_color="#00FFFF"   # Cyan
    )
    
    print("\n🚀 Chart ready!")
    print("Try scrolling ABOVE and BELOW the candles...")
    print("=" * 70)
    
    chart.render()

if __name__ == "__main__":
    main()
