"""
Example 1: Basic Line Chart
Simple line chart with moving average data
"""

import sys
from pathlib import Path
import os

# Suppress Qt DPI warning on Windows
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'

# Add src to path so we can import lightweight_charts
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lightweight_charts import Chart, LineStyleOptions
from datetime import datetime, timedelta
import numpy as np


def generate_price_data(num_points: int = 100):
    """Generate synthetic price data."""
    base_date = datetime(2024, 1, 1)
    data = []
    price = 100
    
    for i in range(num_points):
        date = base_date + timedelta(days=i)
        price += np.random.randn() * 2
        data.append({
            "time": date,
            "value": price
        })
    
    return data


def main():
    print("=" * 60)
    print("Basic Line Chart Example")
    print("=" * 60)
    
    # Create chart
    chart = Chart(
        width=1200,
        height=600,
        title="Basic Line Chart - Stock Price"
    )

    # Generate data
    data = generate_price_data(100)

    # Add line series
    line_series = chart.add_line_series(
        "Stock Price",
        LineStyleOptions(
            color="#2196F3",
            width=2
        )
    )
    line_series.set_data(data)

    # Set time scale data
    chart.update_time_scale_data(data)

    # Render chart
    print("✓ Chart created successfully!")
    print("✓ Data loaded: 100 points")
    print("\n📊 Rendering chart window...")
    print("   • Pan: Click and drag")
    print("   • Zoom: Mouse wheel")
    print("   • Close window to exit")
    print("=" * 60)
    
    chart.render()


if __name__ == "__main__":
    main()
