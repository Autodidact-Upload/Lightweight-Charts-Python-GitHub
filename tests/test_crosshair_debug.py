"""
DEBUG: Test crosshair visibility
This script will help us debug why the crosshair isn't showing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lightweight_charts import Chart, LineStyleOptions
from datetime import datetime, timedelta
import numpy as np
import logging

# Enable DEBUG logging to see everything
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 70)
    logger.info("CROSSHAIR DEBUG TEST")
    logger.info("=" * 70)
    
    # Create simple chart
    logger.info("Creating chart...")
    chart = Chart(
        width=800,
        height=600,
        title="Crosshair Debug Test",
        background_color="#000000"  # Black background for contrast
    )
    
    # Generate simple line data
    logger.info("Generating data...")
    base_date = datetime(2024, 1, 1)
    data = []
    for i in range(50):
        data.append({
            "time": base_date + timedelta(days=i),
            "value": 100 + i * 0.5
        })
    
    # Add line series with bright color
    logger.info("Adding line series...")
    line = chart.add_line_series(
        "Test",
        LineStyleOptions(color="#00FF00", width=3)  # Bright green, thick
    )
    line.set_data(data)
    
    # Update time scale
    chart.update_time_scale_data(data)
    
    # Set crosshair to bright colors for visibility
    logger.info("Setting crosshair colors...")
    chart.set_crosshair_colors(
        vert_color="#FF0000",   # Bright red
        horiz_color="#0000FF"   # Bright blue
    )
    
    # Check crosshair visual
    if chart.crosshair_visual:
        logger.info("✅ Crosshair visual exists")
        logger.info(f"   Initialized: {chart.crosshair_visual._initialized}")
        logger.info(f"   Options visible: {chart.crosshair_visual.options.visible}")
        
        # Try to force show it
        logger.info("Forcing crosshair to show...")
        chart.crosshair_visual.show()
    else:
        logger.error("❌ Crosshair visual is None!")
    
    logger.info("=" * 70)
    logger.info("Rendering chart...")
    logger.info("MOVE YOUR MOUSE OVER THE CHART!")
    logger.info("You should see:")
    logger.info("  - RED vertical line (follows X)")
    logger.info("  - BLUE horizontal line (follows Y)")
    logger.info("=" * 70)
    
    # Render
    chart.render()


if __name__ == "__main__":
    main()
