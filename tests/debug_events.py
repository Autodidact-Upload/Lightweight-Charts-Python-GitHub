"""
Test to see what events fire when scrolling
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
    print("Event Detection Test")
    print("=" * 70)
    print("\nMove mouse over chart, then scroll. Watch what fires:")
    print("=" * 70)
    
    chart = Chart(
        title="Event Test",
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
    chart.set_crosshair_colors("#FFFF00", "#FFFF00")
    
    # Hook into all possible events
    def on_mouse_move(event):
        print(f"MOUSE_MOVE: pos={event.pos}")
    
    def on_mouse_wheel(event):
        print(f"MOUSE_WHEEL: delta={event.delta}")
    
    def on_key_press(event):
        print(f"KEY_PRESS: {event.key}")
    
    def on_draw(event):
        print("DRAW")
    
    chart.canvas.events.mouse_move.connect(on_mouse_move)
    chart.canvas.events.mouse_wheel.connect(on_mouse_wheel)
    chart.canvas.events.key_press.connect(on_key_press)
    chart.canvas.events.draw.connect(on_draw)
    
    # Camera events
    def on_camera_change(event):
        print(f"CAMERA: {event}")
    
    chart.view.camera.events.connect(on_camera_change)
    
    print("\n✅ Ready! Move mouse and scroll.\n")
    chart.render()

if __name__ == "__main__":
    main()
