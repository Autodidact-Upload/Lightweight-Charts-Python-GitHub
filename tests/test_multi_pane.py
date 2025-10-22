"""
Test script for multi-pane functionality
Simple 2-pane test: Main chart + RSI indicator
"""

import sys
from pathlib import Path
import os

# Suppress Qt DPI warning
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lightweight_charts import Chart, CandleStickStyleOptions, LineStyleOptions
from datetime import datetime, timedelta
import numpy as np
import logging

# Enable DEBUG logging to see pane coordinates
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def generate_ohlc_data(num_candles: int = 100):
    """Generate synthetic OHLC data."""
    base_date = datetime(2024, 1, 1)
    data = []
    price = 100
    
    for i in range(num_candles):
        date = base_date + timedelta(days=i)
        
        open_price = price
        close_price = price + np.random.randn() * 2
        high_price = max(open_price, close_price) + abs(np.random.randn() * 1)
        low_price = min(open_price, close_price) - abs(np.random.randn() * 1)
        
        data.append({
            "time": date,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price
        })
        
        price = close_price
    
    return data


def calculate_rsi(data, period=14):
    """Calculate RSI indicator."""
    rsi_data = []
    closes = [d["close"] for d in data]
    
    for i in range(len(data)):
        if i < period:
            rsi_data.append({"time": data[i]["time"], "value": 50})  # Neutral
        else:
            window = closes[i-period+1:i+1]
            gains = []
            losses = []
            
            for j in range(1, len(window)):
                change = window[j] - window[j-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            avg_gain = np.mean(gains) if gains else 0
            avg_loss = np.mean(losses) if losses else 0
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_data.append({"time": data[i]["time"], "value": rsi})
    
    return rsi_data


def main():
    print("=" * 70)
    print("Multi-Pane Test: 2 Panes (Main + RSI)")
    print("=" * 70)
    
    # Create chart
    chart = Chart(
        title="Multi-Pane Test - 2 Panes",
        background_color="#1e1e1e",  # Dark theme
        width=1400,
        height=800
    )

    # Generate OHLC data
    logger.info("Generating OHLC data...")
    ohlc_data = generate_ohlc_data(100)

    # ========== PANE 1: Main Chart (80% height) ==========
    logger.info("Creating Pane 1: Main Chart (height_ratio=0.8)...")
    main_pane = chart.add_pane(name="main", height_ratio=0.8)
    
    # Add candlesticks to main pane
    candles = main_pane.add_candlestick_series(
        "Price",
        CandleStickStyleOptions(
            up_color="#26a69a",
            down_color="#ef5350",
            wick_color="#FFFFFF"
        )
    )
    candles.set_data(ohlc_data)
    logger.info(f"Added {len(ohlc_data)} candlesticks to main pane")
    
    # ========== PANE 2: RSI Indicator (20% height) ==========
    logger.info("Creating Pane 2: RSI (height_ratio=0.2)...")
    rsi_pane = chart.add_pane(name="rsi", height_ratio=0.2)
    
    # Calculate RSI
    logger.info("Calculating RSI...")
    rsi_data = calculate_rsi(ohlc_data, period=14)
    
    # Add RSI line
    rsi_line = rsi_pane.add_line_series(
        "RSI(14)",
        LineStyleOptions(color="#9C27B0", width=2)
    )
    rsi_line.set_data(rsi_data)
    logger.info(f"Added RSI line with {len(rsi_data)} points to RSI pane")
    
    # Add reference lines at 70 (overbought) and 30 (oversold)
    overbought_data = [{"time": d["time"], "value": 70} for d in ohlc_data]
    oversold_data = [{"time": d["time"], "value": 30} for d in ohlc_data]
    
    ob_line = rsi_pane.add_line_series(
        "Overbought",
        LineStyleOptions(color="#FF4444", width=1)
    )
    ob_line.set_data(overbought_data)
    
    os_line = rsi_pane.add_line_series(
        "Oversold",
        LineStyleOptions(color="#44FF44", width=1)
    )
    os_line.set_data(oversold_data)
    logger.info("Added RSI reference lines (70/30)")

    # Set time scale data (shared across all panes)
    logger.info("Setting time scale data...")
    chart.update_time_scale_data(ohlc_data)

    print("\n" + "=" * 70)
    print("✅ Chart created successfully!")
    print(f"   • Pane 1 (main): 80% height - {len(candles.data)} candlesticks")
    print(f"   • Pane 2 (rsi): 20% height - RSI indicator")
    print("   • Total panes: 2")
    print("   • Separator line should be visible")
    print("\n💡 Check the console output for Y-coordinate ranges")
    print("=" * 70)
    
    # Render chart
    logger.info("Rendering chart...")
    chart.render()


if __name__ == "__main__":
    main()
