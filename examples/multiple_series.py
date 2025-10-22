"""
Example 3: Multiple Series
Display multiple series (candles + moving averages) on same chart
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
    LineStyleOptions,
    CandleStickStyleOptions,
    AreaStyleOptions
)
from datetime import datetime, timedelta
import numpy as np


def generate_ohlc_with_ma(num_candles: int = 100):
    """Generate OHLC data with moving averages."""
    base_date = datetime(2024, 1, 1)
    ohlc_data = []
    price = 100
    
    for i in range(num_candles):
        date = base_date + timedelta(days=i)
        
        open_price = price
        close_price = price + np.random.randn() * 3
        high_price = max(open_price, close_price) + abs(np.random.randn() * 2)
        low_price = min(open_price, close_price) - abs(np.random.randn() * 2)
        
        ohlc_data.append({
            "time": date,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": np.random.randint(1000000, 10000000)
        })
        
        price = close_price
    
    # Calculate moving averages
    ma20_data = []
    ma50_data = []
    
    for i, candle in enumerate(ohlc_data):
        # MA20
        start_ma20 = max(0, i - 19)
        ma20 = np.mean([c["close"] for c in ohlc_data[start_ma20:i+1]])
        ma20_data.append({
            "time": candle["time"],
            "value": ma20
        })
        
        # MA50
        start_ma50 = max(0, i - 49)
        ma50 = np.mean([c["close"] for c in ohlc_data[start_ma50:i+1]])
        ma50_data.append({
            "time": candle["time"],
            "value": ma50
        })
    
    return ohlc_data, ma20_data, ma50_data


def main():
    # Create chart
    chart = Chart(
        width=1400,
        height=700,
        title="Multiple Series - Price with Moving Averages"
    )

    # Generate data
    ohlc_data, ma20_data, ma50_data = generate_ohlc_with_ma(100)

    # Add candlestick series
    candle_series = chart.add_candlestick_series(
        "OHLC",
        CandleStickStyleOptions(
            up_color="#26a69a",
            down_color="#ef5350"
        )
    )
    candle_series.set_data(ohlc_data)

    # Add MA20 line
    ma20_series = chart.add_line_series(
        "MA20",
        LineStyleOptions(
            color="#FF9800",
            width=2
        )
    )
    ma20_series.set_data(ma20_data)

    # Add MA50 line
    ma50_series = chart.add_line_series(
        "MA50",
        LineStyleOptions(
            color="#9C27B0",
            width=2
        )
    )
    ma50_series.set_data(ma50_data)

    # Set time scale
    chart.update_time_scale_data(ohlc_data)

    # Render chart
    print("Rendering chart... Close the window to exit.")
    chart.render()


if __name__ == "__main__":
    main()
