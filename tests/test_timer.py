"""
Ultra-simple test to verify timer is working
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

# Counters to see if timer is working
timer_count = 0
mouse_move_count = 0

def main():
    global timer_count, mouse_move_count
    
    print("=" * 70)
    print("Timer Diagnostic Test")
    print("=" * 70)
    
    chart = Chart(
        title="Timer Test",
        background_color="#000000",
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
    chart.set_crosshair_colors("#FFFF00", "#FFFF00")
    
    # Patch the timer function to count calls
    original_update = chart._update_crosshair_position
    
    def patched_update(event=None):
        global timer_count
        timer_count += 1
        if timer_count % 60 == 0:  # Print every second
            print(f"Timer called {timer_count} times, Mouse moves: {mouse_move_count}")
        original_update(event)
    
    chart._update_crosshair_position = patched_update
    
    # Patch mouse move to count
    original_mouse_move = chart._on_mouse_move
    
    def patched_mouse_move(event):
        global mouse_move_count
        mouse_move_count += 1
        original_mouse_move(event)
    
    chart._on_mouse_move = patched_mouse_move
    
    print("\n✅ Watch console:")
    print("   - Should see 'Timer called X times' every second")
    print("   - Move mouse over chart - mouse move count should increase")
    print("   - Scroll - timer should still be running\n")
    
    chart.render()

if __name__ == "__main__":
    main()
