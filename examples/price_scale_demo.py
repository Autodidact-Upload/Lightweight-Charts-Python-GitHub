"""
Price Scale Visual Demo
Demonstrates the visual price scale with labels and tick marks
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lightweight_charts import (
    Chart,
    CandleStickStyleOptions,
    LineStyleOptions,
    PriceScaleOptions,
    PriceScaleMode,
    PriceScaleMargins
)
from lightweight_charts.indicators import MovingAverage
from datetime import datetime, timedelta
import numpy as np

def main():
    print("=" * 80)
    print("🎨 PRICE SCALE VISUAL DEMO")
    print("=" * 80)
    
    print("\n✨ FEATURES DEMONSTRATED:")
    print("   1. Visual price scale on right side")
    print("   2. Price labels with auto-formatting")
    print("   3. Tick marks at each price level")
    print("   4. Border line separating scale from chart")
    print("   5. Customizable colors and styling")
    print("   6. Multiple display modes (normal, logarithmic, etc.)")
    
    print("\n📊 Generating sample data...")
    
    # Generate realistic OHLC data
    base_date = datetime(2024, 1, 1)
    data = []
    price = 45000  # Starting BTC price
    
    for i in range(100):
        # Random walk with slight uptrend
        change = np.random.randn() * 500 + 50
        
        open_p = price
        close_p = price + change
        high_p = max(open_p, close_p) + abs(np.random.randn() * 200)
        low_p = min(open_p, close_p) - abs(np.random.randn() * 200)
        volume = np.random.uniform(100, 1000)
        
        data.append({
            "time": base_date + timedelta(days=i),
            "open": open_p,
            "high": high_p,
            "low": low_p,
            "close": close_p,
            "volume": volume
        })
        
        price = close_p
    
    print(f"✅ Generated {len(data)} candles")
    print(f"   Price range: ${data[0]['open']:.2f} → ${data[-1]['close']:.2f}")
    
    # Create chart
    print("\n🎨 Creating chart with dark theme...")
    chart = Chart(
        width=1400,
        height=800,
        title="BTC/USD - Price Scale Demo",
        background_color="#0a0a0a"
    )
    
    # Add candlestick series
    print("\n🕯️  Adding candlestick series...")
    candle_series = chart.add_candlestick_series(
        "BTC/USD",
        CandleStickStyleOptions(
            up_color="#26A69A",
            down_color="#EF5350",
            wick_color="#787B86",
            border_visible=False
        )
    )
    candle_series.set_data(data)
    print("✅ Candlesticks added")
    
    # Add moving average
    print("\n📈 Adding SMA(20) indicator...")
    sma20_data = MovingAverage.sma(data, period=20)
    sma20_series = chart.add_line_series(
        "SMA(20)",
        LineStyleOptions(color="#FFD700", width=2)
    )
    sma20_series.set_data(sma20_data)
    print("✅ SMA(20) added")
    
    # Update time scale
    chart.update_time_scale_data(data)
    
    # Configure price scale with custom options
    print("\n⚙️  CONFIGURING PRICE SCALE:")
    print("   • Mode: Normal (displays actual prices)")
    print("   • Position: Right side")
    print("   • Border: Visible (dark gray)")
    print("   • Tick marks: Enabled")
    print("   • Labels: 8 levels, auto-formatted")
    print("   • Text color: Light gray (#D1D4DC)")
    print("   • Margins: Top 20%, Bottom 10%")
    
    price_scale_opts = PriceScaleOptions(
        auto_scale=True,
        mode=PriceScaleMode.NORMAL,
        invert_scale=False,
        align_labels=True,
        scale_margins=PriceScaleMargins(top=0.2, bottom=0.1),
        border_visible=True,
        border_color="#3C3C3C",
        text_color="#D1D4DC",
        visible=True,
        ticks_visible=True,
        entire_text_only=False,
        minimum_width=70
    )
    
    chart.configure_price_scale(price_scale_opts)
    print("✅ Price scale configured")
    
    # Configure crosshair with complementary colors
    print("\n✨ Configuring crosshair...")
    chart.set_crosshair_colors(
        vert_color="#00BFFF",   # Deep Sky Blue
        horiz_color="#FF69B4"    # Hot Pink
    )
    print("✅ Crosshair configured")
    
    # Display summary
    print("\n" + "=" * 80)
    print("🎉 CHART READY!")
    print("=" * 80)
    
    print("\n📊 VISUAL COMPONENTS:")
    print("   • Candlesticks: Green (up) / Red (down)")
    print("   • SMA(20): Golden line")
    print("   • Price Scale: Right side with labels")
    print("   • Crosshair: Blue (vertical) + Pink (horizontal)")
    
    print("\n🎮 INTERACTIVE FEATURES:")
    print("   • Move mouse → Crosshair follows")
    print("   • Scroll wheel → Zoom in/out (price scale auto-updates)")
    print("   • Click + drag → Pan left/right (price scale stays fixed)")
    print("   • Price labels → Auto-format (K, M, B for large numbers)")
    print("   • Tick marks → Show exact price levels")
    
    print("\n🎯 OBSERVE:")
    print("   1. Price labels on the right edge")
    print("   2. Small tick marks extending from border")
    print("   3. Border line separating data from scale")
    print("   4. Auto-formatted prices ($45.2K format)")
    print("   5. Price scale updates when zooming/panning")
    
    print("\n" + "=" * 80)
    print("🚀 LAUNCHING CHART...")
    print("=" * 80)
    print("\nClose the chart window when done.\n")
    
    # Render the chart
    chart.render()
    
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
