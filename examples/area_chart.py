"""
Example 4: Area Chart
Area chart with custom colors and styling
"""

import sys
from pathlib import Path
import os

# Suppress Qt DPI warning on Windows
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lightweight_charts import Chart, AreaStyleOptions
from datetime import datetime, timedelta
import numpy as np


def generate_cumulative_data(num_points: int = 100):
    """Generate cumulative return data."""
    base_date = datetime(2024, 1, 1)
    data = []
    value = 100
    
    for i in range(num_points):
        date = base_date + timedelta(days=i)
        value += np.random.randn() * 1.5
        value = max(50, value)  # Floor at 50
        data.append({
            "time": date,
            "value": value
        })
    
    return data


def main():
    # Create chart
    chart = Chart(
        width=1200,
        height=600,
        title="Area Chart - Portfolio Value Over Time"
    )

    # Generate data
    data = generate_cumulative_data(100)

    # Add area series with custom styling
    area_series = chart.add_area_series(
        "Portfolio Value",
        AreaStyleOptions(
            line_color="#4CAF50",
            fill_color="#4CAF50",
            line_width=3,
            fill_alpha=0.3
        )
    )
    area_series.set_data(data)

    # Set time scale
    chart.update_time_scale_data(data)

    # Render chart
    print("Rendering chart... Close the window to exit.")
    chart.render()


if __name__ == "__main__":
    main()
