"""
Time and Price scale management
"""

from typing import List, Tuple, Optional
from datetime import datetime
from enum import Enum
import numpy as np


class PriceScaleMode(Enum):
    """Price scale display modes"""
    NORMAL = "normal"
    LOGARITHMIC = "logarithmic"
    PERCENTAGE = "percentage"
    INDEXED_TO_100 = "indexed_to_100"


class PriceScaleMargins:
    """Price scale margin configuration"""
    
    def __init__(self, top: float = 0.2, bottom: float = 0.1):
        """
        Initialize margins.
        
        Args:
            top: Top margin (0.0 to 1.0)
            bottom: Bottom margin (0.0 to 1.0)
        """
        self.top = max(0.0, min(1.0, top))
        self.bottom = max(0.0, min(1.0, bottom))


class PriceScaleOptions:
    """Complete price scale visual options"""
    
    def __init__(
        self,
        auto_scale: bool = True,
        mode: PriceScaleMode = PriceScaleMode.NORMAL,
        invert_scale: bool = False,
        align_labels: bool = True,
        scale_margins: Optional[PriceScaleMargins] = None,
        border_visible: bool = True,
        border_color: str = "#2B2B43",
        text_color: str = "#D1D4DC",
        visible: bool = True,
        ticks_visible: bool = False,
        entire_text_only: bool = False,
        minimum_width: int = 50
    ):
        """
        Initialize price scale options.
        
        Args:
            auto_scale: Automatically adjust scale to fit visible data
            mode: Display mode (normal, logarithmic, percentage, indexed)
            invert_scale: Invert the Y-axis
            align_labels: Prevent label overlap
            scale_margins: Top/bottom margins
            border_visible: Show border line
            border_color: Border color (hex)
            text_color: Label text color (hex)
            visible: Show the price scale
            ticks_visible: Show tick marks
            entire_text_only: Only show full text labels
            minimum_width: Minimum width in pixels
        """
        self.auto_scale = auto_scale
        self.mode = mode
        self.invert_scale = invert_scale
        self.align_labels = align_labels
        self.scale_margins = scale_margins or PriceScaleMargins()
        self.border_visible = border_visible
        self.border_color = border_color
        self.text_color = text_color
        self.visible = visible
        self.ticks_visible = ticks_visible
        self.entire_text_only = entire_text_only
        self.minimum_width = minimum_width


class TimeScale:
    """
    Manages time scale and axis labels.
    Handles visible range and time-based data access.
    """

    def __init__(self, data: Optional[List] = None):
        """
        Initialize TimeScale.
        
        Args:
            data: Initial data list
        """
        self.data = data or []
        self.visible_range = (0, len(self.data) - 1) if self.data else (0, 0)
        self._zoom_level = 1.0

    def set_data(self, data: List):
        """Set the data and update range."""
        self.data = data
        self.visible_range = (0, len(data) - 1) if data else (0, 0)

    def get_visible_data(self) -> List:
        """Get currently visible data points."""
        if not self.data:
            return []
        start, end = self.visible_range
        return self.data[int(start):int(end) + 1]

    def set_visible_range(self, start: float, end: float):
        """
        Set visible time range.
        
        Args:
            start: Start index
            end: End index
        """
        start = max(0, min(start, len(self.data) - 1))
        end = max(start, min(end, len(self.data) - 1))
        self.visible_range = (start, end)

    def zoom(self, factor: float, center: Optional[float] = None):
        """
        Zoom in/out.
        
        Args:
            factor: Zoom factor (>1 = zoom in, <1 = zoom out)
            center: Center point for zoom (0-1)
        """
        start, end = self.visible_range
        range_size = end - start
        new_size = range_size / factor

        if center is None:
            center = 0.5

        center_idx = start + range_size * center
        new_start = center_idx - new_size * center
        new_end = center_idx + new_size * (1 - center)

        self.set_visible_range(new_start, new_end)

    def pan(self, delta: float):
        """
        Pan left/right.
        
        Args:
            delta: Number of bars to pan
        """
        start, end = self.visible_range
        self.set_visible_range(start + delta, end + delta)

    def get_labels(self, num_labels: int = 6) -> List[str]:
        """
        Generate time labels for visible range.
        
        Args:
            num_labels: Number of labels to generate
        
        Returns:
            List of time label strings
        """
        visible = self.get_visible_data()
        if not visible:
            return []

        if len(visible) < num_labels:
            indices = range(len(visible))
        else:
            indices = np.linspace(0, len(visible) - 1, num_labels, dtype=int)

        labels = []
        for idx in indices:
            if idx < len(visible):
                item = visible[int(idx)]
                time_obj = item.get("time") if isinstance(item, dict) else getattr(item, "time", None)
                
                if isinstance(time_obj, datetime):
                    labels.append(time_obj.strftime("%Y-%m-%d"))
                else:
                    labels.append(str(time_obj))
        
        return labels


class PriceScale:
    """
    Manages price scale and formatting.
    Handles auto-scaling and price label generation.
    """

    def __init__(self, auto_scale: bool = True):
        """
        Initialize PriceScale.
        
        Args:
            auto_scale: Enable automatic scaling
        """
        self.auto_scale = auto_scale
        self.min_value = 0.0
        self.max_value = 100.0
        self._padding = 0.05  # 5% padding

    def get_labels(self, num_labels: int = 6) -> List[Tuple[float, str]]:
        """
        Generate price labels.
        
        Args:
            num_labels: Number of labels to generate
        
        Returns:
            List of (value, label_string) tuples
        """
        values = np.linspace(self.min_value, self.max_value, num_labels)
        return [(v, self._format_price(v)) for v in values]

    def update_range(self, min_val: float, max_val: float, auto_pad: bool = True):
        """
        Update visible price range.
        
        Args:
            min_val: Minimum price
            max_val: Maximum price
            auto_pad: Apply automatic padding
        """
        if min_val == max_val:
            min_val -= 1
            max_val += 1

        if auto_pad:
            padding = (max_val - min_val) * self._padding
            self.min_value = min_val - padding
            self.max_value = max_val + padding
        else:
            self.min_value = min_val
            self.max_value = max_val

    def get_price_at_y(self, y: float) -> float:
        """
        Convert normalized Y coordinate to price.
        
        Args:
            y: Normalized Y value (-1 to 1)
        
        Returns:
            Price value
        """
        return (y + 1) / 2 * (self.max_value - self.min_value) + self.min_value

    def get_y_at_price(self, price: float) -> float:
        """
        Convert price to normalized Y coordinate.
        
        Args:
            price: Price value
        
        Returns:
            Normalized Y value (-1 to 1)
        """
        if self.max_value == self.min_value:
            return 0.0
        return (price - self.min_value) / (self.max_value - self.min_value) * 2 - 1

    @staticmethod
    def _format_price(value: float) -> str:
        """Format price value."""
        if abs(value) >= 1e9:
            return f"${value / 1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"${value / 1e6:.2f}M"
        elif abs(value) >= 1e3:
            return f"${value / 1e3:.2f}K"
        else:
            return f"${value:.2f}"

    def set_padding(self, padding: float):
        """Set automatic padding ratio (0.0-1.0)."""
        self._padding = max(0.0, min(1.0, padding))
