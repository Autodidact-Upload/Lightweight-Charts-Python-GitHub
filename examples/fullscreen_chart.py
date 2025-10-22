"""
Example: Fullscreen Chart Demo
Opens the chart in fullscreen mode
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


def generate_ohlc_data(num_candles: int = 200):
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


def main():
    print("=" * 70)
    print("Fullscreen Chart Demo")
    print("=" * 70)
    print("\n🖥️  Opening chart in FULLSCREEN mode...")
    print("   • Press ESC or F11 to exit fullscreen")
    print("   • Close window to exit")
    print("=" * 70)
    
    # Create chart in FULLSCREEN mode
    chart = Chart(
        title="Fullscreen Trading Chart - BTC/USD",
        background_color="#1e1e1e",  # Dark theme looks better fullscreen
        fullscreen=True  # ⭐ THIS ENABLES FULLSCREEN
    )

    # Generate OHLC data
    ohlc_data = generate_ohlc_data(200)

    # Add candlestick series
    candle_series = chart.add_candlestick_series(
        "BTC/USD",
        CandleStickStyleOptions(
            up_color="#00FF41",      # Neon green
            down_color="#FF0040",    # Hot pink
            wick_color="#FFFFFF"
        )
    )
    candle_series.set_data(ohlc_data)

    # Add moving averages
    # MA20
    ma20_data = []
    for i in range(len(ohlc_data)):
        if i < 20:
            ma20_data.append({"time": ohlc_data[i]["time"], "value": np.nan})
        else:
            window = ohlc_data[i-19:i+1]
            avg = np.mean([c["close"] for c in window])
            ma20_data.append({"time": ohlc_data[i]["time"], "value": avg})
    
    ma20_series = chart.add_line_series(
        "MA20",
        LineStyleOptions(color="#FFD700", width=2)  # Gold
    )
    ma20_series.set_data(ma20_data)

    # MA50
    ma50_data = []
    for i in range(len(ohlc_data)):
        if i < 50:
            ma50_data.append({"time": ohlc_data[i]["time"], "value": np.nan})
        else:
            window = ohlc_data[i-49:i+1]
            avg = np.mean([c["close"] for c in window])
            ma50_data.append({"time": ohlc_data[i]["time"], "value": avg})
    
    ma50_series = chart.add_line_series(
        "MA50",
        LineStyleOptions(color="#9C27B0", width=2)  # Purple
    )
    ma50_series.set_data(ma50_data)

    # Set time scale
    chart.update_time_scale_data(ohlc_data)

    print("\n✨ Chart opening in fullscreen...")
    print("   Enjoy the immersive view!")
    
    # Render chart in fullscreen
    chart.render()


if __name__ == "__main__":
    main()
