"""
Series classes for different chart types
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional, Any, TYPE_CHECKING
import numpy as np
import logging

logger = logging.getLogger(__name__)

from .data_types import (
    LineStyleOptions,
    CandleStickStyleOptions,
    HistogramStyleOptions,
    AreaStyleOptions
)
from .scales import TimeScale, PriceScale
from .utils import hex_to_rgb, hex_to_rgba, normalize_value

# Type checking imports to avoid runtime issues
if TYPE_CHECKING:
    from vispy.scene import visuals

try:
    from vispy.scene import visuals  # type: ignore[import]
except ImportError:
    visuals = None  # type: ignore


class BaseSeries(ABC):
    """Base class for all series types"""

    def __init__(self, name: str = "", visible: bool = True):
        """
        Initialize BaseSeries.
        
        Args:
            name: Series name/label
            visible: Initial visibility state
        """
        self.name = name
        self.visible = visible
        self.data: List = []
        self.visuals: Dict[str, Any] = {}

    def set_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Set series data.
        
        Args:
            data: List of data points (dicts or dataclass objects)
        
        Raises:
            ValueError: If data is empty or invalid
            TypeError: If data is not a list
        """
        if not data:
            raise ValueError(f"{self.__class__.__name__}: Data cannot be empty")
        
        if not isinstance(data, list):
            raise TypeError(f"{self.__class__.__name__}: Data must be a list")
        
        # Validate that all items have 'time' field
        for i, item in enumerate(data):
            if isinstance(item, dict):
                if "time" not in item:
                    raise ValueError(
                        f"{self.__class__.__name__}: Data point at index {i} missing 'time' field"
                    )
            elif not hasattr(item, "time"):
                raise ValueError(
                    f"{self.__class__.__name__}: Data point at index {i} missing 'time' attribute"
                )
        
        # Call series-specific validation
        self._validate_data(data)
        
        self.data = data
        logger.debug(f"{self.__class__.__name__}: Set {len(data)} data points")
    
    def update(self, bar: Dict[str, Any]) -> None:
        """
        Update the last bar in real-time (for live data).
        If bar time matches last bar, updates it. Otherwise appends new bar.
        
        Args:
            bar: New or updated bar data
        """
        if not self.data:
            self.data = [bar]
            return
        
        # Get time of incoming bar
        bar_time = bar.get("time") if isinstance(bar, dict) else getattr(bar, "time", None)
        last_time = self.data[-1].get("time") if isinstance(self.data[-1], dict) else getattr(self.data[-1], "time", None)
        
        if bar_time == last_time:
            # Update existing last bar
            self.data[-1] = bar
        else:
            # Append new bar
            self.data.append(bar)
    
    def _validate_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Validate series-specific data requirements.
        Override in subclasses for custom validation.
        
        Args:
            data: Data to validate
        
        Raises:
            ValueError: If data is invalid
        """
        pass

    def get_visible_data(self, time_scale: TimeScale) -> List:
        """Get data points in visible time range."""
        if not self.data:
            return []
        start, end = time_scale.visible_range
        return self.data[int(start):int(end) + 1]

    def _get_price_range(self, data: List) -> Tuple[float, float]:
        """Calculate min/max prices from data."""
        if not data:
            return 0.0, 100.0

        prices = []
        for item in data:
            if isinstance(item, dict):
                # For OHLC data, use high and low
                if "high" in item and "low" in item:
                    prices.extend([item["high"], item["low"]])
                # For line/area data, use value or close
                elif "value" in item:
                    prices.append(item["value"])
                elif "close" in item:
                    prices.append(item["close"])
            else:
                # For dataclass objects
                if hasattr(item, "high") and hasattr(item, "low"):
                    prices.extend([item.high, item.low])
                elif hasattr(item, "value"):
                    prices.append(item.value)
                elif hasattr(item, "close"):
                    prices.append(item.close)

        return (min(prices), max(prices)) if prices else (0.0, 100.0)

    @abstractmethod
    def create_visual(self, view: Any) -> Any:
        """Create Vispy visual elements."""
        pass

    @abstractmethod
    def update_visual(self, time_scale: TimeScale, price_scale: PriceScale) -> None:
        """Update visual with data."""
        pass


class LineSeries(BaseSeries):
    """Line chart series"""

    def __init__(self, name: str = "", style: Optional[LineStyleOptions] = None):
        super().__init__(name)
        self.style = style or LineStyleOptions()
        self.line_visual: Any = None
    
    def _validate_data(self, data: List[Dict[str, Any]]) -> None:
        """Validate line series data."""
        for i, item in enumerate(data):
            value = item.get("value") if isinstance(item, dict) else getattr(item, "value", None)
            if value is None:
                raise ValueError(
                    f"LineSeries: Data point at index {i} missing 'value' field"
                )

    def create_visual(self, view: Any) -> Any:
        """Create Vispy line visual."""
        if not visuals:
            logger.warning("LineSeries: Vispy not available, visual not created")
            return None

        try:
            color_tuple = hex_to_rgb(self.style.color)
            self.line_visual = visuals.Line(  # type: ignore[attr-defined]
                color=color_tuple,
                width=self.style.width,
                connect='strip'
            )
            view.add(self.line_visual)
            self.visuals['line'] = self.line_visual
            logger.debug("LineSeries: Visual created successfully")
            return self.line_visual
        except Exception as e:
            logger.error(f"LineSeries: Failed to create visual: {e}")
            raise

    def update_visual(self, time_scale: TimeScale, price_scale: PriceScale) -> None:
        """Update line visual with data."""
        if not self.line_visual:
            logger.warning("LineSeries: Visual not initialized, skipping update")
            return
        
        if not self.data:
            logger.warning("LineSeries: No data to render")
            return

        try:
            visible_data = self.get_visible_data(time_scale)
            if not visible_data:
                logger.debug("LineSeries: No visible data in current range")
                return

            x_coords = np.arange(len(visible_data))
            y_coords = np.array([
                item.get("value") if isinstance(item, dict) else getattr(item, "value")
                for item in visible_data
            ])

            # Normalize Y to screen space
            y_normalized = np.array([
                price_scale.get_y_at_price(float(y)) for y in y_coords
            ])

            pos = np.column_stack([x_coords, y_normalized, np.zeros(len(x_coords))])
            self.line_visual.set_data(pos)
            logger.debug(f"LineSeries: Updated visual with {len(visible_data)} points")
        except Exception as e:
            logger.error(f"LineSeries: Failed to update visual: {e}")
            raise


class CandlestickSeries(BaseSeries):
    """Candlestick chart series"""

    def __init__(self, name: str = "", style: Optional[CandleStickStyleOptions] = None):
        super().__init__(name)
        self.style = style or CandleStickStyleOptions()
        self.bodies_visual: Any = None
        self.wicks_visual: Any = None
        self.view: Any = None
    
    def _validate_data(self, data: List[Dict[str, Any]]) -> None:
        """Validate candlestick OHLC data."""
        required_fields = {"open", "high", "low", "close"}
        for i, item in enumerate(data):
            if isinstance(item, dict):
                missing = required_fields - set(item.keys())
                if missing:
                    raise ValueError(
                        f"CandlestickSeries: Data point at index {i} missing fields: {missing}"
                    )
            else:
                for field in required_fields:
                    if not hasattr(item, field):
                        raise ValueError(
                            f"CandlestickSeries: Data point at index {i} missing '{field}' attribute"
                        )

    def create_visual(self, view: Any) -> None:
        """Create Vispy candlestick visuals."""
        if not visuals:
            logger.warning("CandlestickSeries: Vispy not available, visuals not created")
            return

        try:
            self.view = view
            # Create empty line visuals that will be updated with data
            self.bodies_visual = visuals.Line(connect='segments')  # type: ignore[attr-defined]
            self.wicks_visual = visuals.Line(connect='segments')  # type: ignore[attr-defined]
            view.add(self.bodies_visual)
            view.add(self.wicks_visual)
            self.visuals['bodies'] = self.bodies_visual
            self.visuals['wicks'] = self.wicks_visual
            logger.debug("CandlestickSeries: Visuals created successfully")
        except Exception as e:
            logger.error(f"CandlestickSeries: Failed to create visuals: {e}")
            raise

    def update_visual(self, time_scale: TimeScale, price_scale: PriceScale) -> None:
        """Update candlestick visual."""
        if not self.bodies_visual:
            logger.warning("CandlestickSeries: Visuals not initialized, skipping update")
            return
        
        if not self.data:
            logger.warning("CandlestickSeries: No data to render")
            return

        try:
            visible_data = self.get_visible_data(time_scale)
            if not visible_data:
                logger.debug("CandlestickSeries: No visible data in current range")
                return

            wick_positions = []
            wick_colors = []
            body_positions = []
            body_colors = []

            for i, item in enumerate(visible_data):
                # Extract OHLC values with proper type handling
                if isinstance(item, dict):
                    open_p = float(item.get("open", 0))
                    close_p = float(item.get("close", 0))
                    high = float(item.get("high", 0))
                    low = float(item.get("low", 0))
                else:
                    open_p = float(getattr(item, "open", 0))
                    close_p = float(getattr(item, "close", 0))
                    high = float(getattr(item, "high", 0))
                    low = float(getattr(item, "low", 0))

                is_up = close_p >= open_p

                # Normalize prices
                y_open = price_scale.get_y_at_price(open_p)
                y_close = price_scale.get_y_at_price(close_p)
                y_high = price_scale.get_y_at_price(high)
                y_low = price_scale.get_y_at_price(low)

                # Body color
                body_color = hex_to_rgb(self.style.up_color if is_up else self.style.down_color)
                wick_color = hex_to_rgb(self.style.wick_color)

                # Create body as thick line segment
                body_positions.extend([
                    [i, y_open, 0],
                    [i, y_close, 0]
                ])
                body_colors.extend([body_color, body_color])

                # Create wicks if visible
                if self.style.wick_visible:
                    # Upper wick
                    wick_positions.extend([
                        [i, max(y_open, y_close), 0],
                        [i, y_high, 0]
                    ])
                    wick_colors.extend([wick_color, wick_color])
                    
                    # Lower wick
                    wick_positions.extend([
                        [i, min(y_open, y_close), 0],
                        [i, y_low, 0]
                    ])
                    wick_colors.extend([wick_color, wick_color])

            # Update bodies (thick lines)
            if body_positions:
                self.bodies_visual.set_data(
                    pos=np.array(body_positions),
                    color=np.array(body_colors),
                    width=self.style.body_width * 50,  # Scale width for visibility
                    connect='segments'
                )

            # Update wicks (thin lines)
            if wick_positions:
                self.wicks_visual.set_data(
                    pos=np.array(wick_positions),
                    color=np.array(wick_colors),
                    width=1,
                    connect='segments'
                )
            
            logger.debug(f"CandlestickSeries: Updated visual with {len(visible_data)} candles")
        except Exception as e:
            logger.error(f"CandlestickSeries: Failed to update visual: {e}")
            raise


class AreaSeries(LineSeries):
    """Area chart series with fill"""

    def __init__(self, name: str = "", style: Optional[AreaStyleOptions] = None):
        from .data_types import AreaStyleOptions
        style = style or AreaStyleOptions()
        line_style = LineStyleOptions(
            color=style.line_color,
            width=style.line_width
        )
        super().__init__(name, line_style)
        self.area_style = style
        self.fill_visual: Any = None

    def create_visual(self, view: Any) -> Any:
        """Create Vispy area visual."""
        self.line_visual = super().create_visual(view)
        if not visuals:
            logger.warning("AreaSeries: Vispy not available, fill visual not created")
            return None

        try:
            fill_color = hex_to_rgba(self.area_style.fill_color, self.area_style.fill_alpha)
            self.fill_visual = visuals.Polygon(color=fill_color)  # type: ignore[attr-defined]
            view.add(self.fill_visual)
            self.visuals['fill'] = self.fill_visual
            logger.debug("AreaSeries: Fill visual created successfully")
            return self.fill_visual
        except Exception as e:
            logger.error(f"AreaSeries: Failed to create fill visual: {e}")
            raise

    def update_visual(self, time_scale: TimeScale, price_scale: PriceScale) -> None:
        """Update area visual."""
        super().update_visual(time_scale, price_scale)

        if not self.fill_visual:
            logger.warning("AreaSeries: Fill visual not initialized, skipping update")
            return
        
        if not self.data:
            return

        try:
            visible_data = self.get_visible_data(time_scale)
            if not visible_data:
                return

            x_coords = np.arange(len(visible_data))
            y_coords = np.array([
                item.get("value") if isinstance(item, dict) else getattr(item, "value")
                for item in visible_data
            ])

            y_normalized = np.array([
                price_scale.get_y_at_price(float(y)) for y in y_coords
            ])

            # Create polygon vertices for area fill
            vertices = []
            for x, y in zip(x_coords, y_normalized):
                vertices.append([x, y, 0])
            
            # Add bottom edge (reverse order)
            for x in reversed(x_coords):
                vertices.append([x, -1.0, 0])

            # Update polygon with new vertices
            vertices_array = np.array(vertices, dtype=np.float32)
            self.fill_visual.pos = vertices_array
            logger.debug("AreaSeries: Updated fill visual")
        except Exception as e:
            logger.error(f"AreaSeries: Failed to update fill visual: {e}")
            raise


class HistogramSeries(BaseSeries):
    """Histogram/bar chart series"""

    def __init__(
        self,
        name: str = "",
        style: Optional[HistogramStyleOptions] = None
    ):
        super().__init__(name)
        self.style = style or HistogramStyleOptions()
        self.bars_visual: Any = None
    
    def _validate_data(self, data: List[Dict[str, Any]]) -> None:
        """Validate histogram data."""
        for i, item in enumerate(data):
            value = item.get("value") if isinstance(item, dict) else getattr(item, "value", None)
            if value is None:
                raise ValueError(
                    f"HistogramSeries: Data point at index {i} missing 'value' field"
                )

    def create_visual(self, view: Any) -> None:
        """Create histogram bars visual."""
        if not visuals:
            logger.warning("HistogramSeries: Vispy not available, visual not created")
            return

        try:
            # Use line segments for bars
            self.bars_visual = visuals.Line(connect='segments')  # type: ignore[attr-defined]
            view.add(self.bars_visual)
            self.visuals['bars'] = self.bars_visual
            logger.debug("HistogramSeries: Visual created successfully")
        except Exception as e:
            logger.error(f"HistogramSeries: Failed to create visual: {e}")
            raise

    def update_visual(self, time_scale: TimeScale, price_scale: PriceScale) -> None:
        """Update histogram."""
        if not self.bars_visual or not visuals:
            logger.warning("HistogramSeries: Visual not initialized, skipping update")
            return
        
        if not self.data:
            logger.warning("HistogramSeries: No data to render")
            return

        try:
            visible_data = self.get_visible_data(time_scale)
            if not visible_data:
                logger.debug("HistogramSeries: No visible data in current range")
                return

            bar_positions = []
            bar_colors = []
            color = hex_to_rgb(self.style.color)

            for i, item in enumerate(visible_data):
                value = item.get("value") if isinstance(item, dict) else getattr(item, "value", 0)
                value = float(value) if value is not None else 0.0
                y_normalized = price_scale.get_y_at_price(value)

                # Create bar as line segment from bottom to value
                bar_positions.extend([
                    [i, -1.0, 0],  # Bottom
                    [i, y_normalized, 0]  # Top
                ])
                bar_colors.extend([color, color])

            if bar_positions:
                self.bars_visual.set_data(
                    pos=np.array(bar_positions),
                    color=np.array(bar_colors),
                    width=self.style.bar_width * 50,  # Scale width for visibility
                    connect='segments'
                )
                logger.debug(f"HistogramSeries: Updated visual with {len(visible_data)} bars")
        except Exception as e:
            logger.error(f"HistogramSeries: Failed to update visual: {e}")
            raise
