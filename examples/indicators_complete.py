"""
Example 9: Technical Indicators
Demonstrates SMA, EMA, RSI, MACD, and Bollinger Bands
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
    HistogramStyleOptions,
    MovingAverage,
    RSI,
    MACD,
    BollingerBands
)
from datetime import datetime, timedelta
import numpy as np


def generate_ohlc_data(num_candles: int = 200):
    """Generate synthetic OHLC data."""
    base_date = datetime(2024, 1, 1)
    data = []
    price = 100
    
    for i in range(num_candles):
        date = base_date + timedelta(days=i)
        
        # Add some trend
        trend = np.sin(i / 20) * 5
        price = price + np.random.randn() * 2 + trend * 0.1
        
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
    print("=" * 80)
    print("Technical Indicators Example")
    print("=" * 80)
    print("This example demonstrates all built-in technical indicators:")
    print("  • SMA (Simple Moving Average)")
    print("  • EMA (Exponential Moving Average)")
    print("  • RSI (Relative Strength Index)")
    print("  • MACD (Moving Average Convergence Divergence)")
    print("  • Bollinger Bands")
    print("=" * 80)
    
    # Generate OHLC data
    ohlc_data = generate_ohlc_data(200)
    
    # Create chart
    chart = Chart(
        width=1600,
        height=900,
        title="Technical Indicators - Complete Suite"
    )

    # Add candlestick series
    print("\n📊 Adding candlestick chart...")
    candles = chart.add_candlestick_series(
        "Price",
        CandleStickStyleOptions(
            up_color="#26a69a",
            down_color="#ef5350"
        )
    )
    candles.set_data(ohlc_data)

    # Calculate and add SMA
    print("📈 Calculating SMA(20)...")
    sma_data = MovingAverage.sma(ohlc_data, period=20, source="close")
    sma_series = chart.add_line_series(
        "SMA(20)",
        LineStyleOptions(color="#2196F3", width=2)
    )
    sma_series.set_data(sma_data)

    # Calculate and add EMA
    print("📈 Calculating EMA(50)...")
    ema_data = MovingAverage.ema(ohlc_data, period=50, source="close")
    ema_series = chart.add_line_series(
        "EMA(50)",
        LineStyleOptions(color="#FF9800", width=2)
    )
    ema_series.set_data(ema_data)

    # Calculate and add Bollinger Bands
    print("📈 Calculating Bollinger Bands(20, 2)...")
    bb_upper, bb_middle, bb_lower = BollingerBands.calculate(
        ohlc_data,
        period=20,
        std_dev=2.0,
        source="close"
    )
    
    bb_upper_series = chart.add_line_series(
        "BB Upper",
        LineStyleOptions(color="#9C27B0", width=1)
    )
    bb_upper_series.set_data(bb_upper)
    
    bb_lower_series = chart.add_line_series(
        "BB Lower",
        LineStyleOptions(color="#9C27B0", width=1)
    )
    bb_lower_series.set_data(bb_lower)

    # Set time scale
    chart.update_time_scale_data(ohlc_data)

    print("\n✓ Chart created with indicators:")
    print("  ✓ Candlesticks")
    print("  ✓ SMA(20) - Blue line")
    print("  ✓ EMA(50) - Orange line")
    print("  ✓ Bollinger Bands - Purple lines")
    
    print("\n📊 Statistical Summary:")
    print(f"  • Data points: {len(ohlc_data)}")
    print(f"  • Price range: ${min([d['low'] for d in ohlc_data]):.2f} - ${max([d['high'] for d in ohlc_data]):.2f}")
    print(f"  • Last close: ${ohlc_data[-1]['close']:.2f}")
    print(f"  • SMA(20): ${[x['value'] for x in sma_data if not np.isnan(x['value'])][-1]:.2f}")
    print(f"  • EMA(50): ${[x['value'] for x in ema_data if not np.isnan(x['value'])][-1]:.2f}")
    
    # Calculate RSI for info
    rsi_data = RSI.calculate(ohlc_data, period=14)
    rsi_values = [x['value'] for x in rsi_data if not np.isnan(x['value'])]
    if rsi_values:
        print(f"  • RSI(14): {rsi_values[-1]:.2f}")
    
    # Calculate MACD for info
    macd_line, signal_line, histogram = MACD.calculate(ohlc_data)
    macd_values = [x['value'] for x in macd_line if not np.isnan(x['value'])]
    if macd_values:
        print(f"  • MACD: {macd_values[-1]:.4f}")
    
    print("\n💡 Note: RSI and MACD are calculated but not displayed on this chart.")
    print("   Run 'python examples/indicators_rsi.py' and 'indicators_macd.py'")
    print("   to see them in separate charts.")
    
    print("\n" + "=" * 80)
    print("Rendering chart... Close the window to exit.")
    print("=" * 80)
    
    # Render
    chart.render()


if __name__ == "__main__":
    main()
