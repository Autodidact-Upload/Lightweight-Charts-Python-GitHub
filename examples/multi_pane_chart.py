"""
Example: Multi-Pane Chart with Indicators
Demonstrates the multi-pane layout system
"""

import sys
from pathlib import Path
import os

# Suppress Qt DPI warning on Windows
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lightweight_charts import Chart, CandleStickStyleOptions, LineStyleOptions, HistogramStyleOptions
from lightweight_charts.indicators import RSI, MACD
from datetime import datetime, timedelta
import numpy as np
import logging

# Enable INFO logging to see pane ranges
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)


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
    print("Multi-Pane Chart Demo")
    print("=" * 70)
    print("\n🎯 Features:")
    print("   ✅ Multiple independent panes")
    print("   ✅ Main chart (70% height)")
    print("   ✅ RSI pane (15% height)")
    print("   ✅ MACD pane (15% height)")
    print("   ✅ Synchronized scrolling/zooming")
    print("   ✅ Independent price scales")
    print("=" * 70)
    
    # Create chart
    chart = Chart(
        title="Multi-Pane Chart - Price + RSI + MACD",
        background_color="#0a0a0a",  # Dark theme
        maximized=True
    )

    # Generate OHLC data
    ohlc_data = generate_ohlc_data(200)

    # ==========  PANE 1: Main Chart (Price Action) ==========
    print("\n📊 Creating Pane 1: Main Chart (70% height)...")
    main_pane = chart.add_pane(name="main", height_ratio=0.7)
    
    # Add candlesticks to main pane
    candles = main_pane.add_candlestick_series(
        "BTC/USD",
        CandleStickStyleOptions(
            up_color="#00FF41",
            down_color="#FF0040",
            wick_color="#FFFFFF"
        )
    )
    candles.set_data(ohlc_data)
    
    # Add MA20 to main pane
    ma20_data = []
    for i in range(len(ohlc_data)):
        if i < 20:
            ma20_data.append({"time": ohlc_data[i]["time"], "value": np.nan})
        else:
            window = ohlc_data[i-19:i+1]
            avg = np.mean([c["close"] for c in window])
            ma20_data.append({"time": ohlc_data[i]["time"], "value": avg})
    
    ma20 = main_pane.add_line_series(
        "MA20",
        LineStyleOptions(color="#FFD700", width=2)
    )
    ma20.set_data(ma20_data)
    
    # ==========  PANE 2: RSI Indicator ==========
    print("📈 Creating Pane 2: RSI (15% height)...")
    rsi_pane = chart.add_pane(name="rsi", height_ratio=0.15)
    
    # Calculate RSI
    rsi_data = RSI.calculate(ohlc_data, period=14)
    
    # Add RSI line
    rsi_line = rsi_pane.add_line_series(
        "RSI(14)",
        LineStyleOptions(color="#9C27B0", width=2)
    )
    rsi_line.set_data(rsi_data)
    
    # Add overbought/oversold reference lines (70/30)
    overbought_data = [{"time": d["time"], "value": 70} for d in ohlc_data]
    oversold_data = [{"time": d["time"], "value": 30} for d in ohlc_data]
    
    ob_line = rsi_pane.add_line_series(
        "OB(70)",
        LineStyleOptions(color="#FF4444", width=1)
    )
    ob_line.set_data(overbought_data)
    
    os_line = rsi_pane.add_line_series(
        "OS(30)",
        LineStyleOptions(color="#44FF44", width=1)
    )
    os_line.set_data(oversold_data)
    
    # ==========  PANE 3: MACD Indicator ==========
    print("📉 Creating Pane 3: MACD (15% height)...")
    macd_pane = chart.add_pane(name="macd", height_ratio=0.15)
    
    # Calculate MACD
    macd_line_data, signal_line_data, histogram_data = MACD.calculate(ohlc_data)
    
    # Add MACD line
    macd_line = macd_pane.add_line_series(
        "MACD",
        LineStyleOptions(color="#2196F3", width=2)
    )
    macd_line.set_data(macd_line_data)
    
    # Add Signal line
    signal_line = macd_pane.add_line_series(
        "Signal",
        LineStyleOptions(color="#FF9800", width=2)
    )
    signal_line.set_data(signal_line_data)
    
    # Add Histogram
    macd_hist = macd_pane.add_histogram_series(
        "Histogram",
        HistogramStyleOptions(color="#26a69a", bar_width=0.6)
    )
    macd_hist.set_data(histogram_data)

    # Set time scale data (shared across all panes)
    chart.update_time_scale_data(ohlc_data)

    print("\n✨ Chart ready!")
    print("   • Pane 1: Price action with MA20")
    print("   • Pane 2: RSI with overbought/oversold lines")
    print("   • Pane 3: MACD with signal and histogram")
    print("   • All panes synchronized!")
    print("=" * 70)
    
    # Render chart
    chart.render()


if __name__ == "__main__":
    main()
