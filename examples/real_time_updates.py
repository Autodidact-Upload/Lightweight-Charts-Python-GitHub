"""
Example 7: Real-time Updates
Simulating real-time data streaming to the chart
Note: This is a simplified example. In production, you would connect to a real data feed.
"""

import sys
from pathlib import Path
import os

# Suppress Qt DPI warning on Windows
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lightweight_charts import Chart, LineStyleOptions, CandleStickStyleOptions
from datetime import datetime, timedelta
import numpy as np


def generate_initial_data(num_points: int = 50):
    """Generate initial historical data."""
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
    print("Real-time Chart Example")
    print("=" * 50)
    print("This example demonstrates the data structure for real-time updates.")
    print("In production, you would update the chart with new data points")
    print("from a live data feed (WebSocket, API, etc.)")
    print("=" * 50)
    
    # Create chart
    chart = Chart(
        width=1200,
        height=600,
        title="Real-time Price Stream"
    )

    # Generate initial data
    initial_data = generate_initial_data(50)

    # Add line series
    line_series = chart.add_line_series(
        "Live Price",
        LineStyleOptions(
            color="#2196F3",
            width=2
        )
    )
    line_series.set_data(initial_data)

    # Set time scale
    chart.update_time_scale_data(initial_data)

    print("\nInitialized chart with 50 historical data points.")
    print("\nTo implement real-time updates in your application:")
    print("1. Connect to your data feed (WebSocket, REST API, etc.)")
    print("2. On each new data point:")
    print("   - Append to your data list")
    print("   - Call: line_series.set_data(updated_data)")
    print("   - Call: chart.update_time_scale_data(updated_data)")
    print("   - Call: chart._update_visuals()")
    print("\nRendering static chart... Close the window to exit.")
    
    # Render chart
    chart.render()


if __name__ == "__main__":
    main()
