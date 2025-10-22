"""
Quick test: Verify both vertical and horizontal dashed lines work
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lightweight_charts import Chart, LineStyleOptions
from datetime import datetime, timedelta
import numpy as np

print("="  * 70)
print("DASHED CROSSHAIR - VERIFICATION TEST")
print("=" * 70)
print("\n✅ Testing:")
print("   1. Vertical line is dashed")
print("   2. Horizontal line is dashed")
print("   3. Both lines extend full screen")
print("   4. Dashes scale with zoom level")
print("\n🔍 Check:")
print("   • Move mouse horizontally → vertical dashed line follows")
print("   • Move mouse vertically → horizontal dashed line follows")
print("   • Zoom in/out → dashes remain visible")
print("   • Scroll beyond data → lines still visible")
print("=" * 70)

chart = Chart(
    width=1200,
    height=700,
    title="Dashed Crosshair Test - BOTH LINES SHOULD BE DASHED!",
    background_color="#000000"  # Black for contrast
)

# Simple line data
base_date = datetime(2024, 1, 1)
data = []
for i in range(50):
    data.append({
        "time": base_date + timedelta(days=i),
        "value": 100 + i + np.random.randn() * 5
    })

line = chart.add_line_series(
    "Price",
    LineStyleOptions(color="#00FF00", width=3)
)
line.set_data(data)

chart.update_time_scale_data(data)

# Bright colors for testing
chart.set_crosshair_colors(
    vert_color="#FFFF00",  # YELLOW vertical
    horiz_color="#00FFFF"   # CYAN horizontal
)

print("\n🚀 Chart ready!")
print("✨ YELLOW dashed vertical line")
print("✨ CYAN dashed horizontal line")
print("=" * 70)

chart.render()
