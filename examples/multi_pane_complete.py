"""
Complete Multi-Pane Chart Example
Demonstrates professional multi-pane layout with synchronized crosshair
"""

from lightweight_charts import Chart
from lightweight_charts.indicators import MovingAverage, RSI, MACD
from datetime import datetime, timedelta
import numpy as np
import logging

# Enable logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_realistic_ohlc_data(days: int = 100, start_price: float = 100.0):
    """Generate realistic OHLC data with volume"""
    np.random.seed(42)
    data = []
    current_price = start_price
    base_date = datetime(2024, 1, 1)
    
    for i in range(days):
        # Add trend and noise
        trend = 0.1 * np.sin(i / 10)  # Sine wave trend
        noise = np.random.randn() * 2  # Random noise
        
        current_price = max(10, current_price + trend + noise)
        
        # Generate OHLC
        daily_range = abs(np.random.randn()) * 3
        open_price = current_price + np.random.randn() * 0.5
        close_price = current_price + np.random.randn() * 0.5
        high_price = max(open_price, close_price) + daily_range * 0.7
        low_price = min(open_price, close_price) - daily_range * 0.3
        
        # Generate volume (higher on big moves)
        price_change = abs(close_price - open_price)
        base_volume = 1000000
        volume = base_volume * (1 + price_change / current_price * 10) * (0.5 + np.random.rand())
        
        data.append({
            "time": base_date + timedelta(days=i),
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": volume
        })
    
    return data


def main():
    print("=" * 60)
    print("🎨 Multi-Pane Chart Example")
    print("=" * 60)
    print()
    
    # Generate data
    print("📊 Generating OHLC data...")
    ohlc_data = generate_realistic_ohlc_data(days=150, start_price=100)
    
    # Calculate indicators
    print("📈 Calculating indicators...")
    sma_20 = MovingAverage.sma(ohlc_data, period=20)
    sma_50 = MovingAverage.sma(ohlc_data, period=50)
    rsi_data = RSI.calculate(ohlc_data, period=14)
    macd_line, signal_line, histogram = MACD.calculate(ohlc_data)
    
    # Extract volume data
    volume_data = [{"time": d["time"], "value": d["volume"]} for d in ohlc_data]
    
    print("✅ Data prepared!")
    print()
    
    # Create chart
    print("🎨 Creating multi-pane chart...")
    chart = Chart(
        width=1400,
        height=900,
        title="Multi-Pane Chart - BTC/USD",
        background_color="#1E222D"
    )
    
    # ========== CREATE PANES ==========
    print("📐 Setting up panes...")
    
    # Main price pane (60% of height)
    main_pane = chart.add_pane("Main", height_ratio=0.6)
    print(f"  ✓ Main pane: 60% height")
    
    # Volume pane (15% of height)
    volume_pane = chart.add_pane("Volume", height_ratio=0.15)
    print(f"  ✓ Volume pane: 15% height")
    
    # RSI pane (10% of height)
    rsi_pane = chart.add_pane("RSI", height_ratio=0.10)
    print(f"  ✓ RSI pane: 10% height")
    
    # MACD pane (15% of height)
    macd_pane = chart.add_pane("MACD", height_ratio=0.15)
    print(f"  ✓ MACD pane: 15% height")
    
    print()
    
    # ========== ADD SERIES TO PANES ==========
    print("📊 Adding series to panes...")
    
    # Main pane: Candlesticks + Moving Averages
    print("  → Main pane: Candlesticks + SMA 20 + SMA 50")
    from lightweight_charts import CandleStickStyleOptions, LineStyleOptions
    
    candles = main_pane.add_candlestick_series(
        "Price",
        CandleStickStyleOptions(
            up_color="#26A69A",
            down_color="#EF5350",
            wick_color="#838E93",
            body_width=0.6
        )
    )
    candles.set_data(ohlc_data)
    
    sma20_series = main_pane.add_line_series(
        "SMA 20",
        LineStyleOptions(color="#2196F3", width=2)
    )
    sma20_series.set_data(sma_20)
    
    sma50_series = main_pane.add_line_series(
        "SMA 50",
        LineStyleOptions(color="#FF9800", width=2)
    )
    sma50_series.set_data(sma_50)
    
    # Volume pane: Histogram
    print("  → Volume pane: Histogram")
    from lightweight_charts import HistogramStyleOptions
    
    volume_series = volume_pane.add_histogram_series(
        "Volume",
        HistogramStyleOptions(
            color="#26A69A",
            bar_width=0.8
        )
    )
    volume_series.set_data(volume_data)
    
    # RSI pane: Line
    print("  → RSI pane: RSI Line")
    rsi_series = rsi_pane.add_line_series(
        "RSI",
        LineStyleOptions(color="#9C27B0", width=2)
    )
    rsi_series.set_data(rsi_data)
    
    # MACD pane: MACD Line + Signal + Histogram
    print("  → MACD pane: MACD Line + Signal + Histogram")
    macd_series = macd_pane.add_line_series(
        "MACD",
        LineStyleOptions(color="#2196F3", width=2)
    )
    macd_series.set_data(macd_line)
    
    signal_series = macd_pane.add_line_series(
        "Signal",
        LineStyleOptions(color="#FF9800", width=2)
    )
    signal_series.set_data(signal_line)
    
    macd_hist = macd_pane.add_histogram_series(
        "Histogram",
        HistogramStyleOptions(color="#26A69A", bar_width=0.6)
    )
    macd_hist.set_data(histogram)
    
    print()
    
    # ========== CONFIGURE TIME SCALE ==========
    print("⚙️  Configuring time scale...")
    chart.update_time_scale_data(ohlc_data)
    
    # ========== CONFIGURE CROSSHAIR ==========
    print("🎯 Configuring crosshair...")
    chart.set_crosshair_colors(
        vert_color="#00FFFF",  # Cyan vertical line
        horiz_color="#FF00FF"  # Magenta horizontal line
    )
    
    print()
    print("=" * 60)
    print("✅ Chart Ready!")
    print("=" * 60)
    print()
    print("📌 Features:")
    print("  • 4 synchronized panes (Main, Volume, RSI, MACD)")
    print("  • Crosshair spans all panes")
    print("  • Independent price scales per pane")
    print("  • Pan and zoom with mouse")
    print("  • Separator lines between panes")
    print()
    print("🎮 Controls:")
    print("  • Scroll: Zoom in/out")
    print("  • Drag: Pan left/right")
    print("  • Mouse: Crosshair follows cursor")
    print()
    print("🚀 Rendering chart...")
    print()
    
    # Render
    chart.render()


if __name__ == "__main__":
    main()
